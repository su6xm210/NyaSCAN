from PySide6.QtWidgets import (QVBoxLayout, QWidget, QTextBrowser, QFrame)


class HomePage(QWidget):
    def __init__(self, title="", object_name=""):
        super().__init__()
        self.title = title
        self.setObjectName(object_name)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.content_frame = QFrame()
        self.content_frame.setFrameStyle(QFrame.NoFrame)
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setStyleSheet("""
            QTextBrowser {
                border: none;
                background-color: white;
                padding: 0;
                font-size: 14px;
                line-height: 1.6;
                color: #333;
            }
            
            QTextBrowser h1 {
                color: #1a1a1a;
                font-size: 24px;
                margin-top: 0;
                margin-bottom: 15px;
                font-weight: bold;
            }
            
            QTextBrowser h2 {
                color: #2d5caa;
                font-size: 20px;
                margin-top: 25px;
                margin-bottom: 15px;
                font-weight: 600;
            }
            
            QTextBrowser h3 {
                color: #4a4a4a;
                font-size: 18px;
                margin-top: 20px;
                margin-bottom: 10px;
                font-weight: 500;
            }
            
            QTextBrowser p {
                margin: 10px 0;
                text-align: left;
            }
            
            QTextBrowser ul {
                margin: 10px 0;
                padding-left: 20px;
            }
            
            QTextBrowser li {
                margin: 5px 0;                           
            }
            
            QTextBrowser strong {
                color: #2d5caa;
            }
            
            QTextBrowser em {
                color: #666;
            }
            
            QTextBrowser hr {
                border: 1px solid #e0e0e0;
                margin: 20px 0;
            }
            
            QTextBrowser blockquote {
                border-left: 4px solid #2d5caa;
                padding-left: 15px;
                margin: 20px 0;
                color: #666;
                font-style: italic;
            }
        """)
        
        content_layout.addWidget(self.text_browser)
        
        layout.addWidget(self.content_frame)
        
        self.init_content()
        
    def init_content(self):
        content = """<h1>欢迎使用 NyaSCAN Web漏洞扫描器</h1>
            <h2>📖简介</h2>
            <p>NyaSCAN 是一个页面简洁的图形化漏洞扫描/检测工具，用于Web安全和Python的学习交流。</p>
            <p>开发环境是Python3.12+Windows11。本工具收集的漏洞信息均来源于互联网公开渠道。</p>
            <p>⚠️   NyaScan 仅限用于<b>授权的安全测试</b>和<b>教育学习目的</b>。未经授权对任何系统进行扫描是非法的。</p>
            <p>⚠️   使用者应对其行为负全部责任。开发者和贡献者不对任何误用或损害承担责任。</p>
            <p>⚠️   <b>请务必在获得明确授权的前提下使用本工具 ！！！</b></p>

            <h3>✨主要功能</h3>
            <ul>
            <li><strong>多类型漏洞检测</strong>：支持多种常见Web漏洞检测</li>
            <li><strong>自定义POC</strong>：可以编写和管理自己的检测规则</li>
            &#10;
            <li><strong>批量扫描</strong>：支持对多个目标进行并发扫描</li>
            &#10;
            <li><strong>代理支持</strong>：内置代理功能，方便调试和测试</li>
            &#10;
            </ul>

            <h2>🚀快速开始</h2>
            <h3>1. 创建POC</h3>
            <p>在"PoC"菜单中选择"新建"来创建新的检测规则。</p>
            <p>
                <li><b>1.</b>如果检测规则需要发起请求，请选择"二次请求"</li>
                <li>&nbsp;&nbsp;&nbsp;填写格式: 匹配值@路径。如选择响应码做检测，则是：200@/this/is/a/path.jsp</li>
                <li>&nbsp;&nbsp;&nbsp;请求是GET请求，全局分割字符串方式为从左开始分割一次</li>
                <li><b>2.</b>对于检测中的正则匹配，不进行跨行匹配</li>
                <li><b>3.</b>"需要验证cookie这个"这个选项指请求包需要Cookie/Authorization等参数</li>
                <li><b>4.</b>"如果payload在header/body的某处，建议使用占位符"PAYLOAD"进行填写，在执行扫描时POC内置的header会覆盖扫描传入的同字段header</li>
                <li>&nbsp;&nbsp;&nbsp;请求信息的头，如:Authorization:PAYLOAD </li>
                <li>&nbsp;&nbsp;&nbsp;payload填写具体值，如:'cat /etc/passwd</li>
            </p>

            <h3>2. 配置扫描任务</h3>
            <p>进入"扫描"页面，配置目标URL、请求头和其他扫描参数。</p>
            <p>在"POC选择"项中，如果输入的是POCID那么只会执行输入的POCID用于验证POC或单POC扫描</p>
            <p>
            <p><b>扫描参数</b></p>
                <li><b>1.</b>并发数: 同时发起请求数。如果使用GROUP模式，则是根据URL数和并发数最小的启动。</li>
                <li><b>2.</b>执行的POC类型: 这个选项是为了在选择某类漏洞类型时，选择是使用脚本还是POC库的内容执行</li>
                <li><b>3.</b>跳过写入内容的POC: 指跳过会在目标机器生成文件、修改内容等有影响到目标系统的POC</li>
                <li><b>4.</b>跳过验证Cookie的POC: 这个选项一般指的的是跳过在后台执行的POC</li>
                <li>&nbsp;</li>
                <li>注：如果选择脚本执行，请确保新添加的脚本使用的模块已经安装在环境中</li>
            </p>

            <h3>3. 执行扫描</h3>
            <p>点击"执行"按钮启动扫描任务。</p>
            <h3>4. 查看结果/停止扫描</h3>
            <p>点击"任务"可以查看结果/停止正在执行的扫描任务。</p>
            """
        self.text_browser.setHtml(content)