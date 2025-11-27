from PySide6.QtWidgets import QWidget, QVBoxLayout, QDialog, QTextEdit, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from qfluentwidgets import (
    SubtitleLabel, SettingCardGroup, PushSettingCard, SwitchSettingCard,
    ExpandLayout, FluentIcon as FIF
)
from qfluentwidgets import ConfigItem, BoolValidator, QConfig, PushButton
from pathlib import Path
import json

class ProxyConfig(QConfig):
    """代理配置类"""
    
    proxyAddresses = ConfigItem(
        "Proxy", 
        "Addresses", 
        [] 
    )
    verificationAddress = ConfigItem(
        "Proxy", 
        "VerificationAddress", 
        []
    )
    enableRotation = ConfigItem(
        "Proxy", 
        "EnableRotation", 
        False,
        BoolValidator()
    )
    outputDetailedInfo = ConfigItem(
        "Proxy", 
        "OutputDetailedInfo", 
        True,  # 默认值设为True
        BoolValidator()
    )
    
    def save_to_file(self, file_path):
        """保存配置到指定文件"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "Proxy": {
                    "Addresses": self.get(self.proxyAddresses),
                    "VerificationAddress": self.get(self.verificationAddress),
                    "EnableRotation": self.get(self.enableRotation),
                },
                "OutputDetailedInfo": self.get(self.outputDetailedInfo)
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def load_from_file(self, file_path):
        """从指定文件加载配置"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if "Proxy" in data:
                    proxy_data = data["Proxy"]
                    if "Addresses" in proxy_data:
                        addresses = proxy_data["Addresses"]
                        if isinstance(addresses, str):
                            addresses = [addr.strip() for addr in addresses.split('\n') if addr.strip()]
                        self.set(self.proxyAddresses, addresses)
                    if "VerificationAddress" in proxy_data:
                        addresses = proxy_data["VerificationAddress"]
                        if isinstance(addresses, str):
                            addresses = [addr.strip() for addr in addresses.split('\n') if addr.strip()]
                        self.set(self.verificationAddress, addresses)
                    if "EnableRotation" in proxy_data:
                        self.set(self.enableRotation, proxy_data["EnableRotation"])
                    if "OutputDetailedInfo" in proxy_data:
                        self.set(self.outputDetailedInfo, proxy_data["OutputDetailedInfo"])
        except Exception as e:
            print(f"加载配置文件失败: {e}")

proxy_cfg = ProxyConfig()

config_path = Path("./config/proxy.json")
config_path.parent.mkdir(parents=True, exist_ok=True)

proxy_cfg.load_from_file(config_path)


class TextEditDialog(QDialog):
    def __init__(self, proxy_list=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("编辑代理地址"))
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        self.desc_label = QLabel()
        self.desc_label.setStyleSheet("color: #666666;")
        layout.addWidget(self.desc_label)
        
        self.text_edit = QTextEdit()
        if proxy_list:
            self.text_edit.setPlainText('\n'.join(proxy_list))
        layout.addWidget(self.text_edit)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.cancel_button = PushButton(self.tr("取消"))
        self.ok_button = PushButton(self.tr("确定"))
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self.accept)
        
    def setTitle(self, title):
        self.title_label.setText(title)
        
    def setContent(self, content):
        self.desc_label.setText(content)
        
    @property
    def content(self):
        text = self.text_edit.toPlainText()
        return [addr.strip() for addr in text.split('\n') if addr.strip()]

class ProxyPage(QWidget):
    def __init__(self, title="", object_name="", parent=None):
        super().__init__(parent)
        if object_name:
            self.setObjectName(object_name)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(30)
        
        self.title = SubtitleLabel(self.tr("代理设置"), self)
        self.title.setAlignment(Qt.AlignLeft)
        
        self.proxy_group = SettingCardGroup(self.tr(""), self)
        
        self.proxy_setting_card = PushSettingCard(
            self.tr("设置"),
            FIF.GLOBE,
            self.tr("代理地址"),
            self.tr("配置代理服务器地址"),
            self.proxy_group
        )
        self.verification_setting_card = PushSettingCard(
            self.tr("设置"),
            FIF.LINK,
            self.tr("验证地址"),
            self.tr("配置用于验证代理的地址"),
            self.proxy_group
        )
        self.rotation_setting_card = SwitchSettingCard(
            FIF.SYNC,
            self.tr("代理轮转"),
            self.tr("在多个代理之间自动切换"),
            configItem=proxy_cfg.enableRotation,
            parent=self.proxy_group
        )
        self.detailed_info_setting_card = SwitchSettingCard(
            FIF.INFO,
            self.tr("连接信息"),
            self.tr("在终端输出简短的连接信息(log.info)"),
            configItem=proxy_cfg.outputDetailedInfo,
            parent=self.proxy_group
        )

        self.proxy_group.addSettingCard(self.proxy_setting_card)
        self.proxy_group.addSettingCard(self.verification_setting_card)
        self.proxy_group.addSettingCard(self.rotation_setting_card)
        self.proxy_group.addSettingCard(self.detailed_info_setting_card)

        self.expand_layout = ExpandLayout()
        
        self.expand_layout.addWidget(self.proxy_group)
        
        self.main_layout.addWidget(self.title)
        self.main_layout.addLayout(self.expand_layout)
        self.main_layout.addStretch(1)
        
        self.proxy_setting_card.clicked.connect(self.show_proxy_dialog)
        self.verification_setting_card.clicked.connect(self.show_verification_dialog)
        self.rotation_setting_card.checkedChanged.connect(self.save_config)
        self.detailed_info_setting_card.checkedChanged.connect(self.save_config)

    def show_proxy_dialog(self):
        dialog = TextEditDialog(
            proxy_cfg.get(proxy_cfg.proxyAddresses), 
            self.window()
        )
        dialog.setTitle(self.tr("设置代理地址"))
        dialog.setContent(self.tr("每行输入一个代理地址，支持HTTP、HTTPS和SOCKS代理"))
        
        if dialog.exec() == QDialog.Accepted:
            proxy_cfg.set(proxy_cfg.proxyAddresses, dialog.content)
            self.save_config()
    
    def show_verification_dialog(self):
        dialog = TextEditDialog(
            proxy_cfg.get(proxy_cfg.verificationAddress), 
            self.window()
        )
        dialog.setTitle(self.tr("设置验证地址"))
        dialog.setContent(self.tr("输入用于验证代理可用性的地址"))
        
        if dialog.exec() == QDialog.Accepted:
            proxy_cfg.set(proxy_cfg.verificationAddress, dialog.content)
            self.save_config()
    
    def save_config(self):
        try:
            proxy_cfg.save_to_file(config_path) 
        except Exception as e:
            print(f"保存配置失败: {e}")