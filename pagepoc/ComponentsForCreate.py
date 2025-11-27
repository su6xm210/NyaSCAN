from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QHBoxLayout, 
    QFormLayout, QGroupBox
)
from qfluentwidgets import (
    LineEdit as FluentLineEdit, 
    ComboBox as FluentComboBox, CheckBox as FluentCheckBox, 
    PushButton as FluentPushButton, FluentIcon as FIF
)
from PySide6.QtCore import Qt

from pagepoc import StyleFile as stf


class FormComponents:
    
    group_qss = stf.group_qss
    line_edit_qss = stf.line_edit_qss
    combo_box_qss = stf.combo_box_qss
    check_box_qss = stf.check_box_qss
    text_edit_qss = stf.text_edit_qss
    push_button_qss = stf.push_button_qss
    
    @staticmethod
    def create_basic_info_form():
        """创建基本信息表单"""
        basic_group = QGroupBox("基本信息")
        basic_group.setStyleSheet(FormComponents.group_qss)
        basic_layout = QFormLayout(basic_group)
        basic_layout.setLabelAlignment(Qt.AlignRight)
        basic_layout.setHorizontalSpacing(20)
        basic_layout.setVerticalSpacing(12)
        
        vul_name = FluentLineEdit()
        vul_name.setPlaceholderText("输入漏洞名称")
        vul_name.setStyleSheet(FormComponents.line_edit_qss)
        basic_layout.addRow("漏洞名称", vul_name)
        
        vul_id = FluentLineEdit()
        vul_id.setPlaceholderText("输入CVE/CNVD")
        vul_id.setStyleSheet(FormComponents.line_edit_qss)
        basic_layout.addRow("漏洞编号", vul_id)

        vul_type = FluentComboBox()
        vul_type.addItems([
            "信息泄露", "跨站脚本(XSS)", "SQL注入", "其他注入", "反序列化", "命令执行", "任意代码执行", 
            "文件类", "未授权", "请求伪造(CSRF/SSRF)", "目录类漏洞", "拒绝服务"
        ])
        vul_type.setStyleSheet(FormComponents.combo_box_qss)
        basic_layout.addRow("漏洞类型", vul_type)

        vul_level = FluentComboBox()
        vul_level.addItems(["低危", "中危", "高危"])
        vul_level.setStyleSheet(FormComponents.combo_box_qss)
        basic_layout.addRow("危害等级", vul_level)
        
        return basic_group, vul_name, vul_id, vul_type, vul_level

    @staticmethod
    def create_config_options():
        """创建配置选项"""
        config_group = QGroupBox("配置选项")
        config_group.setStyleSheet(FormComponents.group_qss)
        config_layout = QVBoxLayout(config_group)
        config_layout.setSpacing(8)
        
        enabled_check = FluentCheckBox("启用该POC")
        enabled_check.setChecked(True)
        enabled_check.setStyleSheet(FormComponents.check_box_qss)
        config_layout.addWidget(enabled_check)
        
        cookie_check = FluentCheckBox("需要验证Cookie")
        cookie_check.setChecked(False)
        cookie_check.setStyleSheet(FormComponents.check_box_qss)
        config_layout.addWidget(cookie_check)
        
        content_check = FluentCheckBox("会对目标写入内容")
        content_check.setChecked(False)
        content_check.setStyleSheet(FormComponents.check_box_qss)
        config_layout.addWidget(content_check)
        
        return config_group, enabled_check, cookie_check, content_check

    @staticmethod
    def create_request_info():
        """创建请求信息表单"""
        request_group = QGroupBox("请求信息")
        request_group.setStyleSheet(FormComponents.group_qss)
        request_layout = QFormLayout(request_group)
        request_layout.setLabelAlignment(Qt.AlignRight)
        request_layout.setHorizontalSpacing(20)
        request_layout.setVerticalSpacing(12)

        request_method = FluentComboBox()
        request_method.addItems([
            "GET", "POST", "PUT", "DELETE", "HEAD", 
            "OPTIONS", "PATCH", "TRACE", "CONNECT"
        ])
        request_method.setStyleSheet(FormComponents.combo_box_qss)
        request_layout.addRow("请求方法", request_method)

        request_path = FluentLineEdit()
        request_path.setPlaceholderText("输入请求路径")
        request_path.setStyleSheet(FormComponents.line_edit_qss)
        request_layout.addRow("请求路径", request_path)

        request_headers = QTextEdit()
        request_headers.setPlaceholderText(
            "请输入header信息,多个请换行。如果Payload在header中，以PAYLOAD为占位符。"
        )
        request_headers.setStyleSheet(FormComponents.text_edit_qss)
        request_headers.setMinimumHeight(100)
        request_layout.addRow("请求头", request_headers)

        request_type = FluentComboBox()
        request_type.addItems([
            "没有对应的类型选项请在header中定义content-type",
            "raw", "json", "xml", "binary", "form-data",
            "x-www-form-urlencoded"
        ])
        request_type.setStyleSheet(FormComponents.combo_box_qss)
        request_layout.addRow("数据类型", request_type)
        
        request_data = QTextEdit()
        request_data.setPlaceholderText("请输入请求数据,不存在默认为空")
        request_data.setStyleSheet(FormComponents.text_edit_qss)
        request_data.setMinimumHeight(100)
        request_layout.addRow("请求数据", request_data)
        
        return request_group, request_method, request_path, request_headers, request_type, request_data

    @staticmethod
    def create_payloads_section():
        """创建Payloads部分"""
        payloads_group = QGroupBox("Payloads")
        payloads_group.setStyleSheet(FormComponents.group_qss)
        payloads_layout = QVBoxLayout(payloads_group)
        payloads_layout.setSpacing(12)

        payloads_form_layout = QFormLayout()
        payloads_form_layout.setLabelAlignment(Qt.AlignRight)
        payloads_form_layout.setHorizontalSpacing(20)
        payloads_form_layout.setVerticalSpacing(12)

        payloads_position = FluentComboBox()
        payloads_position.addItems(["None", "URL", "header", "body"])
        payloads_position.setStyleSheet(FormComponents.combo_box_qss)
        payloads_form_layout.addRow("载入位置", payloads_position)

        payloads_layout.addLayout(payloads_form_layout)
        
        payloads_content = QTextEdit()
        payloads_content.setPlaceholderText(
            "请输入payload内容,多个payload请换行（默认多个payload使用相同的匹配规则）"
        )
        payloads_content.setStyleSheet(FormComponents.text_edit_qss)
        payloads_content.setMinimumHeight(100)
        payloads_layout.addWidget(payloads_content)

        return payloads_group, payloads_position, payloads_content

    @staticmethod
    def create_matching_rules():
        """创建匹配规则部分"""
        rules_group = QGroupBox("匹配规则")
        rules_group.setStyleSheet(FormComponents.group_qss)
        rules_main_layout = QVBoxLayout(rules_group)
        rules_main_layout.setSpacing(15)

        rules_container = QWidget()
        rules_container.setStyleSheet("background-color: transparent;")
        rules_layout = QVBoxLayout(rules_container)
        rules_layout.setSpacing(10)
        rules_layout.setContentsMargins(0, 0, 0, 0)
        rules_main_layout.addWidget(rules_container)
        
        add_rule_layout = QHBoxLayout()
        add_rule_button = FluentPushButton("添加规则")
        add_rule_button.setIcon(FIF.ADD)
        add_rule_layout.addWidget(add_rule_button)
        add_rule_layout.addStretch()
        rules_main_layout.addLayout(add_rule_layout)
        
        return rules_group, rules_container, rules_layout, add_rule_button

    @staticmethod
    def create_rule_group(group_qss, combo_box_qss, line_edit_qss, push_button_qss, group_index):
        """创建单个规则组"""
        rule_container = QGroupBox(f"规则 {group_index}")
        rule_container.setStyleSheet(group_qss)
        rule_layout = QFormLayout(rule_container)
        rule_layout.setLabelAlignment(Qt.AlignRight)
        rule_layout.setHorizontalSpacing(15)
        rule_layout.setVerticalSpacing(8)

        rules_position = FluentComboBox()
        rules_position.addItems(["响应体", "二次请求", "无"])
        rules_position.setStyleSheet(combo_box_qss)
        rule_layout.addRow("匹配位置", rules_position)

        rules_type = FluentComboBox()
        rules_type.addItems(["正则", "状态码", "内容长度", "时间长度"])
        rules_type.setStyleSheet(combo_box_qss)
        rule_layout.addRow("规则类型", rules_type)
        
        rules_op = FluentComboBox()
        rules_op.addItems(["等于/是", "不等于/不是", "大于等于", "小于等于", "大于", "小于"])
        rules_op.setStyleSheet(combo_box_qss)
        rule_layout.addRow("关系运算", rules_op)
        
        rules_val = FluentLineEdit()
        rules_val.setPlaceholderText("请输入匹配规则值")
        rules_val.setStyleSheet(line_edit_qss)
        rule_layout.addRow("匹配值", rules_val)
        
        rules_res_d = FluentLineEdit()
        rules_res_d.setPlaceholderText("请输入结果描述，默认为空")
        rules_res_d.setStyleSheet(line_edit_qss)
        rule_layout.addRow("结果描述", rules_res_d)
        
        return rule_container, rules_position, rules_type, rules_op, rules_val, rules_res_d

    @staticmethod
    def create_action_buttons():
        """创建操作按钮"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_button = FluentPushButton("保存")
        save_button.setIcon(FIF.SAVE)
        button_layout.addWidget(save_button)
        
        reset_button = FluentPushButton("重置")
        reset_button.setIcon(FIF.DELETE)
        button_layout.addWidget(reset_button)
        
        return button_layout, save_button, reset_button