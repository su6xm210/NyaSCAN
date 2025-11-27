from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QAbstractItemView, QGroupBox
)
from PySide6.QtCore import Qt
from qfluentwidgets import (
    SubtitleLabel, SettingCardGroup, SwitchSettingCard,
    FluentIcon as FIF, InfoBar, InfoBarPosition,
    PushButton, LineEdit, RangeSettingCard, RangeConfigItem, RangeValidator,
    OptionsSettingCard,ListWidget,TextEdit,ConfigItem, OptionsConfigItem, 
    OptionsValidator, BoolValidator, QConfig
)

from pathlib import Path
import json

from pagepoc import StyleFile as sf
from scan.VerifyScanCFG import verify_scan_cfg

class ScanConfig(QConfig):
    """扫描配置类"""
    concurrency = RangeConfigItem(
        "Scan", 
        "Concurrency", 
        16,
        RangeValidator(1, 256)
    )
    
    scanMode = OptionsConfigItem(
        "Scan",
        "Mode",
        "ALONE",
        OptionsValidator(["ALONE", "GROUP"])
    )
    
    usePocScript = OptionsConfigItem(
        "Scan",
        "UsePocScript",
        "POC", 
        OptionsValidator(["POC", "脚本", "全部"])
    )

    skipWriteContent = ConfigItem(
        "Scan",
        "SkipWriteContent",
        True,
        BoolValidator()
    )
    
    skipVerifyCookie = ConfigItem(
        "Scan",
        "SkipVerifyCookie",
        True,
        BoolValidator()
    )
    
    enableProxy = ConfigItem(
        "Scan",
        "EnableProxy",
        False,
        BoolValidator()
    )
    
    maxRetries = RangeConfigItem(
        "Scan",
        "MaxRetries",
        3,
        RangeValidator(0, 10)
    )
    
    enableRetryBackoff = ConfigItem(
        "Scan",
        "EnableRetryBackoff",
        False,
        BoolValidator()
    )    
    
    skipProxyVerify = ConfigItem(
        "Scan",
        "SkipProxyVerify",
        True,
        BoolValidator()
    )

    def save_to_file(self, file_path):
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "Scan": {
                    "Concurrency": self.get(self.concurrency),
                    "Mode": self.get(self.scanMode),
                    "UsePocScript": self.get(self.usePocScript),
                    "SkipWriteContent": self.get(self.skipWriteContent),
                    "SkipVerifyCookie": self.get(self.skipVerifyCookie),
                    "EnableProxy": self.get(self.enableProxy),
                    "SkipProxyVerify": self.get(self.skipProxyVerify),
                    "MaxRetries": self.get(self.maxRetries),
                    "EnableRetryBackoff": self.get(self.enableRetryBackoff)
                }
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
                
                if "Scan" in data:
                    scan_data = data["Scan"]
                    if "Concurrency" in scan_data:
                        self.set(self.concurrency, scan_data["Concurrency"])
                    if "Mode" in scan_data:
                        self.set(self.scanMode, scan_data["Mode"])
                    if "SkipWriteContent" in scan_data:
                        self.set(self.skipWriteContent, scan_data["SkipWriteContent"])
                    if "SkipVerifyCookie" in scan_data:
                        self.set(self.skipVerifyCookie, scan_data["SkipVerifyCookie"])
                    if "EnableProxy" in scan_data:
                        self.set(self.enableProxy, scan_data["EnableProxy"])
                    if "SkipProxyVerify" in scan_data:
                        self.set(self.skipProxyVerify, scan_data["SkipProxyVerify"])
                    if "MaxRetries" in scan_data:
                        self.set(self.maxRetries, scan_data["MaxRetries"])
                    if "EnableRetryBackoff" in scan_data:
                        self.set(self.enableRetryBackoff, scan_data["EnableRetryBackoff"])
        except Exception as e:
            print(f"加载配置文件失败: {e}")

scan_cfg = ScanConfig()

config_path = Path("./config/scan_cfg.json")
config_path.parent.mkdir(parents=True, exist_ok=True)

scan_cfg.load_from_file(config_path)


class ScanPage(QWidget):
    def __init__(self, title="", object_name="", parent=None):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.title = SubtitleLabel(self.tr("扫描策略"), self)
        self.urls = []
        self.headers = []
        self.selected_pocs = []
        self.custom_pocs_added = False 
        
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        """设置界面"""
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.content_widget = QWidget()
        self.scroll_area.setWidget(self.content_widget)
        
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        self.content_layout.setSpacing(30)
        
        self.title.setAlignment(Qt.AlignLeft)
        

        self.input_group = QGroupBox()
        self.input_group.setStyleSheet("""
        QGroupBox {
            font-size: 14px;
            font-weight: 500;
            border: 1px solid #e0e0e0;       
            border-radius: 6px;
            margin-top: 1ex;
            padding-top: 15px;
            padding-left: 15px;
            padding-right: 15px;
            padding-bottom: 15px;
            background-color: #fafafa;
        }
""")
        input_layout = QVBoxLayout()
        
        url_label = QLabel(self.tr("URL设置"))
        url_label.setStyleSheet("margin-top: 20px; font-size: 14px;")
        self.url_text_edit = TextEdit()
        self.url_text_edit.setPlaceholderText(self.tr("每行输入一个URL(http://或https://)地址"))
        self.url_text_edit.setMaximumHeight(100)
        
        header_label = QLabel(self.tr("请求头设置"))
        header_label.setStyleSheet("margin-top: 20px; font-size: 14px;")
        self.header_text_edit = TextEdit()
        self.header_text_edit.setPlaceholderText(self.tr("输入HTTP请求头"))
        self.header_text_edit.setMaximumHeight(100)
        
        poc_label = QLabel(self.tr("POC选择"))
        poc_label.setStyleSheet("margin-top: 20px; font-size: 14px;")
        
        self.poc_list = ListWidget()
        self.poc_list.setSelectionMode(QAbstractItemView.MultiSelection)
        poc_options = ["全量", "全部POC","全部脚本",
            "信息泄露", "跨站脚本(XSS)", "SQL注入", "其他注入", "反序列化","命令执行", "任意代码执行", 
            "文件类", "未授权", "请求伪造(CSRF/SSRF)", "目录类漏洞", "拒绝服务"
        ]
        self.poc_list.addItems(poc_options)
        
        self.poc_input = LineEdit()
        self.poc_input.setPlaceholderText(self.tr("输入POCID，回车添加"))
        self.poc_input.setStyleSheet(sf.line_edit_qss)
        self.poc_input.returnPressed.connect(self.add_custom_poc)
        
        self.clear_poc_button = PushButton(self.tr("清空选择"))
        self.clear_poc_button.clicked.connect(self.clear_poc_selection)
        
        input_layout.addWidget(url_label)
        input_layout.addWidget(self.url_text_edit)
        input_layout.addWidget(header_label)
        input_layout.addWidget(self.header_text_edit)
        input_layout.addWidget(poc_label)
        input_layout.addWidget(self.poc_list)
        input_layout.addWidget(self.poc_input)
        input_layout.addWidget(self.clear_poc_button)
        
        self.input_group.setLayout(input_layout)
        
        self.scan_group = SettingCardGroup(self.tr("扫描设置"), self.content_widget)
        
        self.concurrency_setting_card = RangeSettingCard(
            configItem=scan_cfg.concurrency,
            icon=FIF.SPEED_HIGH,
            title=self.tr("并发数"),
            content=self.tr("设置扫描并发数"),
            parent=self.scan_group
        )
        
        self.mode_setting_card = OptionsSettingCard(
            configItem=scan_cfg.scanMode,
            icon=FIF.MENU,
            title=self.tr("扫描模式"),
            content=self.tr("选择扫描模式"),
            texts=["ALONE", "GROUP"],
            parent=self.scan_group
        )
        
        self.use_poc_script_card = OptionsSettingCard(
            configItem=scan_cfg.usePocScript,
            icon=FIF.CODE,
            title=self.tr("执行POC类型"),
            content=self.tr("选择Poc使用类型(仅对漏洞类型有效)"),
            texts=["POC", "脚本", "全部"],
            parent=self.scan_group
        )


        self.skip_write_content_card = SwitchSettingCard(
            FIF.PENCIL_INK,
            self.tr("跳过写入内容的POC"),
            self.tr("是否跳过需要写入内容的POC"),
            configItem=scan_cfg.skipWriteContent,
            parent=self.scan_group
        )
        
        self.skip_verify_cookie_card = SwitchSettingCard(
            FIF.BOOK_SHELF,
            self.tr("跳过验证Cookie的POC"),
            self.tr("是否跳过需要验证Cookie的POC"),
            configItem=scan_cfg.skipVerifyCookie,
            parent=self.scan_group
        )
        
        self.enable_proxy_card = SwitchSettingCard(
            FIF.GLOBE,
            self.tr("启用代理"),
            self.tr("是否启用代理"),
            configItem=scan_cfg.enableProxy,
            parent=self.scan_group
        )
        self.skip_proxy_verify_card = SwitchSettingCard(
            FIF.CERTIFICATE,
            self.tr("跳过代理验证"),
            self.tr("是否跳过代理有效性验证"),
            configItem=scan_cfg.skipProxyVerify,
            parent=self.scan_group
        )
        self.max_retries_card = RangeSettingCard(
            configItem=scan_cfg.maxRetries,
            icon=FIF.SYNC,
            title=self.tr("最大重试次数"),
            content=self.tr("设置请求失败时的最大重试次数"),
            parent=self.scan_group
        )
        
        self.enable_retry_backoff_card = SwitchSettingCard(
            FIF.TILES,
            self.tr("启用重试退避"),
            self.tr("是否在重试时启用退避策略(如果启用,则每次重试的延迟时间会指数递增)"),
            configItem=scan_cfg.enableRetryBackoff,
            parent=self.scan_group
    )
        self.scan_group.addSettingCard(self.concurrency_setting_card)
        self.scan_group.addSettingCard(self.mode_setting_card)
        self.scan_group.addSettingCard(self.use_poc_script_card)
        self.scan_group.addSettingCard(self.skip_write_content_card)
        self.scan_group.addSettingCard(self.skip_verify_cookie_card)
        self.scan_group.addSettingCard(self.enable_proxy_card)
        self.scan_group.addSettingCard(self.skip_proxy_verify_card)
        self.scan_group.addSettingCard(self.max_retries_card)
        self.scan_group.addSettingCard(self.enable_retry_backoff_card)

        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(20)
        self.button_layout.addStretch()
        
        self.reset_button = PushButton(self.tr("重置"))
        self.execute_button = PushButton(self.tr("执行"))
        self.reset_button.setFixedWidth(100)
        self.execute_button.setFixedWidth(100)
        
        self.button_layout.addWidget(self.reset_button)
        self.button_layout.addWidget(self.execute_button)
        
        self.content_layout.addWidget(self.title)
        self.content_layout.addWidget(self.input_group)
        self.content_layout.addWidget(self.scan_group)
        self.content_layout.addLayout(self.button_layout)
        self.content_layout.addStretch(1)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.scroll_area)
        
        self.reset_button.clicked.connect(self.reset_settings)
        self.execute_button.clicked.connect(self.execute_scan)

    def add_custom_poc(self):
        """添加自定义POC"""
        text = self.poc_input.text().strip()
        if text:
            if not self.custom_pocs_added:
                self.poc_list.clear()
                self.custom_pocs_added = True
                
            items = [self.poc_list.item(i).text() for i in range(self.poc_list.count())]
            if text not in items:
                self.poc_list.addItem(text)
            self.poc_input.clear()

    def clear_poc_selection(self):
        """清空POC选择"""
        if self.custom_pocs_added:
            self.custom_pocs_added = False
            poc_options = ["全量", "全部POC","全部脚本",
                "信息泄露", "跨站脚本(XSS)", "SQL注入","其他注入", "反序列化", "命令执行", "任意代码执行", 
                "文件类", "未授权", "请求伪造(CSRF/SSRF)", "目录类漏洞", "拒绝服务"
            ]
            self.poc_list.clear()
            self.poc_list.addItems(poc_options)
        else:
            for i in range(self.poc_list.count()):
                item = self.poc_list.item(i)
                item.setSelected(False)
        
    def load_config(self):
        pass
    
    def save_config(self):
        """保存配置到指定文件"""
        try:
            scan_cfg.save_to_file(config_path)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def reset_settings(self):
        """重置设置"""
        scan_cfg.set(scan_cfg.concurrency, 16)
        scan_cfg.set(scan_cfg.scanMode, "ALONE")
        scan_cfg.set(scan_cfg.skipWriteContent, True)
        scan_cfg.set(scan_cfg.skipVerifyCookie, True)
        scan_cfg.set(scan_cfg.enableProxy, False)
        scan_cfg.set(scan_cfg.skipProxyVerify, False)
        scan_cfg.set(scan_cfg.maxRetries, 3)
        scan_cfg.set(scan_cfg.enableRetryBackoff, False)
        scan_cfg.set(scan_cfg.usePocScript, "POC")

        self.load_config()
        self.save_config()
        
        self.url_text_edit.clear()
        self.header_text_edit.clear()
        self.clear_poc_selection()
        
        self.custom_pocs_added = False
        poc_options = ["全量", "全部POC","全部脚本",
            "信息泄露", "跨站脚本(XSS)", "SQL注入", "其他注入", "反序列化","命令执行", "任意代码执行", 
            "文件类", "未授权", "请求伪造(CSRF/SSRF)", "目录类漏洞", "拒绝服务"
        ]
        self.poc_list.clear()
        self.poc_list.addItems(poc_options)

        InfoBar.success(
            self.tr("重置成功"),
            self.tr("已重置为默认值"),
            duration=2000,
            position=InfoBarPosition.TOP,
            parent=self
        )

    def execute_scan(self):
        """执行扫描"""
        self.save_config()
        
        urls_text = self.url_text_edit.toPlainText()
        self.urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        headers_text = self.header_text_edit.toPlainText()
        header_line = headers_text.split('\n')
        self.headers =  [line for line in header_line if line.strip()] 
        
        self.selected_pocs = []
        for i in range(self.poc_list.count()):
            item = self.poc_list.item(i)
            if item.isSelected():
                self.selected_pocs.append(item.text())
        scan_data = {
            "urls": self.urls,
            "headers": self.headers,
            "selected_pocs": self.selected_pocs,
            "concurrency": scan_cfg.get(scan_cfg.concurrency),
            "mode": scan_cfg.get(scan_cfg.scanMode),
            "use_poc_script": scan_cfg.get(scan_cfg.usePocScript),
            "skip_write_content": scan_cfg.get(scan_cfg.skipWriteContent),
            "skip_verify_cookie": scan_cfg.get(scan_cfg.skipVerifyCookie),
            "enable_proxy": scan_cfg.get(scan_cfg.enableProxy),
            "skip_proxy_verify": scan_cfg.get(scan_cfg.skipProxyVerify),
            "max_retries": scan_cfg.get(scan_cfg.maxRetries),
            "enable_retry_backoff": scan_cfg.get(scan_cfg.enableRetryBackoff)
        }

        is_valid, msg = verify_scan_cfg(scan_data)
        if not is_valid:
            InfoBar.error(
                self.tr("配置错误"),
                msg,
                duration=5000,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return
        
        print(f"扫描信息: {scan_data}")
        success, msg = start_scan(scan_data)
        if success:
            InfoBar.success(
                self.tr("扫描启动"),
                self.tr("已开始执行扫描"),
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
        else:
            InfoBar.error(
                self.tr("启动失败"),
                msg,
                duration=5000,
                position=InfoBarPosition.TOP,
                parent=self
            )


def start_scan(scan_data):
        """启动扫描任务"""
        try:
            from scan.scan_controller import scan_controller
            success, msg = scan_controller.start_scan(scan_data)
            return success, msg
        except Exception as e:
            return False, f"启动扫描时出错: {str(e)}"