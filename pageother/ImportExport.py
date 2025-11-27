from PySide6.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from PySide6.QtCore import Qt
from qfluentwidgets import (
    SubtitleLabel, SettingCardGroup, PushSettingCard,
    ExpandLayout, FluentIcon as FIF, InfoBar, InfoBarPosition,
    MessageBox
)

from pageother.FileManager import (
    export_data as fm_export_data, import_data as fm_import_data,
    clear_script as fm_clear_script
)


class ImportExportPage(QWidget):
    def __init__(self, title="", object_name="", parent=None):
        super().__init__(parent)
        
        if object_name:
            self.setObjectName(object_name)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(30)
        
        self.title = SubtitleLabel(self.tr("导入导出"), self)
        self.title.setAlignment(Qt.AlignLeft)
        
        self.import_export_group = SettingCardGroup(self.tr(""), self)
        
        self.import_setting_card = PushSettingCard(
            self.tr("选择文件"),
            FIF.DOWNLOAD,  
            self.tr("导入数据"),
            self.tr("从ZIP文件导入POC数据"),
            self.import_export_group
        )
        
        self.export_setting_card = PushSettingCard(
            self.tr("选择路径"),
            FIF.SHARE,
            self.tr("导出数据"),
            self.tr("将POC数据导出到ZIP文件"),
            self.import_export_group
        )
        

        self.clear_script_card = PushSettingCard(
            self.tr("清理"),
            FIF.DELETE,
            self.tr("清理缓存脚本"),
            self.tr("清理未有对应POC信息的脚本文件"),
            self.import_export_group
        )
        
        self.import_export_group.addSettingCard(self.import_setting_card)
        self.import_export_group.addSettingCard(self.export_setting_card)
        self.import_export_group.addSettingCard(self.clear_script_card)
        
        self.expand_layout = ExpandLayout()
        
        self.expand_layout.addWidget(self.import_export_group)
        
        self.main_layout.addWidget(self.title)
        self.main_layout.addLayout(self.expand_layout)
        self.main_layout.addStretch(1)
        
        self.import_setting_card.clicked.connect(self.import_data)
        self.export_setting_card.clicked.connect(self.export_data)

        self.clear_script_card.clicked.connect(self.clear_cache_scripts)
    
    def import_data(self):
        """导入数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("选择导入文件"),
            "",
            self.tr("ZIP Files (*.zip);;All Files (*)")
        )
        
        if file_path:
            title = self.tr('警告')
            content = self.tr('导入操作将会覆盖当前所有的POC和脚本内容，确定要继续吗？')
            w = MessageBox(title, content, self.window())
            w.yesButton.setText(self.tr('确定'))
            w.cancelButton.setText(self.tr('取消'))
            
            if w.exec():
                try:
                    success = fm_import_data(file_path)
                    
                    if success:
                        InfoBar.success(
                            title=self.tr("导入成功"),
                            content=self.tr("数据导入成功！"),
                            orient=Qt.Horizontal,
                            isClosable=True,
                            position=InfoBarPosition.TOP,
                            duration=2000,
                            parent=self
                        )
                    else:
                        InfoBar.warning(
                            title=self.tr("导入失败"),
                            content=self.tr("导入错误，请确保文件内容符合要求。"),
                            orient=Qt.Horizontal,
                            isClosable=True,
                            position=InfoBarPosition.TOP,
                            duration=2000,
                            parent=self
                        )
                except Exception as e:
                    InfoBar.error(
                        title=self.tr("导入错误"),
                        content=self.tr(f"导入过程中发生错误：{str(e)}"),
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=2000,
                        parent=self
                    )
    
    def export_data(self):
        """导出数据"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("选择导出路径"),
            "poc.zip",
            self.tr("ZIP Files (*.zip);;All Files (*)")
        )
        
        if file_path:
            try:
                if not file_path.endswith('.zip'):
                    file_path += '.zip'
                
                success = fm_export_data(file_path)
                
                if success:
                    InfoBar.success(
                        title=self.tr("导出成功"),
                        content=self.tr("数据导出成功！"),
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=2000,
                        parent=self
                    )
                else:
                    InfoBar.warning(
                        title=self.tr("导出失败"),
                        content=self.tr("数据导出失败，请重试。"),
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=2000,
                        parent=self
                    )
            except Exception as e:
                InfoBar.error(
                    title=self.tr("导出错误"),
                    content=self.tr(f"导出过程中发生错误：{str(e)}"),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
    
    def clear_cache_scripts(self):
        """清理缓存脚本"""
        title = self.tr('确认清理')
        content = self.tr('确定要清理未有对应POC信息的脚本文件吗？此操作不可撤销。')
        w = MessageBox(title, content, self.window())
        w.yesButton.setText(self.tr('确定'))
        w.cancelButton.setText(self.tr('取消'))
        
        if w.exec():
            try:
                success = fm_clear_script()
                
                if success:
                    InfoBar.success(
                        title=self.tr("清理成功"),
                        content=self.tr("缓存脚本清理完成！"),
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=2000,
                        parent=self
                    )
                else:
                    InfoBar.warning(
                        title=self.tr("清理失败"),
                        content=self.tr("清理过程中出现错误，请重试。"),
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=2000,
                        parent=self
                    )
            except Exception as e:
                InfoBar.error(
                    title=self.tr("清理错误"),
                    content=self.tr(f"清理过程中发生错误：{str(e)}"),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )