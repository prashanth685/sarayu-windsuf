from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, 
                            QPushButton, QLabel, QMessageBox, QScrollArea, QComboBox, 
                            QApplication, QTableWidget, QTableWidgetItem, QHeaderView,
                            QTabWidget, QSpinBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal
import sys
import datetime
import logging

app = QApplication.instance()
if app:
    # Global stylesheet for QMessageBox and QComboBox
    app.setStyleSheet("""
    QMessageBox {
        background-color: #ffffff !important;
        color: #000000 !important;
        font: 13px "Segoe UI" !important;
        border: 1px solid #cbd5e0 !important;
        padding: 10px !important;
    }

    QMessageBox QLabel {
        color: #000000 !important;
        background-color: transparent !important;
        font-weight: normal !important;
    }

    QMessageBox QLabel#qt_msgbox_label {
        color: #000000 !important;
        background-color: transparent !important;
    }

    QMessageBox QLabel#qt_msgbox_text_label {
        color: #000000 !important;
        background-color: transparent !important;
    }

    QMessageBox QPushButton {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #d1d5db !important;
        padding: 6px 12px !important;
        border-radius: 4px !important;
        min-width: 80px !important;
        font-weight: 500 !important;
    }
    QMessageBox QPushButton:hover {
        background-color: #2563eb !important;
        color: #ffffff !important;
    }
    QMessageBox QPushButton:pressed {
        background-color: #1d4ed8 !important;
        color: #ffffff !important;
    }

    QMessageBox QTextEdit {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 4px !important;
        padding: 4px !important;
    }

    QMessageBox QMessageBox {
        color: #000000 !important;
    }

    QMessageBox * {
        color: #000000 !important;
    }

    QMessageBox QLabel#qt_msgbox_exclamation_label {
        color: #000000 !important;
    }

    QMessageBox QLabel#qt_msgbox_informativelabel {
        color: #000000 !important;
    }

    QMessageBox QLabel#qt_msgbox_warninglabel {
        color: #000000 !important;
    }

    QMessageBox QLabel#qt_msgbox_critical_label {
        color: #000000 !important;
    }

    QComboBox {
        border: 1px solid #d1d5db;
        border-radius: 4px;
        padding: 6px;
        font-size: 13px;
        background-color: #ffffff;
        min-height: 28px;
        color: #000000;
    }
    QComboBox::drop-down {
        border-left: 1px solid #d1d5db;
        width: 20px;
    }
    QComboBox::down-arrow {
        image: none;
        width: 10px;
        height: 10px;
    }
    QComboBox:hover {
        border-color: #93c5fd;
    }
    QComboBox:focus {
        border-color: #3b82f6;
        outline: none;
    }
    QComboBox QAbstractItemView {
        border: 1px solid #d1d5db;
        background-color: #ffffff;
        color: #000000;
        selection-background-color: #3b82f6;
        selection-color: #ffffff;
        padding: 4px;
    }
    QComboBox QAbstractItemView::item {
        padding: 6px 8px;
        min-height: 20px;
        color: #000000;
    }
    QComboBox QAbstractItemView::item:selected {
        background-color: #3b82f6;
        color: #ffffff;
    }
""")

def show_message_box(title, text, icon_type=QMessageBox.Information):
    """Custom message box function to ensure proper text styling"""
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.setIcon(icon_type)
    
    # Force text color styling
    msg_box.setStyleSheet("""
        QMessageBox {
            background-color: #ffffff;
            color: #000000;
        }
        QMessageBox QLabel {
            color: #000000;
            background-color: transparent;
        }
        QMessageBox QPushButton {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #d1d5db;
            padding: 6px 12px;
            border-radius: 4px;
            min-width: 80px;
            font-weight: 500;
        }
        QMessageBox QPushButton:hover {
            background-color: #2563eb;
            color: #ffffff;
        }
    """)
    
    return msg_box

class CreateProjectWidget(QWidget):
    project_edited = pyqtSignal(str, list, str, str, str)  # Signal for edited project (new_project_name, updated_models, channel_count, ip_address, tag_name)

    def __init__(self, parent=None, edit_mode=False, existing_project_name=None, existing_models=None, existing_channel_count="DAQ4CH", existing_ip_address="", existing_tag_name=""):
        super().__init__(parent)
        self.parent = parent
        self.db = parent.db
        self.edit_mode = edit_mode
        self.existing_project_name = existing_project_name
        self.existing_models = existing_models or []
        self.existing_channel_count = existing_channel_count
        self.existing_ip_address = existing_ip_address
        self.existing_tag_name = existing_tag_name
        self.models = []
        self.available_types = ["Displacement", "Acc/Vel"]
        self.available_directions = ["Right", "Left"]
        self.available_channel_counts = ["DAQ4CH", "DAQ8CH", "DAQ10CH"]
        self.available_units_displacement = ["mil", "mm", "um","v"]
        self.available_units_accvel = ["g", "m/s²", "mm/s"]
        self.available_unit_types = ["Displacement", "Volts"]
        self.initUI()
        logging.debug(f"Initialized CreateProjectWidget in {'edit' if edit_mode else 'create'} mode for project: {existing_project_name}")

    def initUI(self):
        self.setStyleSheet("background-color: #f7f7f9;")

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(main_layout)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs
        self.general_tab = QWidget()
        self.advanced_tab = QWidget()
        self.io_tab = QWidget()
        
        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.advanced_tab, "Advanced")
        self.tabs.addTab(self.io_tab, "I/O")
        
        # Initialize tabs
        self.init_general_tab()
        self.init_advanced_tab()
        self.init_io_tab()
        
        # Add buttons at the bottom
        self.init_bottom_buttons()
        
    def init_advanced_tab(self):
        """Initialize the Advanced tab with sampling frequency and other settings"""
        layout = QVBoxLayout(self.advanced_tab)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create form for advanced settings
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # Sampling Frequency
        self.sampling_freq = QDoubleSpinBox()
        self.sampling_freq.setRange(0.1, 10000.0)
        self.sampling_freq.setValue(1000.0)
        self.sampling_freq.setSuffix(" Hz")
        self.sampling_freq.setStyleSheet("""
            QDoubleSpinBox {
                min-width: 200px;
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
            }
        """)
        form_layout.addRow("Sampling Frequency:", self.sampling_freq)
        
        # Input Delta Time
        self.delta_time = QDoubleSpinBox()
        self.delta_time.setRange(0.001, 10.0)
        self.delta_time.setValue(0.1)
        self.delta_time.setSuffix(" s")
        self.delta_time.setStyleSheet("""
            QDoubleSpinBox {
                min-width: 200px;
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
            }
        """)
        form_layout.addRow("Input Delta Time:", self.delta_time)
        
        # Number of Data Points
        self.num_data_points = QSpinBox()
        self.num_data_points.setRange(100, 1000000)
        self.num_data_points.setValue(1000)
        self.num_data_points.setStyleSheet("""
            QSpinBox {
                min-width: 200px;
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
            }
        """)
        form_layout.addRow("Number of Data Points:", self.num_data_points)
        
        # Delta RPM Button
        self.delta_rpm_btn = QPushButton("Delta RPM")
        self.delta_rpm_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 500;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        self.delta_rpm_btn.clicked.connect(self.on_delta_rpm_clicked)
        form_layout.addRow("", self.delta_rpm_btn)
        
        layout.addLayout(form_layout)
        layout.addStretch()
    
    def init_io_tab(self):
        """Initialize the I/O tab with IP address and tag name settings"""
        layout = QVBoxLayout(self.io_tab)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create form for I/O settings
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # IP Address Input
        self.ip_address = QLineEdit()
        self.ip_address.setPlaceholderText("Enter IP Address")
        self.ip_address.setStyleSheet("""
            QLineEdit {
                min-width: 200px;
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        form_layout.addRow("IP Address:", self.ip_address)
        
        # Tag Name Input
        self.tag_name = QLineEdit()
        self.tag_name.setPlaceholderText("Enter Tag Name")
        self.tag_name.setStyleSheet("""
            QLineEdit {
                min-width: 200px;
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        form_layout.addRow("Tag Name:", self.tag_name)
        
        # Send Button
        self.send_btn = QPushButton("Send Sensitivity Values")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px 20px;
                font-weight: 500;
                min-width: 180px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
            }
        """)
        self.send_btn.clicked.connect(self.send_sensitivity_values)
        form_layout.addRow("", self.send_btn)
        
        # Pre-populate fields if in edit mode
        if self.edit_mode:
            if self.existing_ip_address:
                self.ip_address.setText(self.existing_ip_address)
            if self.existing_tag_name:
                self.tag_name.setText(self.existing_tag_name)
        
        layout.addLayout(form_layout)
        layout.addStretch()
    
    def init_bottom_buttons(self):
        """Initialize the bottom buttons that appear below the tabs"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.setAlignment(Qt.AlignRight)
        
        # Back Button
        back_button = QPushButton("Back")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #6b7280;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
            }
        """)
        back_button.clicked.connect(self.back_to_select)
        
        # Create/Update Button
        self.create_button = QPushButton("Update Project" if self.edit_mode else "Create Project")
        self.create_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        self.create_button.clicked.connect(self.submit_project)
        
        button_layout.addWidget(back_button)
        button_layout.addWidget(self.create_button)
        
        # Add the button layout to the main layout (below tabs)
        self.layout().addLayout(button_layout)
    
    def get_sensitivity_values_from_table(self):
        """Get sensitivity values from the first model's table"""
        if not self.model_inputs:
            return None, "No models found. Please add a model in the General tab."
            
        try:
            # Get the first model's table
            model_widget, model_name_input, tag_name_input, channel_inputs, _ = self.model_inputs[0]
            if not channel_inputs:
                return None, "No channel configuration found in the model."
                
            table, _ = channel_inputs[0]  # Get the table from the first model
            sensitivity_values = []
            
            # Get sensitivity values from the table (column 3, 0-based index)
            for row in range(table.rowCount()):
                sensitivity_item = table.item(row, 3)
                if sensitivity_item and sensitivity_item.text().strip():
                    try:
                        value = float(sensitivity_item.text().strip())
                        sensitivity_values.append(value)
                    except ValueError:
                        return None, f"Invalid sensitivity value in row {row+1}. Please enter a valid number."
            
            if not sensitivity_values:
                return None, "No sensitivity values found in the table."
                
            return sensitivity_values, None
            
        except Exception as e:
            return None, f"Error reading sensitivity values: {str(e)}"

    def send_sensitivity_values(self):
        """Send sensitivity values via MQTT using values from the table"""
        try:
            import paho.mqtt.publish as publish
            
            # Get values from UI
            ip_address = self.ip_address.text().strip()
            tag_name = self.tag_name.text().strip()
            
            # Validate inputs
            if not ip_address:
                msg = show_message_box("Error", "Please enter an IP address", QMessageBox.Warning)
                msg.exec_()
                return
                
            if not tag_name:
                msg = show_message_box("Error", "Please enter a tag name", QMessageBox.Warning)
                msg.exec_()
                return
            
            # Get sensitivity values from the table
            sensitivity_values, error = self.get_sensitivity_values_from_table()
            if error:
                msg = show_message_box("Error", error, QMessageBox.Warning)
                msg.exec_()
                return
                
            # Get model name for the topic
            if not self.model_inputs:
                msg = show_message_box("Error", "No models found", QMessageBox.Warning)
                msg.exec_()
                return
                
            model_name = self.model_inputs[0][1].text().strip()
            if not model_name:
                model_name = "default_model"
            
            # Create MQTT topic and payload
            topic = f"{tag_name}"
            payload = {
                "sensitivity": sensitivity_values,
                # "channels": len(sensitivity_values),
                # "timestamp": datetime.datetime.now().isoformat(),
                # "model": model_name
            }
            
            # Send MQTT message
            self.send_btn.setEnabled(False)
            self.send_btn.setText("Sending...")
            QApplication.processEvents()  # Update UI
            
            try:
                publish.single(
                    topic,
                    payload=str(payload),
                    hostname=ip_address,
                    port=1883,
                    qos=1,
                    retain=False
                )
                msg = show_message_box("Success", 
                    f"Successfully sent {len(sensitivity_values)} sensitivity values to {topic}", QMessageBox.Information)
                msg.exec_()
            except Exception as e:
                msg = show_message_box("Error", 
                    f"Failed to send sensitivity values: {str(e)}\n\n"
                    f"Please check the IP address and MQTT broker status.", QMessageBox.Critical)
                msg.exec_()
            finally:
                self.send_btn.setEnabled(True)
                self.send_btn.setText("Send Sensitivity Values")
                
        except ImportError:
            msg = show_message_box("Error", 
                "MQTT client library not found. Please install it using: pip install paho-mqtt", QMessageBox.Critical)
            msg.exec_()
        except Exception as e:
            msg = show_message_box("Error", 
                f"An unexpected error occurred: {str(e)}", QMessageBox.Critical)
            msg.exec_()
            if 'send_btn' in locals():
                self.send_btn.setEnabled(True)
                self.send_btn.setText("Send Sensitivity Values")

    def on_delta_rpm_clicked(self):
        """Handle Delta RPM button click"""
        msg = show_message_box("Delta RPM", "Delta RPM button clicked", QMessageBox.Information)
        msg.exec_()
        # Add your Delta RPM logic here
    

    def get_combo_box_style(self):
        """Get consistent styling for QComboBox widgets"""
        return """
            QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 6px;
                font-size: 14px;
                background-color: #ffffff;
                color: #000000;
                min-height: 28px;
            }
            QComboBox:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QComboBox:hover {
                border-color: #93c5fd;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #d1d5db;
                background-color: #ffffff;
                color: #000000;
                selection-background-color: #3b82f6;
                selection-color: #ffffff;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                padding: 6px 8px;
                min-height: 20px;
                color: #000000;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #3b82f6;
                color: #ffffff;
            }
        """

    def init_general_tab(self):
        """Initialize the General tab with channel table and project details"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: 1px solid #d1d5db;
                background: #f9fafb;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #9ca3af;
                min-height: 20px;
                border-radius: 6px;
                border: none;
            }
            QScrollBar::handle:vertical:hover {
                background: #6b7280;
            }
            QScrollBar::handle:vertical:pressed {
                background: #4b5563;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar:horizontal {
                border: 1px solid #d1d5db;
                background: #f9fafb;
                height: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: #9ca3af;
                min-width: 20px;
                border-radius: 6px;
                border: none;
            }
            QScrollBar::handle:horizontal:hover {
                background: #6b7280;
            }
            QScrollBar::handle:horizontal:pressed {
                background: #4b5563;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
                width: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setAlignment(Qt.AlignCenter)
        scroll_layout.setSpacing(24)
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        
        # Main layout for general tab
        general_layout = QVBoxLayout(self.general_tab)
        general_layout.addWidget(scroll_area)
        
        card_widget = QWidget()
        card_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e5e7eb;
                padding: 24px;
            }
        """)
        self.card_layout = QVBoxLayout()
        self.card_layout.setSpacing(16)
        card_widget.setLayout(self.card_layout)
        scroll_layout.addWidget(card_widget)

        title_label = QLabel("Edit Project" if self.edit_mode else "Create New Project")
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: 600;
            color: #1a202c;
            margin-bottom: 8px;
        """)
        self.card_layout.addWidget(title_label, alignment=Qt.AlignCenter)

        subtitle_label = QLabel("General Settings")
        subtitle_label.setStyleSheet("""
            font-size: 14px;
            color: #6b7280;
            margin-bottom: 16px;
        """)
        self.card_layout.addWidget(subtitle_label, alignment=Qt.AlignCenter)

        project_details_label = QLabel("Project Details")
        project_details_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 500;
            color: #1a202c;
            margin-top: 16px;
            margin-bottom: 8px;
        """)
        self.card_layout.addWidget(project_details_label)

        project_form = QFormLayout()
        project_form.setSpacing(12)
        project_form.setLabelAlignment(Qt.AlignLeft)
        project_form.setFormAlignment(Qt.AlignCenter)
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Project name")
        if self.edit_mode and self.existing_project_name:
            self.project_name_input.setText(self.existing_project_name)
        self.project_name_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                min-width: 400px;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QLineEdit:hover {
                border-color: #93c5fd;
            }
        """)
        project_form.addRow("Project Name:", self.project_name_input)
        
        # Add more fields to the general tab as needed
        
        self.card_layout.addLayout(project_form)
        
        # Add channel table section
        channel_section = QLabel("Channel Configuration")
        channel_section.setStyleSheet("""
            font-size: 16px;
            font-weight: 500;
            color: #1a202c;
            margin-top: 16px;
            margin-bottom: 8px;
        """)
        self.card_layout.addWidget(channel_section)
        
        self.channel_count_combo = QComboBox()
        self.channel_count_combo.addItems(self.available_channel_counts)
        if self.edit_mode and self.existing_channel_count:
            self.channel_count_combo.setCurrentText(self.existing_channel_count)
        self.channel_count_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                min-width: 400px;
                background-color: #ffffff;
                color: #000000;
            }
            QComboBox:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QComboBox:hover {
                border-color: #93c5fd;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #d1d5db;
                background-color: #ffffff;
                color: #000000;
                selection-background-color: #3b82f6;
                selection-color: #ffffff;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                padding: 6px 8px;
                min-height: 20px;
                color: #000000;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #3b82f6;
                color: #ffffff;
            }
        """)
        self.channel_count_combo.currentTextChanged.connect(self.update_table)
        project_form.addRow("Channel Count:", self.channel_count_combo)
        self.card_layout.addLayout(project_form)

        add_model_button = QPushButton("+ Add Model")
        add_model_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                font-weight: 500;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        add_model_button.clicked.connect(self.add_model_input)
        self.card_layout.addWidget(add_model_button, alignment=Qt.AlignRight)

        self.model_layout = QVBoxLayout()
        self.model_layout.setSpacing(16)
        self.model_inputs = []
        self.card_layout.addLayout(self.model_layout)

        # Pre-populate models if in edit mode
        if self.edit_mode and self.existing_models:
            for model in self.existing_models:
                self.add_model_input(model)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.setAlignment(Qt.AlignLeft)

        back_button = QPushButton("Back")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #6b7280;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                font-weight: 500;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
            }
            QPushButton:pressed {
                background-color: #e2e8f0;
            }
        """)
        back_button.clicked.connect(self.back_to_select)
        button_layout.addWidget(back_button)

        create_button = QPushButton("Update Project" if self.edit_mode else "Create Project")
        create_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                font-weight: 500;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        create_button.clicked.connect(self.submit_project)
        button_layout.addWidget(create_button)

        # Move buttons to bottom of the window
        self.card_layout.addStretch()

    def update_table(self, channel_count):
        for widget, model_name_input, tag_name_input, channel_inputs, _ in self.model_inputs:
            for table, num_channels in channel_inputs:
                model_layout = widget.layout()
                model_layout.removeWidget(table)
                table.deleteLater()

            num_channels = {"DAQ4CH": 4, "DAQ8CH": 8, "DAQ10CH": 10}.get(channel_count, 4)
            table = QTableWidget(num_channels, 12)
            table.setHorizontalHeaderLabels(["S.No.", "Channel Name", "Channel Type", "Sensitivity", "Unit", "Subunit", "Correction Factor", "Gain", "Unit Type", "Angle", "Direction", "Shaft"])
            table.setStyleSheet("""
                QTableWidget {
                    border: 2px solid #e5e7eb;
                    border-radius: 8px;
                    background-color: #ffffff;
                    padding: 8px;
                    font-size: 14px;
                    gridline-color: #e5e7eb;
                    selection-background-color: #edf2f7;
                    selection-color: #1a202c;
                    alternate-background-color: #f9fafb;
                }
                QTableWidget::item {
                    padding: 12px 8px !important;
                    border-bottom: 1px solid #f1f5f9 !important;
                    color: #000000 !important;
                    font-size: 14px !important;
                    min-height: 45px !important;
                    background-color: transparent !important;
                }
                QTableWidget::item:selected {
                    background-color: #edf2f7 !important;
                    color: #000000 !important;
                }
                QTableWidget QLineEdit {
                    color: #000000 !important;
                    background-color: #ffffff !important;
                    border: 1px solid #d1d5db !important;
                    padding: 4px !important;
                    font-size: 14px !important;
                }
                QHeaderView::section {
                    background-color: #4a5568;
                    color: white;
                    padding: 12px;
                    font-weight: 600;
                    border: none;
                    border-bottom: 2px solid #2d3748;
                    font-size: 14px;
                    min-height: 55px;
                }
            """)
            table.horizontalHeader().setVisible(True)
            table.horizontalHeader().setStretchLastSection(True)
            table.horizontalHeader().setMinimumHeight(55)
            table.horizontalHeader().setDefaultSectionSize(120)
            table.verticalHeader().setVisible(False)
            table.setAlternatingRowColors(True)
            table.setEditTriggers(QTableWidget.AllEditTriggers)
            table.verticalHeader().setDefaultSectionSize(50)
            table.setMinimumHeight(table.verticalHeader().defaultSectionSize() * num_channels + table.horizontalHeader().height() + 40)
            table.setMaximumHeight(table.verticalHeader().defaultSectionSize() * num_channels + table.horizontalHeader().height() + 40)
            table.setMinimumWidth(1200)
            table.resizeColumnsToContents()
            
            # Set specific column widths for better layout
            header = table.horizontalHeader()
            header.resizeSection(0, 60)   # S.No.
            header.resizeSection(1, 150)  # Channel Name
            header.resizeSection(2, 120)  # Channel Type
            header.resizeSection(3, 100)  # Sensitivity
            header.resizeSection(4, 80)   # Unit
            header.resizeSection(5, 80)   # Subunit
            header.resizeSection(6, 120)  # Correction Factor
            header.resizeSection(7, 80)   # Gain
            header.resizeSection(8, 100)  # Unit Type
            header.resizeSection(9, 80)   # Angle
            header.resizeSection(10, 100) # Direction
            header.resizeSection(11, 80)  # Shaft

            for row in range(num_channels):
                item = QTableWidgetItem(str(row + 1))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, 0, item)
                table.setItem(row, 1, QTableWidgetItem(""))
                
                type_combo = QComboBox()
                type_combo.addItems(self.available_types)
                type_combo.setCurrentText("Displacement")
                type_combo.setStyleSheet(self.get_combo_box_style())
                type_combo.currentIndexChanged.connect(lambda _, r=row: self.update_unit_combo(table, r))
                table.setCellWidget(row, 2, type_combo)
                
                table.setItem(row, 3, QTableWidgetItem(""))
                
                unit_combo = QComboBox()
                unit_combo.addItems(self.available_units_displacement)
                unit_combo.setCurrentText("mil")
                unit_combo.setStyleSheet(self.get_combo_box_style())
                unit_combo.currentTextChanged.connect(lambda text, r=row: self.update_unit_type_based_on_unit(table, r))
                table.setCellWidget(row, 4, unit_combo)

                subunit_combo = QComboBox()
                subunit_combo.addItems(["pp", "pk", "rms"])
                subunit_combo.setCurrentText("pp")
                subunit_combo.setStyleSheet(self.get_combo_box_style())
                table.setCellWidget(row, 5, subunit_combo)
                
                table.setItem(row, 6, QTableWidgetItem(""))
                table.setItem(row, 7, QTableWidgetItem(""))
                unit_type_combo = QComboBox()
                unit_type_combo.addItems(self.available_unit_types)
                # Default to 'Displacement' unless unit is 'v'
                try:
                    current_unit_widget = table.cellWidget(row, 4)
                    current_unit_text = current_unit_widget.currentText().lower() if current_unit_widget else "mil"
                except Exception:
                    current_unit_text = "mil"
                unit_type_combo.setCurrentText("Volts" if current_unit_text == "v" else "Displacement")
                unit_type_combo.setStyleSheet(self.get_combo_box_style())
                table.setCellWidget(row, 8, unit_type_combo)
                table.setItem(row, 9, QTableWidgetItem(""))
                
                direction_combo = QComboBox()
                direction_combo.addItems(self.available_directions)
                direction_combo.setCurrentText("Right")
                direction_combo.setStyleSheet(self.get_combo_box_style())
                table.setCellWidget(row, 10, direction_combo)
                
                table.setItem(row, 11, QTableWidgetItem(""))

            model_layout.addWidget(table)
            channel_inputs[0] = (table, num_channels)

    def update_unit_type_based_on_unit(self, table, row):
        """Update unit type combo based on selected unit"""
        unit_type_combo = table.cellWidget(row, 8)
        if unit_type_combo:
            unit_combo = table.cellWidget(row, 4)
            if unit_combo:
                selected_unit = unit_combo.currentText().lower()
                unit_type_combo.setCurrentText("Volts" if selected_unit == "v" else "Displacement")

    def update_unit_combo(self, table, row):
        type_combo = table.cellWidget(row, 2)
        unit_combo = table.cellWidget(row, 4)
        current_type = type_combo.currentText()
        
        # Save current unit selection before clearing
        current_unit = unit_combo.currentText() if unit_combo else ""
        
        # Clear and update unit combo based on channel type
        unit_combo.clear()
        unit_items = self.available_units_displacement if current_type == "Displacement" else self.available_units_accvel
        unit_combo.addItems(unit_items)
        
        # Try to restore previous unit if it exists in the new list, otherwise set default
        if current_unit in unit_items:
            unit_combo.setCurrentText(current_unit)
        else:
            # Set default based on channel type
            if current_type == "Displacement":
                unit_combo.setCurrentText("mil")  # Default for displacement
            else:
                unit_combo.setCurrentText("g")   # Default for acc/vel
        
        # Update unit type combo based on selected unit
        unit_type_combo = table.cellWidget(row, 8)
        if unit_type_combo:
            selected_unit = unit_combo.currentText().lower()
            unit_type_combo.setCurrentText("Volts" if selected_unit == "v" else "Displacement")

    def add_model_input(self, existing_model=None):
        channel_count = self.channel_count_combo.currentText()
        num_channels = {"DAQ4CH": 4, "DAQ8CH": 8, "DAQ10CH": 10}.get(channel_count, 4)

        model_widget = QWidget()
        model_widget.setStyleSheet("""
            background-color: #fafafa;
            border-radius: 4px;
            padding: 16px;
            border: 1px solid #e5e7eb;
        """)
        model_layout = QVBoxLayout()
        model_layout.setSpacing(12)
        model_widget.setLayout(model_layout)

        model_header_layout = QHBoxLayout()
        model_header_layout.setSpacing(8)
        model_label = QLabel(f"Model {len(self.model_inputs) + 1}")
        model_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 500;
            color: #1a202c;
        """)
        model_header_layout.addWidget(model_label)

        remove_model_button = QPushButton("Remove Model")
        remove_model_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ef4444;
                border: none;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                color: #dc2626;
            }
            QPushButton:pressed {
                color: #b91c1c;
            }
        """)
        remove_model_button.clicked.connect(lambda: self.remove_model_input(model_widget))
        model_header_layout.addWidget(remove_model_button, alignment=Qt.AlignRight)
        model_layout.addLayout(model_header_layout)

        model_form = QFormLayout()
        model_form.setSpacing(12)
        model_form.setLabelAlignment(Qt.AlignLeft)
        model_form.setFormAlignment(Qt.AlignCenter)

        model_name_input = QLineEdit()
        model_name_input.setPlaceholderText("Model name")
        if existing_model:
            model_name = existing_model.get("name", "")
            if model_name.startswith(channel_count + "_"):
                model_name = model_name[len(channel_count) + 1:]
            model_name_input.setText(model_name)
        model_name_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                min-width: 400px;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QLineEdit:hover {
                border-color: #93c5fd;
            }
        """)
        model_form.addRow("Model Name:", model_name_input)

        tag_name_input = QLineEdit()
        tag_name_input.setPlaceholderText("Tag name")
        if existing_model:
            tag_name_input.setText(existing_model.get("tagName", ""))
        tag_name_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                min-width: 400px;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QLineEdit:hover {
                border-color: #93c5fd;
            }
        """)
        model_form.addRow("Tag Name:", tag_name_input)
        model_layout.addLayout(model_form)

        channels_label = QLabel("Channels")
        channels_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 500;
            color: #1a202c;
            margin-top: 8px;
            margin-bottom: 8px;
        """)
        model_layout.addWidget(channels_label)

        table = QTableWidget(num_channels, 12)
        table.setHorizontalHeaderLabels(["S.No.", "Channel Name", "Channel Type", "Sensitivity", "Unit", "Subunit", "Correction Factor", "Gain", "Unit Type", "Angle", "Direction", "Shaft"])
        table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                font-size: 14px;
                gridline-color: #e5e7eb;
                selection-background-color: #edf2f7;
                selection-color: #1a202c;
                alternate-background-color: #f9fafb;
                padding: 4px;
            }
            QTableWidget::item {
                padding: 12px 8px !important;
                border: none !important;
                min-height: 45px !important;
                color: #000000 !important;
                font-size: 14px !important;
                background-color: transparent !important;
            }
            QTableWidget::item:selected {
                background-color: #edf2f7 !important;
                color: #000000 !important;
            }
            QTableWidget QLineEdit {
                color: #000000 !important;
                background-color: #ffffff !important;
                border: 1px solid #d1d5db !important;
                padding: 4px !important;
                font-size: 14px !important;
            }
            QHeaderView::section {
                background-color: #4a5568;
                color: white;
                height: 55px;
                font-weight: 600;
                font-size: 14px;
                border: none;
                border-bottom: 2px solid #e5e7eb;
                padding: 8px 12px;
            }
        """)
        table.horizontalHeader().setVisible(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setMinimumHeight(55)
        table.horizontalHeader().setDefaultSectionSize(120)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.AllEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        table.verticalHeader().setDefaultSectionSize(50)
        table.setMinimumHeight(table.verticalHeader().defaultSectionSize() * num_channels + table.horizontalHeader().height() + 40)
        table.setMaximumHeight(table.verticalHeader().defaultSectionSize() * num_channels + table.horizontalHeader().height() + 40)
        table.setMinimumWidth(1200)
        table.resizeColumnsToContents()
        
        # Set specific column widths for better layout
        header = table.horizontalHeader()
        header.resizeSection(0, 60)   # S.No.
        header.resizeSection(1, 150)  # Channel Name
        header.resizeSection(2, 120)  # Channel Type
        header.resizeSection(3, 100)  # Sensitivity
        header.resizeSection(4, 80)   # Unit
        header.resizeSection(5, 80)   # Subunit
        header.resizeSection(6, 120)  # Correction Factor
        header.resizeSection(7, 80)   # Gain
        header.resizeSection(8, 100)  # Unit Type
        header.resizeSection(9, 80)   # Angle
        header.resizeSection(10, 100) # Direction
        header.resizeSection(11, 80)  # Shaft

        if existing_model and existing_model.get("channels"):
            for row, channel in enumerate(existing_model["channels"]):
                if row >= num_channels:
                    break
                item = QTableWidgetItem(str(row + 1))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, 0, item)
                table.setItem(row, 1, QTableWidgetItem(channel.get("channelName", "")))
                
                type_combo = QComboBox()
                type_combo.addItems(self.available_types)
                type_combo.setCurrentText(channel.get("type", "Displacement"))
                type_combo.setStyleSheet(self.get_combo_box_style())
                type_combo.currentIndexChanged.connect(lambda _, r=row: self.update_unit_combo(table, r))
                table.setCellWidget(row, 2, type_combo)
                
                table.setItem(row, 3, QTableWidgetItem(channel.get("sensitivity", "")))
                
                unit_combo = QComboBox()
                current_type = type_combo.currentText()
                unit_items = self.available_units_displacement if current_type == "Displacement" else self.available_units_accvel
                unit_combo.addItems(unit_items)
                unit_combo.setCurrentText(channel.get("unit", unit_items[0]))
                unit_combo.setStyleSheet(self.get_combo_box_style())
                unit_combo.currentTextChanged.connect(lambda text, r=row: self.update_unit_type_based_on_unit(table, r))
                table.setCellWidget(row, 4, unit_combo)

                subunit_combo = QComboBox()
                subunit_combo.addItems(["pp", "pk", "rms"])
                sub_val = str(channel.get("subunit", "pp") or "pp").lower()
                subunit_combo.setCurrentText("pp" if sub_val in ("pp", "pk-pk", "peak to peak") else ("pk" if sub_val in ("pk", "peak") else "rms"))
                subunit_combo.setStyleSheet(self.get_combo_box_style())
                table.setCellWidget(row, 5, subunit_combo)
                
                table.setItem(row, 6, QTableWidgetItem(channel.get("correctionValue", "")))
                table.setItem(row, 7, QTableWidgetItem(channel.get("gain", "")))
                unit_type_combo = QComboBox()
                unit_type_combo.addItems(self.available_unit_types)
                # Prefer existing channel unitType, else infer from unit
                existing_unit_type = channel.get("unitType")
                inferred_unit_type = "Volts" if str(channel.get("unit", "")).lower() == "v" else "Displacement"
                unit_type_combo.setCurrentText(existing_unit_type if existing_unit_type in self.available_unit_types else inferred_unit_type)
                unit_type_combo.setStyleSheet(self.get_combo_box_style())
                table.setCellWidget(row, 8, unit_type_combo)
                table.setItem(row, 9, QTableWidgetItem(channel.get("angle", "")))
                
                direction_combo = QComboBox()
                direction_combo.addItems(self.available_directions)
                direction_combo.setCurrentText(channel.get("angleDirection", "Right"))
                direction_combo.setStyleSheet(self.get_combo_box_style())
                table.setCellWidget(row, 10, direction_combo)
                
                table.setItem(row, 11, QTableWidgetItem(channel.get("shaft", "")))
        else:
            for row in range(num_channels):
                item = QTableWidgetItem(str(row + 1))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, 0, item)
                table.setItem(row, 1, QTableWidgetItem(""))
                
                type_combo = QComboBox()
                type_combo.addItems(self.available_types)
                type_combo.setCurrentText("Displacement")
                type_combo.setStyleSheet(self.get_combo_box_style())
                type_combo.currentIndexChanged.connect(lambda _, r=row: self.update_unit_combo(table, r))
                table.setCellWidget(row, 2, type_combo)
                
                table.setItem(row, 3, QTableWidgetItem(""))
                
                unit_combo = QComboBox()
                unit_combo.addItems(self.available_units_displacement)
                unit_combo.setCurrentText("mil")
                unit_combo.setStyleSheet(self.get_combo_box_style())
                unit_combo.currentTextChanged.connect(lambda text, r=row: self.update_unit_type_based_on_unit(table, r))
                table.setCellWidget(row, 4, unit_combo)

                subunit_combo = QComboBox()
                subunit_combo.addItems(["pp", "pk", "rms"])
                subunit_combo.setCurrentText("pp")
                subunit_combo.setStyleSheet(self.get_combo_box_style())
                table.setCellWidget(row, 5, subunit_combo)
                
                table.setItem(row, 6, QTableWidgetItem(""))
                table.setItem(row, 7, QTableWidgetItem(""))
                table.setItem(row, 8, QTableWidgetItem(""))
                table.setItem(row, 9, QTableWidgetItem(""))
                
                direction_combo = QComboBox()
                direction_combo.addItems(self.available_directions)
                direction_combo.setCurrentText("Right")
                direction_combo.setStyleSheet(self.get_combo_box_style())
                table.setCellWidget(row, 10, direction_combo)
                
                table.setItem(row, 11, QTableWidgetItem(""))

        model_layout.addWidget(table)

        self.model_inputs.append((model_widget, model_name_input, tag_name_input, [(table, num_channels)], channel_count))
        self.model_layout.addWidget(model_widget)

    def add_channel_to_table(self, table):
        current_rows = table.rowCount()
        table.setRowCount(current_rows + 1)
        item = QTableWidgetItem(str(current_rows + 1))
        item.setTextAlignment(Qt.AlignCenter)
        table.setItem(current_rows, 0, item)
        table.setItem(current_rows, 1, QTableWidgetItem(""))
        
        type_combo = QComboBox()
        type_combo.addItems(self.available_types)
        type_combo.setCurrentText("Displacement")
        type_combo.setStyleSheet(self.get_combo_box_style())
        type_combo.currentIndexChanged.connect(lambda _, r=current_rows: self.update_unit_combo(table, r))
        table.setCellWidget(current_rows, 2, type_combo)
        
        table.setItem(current_rows, 3, QTableWidgetItem(""))
        
        unit_combo = QComboBox()
        unit_combo.addItems(self.available_units_displacement)
        unit_combo.setCurrentText("mil")
        unit_combo.setStyleSheet(self.get_combo_box_style())
        unit_combo.currentTextChanged.connect(lambda text, r=current_rows: self.update_unit_type_based_on_unit(table, r))
        table.setCellWidget(current_rows, 4, unit_combo)

        subunit_combo = QComboBox()
        subunit_combo.addItems(["pp", "pk", "rms"])
        subunit_combo.setCurrentText("pp")
        subunit_combo.setStyleSheet(self.get_combo_box_style())
        table.setCellWidget(current_rows, 5, subunit_combo)
        
        table.setItem(current_rows, 6, QTableWidgetItem(""))
        table.setItem(current_rows, 7, QTableWidgetItem(""))
        unit_type_combo = QComboBox()
        unit_type_combo.addItems(self.available_unit_types)
        unit_type_combo.setCurrentText("Displacement")
        unit_type_combo.setStyleSheet(self.get_combo_box_style())
        table.setCellWidget(current_rows, 8, unit_type_combo)
        table.setItem(current_rows, 9, QTableWidgetItem(""))
        
        direction_combo = QComboBox()
        direction_combo.addItems(self.available_directions)
        direction_combo.setCurrentText("Right")
        direction_combo.setStyleSheet(self.get_combo_box_style())
        table.setCellWidget(current_rows, 10, direction_combo)
        
        table.setItem(current_rows, 11, QTableWidgetItem(""))
        table.setMinimumHeight(table.verticalHeader().defaultSectionSize() * (current_rows + 1) + table.horizontalHeader().height() + 40)
        table.setMaximumHeight(table.verticalHeader().defaultSectionSize() * (current_rows + 1) + table.horizontalHeader().height() + 40)
        table.resizeColumnsToContents()
        
        # Update column widths after adding new row
        header = table.horizontalHeader()
        header.resizeSection(0, 60)   # S.No.
        header.resizeSection(1, 150)  # Channel Name
        header.resizeSection(2, 120)  # Channel Type
        header.resizeSection(3, 100)  # Sensitivity
        header.resizeSection(4, 80)   # Unit
        header.resizeSection(5, 80)   # Subunit
        header.resizeSection(6, 120)  # Correction Factor
        header.resizeSection(7, 80)   # Gain
        header.resizeSection(8, 100)  # Unit Type
        header.resizeSection(9, 80)   # Angle
        header.resizeSection(10, 100) # Direction
        header.resizeSection(11, 80)  # Shaft

    def remove_model_input(self, model_widget):
        if len(self.model_inputs) > 1 or not self.edit_mode:
            for inputs in self.model_inputs:
                if inputs[0] == model_widget:
                    self.model_inputs.remove(inputs)
                    self.model_layout.removeWidget(model_widget)
                    model_widget.deleteLater()
                    for i, (widget, _, _, _, _) in enumerate(self.model_inputs):
                        widget.layout().itemAt(0).layout().itemAt(0).widget().setText(f"Model {i + 1}")
                    break

    def submit_project(self):
        project_name = self.project_name_input.text().strip()
        channel_count = self.channel_count_combo.currentText()
        ip_address = self.ip_address.text().strip()
        tag_name = self.tag_name.text().strip()
        
        if not project_name:
            msg = show_message_box("Error", "Project name cannot be empty!", QMessageBox.Warning)
            msg.exec_()
            return

        if not self.model_inputs:
            msg = show_message_box("Error", "At least one model is required!", QMessageBox.Warning)
            msg.exec_()
            return

        self.models = []
        for _, model_name_input, tag_name_input, channel_inputs, _ in self.model_inputs:
            model_name = model_name_input.text().strip()
            tag_name = tag_name_input.text().strip()
            if not model_name:
                msg = show_message_box("Error", f"Model name cannot be empty for model {len(self.models) + 1}!", QMessageBox.Warning)
                msg.exec_()
                return

            channels = []
            for table, num_channels in channel_inputs:
                for row in range(table.rowCount()):
                    channel_name = table.item(row, 1).text().strip() if table.item(row, 1) else ""
                    if not channel_name:
                        msg = show_message_box("Error", f"Channel name cannot be empty for model '{model_name}'!", QMessageBox.Warning)
                        msg.exec_()
                        return
                    channels.append({
                        "channelName": channel_name,
                        "type": table.cellWidget(row, 2).currentText() if table.cellWidget(row, 2) else "Displacement",
                        "sensitivity": table.item(row, 3).text().strip() if table.item(row, 3) else "",
                        "unit": table.cellWidget(row, 4).currentText() if table.cellWidget(row, 4) else "mil",
                        "subunit": table.cellWidget(row, 5).currentText() if table.cellWidget(row, 5) else "pp",
                        "correctionValue": table.item(row, 6).text().strip() if table.item(row, 6) else "",
                        "gain": table.item(row, 7).text().strip() if table.item(row, 7) else "",
                        "unitType": (table.cellWidget(row, 8).currentText().strip() if table.cellWidget(row, 8) else (table.item(row, 8).text().strip() if table.item(row, 8) else "")),
                        "angle": table.item(row, 9).text().strip() if table.item(row, 9) else "",
                        "angleDirection": table.cellWidget(row, 10).currentText() if table.cellWidget(row, 10) else "Right",
                        "shaft": table.item(row, 11).text().strip() if table.item(row, 11) else ""
                    })

            if not channels:
                msg = show_message_box("Error", f"At least one channel is required for model '{model_name}'!", QMessageBox.Warning)
                msg.exec_()
                return

            self.models.append({
                "name": f"{channel_count}_{model_name}",
                "tagName": tag_name,
                "channels": channels
            })

        try:
            if self.edit_mode:
                self.project_edited.emit(project_name, self.models, channel_count, ip_address, tag_name)
            else:
                success, message = self.db.create_project(project_name, self.models, channel_count, ip_address, tag_name)
                if success:
                    msg = show_message_box("Success", "Project created successfully!", QMessageBox.Information)
                    msg.exec_()
                    logging.info(f"Created new project: {project_name} with {len(self.models)} models")
                    logging.debug(f"Calling load_project for project: {project_name}")
                    self.parent.load_project(project_name)
                else:
                    msg = show_message_box("Error", message, QMessageBox.Warning)
                    msg.exec_()
                    return
            
            # Send sensitivity values via MQTT if IP address and tag name are provided
            if ip_address and tag_name and hasattr(self.parent, 'mqtt_handler') and self.parent.mqtt_handler:
                try:
                    # Extract sensitivity values from all channels
                    sensitivity_values = []
                    for model in self.models:
                        for channel in model.get("channels", []):
                            sensitivity = channel.get("sensitivity", "").strip()
                            if sensitivity:
                                try:
                                    # Convert to float if possible, otherwise keep as string
                                    sensitivity_values.append(float(sensitivity))
                                except ValueError:
                                    sensitivity_values.append(sensitivity)
                    
                    if sensitivity_values:
                        mqtt_success, mqtt_message = self.parent.mqtt_handler.send_sensitivity_values(
                            ip_address, tag_name, sensitivity_values
                        )
                        if mqtt_success:
                            logging.info(f"Sensitivity values sent via MQTT: {sensitivity_values}")
                        else:
                            logging.warning(f"Failed to send sensitivity values via MQTT: {mqtt_message}")
                    else:
                        logging.warning("No sensitivity values found to send via MQTT")
                        
                except Exception as e:
                    logging.error(f"Error sending sensitivity values via MQTT: {str(e)}")
                    
        except Exception as e:
            logging.error(f"Error submitting project: {str(e)}")
            msg = show_message_box("Error", f"Failed to submit project: {str(e)}", QMessageBox.Warning)
            msg.exec_()

    def back_to_select(self):
        logging.debug("Returning to project selection UI")
        self.parent.display_select_project()    