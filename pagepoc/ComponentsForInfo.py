from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem
from PySide6.QtCore import Qt, Signal
from qfluentwidgets import (
    TableWidget, TableItemDelegate, PushButton, 
    SubtitleLabel, LineEdit, ToolButton, FluentIcon as FIF
)

from pagepoc import StyleFile
import time


class ReusableTableWidget(QWidget):
    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.headers = headers
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = TableWidget()
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setItemDelegate(TableItemDelegate(self.table))
        self.table.setRowCount(0)
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.setEditTriggers(TableWidget.NoEditTriggers)
        self.table.setStyleSheet(StyleFile.table_widget_qss)
        self.table.setMinimumWidth(1200)
        
        layout.addWidget(self.table)
        
    def set_data(self, data_list):
        """设置表格数据"""
        self.table.setRowCount(0)
        for row, data in enumerate(data_list):
            self.table.insertRow(row)
            self.fill_row_data(row, data)
            
    def fill_row_data(self, row, data):
        """填充行数据，子类需要重写此方法"""
        raise NotImplementedError("子类需要实现fill_row_data方法")
        
    def adjust_column_widths(self):
        """调整列宽"""
        if self.table.columnCount() == 0:
            return
        self.table.resizeColumnsToContents()
        
        total_width = self.table.viewport().width()
        if total_width < 100:
            total_width = 800
        
        content_widths = []
        for i in range(self.table.columnCount()):
            content_widths.append(self.table.columnWidth(i))
        content_total = sum(content_widths)
        
        if content_total < total_width:
            extra_space = total_width - content_total
            extra_per_column = extra_space / (self.table.columnCount() - 1)
            for i in range(self.table.columnCount() - 1):
                new_width = max(content_widths[i], int(content_widths[i] + extra_per_column))
                self.table.setColumnWidth(i, new_width)
        if self.table.columnCount() > 0:
            self.table.setColumnWidth(self.table.columnCount()-1, max(content_widths[-1], 150))


class PocTableWidget(ReusableTableWidget):
    """POC信息表格组件"""
    
    detail_requested = Signal(str, int)  
    modify_requested = Signal(int)       
    delete_requested = Signal(int)       
    
    def __init__(self, headers, parent=None):
        super().__init__(headers, parent)
        self.row_poc_ids = []
        
    def set_data(self, data_list):
        """设置表格数据"""
        self.table.setRowCount(0)
        self.row_poc_ids = [] 
        for row, data in enumerate(data_list):
            self.table.insertRow(row)
            self.fill_row_data(row, data)
            
    def fill_row_data(self, row, poc_data):
        """填充POC表格行数据"""
        # 数据顺序为: created_time, poc_id, vul_name, vul_id, vul_type, vul_level, enabled
        if isinstance(poc_data, (list, tuple)) and len(poc_data) >= 7:
            created_time = poc_data[0]
            poc_id = str(poc_data[1]) if len(poc_data) > 1 else ""
            vul_name = str(poc_data[2]) if len(poc_data) > 2 else ""
            vul_id = str(poc_data[3]) if len(poc_data) > 3 else ""
            vul_type = str(poc_data[4]) if len(poc_data) > 4 else ""
            vul_level = str(poc_data[5]) if len(poc_data) > 5 else ""
            enable = bool(poc_data[6]) if len(poc_data) > 6 else False
        else:
            created_time = ""
            poc_id = ""
            vul_name = ""
            vul_id = ""
            vul_type = ""
            vul_level = ""
            enable = False
        
        if row >= len(self.row_poc_ids):
            self.row_poc_ids.append(poc_id)
        else:
            self.row_poc_ids[row] = poc_id
        
        try:
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(created_time)))
        except:
            formatted_time = created_time
        
        time_item = QTableWidgetItem(formatted_time)
        self.table.setItem(row, 0, time_item)

        name_item = QTableWidgetItem(vul_name)
        self.table.setItem(row, 1, name_item)
        
        id_item = QTableWidgetItem(vul_id)
        self.table.setItem(row, 2, id_item)
        
        type_item = QTableWidgetItem(vul_type)
        type_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.table.setItem(row, 3, type_item)
        
        level_item = QTableWidgetItem(vul_level)
        level_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.table.setItem(row, 4, level_item)
        
        enable_text = "是" if enable else "否"
        enable_item = QTableWidgetItem(enable_text)
        enable_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.table.setItem(row, 5, enable_item)
        
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setAlignment(Qt.AlignCenter)
        buttons_layout.setSpacing(5)
        
        detail_button = PushButton("详情")
        detail_button.clicked.connect(
            lambda checked=False, pid=poc_id, r=row: self.detail_requested.emit(pid, r)
        )
        buttons_layout.addWidget(detail_button)
        
        modify_button = PushButton("修改")
        modify_button.setFixedHeight(30)
        modify_button.clicked.connect(
            lambda checked=False, r=row: self.modify_requested.emit(r)
        )
        buttons_layout.addWidget(modify_button)
        
        delete_button = PushButton("删除")
        delete_button.setFixedHeight(30)
        delete_button.clicked.connect(
            lambda checked=False, r=row: self.delete_requested.emit(r)
        )
        buttons_layout.addWidget(delete_button)
        
        self.table.setCellWidget(row, 6, buttons_widget)
        
    def get_poc_id_by_row(self, row):
        """根据行号获取POC ID"""
        if 0 <= row < len(self.row_poc_ids):
            return self.row_poc_ids[row]
        return None


class PaginationWidget(QWidget):
    page_changed = Signal(int)  
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 1
        self.total_pages = 1
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.prev_button = PushButton("上一页")
        self.next_button = PushButton("下一页")
        self.page_label = SubtitleLabel("第 1 页")
        self.page_label.setStyleSheet("font-size: 12px; color: #666666;")
        
        layout.addStretch(1)
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)

        layout.addWidget(self.prev_button)
        layout.addWidget(self.page_label)
        layout.addWidget(self.next_button)
        layout.addStretch(1)
        
    def update_pagination(self, current_page, total_pages, total_count):
        """更新分页信息"""
        self.current_page = current_page
        self.total_pages = total_pages
        
        self.page_label.setText(f"第 {current_page} 页，共 {total_pages} 页，总共 {total_count} 条")
        self.prev_button.setEnabled(current_page > 1)
        self.next_button.setEnabled(current_page < total_pages)
        
    def prev_page(self):
        if self.current_page > 1:
            self.page_changed.emit(self.current_page - 1)
            
    def next_page(self):
        if self.current_page < self.total_pages:
            self.page_changed.emit(self.current_page + 1)


class SearchBarWidget(QWidget):
    search_requested = Signal(str)  
    refresh_requested = Signal()    
    
    def __init__(self, placeholder_text="请输入搜索关键词", parent=None):
        super().__init__(parent)
        self.placeholder_text = placeholder_text
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_box = LineEdit()
        self.search_box.setPlaceholderText(self.placeholder_text)
        self.search_box.returnPressed.connect(self.on_search)
        
        self.search_button = ToolButton(FIF.SEARCH)
        self.refresh_button = ToolButton(FIF.SYNC)
        self.refresh_button.setToolTip("刷新数据")
        
        self.search_button.clicked.connect(self.on_search)
        self.refresh_button.clicked.connect(self.on_refresh)
        
        layout.addWidget(self.search_box)
        layout.addWidget(self.search_button)
        layout.addWidget(self.refresh_button)
        
    def on_search(self):
        keyword = self.search_box.text().strip()
        self.search_requested.emit(keyword)
        
    def on_refresh(self):
        self.search_box.clear()
        self.refresh_requested.emit()
        
    def get_search_text(self):
        return self.search_box.text().strip()
        
    def clear_search_text(self):
        self.search_box.clear()