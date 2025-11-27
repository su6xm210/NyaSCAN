from datetime import datetime
from pathlib import Path
from typing import Optional
import aiofiles


module_dir = Path(__file__).parent

def create_log_file(subffix: Optional[str] = '' ) -> Path:
    """创建日志"""
    time_str = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    log_dir = module_dir.parent / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    if subffix == '':
        file_path = log_dir / f"CORELOG_{time_str}"
    else:
        file_path = log_dir / f"{subffix}_result"
    file_path.write_text("", encoding='utf-8')
    return str(file_path)

async def write_error_log(
        log_path: Optional[str],
        content: str, 
        *args
    ):
    """写入错误日志"""
    try:
        file = Path(log_path)
        file.parent.mkdir(parents=True, exist_ok=True)
        time_str = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
        extra = " ".join(map(str, args)) if args else ""
        content = time_str + str(content) + ("--- For target:" + extra if extra else "")
        async with aiofiles.open(file, "a") as f:
            await f.write(content + "\n")
    except Exception as e:
        print("log write error:")
        print(e)

async def write_result_log(
        log_path: Optional[str],
        check_result: str,
        url: str = "",
        poc_name: str = "",
        *args
    ):
    """写入结果日志"""
    try:
        file = Path(log_path)
        file.parent.mkdir(parents=True, exist_ok=True)
        time_str = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
        extra = " ".join(map(str, args)) if args else ""

        content = time_str + url + " " +str(check_result) + " \"" + poc_name + "\" " + (extra if extra else "")
        async with aiofiles.open(file, "a") as f:
            await f.write(content + "\n")
    except Exception as e:
        print("log write error:")
        print(e)

if __name__ == "__main__":
    pass

