from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QPushButton, 
                            QMessageBox, QMdiSubWindow, QLabel, QLineEdit, QDoubleSpinBox, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
import logging
import json
from datetime import datetime

# Set style for message boxes
message_box_style = """
    QMessageBox {
        background-color: #000000;
        color: #ffffff;
    }
    QMessageBox QLabel {
        color: #ffffff;
    }
    QMessageBox QPushButton {
        background-color: #000000;
        color: #ffffff;
        border: 1px solid #5a5a5a;
        padding: 5px 15px;
        border-radius: 3px;
    }
    QMessageBox QPushButton:hover {
        background-color: #4a4a4a;
    }
    QMessageBox QPushButton:pressed {
        background-color: #2a2a2a;
    }
"""

# The style will be applied when DCSettingsWindow is initialized

class DCSettingsWindow(QMdiSubWindow):
    """
    A subwindow for displaying and editing DC settings for channels.
    """
    # Signal emitted when the window is closed
    closed = pyqtSignal()
    def __init__(self, parent=None, channel_count=4, mqtt_handler=None):
        super().__init__(parent)
        self.setWindowTitle("DC Calibration")
        self.channel_count = channel_count
        self.mqtt_handler = mqtt_handler
        self.setMinimumSize(900, 650)
        
        # Apply the style to all QMessageBox instances
        app = QApplication.instance()
        if app:
            app.setStyleSheet(app.styleSheet() + message_box_style)
        
        # Set the style for message boxes in this window
        self.setStyleSheet(self.styleSheet() + message_box_style)
        
        # Create main widget and layout
        self.main_widget = QWidget()
        self.setWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        
        # Add title
        title = QLabel("DC Calibration")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px 0;")
        self.layout.addWidget(title, alignment=Qt.AlignCenter)
        
        # Add description
        description = QLabel("Enter actual DC values and click 'Send' to calibrate")
        description.setStyleSheet("font-size: 16px; color: #666; margin-bottom: 25px;")
        self.layout.addWidget(description, alignment=Qt.AlignCenter)
        
        # Create table
        self.create_table()
        
        # Add buttons
        self.button_layout = QHBoxLayout()
        
        # Style for buttons
        button_style = """
            QPushButton {
                padding: 10px 24px;
                font-size: 14px;
                border: none;
                border-radius: 4px;
                min-width: 120px;
                margin: 0 5px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton:pressed {
                padding-top: 11px;
                padding-bottom: 9px;
            }
        """
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #f0ad4e;
                color: white;
            }
            QPushButton:hover {
                background-color: #ec971f;
            }
        """)
        self.reset_button.clicked.connect(self.reset_values)
        self.button_layout.addWidget(self.reset_button)
        
        self.button_layout.addStretch()
        
        # Add Calculate button
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #5bc0de;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #46b8da;
            }
        """)
        self.calculate_button.clicked.connect(self.calculate_ratio)
        self.button_layout.addWidget(self.calculate_button)
        
        self.send_button = QPushButton("Send Calibration")
        self.send_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #5cb85c;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4cae4c;
            }
        """)
        self.send_button.clicked.connect(self.send_calibration)
        self.button_layout.addWidget(self.send_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.close_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.close_button)
        
        self.layout.addLayout(self.button_layout)
        
        # Load initial values
        # self.load_initial_values()
        
        # Set window flags to make it a proper subwindow
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | 
                           Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
    
    def create_table(self):
        """Create and configure the table widget."""
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # Channel, Measured DC, Actual DC, Ratio
        self.table.setHorizontalHeaderLabels(["Channel", "Measured DC (V)", "Actual DC (V)", "Calibration Factor"])
        
        # Set row count based on channel count
        self.table.setRowCount(self.channel_count)
        
        # Set column widths
        self.table.setColumnWidth(0, 150)  # Increased from 100
        self.table.setColumnWidth(1, 200)  # Increased from 150
        self.table.setColumnWidth(2, 200)  # Increased from 150
        self.table.setColumnWidth(3, 200)  # Increased from 150
        
        # Populate channel numbers
        for i in range(self.channel_count):
            # Channel number
            channel_item = QTableWidgetItem(f"Channel {i+1}")
            channel_item.setFlags(channel_item.flags() & ~Qt.ItemIsEditable)
            channel_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, channel_item)
            
            # Measured DC (read-only)
            measured_item = QTableWidgetItem("0.000")
            measured_item.setFlags(measured_item.flags() & ~Qt.ItemIsEditable)
            measured_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 1, measured_item)
            
            # Actual DC (editable spinbox)
            actual_widget = QWidget()
            actual_layout = QHBoxLayout(actual_widget)
            actual_layout.setContentsMargins(5, 2, 5, 2)  # Reduced margins for better fit
            actual_spinbox = QDoubleSpinBox()
            actual_spinbox.setRange(-1000.0, 1000.0)
            actual_spinbox.setDecimals(3)
            actual_spinbox.setValue(0.0)
            actual_spinbox.setSingleStep(0.1)
            actual_spinbox.setButtonSymbols(QDoubleSpinBox.UpDownArrows)
            actual_spinbox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            actual_spinbox.setStyleSheet("""
                QDoubleSpinBox {
                    padding: 5px 8px;
                    font-size: 14px;
                    min-width: 120px;
                    max-width: 180px;
                    height: 30px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    background: white;
                }
                QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                    width: 20px;
                    border-left: 1px solid #ddd;
                }
                QDoubleSpinBox::up-button {
                    subcontrol-position: right top;
                    subcontrol-origin: border;
                    height: 14px;
                }
                QDoubleSpinBox::down-button {
                    subcontrol-position: right bottom;
                    subcontrol-origin: border;
                    height: 14px;
                }
                QDoubleSpinBox::up-arrow, QDoubleSpinBox::down-arrow {
                    width: 8px;
                    height: 8px;
                }
            """)
            # Remove the automatic calculation on value change
            # actual_spinbox.valueChanged.connect(self.calculate_ratio)
            actual_layout.addWidget(actual_spinbox)
            actual_layout.setContentsMargins(15, 0, 15, 0)  # Add horizontal padding
            actual_layout.setSpacing(0)
            actual_widget.setLayout(actual_layout)
            self.table.setCellWidget(i, 2, actual_widget)
            
            # Ratio (read-only)
            ratio_item = QTableWidgetItem("1.000")
            ratio_item.setFlags(ratio_item.flags() & ~Qt.ItemIsEditable)
            ratio_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 3, ratio_item)
        
        # Configure table properties
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(50)  # Increased row height
        self.table.setAlternatingRowColors(True)
        
        # Apply table styles
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
                gridline-color: #e0e0e0;
                selection-background-color: #e6f2ff;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 8px;
                border: 1px solid #d0d0d0;
                font-size: 14px;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QDoubleSpinBox {
                padding: 6px;
                font-size: 14px;
                min-width: 120px;
            }
        """)
        
        self.layout.addWidget(self.table)
    
    def calculate_ratio(self, force_update=False):
        """
        Calculate the calibration ratio (Actual/Measured) and update the table.
        
        Args:
            force_update: If True, will update the ratio column. If False, will only calculate without updating.
        """
        for i in range(self.channel_count):
            measured_text = self.table.item(i, 1).text()
            try:
                measured = float(measured_text)
                actual = self.table.cellWidget(i, 2).findChild(QDoubleSpinBox).value()
                
                # Avoid division by zero
                if abs(measured) > 1e-9:  # Small threshold to avoid division by very small numbers
                    ratio = actual / measured
                else:
                    ratio = 1.0 if actual == 0 else float('inf')
                
                # Only update the ratio column if force_update is True
                if force_update:
                    ratio_item = self.table.item(i, 3)
                    if abs(ratio) < 1000:  # Prevent display of very large numbers
                        ratio_item.setText(f"{ratio:.6f}")
                    else:
                        ratio_item.setText("N/A")
                
                return ratio
                
            except (ValueError, AttributeError) as e:
                logging.error(f"Error calculating ratio: {e}")
                return None
    
    def reset_values(self):
        """Reset all input fields to zero and send reset command via MQTT."""
        # Reset UI values
        for i in range(self.channel_count):
            spinbox = self.table.cellWidget(i, 2).findChild(QDoubleSpinBox)
            if spinbox:
                spinbox.setValue(0.0)
            self.table.item(i, 3).setText("1.000")
        
        # Send reset command via MQTT
        if self.mqtt_handler:
            try:
                # Create a reset command payload
                reset_payload = "$ResetCalibrationData#"  # Reset all channels to 1.0
                self.mqtt_handler.publish("dccalibrated/data", reset_payload)
                QMessageBox.information(self, "Success", "Calibration reset command sent successfully!")
            except Exception as e:
                logging.error(f"Error sending reset command: {e}")
                QMessageBox.critical(self, "Error", f"Failed to send reset command: {e}")
        else:
            QMessageBox.warning(self, "Error", "MQTT handler not available")
    
    def send_calibration(self):
        """Send calibration data via MQTT."""
        if not self.mqtt_handler:
            QMessageBox.warning(self, "Error", "MQTT handler not available")
            return
        
        try:
            # Create a list to store ratio values
            ratio_values = []
            
            for i in range(self.channel_count):
                # Get the ratio value from the table
                ratio_text = self.table.item(i, 3).text()
                ratio = float(ratio_text) if ratio_text != "N/A" else 1.0
                ratio_values.append(ratio)
            
            # Create a simple dictionary with just the ratio values
            # payload = "$DC_CalibratedData:" + ", ".join(map(str, ratio_values)) + "#"
            payload = "$DC_CalibratedData:" + ",".join(map(str, ratio_values)) + "#"



            
            # Convert to JSON and publish
            self.mqtt_handler.publish("dccalibrated/data", payload)
            
            QMessageBox.information(self, "Success", "Calibration ratios sent successfully!")
            
        except Exception as e:
            logging.error(f"Error sending calibration data: {e}")
            QMessageBox.critical(self, "Error", f"Failed to send calibration data: {e}")
            
            QMessageBox.information(self, "Success", "Calibration data sent successfully!")
            
        except Exception as e:
            logging.error(f"Error sending calibration data: {e}")
            QMessageBox.critical(self, "Error", f"Failed to send calibration data: {e}")
    
    def update_measured_dc_values(self, dc_values):
        """Update the measured DC values in the table.
        
        Args:
            dc_values (list): List of DC values to display (up to channel_count values)
        """
        if not dc_values or not isinstance(dc_values, list):
            return
            
        try:
            for i, value in enumerate(dc_values[:self.channel_count]):
                try:
                    # Update measured DC value
                    measured_item = self.table.item(i, 1)
                    if measured_item:
                        measured_item.setText(f"{float(value):.3f}")
                    
                    # If actual DC is not set, initialize it with the measured value
                    spinbox = self.table.cellWidget(i, 2).findChild(QDoubleSpinBox)
                    if spinbox and abs(spinbox.value()) < 1e-9:  # Check if close to zero
                        spinbox.setValue(float(value))
                    
                    # Recalculate ratio
                    self.calculate_ratio()
                    
                except (ValueError, AttributeError) as e:
                    logging.error(f"Error updating DC value for channel {i+1}: {e}")
                    
        except Exception as e:
            logging.error(f"Error in update_measured_dc_values: {e}")
            QMessageBox.warning(self, "Error", f"Failed to update DC values: {e}")
    
    def save_settings(self):
        """Save the DC settings."""
        try:
            # TODO: Implement actual saving logic
            # For now, just show a success message
            QMessageBox.information(self, "Success", "DC settings saved successfully!")
        except Exception as e:
            logging.error(f"Error saving DC settings: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to save DC settings: {str(e)}")
    
    def get_dc_values(self):
        """Get the current DC values from the table."""
        values = {}
        for i in range(self.channel_count):
            channel = i + 1
            try:
                measured = (self.table.item(i, 1).text())
                actual = (self.table.item(i, 2).text())
                values[channel] = {"measured": measured, "actual": actual}
            except (ValueError, AttributeError) as e:
                logging.error(f"Error reading DC values for channel {channel}: {str(e)}")
        return values
    
    def set_measured_dc(self, channel, value):
        """Set the measured DC value for a channel."""
        if 1 <= channel <= self.channel_count:
            item = self.table.item(channel - 1, 1)
            if item:
                item.setText(f"{value:.3f}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        try:
            # Emit the closed signal before closing
            self.closed.emit()
            super().closeEvent(event)
        except Exception as e:
            logging.error(f"Error during closeEvent: {str(e)}")
            super().closeEvent(event)
