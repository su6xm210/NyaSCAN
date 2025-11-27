from scan.Constructor import Tactics, Poc
from scan.LogManager import create_log_file, write_error_log, write_result_log
from scan.AsyncRequest import make_async_client, request_with_tactics

from fake_useragent import UserAgent

from collections import deque
import asyncio
import aiosqlite
import yaml
import httpx
import json
import re
import time
import sqlite3
import importlib.util
import sys
import os
import copy


MAKE_CLIENT_CONFIG = {}
RETRY_TACTICS = {}
MAX_CONCURRENCY = 0
DB_POOL = None

def start_scan(cfg_data):
    try:
        # 创建日志文件
        error_log = create_log_file()
        print("error log path : "+error_log)
        result_log = create_log_file(error_log)
        print("result log path: "+result_log)

        poc = Poc(cfg_data)
        poc_id, pocscript = poc.get_pocid()
        if poc_id:
            pass
        elif pocscript:
            pass
        else:
            print("ERROR: 未选择任何poc")
            raise Exception("ERROR: 未选择任何poc")

        if poc_id:
            tactics = Tactics(cfg_data)
            scfg = tactics.cfg_data
            load_global_cfg()
            global MAX_CONCURRENCY
            if scfg['mode'] == 'ALONE':
                MAX_CONCURRENCY = scfg['concurrency']
            else:
                MAX_CONCURRENCY = min(len(scfg['urls']), scfg['concurrency'])
            for i in range(len(scfg['urls'])):
                if scfg['urls'][i][-1] == '/':
                    scfg['urls'][i] = scfg['urls'][i][:-1]

            # 根据代理配置生成client
            if not scfg['enable_proxy'] or not scfg['EnableRotation']:
                if scfg['Proxy'] is None or scfg['Proxy'][0] is None:
                    proxy = None
                else:
                    proxy = scfg['Proxy'][0]
                client = make_client(scfg, proxy)
                if scfg['mode'] == 'ALONE':
                    for url in scfg['urls']:
                        asyncio.run(concurrency_tasks(poc_id, client,
                                                    url, scfg['headers'], 
                                                    scfg['enable_retry_backoff'], 
                                                    scfg['max_retries'], None,"A",
                                                    error_log, result_log))
                if scfg['mode'] == 'GROUP':
                    for pocid in poc_id:
                        asyncio.run(concurrency_tasks(scfg['urls'], client,
                                                    None, scfg['headers'], 
                                                    scfg['enable_retry_backoff'], 
                                                    scfg['max_retries'], pocid,'G',
                                                    error_log, result_log))
                asyncio.run(close_client(client))
            else:
                proxy_list = scfg['Proxy']
                if not proxy_list:
                    print("ERROR: 启用代理轮换但未提供代理列表")
                    raise Exception("ERROR: 启用代理轮换但未提供代理列表")
                proxy_index = 0
                if scfg['mode'] == 'ALONE':
                    for url in scfg['urls']:
                        batch_split_num = MAX_CONCURRENCY
                        if MAX_CONCURRENCY > len(poc_id):
                            batch_split_num = len(poc_id)
                        poc_batches = [poc_id[i:i + batch_split_num] for i in range(0, len(poc_id), batch_split_num)]
                        print(f"{url}=={poc_batches}")
                        for batch in poc_batches:
                            current_proxy = proxy_list[proxy_index]
                            client = make_client(scfg, current_proxy)
                            asyncio.run(concurrency_tasks(batch, client,
                                                url, scfg['headers'], 
                                                scfg['enable_retry_backoff'], 
                                                scfg['max_retries'], None,'A',
                                                error_log, result_log))
                            asyncio.run(close_client(client))
                            proxy_index = (proxy_index + 1) % len(proxy_list)
                            
                if scfg['mode'] == 'GROUP':
                    for pocid in poc_id:
                        url_batches = [scfg['urls'][i:i + MAX_CONCURRENCY] for i in range(0, len(scfg['urls']), MAX_CONCURRENCY)]
                        for batch in url_batches:
                            current_proxy = proxy_list[proxy_index]
                            client = make_client(scfg, current_proxy)
                            asyncio.run(concurrency_tasks(batch, client,
                                                None, scfg['headers'], 
                                                scfg['enable_retry_backoff'], 
                                                scfg['max_retries'], pocid,'G',
                                                error_log, result_log))
                            asyncio.run(close_client(client))
                            proxy_index = (proxy_index + 1) % len(proxy_list)
            print("POC执行结束")
        if pocscript:
            work_script(pocscript, cfg_data['urls'], cfg_data['mode'], error_log, result_log)
            print("POC脚本执行结束")
        return "完成"

    except Exception as e:
        print(f"errr:{e}")
        with open(error_log,"a") as el:
            el.write(f"ERROR: {e}\n")
        return f"ERROR: {e}"

async def close_client(client):
    try:
        await client.aclose()
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            pass

async def work_all(client, poc, url, header, backoff, max_attempts, error_log, result_log):
    """POC库的检测"""
    try:
        res =  await async_qurery_poc(poc)
        r_header = {}
        if header != []:
            for i in header:
                k, v = i.split(':')
                r_header[k] = v.strip()
        else:
            r_header = None
        r_header = parse_headers(res['request']['headers'] ,r_header, res['request']['data_type'])
        
        r_payloads = res['payload']['content'].split('\n')
        if res['request']['path'][0] != '/':
            r_url = url + '/' + res['request']['path']
        else:
            r_url = url + res['request']['path']
        for i in r_payloads:
            if i == '':
                r_payloads.remove(i)
        if r_payloads == []:
            r_payloads = ['']
        for pay in r_payloads:
            w_url = r_url
            w_header = copy.deepcopy(r_header)
            w_body = res['request']['data']
            if res['payload']['position'] == 'URL':
                if len(pay) >= 1:
                    if r_url[-1] == '/':
                        if pay[0] == '/':
                            w_url =r_url + pay[1:]
                        else:
                            w_url = r_url + pay
                    else:
                        w_url = r_url + pay
            elif res['payload']['position'] == 'header' and "PAYLOAD" in res['request']['headers']:
                for key,value in w_header.items():
                    w_header[key] = value.replace('PAYLOAD', pay)
            elif res['payload']['position'] == 'body' and "PAYLOAD" not in res['request']['data']:
                w_body = res['request']['data'] + pay
            elif res['payload']['position'] == 'body' and "PAYLOAD" in res['request']['data']:
                w_body = w_body.replace('PAYLOAD', pay)

            if len(res['rules']) < 2 and res['rules'][0]['type'] == 'time':
                start_time = time.time()
                resp = await request_with_tactics(
                        client, res['request']['method'],w_url,error_log,
                        headers=w_header,data=w_body,
                        backoff=False,
                        max_attempts=1,
                        retry_tatics=RETRY_TACTICS,
                        TimeoutConfig={"connect":max(MAKE_CLIENT_CONFIG['MaxConnectTimeout'],int(res['rules'][0]['val'])),
                                        "read": max(MAKE_CLIENT_CONFIG['MaxReadTimeout'],int(res['rules'][0]['val'])),
                                        "write": max(MAKE_CLIENT_CONFIG['MaxWriteTimeout'], int(res['rules'][0]['val'])),
                                        "pool": MAKE_CLIENT_CONFIG['MaxPoolDelay']
                                        }
                    )
                use_time = time.time()-start_time
                if res['rules'][0]['op'] in ['<', '>='] and use_time >= int(res['rules'][0]['val']):
                    await write_result_log(result_log, "There is a security vulnerability", url, res['poc_name'], " ", poc, f"检测方式为时间检测: {res['rules'][0]['op']} {res['rules'][0]['val']}")
                    continue
                if res['rules'][0]['op'] in ['>', '<='] and use_time < int(res['rules'][0]['val']):
                    await write_result_log(result_log, "There is a security vulnerability", url, res['poc_name']," ", poc, f"检测方式为时间检测: {res['rules'][0]['op']} {res['rules'][0]['val']}")
                    continue
                await write_result_log(result_log, "There is not a security vulnerability", url,res['poc_name']," ", poc, f"检测方式为时间检测: {res['rules'][0]['op']} {res['rules'][0]['val']}")
                continue
            resp = await request_with_tactics(
                client, res['request']['method'],w_url,error_log,
                headers=w_header,data=w_body,
                backoff=backoff,
                max_attempts=max_attempts,
                retry_tatics=RETRY_TACTICS
                )
            for ru in res['rules']:
                if ru['position'] == 'again_req':
                    check_result_a =  await check_again_req(ru, url, client, error_log)
                else:
                    check_result_a =  check_result(ru,resp)
                if check_result_a[0]:
                    await write_result_log(result_log, "There is a security vulnerability", url, res['poc_name'], " ", poc, check_result_a[1], " ",check_result_a[2])
                else:
                    await write_result_log(result_log, "There is not a security vulnerability", url, res['poc_name'], " ", poc, check_result_a[1]," ",check_result_a[2])
            continue
          
    except Exception as e:
        print("work func error:", end=" ")
        print(e)
        await write_error_log(error_log, url, f" POC INFO: {poc}",f"ERROR: {e}")
        return 

async def concurrency_tasks(task_queue, client, url, header, backoff, max_attempts, pocid, mode,error_log, result_log):
    """流式处理"""
    task_queue = deque(task_queue)
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    await init_db_pool('poc')
    async def run_task(client, poc, url, header, backoff, max_attempts, error_log, result_log):
        async with semaphore:
            await work_all(client, poc, url, header, backoff, max_attempts, error_log, result_log)

    running_tasks = []
    for _ in range(min(MAX_CONCURRENCY, len(task_queue))):
        if task_queue and mode == "A":
            task_id = task_queue.popleft()
            task = asyncio.create_task(run_task(client, task_id, url, header, backoff, max_attempts, error_log, result_log))
            running_tasks.append(task)
        if task_queue and mode == "G":
            task_id = task_queue.popleft()
            task = asyncio.create_task(run_task(client, pocid, task_id, header, backoff, max_attempts, error_log, result_log))
            running_tasks.append(task)
    
    while running_tasks:
        done, pending = await asyncio.wait(running_tasks, return_when=asyncio.FIRST_COMPLETED)
        running_tasks = list(pending)
    
        while len(running_tasks) < MAX_CONCURRENCY and task_queue:
            if mode == 'A':
                task_id = task_queue.popleft()
                task = asyncio.create_task(run_task(client, task_id, url, header, backoff, max_attempts, error_log, result_log))
                running_tasks.append(task)
            if mode == 'G':
                task_id = task_queue.popleft()
                task = asyncio.create_task(run_task(client, pocid, task_id, header, backoff, max_attempts, error_log, result_log))
                running_tasks.append(task)

    if running_tasks:
        await asyncio.gather(*running_tasks, return_exceptions=True)
    await close_db_pool()

def load_global_cfg():
    with open('config/global_cfg.yaml', 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    global MAKE_CLIENT_CONFIG
    global RETRY_TACTICS
    MAKE_CLIENT_CONFIG = data['MakeClientConfig']
    RETRY_TACTICS = data['Retry']

def make_client(scfg, proxy):
    if scfg['concurrency'] == 1:
        max_keep_alive_connections = 0
    elif scfg['concurrency'] <= 10:
        max_keep_alive_connections = 1
    elif scfg['concurrency'] > 10:
        max_keep_alive_connections = int(scfg['concurrency'] * MAKE_CLIENT_CONFIG['MaxKeepaliveConnectionsRatio'])
    proxies = None
    if proxy:
        proxies = {
            "http://": proxy,
            "https://": proxy,
        }
    client = make_async_client(
        timeout=httpx.Timeout(
            connect=MAKE_CLIENT_CONFIG['MaxConnectTimeout'],
            read=MAKE_CLIENT_CONFIG['MaxReadTimeout'],
            write=MAKE_CLIENT_CONFIG['MaxWriteTimeout'],
            pool=MAKE_CLIENT_CONFIG['MaxPoolDelay']
            ),
        limits=httpx.Limits(
            max_connections=scfg['concurrency'],
            max_keepalive_connections=max_keep_alive_connections
            ),
        proxies=proxies
    )
    return client

async def init_db_pool(dbname):
    """初始化数据库连接池"""
    global DB_POOL
    DB_POOL = await aiosqlite.connect(f"data/db/{dbname}.db")

async def close_db_pool():
    """关闭数据库连接池"""
    if DB_POOL:
        await DB_POOL.close()

def parse_headers(header_string, existing_headers=None, header_type=None):
    """
    解析headers
    header_string POC内置的headers
    existing_headers 上层传入的headers
    header_type 请求头类型(辅助header_string)
    """
    if existing_headers is None:
        existing_headers = {}
    if len(existing_headers)<=1:
        existing_headers = {}
    if len(header_string) > 1:
        lines = header_string.split('\n')
        lines = list(filter(lambda item: item != "", lines))
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                existing_headers[key] = value

    if 'Content-Type' in header_string:
        if header_type == 'raw':
            existing_headers['Content-Type'] = 'text/plain'
        elif header_type == 'json':
            existing_headers['Content-Type'] = 'application/json'
        elif header_type == 'xml':
            existing_headers['Content-Type'] = 'application/xml'
        elif header_type == 'form-data':
            existing_headers['Content-Type'] = 'multipart/form-data'
        elif header_type == 'x-www-form-urlencoded':
            existing_headers['Content-Type'] = 'application/x-www-form-urlencoded'

    if 'User-Agent' not in existing_headers:
        existing_headers['User-Agent'] = UserAgent().random

    for key, value in existing_headers.items():
        existing_headers[key] = value.strip()

    return existing_headers

async def async_qurery_poc(id) -> dict:
    """异步查询数据库"""
    global DB_POOL
    async with DB_POOL.execute(f"SELECT * FROM poc WHERE poc_id = ?", (id,)) as cursor:
        res = await cursor.fetchone()
        if res is None:
            raise Exception("Poc not found")
        res_dict = {
                "poc_id": res[0],
                "poc_name": res[1],
                "vul_id": res[2],
                "request": json.loads(res[9]),
                "payload":  json.loads(res[10]),
                "rules": json.loads(res[11])
        }
        return res_dict
    
def conn_script_db():
    conn = sqlite3.connect('./data/db/pocscript.db')
    cursor = conn.cursor()
    return conn, cursor

def close_script_db(conn):
    conn.close()

def qurery_poc_script(id, cursor) -> dict:
    """同步查询数据库"""
    cursor.execute(f"SELECT * FROM pocscript WHERE poc_id = ?", (id,))
    res = cursor.fetchone()
    res_dict = {
        "poc_id": res[0],
        "poc_name": res[1],
        "vul_id": res[2],
        "script_id": res[9]
    }
    return res_dict

def check_result(rule, response):
    """检查结果"""
    msg = [f" 检测方式为 {rule['type']}:{rule['val']}"]
    if response is None:
        return False, msg, None
    if rule['type'] == 'status':
        response_status = response.status_code
        if rule['op']=='==' and response_status == rule['val']:
            return True, msg, rule['res_d']
        if rule['op']=='!=' and response_status != rule['val']:
            return True, msg, rule['res_d']
        return False, msg, None

    if rule['type'] == 'regex':
        pattern = re.compile(rule['val'], re.MULTILINE)
        if rule['op'] == '==' and pattern.search(str(response.text)):
            print("[+] 匹配到结果")
            print(f"[+] 匹配到结果: {rule['val']}")
            print(f"响应内容: {response.text}")
            return True, msg, rule['res_d']
        if rule['op'] == '!=' and not pattern.search(str(response.text)):
            return True, msg, rule['res_d']

        if rule['op'] == '==' and pattern.search(str(response.content.decode())):
            return True, msg, rule['res_d']
        if rule['op'] == '!=' and not pattern.search(str(response.content.decode())):
            return True, msg, rule['res_d']

        if rule['op'] == '==':
            headers_str = '\n'.join([f"{k}: {v}" for k, v in response.headers.items()])
            if pattern.search(headers_str):
                return True, msg, rule['res_d']
        if rule['op'] == '!=':
            headers_str = '\n'.join([f"{k}: {v}" for k, v in response.headers.items()])
            if not pattern.search(headers_str):
                return True, msg, rule['res_d']
        return False, msg, None
    
    if rule['type'] == 'content':
        val = int(rule['val'])
        if response.status_code in [404 , 302, 301]:
            return False, msg, f"不通过，因为status_code:{response.status_code}"
        if rule['op'] == '==':
            if len(response.text) == val or len(response.content.decode()) == val:
                return True, msg, rule['res_d']
            return False, msg, None
        elif rule['op'] == '!=':
            if len(response.text) != val or len(response.content.decode()) != val:
                return True, msg, rule['res_d']
            return False, msg, None
        elif rule['op'] == '>':
            if len(response.text) >val or len(response.content.decode()) > val:
                return True, msg, rule['res_d']
        elif rule['op'] == '<':
            if len(response.text) < val or len(response.content.decode()) < val:
                return True, msg, rule['res_d']
        elif rule['op'] == '>=':
            if len(response.text) >= val or len(response.content.decode()) >=val:
                return True, msg, rule['res_d']
        elif rule['op'] == '<=':
            if len(response.text) <= val or len(response.content.decode()) <= val:
                return True, msg, rule['res_d']
        return False, msg, None
    if rule['type'] == 'oob':
        # oob检测逻辑暂时为空
        return True, "检测方式为 OOB", rule['res_d']

async def check_again_req(rule, url, client, error_log):
    plit = rule['val'].split('@', 1)
    val = plit[0]
    rq_url = url + plit[1]
    response = await request_with_tactics(
                client, 'GET', rq_url, error_log, retry_tatics=RETRY_TACTICS
                )
    n_rule = {
        "type": rule['type'],
        "val": val,
        'res_d': rule['res_d'],
        'op': rule['op'],
    }
    return check_result(n_rule, response)

def work_script(poc_id: list, urls: list, mode: str,error_log, result_log):
    """处理脚本"""
    conn, cursor = conn_script_db()
    if mode == "ALONE":
        for url in urls:
            for poc in poc_id:
                sqlre = qurery_poc_script(poc, cursor)
                try:
                    result = execute_script_main(sqlre['script_id'], url)
                    if result:
                        asyncio.run(write_result_log(result_log, "There is a security vulnerability", url, sqlre['poc_name'], " ", poc, f"执行脚本检测: {sqlre['script_id']}"))
                    else:
                        asyncio.run(write_result_log(result_log, "There is not a security vulnerability", url, sqlre['poc_name'], " ", poc, f"执行脚本检测: {sqlre['script_id']}"))
                except Exception as e:
                    asyncio.run(write_error_log(error_log, url, f" POC INFO: {poc}",f"ERROR: {e}"))
                    continue
    elif mode == "GROUP":
        for poc in poc_id:
            sqlre = qurery_poc_script(poc, cursor)
            for url in urls:
                try:
                    result = execute_script_main(sqlre['script_id'], url)
                    if result:
                        asyncio.run(write_result_log(result_log, "There is a security vulnerability", url, sqlre['poc_name'], " ", poc, f"执行脚本检测: {sqlre['script_id']}"))
                    else:
                        asyncio.run(write_result_log(result_log, "There is not a security vulnerability", url, sqlre['poc_name'], " ", poc, f"执行脚本检测: {sqlre['script_id']}"))
                except Exception as e:
                    asyncio.run(write_error_log(error_log, url, f" POC INFO: {poc}",f"ERROR: {e}"))
                    continue
    close_script_db(conn)

def execute_script_main(script_name, url):
    """
    动态执行脚本中的vulnerability_check方法
    """
    script_path = 'data/script'
    full_path = os.path.join(script_path, f"{script_name}")
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"脚本文件不存在: {full_path}")
    
    spec = importlib.util.spec_from_file_location(script_name, full_path)
    module = importlib.util.module_from_spec(spec)

    sys.modules[script_name] = module
    spec.loader.exec_module(module)
    
    if hasattr(module, 'vulnerability_check'):
        result = module.vulnerability_check(url)
        return result
    else:
        raise AttributeError(f"脚本 {script_name} 中没有定义vulnerability_check函数")