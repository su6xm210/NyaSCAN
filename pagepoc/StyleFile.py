# 样式定义
group_qss = """
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
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;    
            padding: 0 10px;
            background-color: transparent;
            color: #666666;
            font-weight: 500;
            margin: -3px 0px 20px;
        }
    """

line_edit_qss = """
        LineEdit {
            padding: 4px 8px;
            border: 1px solid #d0d0d0;
            border-radius: 4px;
            background-color: white;
            selection-background-color: #4a90e2;
            selection-color: white;
            text-align: left;
        }
        LineEdit:focus {
            border: 1px solid #4a90e2;
            outline: none;
        }
    """

combo_box_qss = """
        ComboBox {
            padding: 6px;
            border: 1px solid #d0d0d0;
            border-radius: 4px;
            background-color: white;
        }
        ComboBox:hover {
            border: 1px solid #a0a0a0;
        }
        ComboBox:focus {
            border: 1px solid #4a90e2;
            outline: none;
        }
    """

check_box_qss = """
        CheckBox {
            spacing: 8px;
            font-size: 14px;
            padding: 0 5px;
        }
        CheckBox::indicator:unchecked {
            border: 1px solid #a0a0a0;
            border-radius: 3px;
            background-color: white;
        }
    """

text_edit_qss = """
        QTextEdit {
            padding: 4px 8px;
            border: 1px solid #d0d0d0;
            border-radius: 4px;
            background-color: white;
            selection-background-color: #4a90e2;
            selection-color: white;
            outline: none;
        }
        QTextEdit:focus {
            border: 1px solid #4a90e2;
            outline: none;
        }
    """

push_button_qss = """
        PushButton {
            padding: 4px 8px;
            border: 1px solid #d0d0d0;
            border-radius: 4px;
            background-color: white;
        }
        PushButton:hover {
            border: 1px solid #a0a0a0;
        }
    """

table_widget_qss = """
        TableWidget {
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: white;
        }
        TableWidget::item {
            padding: 5px;
            border: none;
            text-align: center;
            vertical-align: middle; 
        }
        QHeaderView::section {
            background-color: #f0f0f0;
            border: none;
            padding: 8px;
            font-weight: bold;
        }
    """