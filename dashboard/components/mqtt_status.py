from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QPlainTextEdit, QSizePolicy
from PyQt5.QtCore import Qt

class MQTTStatus(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.is_maximized = False
        self.initUI()
        self.parent.mqtt_status_changed.connect(self.update_mqtt_status_indicator)
        # Buffered console to avoid UI thrash
        self._buffer = []
        self._flush_timer = None
        self._max_lines = 500

    def initUI(self):
        self.setFixedHeight(40)
        self.setStyleSheet("background-color: black;")
        
        # Main vertical layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 0, 5, 0)
        main_layout.setSpacing(0)
        
        # Console message area (initially hidden)
        self.console_message_area = QPlainTextEdit()
        self.console_message_area.setReadOnly(True)
        self.console_message_area.setFixedHeight(0)
        self.console_message_area.hide()
        self.console_message_area.setStyleSheet("""
            QPlainTextEdit { 
                background-color: #0a0a0a; 
                color: #e0e0e0; 
                border: none; 
                font-family: Consolas, monospace; 
                font-size: 14px; 
                padding: 10px; 
            }
            QPlainTextEdit QScrollBar:vertical { 
                width: 0px; 
                height: 0px; 
            }
            QPlainTextEdit QScrollBar:horizontal { 
                width: 0px; 
                height: 0px; 
            }
        """)
        main_layout.addWidget(self.console_message_area)
        
        # Horizontal layout for status and button
        status_layout = QHBoxLayout()
        status_layout.setSpacing(5)
        
        self.status_label = QLabel("Status: Disconnected 🔴")
        self.status_label.setToolTip("MQTT Connection Status")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: black;
                color: #FFFFFF;
                font-size: 14px;
                font: bold;
                padding: 2px 8px;
                border-radius: 0px;
            }
        """)
        status_layout.addWidget(self.status_label)
        
        # Spacer to push maximize button to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        status_layout.addWidget(spacer)
        
        # Maximize button
        self.maximize_button = QPushButton("🗖")
        self.maximize_button.setToolTip("Maximize Console")
        self.maximize_button.clicked.connect(self.toggle_console)
        self.maximize_button.setFixedSize(30, 30)
        self.maximize_button.setStyleSheet("""
            QPushButton { 
                color: white; 
                font-size: 14px; 
                padding: 2px; 
                border-radius: 4px; 
                background-color: #34495e; 
                border: none;
            }
            QPushButton:hover { background-color: #4a90e2; }
            QPushButton:pressed { background-color: #357abd; }
        """)
        status_layout.addWidget(self.maximize_button)
        
        # Add status layout to main layout
        main_layout.addLayout(status_layout)
        
        self.setLayout(main_layout)

    def toggle_console(self):
        if self.is_maximized:
            self.minimize_console()
        else:
            self.maximize_console()

    def maximize_console(self):
        self.is_maximized = True
        self.maximize_button.setText("🗕")
        self.maximize_button.setToolTip("Minimize Console")
        self.setFixedHeight(100)
        
        # Show console area (already in layout at position 0)
        self.console_message_area.setFixedHeight(80)
        self.console_message_area.show()
        
        # Update parent container height
        if hasattr(self.parent, 'console_container'):
            self.parent.console_container.setFixedHeight(120)
        
        # Flush any buffered messages
        self.flush_buffer()

    def minimize_console(self):
        self.is_maximized = False
        self.maximize_button.setText("🗖")
        self.maximize_button.setToolTip("Maximize Console")
        self.setFixedHeight(40)
        
        # Hide console area
        self.console_message_area.hide()
        
        # Update parent container height
        if hasattr(self.parent, 'console_container'):
            self.parent.console_container.setFixedHeight(40)

    def append_to_console(self, text):
        # Log minimal info and buffer writes to UI
        if "MQTT" in text or "mqtt" in text or "layout" in text.lower():
            import logging
            logging.info(text)
            # Buffer messages; flush timer will handle UI append
            self._buffer.append(text)
            if not self._flush_timer:
                from PyQt5.QtCore import QTimer
                self._flush_timer = QTimer(self)
                self._flush_timer.setInterval(400)  # ms
                self._flush_timer.timeout.connect(self.flush_buffer)
            if not self._flush_timer.isActive():
                self._flush_timer.start()

    def flush_buffer(self):
        if not self.console_message_area.isVisible():
            # If hidden, keep buffer small to avoid memory growth
            if len(self._buffer) > 100:
                self._buffer = self._buffer[-100:]
            return
        if not self._buffer:
            if self._flush_timer:
                self._flush_timer.stop()
            return
        try:
            chunk = "\n".join(self._buffer)
            self._buffer.clear()
            self.console_message_area.appendPlainText(chunk)
            self.console_message_area.ensureCursorVisible()
            # Cap the total number of lines to avoid QTextEdit slowdown
            doc = self.console_message_area.document()
            if doc.blockCount() > self._max_lines:
                cursor = self.console_message_area.textCursor()
                cursor.movePosition(cursor.Start)
                cursor.select(cursor.LineUnderCursor)
                # Remove oldest blocks until within limit
                to_remove = doc.blockCount() - self._max_lines
                while to_remove > 0:
                    cursor.select(cursor.LineUnderCursor)
                    cursor.removeSelectedText()
                    cursor.deleteChar()  # remove newline
                    cursor.movePosition(cursor.NextBlock)
                    to_remove -= 1
        except Exception as e:
            import logging
            logging.error(f"Error flushing console buffer: {str(e)}")

    def update_mqtt_status_indicator(self, connected=None):
        status_text = "Status: Connected 🟢" if (connected if connected is not None else self.parent.mqtt_connected) else "Status: Disconnected 🔴"
        self.status_label.setText(status_text)