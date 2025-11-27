from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, Signal
from qfluentwidgets import SubtitleLabel, PushButton, InfoBar, MessageBox
import json

from pageother import SQLManager
from pagepoc.ComponentsForInfo import (
    PaginationWidget, 
    SearchBarWidget, PocTableWidget
)


class ShowPocInfo(QWidget):
    modify_poc_requested = Signal(object)
    def __init__(self, title: str, object_name: str = None):
        super().__init__()
        if object_name:
            self.setObjectName(object_name)
        self.page_size = 50
        self.current_search_keyword = ""
        self.current_page = 1
        self.total_pages = 1
        
        self.init_ui()
        self.load_poc_data()
        self.init_connections()
        self.init_detail_panel()
        
    def init_ui(self):
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")

        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = SubtitleLabel("POC信息")
        layout.addWidget(title_label)
        
        self.search_bar = SearchBarWidget("请输入搜索关键词")
        layout.addWidget(self.search_bar)
        
        headers = ["创建时间", "漏洞名称", "漏洞编号", "漏洞类型", "漏洞等级", "启用状态", "操作"]
        self.poc_table = PocTableWidget(headers)
        layout.addWidget(self.poc_table)

        self.pagination = PaginationWidget()
        layout.addWidget(self.pagination)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(content_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
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
        panel_layout.setContentsMargins(20, 20, 20, 20)
        
        self.detail_title = SubtitleLabel("POC详情")
        panel_layout.addWidget(self.detail_title)
        
        self.detail_text_edit = QTextEdit()
        self.detail_text_edit.setReadOnly(True)
        panel_layout.addWidget(self.detail_text_edit)
        
        close_button = PushButton("关闭")
        close_button.clicked.connect(self.hide_detail_panel)
        panel_layout.addWidget(close_button)
        
        self.panel_animation = QPropertyAnimation(self.detail_panel, b"pos")
        self.panel_animation.setDuration(300)
        self.panel_animation.setEasingCurve(QEasingCurve.OutCubic)
            
    def init_connections(self):
        self.search_bar.search_requested.connect(self.on_search)
        self.search_bar.refresh_requested.connect(self.on_refresh)
        self.pagination.page_changed.connect(self.on_page_changed)
        
        self.poc_table.detail_requested.connect(self.view_detail_by_id)
        self.poc_table.modify_requested.connect(self._modify_poc_handler)
        self.poc_table.delete_requested.connect(self.delete_poc)
        
    def _modify_poc_handler(self, row):
        """处理修改POC请求的中间函数"""
        self.modify_poc(row)
        
    def on_search(self, keyword):
        self.current_search_keyword = keyword
        self.load_poc_data(keyword, 1)
        
    def on_refresh(self):
        self.current_search_keyword = ""
        self.load_poc_data("", 1)
        
    def on_page_changed(self, page):
        self.load_poc_data(self.current_search_keyword, page)

    def load_poc_data(self, search_keyword="", page=1):
        self.current_page = page
        self.current_search_keyword = search_keyword
        
        try:
            if search_keyword:
                poc_data_list = SQLManager.query_poc(search_keyword, page, self.page_size)
                total_count = SQLManager.get_poc_count(search_keyword)
            else:
                poc_data_list = SQLManager.get_poc_info(page, self.page_size)
                total_count = SQLManager.get_total_poc_count()
                
            self.total_pages = (total_count + self.page_size - 1) // self.page_size
            
            self.poc_table.set_data(poc_data_list)
            self.pagination.update_pagination(page, self.total_pages, total_count)
                
        except Exception as e:
            print(f"获取数据出错: {e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.poc_table.adjust_column_widths()
        if self.detail_panel.isVisible():
            self.detail_panel.setGeometry(
                self.width() - self.detail_panel.width(),
                0,
                self.detail_panel.width(),
                self.height()
            )

    def view_detail_by_id(self, poc_id, row):
        
        if not poc_id:
            print("POC ID为空")
            return
        
        try:
            poc_info = SQLManager.query_poc_info(poc_id)
            
            if not poc_info:
                error_msg = f"未找到相关POC信息，查询ID: {poc_id}"
                print(error_msg)
                self.detail_text_edit.setPlainText(error_msg)
                self.show_detail_panel()
                return
                
            if not isinstance(poc_info, (tuple, list)):
                error_msg = f"POC信息格式错误，期望tuple或list，实际为: {type(poc_info)}"
                print(error_msg)
                self.detail_text_edit.setPlainText(error_msg)
                self.show_detail_panel()
                return
            
            def safe_get(lst, index, default=""):
                try:
                    return lst[index] if index < len(lst) else default
                except IndexError:
                    return default
            
            vul_name = safe_get(poc_info, 2, "未知")
            
            self.detail_title.setText(f"POC详情 - {vul_name}")
            
            poc_data = {
                "created_time": safe_get(poc_info, 0),
                "poc_id": safe_get(poc_info, 1),
                "vul_name": safe_get(poc_info, 2),
                "vul_id": safe_get(poc_info, 3),
                "vul_type": safe_get(poc_info, 4),
                "vul_level": safe_get(poc_info, 5),
                "enabled": safe_get(poc_info, 6),
                "need_cookie": safe_get(poc_info, 7),
                "write_content": safe_get(poc_info, 8),
                "request": {},
                "payloads": {},
                "rules": {}
            }
            
            try:
                request_data = safe_get(poc_info, 10)
                if request_data:
                    poc_data["request"] = json.loads(request_data) if isinstance(request_data, str) else request_data
            except Exception as e:
                print(f"解析request字段出错: {e}")
                
            try:
                payloads_data = safe_get(poc_info, 11)
                if payloads_data:
                    poc_data["payloads"] = json.loads(payloads_data) if isinstance(payloads_data, str) else payloads_data
            except Exception as e:
                print(f"解析payloads字段出错: {e}")
                
            try:
                rules_data = safe_get(poc_info, 12)
                if rules_data:
                    poc_data["rules"] = json.loads(rules_data) if isinstance(rules_data, str) else rules_data
            except Exception as e:
                print(f"解析rules字段出错: {e}")
            
            formatted_json = json.dumps(poc_data, ensure_ascii=False, indent=4)
            self.detail_text_edit.setPlainText(formatted_json)
            self.show_detail_panel()
            
        except Exception as e:
            error_msg = f"获取POC详情时出错: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self.detail_text_edit.setPlainText(error_msg)
            self.show_detail_panel()

    def modify_poc(self, row):
        poc_id = self.get_poc_id_by_row(row)
        if not poc_id:
            InfoBar.error(
                title="错误",
                content="无法获取POC ID",
                parent=self,
                duration=2000
            )
            return
        
        try:
            poc_info = SQLManager.query_poc_info(poc_id)
            if not poc_info:
                InfoBar.error(
                    title="错误",
                    content="未找到相关POC信息",
                    parent=self,
                    duration=2000
                )
                return
                
            self.modify_poc_requested.emit(poc_info)
            
        except Exception as e:
            InfoBar.error(
                title="错误",
                content=f"获取POC信息时出错: {str(e)}",
                parent=self,
                duration=2000
            )
            print(f"修改POC时出错: {e}")

    def delete_poc(self, row):
        """删除POC"""
        poc_id = self.get_poc_id_by_row(row)
        if not poc_id:
            InfoBar.error(
                title="错误",
                content="无法获取POC ID",
                parent=self,
                duration=2000
            )
            return
            
        vul_name = self.get_vul_name_by_row(row)
        message_box = MessageBox(
                "确认删除",
                f"确定要删除漏洞名称为 '{vul_name}' 的记录吗？",
                self
            )
        
        if message_box.exec():
            try:
                result = SQLManager.delete_poc_info(poc_id)
                if result:
                    InfoBar.success(
                        title="删除成功",
                        content=f"POC: {vul_name} 删除完成",
                        parent=self,
                        duration=2000
                    )
                    self.load_poc_data(self.current_search_keyword, self.current_page)
                else:
                    InfoBar.error(
                        title="删除失败",
                        content="删除操作未能成功执行",
                        parent=self,
                        duration=2000
                    )
            except Exception as e:
                InfoBar.error(
                    title="删除失败",
                    content=f"删除过程中出现错误: {str(e)}",
                    parent=self,
                    duration=2000
                )

    def get_poc_id_by_row(self, row):
        """
        根据行号获取POC ID
        """
        try:
            poc_id = self.poc_table.get_poc_id_by_row(row)
            return poc_id
        except Exception as e:
            print(f"获取POC ID时出错: {e}")
            return None
    
    def get_vul_name_by_row(self, row):
        try:
            poc_id = self.get_poc_id_by_row(row)
            if poc_id:
                poc_info = SQLManager.query_poc_info(poc_id)
                if poc_info and isinstance(poc_info, (tuple, list)) and len(poc_info) > 2:
                    return str(poc_info[2])  # 漏洞名称在索引2位置
            return "未知漏洞"
        except Exception as e:
            print(f"获取漏洞名称时出错: {e}")
            return "未知漏洞"
            
    def show_detail_panel(self):
        if not hasattr(self, 'panel_animation') or not self.detail_panel:
            return

        panel_width = self.detail_panel.width()
        self.detail_panel.setGeometry(
            self.width(),
            0,
            panel_width,
            self.height()
        )
        self.detail_panel.show()
        
        if self.panel_animation.targetObject() != self.detail_panel:
            self.panel_animation.setTargetObject(self.detail_panel)
            
        self.panel_animation.setStartValue(QPoint(self.width(), 0))
        self.panel_animation.setEndValue(QPoint(self.width() - panel_width, 0))
        self.panel_animation.start()
        
    def hide_detail_panel(self):
        """隐藏详情面板"""
        if not hasattr(self, 'panel_animation') or not self.detail_panel:
            self.detail_panel.hide()
            return

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