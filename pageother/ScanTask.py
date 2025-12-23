import os
import chardet
from datetime import datetime
from PySide6.QtCore import Qt, QEasingCurve, QPropertyAnimation, QPoint, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QTextEdit
)
from PySide6.QtGui import QTextOption
from qfluentwidgets import (
    CardWidget, BodyLabel, StrongBodyLabel, PushButton
)
from PySide6.QtWidgets import QMessageBox

from pagepoc import StyleFile
from scan.scan_controller import scan_controller


class ScanTaskPage(QWidget):
    def __init__(self, title="", object_name="", parent=None):
        super().__init__(parent)
        if object_name:
            self.setObjectName(object_name)
            
        self.side_panel = None
        self.panel_animation = None
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_scan_status)
        self.status_timer.start(1000) 
        self.setup_ui()
        self.refresh_tasks()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        self.header_label = StrongBodyLabel("扫描任务", self)
        main_layout.addWidget(self.header_label)
        
        
        self.current_scan_card = self.create_current_scan_card()
        main_layout.addWidget(self.current_scan_card)
        
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.card_container = QWidget()
        self.card_layout = QVBoxLayout(self.card_container)
        self.card_layout.setAlignment(Qt.AlignTop)
        self.card_layout.setSpacing(10)
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_area.setWidget(self.card_container)
        main_layout.addWidget(self.scroll_area)
        
        button_layout = QHBoxLayout()
        
        self.refresh_button = PushButton("刷新", self)
        self.refresh_button.setStyleSheet(StyleFile.push_button_qss)
        self.refresh_button.setFixedWidth(100)
        self.refresh_button.clicked.connect(self.refresh_tasks)
        button_layout.addWidget(self.refresh_button)
        
        self.generate_report_button = PushButton("生成测试报告", self)
        self.generate_report_button.setStyleSheet(StyleFile.push_button_qss)
        self.generate_report_button.setFixedWidth(120)
        self.generate_report_button.clicked.connect(self.generate_test_report)
        button_layout.addWidget(self.generate_report_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        self.init_detail_panel()
        
       
        self.update_scan_status()

    def create_current_scan_card(self):
        card = CardWidget(self)
        card.setFixedHeight(80)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        self.status_label = StrongBodyLabel("当前状态: 无扫描进程", card)
        layout.addWidget(self.status_label)
        layout.addStretch()
        
        self.stop_scan_button = PushButton("停止扫描", card)
        self.stop_scan_button.setStyleSheet(StyleFile.push_button_qss)
        self.stop_scan_button.clicked.connect(self.stop_scan) 
        self.stop_scan_button.setEnabled(False)
        layout.addWidget(self.stop_scan_button)
        
        return card

    def update_scan_status(self):
        if scan_controller.is_scan_running():
            self.status_label.setText("当前状态: 扫描进行中...")
            self.stop_scan_button.setEnabled(True)
        else:
            status = scan_controller.get_scan_status()
            if status == "空闲":
                self.status_label.setText("当前状态: 无扫描进程")
            elif status == "已完成":
                self.status_label.setText("当前状态: 扫描已完成")
            else:
                self.status_label.setText(f"当前状态: {status}")
            self.stop_scan_button.setEnabled(False)

    def stop_scan(self): 
        try:
            success, message = scan_controller.stop_scan()
            print(message)
            
            if success:
                self.update_scan_status()
                
            return success
        except Exception as e:
            print(f"停止扫描时出错: {e}")
            return False

    def init_detail_panel(self):
        self.detail_panel = QWidget(self)
        self.detail_panel.setObjectName("detailPanel")
        self.detail_panel.setStyleSheet("""
            QWidget#detailPanel {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        self.detail_panel.setFixedWidth(400)
        self.detail_panel.hide()
        
        panel_layout = QVBoxLayout(self.detail_panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)
        
        title_widget = QWidget()
        title_widget.setFixedHeight(40)
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(20, 10, 20, 10)
        self.detail_title = StrongBodyLabel("详情")
        self.detail_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        close_button = PushButton("关闭")
        close_button.setStyleSheet(StyleFile.push_button_qss)
        close_button.setFixedSize(60, 25)
        close_button.clicked.connect(self.hide_detail_panel)
        title_layout.addWidget(self.detail_title)
        title_layout.addStretch()
        title_layout.addWidget(close_button)
        panel_layout.addWidget(title_widget)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 0, 20, 20)
        content_layout.setSpacing(15)
        
        self.detail_content = QTextEdit()
        self.detail_content.setReadOnly(True)
        self.detail_content.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.detail_content.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        content_layout.addWidget(self.detail_content)
        
        panel_layout.addWidget(content_widget)
        
        self.panel_animation = QPropertyAnimation(self.detail_panel, b"pos")
        self.panel_animation.setDuration(300)
        self.panel_animation.setEasingCurve(QEasingCurve.OutCubic)

    def refresh_tasks(self):
        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        log_dir = "./log"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        files = [f for f in os.listdir(log_dir) 
                if f.startswith("CORELOG_") 
                and not f.endswith("_result") 
                and os.path.isfile(os.path.join(log_dir, f))]
        
        parsed_files = []
        for file in files:
            try:
                parts = file[8:].split('_') 
                if len(parts) >= 4:
                    date_part = parts[0] + "-" + parts[1] + "-" + parts[2] + " " + parts[3][:2] + ":" + parts[3][2:4] + ":" + parts[3][4:6]
                    dt = datetime.strptime(date_part, "%Y-%m-%d %H:%M:%S")
                    parsed_files.append((dt, file))
            except Exception as e:
                print(f"无法解析文件名: {file}, 错误: {e}")
                
        parsed_files.sort(key=lambda x: x[0], reverse=False) 
        
        for i, (dt, file) in enumerate(parsed_files):
            card = self.create_task_card(i+1, file, dt.strftime("%Y-%m-%d %H:%M:%S"))
            self.card_layout.addWidget(card)

    def create_task_card(self, index: int, file_name: str, time_str: str) -> CardWidget:
        card = CardWidget(self)
        card.setFixedHeight(120)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        title_label = StrongBodyLabel(f"Task{index}", card)
        subtitle_label = BodyLabel(time_str, card)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addStretch()
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        result_btn = PushButton("结果", card)
        result_btn.setStyleSheet(StyleFile.push_button_qss)
        result_btn.clicked.connect(lambda: self._on_result_clicked(file_name))
        
        info_btn = PushButton("详细信息", card)
        info_btn.setStyleSheet(StyleFile.push_button_qss)
        info_btn.clicked.connect(lambda: self._on_info_clicked(file_name))
        
        error_btn = PushButton("错误日志", card)
        error_btn.setStyleSheet(StyleFile.push_button_qss)
        error_btn.clicked.connect(lambda: self._on_error_clicked(file_name))
        
        delete_btn = PushButton("删除", card)
        delete_btn.setStyleSheet(StyleFile.push_button_qss)
        delete_btn.clicked.connect(lambda: self._on_delete_clicked(file_name))
        
        button_layout.addWidget(result_btn)
        button_layout.addWidget(info_btn)
        button_layout.addWidget(error_btn)
        button_layout.addStretch()
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        
        return card

    def _detect_encoding(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                if encoding is None or result['confidence'] < 0.7:
                    return 'gbk'
                return encoding
        except Exception:
            return 'gbk'

    def _read_file_with_encoding(self, file_path):
        try:
            encoding = self._detect_encoding(file_path)
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            for encoding in ['gbk', 'gb2312', 'latin1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                return raw_data.decode('utf-8', errors='ignore')
        except Exception as e:
            return f"读取文件时出错: {str(e)}"

    def _on_result_clicked(self, file_name: str):
        result_file_name = file_name + "_result"
        file_path = os.path.join("./log", result_file_name)

        try:
            if os.path.exists(file_path):
                content = self._read_file_with_encoding(file_path)
                if content:
                    lines = content.split('\n')
                    existing_lines = [line for line in lines if "There is a security vulnerability" in line]
                    if existing_lines:
                        formatted_lines = []
                        for line in existing_lines:
                            formatted_line = line.replace("There is a security vulnerability", "存在")
                            formatted_lines.append(formatted_line)
                        result_content = "\n\n".join(formatted_lines)
                    else:
                        result_content = "未发现存在漏洞的条目"
                else:
                    result_content = "文件内容为空"
            else:
                result_content = f"结果文件不存在: {result_file_name}"
        except Exception as e:
            result_content = f"读取结果文件时出错: {str(e)}"
            
        self.show_detail_panel("结果", result_content)

    def _on_info_clicked(self, file_name: str):
        result_file_name = file_name + "_result"
        file_path = os.path.join("./log", result_file_name)
        
        try:
            if os.path.exists(file_path):
                content = self._read_file_with_encoding(file_path)
                if content:
                    content = content.replace(" None", "")
                else:
                    content = "文件内容为空"
            else:
                content = f"详细信息文件不存在: {result_file_name}"
        except Exception as e:
            content = f"读取详细信息文件时出错: {str(e)}"
            
        self.show_detail_panel("详细信息", content)

    def _on_error_clicked(self, file_name: str):
        file_path = os.path.join("./log", file_name)
        
        try:
            if os.path.exists(file_path):
                content = self._read_file_with_encoding(file_path)
                if not content:
                    content = "日志文件内容为空"
            else:
                content = f"日志文件不存在: {file_name}"
        except Exception as e:
            content = f"读取日志文件时出错: {str(e)}"
            
        self.show_detail_panel("错误日志", content)

    def _on_delete_clicked(self, file_name: str):
        original_file_path = os.path.join("./log", file_name)
        if os.path.exists(original_file_path):
            try:
                os.remove(original_file_path)
            except Exception as e:
                print(f"删除原始文件时出错: {str(e)}")
        
        result_file_name = file_name + "_result"
        result_file_path = os.path.join("./log", result_file_name)
        if os.path.exists(result_file_path):
            try:
                os.remove(result_file_path)
            except Exception as e:
                print(f"删除结果文件时出错: {str(e)}")
        
        self.refresh_tasks()

    def generate_test_report(self):
        try:
            from GenerateReport import main as generate_report_main
            generate_report_main()
            QMessageBox.information(self, "报告生成成功", f"测试报告已生成到项目根目录的scan_report.html")
        except Exception as e:
            QMessageBox.critical(self, "报告生成失败", f"生成测试报告时出错：\n{str(e)}")

    def show_detail_panel(self, title: str, content: str):
        self.detail_title.setText(title)
        if '<b>' in content or '<strong>' in content:
            self.detail_content.setHtml("<pre>" + content + "</pre>")
        else:
            self.detail_content.setPlainText(content)
        
        if self.panel_animation is None:
            self.panel_animation = QPropertyAnimation(self.detail_panel, b"pos")
            self.panel_animation.setDuration(300)
            self.panel_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        panel_width = self.detail_panel.width()
        self.detail_panel.setGeometry(
            self.width(),
            0,
            panel_width,
            self.height()
        )
        self.detail_panel.show()
        
        if self.panel_animation.state() == QPropertyAnimation.Running:
            self.panel_animation.stop()
            
        if self.panel_animation.targetObject() != self.detail_panel:
            self.panel_animation.setTargetObject(self.detail_panel)
            
        self.panel_animation.setStartValue(QPoint(self.width(), 0))
        self.panel_animation.setEndValue(QPoint(self.width() - panel_width, 0))
        self.panel_animation.start()

    def hide_detail_panel(self):
        if not hasattr(self, 'panel_animation') or not self.detail_panel or not self.detail_panel.isVisible():
            if self.detail_panel:
                self.detail_panel.hide()
            return
            
        if self.panel_animation is None:
            self.panel_animation = QPropertyAnimation(self.detail_panel, b"pos")
            self.panel_animation.setDuration(300)
            self.panel_animation.setEasingCurve(QEasingCurve.OutCubic)
            
        if self.panel_animation.state() == QPropertyAnimation.Running:
            self.panel_animation.stop()
            
        panel_width = self.detail_panel.width()

        if self.panel_animation.targetObject() != self.detail_panel:
            self.panel_animation.setTargetObject(self.detail_panel)
            
        self.panel_animation.setStartValue(QPoint(self.width() - panel_width, 0))
        self.panel_animation.setEndValue(QPoint(self.width(), 0))
        self.panel_animation.finished.connect(self._hide_panel_callback)
        self.panel_animation.start()
        
    def _hide_panel_callback(self):
        if self.detail_panel: 
            self.detail_panel.hide()
            try:
                if self.panel_animation:
                    self.panel_animation.finished.disconnect(self._hide_panel_callback)
            except:
                pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.detail_panel and self.detail_panel.isVisible():
            self.detail_panel.setGeometry(
                self.width() - self.detail_panel.width(),
                0,
                self.detail_panel.width(),
                self.height()
            )