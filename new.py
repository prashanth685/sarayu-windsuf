import sys
from PyQt5.QtWidgets import QApplication, QWidget, QCheckBox, QLabel, QVBoxLayout

class CheckBoxDemo(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt5 Checkbox Example")

        # Create a checkbox
        self.checkbox = QCheckBox("Check me")

        # Create a label
        self.label = QLabel("Unchecked")

        # Connect checkbox state change
        self.checkbox.stateChanged.connect(self.update_label)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def update_label(self):
        if self.checkbox.isChecked():
            self.label.setText("Checked")
        else:
            self.label.setText("Unchecked")

# Run the app
app = QApplication(sys.argv)
window = CheckBoxDemo()
window.show()
sys.exit(app.exec_())