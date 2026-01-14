from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QGridLayout
from PyQt5.QtCore import QTimer, Qt
import pyqtgraph as pg
import numpy as np
import logging
import time

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class CenterLineFeature:
    def __init__(self, parent, db, project_name, channel=None, model_name=None, console=None):
        self.parent = parent
        self.db = db
        self.project_name = project_name
        self.channel = channel
        self.model_name = model_name
        self.console = console
        self.widget = None
        self.plot_widget = None
        self.plot_item = None
        self.primary_gap_values = []
        self.secondary_gap_values = []
        self.time_values = []
        self.channel_names = []
        self.channel_index = None
        self.secondary_channel_index = None
        self.primary_channel_index = None
        self.tag_name = None
        self.main_channels = 0
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_plots)
        self.update_interval = 200  # ms
        self.start_time = time.time()
        self.all_dc_values = []  # Store all 11 DC values from header
        self.is_updating = False
        self.initUI()
        # Connect to tree view signals like orbit.py
        self.parent.tree_view.model_selected.connect(self.update_model)
        self.parent.tree_view.channel_selected.connect(self.update_channel)
        self.cache_channel_data()
        logging.debug(f"Initialized CenterLineFeature with project_name: {project_name}, model_name: {model_name}, channel: {channel}")

    def initUI(self):
        self.widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.widget.setLayout(main_layout)

        # Channel selection layout
        channel_layout = QHBoxLayout()
        
        # Primary channel selection
        primary_label = QLabel("Primary Channel:")
        primary_label.setStyleSheet("color: black; font-size: 14px; padding: 5px;")
        channel_layout.addWidget(primary_label)
        
        self.primary_channel_combo = QComboBox()
        self.primary_channel_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: black;
                border: 1px solid #cccccc;
                padding: 5px;
                border-radius: 4px;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #e3f2fd;
                border: 1px solid #cccccc;
            }
        """)
        self.primary_channel_combo.currentIndexChanged.connect(self.primary_channel_changed)
        # Primary selection is fixed by tree_view updates; disable manual changes like orbit.py
        self.primary_channel_combo.setEnabled(False)
        channel_layout.addWidget(self.primary_channel_combo)
        
        # Secondary channel selection
        secondary_label = QLabel("Secondary Channel:")
        secondary_label.setStyleSheet("color: black; font-size: 14px; padding: 5px;")
        channel_layout.addWidget(secondary_label)
        
        self.secondary_channel_combo = QComboBox()
        self.secondary_channel_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: black;
                border: 1px solid #cccccc;
                padding: 5px;
                border-radius: 4px;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #e3f2fd;
                border: 1px solid #cccccc;
            }
        """)
        self.secondary_channel_combo.currentIndexChanged.connect(self.secondary_channel_changed)
        channel_layout.addWidget(self.secondary_channel_combo)
        
        main_layout.addLayout(channel_layout)

        # Plot layout for single scatter plot
        plot_layout = QVBoxLayout()
        
        # Setup pyqtgraph
        pg.setConfigOptions(antialias=True)
        
        # Primary vs Secondary scatter plot
        self.scatter_plot = pg.PlotWidget()
        self.scatter_plot.setBackground("white")
        self.scatter_plot.setTitle("Centerline", color="black", size="20pt")
        self.scatter_plot.setLabel('left', 'Secondary Channel DC Value (V)', color='black')
        self.scatter_plot.setLabel('bottom', 'Primary Channel DC Value (V)', color='black')
        self.scatter_plot.showGrid(x=True, y=True)
        self.scatter_plot_item = self.scatter_plot.plot(
            x=[], y=[],
            symbol='o',
            symbolSize=5,
            pen=None,
            symbolPen=pg.mkPen(color=(0, 128, 0), width=2),  # Green
            symbolBrush=pg.mkBrush(color=(0, 128, 0)),
            name="Primary vs Secondary DC"
        )
        plot_layout.addWidget(self.scatter_plot)
        
        main_layout.addLayout(plot_layout)

        # Waiting message label
        self.waiting_message = QLabel("Waiting for DC data...")
        self.waiting_message.setStyleSheet("color: black; font-size: 14px; padding: 10px;")
        self.waiting_message.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.waiting_message)

        self.update_timer.start(self.update_interval)

    def cache_channel_data(self):
        try:
            if not self.db.is_connected():
                self.db.reconnect()
            project_data = self.db.get_project_data(self.project_name)
            if not project_data or "models" not in project_data:
                logging.error(f"Project {self.project_name} or models not found")
                if self.console:
                    self.console.append_to_console(f"Project {self.project_name} or models not found.")
                self.waiting_message.setText("Project or models not found.")
                return

            model = next((m for m in project_data["models"] if m.get("name") == self.model_name), None)
            if not model:
                logging.error(f"Model {self.model_name} not found")
                if self.console:
                    self.console.append_to_console(f"Model {self.model_name} not found.")
                self.waiting_message.setText("Model not found.")
                return

            self.tag_name = model.get("tagName")
            if not self.tag_name:
                logging.error(f"TagName is empty for model {self.model_name}")
                if self.console:
                    self.console.append_to_console(f"TagName not found for model {self.model_name}.")
                self.waiting_message.setText("TagName not found for selected model.")
                return

            # Create DC channel names (ch1 to ch10) for dropdowns
            self.channel_names = [f"ch{i+1}" for i in range(10)]
            self.main_channels = len(self.channel_names)

            # Find primary channel index (0-based) - use the channel from treeview or default to ch1
            if self.channel is None or self.channel not in self.channel_names:
                self.channel = self.channel_names[0] if self.channel_names else None
                logging.warning(f"Channel was None or not found, using default: {self.channel}")
                if self.console:
                    self.console.append_to_console(f"Channel was None or not found, using default: {self.channel}")
            
            self.channel_index = self.channel_names.index(self.channel) if self.channel and self.channel in self.channel_names else -1
            self.primary_channel_index = self.channel_index
            if self.channel_index == -1:
                logging.error(f"Selected channel {self.channel} not found. Available channels: {', '.join(self.channel_names)}")
                if self.console:
                    self.console.append_to_console(f"Selected channel {self.channel} not found.")
                self.waiting_message.setText("Selected channel not found.")
                return

            # Populate primary channel combo box with all channels (display only; disabled for manual change)
            self.primary_channel_combo.clear()
            self.primary_channel_combo.addItems(self.channel_names)
            
            # Set primary channel from treeview selection or default to first channel
            if self.channel and self.channel in self.channel_names:
                self.channel_index = self.channel_names.index(self.channel)
            else:
                self.channel = self.channel_names[0] if self.channel_names else None
                self.channel_index = 0
                logging.warning(f"Channel was None or not found, using default: {self.channel}")
                if self.console:
                    self.console.append_to_console(f"Channel was None or not found, using default: {self.channel}")
            
            self.primary_channel_index = self.channel_index
            self.primary_channel_combo.setCurrentIndex(self.primary_channel_index)

            # Populate secondary channel combo box with all DC channels
            self.secondary_channel_combo.clear()
            self.secondary_channel_combo.addItems(self.channel_names)
            
            # Set default secondary channel to next channel after primary
            # If primary is ch1, secondary should be ch2; if ch2 -> ch3, etc.
            # For ch10, wrap around to ch1
            primary_channel_num = int(self.channel.replace('ch', ''))
            secondary_channel_num = primary_channel_num % 10 + 1  # Wrap around after ch10
            secondary_channel = f'ch{secondary_channel_num}'
            
            # Find and set the secondary channel
            if secondary_channel in self.channel_names:
                secondary_index = self.channel_names.index(secondary_channel)
                self.secondary_channel_combo.setCurrentIndex(secondary_index)
                self.secondary_channel_index = secondary_index
            else:
                # Fallback to first different channel if next channel not found
                for i, channel_name in enumerate(self.channel_names):
                    if channel_name != self.channel:
                        self.secondary_channel_combo.setCurrentIndex(i)
                        self.secondary_channel_index = i
                        break

            logging.debug(f"Primary channel {self.channel} index (0-based): {self.channel_index}, TagName: {self.tag_name}, Secondary channel: {self.secondary_channel_combo.currentText()}")
            if self.console:
                self.console.append_to_console(f"Primary channel: {self.channel_names[self.channel_index]}")
                self.console.append_to_console(f"Available DC channels: {', '.join(self.channel_names)}")
                if self.secondary_channel_combo.currentText():
                    self.console.append_to_console(f"Selected default secondary channel: {self.secondary_channel_combo.currentText()}")

        except Exception as e:
            logging.error(f"Error caching channel data: {str(e)}")
            if self.console:
                self.console.append_to_console(f"Error caching channel data: {str(e)}")
            self.waiting_message.setText("Error initializing view.")

    def update_model(self, model_name):
        """Handle model selection from tree view (like orbit.py)"""
        if self.model_name != model_name:
            self.model_name = model_name
            self.channel = None
            self.channel_index = None
            self.primary_channel_index = None
            self.secondary_channel_index = None
            self.primary_gap_values.clear()
            self.secondary_gap_values.clear()
            self.time_values.clear()
            self.all_dc_values = []
            self.cache_channel_data()
            if self.console:
                self.console.append_to_console(f"CenterLineFeature: Updated model to {model_name}")

    def update_channel(self, model_name, channel_name):
        """Handle channel selection from tree view (like orbit.py)"""
        if self.model_name == model_name and channel_name in self.channel_names:
            self.update_selected_channel(channel_name)
            if self.console:
                self.console.append_to_console(f"CenterLineFeature: Updated channel to {channel_name}")
        else:
            if self.console:
                self.console.append_to_console(
                    f"CenterLineFeature: Skipped channel update - model mismatch ({self.model_name} vs {model_name}) "
                    f"or channel {channel_name} not in {self.channel_names}"
                )

    def update_selected_channel(self, channel_name):
        """Update selected channel from tree view (like orbit.py)"""
        if self.is_updating:
            return
        self.is_updating = True
        try:
            if channel_name and channel_name in self.channel_names:
                self.channel = channel_name
                self.channel_index = self.channel_names.index(channel_name)
                self.primary_channel_index = self.channel_index
                
                # Update primary dropdown
                self.primary_channel_combo.setCurrentIndex(self.primary_channel_index)
                
                # Set secondary channel to next channel after primary
                primary_channel_num = int(channel_name.replace('ch', ''))
                secondary_channel_num = primary_channel_num % 10 + 1  # Wrap around after ch10
                secondary_channel = f'ch{secondary_channel_num}'
                
                # Set secondary channel (next channel after primary)
                if secondary_channel in self.channel_names:
                    secondary_index = self.channel_names.index(secondary_channel)
                    self.secondary_channel_combo.setCurrentIndex(secondary_index)
                    self.secondary_channel_index = secondary_index
                else:
                    # Fallback to first different channel
                    for i, channel_name in enumerate(self.channel_names):
                        if channel_name != channel_name:
                            self.secondary_channel_combo.setCurrentIndex(i)
                            self.secondary_channel_index = i
                            break
                
                # Clear data and reset for new primary channel
                self.primary_gap_values.clear()
                self.secondary_gap_values.clear()
                self.time_values.clear()
                self.scatter_plot_item.clear()
                self.waiting_message.setVisible(True)
                self.waiting_message.setText("Waiting for DC data...")
                
                logging.debug(f"Primary channel updated from treeview: {channel_name}")
                if self.console:
                    self.console.append_to_console(f"Primary channel updated from treeview: {channel_name}")
                    self.console.append_to_console(f"Secondary channel set to: {self.secondary_channel_combo.currentText()}")
            else:
                logging.warning(f"Channel {channel_name} not found in available channels: {self.channel_names}")
                if self.console:
                    self.console.append_to_console(f"Channel {channel_name} not found in available channels")
        except Exception as e:
            logging.error(f"Error updating selected channel: {str(e)}")
            if self.console:
                self.console.append_to_console(f"Error updating selected channel: {str(e)}")
        finally:
            self.is_updating = False

    def get_widget(self):
        return self.widget

    def on_measured_dc_values_received(self, dc_values):
        """Handle measured DC values from MQTT handler."""
        try:
            logging.debug(f"Received DC values: {len(dc_values)} channels")
            
            # Validate we have 10 DC values
            if len(dc_values) != 10:
                logging.warning(f"Expected 10 DC values, got {len(dc_values)}")
                if self.console:
                    self.console.append_to_console(f"Warning: Expected 10 DC values, got {len(dc_values)}")
                return
            
            # Validate DC values are reasonable
            for i, dc_val in enumerate(dc_values):
                if abs(dc_val) > 1000:
                    logging.warning(f"Ignoring unreasonable DC value for channel {i+1}: {dc_val}")
                    if self.console:
                        self.console.append_to_console(f"Warning: Unreasonable DC value for channel {i+1}: {dc_val}")
                    return
            
            # Store all DC values
            self.all_dc_values = dc_values
            
            # Extract primary and secondary DC values based on dropdown selection
            if (self.primary_channel_index is not None and 
                self.secondary_channel_index is not None and
                self.primary_channel_index < len(dc_values) and 
                self.secondary_channel_index < len(dc_values)):
                
                primary_dc = dc_values[self.primary_channel_index]
                secondary_dc = dc_values[self.secondary_channel_index]
                
                # Append DC values with timestamp
                current_time = time.time()
                self.time_values.append(current_time)
                self.primary_gap_values.append(primary_dc)
                self.secondary_gap_values.append(secondary_dc)
                self.waiting_message.setVisible(False)

                logging.debug(f"Received DC data: Primary ({self.channel_names[self.primary_channel_index]}): {primary_dc:.2f}, "
                             f"Secondary ({self.channel_names[self.secondary_channel_index]}): {secondary_dc:.2f}")
                if self.console:
                    self.console.append_to_console(f"Received DC: Primary ({self.channel_names[self.primary_channel_index]}): {primary_dc:.2f}V, "
                                                 f"Secondary ({self.channel_names[self.secondary_channel_index]}): {secondary_dc:.2f}V")

                # Immediate plot update
                self.update_plots()
            else:
                logging.warning(f"Invalid channel indices: Primary={self.primary_channel_index}, Secondary={self.secondary_channel_index}")
                if self.console:
                    self.console.append_to_console(f"Warning: Invalid channel selection")

        except Exception as e:
            logging.error(f"Error in on_measured_dc_values_received: {str(e)}")
            if self.console:
                self.console.append_to_console(f"Error processing DC values: {str(e)}")
            self.waiting_message.setText("Error processing DC data.")

    def update_plots(self):
        try:
            if not self.primary_gap_values or not self.secondary_gap_values or not self.time_values:
                logging.debug("No data to plot")
                return

            # Ensure data is in NumPy arrays
            time_data = np.array(self.time_values, dtype=np.float64)
            if len(time_data) > 0:
                # Convert to relative time from start
                time_data = time_data - self.start_time
            
            primary_data = np.array(self.primary_gap_values, dtype=np.float64)
            secondary_data = np.array(self.secondary_gap_values, dtype=np.float64)

            # Update primary vs secondary scatter plot
            self.scatter_plot_item.setData(x=primary_data, y=secondary_data)
            self.scatter_plot.setTitle(f"{self.channel_names[self.primary_channel_index]} vs {self.channel_names[self.secondary_channel_index]} DC")
            self.scatter_plot.setLabel('bottom', f"{self.channel_names[self.primary_channel_index]} DC Value (V)")
            self.scatter_plot.setLabel('left', f"{self.channel_names[self.secondary_channel_index]} DC Value (V)")
            self.scatter_plot.getPlotItem().autoRange()

            logging.debug(f"Updated plots with {len(self.primary_gap_values)} points: "
                         f"Primary = {self.primary_gap_values[:5]}, Secondary = {self.secondary_gap_values[:5]}")
            if self.console:
                self.console.append_to_console(f"Updated plots with {len(self.primary_gap_values)} points")

        except Exception as e:
            logging.error(f"Error updating plots: {str(e)}")
            if self.console:
                self.console.append_to_console(f"Error updating plots: {str(e)}")


    def primary_channel_changed(self):
        # Primary channel is fixed from treeview selection, this should not be changeable
        # Reset to the original channel if somehow changed
        if self.is_updating:
            return
        self.is_updating = True
        try:
            if self.channel and self.channel in self.channel_names:
                index = self.primary_channel_combo.findText(self.channel)
                if index >= 0:
                    self.primary_channel_combo.setCurrentIndex(index)
                    self.primary_channel_index = self.channel_names.index(self.channel)
            logging.debug("Primary channel selection is fixed from treeview")
        finally:
            self.is_updating = False

    def secondary_channel_changed(self):
        if self.is_updating:
            return
        self.is_updating = True
        try:
            selected_channel = self.secondary_channel_combo.currentText()
            if selected_channel:
                self.secondary_channel_index = self.channel_names.index(selected_channel)
                # Clear data and reset for new secondary channel
                self.primary_gap_values.clear()
                self.secondary_gap_values.clear()
                self.time_values.clear()
                self.scatter_plot_item.clear()
                self.waiting_message.setVisible(True)
                self.waiting_message.setText("Waiting for DC data...")
                logging.debug(f"Secondary channel changed to {selected_channel}. Plot data reset.")
                if self.console:
                    self.console.append_to_console(f"Secondary channel changed to {selected_channel}. Plot data reset.")
        except Exception as e:
            logging.error(f"Error changing secondary channel: {str(e)}")
            if self.console:
                self.console.append_to_console(f"Error changing secondary channel: {str(e)}")
        finally:
            self.is_updating = False

    def cleanup(self):
        self.update_timer.stop()
        self.primary_gap_values.clear()
        self.secondary_gap_values.clear()
        self.time_values.clear()
        self.scatter_plot_item.clear()
        logging.debug("Cleaned up CenterLineFeature resources")
        if self.console:
            self.console.append_to_console("Cleaned up Centerline View resources")