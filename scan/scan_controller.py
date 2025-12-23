import multiprocessing
import logging
from scan import NYAScanCroe as nyascan
import json


with open("config/network.json", "r") as f:
    config = json.load(f)
OutputDetailedInfo = config['OutputDetailedInfo']
if OutputDetailedInfo:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class ScanController:
    def __init__(self):
        self.scan_process = None
        self.is_running = False
        
    def start_scan(self, cfg_data):
        """
        启动扫描任务（使用进程）
        """
        if self.is_running:
            return False, "扫描已在运行中"
            
        try:
            # 使用进程运行扫描任务
            self.scan_process = multiprocessing.Process(
                target=self._run_scan, 
                args=(cfg_data,)
            )
            self.scan_process.start()
            self.is_running = True
            return True, "扫描已启动"
        except Exception as e:
            self.is_running = False
            return False, f"启动扫描时出错: {str(e)}"
    
    def _run_scan(self, cfg_data):
        try:
            result = nyascan.start_scan(cfg_data)
            if result != "完成":
                logger.error("扫描任务出错")
            else:
                logger.info("扫描已完成，进程结束")
        except Exception as e:
            logger.error("扫描进程异常终止: %s", str(e))
        finally:
            self.is_running = False
    
    def stop_scan(self):
        """
        停止扫描任务
        """
        if not self.is_running or not self.scan_process:
            return False, "没有正在运行的扫描任务"
        
        try:
            if self.scan_process.is_alive():
                self.scan_process.terminate()
                self.scan_process.join(timeout=5)
                
                if self.scan_process.is_alive():
                    self.scan_process.kill()
                    self.scan_process.join(timeout=2)
                    
            self.is_running = False
            self.scan_process = None
            return True, "扫描任务已停止"
        except Exception as e:
            return False, f"停止扫描时出错: {str(e)}"
    
    def is_scan_running(self):
        """
        检查扫描是否正在运行
        """
        if self.scan_process and self.scan_process.is_alive():
            return True
        elif self.scan_process and not self.scan_process.is_alive():
            self.is_running = False
            self.scan_process = None
        return self.is_running
    
    def get_scan_status(self):
        """
        获取扫描状态
        """
        if not self.is_running:
            return "空闲"
        elif self.scan_process and not self.scan_process.is_alive():
            return "已完成"
        else:
            return "运行中"

scan_controller = ScanController()

if __name__ == '__main__':
    multiprocessing.freeze_support()