from scan import VerifyScanCFG as vscf

import re
import sqlite3


class Tactics:
    def __init__(self, cfg_data, mode="gui", skip_proxy_verify = False):
        self.mode = mode
        self.skip_proxy_verify = cfg_data['skip_proxy_verify']
        self.is_valid, self.msg = self._scan_cfg(cfg_data)
        if not self.is_valid:
            raise ValueError(f"配置无效: {self.msg}")
        self.cfg_data = self.msg
        self._cfg_data_selected_pocs_()
    
    def _scan_cfg(self, cfg_data):
        if self.mode == "terminal":
            is_valid, msg = vscf.verify_scan_cfg(cfg_data)
            if not is_valid:
                print("输入选项错误："+msg)
                return False, msg
        if cfg_data['enable_proxy'] is True:
            proxy_valid, proxy_msg = vscf.start_proxy()
            if not proxy_valid:
                return False, proxy_msg
            if self.skip_proxy_verify is False:
                for i in proxy_msg['Proxy']["Addresses"]:
                    if not vscf.verify_proxy(i):
                        return False, f"Invalid proxies infomation address: {i}"
            cfg_data['Proxy'] = proxy_msg['Proxy']["Addresses"]
            cfg_data['EnableRotation'] = proxy_msg['Proxy']["EnableRotation"]
        else:
            cfg_data['Proxy'] = None
            cfg_data['EnableRotation'] = None
        return True, cfg_data
    
    def _cfg_data_selected_pocs_(self):
        if "全量" in self.cfg_data['selected_pocs']:
            self.cfg_data['selected_pocs'] = ["全量"]
        if "全部脚本" in self.cfg_data['selected_pocs'] and "全部POC" in self.cfg_data['selected_pocs']:
            self.cfg_data['selected_pocs'] = ["全量"]


class Poc:
    def __init__(self, cfg_data):
        self.cfg_data = cfg_data
        self.selected_pocs = self.cfg_data['selected_pocs']
        self.use_poc_script = self.cfg_data['use_poc_script']
        self.skip_verify_cookie = self.cfg_data['skip_verify_cookie']
        self.skip_write_content = self.cfg_data['skip_write_content']

    def get_pocid(self):
        other_args = ''
        if self.skip_verify_cookie:
            other_args += 'AND need_cookie = 0 '
        if self.skip_write_content:
            other_args += 'AND write_content = 0 '

        if "全量" in self.selected_pocs:
            select_poc_sql = f"SELECT poc_id FROM poc WHERE enabled = 1 {other_args}"
            conn_poc, cursor_poc = self._make_poc_conn()
            poc_id = cursor_poc.execute(select_poc_sql).fetchall()
            conn_poc.close()

            select_pocscript_sql = f"SELECT poc_id FROM pocscript WHERE enabled = 1 {other_args}"
            conn_pocscript, cursor_pocscript = self._make_pocscript_conn()
            pocscript_id = cursor_pocscript.execute(select_pocscript_sql).fetchall()       
            conn_pocscript.close()

            return self._consvert_list(poc_id), self._consvert_list(pocscript_id)
        elif "全部POC" in self.selected_pocs:
            select_poc_sql = f"SELECT poc_id FROM poc WHERE enabled = 1 {other_args}"
            conn_poc, cursor_poc = self._make_poc_conn()
            poc_id = cursor_poc.execute(select_poc_sql).fetchall()
            conn_poc.close()
            return self._consvert_list(poc_id), None
        elif "全部脚本" in self.selected_pocs:
            select_pocscript_sql = f"SELECT poc_id FROM pocscript WHERE enabled = 1 {other_args}"
            conn_pocscript, cursor_pocscript = self._make_pocscript_conn()
            pocscript_id = cursor_pocscript.execute(select_pocscript_sql).fetchall()
            conn_pocscript.close()
            return None, self._consvert_list(pocscript_id)
        else:
            pattern = r'^POC-|^SCRIPT-'
            re_result = re.match(pattern, self.selected_pocs[0])
            if re_result:
                poc = []
                pocscript = []
                for i in self.selected_pocs:
                    if 'POC' in i:
                        poc.append(i)
                    elif 'SCRIPT' in i:
                        pocscript.append(i)
                return poc, pocscript
            else:
                vuln_type = "','".join(self.selected_pocs) 
                if 'POC' in self.use_poc_script:
                    select_poc_sql = f"SELECT poc_id FROM poc WHERE vul_type IN ('{vuln_type}') AND enabled = 1 {other_args}"
                    conn_poc, cursor_poc = self._make_poc_conn()                    
                    poc_id = cursor_poc.execute(select_poc_sql).fetchall()
                    conn_poc.close()
                    
                    return self._consvert_list(poc_id), None
                if '脚本' in self.use_poc_script:
                    select_pocscript_sql = f"SELECT poc_id FROM pocscript WHERE vul_type IN ('{vuln_type}') AND enabled = 1 {other_args}"
                    conn_pocscript, cursor_pocscript = self._make_pocscript_conn()
                    pocscript_id = cursor_pocscript.execute(select_pocscript_sql).fetchall()
                    conn_pocscript.close()

                    return None, self._consvert_list(pocscript_id)
                if '全部' in self.use_poc_script:
                    print("全部")
                    select_poc_sql = f"SELECT poc_id FROM poc WHERE vul_type IN ('{vuln_type}') AND enabled = 1 {other_args}"
                    conn_poc, cursor_poc = self._make_poc_conn()
                    poc_id = cursor_poc.execute(select_poc_sql).fetchall()
                    conn_poc.close()

                    select_pocscript_sql = f"SELECT poc_id FROM pocscript WHERE vul_type IN ('{vuln_type}') AND enabled = 1 {other_args}"
                    conn_pocscript, cursor_pocscript = self._make_pocscript_conn()
                    pocscript_id = cursor_pocscript.execute(select_pocscript_sql).fetchall()
                    conn_pocscript.close()

                    return self._consvert_list(poc_id), self._consvert_list(pocscript_id)
        return None, None
    
    def _make_poc_conn(self):
        conn_poc = sqlite3.connect('./data/db/poc.db')
        cursor_poc = conn_poc.cursor()
        return conn_poc, cursor_poc
    
    def _make_pocscript_conn(self):
        conn_pocscript = sqlite3.connect('./data/db/pocscript.db')
        cursor_pocscript = conn_pocscript.cursor()
        return conn_pocscript, cursor_pocscript

    def _consvert_list(self, poc_id: list):
        return list(map(lambda x: x[0], poc_id))