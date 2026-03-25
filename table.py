from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView, 
                            QComboBox, QCheckBox, QWidget, QHBoxLayout)
from PyQt5.QtCore import Qt
import logging

class ChannelTable:
    """Helper class for creating and managing channel configuration tables"""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.available_types = ["Displacement", "Acceleration", "Velocity", "Generic Input"]
        self.available_directions = ["Right", "Left"]
        self.available_units_displacement = ["um", "mil", "mm"]
        self.available_units_acceleration = ["g", "m/s²"]
        self.available_units_velocity = ["mm/s", "in/s"]
        self.available_units_generic = ["v"]
        self.available_unit_types = ["Displacement", "Volts"]
    
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
    
    def get_table_style(self):
        """Get comprehensive table styling"""
        return """
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
        """
    
    def get_header_style(self):
        """Get header styling for tables"""
        return """
            QHeaderView::section {
                background: #7ea4a6;
                color: #ffffff;
                font-size: 13px;
                font-weight: 600;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                padding: 12px 8px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QHeaderView::section:hover {
                background: #7ea4a6;
            }
        """
    
    def create_channel_table(self, num_channels, existing_model=None):
        """Create a channel configuration table"""
        table = QTableWidget(num_channels, 12)
        table.setHorizontalHeaderLabels(["S.No.", "Active", "Channel Name", "Channel Type", "Sensitivity", "Unit", "Subunit", "Correction Value", "Gain", "Angle", "Angle Dir", "Shaft"])
        
        # Apply header styling
        header = table.horizontalHeader()
        header.setStyleSheet(self.get_header_style())
        
        # Apply table styling
        table.setStyleSheet(self.get_table_style())
        
        # Configure table properties
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
        table.setMinimumWidth(1500)
        
        # Set specific column widths
        self._set_column_widths(table.horizontalHeader())
        
        # Populate table with data
        if existing_model and existing_model.get("channels"):
            for row, channel in enumerate(existing_model["channels"]):
                if row >= num_channels:
                    break
                self.populate_channel_row(table, row, channel)
        else:
            for row in range(num_channels):
                self.populate_channel_row(table, row)
        
        return table
    
    def _set_column_widths(self, header):
        """Set specific column widths for better layout"""
        header.resizeSection(0, 70)   # S.No.
        header.resizeSection(1, 80)   # Active (checkbox)
        header.resizeSection(2, 250)  # Channel Name
        header.resizeSection(3, 160)  # Channel Type
        header.resizeSection(4, 150)  # Sensitivity
        header.resizeSection(5, 110)  # Unit
        header.resizeSection(6, 110)  # Subunit
        header.resizeSection(7, 160)  # Correction Factor
        header.resizeSection(8, 110)  # Gain
        header.resizeSection(9, 100)  # Angle
        header.resizeSection(10, 140) # Direction
        header.resizeSection(11, 120)  # Shaft
        
        # Make the last column stretch to fill remaining space
        header.setStretchLastSection(True)
    
    def populate_channel_row(self, table, row, channel_data=None):
        """Populate a single row in the channel table"""
        # S.No.
        item = QTableWidgetItem(str(row + 1))
        item.setTextAlignment(Qt.AlignCenter)
        table.setItem(row, 0, item)
        
        # Add checkbox for Active column (column 1)
        checkbox = QCheckBox()
        checkbox.setChecked(channel_data.get("active", True) if channel_data else True)
        checkbox.setStyleSheet("""
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #d1d5db;
                border-radius: 3px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:hover {
                border-color: #3b82f6;
            }
            QCheckBox::indicator:checked {
                background-color: #3b82f6;
                border-color: #3b82f6;
                image: url(right.png);
            }
        """)
        checkbox_cell_widget = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_cell_widget)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        checkbox_layout.setAlignment(Qt.AlignCenter)
        checkbox_layout.addWidget(checkbox)
        table.setCellWidget(row, 1, checkbox_cell_widget)
        
        # Channel Name
        table.setItem(row, 2, QTableWidgetItem(channel_data.get("channelName", f"CH{row + 1}") if channel_data else f"CH{row + 1}"))
        
        # Channel Type
        type_combo = QComboBox()
        type_combo.addItems(self.available_types)
        type_combo.setCurrentText(channel_data.get("type", "Displacement") if channel_data else "Displacement")
        type_combo.setStyleSheet(self.get_combo_box_style())
        type_combo.currentIndexChanged.connect(lambda _, r=row: self.update_unit_combo(table, r))
        table.setCellWidget(row, 3, type_combo)
        
        # Sensitivity - set based on channel type
        current_type = type_combo.currentText()
        sensitivity_values = {
            "Displacement": 0.007874,
            "Acceleration": 0.1,
            "Velocity": 0.02,
            "Generic Input": 1.0
        }
        default_sensitivity = sensitivity_values.get(current_type, 0.007874)
        table.setItem(row, 4, QTableWidgetItem(channel_data.get("sensitivity", str(default_sensitivity)) if channel_data else str(default_sensitivity)))
        
        # Unit
        unit_combo = QComboBox()
        current_type = type_combo.currentText()
        
        if current_type == "Displacement":
            unit_items = self.available_units_displacement
            default_unit = "um"
        elif current_type == "Acceleration":
            unit_items = self.available_units_acceleration
            default_unit = "g"
        elif current_type == "Velocity":
            unit_items = self.available_units_velocity
            default_unit = "mm/s"
        elif current_type == "Generic Input":
            unit_items = self.available_units_generic
            default_unit = "v"
        else:
            unit_items = self.available_units_displacement
            default_unit = "um"
            
        unit_combo.addItems(unit_items)
        unit_combo.setCurrentText(channel_data.get("unit", default_unit) if channel_data else default_unit)
        unit_combo.setStyleSheet(self.get_combo_box_style())
        table.setCellWidget(row, 5, unit_combo)

        # Subunit
        subunit_combo = QComboBox()
        subunit_combo.addItems(["pp", "pk", "rms"])
        if channel_data:
            sub_val = str(channel_data.get("subunit", "pp") or "pp").lower()
            subunit_combo.setCurrentText("pp" if sub_val in ("pp", "pk-pk", "peak to peak") else ("pk" if sub_val in ("pk", "peak") else "rms"))
        else:
            subunit_combo.setCurrentText("pp")
        subunit_combo.setStyleSheet(self.get_combo_box_style())
        table.setCellWidget(row, 6, subunit_combo)
        
        # Correction Factor
        table.setItem(row, 7, QTableWidgetItem(channel_data.get("correctionValue", "1") if channel_data else "1"))
        
        # Gain
        table.setItem(row, 8, QTableWidgetItem(channel_data.get("gain", "1") if channel_data else "1"))
        
        # Angle
        table.setItem(row, 9, QTableWidgetItem(channel_data.get("angle", "45") if channel_data else "45"))
        
        # Direction
        direction_combo = QComboBox()
        direction_combo.addItems(self.available_directions)
        default_direction = "Right" if row % 2 == 0 else "Left"
        direction_combo.setCurrentText(channel_data.get("angleDirection", default_direction) if channel_data else default_direction)
        direction_combo.setStyleSheet(self.get_combo_box_style())
        table.setCellWidget(row, 10, direction_combo)
        
        # Shaft
        shaft_combo = QComboBox()
        shaft_combo.addItems(["CCW", "CW"])
        shaft_combo.setCurrentText(channel_data.get("shaft", "CCW") if channel_data else "CCW")
        shaft_combo.setStyleSheet(self.get_combo_box_style())
        table.setCellWidget(row, 11, shaft_combo)
    
    def update_unit_combo(self, table, row):
        """Update unit combo box based on channel type selection"""
        type_combo = table.cellWidget(row, 3)
        unit_combo = table.cellWidget(row, 5)
        current_type = type_combo.currentText()
        
        # Save current unit selection before clearing
        current_unit = unit_combo.currentText() if unit_combo else ""
        
        # Clear and update unit combo based on channel type
        unit_combo.clear()
        
        # Set sensitivity based on channel type
        sensitivity_values = {
            "Displacement": 0.007874,
            "Acceleration": 0.1,
            "Velocity": 0.02,
            "Generic Input": 1.0
        }
        
        if current_type == "Displacement":
            unit_items = self.available_units_displacement
            default_unit = "um"
        elif current_type == "Acceleration":
            unit_items = self.available_units_acceleration
            default_unit = "g"
        elif current_type == "Velocity":
            unit_items = self.available_units_velocity
            default_unit = "mm/s"
        elif current_type == "Generic Input":
            unit_items = self.available_units_generic
            default_unit = "v"
        else:
            unit_items = self.available_units_displacement
            default_unit = "um"
            
        unit_combo.addItems(unit_items)
        
        # Try to restore previous unit if it exists in the new list, otherwise set default
        if current_unit in unit_items:
            unit_combo.setCurrentText(current_unit)
        else:
            unit_combo.setCurrentText(default_unit)
        
        # Set sensitivity value based on channel type
        sensitivity_value = sensitivity_values.get(current_type, 1.0)
        table.setItem(row, 4, QTableWidgetItem(str(sensitivity_value)))
    
    def get_sensitivity_values_from_table(self, table):
        """Extract sensitivity values from a table, only from active channels"""
        sensitivity_values = []
        
        for row in range(table.rowCount()):
            # Check if channel is active
            checkbox_widget = table.cellWidget(row, 1)
            checkbox = checkbox_widget.findChild(QCheckBox) if checkbox_widget else None
            is_active = checkbox.isChecked() if checkbox else True
            
            if not is_active:
                continue  # Skip inactive channels
                
            sensitivity_item = table.item(row, 4)
            if sensitivity_item and sensitivity_item.text().strip():
                try:
                    value = float(sensitivity_item.text().strip())
                    sensitivity_values.append(value)
                except ValueError:
                    raise ValueError(f"Invalid sensitivity value in row {row+1}. Please enter a valid number.")
        
        if not sensitivity_values:
            raise ValueError("No sensitivity values found in the table.")
            
        return sensitivity_values
    
    def get_table_data(self, table):
        """Extract all data from a table"""
        channels = []
        for row in range(table.rowCount()):
            # Get checkbox state from column 1
            checkbox_widget = table.cellWidget(row, 1)
            checkbox = checkbox_widget.findChild(QCheckBox) if checkbox_widget else None
            is_active = checkbox.isChecked() if checkbox else True
            
            channel_name = table.item(row, 2).text().strip() if table.item(row, 2) else ""
            if not channel_name:
                raise ValueError(f"Channel name cannot be empty for row {row + 1}!")
                
            channels.append({
                "active": is_active,
                "channelName": channel_name,
                "type": table.cellWidget(row, 3).currentText() if table.cellWidget(row, 3) else "Displacement",
                "sensitivity": table.item(row, 4).text().strip() if table.item(row, 4) else "",
                "unit": table.cellWidget(row, 5).currentText() if table.cellWidget(row, 5) else "mil",
                "subunit": table.cellWidget(row, 6).currentText() if table.cellWidget(row, 6) else "pp",
                "correctionValue": table.item(row, 7).text().strip() if table.item(row, 7) else "",
                "gain": table.item(row, 8).text().strip() if table.item(row, 8) else "",
                "angle": table.item(row, 9).text().strip() if table.item(row, 9) else "",
                "angleDirection": table.cellWidget(row, 10).currentText() if table.cellWidget(row, 10) else "Right",
                "shaft": table.cellWidget(row, 11).currentText() if table.cellWidget(row, 11) else "CCW"
            })
        
        return channels
