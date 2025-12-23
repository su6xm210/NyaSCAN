from PySide6.QtWidgets import (QVBoxLayout, QWidget, QTextBrowser, QFrame)


class AboutPage(QWidget):
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
        content = """<h1>关于</h1>
            <h2></h2>
            <p>更多请访问: https://github.com/su6xm210/NyaSCAN</p>
            """
        self.text_browser.setHtml(content)
