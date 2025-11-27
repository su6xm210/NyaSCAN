from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QFormLayout, QGroupBox, QScrollArea, QFileDialog
)
from PySide6.QtCore import Qt
from qfluentwidgets import (
    SubtitleLabel, LineEdit as FluentLineEdit, 
    ComboBox as FluentComboBox, CheckBox as FluentCheckBox, 
    PushButton as FluentPushButton, FluentIcon as FIF,
    InfoBar, InfoBarPosition
)

import os

from pageother import FileManager as fm
from pageother import SQLManager as sqlm
from pagepoc import StyleFile


class NewPOCScript(QWidget):
    def __init__(self, title: str, object_name: str = None):
        super().__init__()
        if object_name:
            self.setObjectName(object_name)
        self.init_ui()
    
    def init_ui(self):
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")

        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        title_label = SubtitleLabel("新建POC-Python脚本")
        layout.addWidget(title_label)
        
        self._setup_form_area(layout)
        
        self._setup_action_buttons(layout)
        
        scroll_area.setWidget(content_widget)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
        self._connect_signals()
        
    def _setup_form_area(self, parent_layout):
        """设置表单区域"""
        form_group = QGroupBox("脚本信息")
        form_group.setStyleSheet(StyleFile.group_qss)
        form_layout = QFormLayout(form_group)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(12)
        
        self.vul_name = FluentLineEdit()
        self.vul_name.setPlaceholderText("输入漏洞名称")
        self.vul_name.setStyleSheet(StyleFile.line_edit_qss)
        form_layout.addRow("漏洞名称", self.vul_name)
        
        self.vul_id = FluentLineEdit()
        self.vul_id.setPlaceholderText("输入漏洞编号")
        self.vul_id.setStyleSheet(StyleFile.line_edit_qss)
        form_layout.addRow("漏洞编号", self.vul_id)

        self.vul_type = FluentComboBox()
        self.vul_type.addItems([
            "信息泄露", "跨站脚本(XSS)", "SQL注入", "其他注入", "反序列化", "命令执行", "任意代码执行", 
            "文件类", "未授权", "请求伪造(CSRF/SSRF)", "目录类漏洞", "拒绝服务"
        ])
        form_layout.addRow("漏洞类型", self.vul_type)

        self.vul_level = FluentComboBox()
        self.vul_level.addItems(["低危", "中危", "高危"])
        form_layout.addRow("危害等级", self.vul_level)
                
        self.enabled_check = FluentCheckBox("启用该POC")
        self.enabled_check.setChecked(True)
        form_layout.addRow("状态", self.enabled_check)
        
        self.cookie_check = FluentCheckBox("需要验证Cookie")
        self.cookie_check.setChecked(False)
        form_layout.addRow("", self.cookie_check)
        
        self.content_check = FluentCheckBox("会对目标写入内容")
        self.content_check.setChecked(False)
        form_layout.addRow("", self.content_check)
        
        file_layout = QHBoxLayout()
        self.file_path_edit = FluentLineEdit()
        self.file_path_edit.setPlaceholderText("请选择Python脚本文件")
        self.file_path_edit.setReadOnly(True)
        
        self.file_browse_button = FluentPushButton(FIF.FOLDER, "浏览")
        
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(self.file_browse_button)
        form_layout.addRow("脚本文件", file_layout)
        
        parent_layout.addWidget(form_group)
        
    def _setup_action_buttons(self, parent_layout):
        """设置操作按钮"""
        button_layout = QHBoxLayout()
        
        self.save_button = FluentPushButton(FIF.SAVE, "保存")
        self.reset_button = FluentPushButton(FIF.CANCEL, "重置")
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.reset_button)
        
        parent_layout.addLayout(button_layout)
        parent_layout.addStretch()
        
    def _connect_signals(self):
        self.reset_button.clicked.connect(self.reset_form)
        self.save_button.clicked.connect(self.save_form)
        self.file_browse_button.clicked.connect(self.browse_file)
        
    def browse_file(self):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择Python文件", 
            "", 
            "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
        
    def reset_form(self):
        """重置表单内容"""
        self.vul_name.clear()
        self.vul_id.clear()
        self.vul_type.setCurrentIndex(0)
        self.vul_level.setCurrentIndex(0)
        
        self.enabled_check.setChecked(True)
        self.cookie_check.setChecked(False)
        self.content_check.setChecked(False)
        
        self.file_path_edit.clear()
        
    def save_form(self):
        """保存表单"""
        file_path = self.file_path_edit.text()
        if file_path:
            script_name = os.path.basename(file_path)
        else:
            script_name = ""
            
        form_data = {
            'vul_name': self.vul_name.text().strip(),
            'vul_id': self.vul_id.text().strip(),
            'vul_type': self.vul_type.currentText(),
            'vul_level': self.vul_level.currentText(),
            'enabled': self.enabled_check.isChecked(),
            'need_cookie': self.cookie_check.isChecked(),
            'write_content': self.content_check.isChecked(),
            'scriptname': script_name,
            'file_path': self.file_path_edit.text()
        }
        
        if not form_data['vul_name']:
            InfoBar.warning(
                title='验证失败',
                content="漏洞名称不能为空",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
            
        if not form_data['file_path']:
            InfoBar.warning(
                title='验证失败',
                content="请选择脚本文件",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
            
        try:
            from pageother.FileManager import verify_py_script
            verification_result = verify_py_script(form_data['file_path'])
            
            if verification_result is not True:
                if verification_result is False:
                    error_msg = "Python脚本验证失败：脚本中未找到payload相关函数"
                else:
                    error_msg = f"Python脚本验证出错：{str(verification_result)}"
                    
                InfoBar.warning(
                    title='验证失败',
                    content=error_msg,
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self
                )
                return
        except ImportError:
            InfoBar.warning(
                title='验证失败',
                content="无法导入文件验证模块",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        except Exception as e:
            InfoBar.warning(
                title='验证失败',
                content=f"脚本验证过程中发生错误：{str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
            return
            
        try:
            poc_id = fm.generate_poc_id()
            file_id = fm.gerenate_file_id(poc_id)
            poc_id = poc_id.replace("POC", "SCRIPT")
            file_id = file_id.replace("POC", "SCRIPT")
            target_dir = "./data/script"
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)      
            target_file_path = os.path.join(target_dir, file_id)
            
            copy_result = fm.copy_save_file(form_data['file_path'], target_file_path)
            if copy_result is not True:
                InfoBar.warning(
                    title='保存失败',
                    content=f"文件保存失败：{str(copy_result)}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self
                )
                return
                
            db_data = {
                'poc_id': poc_id,
                'vul_name': form_data['vul_name'],
                'vul_id': form_data['vul_id'],
                'vul_type': form_data['vul_type'],
                'vul_level': form_data['vul_level'],
                'enabled': form_data['enabled'],
                'need_cookie': form_data['need_cookie'],
                'write_content': form_data['write_content'],
                'scriptname': file_id  
            }
            
            sqlm.insert_poc_script(db_data)
            print(f"成功插入脚本数据: {db_data}" )
            InfoBar.success(
                title='保存成功',
                content="POC脚本保存成功",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )

            self.reset_form()
            
        except Exception as e:
            InfoBar.error(
                title='保存失败',
                content=f"保存POC脚本时出错：{str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
            return