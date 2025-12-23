
import httpx
import re
import json

from pageother.SQLManager import verify_pocid


VERIFY_ADDRESS = []

def verify_url(url):
    try:
        parsed_url = httpx.URL(url)
        
        if parsed_url.scheme not in ['http', 'https']:
            return False
            
        if not parsed_url.host:
            return False
            
        if not parsed_url.host.strip():
            return False
            
        host = parsed_url.host.strip()
        
        if host == 'localhost':
            return True
            
        if is_valid_ip(host):
            return True
            
        if is_valid_domain(host):
            return True
            
        return False
        
    except Exception:
        return False

def is_valid_ip(ip):
    try:
        import ipaddress
        ipaddress.ip_address(ip)
        return True
    except Exception:
        return False

def is_valid_domain(domain):
    pattern = re.compile(
        r'^[a-zA-Z0-9\-\.]+\.[a-zA-Z]{1,}$'
    )
    return bool(pattern.match(domain))

def verify_headers(header):
    try:
        key, value = header.split(':', 1)
        return True
    except Exception:
        return False
        
def verify_pocs(pocs):
    poc_list = ["全量", "全部POC","全部脚本",
            "信息泄露", "跨站脚本(XSS)", "SQL注入", "命令执行", "任意代码执行", 
            "文件类", "未授权", "请求伪造(CSRF/SSRF)", "目录类漏洞", "拒绝服务"
        ]
    pattern = r'^POC-\d{6}-\d{6}-\d{3,}'
    msg = []
    for i in pocs:
        if i not in poc_list:
            if bool(re.match(pattern, i)):
                if verify_pocid(i) or verify_pocid(i,1):
                    continue
                else:
                    msg.append(i)
            else:
                msg.append(i)
    if msg:
        return False, msg
    return True, None      

def verify_scan_cfg(cfg_data):
    error_msg = {
        'urls': [],
        'headers': [],
    }

    urls = cfg_data['urls']
    headers = cfg_data['headers']
    selected_pocs = cfg_data['selected_pocs']

    if not urls or not selected_pocs: 
        return False, '请填写完整配置信息'
    
    for i in urls:
        if not verify_url(i):
            error_msg['urls'].append(i)
    if error_msg['urls']:
        return False, "目标地址错误: "+str(error_msg['urls'])
    
    for i in headers:
        if not verify_headers(i):
            error_msg['headers'].append(i)
    if error_msg['headers']:
        return False,"请求头格式错误: " + str(error_msg['headers'])
   
    is_valid, poc_msg = verify_pocs(selected_pocs)
    if not is_valid:
        return False, "POCID格式错误/不存在： " + str(poc_msg)
    return True, None
        
def start_proxy()->tuple:
    with open("./config/network.json", "r", encoding="utf-8") as f:
        proxy_cfg = json.load(f)
    if 'Proxy' in proxy_cfg:
        print("正在检查代理配置...")
        if "Addresses" not in proxy_cfg['Proxy']:
            return False, "代理地址不存在"
        if "EnableRotation" not in proxy_cfg['Proxy']:
            return False, "代理配置不存在"
        if "VerificationAddress" not in proxy_cfg['Proxy']:
            return False, "代理验证地址不存在"
    else:
        return False, "代理配置文件不存在，请设置代理配置"
    global VERIFY_ADDRESS
    VERIFY_ADDRESS = proxy_cfg['Proxy']['VerificationAddress']
    proxy_list = proxy_cfg['Proxy']['Addresses']
    pattern = r'^(http|https?)://[\w.-]+(:\d+)?$'
    log_error_proxy = []
    for i in proxy_list:
        if not re.match(pattern, i):
            log_error_proxy.append(i)
    if len(log_error_proxy) != 0:
        return False, f"配置文件代理地址格式错误：{log_error_proxy}"
    print("代理配置检查通过")
    return True, proxy_cfg

def verify_proxy(proxies: str):
    print("正在检查代理地址可用性...")
    proxy = {
        "http://": proxies,
        "https://": proxies
    }
    urls = VERIFY_ADDRESS
    resp = []
    ua = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    for i in urls:
        try:
            print(f"正在检查代理地址可用性，目标：{i}")
            response = httpx.get(i, proxies=proxy, headers=ua, timeout=10, verify=False)
            resp.append(response.status_code)
        
        except Exception as e:
            print(f"代理地址可用性测试失败，错误信息：{e}")   
    if 200 in resp or 302 in resp:
        print(f"代理地址可用性测试通过: Proxies = {proxies}")
        return True
    return False 