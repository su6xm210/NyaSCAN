import sqlite3
import random
import time

conn = sqlite3.connect('./data/db/pocscript.db')
cur = conn.cursor()

count = 0
while count < 200: 
    poc_id = 'poc_id_' + str(random.randint(1, 100000000))
    vul_name = 'vul_name_' + str(random.randint(1, 100000000))
    vul_id = 'vul_id_' + str(random.randint(1, 100000000))
    scriptname = 'scriptname_' + str(random.randint(1, 100000000))
    ctime = str(int(time.time()))
    
    sql = """
        INSERT INTO pocscript (poc_id, vul_name, vul_id, vul_type, vul_level, enabled, need_cookie, write_content, created_time, scriptname) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur.execute(sql, (poc_id, vul_name, vul_id, '信息泄露', 'high', True, True, True, ctime, scriptname))
    
    count += 1
    
    if count % 50 == 0:
        conn.commit()
        print(f"已插入 {count} 条记录")


conn.commit()
print(f"总共插入 {count} 条记录")

conn.close()