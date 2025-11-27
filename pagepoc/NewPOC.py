from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
)
from qfluentwidgets import (
    SubtitleLabel, InfoBar, InfoBarPosition,FluentIcon as FIF
)
from PySide6.QtCore import Qt

from pageother import (
    SQLManager as sqlm
)
from pageother import FileManager as fm
from pagepoc import ComponentsForCreate as cc


class NewPOC(QWidget): 
    """新建POC页面类"""
    def __init__(self, title: str, object_name: str = None):
        super().__init__()
        if object_name:
            self.setObjectName(object_name)
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)
        
        title_label = SubtitleLabel("新建POC")
        layout.addWidget(title_label)
        
        self._setup_basic_info_form(layout)
        self._setup_config_options(layout)
        self._setup_request_info(layout)
        self._setup_payloads(layout)
        self._setup_matching_rules(layout)
        self._setup_action_buttons(layout)
        
        scroll_area.setWidget(content_widget)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
        self._connect_signals()
        
    def _setup_basic_info_form(self, parent_layout):
        """设置基本信息表单"""
        (self.basic_group, self.vul_name, self.vul_id, 
         self.vul_type, self.vul_level) = cc.FormComponents.create_basic_info_form()
        parent_layout.addWidget(self.basic_group)
        
    def _setup_config_options(self, parent_layout):
        """设置配置选项"""
        (self.config_group, self.enabled_check, self.cookie_check, 
         self.content_check) = cc.FormComponents.create_config_options()
        parent_layout.addWidget(self.config_group)
        
    def _setup_request_info(self, parent_layout):
        """设置请求信息"""
        (self.request_group, self.request_method, self.request_path, 
         self.request_headers, self.request_type, self.request_data) = cc.FormComponents.create_request_info()
        parent_layout.addWidget(self.request_group)
        
    def _setup_payloads(self, parent_layout):
        """设置Payloads"""
        (self.payloads_group, self.payloads_position, 
         self.payloads_content) = cc.FormComponents.create_payloads_section()
        parent_layout.addWidget(self.payloads_group)
        
    def _setup_matching_rules(self, parent_layout):
        """设置匹配规则"""
        (self.rules_group, self.rules_container, self.rules_layout, 
         self.add_rule_button) = cc.FormComponents.create_matching_rules()
         
        self.rules_containers = []  
        self.rules_data = [] 
        
        parent_layout.addWidget(self.rules_group)
        self.add_rule_group()
        
    def _setup_action_buttons(self, parent_layout):
        """设置操作按钮"""
        self.button_layout, self.save_button, self.reset_button = cc.FormComponents.create_action_buttons()
        parent_layout.addLayout(self.button_layout)
        parent_layout.addStretch()
        
    def _connect_signals(self):
        self.reset_button.clicked.connect(self.reset_form)
        self.save_button.clicked.connect(self.save_form)
        self.add_rule_button.clicked.connect(self.add_rule_group)
        
    def reset_form(self):
        """重置表单内容"""
        self.vul_name.clear()
        self.vul_id.clear()
        self.vul_type.setCurrentIndex(0)
        self.vul_level.setCurrentIndex(0)
        
        self.enabled_check.setChecked(True)
        self.cookie_check.setChecked(False)
        self.content_check.setChecked(False)

        
        self.request_method.setCurrentIndex(0)
        self.request_path.clear()
        self.request_headers.clear()
        self.request_type.setCurrentIndex(0)
        self.request_data.clear()
        
        self.payloads_position.setCurrentIndex(0)
        self.payloads_content.clear()
        self.payloads_content.setVisible(True)

        
        for container in self.rules_containers[:]:
            self.remove_rule_group(container)
        self.add_rule_group()  

    def add_rule_group(self):
        """添加一个新的规则组"""
        group_index = len(self.rules_containers) + 1
        (rule_container, rules_position, rules_type, rules_op, 
         rules_val, rules_res_d) = cc.FormComponents.create_rule_group(
            cc.FormComponents.group_qss, cc.FormComponents.combo_box_qss, 
            cc.FormComponents.line_edit_qss, cc.FormComponents.push_button_qss, 
            group_index
        )
        
        delete_layout = QHBoxLayout()
        delete_button = cc.FormComponents.create_action_buttons()[2] 
        delete_button.setText("删除此规则")
        delete_button.setIcon(FIF.DELETE)
        delete_button.clicked.connect(
            lambda _, container=rule_container: self.remove_rule_group(container)
        )
        delete_layout.addStretch()
        delete_layout.addWidget(delete_button)
        rule_container.layout().addRow("", delete_layout)
        
        # 用于存储规则控件引用
        rule_data = {
            'container': rule_container,
            'position': rules_position,
            'type': rules_type,
            'op': rules_op,
            'val': rules_val,
            'res_d': rules_res_d,
            'delete_button': delete_button
        } 
        self.rules_containers.append(rule_container)
        self.rules_data.append(rule_data)
        self.rules_layout.addWidget(rule_container)
        self.update_rule_titles()

    def remove_rule_group(self, container):
        """删除指定的规则组"""
        for i, rule_container in enumerate(self.rules_containers):
            if rule_container == container:
                self.rules_layout.removeWidget(container)
                container.deleteLater()
                del self.rules_containers[i]
                del self.rules_data[i]
                break
        self.update_rule_titles()

    def update_rule_titles(self):
        """更新所有规则组的标题"""
        for i, container in enumerate(self.rules_containers):
            container.setTitle(f"规则 {i + 1}")

    def get_rules_data(self):
        """获取所有规则组的数据"""
        rules = []
        for rule_data in self.rules_data:
            rule = {
                'position': rule_data['position'].currentText(),
                'type': rule_data['type'].currentText(),
                'op': rule_data['op'].currentText(),
                'val': rule_data['val'].text(),
                'res_d': rule_data['res_d'].text()
            }
            rules.append(rule)
        return rules
        
    def get_form_data(self):
        """
        获取表单所有数据
        
        Returns:
            dict: 包含所有表单数据的字典
        """
        form_data = {}
        
        form_data['basic_info'] = {
            'vul_name': self.vul_name.text().strip(),
            'vul_id': self.vul_id.text().strip(),
            'vul_type': self.vul_type.currentText(),
            'vul_level': self.vul_level.currentText(),
        }
        
        form_data['config'] = {
            'enabled': self.enabled_check.isChecked(),
            'need_cookie': self.cookie_check.isChecked(),
            'write_content': self.content_check.isChecked()
        }
        
        form_data['request'] = {
            'method': self.request_method.currentText(),
            'path': self.request_path.text().strip(),
            'headers': self.request_headers.toPlainText(),
            'data_type': self.request_type.currentText(),
            'data': self.request_data.toPlainText()
        }
        
        form_data['payloads'] = {
            'position': self.payloads_position.currentText(),
            'content': self.payloads_content.toPlainText()
        }
        
        form_data['payloads']['content'] = self.payloads_content.toPlainText()
            
        form_data['rules'] = self.get_rules_data()
        
        return form_data

    def verify_form(self, form_data):
        """
        验证表单数据
        
        Returns:
            tuple: (is_valid, error_message) 验证结果和错误信息
        """
        basic_info = form_data['basic_info']
        if not basic_info['vul_name'].strip():
            return False, "漏洞名称不能为空"

        request_info = form_data['request']   
        if not request_info['path'].strip():
            return False, "请求路径不能为空"

        rules_info = form_data['rules']
        if not rules_info:
            return False, "至少需要添加一个匹配规则"
            
        for i, rule in enumerate(rules_info):
            if not rule['val'].strip():
                return False, f"规则 {i+1} 的匹配值不能为空"
                
        return True, "验证通过"
        
    def save_form(self):
        try:
            form_data = self.get_form_data()
            is_valid, message = self.verify_form(form_data)
        
            if not is_valid:
                InfoBar.warning(
                    title='验证失败',
                    content=message,
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                return
            form_data = self.map_form_data_values(form_data)
            form_data['basic_info']['poc_id'] = fm.generate_poc_id()
            # 打印数据
            # print("=== 表单数据 ===")
            # print(json.dumps(form_data, ensure_ascii=False, indent=2))
            # print("===============")
            sqlm.insert_poc(form_data)
            # print("====已成功插入到数据库====")
            
            self.reset_form()
            InfoBar.success(
                title='保存成功',
                content="POC保存成功，请前往执行界面进行测试！",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000, 
                parent=self
            )
            
        except Exception as e:
            InfoBar.error(
                title='保存失败',
                content=f"保存POC时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
            print(f"保存表单时出错: {e}")

    def map_form_data_values(self, form_data):
        mappings = {
            'request_type': {
                "没有对应的类型选项请在header中定义content-type": "null",
                "raw": "raw",
                "json": "json",
                "xml": "xml",
                "binary": "binary",
                "form-data": "form-data",
                "x-www-form-urlencoded": "x-www-form-urlencoded"
            },
            'rules_position': {
                "响应体": "resp_body",
                "二次请求": "again_req",
                "无": "resp"
            },
            'rules_type': {
                "正则": "regex",
                "状态码": "status",
                "内容长度": "content",
                "时间长度": "time",
                "带外检测": "oob"
            },
            'rules_op': {
                "等于/是": "==",
                "不等于/不是": "!=",
                "大于等于": ">=",
                "小于等于": "<=",
                "大于": ">",
                "小于": "<"
            }
        }
        
        if 'request' in form_data:
            request = form_data['request']
            if request.get('data_type') in mappings['request_type']:
                request['data_type'] = mappings['request_type'][request['data_type']]
        
        if 'rules' in form_data:
            for rule in form_data['rules']:
                if rule.get('position') in mappings['rules_position']:
                    rule['position'] = mappings['rules_position'][rule['position']]
                    
                if rule.get('type') in mappings['rules_type']:
                    rule['type'] = mappings['rules_type'][rule['type']]
                    
                if rule.get('op') in mappings['rules_op']:
                    rule['op'] = mappings['rules_op'][rule['op']]
        return form_data