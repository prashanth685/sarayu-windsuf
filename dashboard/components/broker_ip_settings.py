from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import pyqtSignal, Qt
import json
import os

class BrokerIPDialog(QDialog):
    settings_updated = pyqtSignal(str, int)  # Signal when settings are updated (host, port)
    
    def __init__(self, parent=None, current_host="", current_port=1883):
        super().__init__(parent)
        self.setWindowTitle("MQTT Broker Settings")
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumWidth(350)
        
        layout = QVBoxLayout()
        
        # IP Address
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel("Broker IP:"))
        self.ip_edit = QLineEdit(current_host)
        self.ip_edit.setPlaceholderText("e.g., 192.168.1.231")
        ip_layout.addWidget(self.ip_edit)
        
        # Port
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.port_edit = QLineEdit(str(current_port))
        self.port_edit.setPlaceholderText("e.g., 1883")
        port_layout.addWidget(self.port_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        # Add layouts to main layout
        layout.addLayout(ip_layout)
        layout.addLayout(port_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Connect signals
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn.clicked.connect(self.reject)
    
    def save_settings(self):
        """Validate and save the broker settings."""
        host = self.ip_edit.text().strip()
        port_str = self.port_edit.text().strip()
        
        # Basic validation
        if not host:
            QMessageBox.warning(self, "Validation Error", "Broker IP cannot be empty")
            return
            
        try:
            port = int(port_str)
            if not (0 < port <= 65535):
                raise ValueError("Port out of range")
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Port must be a number between 1 and 65535")
            return
        
        # Save to settings file
        settings = {
            "broker_host": host,
            "broker_port": port
        }
        
        try:
            config_dir = os.path.join(os.path.expanduser("~"), ".sarayu")
            os.makedirs(config_dir, exist_ok=True)
            settings_file = os.path.join(config_dir, "mqtt_settings.json")
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
                
            self.settings_updated.emit(host, port)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

    @staticmethod
    def load_settings():
        """Load saved broker settings."""
        try:
            settings_file = os.path.join(os.path.expanduser("~"), ".sarayu", "mqtt_settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get("broker_host", ""), settings.get("broker_port", 1883)
        except Exception:
            pass
        return "", 1883  # Default values
