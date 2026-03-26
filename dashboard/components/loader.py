from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont

class LoaderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Loading text
        self.loading_label = QLabel("Loading Project Editor...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 18px;
                font-weight: bold;
                margin: 10px;
            }
        """)
        self.loading_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(300)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2c3e50;
                border-radius: 3px;
                text-align: center;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #4a90e2;
                border-radius: 2px;
            }
        """)
        
        # Add pulsing animation
        self.animation = QPropertyAnimation(self.progress_bar, b"value")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(100)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setLoopCount(-1)  # Infinite loop
        
        layout.addStretch()
        layout.addWidget(self.loading_label)
        layout.addWidget(self.progress_bar, 0, Qt.AlignCenter)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def start_loading(self):
        """Start the loading animation"""
        self.animation.start()
        
    def stop_loading(self):
        """Stop the loading animation"""
        self.animation.stop()
        self.progress_bar.setValue(0)
