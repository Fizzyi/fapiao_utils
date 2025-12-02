import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QListWidget, QFileDialog, QMessageBox,
                             QCheckBox, QGroupBox, QComboBox, QTextBrowser, QListWidgetItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

from func import rename_main


class InvoiceRenameTool(QMainWindow):
    def __init__(self):
        super().__init__()
        # 初始化实例变量
        self.selected_files = []  # 存储选中的PDF文件路径
        self.save_dir = ""  # 保存目录（默认原目录）
        # 定义所有可用于命名的参数
        self.invoice_params = {
            "fphm": "发票号码",
            "fpsj": "发票时间",
            "xfmc": "销方名称",
            "xfsh": "销方税号",
            "gfmc": "购方名称",
            "gfsh": "购方税号",
            "fpje": "发票金额"
        }
        # 存储选中参数的顺序（核心：用于排序）
        self.selected_params_order = []
        self.init_ui()

    def init_ui(self):
        # 窗口基本设置
        self.setWindowTitle("发票PDF批量重命名工具")
        self.setGeometry(100, 100, 850, 700)  # 调整窗口尺寸

        # 中心部件和主布局（整体浅色日间风格）
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            }
        """)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # 1. 标题区域
        title_label = QLabel("发票PDF批量重命名工具")
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: 600;
            color: #1f2933;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label = QLabel("从发票内容自动解析并批量重命名 PDF 文件")
        subtitle_label.setStyleSheet("""
            font-size: 12px;
            color: #62727b;
        """)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)

        # 2. 核心功能区：参数组合+排序（直接显示，无需切换）
        core_layout = QVBoxLayout()

        # 参数选择与排序布局（左右分栏）
        params_sort_layout = QHBoxLayout()

        # 左侧：参数选择分组框
        left_group = QGroupBox("选择要包含的参数（可多选）")
        left_group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: 500;
                border: 1px solid #e0e4e8;
                border-radius: 8px;
                margin-top: 18px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
                background-color: transparent;
                color: #3e4c59;
            }
        """)
        left_layout = QVBoxLayout(left_group)

        # 存储参数复选框
        self.param_checkboxes = {}
        param_list = list(self.invoice_params.items())

        # 一列展示复选框
        left_col = QVBoxLayout()
        for i, (param_key, param_name) in enumerate(param_list):
            checkbox = QCheckBox(param_name)
            # 现代风格的参数选择：更大的勾选框和统一主色
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 12px;
                    margin: 4px 0;
                    padding: 4px 4px;
                    color: #334e68;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox::indicator:unchecked {
                    border: 1px solid #cbd2e1;
                    border-radius: 4px;
                    background: #ffffff;
                }
                QCheckBox::indicator:checked {
                    border: 1px solid #2563eb;
                    border-radius: 4px;
                    background: #2563eb;
                }
                QCheckBox:hover {
                    background-color: #eef2ff;
                    border-radius: 4px;
                }
                QCheckBox:checked {
                    background-color: #eef2ff;
                    border-radius: 4px;
                }
            """)
            checkbox.stateChanged.connect(self.on_param_check)  # 绑定勾选事件
            self.param_checkboxes[param_key] = checkbox
            left_col.addWidget(checkbox)

        left_layout.addLayout(left_col)
        params_sort_layout.addWidget(left_group, stretch=1)  # 左侧占1份宽度

        # 中间：排序按钮（垂直排列）
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.setSpacing(12)

        primary_button_style = """
            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                font-size: 12px;
                border-radius: 999px;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
            QPushButton:disabled {
                background-color: #cbd2e1;
                color: #9fb3c8;
            }
        """

        # 上移按钮
        self.up_btn = QPushButton("↑ 上移")
        self.up_btn.setStyleSheet(primary_button_style)
        self.up_btn.clicked.connect(self.move_param_up)
        self.up_btn.setDisabled(True)  # 初始禁用
        btn_layout.addWidget(self.up_btn)

        # 下移按钮
        self.down_btn = QPushButton("↓ 下移")
        self.down_btn.setStyleSheet(primary_button_style)
        self.down_btn.clicked.connect(self.move_param_down)
        self.down_btn.setDisabled(True)  # 初始禁用
        btn_layout.addWidget(self.down_btn)

        params_sort_layout.addLayout(btn_layout)  # 中间按钮区域

        # 右侧：选中参数顺序显示
        right_group = QGroupBox("当前参数顺序（选中项可排序）")
        right_group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: 500;
                border: 1px solid #e0e4e8;
                border-radius: 8px;
                margin-top: 18px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
                background-color: transparent;
                color: #3e4c59;
            }
        """)
        right_layout = QVBoxLayout(right_group)

        # 用QListWidget显示选中参数的顺序
        self.order_list = QListWidget()
        # 高亮当前选中项，方便和左侧复选框对应
        self.order_list.setStyleSheet("""
            QListWidget {
                font-size: 11px;
                background-color: #ffffff;
                border: none;
            }
            QListWidget::item {
                padding: 4px 6px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
                border-radius: 4px;
            }
        """)
        self.order_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)  # 单选
        self.order_list.itemClicked.connect(self.on_order_item_selected)  # 绑定选中事件
        right_layout.addWidget(self.order_list)

        params_sort_layout.addWidget(right_group, stretch=1)  # 右侧占1份宽度

        core_layout.addLayout(params_sort_layout)

        # 分隔符设置
        separator_layout = QHBoxLayout()
        separator_label = QLabel("参数分隔符：")
        separator_label.setStyleSheet("font-size: 13px; font-weight: 500; color: #3e4c59;")
        self.separator_combo = QComboBox()
        self.separator_combo.addItems(["_（下划线）", "-（短横线）", "（空格）", "·（点）", "无分隔符"])
        self.separator_combo.setCurrentIndex(0)  # 默认下划线
        self.separator_combo.setStyleSheet("""
            QComboBox {
                font-size: 12px;
                padding: 6px 8px;
                min-width: 150px;
                border-radius: 6px;
                border: 1px solid #d0d7de;
                background-color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        separator_layout.addWidget(separator_label)
        separator_layout.addWidget(self.separator_combo)
        separator_layout.addStretch()
        core_layout.addLayout(separator_layout)

        # 预览区域（卡片样式）
        preview_label = QLabel("命名预览（实时更新）：")
        preview_label.setStyleSheet("font-size: 13px; font-weight: 500; color: #3e4c59;")
        core_layout.addWidget(preview_label)

        self.preview_browser = QTextBrowser()
        self.preview_browser.setStyleSheet("""
            QTextBrowser {
                font-size: 12px;
                padding: 10px;
                background-color: #ffffff;
                color: #243b53;
                border: 1px solid #e0e4e8;
                border-radius: 8px;
            }
        """)
        self.preview_browser.setFixedHeight(60)
        core_layout.addWidget(self.preview_browser)

        # 绑定预览更新事件
        self.separator_combo.currentIndexChanged.connect(self.update_preview)

        main_layout.addLayout(core_layout)

        # 3. 文件选择区域
        file_layout = QVBoxLayout()
        file_label = QLabel("已选择的文件：")
        file_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #3e4c59;")
        file_layout.addWidget(file_label)

        # 文件列表显示
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                font-size: 12px;
                background-color: #ffffff;
                border: 1px solid #e0e4e8;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 4px 6px;
            }
        """)
        file_layout.addWidget(self.file_list)

        # 按钮布局
        file_btn_layout = QHBoxLayout()
        # 选择文件按钮
        self.select_btn = QPushButton("批量选择PDF文件")
        self.select_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                font-size: 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)
        self.select_btn.clicked.connect(self.select_files)
        file_btn_layout.addWidget(self.select_btn)

        # 清空选择按钮
        self.clear_btn = QPushButton("清空选择")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e11d48;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #be123c;
            }
            QPushButton:pressed {
                background-color: #9f1239;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_files)
        file_btn_layout.addWidget(self.clear_btn)

        file_layout.addLayout(file_btn_layout)
        main_layout.addLayout(file_layout)

        # 4. 保存目录选择
        save_layout = QHBoxLayout()
        save_label = QLabel("保存目录：")
        save_label.setStyleSheet("font-size: 13px; color: #3e4c59;")
        self.save_dir_label = QLabel("默认：原文件所在目录")
        self.save_dir_label.setStyleSheet("font-size: 12px; color: #7b8794;")
        self.save_dir_btn = QPushButton("更改保存目录")
        self.save_dir_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)
        self.save_dir_btn.clicked.connect(self.select_save_dir)
        save_layout.addWidget(save_label)
        save_layout.addWidget(self.save_dir_label)
        save_layout.addStretch()
        save_layout.addWidget(self.save_dir_btn)
        main_layout.addLayout(save_layout)

        # 5. 执行按钮（放大尺寸，更醒目）
        self.execute_btn = QPushButton("开始批量重命名")
        self.execute_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                border: none;
                padding: 12px 32px;
                font-size: 15px;
                font-weight: 600;
                border-radius: 999px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
            QPushButton:disabled {
                background-color: #cbd2e1;
                color: #9fb3c8;
            }
        """)
        self.execute_btn.clicked.connect(self.batch_rename)
        self.execute_btn.setDisabled(True)  # 未选择文件时禁用
        main_layout.addWidget(self.execute_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # 初始化预览
        self.update_preview()

    def on_param_check(self, state):
        """参数勾选状态变化时更新顺序列表和预览"""
        # 遍历所有复选框，更新选中参数顺序
        self.selected_params_order.clear()
        for param_key, checkbox in self.param_checkboxes.items():
            if checkbox.isChecked():
                self.selected_params_order.append(param_key)

        # 更新顺序列表显示
        self.update_order_list()
        # 实时更新预览
        self.update_preview()
        # 更新排序按钮状态
        self.update_sort_buttons_state()

    def update_order_list(self):
        """更新参数顺序列表的显示"""
        self.order_list.clear()
        for param_key in self.selected_params_order:
            param_name = self.invoice_params[param_key]
            QListWidgetItem(param_name, self.order_list)

    def on_order_item_selected(self, item):
        """选中顺序列表中的项时，更新排序按钮状态"""
        self.update_sort_buttons_state()

    def update_sort_buttons_state(self):
        """根据当前选中项和列表长度，更新上移/下移按钮的启用状态"""
        selected_item = self.order_list.currentItem()
        if not selected_item or len(self.selected_params_order) <= 1:
            # 无选中项或只有1个参数，禁用两个按钮
            self.up_btn.setDisabled(True)
            self.down_btn.setDisabled(True)
            return

        # 获取当前选中项的索引
        current_index = self.order_list.row(selected_item)
        # 第一个项不能上移，最后一个项不能下移
        self.up_btn.setDisabled(current_index == 0)
        self.down_btn.setDisabled(current_index == len(self.selected_params_order) - 1)

    def move_param_up(self):
        """将选中的参数上移一位"""
        selected_item = self.order_list.currentItem()
        if not selected_item:
            return

        current_index = self.order_list.row(selected_item)
        if current_index > 0:
            # 交换列表中的位置
            self.selected_params_order[current_index], self.selected_params_order[current_index - 1] = \
                self.selected_params_order[current_index - 1], self.selected_params_order[current_index]
            # 更新列表显示和预览
            self.update_order_list()
            # 保持选中状态
            self.order_list.setCurrentRow(current_index - 1)
            self.update_preview()
            self.update_sort_buttons_state()

    def move_param_down(self):
        """将选中的参数下移一位"""
        selected_item = self.order_list.currentItem()
        if not selected_item:
            return

        current_index = self.order_list.row(selected_item)
        if current_index < len(self.selected_params_order) - 1:
            # 交换列表中的位置
            self.selected_params_order[current_index], self.selected_params_order[current_index + 1] = \
                self.selected_params_order[current_index + 1], self.selected_params_order[current_index]
            # 更新列表显示和预览
            self.update_order_list()
            # 保持选中状态
            self.order_list.setCurrentRow(current_index + 1)
            self.update_preview()
            self.update_sort_buttons_state()

    def get_separator(self):
        """获取选中的分隔符"""
        separator_map = {
            0: "_",
            1: "-",
            2: " ",
            3: "·",
            4: ""
        }
        return separator_map[self.separator_combo.currentIndex()]

    def update_preview(self):
        """预览：展示「选中参数+分隔符」的效果"""
        if not self.selected_params_order:
            self.preview_browser.setText("请至少选择一个命名参数！")
            return

        # 获取参数显示名称（按当前顺序）
        param_display_names = [self.invoice_params[key] for key in self.selected_params_order]
        # 获取选中的分隔符
        separator = self.get_separator()

        # 生成模板和示例
        template_text = separator.join(param_display_names) + ".pdf"

        example_map = {
            "fphm": "25502000000102496258",
            "fpsj": "20240520",
            "xfmc": "XX科技有限公司",
            "xfsh": "91110105MA01234567",
            "gfmc": "YY贸易公司",
            "gfsh": "91310115MB67890123",
            "fpje": "1234.56"
        }
        example_params = [example_map[key] for key in self.selected_params_order]
        example_text = separator.join(example_params) + ".pdf"

        self.preview_browser.setText(f"模板：{template_text}\n示例：{example_text}")

    def select_files(self):
        """批量选择PDF文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择PDF文件",
            "",
            "PDF文件 (*.pdf);;所有文件 (*.*)"
        )
        if files:
            # 去重并添加到列表
            new_files = [f for f in files if f not in self.selected_files]
            self.selected_files.extend(new_files)
            # 更新文件列表显示
            self.file_list.addItems([os.path.basename(f) for f in new_files])
            # 启用执行按钮
            self.execute_btn.setDisabled(False)

    def clear_files(self):
        """清空已选择的文件"""
        self.selected_files.clear()
        self.file_list.clear()
        self.execute_btn.setDisabled(True)

    def select_save_dir(self):
        """选择保存目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择保存目录")
        if dir_path:
            self.save_dir = dir_path
            self.save_dir_label.setText(f"自定义：{dir_path}")
            self.save_dir_label.setStyleSheet("font-size: 12px; color: #27ae60;")

    def generate_invoice_params(self, idx):
        """生成发票参数的示例数据（实际使用时可替换为从PDF读取的真实数据）"""
        return {
            "fphm": f"2550200000010249625{idx}",
            "fpsj": f"202405{20 + idx % 10}",  # 日期变化
            "xfmc": "XX科技有限公司",
            "xfsh": "91110105MA01234567",
            "gfmc": "YY贸易公司",
            "gfsh": "91310115MB67890123",
            "fpje": f"{1000 + idx * 123.45:.2f}"  # 金额变化
        }

    def batch_rename(self):
        """执行批量重命名（仅按参数组合+排序+分隔符）"""
        if not self.selected_files:
            QMessageBox.warning(self, "警告", "请先选择要重命名的PDF文件！")
            return

        if not self.selected_params_order:
            QMessageBox.warning(self, "警告", "请至少选择一个命名参数！")
            return

        success_count = 0
        fail_count = 0
        fail_files = []

        # 处理每个文件
        for idx, file_path in enumerate(self.selected_files, 1):
            try:
                # 获取文件信息
                file_dir = os.path.dirname(file_path)
                original_name = os.path.basename(file_path)
                # 新文件名称
                # 核心逻辑：按选中参数顺序+分隔符生成文件名
                # 确定保存目录
                target_dir = self.save_dir if self.save_dir else file_dir
                title_dict = {
                    "title_params_list": self.selected_params_order,
                    "separator": self.get_separator()
                }
                if rename_main(file_path, target_dir, title_dict):
                    success_count += 1
                else:
                    fail_count += 1
                    fail_files.append(f"{original_name}：重命名失败")
            except Exception as e:
                fail_count += 1
                fail_files.append(f"{original_name}：{str(e)}")

        # 显示结果提示
        result_msg = f"重命名完成！\n成功：{success_count} 个文件\n失败：{fail_count} 个文件"
        if fail_files:
            result_msg += "\n\n失败文件详情：\n" + "\n".join(fail_files)

        QMessageBox.information(self, "结果", result_msg)

        # 清空选择（重命名后文件路径已改变）
        self.clear_files()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 使用 Fusion 风格并强制日间模式浅色调
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#f5f5f5"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f0f0f0"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#2c3e50"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#2c3e50"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#2c3e50"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#3498db"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    window = InvoiceRenameTool()
    window.show()
    sys.exit(app.exec())
