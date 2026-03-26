#!/usr/bin/env python3
"""
Test script to verify the edit dialog optimization
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import time
import logging

# Mock database for testing
class MockDB:
    def __init__(self):
        self.projects = {
            "test_project": {
                "models": [
                    {
                        "name": "Model 1",
                        "channels": [
                            {"channelName": "CH1", "type": "Displacement", "sensitivity": "0.007874", "unit": "um"},
                            {"channelName": "CH2", "type": "Acceleration", "sensitivity": "0.1", "unit": "g"},
                            {"channelName": "CH3", "type": "Velocity", "sensitivity": "0.02", "unit": "mm/s"},
                            {"channelName": "CH4", "type": "Generic Input", "sensitivity": "1.0", "unit": "v"}
                        ]
                    },
                    {
                        "name": "Model 2",
                        "channels": [
                            {"channelName": "CH1", "type": "Displacement", "sensitivity": "0.007874", "unit": "um"},
                            {"channelName": "CH2", "type": "Acceleration", "sensitivity": "0.1", "unit": "g"}
                        ]
                    },
                    {
                        "name": "Model 3",
                        "channels": [
                            {"channelName": "CH1", "type": "Displacement", "sensitivity": "0.007874", "unit": "um"}
                        ]
                    }
                ],
                "channel_count": "DAQ4CH",
                "ip_address": "192.168.1.100",
                "tag_name": "TEST_TAG"
            }
        }
    
    def get_project_data(self, project_name):
        return self.projects.get(project_name)
    
    def is_connected(self):
        return True
    
    def reconnect(self):
        pass

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Dialog Performance Test")
        self.setGeometry(100, 100, 400, 200)
        
        layout = QVBoxLayout()
        
        # Test button
        self.test_button = QPushButton("Test Edit Dialog (Optimized)")
        self.test_button.clicked.connect(self.test_edit_dialog)
        layout.addWidget(self.test_button)
        
        # Status label
        self.status_label = QLabel("Click button to test")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Mock dashboard
        self.db = MockDB()
        self.current_project = "test_project"
        self.main_section = MockMainSection()
        
    def test_edit_dialog(self):
        """Test the optimized edit dialog"""
        self.status_label.setText("Testing optimized edit dialog...")
        QApplication.processEvents()
        
        start_time = time.time()
        
        # Import and create the optimized widget
        from create_project import CreateProjectWidget
        
        project_data = self.db.get_project_data(self.current_project)
        
        # Create widget with lazy loading enabled
        widget = CreateProjectWidget(
            self,
            edit_mode=True,
            existing_project_name=self.current_project,
            existing_models=project_data.get("models", []),
            existing_channel_count=project_data.get("channel_count", "DAQ4CH"),
            existing_ip_address=project_data.get("ip_address", ""),
            existing_tag_name=project_data.get("tag_name", ""),
            lazy_load=True  # Enable optimization
        )
        
        # The widget should appear quickly due to lazy loading
        creation_time = time.time() - start_time
        self.status_label.setText(f"Dialog created in {creation_time:.3f}s (models loading asynchronously)")
        
        # Show the widget in a simple window
        widget.show()
        widget.setWindowTitle("Optimized Edit Dialog")
        
class MockMainSection:
    """Mock main section for testing"""
    def set_widget(self, widget):
        widget.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec_())
