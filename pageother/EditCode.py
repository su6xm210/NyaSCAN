from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
from PySide6.QtCore import Qt
from qfluentwidgets import (
    SubtitleLabel, PlainTextEdit, ToolButton, FluentIcon as FIF,
    InfoBar, InfoBarPosition, PushButton
)

import os

class CodeEditor(PlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLineWrapMode(PlainTextEdit.NoWrap)
        
        font = self.font()
        font.setFamily("Consolas")
        font.setPointSize(12)
        self.setFont(font)


class EditPythonPage(QWidget):
    def __init__(self, title="", object_name="", parent=None):
        super().__init__(parent)
        
        if object_name:
            self.setObjectName(object_name)
            
        self.current_file_path = None
        self.is_new_file = False  
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        self.title_label = SubtitleLabel(self.tr("代码编辑器"), self)
        layout.addWidget(self.title_label)
        
        toolbar_layout = QHBoxLayout()
        
        self.new_button = ToolButton(FIF.ADD)
        self.new_button.setToolTip(self.tr("新建文件"))
        self.new_button.clicked.connect(self.new_file)
        
        self.open_button = ToolButton(FIF.FOLDER)
        self.open_button.setToolTip(self.tr("打开文件"))
        self.open_button.clicked.connect(self.open_file)
        
        self.save_button = ToolButton(FIF.SAVE)
        self.save_button.setToolTip(self.tr("保存文件"))
        self.save_button.clicked.connect(self.save_file)
        
        self.save_as_button = ToolButton(FIF.SAVE_AS)
        self.save_as_button.setToolTip(self.tr("另存为"))
        self.save_as_button.clicked.connect(self.save_as_file)
        
        self.file_path_label = QLabel(self.tr("未打开文件"))
        self.file_path_label.setStyleSheet("color: gray;")
        
        toolbar_layout.addWidget(self.new_button)
        toolbar_layout.addWidget(self.open_button)
        toolbar_layout.addWidget(self.save_button)
        toolbar_layout.addWidget(self.save_as_button)
        toolbar_layout.addSpacing(20)
        toolbar_layout.addWidget(self.file_path_label)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        self.editor = CodeEditor(self)
        self.editor.setPlaceholderText(self.tr("在这里输入Python代码..."))
        layout.addWidget(self.editor)
        
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel(self.tr("就绪"))
        self.status_label.setStyleSheet("color: gray;")
        
        self.example_buttons_layout = QHBoxLayout()
        
        
        class_button = PushButton(self.tr("Script模板"))
        class_button.clicked.connect(self.insert_script_template)
        class_button.setFixedWidth(120)
        
        self.example_buttons_layout.addWidget(class_button)
        self.example_buttons_layout.addStretch()
        
        status_layout.addWidget(self.status_label)
        status_layout.addLayout(self.example_buttons_layout)
        
        layout.addLayout(status_layout)
        
    def new_file(self):
        """新建文件"""
        self.editor.clear()
        self.current_file_path = None
        self.is_new_file = True  
        self.file_path_label.setText(self.tr("未保存的文件"))
        self.status_label.setText(self.tr("已创建新文件"))
        
    def open_file(self):
        """打开文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("打开Python/配置文件"),
            "",
            self.tr("Code Files (*.py *.json *.yaml *.yml);;All Files (*)")
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.editor.setPlainText(content)
                self.current_file_path = file_path
                self.is_new_file = False  
                self.file_path_label.setText(file_path)
                self.status_label.setText(self.tr(f"已打开: {os.path.basename(file_path)}"))
                
            except Exception as e:
                InfoBar.error(
                    title=self.tr("打开文件失败"),
                    content=self.tr(f"无法打开文件: {str(e)}"),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
    
    def save_file(self):
        """保存文件"""
        if self.is_new_file or self.current_file_path is None:
            self.save_as_file()
        else:
            try:
                content = self.editor.toPlainText()
                with open(self.current_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.status_label.setText(self.tr(f"已保存: {os.path.basename(self.current_file_path)}"))
                InfoBar.success(
                    title=self.tr("保存成功"),
                    content=self.tr("文件已保存"),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=1500,
                    parent=self
                )
            except Exception as e:
                InfoBar.error(
                    title=self.tr("保存失败"),
                    content=self.tr(f"无法保存文件: {str(e)}"),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
    
    def save_as_file(self):
        """另存为文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("保存Python文件"),
            "",
            self.tr("Python Files (*.py);;All Files (*)")
        )
        
        if file_path:
            if not file_path.endswith('.py'):
                file_path += '.py'
                
            try:
                content = self.editor.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.current_file_path = file_path
                self.is_new_file = False  
                self.file_path_label.setText(file_path)
                self.status_label.setText(self.tr(f"已保存: {os.path.basename(file_path)}"))
                InfoBar.success(
                    title=self.tr("保存成功"),
                    content=self.tr("文件已保存"),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=1500,
                    parent=self
                )
            except Exception as e:
                InfoBar.error(
                    title=self.tr("保存失败"),
                    content=self.tr(f"无法保存文件: {str(e)}"),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
    
    def insert_script_template(self):
        """插入类模板"""
        class_code = '''
# 自定义POC检测脚本模板
# 模块导入
from typing import Optional, Dict, Any

# 主方法
def vulnerability_check(url: Optional[str],
                )->bool:
    """
    用于被扫描器调用的主方法
    Args:
        url: 由扫描器传入的目标地址
    Return:
        返回True(存在漏洞)或者False(不存在漏洞)
    """
    # TODO:下面写你的检测漏洞脚本，存在返回True不存在返回False

    


    
    return True
'''
        self.editor.setPlainText(class_code)
        self.status_label.setText(self.tr("已插入Script模板"))