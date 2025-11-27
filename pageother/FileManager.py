from typing import Optional, Dict, Any
import re
import time
import random
import zipfile
import os

from pageother.SQLManager import verify_pocid


def generate_poc_id()-> str:
    random_num = random.randint(100, 999)
    return "POC-" + time.strftime("%y%m%d-%H%M%S-", time.localtime()) + str(random_num)

def gerenate_file_id(poc_id: Optional["str"])-> str:
    x = poc_id.replace("-", "_")
    return x+".py"

def copy_save_file(source_file_path: Optional["str"], target_file_path: Optional["str"]) -> Dict[str, Any]:
    try:
        with open(source_file_path, 'rb') as f:
            code = f.read()
        with open(target_file_path, 'wb') as f:
            f.write(code)
        return True
    except Exception as e:
        return e

def verify_py_script(file_path: Optional["str"]) -> Dict[str, Any]:
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            code = f.read()
        matches = re.findall(r'return|vulnerability_check\(', code)
        if(len(matches) == 0): return False
        return True
    except Exception as e:
        return e

def export_data(file_path: str) -> bool:
    try:
        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            if os.path.exists('./data/db/poc.db'):
                zf.write('./data/db/poc.db', './db/poc.db')
            if os.path.exists('./data/db/pocscript.db'):
                zf.write('./data/db/pocscript.db', './db/pocscript.db')
            if os.path.exists('./data/script'):
                for root, dirs, files in os.walk('./data/script'):
                    for file in files:
                        file_path = os.path.join(root, file)
                        archive_path = os.path.relpath(file_path, './data')
                        zf.write(file_path, archive_path)
        return True
    except Exception:
        return False

def import_data(file_path: str) -> bool:
    with zipfile.ZipFile(file_path, 'r') as zf:
        zf.extractall('./data')
    return True

def clear_script():
    try:
        path = './data/script'
        items = os.listdir(path)
        files = [item for item in items if os.path.isfile(os.path.join(path, item))]
        for file in files:
            f = file.replace('.py', '') 
            f = f.replace('_', '-')
            if not verify_pocid(f,1):
                print(f"删除无对应POC的脚本: {file}")
                os.remove(os.path.join(path, file))
        return True 
    except Exception as e:
        print(f"清理脚本时出错: {e}")
        return False