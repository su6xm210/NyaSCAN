from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QTimer, QEventLoop, QSize
from PySide6.QtGui import QIcon
import platform
import sys
import os
from contextlib import redirect_stdout
with open(os.devnull, 'w') as f, redirect_stdout(f):
    from qfluentwidgets import (
        FluentWindow, NavigationItemPosition, FluentIcon as FIF, SplashScreen)
from pagepoc.NewPOC import NewPOC
from pagepoc.ShowPOCInfo import ShowPocInfo
from pagepoc.ModifyPOC import ModifyPOC
from pagepoc.NewPOCScript import NewPOCScript
from pagepoc.ShowPOCScriptInfo import ShowPocScriptInfo
from pageother.NetworkSet import ProxyPage
from pageother.ImportExport import ImportExportPage
from pageother.EditCode import EditPythonPage
from pageother.Scan import ScanPage
from pageother.ScanTask import ScanTaskPage
from pageother.HomePage import HomePage
from pageother.About import AboutPage


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NyaSCAN - WEB漏洞扫描器")
        self.setWindowIcon(QIcon('data/pictrue/nyascan.jpg'))
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(300, 300))

        self.splashScreen.raise_()

        self.resize(1300, 800)
        self.center_window()
        self.show()
        self.init_pages()
        self.navigationInterface.setExpandWidth(180)
        self.splashScreen.finish()
    
    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)

    def init_pages(self):
        loop = QEventLoop(self)
        QTimer.singleShot(888, loop.quit)
        loop.exec()
        
        self.home_page = HomePage("开始", "homePage")

        self.poc_list_page = ShowPocInfo("", "ShowPocInfoPage")
        self.poc_new_page = NewPOC("新建POC","NewPOCPage") 
        self.poc_plugin_page = ShowPocScriptInfo("POC检测的Python代码", "ShowPocScriptInfo")
        self.poc_plugin_new_page = NewPOCScript("新建POC脚本", "NewPOCScriptPage") 

        self.scan_page = ScanPage("扫描", "ScanPage")
        self.scan_history_page = ScanTaskPage("任务", "ScanTaskPage")
        
        self.proxy_page = ProxyPage("代理", "ProxyPage")
        self.edit_python_page = EditPythonPage("编辑代码", "EditPython")
        self.iepage = ImportExportPage("导入导出", "ImportExport")
        self.about_page = AboutPage("关于", "aboutPage")

        self.addSubInterface(self.home_page, FIF.HOME, "开始")
        
        poc_group_widget = QWidget()
        poc_group_widget.setObjectName("pocGroupWidget")
        poc_group_interface = self.addSubInterface(poc_group_widget, FIF.FOLDER, "PoC")
        self.addSubInterface(self.poc_list_page, FIF.ZOOM, "列表", parent=poc_group_widget)
        self.addSubInterface(self.poc_new_page, FIF.ADD, "新建", parent=poc_group_widget)
        self.addSubInterface(self.poc_plugin_page, FIF.CODE, "Py信息", parent=poc_group_widget)
        self.addSubInterface(self.poc_plugin_new_page, FIF.ADD, "Py新建", parent=poc_group_widget)
        
        self.addSubInterface(self.scan_page, FIF.PLAY, "扫描")
        self.addSubInterface(self.scan_history_page, FIF.HISTORY, "任务")
        
        self.addSubInterface(self.proxy_page, FIF.GLOBE, "代理")
        self.addSubInterface(self.edit_python_page, FIF.EDIT, "编辑代码")
        self.addSubInterface(self.iepage, FIF.SHARE, "导入导出")
        
        self.addSubInterface(self.about_page, FIF.INFO, "关于", position=NavigationItemPosition.BOTTOM)
        self.switchTo(self.home_page)

        poc_group_interface.clicked.connect(lambda: self.switchTo(self.poc_list_page))
        
        self.poc_list_page.modify_poc_requested.connect(self.switch_to_modify_page)
        
    def switch_to_modify_page(self, poc_info):
        for i in range(self.stackedWidget.count()):
            widget = self.stackedWidget.widget(i)
            if isinstance(widget, ModifyPOC):
                self.stackedWidget.removeWidget(widget)
                break
        modify_page = ModifyPOC(poc_info, "ModifyPOCPage")
        modify_page.cancel_editing.connect(self.return_to_poc_list)
        
        self.stackedWidget.addWidget(modify_page)
        self.stackedWidget.setCurrentWidget(modify_page)

    def return_to_poc_list(self):
        self.switchTo(self.poc_list_page)
        
        for i in range(self.stackedWidget.count()):
            widget = self.stackedWidget.widget(i)
            if isinstance(widget, ModifyPOC):
                self.stackedWidget.removeWidget(widget)
                widget.deleteLater()
                break
        
        self.poc_list_page.load_poc_data()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    system = platform.system()
    if system != "Windows":
        app.setStyle('Fusion')
        app.setStyleSheet("""
            QWidget {
                color: #000000;
                background-color: #ffffff;
            }
            QTableWidget {
            alternate-background-color: #f0f0f0;
            background-color: white;
            gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                color: black;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
    app.setWindowIcon(QIcon("data/pictrue/nyascan.jpg"))
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
    win = MainWindow()
    sys.exit(app.exec())