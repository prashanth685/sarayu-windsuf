from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, 
                            QPushButton, QLabel, QMessageBox, QScrollArea, QComboBox, 
                            QApplication, QTableWidget, QTableWidgetItem, QHeaderView,
                            QTabWidget, QSpinBox, QDoubleSpinBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
import sys
import datetime
import logging

app = QApplication.instance()
if app:
    # Global stylesheet for QMessageBox, QComboBox, and Scrollbars
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
    
    /* Global Modern Scrollbars */
    QScrollBar:vertical {
        background: #f8fafc;
        width: 10px;
        border-radius: 5px;
        margin: 0px;
    }
    
    QScrollBar::handle:vertical {
        background: #7ea4a6;
        min-height: 20px;
        border-radius: 5px;
        border: none;
    }
    
    QScrollBar::handle:vertical:hover {
        background: #6b9395;
    }
    
    QScrollBar::handle:vertical:pressed {
        background: #5a8284;
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
        background: #f8fafc;
        height: 10px;
        border-radius: 5px;
        margin: 0px;
    }
    
    QScrollBar::handle:horizontal {
        background: #7ea4a6;
        min-width: 20px;
        border-radius: 5px;
        border: none;
    }
    
    QScrollBar::handle:horizontal:hover {
        background: #6b9395;
    }
    
    QScrollBar::handle:horizontal:pressed {
        background: #5a8284;
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
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(main_layout)
        
        # Create single project card at top level
        self.create_project_card(main_layout)
        
        # Scroll area for model cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setAlignment(Qt.AlignTop)
        scroll_layout.setSpacing(30)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
        
        # Container for model cards
        self.model_container = QWidget()
        self.model_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
                padding: 10px;
            }
        """)
        self.model_layout = QVBoxLayout()
        self.model_layout.setSpacing(25)
        self.model_layout.setContentsMargins(15, 15, 15, 15)
        self.model_container.setLayout(self.model_layout)
        scroll_layout.addWidget(self.model_container)
        
        self.model_inputs = []
        
        # Pre-populate models if in edit mode
        if self.edit_mode and self.existing_models:
            for model in self.existing_models:
                self.add_model_input(model)
        
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
                padding: 4px 4px;
                font-size: 14px;
                background-color: #ffffff;
                color: #000000;
                min-height: 24px;
                max-height: 24px;
                margin: 2px;
                text-align: center;
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
                padding: 2px;
                text-align: center;
            }
            QComboBox QAbstractItemView::item {
                padding: 4px 8px;
                min-height: 18px;
                color: #000000;
                text-align: center;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #3b82f6;
                color: #ffffff;
            }
        """

    
    def create_project_card(self, parent_layout):
        """Create the main project configuration card"""
        # Main project card container
        project_card = QFrame()
        project_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #4a90e2;
                border-radius: 12px;
                padding: 25px;
                margin: 15px;
            }
        """)
        project_card.setMinimumHeight(160)
        project_card.setMaximumHeight(160)
        
        card_layout = QHBoxLayout(project_card)
        card_layout.setSpacing(40)
        
        # Project Name Section
        name_section = QVBoxLayout()
        name_section.setSpacing(10)
        
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Enter project name")
        if self.edit_mode and self.existing_project_name:
            self.project_name_input.setText(self.existing_project_name)
        self.project_name_input.setStyleSheet("""
            QLineEdit {
                border: 3px solid #d1d5db;
                border-radius: 10px;
                padding: 18px;
                font-size: 18px;
                font-weight: 500;
                background-color: #ffffff;
                min-width: 320px;
                min-height: 25px;
                color: #1a202c;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                outline: none;
                border-width: 4px;
            }
            QLineEdit:hover {
                border-color: #93c5fd;
                border-width: 3px;
            }
            QLineEdit::placeholder {
                color: #6b7280;
                font-weight: 500;
            }
        """)
        name_section.addWidget(self.project_name_input)
        card_layout.addLayout(name_section)
        
        # Channel Count Section
        channel_section = QVBoxLayout()
        channel_section.setSpacing(10)
        
        self.channel_count_combo = QComboBox()
        self.channel_count_combo.addItems(self.available_channel_counts)
        if self.edit_mode and self.existing_channel_count:
            self.channel_count_combo.setCurrentText(self.existing_channel_count)
        self.channel_count_combo.setStyleSheet("""
            QComboBox {
                border: 3px solid #d1d5db;
                border-radius: 10px;
                padding: 18px;
                font-size: 18px;
                font-weight: 500;
                background-color: #ffffff;
                color: #1a202c;
                min-width: 200px;
                min-height: 25px;
            }
            QComboBox:focus {
                border-color: #3b82f6;
                outline: none;
                border-width: 4px;
            }
            QComboBox:hover {
                border-color: #93c5fd;
                border-width: 3px;
            }
            QComboBox::drop-down {
                border: none;
                width: 40px;
                padding-right: 15px;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 10px solid transparent;
                border-right: 10px solid transparent;
                border-top: 10px solid #374151;
                margin-right: 15px;
            }
            QComboBox QAbstractItemView {
                border: 3px solid #d1d5db;
                background-color: #ffffff;
                color: #1a202c;
                selection-background-color: #3b82f6;
                selection-color: #ffffff;
                padding: 12px;
                border-radius: 8px;
            }
            QComboBox QAbstractItemView::item {
                padding: 15px 20px;
                min-height: 35px;
                color: #1a202c;
                font-size: 17px;
                font-weight: 500;
                border-radius: 6px;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #3b82f6;
                color: #ffffff;
            }
        """)
        self.channel_count_combo.currentTextChanged.connect(self.update_table)
        channel_section.addWidget(self.channel_count_combo)
        card_layout.addLayout(channel_section)
        
        # Add Model Button
        add_model_button = QPushButton("+ Add Model")
        add_model_button.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 18px 32px;
                font-size: 18px;
                font-weight: 700;
                min-width: 160px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        add_model_button.clicked.connect(self.add_model_input)
        card_layout.addWidget(add_model_button, alignment=Qt.AlignCenter)
        
        parent_layout.addWidget(project_card)

    def update_table(self, channel_count):
        for widget, model_name_input, tag_name_input, channel_inputs, _ in self.model_inputs:
            for table, num_channels in channel_inputs:
                model_layout = widget.layout()
                model_layout.removeWidget(table)
                table.deleteLater()

            num_channels = {"DAQ4CH": 4, "DAQ8CH": 8, "DAQ10CH": 10}.get(channel_count, 4)
            table = QTableWidget(num_channels, 12)
            table.setHorizontalHeaderLabels(["S.No.", "Channel Name", "Channel Type", "Sensitivity", "Unit", "Subunit", "Correction Factor", "Gain", "Unit Type", "Angle", "Direction", "Shaft"])
            
            # Apply header background color
            header = table.horizontalHeader()
            header.setStyleSheet("""
                QHeaderView::section {
                    background: #7ea4a6;
                    color: #ffffff;
                    font-size: 13px;
                    font-weight: 600;
                    border: none;
                    border-bottom: 2px solid #e2e8f0;
                    padding: 12px 20px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                QHeaderView::section:hover {
                    background: #7ea4a6;
                }
            """)

            table.setStyleSheet("""
            /* Modern Table Styling */
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                font-size: 14px;
                gridline-color: #f1f5f9;
                selection-background-color: #f0f9ff;
                selection-color: #0f172a;
                alternate-background-color: #fafbfc;
                outline: none;
            }

            /* Table Cells */
            QTableWidget::item {
                border: none;
                border-bottom: 1px solid #f1f5f9;
                color: #1e293b;
                font-size: 14px;
                padding: 8px 4px;
                background-color: transparent;
                text-align: center;
            }

            QTableWidget::item:selected {
                background-color: #f0f9ff;
                color: #0f172a;
            }

            QTableWidget::item:hover {
                background-color: #f8fafc;
            }

            /* Center align combo boxes in table cells */
            QTableWidget QWidget {
                text-align: center;
            }

            /* Modern Header */
            QHeaderView::section {
                background: #7ea4a6;
                color: #ffffff;
                font-size: 13px;
                font-weight: 600;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                padding: 12px 20px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            QHeaderView::section:hover {
                background: #7ea4a6;
            }

            /* Modern Input Fields */
            QTableWidget QLineEdit {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 14px;
                color: #1e293b;
            }
            
            QTableWidget QLineEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
            
            QTableWidget QLineEdit:hover {
                border-color: #cbd5e1;
            }
            
            /* Modern ComboBox */
            QTableWidget QComboBox {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                font-size: 14px;
                color: #1e293b;
                min-width: 60px;
                min-height: 20px;
                max-height: 20px;
                margin: 1px;
                text-align: center;
            }
            
            QTableWidget QComboBox:focus {
                border-color: #3b82f6;
                outline: none;
            }
            
            QTableWidget QComboBox:hover {
                border-color: #cbd5e1;
            }
            
            QTableWidget QComboBox::drop-down {
                border: none;
                width: 16px;
            }
            
            QTableWidget QComboBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 4px solid #64748b;
            }
            
            QTableWidget QComboBox QAbstractItemView {
                text-align: center;
            }
            
            QTableWidget QComboBox QAbstractItemView::item {
                text-align: center;
                padding: 2px 4px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 4px;
                selection-background-color: #f0f9ff;
                selection-color: #0f172a;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                border-radius: 4px;
                color: #1e293b;
                font-size: 14px;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #3b82f6;
                color: #ffffff;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #f1f5f9;
            }
            
            /* Modern Scrollbars */
            QScrollBar:vertical {
                background: #f8fafc;
                width: 10px;
                border-radius: 5px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: #7ea4a6;
                min-height: 20px;
                border-radius: 5px;
                border: none;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #6b9395;
            }
            
            QScrollBar::handle:vertical:pressed {
                background: #5a8284;
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
                background: #f8fafc;
                height: 10px;
                border-radius: 5px;
                margin: 0px;
            }
            
            QScrollBar::handle:horizontal {
                background: #7ea4a6;
                min-width: 20px;
                border-radius: 5px;
                border: none;
            }
            
            QScrollBar::handle:horizontal:hover {
                background: #6b9395;
            }
            
            QScrollBar::handle:horizontal:pressed {
                background: #5a8284;
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
            table.horizontalHeader().setVisible(True)
            table.horizontalHeader().setStretchLastSection(True)
            table.horizontalHeader().setMinimumHeight(48)
            table.horizontalHeader().setDefaultSectionSize(120)
            table.verticalHeader().setVisible(False)
            table.setAlternatingRowColors(True)
            table.setEditTriggers(QTableWidget.AllEditTriggers)
            table.verticalHeader().setDefaultSectionSize(80)
            table.setMinimumHeight(table.verticalHeader().defaultSectionSize() * num_channels + table.horizontalHeader().height() + 40)
            table.setMaximumHeight(table.verticalHeader().defaultSectionSize() * num_channels + table.horizontalHeader().height() + 40)
            table.setMinimumWidth(1400)
            table.resizeColumnsToContents()
            
            # Set specific column widths for better layout - increased for better usability
            header = table.horizontalHeader()
            header.resizeSection(0, 60)   # S.No.
            header.resizeSection(1, 250)  # Channel Name - increased from 150
            header.resizeSection(2, 160)  # Channel Type - increased from 120
            header.resizeSection(3, 150)  # Sensitivity - increased from 100
            header.resizeSection(4, 110)  # Unit - increased from 80
            header.resizeSection(5, 110)  # Subunit - increased from 80
            header.resizeSection(6, 160)  # Correction Factor - increased from 120
            header.resizeSection(7, 110)  # Gain - increased from 80
            header.resizeSection(8, 140)  # Unit Type - increased from 100
            header.resizeSection(9, 100)  # Angle - increased from 80
            header.resizeSection(10, 140) # Direction - increased from 100
            header.resizeSection(11, 100)  # Shaft - increased from 80

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

        # Create collapsible model card
        model_card = QFrame()
        model_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                margin: 15px;
            }
        """)
        
        model_main_layout = QVBoxLayout(model_card)
        model_main_layout.setContentsMargins(25, 20, 25, 20)
        model_main_layout.setSpacing(20)
        
        # Header with collapse/expand and remove buttons
        header_layout = QHBoxLayout()
        header_layout.setSpacing(20)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        # Collapse/Expand button
        collapse_button = QPushButton("▶")
        collapse_button.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 600;
                min-width: 40px;
                max-width: 40px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        collapse_button.setCheckable(True)
        collapse_button.setChecked(True)
        
        # Model title (editable)
        model_title_input = QLineEdit()
        model_title_input.setText(f"Model {len(self.model_inputs) + 1}")
        model_title_input.setStyleSheet("""
            QLineEdit {
                font-size: 18px;
                font-weight: 600;
                color: #1a202c;
                background: transparent;
                border: 2px solid transparent;
                border-radius: 6px;
                padding: 5px 10px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background-color: rgba(255, 255, 255, 0.9);
            }
        """)
        model_title_input.setReadOnly(False)
        
        # Remove button
        remove_button = QPushButton("✕")
        remove_button.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 600;
                min-width: 40px;
                max-width: 40px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        
        header_layout.addWidget(collapse_button)
        header_layout.addWidget(model_title_input)
        header_layout.addStretch()
        header_layout.addWidget(remove_button)
        model_main_layout.addLayout(header_layout)
        
        # Content container (collapsible)
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #f9fafb;
                border-radius: 8px;
                padding: 5px;
                margin: 5px 0px;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(5)
        content_layout.setContentsMargins(5, 5, 5, 5)
        
        # No model form fields - only tabs with table
        
        # Create tab widget for this model
        model_tabs = QTabWidget()
        model_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background-color: white;
                padding: 5px;
            }
            QTabBar::tab {
                background-color: #f3f4f6;
                border: 1px solid #d1d5db;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                padding: 8px 16px;
                margin-right: 2px;
                font-size: 14px;
                font-weight: 500;
                width:100%
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
                color: #3b82f6;
            }
            QTabBar::tab:hover {
                background-color: #e5e7eb;
            }
        """)
        
        # Create tabs for this model
        model_general_tab = QWidget()
        model_advanced_tab = QWidget()
        model_channel_settings_tab = QWidget()
        
        model_tabs.addTab(model_general_tab, "General")
        model_tabs.addTab(model_advanced_tab, "Advanced")
        model_tabs.addTab(model_channel_settings_tab, "I/O")
        
        # Initialize model tabs
        self.init_model_general_tab(model_general_tab, existing_model, num_channels)
        self.init_model_advanced_tab(model_advanced_tab, existing_model)
        self.init_model_channel_settings_tab(model_channel_settings_tab, existing_model)
        
        content_layout.addWidget(model_tabs)
        model_main_layout.addWidget(content_widget)
        
        # Initially hide the content widget (collapsed state)
        content_widget.hide()
        
        # Connect collapse functionality
        collapse_button.toggled.connect(lambda checked: self.toggle_model_content(content_widget, collapse_button))
        remove_button.clicked.connect(lambda: self.remove_model_input(model_card))
        
        # Add to model container
        self.model_layout.addWidget(model_card)
        
        # Store model data
        self.model_inputs.append((model_card, model_title_input, None, model_tabs, channel_count))
        
        # Update model numbering
        self.update_model_numbers()
    
    def init_model_general_tab(self, tab_widget, existing_model, num_channels):
        """Initialize the General tab for a specific model"""
        layout = QVBoxLayout(tab_widget)
        layout.setAlignment(Qt.AlignTop)
        # layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create channel table directly without title
        table = self.create_channel_table(num_channels, existing_model)
        layout.addWidget(table)
        
        # Store table reference for this model
        if hasattr(self, 'model_tables'):
            self.model_tables[len(self.model_inputs)] = table
        else:
            self.model_tables = {len(self.model_inputs): table}
    
    def init_model_advanced_tab(self, tab_widget, existing_model):
        """Initialize the Advanced tab for a specific model"""
        layout = QVBoxLayout(tab_widget)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Create form for advanced settings
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # Sampling Frequency
        sampling_freq = QDoubleSpinBox()
        sampling_freq.setRange(0.1, 10000.0)
        sampling_freq.setValue(1000.0)
        sampling_freq.setSuffix(" Hz")
        if existing_model and existing_model.get("samplingFrequency"):
            sampling_freq.setValue(float(existing_model["samplingFrequency"]))
        sampling_freq.setStyleSheet("""
            QDoubleSpinBox {
                min-width: 200px;
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
            }
        """)
        form_layout.addRow("Sampling Frequency:", sampling_freq)
        
        # Input Delta Time
        delta_time = QDoubleSpinBox()
        delta_time.setRange(0.001, 10.0)
        delta_time.setValue(0.1)
        delta_time.setSuffix(" s")
        if existing_model and existing_model.get("deltaTime"):
            delta_time.setValue(float(existing_model["deltaTime"]))
        delta_time.setStyleSheet("""
            QDoubleSpinBox {
                min-width: 200px;
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
            }
        """)
        form_layout.addRow("Input Delta Time:", delta_time)
        
        # Number of Data Points
        num_data_points = QSpinBox()
        num_data_points.setRange(100, 1000000)
        num_data_points.setValue(1000)
        if existing_model and existing_model.get("numDataPoints"):
            num_data_points.setValue(int(existing_model["numDataPoints"]))
        num_data_points.setStyleSheet("""
            QSpinBox {
                min-width: 200px;
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
            }
        """)
        form_layout.addRow("Number of Data Points:", num_data_points)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Store advanced settings for this model
        if hasattr(self, 'model_advanced_settings'):
            self.model_advanced_settings[len(self.model_inputs)] = {
                'sampling_freq': sampling_freq,
                'delta_time': delta_time,
                'num_data_points': num_data_points
            }
        else:
            self.model_advanced_settings = {
                len(self.model_inputs): {
                    'sampling_freq': sampling_freq,
                    'delta_time': delta_time,
                    'num_data_points': num_data_points
                }
            }
    
    def init_model_channel_settings_tab(self, tab_widget, existing_model):
        """Initialize the I/O tab for a specific model"""
        layout = QVBoxLayout(tab_widget)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Create form for I/O settings
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # Tag Name Input
        tag_name_input = QLineEdit()
        tag_name_input.setPlaceholderText("Enter tag name")
        if existing_model:
            tag_name_input.setText(existing_model.get("tagName", ""))
        tag_name_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                background-color: #ffffff;
                min-width: 300px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
        """)
        form_layout.addRow("Tag Name:", tag_name_input)
        
        # IP Address Input
        ip_address = QLineEdit()
        ip_address.setPlaceholderText("Enter IP Address")
        if existing_model and existing_model.get("ipAddress"):
            ip_address.setText(existing_model["ipAddress"])
        ip_address.setStyleSheet("""
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
        form_layout.addRow("IP Address:", ip_address)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Store I/O settings for this model
        if hasattr(self, 'model_io_settings'):
            self.model_io_settings[len(self.model_inputs)] = {
                'tag_name': tag_name_input,
                'ip_address': ip_address
            }
        else:
            self.model_io_settings = {
                len(self.model_inputs): {
                    'tag_name': tag_name_input,
                    'ip_address': ip_address
                }
            }
    
    def send_sensitivity_values_for_model(self, model_index, ip_address_input, tag_name_input):
        """Send sensitivity values for a specific model via MQTT"""
        try:
            import paho.mqtt.publish as publish
            
            # Get values from UI
            ip_address = ip_address_input.text().strip()
            tag_name = tag_name_input.text().strip()
            
            # Validate inputs
            if not ip_address:
                msg = show_message_box("Error", "Please enter an IP address", QMessageBox.Warning)
                msg.exec_()
                return
                
            if not tag_name:
                msg = show_message_box("Error", "Please enter a tag name", QMessageBox.Warning)
                msg.exec_()
                return
            
            # Get sensitivity values from the model's table
            sensitivity_values = []
            if hasattr(self, 'model_tables') and model_index in self.model_tables:
                table = self.model_tables[model_index]
                for row in range(table.rowCount()):
                    sensitivity_item = table.item(row, 3)
                    if sensitivity_item and sensitivity_item.text().strip():
                        try:
                            value = float(sensitivity_item.text().strip())
                            sensitivity_values.append(value)
                        except ValueError:
                            msg = show_message_box("Error", f"Invalid sensitivity value in row {row+1}. Please enter a valid number.", QMessageBox.Warning)
                            msg.exec_()
                            return
            
            if not sensitivity_values:
                msg = show_message_box("Error", "No sensitivity values found in the table.", QMessageBox.Warning)
                msg.exec_()
                return
            
            # Send MQTT message
            if hasattr(self, 'model_io_settings') and model_index in self.model_io_settings:
                send_btn = self.model_io_settings[model_index]['send_btn']
                send_btn.setEnabled(False)
                send_btn.setText("Sending...")
                QApplication.processEvents()  # Update UI
                
                try:
                    publish.single(
                        tag_name,
                        payload=str({"sensitivity": sensitivity_values}),
                        hostname=ip_address,
                        port=1883,
                        qos=1,
                        retain=False
                    )
                    msg = show_message_box("Success", 
                        f"Successfully sent {len(sensitivity_values)} sensitivity values to {tag_name}", QMessageBox.Information)
                    msg.exec_()
                except Exception as e:
                    msg = show_message_box("Error", 
                        f"Failed to send sensitivity values: {str(e)}\n\n"
                        f"Please check the IP address and MQTT broker status.", QMessageBox.Critical)
                    msg.exec_()
                finally:
                    send_btn.setEnabled(True)
                    send_btn.setText("Send Sensitivity Values")
                    
        except ImportError:
            msg = show_message_box("Error", 
                "MQTT client library not found. Please install it using: pip install paho-mqtt", QMessageBox.Critical)
            msg.exec_()
        except Exception as e:
            msg = show_message_box("Error", 
                f"An unexpected error occurred: {str(e)}", QMessageBox.Critical)
            msg.exec_()
            if hasattr(self, 'model_io_settings') and model_index in self.model_io_settings:
                send_btn = self.model_io_settings[model_index]['send_btn']
                send_btn.setEnabled(True)
                send_btn.setText("Send Sensitivity Values")
    
    def create_channel_table(self, num_channels, existing_model=None):
        table = QTableWidget(num_channels, 12)
        table.setHorizontalHeaderLabels(["S.No.", "Channel Name", "Channel Type", "Sensitivity", "Unit", "Subunit", "Correction Factor", "Gain", "Unit Type", "Angle", "Direction", "Shaft"])
        
        # Apply header background color
        header = table.horizontalHeader()
        header.setStyleSheet("""
            QHeaderView::section {
                background: #7ea4a6;
                color: #ffffff;
                font-size: 13px;
                font-weight: 600;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                padding: 12px 20px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QHeaderView::section:hover {
                background: #7ea4a6;
            }
        """)
        
        table.setStyleSheet("""
            /* Modern Table Styling */
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                font-size: 14px;
                gridline-color: #f1f5f9;
                selection-background-color: #f0f9ff;
                selection-color: #0f172a;
                alternate-background-color: #fafbfc;
                outline: none;
            }
            
            /* Table Cells */
            QTableWidget::item {
                border: none;
                border-bottom: 1px solid #f1f5f9;
                color: #1e293b;
                font-size: 14px;
                padding: 16px 20px;
                background-color: transparent;
            }
            
            QTableWidget::item:selected {
                background-color: #f0f9ff;
                color: #0f172a;
            }
            
            QTableWidget::item:hover {
                background-color: #f8fafc;
            }
            
            /* Modern Header */
            QHeaderView::section {
                background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%);
                color: #ffffff;
                font-size: 13px;
                font-weight: 600;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                padding: 12px 20px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            QHeaderView::section:hover {
                background: linear-gradient(135deg, #0c4a6e 0%, #164e63 100%);
            }
            
            /* Modern Input Fields */
            QTableWidget QLineEdit {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 14px;
                color: #1e293b;
            }
            
            QTableWidget QLineEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
            
            QTableWidget QLineEdit:hover {
                border-color: #cbd5e1;
            }
            
            /* Modern ComboBox */
            QTableWidget QComboBox {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 2px 4px;
                font-size: 14px;
                color: #1e293b;
                min-width: 70px;
                min-height: 20px;
                max-height: 20px;
                margin: 1px;
                text-align: center;
            }
            
            QTableWidget QComboBox:focus {
                border-color: #3b82f6;
                outline: none;
            }
            
            QTableWidget QComboBox:hover {
                border-color: #cbd5e1;
            }
            
            QTableWidget QComboBox::drop-down {
                border: none;
                width: 16px;
            }
            
            QTableWidget QComboBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 4px solid #64748b;
            }
            
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 4px;
                selection-background-color: #f0f9ff;
                selection-color: #0f172a;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                border-radius: 4px;
                color: #1e293b;
                font-size: 14px;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #3b82f6;
                color: #ffffff;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #f1f5f9;
            }
            
            /* Modern Scrollbars */
            QScrollBar:vertical {
                background: #f8fafc;
                width: 10px;
                border-radius: 5px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: #7ea4a6;
                min-height: 20px;
                border-radius: 5px;
                border: none;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #6b9395;
            }
            
            QScrollBar::handle:vertical:pressed {
                background: #5a8284;
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
                background: #f8fafc;
                height: 10px;
                border-radius: 5px;
                margin: 0px;
            }
            
            QScrollBar::handle:horizontal {
                background: #7ea4a6;
                min-width: 20px;
                border-radius: 5px;
                border: none;
            }
            
            QScrollBar::handle:horizontal:hover {
                background: #6b9395;
            }
            
            QScrollBar::handle:horizontal:pressed {
                background: #5a8284;
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
        table.horizontalHeader().setVisible(True)
        table.horizontalHeader().setStretchLastSection(False)
        table.horizontalHeader().setMinimumHeight(70)
        table.horizontalHeader().setDefaultSectionSize(140)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.AllEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.verticalHeader().setDefaultSectionSize(80)
        table.setMinimumHeight(table.verticalHeader().defaultSectionSize() * num_channels + table.horizontalHeader().height() + 50)
        table.setMaximumHeight(table.verticalHeader().defaultSectionSize() * num_channels + table.horizontalHeader().height() + 50)
        table.setMinimumWidth(1400)
        
        # Set specific column widths - increased for better usability
        header = table.horizontalHeader()
        header.resizeSection(0, 70)   # S.No.
        header.resizeSection(1, 250)  # Channel Name - increased from 180
        header.resizeSection(2, 160)  # Channel Type - increased from 140
        header.resizeSection(3, 150)  # Sensitivity - increased from 120
        header.resizeSection(4, 110)  # Unit - increased from 90
        header.resizeSection(5, 110)  # Subunit - increased from 90
        header.resizeSection(6, 160)  # Correction Factor - increased from 140
        header.resizeSection(7, 110)  # Gain - increased from 90
        header.resizeSection(8, 140)  # Unit Type - increased from 120
        header.resizeSection(9, 100)  # Angle - increased from 80
        header.resizeSection(10, 140) # Direction - increased from 120
        header.resizeSection(11, 100)  # Shaft - increased from 80
        
        # Populate table with existing data or defaults
        if existing_model and existing_model.get("channels"):
            for row, channel in enumerate(existing_model["channels"]):
                if row >= num_channels:
                    break
                self.populate_channel_row(table, row, channel)
        else:
            for row in range(num_channels):
                self.populate_channel_row(table, row)
        
        return table
    
    def populate_channel_row(self, table, row, channel_data=None):
        """Populate a single row in the channel table"""
        # S.No.
        item = QTableWidgetItem(str(row + 1))
        item.setTextAlignment(Qt.AlignCenter)
        table.setItem(row, 0, item)
        
        # Channel Name
        table.setItem(row, 1, QTableWidgetItem(channel_data.get("channelName", f"CH{row + 1}") if channel_data else f"CH{row + 1}"))
        
        # Channel Type
        type_combo = QComboBox()
        type_combo.addItems(self.available_types)
        type_combo.setCurrentText(channel_data.get("type", "Displacement") if channel_data else "Displacement")
        type_combo.setStyleSheet(self.get_combo_box_style())
        type_combo.currentIndexChanged.connect(lambda _, r=row: self.update_unit_combo(table, r))
        table.setCellWidget(row, 2, type_combo)
        
        # Sensitivity
        table.setItem(row, 3, QTableWidgetItem(channel_data.get("sensitivity", "0.007874") if channel_data else "0.007874"))
        
        # Unit
        unit_combo = QComboBox()
        current_type = type_combo.currentText()
        unit_items = self.available_units_displacement if current_type == "Displacement" else self.available_units_accvel
        unit_combo.addItems(unit_items)
        unit_combo.setCurrentText(channel_data.get("unit", "um") if channel_data else "um")
        unit_combo.setStyleSheet(self.get_combo_box_style())
        unit_combo.currentTextChanged.connect(lambda text, r=row: self.update_unit_type_based_on_unit(table, r))
        table.setCellWidget(row, 4, unit_combo)

        # Subunit
        subunit_combo = QComboBox()
        subunit_combo.addItems(["pp", "pk", "rms"])
        if channel_data:
            sub_val = str(channel_data.get("subunit", "pp") or "pp").lower()
            subunit_combo.setCurrentText("pp" if sub_val in ("pp", "pk-pk", "peak to peak") else ("pk" if sub_val in ("pk", "peak") else "rms"))
        else:
            subunit_combo.setCurrentText("pp")
        subunit_combo.setStyleSheet(self.get_combo_box_style())
        table.setCellWidget(row, 5, subunit_combo)
        
        # Correction Factor
        table.setItem(row, 6, QTableWidgetItem(channel_data.get("correctionValue", "1") if channel_data else "1"))
        
        # Gain
        table.setItem(row, 7, QTableWidgetItem(channel_data.get("gain", "1") if channel_data else "1"))
        
        # Unit Type
        unit_type_combo = QComboBox()
        unit_type_combo.addItems(self.available_unit_types)
        if channel_data:
            existing_unit_type = channel_data.get("unitType")
            inferred_unit_type = "Volts" if str(channel_data.get("unit", "")).lower() == "v" else "Displacement"
            unit_type_combo.setCurrentText(existing_unit_type if existing_unit_type in self.available_unit_types else inferred_unit_type)
        else:
            unit_type_combo.setCurrentText("Displacement")
        unit_type_combo.setStyleSheet(self.get_combo_box_style())
        table.setCellWidget(row, 8, unit_type_combo)
        
        # Angle
        table.setItem(row, 9, QTableWidgetItem(channel_data.get("angle", "45") if channel_data else "45"))
        
        # Direction
        direction_combo = QComboBox()
        direction_combo.addItems(self.available_directions)
        # Direction - alternate between Right and Left
        default_direction = "Right" if row % 2 == 0 else "Left"
        direction_combo.setCurrentText(channel_data.get("angleDirection", default_direction) if channel_data else default_direction)
        direction_combo.setStyleSheet(self.get_combo_box_style())
        table.setCellWidget(row, 10, direction_combo)
        
        # Shaft
        table.setItem(row, 11, QTableWidgetItem(channel_data.get("shaft", "CCW") if channel_data else "CCW"))
    
    def toggle_model_content(self, content_widget, collapse_button):
        """Toggle visibility of model content and update button text"""
        if content_widget.isVisible():
            content_widget.hide()
            collapse_button.setText("▶")
        else:
            content_widget.show()
            collapse_button.setText("▼")
    
    def update_model_numbers(self):
        """Update model numbers after removal"""
        for i, (widget, model_title_input, _, _, _) in enumerate(self.model_inputs):
            # Only update if the user hasn't changed the default name
            current_text = model_title_input.text().strip()
            if current_text.startswith("Model "):
                try:
                    model_num = int(current_text.split(" ")[1])
                    if model_num != i + 1:
                        model_title_input.setText(f"Model {i + 1}")
                except (ValueError, IndexError):
                    model_title_input.setText(f"Model {i + 1}")
            else:
                # Keep user's custom name, just update numbering for new models
                pass

    def add_channel_to_table(self, table):
        current_rows = table.rowCount()
        table.setRowCount(current_rows + 1)
        item = QTableWidgetItem(str(current_rows + 1))
        item.setTextAlignment(Qt.AlignCenter)
        table.setItem(current_rows, 0, item)
        table.setItem(current_rows, 1, QTableWidgetItem(f"CH{current_rows + 1}"))
        
        type_combo = QComboBox()
        type_combo.addItems(self.available_types)
        type_combo.setCurrentText("Displacement")
        type_combo.setStyleSheet(self.get_combo_box_style())
        type_combo.currentIndexChanged.connect(lambda _, r=current_rows: self.update_unit_combo(table, r))
        table.setCellWidget(current_rows, 2, type_combo)
        
        table.setItem(current_rows, 3, QTableWidgetItem("0.007874"))
        
        unit_combo = QComboBox()
        unit_combo.addItems(self.available_units_displacement)
        unit_combo.setCurrentText("um")
        unit_combo.setStyleSheet(self.get_combo_box_style())
        unit_combo.currentTextChanged.connect(lambda text, r=current_rows: self.update_unit_type_based_on_unit(table, r))
        table.setCellWidget(current_rows, 4, unit_combo)

        subunit_combo = QComboBox()
        subunit_combo.addItems(["pp", "pk", "rms"])
        subunit_combo.setCurrentText("pp")
        subunit_combo.setStyleSheet(self.get_combo_box_style())
        table.setCellWidget(current_rows, 5, subunit_combo)
        
        table.setItem(current_rows, 6, QTableWidgetItem("1"))
        table.setItem(current_rows, 7, QTableWidgetItem("1"))
        unit_type_combo = QComboBox()
        unit_type_combo.addItems(self.available_unit_types)
        unit_type_combo.setCurrentText("Displacement")
        unit_type_combo.setStyleSheet(self.get_combo_box_style())
        table.setCellWidget(current_rows, 8, unit_type_combo)
        table.setItem(current_rows, 9, QTableWidgetItem("45"))
        
        direction_combo = QComboBox()
        direction_combo.addItems(self.available_directions)
        # Direction - alternate between Right and Left
        default_direction = "Right" if current_rows % 2 == 0 else "Left"
        direction_combo.setCurrentText(default_direction)
        direction_combo.setStyleSheet(self.get_combo_box_style())
        table.setCellWidget(current_rows, 10, direction_combo)
        
        table.setItem(current_rows, 11, QTableWidgetItem("CCW"))
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

    def remove_model_input(self, model_card):
        """Remove a model card and update numbering"""
        if len(self.model_inputs) > 1 or not self.edit_mode:
            # Find and remove the model input data
            for i, inputs in enumerate(self.model_inputs):
                if inputs[0] == model_card:
                    self.model_inputs.remove(inputs)
                    break
            
            # Remove the widget from layout
            self.model_layout.removeWidget(model_card)
            model_card.deleteLater()
            
            # Update model numbering
            self.update_model_numbers()

    def submit_project(self):
        project_name = self.project_name_input.text().strip()
        channel_count = self.channel_count_combo.currentText()
        
        if not project_name:
            msg = show_message_box("Error", "Project name cannot be empty!", QMessageBox.Warning)
            msg.exec_()
            return

        if not self.model_inputs:
            msg = show_message_box("Error", "At least one model is required!", QMessageBox.Warning)
            msg.exec_()
            return

        self.models = []
        for i, (widget, model_title_input, _, model_tabs, channel_count) in enumerate(self.model_inputs):
            # Get model name from I/O tab or title input
            model_name = ""
            tag_name = ""
            
            # Try to get values from I/O tab
            if hasattr(self, 'model_io_settings') and i in self.model_io_settings:
                io_settings = self.model_io_settings[i]
                if 'tag_name' in io_settings:
                    tag_name = io_settings['tag_name'].text().strip()
            
            # Fallback to title input if I/O tab values are empty
            if not model_name:
                model_name = model_title_input.text().strip()
            
            if not model_name:
                msg = show_message_box("Error", f"Model name cannot be empty for model {i + 1}!", QMessageBox.Warning)
                msg.exec_()
                return

            # Get channels from the model's table
            channels = []
            if hasattr(self, 'model_tables') and i in self.model_tables:
                table = self.model_tables[i]
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

            # Get advanced settings if available
            advanced_settings = {}
            if hasattr(self, 'model_advanced_settings') and i in self.model_advanced_settings:
                settings = self.model_advanced_settings[i]
                advanced_settings = {
                    "samplingFrequency": settings['sampling_freq'].value(),
                    "deltaTime": settings['delta_time'].value(),
                    "numDataPoints": settings['num_data_points'].value()
                }

            # Get I/O settings if available
            io_settings_data = {}
            if hasattr(self, 'model_io_settings') and i in self.model_io_settings:
                settings = self.model_io_settings[i]
                io_settings_data = {
                    "ipAddress": settings['ip_address'].text().strip(),
                    "tagName": settings['tag_name'].text().strip()
                }

            self.models.append({
                "name": f"{channel_count}_{model_name}",
                "tagName": tag_name,
                "channels": channels,
                **advanced_settings,
                **io_settings_data
            })

        try:
            if self.edit_mode:
                self.project_edited.emit(project_name, self.models, channel_count, "", "")
            else:
                success, message = self.db.create_project(project_name, self.models, channel_count, "", "")
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
                    
        except Exception as e:
            logging.error(f"Error submitting project: {str(e)}")
            msg = show_message_box("Error", f"Failed to submit project: {str(e)}", QMessageBox.Warning)
            msg.exec_()

    def back_to_select(self):
        logging.debug("Returning to previous UI")
        if self.edit_mode and self.existing_project_name:
            # If in edit mode, return to the dashboard with the project loaded
            self.parent.load_project(self.existing_project_name)
        else:
            # If in create mode, return to project selection
            self.parent.display_select_project()    