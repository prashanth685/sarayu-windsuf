import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from pymongo import MongoClient
import logging
from datetime import datetime
from scipy import signal

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class BodePlotFeature:
    def __init__(self, parent, db, project_name, channel=None, model_name=None, console=None):
        self.parent = parent
        self.db = db
        self.project_name = project_name
        self.selected_channel = channel
        self.model_name = model_name
        self.console = console
        self.widget = None
        self.plot_widgets = {}
        self.plots = {}
        self.data = {}
        self.tag_name = None
        self.channel_names = []
        self.channel_indices = {}
        self.scaling_factor = 3.3 / 65535.0  # Voltage scaling for ADC
        self.colors = {
            'amplitude': (0, 0, 255),  # Blue
            'phase': (255, 0, 0),      # Red
            '1x_amplitude': (0, 128, 0),  # Green for 1x amplitude
            '1x_phase': (255, 165, 0)     # Orange for 1x phase
        }
        
        # Initialize UI first for instant feedback
        self.init_ui()
        
        # Connect signals
        if hasattr(self.parent, 'tree_view') and hasattr(self.parent.tree_view, 'channel_selected'):
            self.parent.tree_view.channel_selected.connect(self.on_channel_selected)
            self.log_info("Connected to channel_selected signal")
        else:
            self.log_error("Parent tree_view does not have channel_selected signal")
        
        # Initialize data in background
        QTimer.singleShot(100, self.init_data_async)
        
    def init_data_async(self):
        """Initialize data in a non-blocking way"""
        self.init_data()
        # Update UI after data is loaded
        if self.selected_channel:
            self.update_visible_plots()
            self.update_plots()

    def init_data(self):
        try:
            if not self.db.is_connected():
                self.db.reconnect()
            project_data = self.db.get_project_data(self.project_name)
            if not project_data or "models" not in project_data:
                self.log_error(f"Project {self.project_name} or models not found.")
                return
                
            model = next((m for m in project_data["models"] if m["name"] == self.model_name), None)
            if not model or not model.get("tagName"):
                self.log_error(f"TagName not found for Model: {self.model_name}")
                return
                
            self.tag_name = model["tagName"]
            self.channel_names = [c["channelName"] for c in model.get("channels", [])]
            self.channel_indices = {name: idx for idx, name in enumerate(self.channel_names)}
            
            if not self.channel_names:
                self.log_error(f"No channels found in model {self.model_name}.")
                return
                
            for ch_name in self.channel_names:
                self.data[ch_name] = {
                    'frequencies': [],
                    'amplitudes': [],
                    'phases': []
                }
                
            # Initialize plots for all channels
            self.init_plots()
            
            # Update the UI to show the content and hide the placeholder
            self.placeholder.setVisible(False)
            self.content.setVisible(True)
            
            self.log_info(f"Initialized BodePlotFeature for Model: {self.model_name}, Tag: {self.tag_name}")
            
            if self.selected_channel and self.selected_channel in self.channel_names:
                self.log_info(f"Initial channel set to: {self.selected_channel}")
            else:
                self.selected_channel = self.channel_names[0] if self.channel_names else None
                self.log_info(f"Initial channel set to: {self.selected_channel}")
                
            # Start the update timer
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.update_plots)
            self.update_timer.start(1000)
            
        except Exception as e:
            self.log_error(f"Error initializing BodePlotFeature: {str(e)}")
            self.placeholder.setText(f"Error: {str(e)}")
    
    def init_plots(self):
        """Initialize plot widgets for all channels"""
        for ch_name in self.channel_names:
            self._init_channel_plots(ch_name)
        
        # Initialize visibility for the selected channel
        self.update_visible_plots()
        self.log_info("Initialized BodePlotFeature UI")
    
    def _init_channel_plots(self, ch_name):
        """Initialize plot widgets for a single channel using matplotlib"""
        channel_widget = QWidget()
        channel_layout = QVBoxLayout()
        channel_layout.setContentsMargins(0, 0, 0, 0)
        channel_layout.setSpacing(2)
        channel_widget.setLayout(channel_layout)
        channel_widget.setVisible(ch_name == self.selected_channel)

        # Create matplotlib figure with two subplots (amplitude and phase)
        fig = Figure(figsize=(10, 8), facecolor='white')
        canvas = FigureCanvas(fig)
        
        # Amplitude subplot (magnitude vs frequency)
        ax_amp = fig.add_subplot(211)
        ax_amp.set_xlabel('Frequency (Hz)')
        ax_amp.set_ylabel('Magnitude (dB)')
        ax_amp.set_title(f'Magnitude Response - {ch_name}')
        ax_amp.grid(True, which='both', alpha=0.3)
        ax_amp.set_xscale('log')
        
        # Initialize amplitude line
        amp_line, = ax_amp.plot([], [], 'b-', linewidth=1.5, label='Magnitude')
        amp_1x_scatter = ax_amp.scatter([], [], c='g', s=50, marker='o', label='1x Magnitude', zorder=5)
        ax_amp.legend(loc='best')
        
        # Phase subplot
        ax_phase = fig.add_subplot(212)
        ax_phase.set_xlabel('Frequency (Hz)')
        ax_phase.set_ylabel('Phase (degrees)')
        ax_phase.set_title(f'Phase Response - {ch_name}')
        ax_phase.grid(True, which='both', alpha=0.3)
        ax_phase.set_xscale('log')
        ax_phase.set_ylim(-180, 180)
        
        # Initialize phase line
        phase_line, = ax_phase.plot([], [], 'r-', linewidth=1.5, label='Phase')
        phase_1x_scatter = ax_phase.scatter([], [], c='orange', s=50, marker='o', label='1x Phase', zorder=5)
        ax_phase.legend(loc='best')
        
        # Adjust layout
        fig.tight_layout()
        
        # Store matplotlib objects
        self.plot_widgets[f"{ch_name}_widget"] = channel_widget
        self.plot_widgets[f"{ch_name}_canvas"] = canvas
        self.plot_widgets[f"{ch_name}_fig"] = fig
        self.plot_widgets[f"{ch_name}_ax_amp"] = ax_amp
        self.plot_widgets[f"{ch_name}_ax_phase"] = ax_phase
        
        # Store plot lines
        self.plots[f"{ch_name}_amp"] = amp_line
        self.plots[f"{ch_name}_phase"] = phase_line
        self.plots[f"{ch_name}_amp_1x"] = amp_1x_scatter
        self.plots[f"{ch_name}_phase_1x"] = phase_1x_scatter
        
        channel_layout.addWidget(canvas)
        self.plot_layout.addWidget(channel_widget)

    def init_ui(self):
        self.widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)  # Reduce margins for more space
        main_layout.setSpacing(2)  # Reduce spacing between widgets
        self.widget.setLayout(main_layout)

        # Create a placeholder widget that will be shown immediately
        self.placeholder = QLabel("Loading Bode Plot...")
        self.placeholder.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.placeholder)
        
        # Create the actual content that will be shown after initialization
        self.content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(2)
        self.content.setLayout(content_layout)
        
        header_label = QLabel(f"Bode Plot for Model: {self.model_name}")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 2px;")
        content_layout.addWidget(header_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setVisible(False)
        content_layout.addWidget(self.progress_bar)

        self.plot_container = QWidget()
        self.plot_layout = QVBoxLayout()
        self.plot_layout.setContentsMargins(0, 0, 0, 0)
        self.plot_layout.setSpacing(2)
        self.plot_container.setLayout(self.plot_layout)
        content_layout.addWidget(self.plot_container)

        self.error_label = QLabel("Waiting for data or select a channel...")
        self.error_label.setStyleSheet("color: red; font-size: 12px; padding: 2px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.error_label)
        self.error_label.setVisible(False)
        
        # Add content to main layout but hide it initially
        main_layout.addWidget(self.content)
        self.content.setVisible(False)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_plots)
        self.update_timer.start(1000)
        
        # Initialize visibility for the selected channel
        self.update_visible_plots()
        self.log_info("Initialized BodePlotFeature UI")

    def on_channel_selected(self, model_name, channel_name):
        if model_name != self.model_name:
            self.log_info(f"Ignoring channel selection for model: {model_name}")
            return
        if channel_name not in self.channel_names:
            self.log_error(f"Selected channel {channel_name} not found in model {model_name}")
            self.selected_channel = self.channel_names[0] if self.channel_names else None
            self.log_info(f"Defaulted to channel: {self.selected_channel}")
        else:
            self.selected_channel = channel_name
            self.log_info(f"Channel selected: {channel_name}")
        self.update_visible_plots()
        self.update_plots()

    def get_1x_data_from_tabular(self, channel_name):
        """Retrieve 1x amplitude and phase data from the tabular view."""
        try:
            # Check if parent has feature_instances (newer versions)
            if hasattr(self.parent, 'feature_instances'):
                # Find tabular view in feature_instances
                for key, feature in self.parent.feature_instances.items():
                    if 'tabular' in str(key[0]).lower():
                        tabular_view = feature
                        if (hasattr(tabular_view, 'one_x_amps') and 
                            hasattr(tabular_view, 'one_x_phases')):
                            
                            channel_idx = self.channel_names.index(channel_name) if channel_name in self.channel_names else 0
                            
                            if (channel_idx < len(tabular_view.one_x_amps) and 
                                channel_idx < len(tabular_view.one_x_phases) and
                                tabular_view.one_x_amps and 
                                tabular_view.one_x_phases and
                                channel_idx < len(tabular_view.one_x_amps) and
                                channel_idx < len(tabular_view.one_x_phases)):
                                
                                # Get the most recent 1x amplitude and phase values
                                one_x_amp = tabular_view.one_x_amps[channel_idx][-1] if tabular_view.one_x_amps[channel_idx] else 0
                                one_x_phase = tabular_view.one_x_phases[channel_idx][-1] if tabular_view.one_x_phases[channel_idx] else 0
                                
                                # Get the corresponding frequency (RPM/60)
                                rpm = 0
                                if hasattr(tabular_view, 'average_frequency') and tabular_view.average_frequency:
                                    rpm = tabular_view.average_frequency[channel_idx] if channel_idx < len(tabular_view.average_frequency) else 0
                                freq_hz = rpm / 60.0 if rpm > 0 else 0
                                
                                return freq_hz, one_x_amp, one_x_phase
        except Exception as e:
            # Only log the error if it's not the expected 'features' attribute error
            if "'features'" not in str(e):
                self.log_error(f"Error getting 1x data from tabular view: {str(e)}")
        return None, 0, 0

    def update_visible_plots(self):
        try:
            if not hasattr(self, 'plot_widgets') or not self.plot_widgets:
                return
                
            for ch_name in self.channel_names:
                widget_key = f"{ch_name}_widget"
                if widget_key in self.plot_widgets:
                    try:
                        visible = ch_name == self.selected_channel
                        self.plot_widgets[widget_key].setVisible(visible)
                        self.log_info(f"Set visibility for {widget_key}: {visible}")
                    except (KeyError, RuntimeError) as e:
                        if "wrapped C/C++ object" not in str(e):
                            self.log_error(f"Error updating {widget_key}: {str(e)}")
                        continue
                        
            if hasattr(self, 'error_label'):
                try:
                    if self.selected_channel:
                        self.error_label.setVisible(False)
                    else:
                        self.error_label.setText("Please select a channel")
                        self.error_label.setVisible(True)
                except RuntimeError:
                    pass
                    
            self.log_info(f"Updated visible plots for channel: {self.selected_channel}")
            
        except Exception as e:
            if "wrapped C/C++ object" not in str(e):
                self.log_error(f"Error in update_visible_plots: {str(e)}")


    def log_info(self, message):
        logging.info(message)
        if self.console:
            self.console.append_to_console(message)

    def log_error(self, message):
        logging.error(message)
        if self.console:
            self.console.append_to_console(message)
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    def on_data_received(self, feature_name, tag_name, model_name, values, sample_rate, frame_index):
        if self.model_name != model_name or self.tag_name != tag_name or feature_name != "Bode Plot":
            self.log_info(f"Ignoring data for feature: {feature_name}, tag: {tag_name}, model: {model_name}")
            return
        try:
            self.log_info(f"Received data: {len(values)} channels, sample_rate: {sample_rate}, frame_index: {frame_index}, first channel length: {len(values[0]) if values else 0}")

            expected_channels = len(self.channel_names) + 2  # Main channels + freq + trigger
            if len(values) < expected_channels:
                self.log_error(f"Invalid data: expected at least {expected_channels} channels (including freq and trigger), got {len(values)}")
                return

            main_data = values[:len(self.channel_names)]
            freq_data = values[len(self.channel_names)]
            trigger_data = values[len(self.channel_names) + 1]
            self.log_info(f"Main data channels: {len(main_data)}, Freq data length: {len(freq_data)}, Trigger data length: {len(trigger_data)}")

            if not self.selected_channel:
                self.selected_channel = self.channel_names[0] if self.channel_names else None
                self.log_info(f"No channel selected; defaulted to {self.selected_channel}")

            if self.selected_channel:
                ch_idx = self.channel_indices.get(self.selected_channel)
                if ch_idx is not None and ch_idx < len(main_data):
                    channel_data = [float(v) * self.scaling_factor for v in main_data[ch_idx]]
                    self.process_data(channel_data, freq_data, trigger_data, self.selected_channel)
                else:
                    self.log_error(f"Invalid channel index {ch_idx} for {self.selected_channel}")
            else:
                self.log_error("No valid channel selected for processing")
                return

            self.update_plots()
        except Exception as e:
            self.log_error(f"Error processing data: {str(e)}")

    def process_data(self, channel_data, frequency_data, trigger_data, channel_name):
        try:
            if not channel_data or not frequency_data:
                self.log_error(f"Empty data for {channel_name}: channel_data={len(channel_data)}, frequency_data={len(frequency_data)}")
                return
            
            min_length = min(len(channel_data), len(frequency_data))
            if min_length < 1:
                self.log_error(f"Data too short for {channel_name}: length={min_length}")
                return
                
            channel_data = channel_data[:min_length]
            frequency_data = [f for f in frequency_data[:min_length] if f > 0]
            trigger_data = trigger_data[:min_length] if trigger_data else [0] * min_length
            
            if not frequency_data:
                self.log_error(f"No valid frequencies for {channel_name}")
                return
                
            min_length = len(frequency_data)
            channel_data = channel_data[:min_length]
            trigger_data = trigger_data[:min_length]
            
            self.log_info(f"Processing {min_length} samples for {channel_name}")
            
            # Convert to numpy arrays for better numerical processing
            channel_data = np.array(channel_data, dtype=float)
            frequency_data = np.array(frequency_data, dtype=float)
            trigger_data = np.array(trigger_data, dtype=float)
            
            # Calculate amplitude (magnitude) and phase properly
            # For real signals, we need to handle the complex representation
            amplitudes = []
            phases = []
            valid_freqs = []
            
            for i, (v, f, t) in enumerate(zip(channel_data, frequency_data, trigger_data)):
                if f <= 0:
                    continue
                    
                # For magnitude: use absolute value and convert to dB
                # Add small epsilon to avoid log(0)
                magnitude_db = 20 * np.log10(abs(v) + 1e-10)
                
                # For phase: if we have trigger data, use it to determine phase
                # Otherwise, assume the signal represents a complex phasor
                if t != 0:
                    # Use trigger as phase reference
                    phase_deg = np.degrees(np.angle(complex(v, t)))
                else:
                    # For real signals, phase is 0 or 180 degrees based on sign
                    phase_deg = 0 if v >= 0 else 180
                
                # Normalize phase to [-180, 180] range
                phase_deg = ((phase_deg + 180) % 360) - 180
                
                valid_freqs.append(f)
                amplitudes.append(magnitude_db)
                phases.append(phase_deg)
            
            if not valid_freqs:
                self.log_error(f"No valid data points for {channel_name} after filtering")
                return
            
            # Convert to numpy arrays and sort by frequency
            valid_freqs = np.array(valid_freqs)
            amplitudes = np.array(amplitudes)
            phases = np.array(phases)
            
            sort_indices = np.argsort(valid_freqs)
            valid_freqs = valid_freqs[sort_indices]
            amplitudes = amplitudes[sort_indices]
            phases = phases[sort_indices]
            
            # Apply smoothing to reduce noise
            if len(valid_freqs) > 5:
                window_size = min(5, len(valid_freqs) // 3)
                amplitudes = self._smooth_data(amplitudes, window_size)
                phases = self._smooth_data(phases, window_size)
            
            # Store processed data
            self.data[channel_name]['frequencies'] = valid_freqs.tolist()
            self.data[channel_name]['amplitudes'] = amplitudes.tolist()
            self.data[channel_name]['phases'] = phases.tolist()
            
            self.log_info(f"Processed {len(valid_freqs)} data points for {channel_name}")
            
        except Exception as e:
            self.log_error(f"Error processing data for {channel_name}: {str(e)}")
    
    def _smooth_data(self, data, window_size):
        """Apply moving average smoothing to data"""
        if len(data) < window_size:
            return data
        
        smoothed = np.convolve(data, np.ones(window_size)/window_size, mode='same')
        return smoothed

    def update_plots(self):
        try:
            if not self.selected_channel:
                self.error_label.setText("Please select a channel")
                self.error_label.setVisible(True)
                for ch_name in self.channel_names:
                    if f"{ch_name}_amp" in self.plots:
                        self.plots[f"{ch_name}_amp"].set_data([], [])
                        self.plots[f"{ch_name}_phase"].set_data([], [])
                self.log_info("No channel selected; cleared all plots")
                return

            ch_name = self.selected_channel
            freq = np.array(self.data[ch_name]['frequencies'], dtype=float)
            amp = np.array(self.data[ch_name]['amplitudes'], dtype=float)
            phase = np.array(self.data[ch_name]['phases'], dtype=float)
            
            self.log_info(f"Updating plots for {ch_name}: {len(freq)} data points")

            self.update_visible_plots()

            if len(freq) == 0 or len(amp) == 0 or len(phase) == 0:
                if f"{ch_name}_amp" in self.plots:
                    self.plots[f"{ch_name}_amp"].set_data([], [])
                    self.plots[f"{ch_name}_phase"].set_data([], [])
                self.error_label.setText(f"No valid data available for {ch_name}")
                self.error_label.setVisible(True)
                self.log_info(f"No valid data for {ch_name}: freq={len(freq)}, amp={len(amp)}, phase={len(phase)}")
                return

            if not (len(freq) == len(amp) == len(phase)):
                self.log_error(f"Data length mismatch for {ch_name}: freq={len(freq)}, amp={len(amp)}, phase={len(phase)}")
                self.error_label.setText(f"Data length mismatch for {ch_name}")
                self.error_label.setVisible(True)
                return

            # Get matplotlib axes and lines
            ax_amp = self.plot_widgets.get(f"{ch_name}_ax_amp")
            ax_phase = self.plot_widgets.get(f"{ch_name}_ax_phase")
            canvas = self.plot_widgets.get(f"{ch_name}_canvas")
            
            if not all([ax_amp, ax_phase, canvas]):
                self.log_error(f"Missing matplotlib components for {ch_name}")
                return
            
            # Update amplitude plot
            amp_line = self.plots.get(f"{ch_name}_amp")
            if amp_line:
                amp_line.set_data(freq, amp)
                
                # Update amplitude axis limits
                if len(freq) > 0:
                    ax_amp.set_xlim(min(freq) * 0.9, max(freq) * 1.1)
                    y_min, y_max = min(amp) - 10, max(amp) + 10
                    ax_amp.set_ylim(y_min, y_max)
            
            # Update phase plot
            phase_line = self.plots.get(f"{ch_name}_phase")
            if phase_line:
                phase_line.set_data(freq, phase)
                
                # Update phase axis limits
                if len(freq) > 0:
                    ax_phase.set_xlim(min(freq) * 0.9, max(freq) * 1.1)
                    ax_phase.set_ylim(-180, 180)
            
            # Get 1x data from tabular view and update scatter plots
            freq_1x, one_x_amp, one_x_phase = self.get_1x_data_from_tabular(ch_name)
            
            # Update 1x amplitude point
            if freq_1x and freq_1x > 0:
                amp_1x_scatter = self.plots.get(f"{ch_name}_amp_1x")
                if amp_1x_scatter:
                    amp_1x_scatter.set_offsets([[freq_1x, one_x_amp]])
            
            # Update 1x phase point
            if freq_1x and freq_1x > 0:
                phase_1x_scatter = self.plots.get(f"{ch_name}_phase_1x")
                if phase_1x_scatter:
                    phase_1x_scatter.set_offsets([[freq_1x, one_x_phase]])
            
            # Redraw canvas
            canvas.draw()
            
            self.error_label.setVisible(False)
            
        except Exception as e:
            self.log_error(f"Error updating plots: {str(e)}")
            self.error_label.setText(f"Plotting error for {ch_name}: {str(e)}")
            self.error_label.setVisible(True)

    def process_historical_data(self, filename, frame_index):
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            client = MongoClient("mongodb://localhost:27017")
            database = client["changed_db"]
            history_collection = database["timeview_messages"]

            query = {
                "project_name": self.project_name,
                "model_name": self.model_name,
                "topic": self.tag_name,
                "filename": filename
            }
            total_frames = history_collection.count_documents(query)
            self.log_info(f"Found {total_frames} frames for filename: {filename}")

            if total_frames == 0:
                self.log_error(f"No historical data found for filename: {filename}")
                self.progress_bar.setVisible(False)
                return

            if self.selected_channel:
                self.data[self.selected_channel] = {'frequencies': [], 'amplitudes': [], 'phases': []}
            else:
                for ch_name in self.channel_names:
                    self.data[ch_name] = {'frequencies': [], 'amplitudes': [], 'phases': []}

            max_frames = 1500
            batch_size = 50
            sampling_interval = max(1, total_frames // max_frames)
            processed_count = 0
            cursor = history_collection.find(query).sort("frameIndex", 1)

            for history_data in cursor:
                if processed_count % sampling_interval != 0:
                    processed_count += 1
                    continue
                if not self.is_valid_history_data(history_data):
                    processed_count += 1
                    continue

                main_channels = history_data.get("numberOfChannels", 0)
                samples_per_channel = history_data.get("samplingSize", 0)
                tacho_channels = history_data.get("tacoChannelCount", 0)
                freq_start_idx = main_channels * samples_per_channel
                trigger_start_idx = freq_start_idx + samples_per_channel

                if self.selected_channel:
                    ch_idx = self.channel_indices.get(self.selected_channel)
                    if ch_idx is not None and ch_idx < main_channels:
                        channel_data = [history_data["message"][i * main_channels + ch_idx] * self.scaling_factor
                                       for i in range(samples_per_channel)]
                        freq_data = [history_data["message"][freq_start_idx + i]
                                     for i in range(samples_per_channel) if freq_start_idx + i < len(history_data["message"])]
                        trigger_data = [history_data["message"][trigger_start_idx + i]
                                        for i in range(samples_per_channel) if trigger_start_idx + i < len(history_data["message"])]
                        self.log_info(f"Processing historical data for {self.selected_channel}: {len(channel_data)} samples")
                        self.process_data(channel_data, freq_data, trigger_data, self.selected_channel)
                    else:
                        self.log_error(f"Invalid channel index {ch_idx} for {self.selected_channel}")
                else:
                    for ch_idx, ch_name in enumerate(self.channel_names):
                        if ch_idx >= main_channels:
                            continue
                        channel_data = [history_data["message"][i * main_channels + ch_idx] * self.scaling_factor
                                       for i in range(samples_per_channel)]
                        freq_data = [history_data["message"][freq_start_idx + i]
                                     for i in range(samples_per_channel) if freq_start_idx + i < len(history_data["message"])]
                        trigger_data = [history_data["message"][trigger_start_idx + i]
                                        for i in range(samples_per_channel) if trigger_start_idx + i < len(history_data["message"])]
                        self.log_info(f"Processing historical data for {ch_name}: {len(channel_data)} samples")
                        self.process_data(channel_data, freq_data, trigger_data, ch_name)

                processed_count += 1
                self.progress_bar.setValue(int((processed_count / total_frames) * 100))
                if processed_count % batch_size == 0:
                    self.update_plots()

            self.update_plots()
            self.progress_bar.setVisible(False)
            self.log_info(f"Processed {processed_count}/{total_frames} frames for {filename}")
            client.close()
        except Exception as e:
            self.log_error(f"Error processing historical data: {str(e)}")
            self.progress_bar.setVisible(False)

    def is_valid_history_data(self, history_data):
        try:
            main_channels = history_data.get("numberOfChannels", 0)
            samples_per_channel = history_data.get("samplingSize", 0)
            tacho_channels = history_data.get("tacoChannelCount", 0)
            message = history_data.get("message", [])
            valid = (main_channels > 0 and
                     samples_per_channel > 0 and
                     len(message) >= (main_channels + tacho_channels) * samples_per_channel)
            if not valid:
                self.log_error(f"Invalid history data: channels={main_channels}, samples={samples_per_channel}, message_len={len(message)}")
            return valid
        except Exception as e:
            self.log_error(f"Error validating history data: {str(e)}")
            return False

    def get_widget(self):
        return self.widget

    def cleanup(self):
        self.update_timer.stop()
        for ch_name in self.channel_names:
            self.data[ch_name].clear()
        self.plots.clear()
        self.plot_widgets.clear()
        self.log_info("Cleaned up BodePlotFeature")