from scan import NYAScanCroe as nyascan

print("""
     $$\\   $$\\                      $$$$$$\\   $$$$$$\\   $$$$$$\\  $$\\   $$\\ 
     $$$\\  $$ |                    $$  __$$\\ $$  __$$\\ $$  __$$\\ $$$\\  $$ |
     $$$$\\ $$ |$$\\   $$\\  $$$$$$\\  $$ /  \\__|$$ /  \\__|$$ /  $$ |$$$$\\ $$ |
     $$ $$\\$$ |$$ |  $$ | \\____$$\\ \\$$$$$$\\  $$ |      $$$$$$$$ |$$ $$\\$$ |
     $$ \\$$$$ |$$ |  $$ | $$$$$$$ | \\____$$\\ $$ |      $$  __$$ |$$ \\$$$$ |
     $$ |\\$$$ |$$ |  $$ |$$  __$$ |$$\\   $$ |$$ |  $$\\ $$ |  $$ |$$ |\\$$$ |
     $$ | \\$$ |\\$$$$$$$ |\\$$$$$$$ |\\$$$$$$  |\\$$$$$$  |$$ |  $$ |$$ | \\$$ |
     \\__|  \\__| \\____$$ | \\_______| \\______/  \\______/ \\__|  \\__|\\__|  \\__|
               $$\\   $$ |                                                  
               \\$$$$$$  |                                                  
               \\______/                                                                                    
""")
print("感谢使用NyaSCAN WEB漏洞检测工具，本软件仅用于学习交流及授权环境下使用，请勿用于非法用途！！！")

nyascan.start_scan(cfg_data =  
                   {'urls': 
                    ['http://127.0.0.1:8808/'], 
                    'headers': ['User-Agent: 123',"Content-Type: 1233333"],
                    'selected_pocs': ["全量"], 
                    'concurrency': 16, 
                    'mode': 'ALONE', 
                    'use_poc_script': 'POC', 
                    'skip_write_content': True, 
                    'skip_verify_cookie': True, 
                    'enable_proxy': False, 
                    'skip_proxy_verify': False,
                    'max_retries': 0, 
                    'enable_retry_backoff': False
                    })
