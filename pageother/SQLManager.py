import sqlite3
import json
from time import time

def verify_pocid(poc_id: str ,verify: str = None)->list:
    if verify is None:
        conn = sqlite3.connect('./data/db/poc.db')
        db = "poc"
    else:
        conn = sqlite3.connect('./data/db/pocscript.db')
        db = "pocscript"
    cursor = conn.cursor()
    cursor.execute(f"SELECT poc_id FROM {db} WHERE poc_id = ?", (poc_id,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return True
    else:
        return False

def insert_poc(data: dict)->bool:
    conn = sqlite3.connect('./data/db/poc.db')
    cursor = conn.cursor()
    create_time = str(int(time()))
    request_json = json.dumps(data['request'], ensure_ascii=False)
    payloads_json = json.dumps(data['payloads'], ensure_ascii=False)
    rules_json = json.dumps(data['rules'], ensure_ascii=False)
    cursor.execute('''
        INSERT INTO poc (
            poc_id,
            vul_name,
            vul_id,
            vul_type,
            vul_level,
            enabled,
            need_cookie,
            write_content,
            created_time,
            request,
            payloads,
            rules
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',(
            data['basic_info']['poc_id'],
            data['basic_info']['vul_name'],
            data['basic_info']['vul_id'],
            data['basic_info']['vul_type'],
            data['basic_info']['vul_level'],
            data['config']['enabled'],
            data['config']['need_cookie'],
            data['config']['write_content'],
            create_time,
            request_json,
            payloads_json,
            rules_json
        ))
    conn.commit()
    cursor.close()
    return True

def get_poc_info(page=1, page_size=100, verify: str = None)->list:
    if verify is None:
        conn = sqlite3.connect('./data/db/poc.db')
        db = "poc"
    else:
        conn = sqlite3.connect('./data/db/pocscript.db')
        db = "pocscript"
    cursor = conn.cursor()
    offset = (page - 1) * page_size
    cursor.execute(f"""SELECT created_time, poc_id, vul_name, vul_id, vul_type, vul_level, enabled 
                      FROM {db} 
                      ORDER BY created_time DESC
                      LIMIT ? OFFSET ?""", (page_size, offset))
    info = cursor.fetchall()
    cursor.close()
    return info

def get_total_poc_count(verify: str = None)->int:
    if verify is None:
        conn = sqlite3.connect('./data/db/poc.db')
        db = "poc"
    else:
        conn = sqlite3.connect('./data/db/pocscript.db')
        db = "pocscript" 
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {db}" )
    count = cursor.fetchone()[0]
    cursor.close()
    return count

def query_poc(search_keyword: str, page=1, page_size=100,  verify: str = None)->list:
    if verify is None:
        conn = sqlite3.connect('./data/db/poc.db')
        db = "poc"
    else:
        conn = sqlite3.connect('./data/db/pocscript.db')
        db = "pocscript"
    cursor = conn.cursor()
    search_pattern = f"%{search_keyword}%"
    offset = (page - 1) * page_size
    cursor.execute(f"""SELECT created_time, poc_id, vul_name, vul_id, vul_type, vul_level, enabled 
                      FROM {db} 
                      WHERE vul_name LIKE ? OR vul_id LIKE ? OR vul_type LIKE ? OR poc_id LIKE ?
                      ORDER BY created_time DESC
                      LIMIT ? OFFSET ?""",
                   (search_pattern, search_pattern, search_pattern,search_pattern, page_size, offset))
    info = cursor.fetchall()
    cursor.close()
    return info

def get_poc_count(search_keyword: str, verify: str = None)->int:
    if verify is None:
        conn = sqlite3.connect('./data/db/poc.db')
        db = "poc"
    else:
        conn = sqlite3.connect('./data/db/pocscript.db')
        db = "pocscript"
    cursor = conn.cursor()
    search_pattern = f"%{search_keyword}%"
    cursor.execute(f"""SELECT COUNT(*) 
                      FROM {db} 
                      WHERE poc_id LIKE ? OR vul_name LIKE ? OR vul_id LIKE ? OR vul_type LIKE ? OR poc_id LIKE ? """,
                   (search_pattern, search_pattern, search_pattern,search_pattern, search_pattern))
    count = cursor.fetchone()[0]
    cursor.close()
    return count

def query_poc_info(poc_id: str):
    conn = sqlite3.connect('./data/db/poc.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT 
        created_time, 
        poc_id, 
        vul_name, 
        vul_id, 
        vul_type, 
        vul_level, 
        enabled, 
        need_cookie, 
        write_content, 
        created_time, 
        request, 
        payloads, 
        rules 
        FROM poc WHERE poc_id = ?""", (poc_id,))
    info = cursor.fetchone()
    cursor.close()
    return info

def query_poc_script_info(poc_id: str):
    conn = sqlite3.connect('./data/db/pocscript.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT 
        created_time, 
        poc_id, 
        vul_name, 
        vul_id, 
        vul_type, 
        vul_level, 
        enabled, 
        need_cookie, 
        write_content, 
        created_time, 
        scriptname
        FROM pocscript WHERE poc_id = ?""", (poc_id,))
    info = cursor.fetchone()
    cursor.close()
    return info

def delete_poc_info(poc_id: str, verify: str = None)->bool:
    if verify is None:
        conn = sqlite3.connect('./data/db/poc.db')
        db = "poc"
    else:
        conn = sqlite3.connect('./data/db/pocscript.db')
        db = "pocscript"
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {db} WHERE poc_id = ?", (poc_id,))
    conn.commit()
    cursor.close()
    return True

def update_poc(data: dict)->bool:
    conn = sqlite3.connect('./data/db/poc.db')
    cursor = conn.cursor()
    request_json = json.dumps(data['request'], ensure_ascii=False)
    payloads_json = json.dumps(data['payloads'], ensure_ascii=False)
    rules_json = json.dumps(data['rules'], ensure_ascii=False)
    cursor.execute('''
        UPDATE poc SET
            vul_name = ?,
            vul_id = ?,
            vul_type = ?,
            vul_level = ?,
            enabled = ?,
            need_cookie = ?,
            write_content = ?,
            request = ?,
            payloads = ?,
            rules = ?
        WHERE poc_id = ?
        ''',(
            data['basic_info']['vul_name'],
            data['basic_info']['vul_id'],
            data['basic_info']['vul_type'],
            data['basic_info']['vul_level'],
            data['config']['enabled'],
            data['config']['need_cookie'],
            data['config']['write_content'],
            request_json,
            payloads_json,
            rules_json,
            data['basic_info']['poc_id']
        ))
    conn.commit()
    cursor.close()
    return True

def insert_poc_script(data: dict)->bool:
    conn = sqlite3.connect('./data/db/pocscript.db')
    cursor = conn.cursor()
    create_time = str(int(time()))
    cursor.execute('''
        INSERT INTO pocscript (
            poc_id,
            vul_name,
            vul_id,
            vul_type,
            vul_level,
            enabled,
            need_cookie,
            write_content,
            created_time,
            scriptname
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',(
            data['poc_id'],
            data['vul_name'],
            data['vul_id'],
            data['vul_type'],
            data['vul_level'],
            data['enabled'],
            data['need_cookie'],
            data['write_content'],
            create_time,
            data['scriptname']
            
        ))
    conn.commit()
    cursor.close()
    return True

def update_poc_script(data: dict)->bool:
    conn = sqlite3.connect('./data/db/pocscript.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE pocscript SET
            vul_name = ?,
            vul_id = ?,
            vul_type = ?,
            vul_level = ?,
            enabled = ?,
            need_cookie = ?,
            write_content = ?,
            scriptname = ?     
        WHERE poc_id = ?
        ''',(
            data['vul_name'],
            data['vul_id'],
            data['vul_type'],
            data['vul_level'],
            data['enabled'],
            data['need_cookie'],
            data['write_content'],
            data['scriptname'],
            data['poc_id']
        ))
    conn.commit()
    cursor.close()
    return True