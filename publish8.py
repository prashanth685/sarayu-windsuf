# # import math
# # import struct
# # import paho.mqtt.publish as publish
# # from PyQt5.QtCore import QTimer, QObject
# # from PyQt5.QtWidgets import QApplication
# # import logging

# # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# # class MQTTPublisher(QObject):
# #     def __init__(self, broker, topics):
# #         super().__init__()
# #         self.broker = broker
# #         self.topics = topics if isinstance(topics, list) else [topics]
# #         self.count = 1

# #         self.frequency =  500 # Hz
# #         self.amplitude = 1.5  # Reduced amplitude for clarity (0-3.3V range)
# #         self.amplitude_scaled = (self.amplitude*0.5) / (3.3 / 65535)  # Scale for 16-bit ADC
# #         self.offset = 32768  # Midpoint for 16-bit unsigned (0-65535)
# #         self.sample_rate = 4096  # Samples per second
# #         self.time_per_message = 1.0  # 1 second for 4096 samples
# #         self.current_time = 0.0
# #         self.num_channels = 4 # Main channels
# #         self.samples_per_channel = 4096  # Samples per channel
# #         self.num_tacho_channels = 2  # Tacho freq + tacho trigger
# #         self.frame_index = 0

# #         self.timer = QTimer(self)
# #         self.timer.timeout.connect(self.publish_message)
# #         self.timer.start(1000)  # Publish every 1 second
# #         logging.debug(f"Initialized MQTTPublisher with broker: {self.broker}, topics: {self.topics}")

# #     def publish_message(self):
# #         try:
# #             # Generate sine wave samples for all main channels
# #             all_channel_data = []
# #             for i in range(self.samples_per_channel):
# #                 t = self.current_time + (i / self.sample_rate)
# #                 base_value = self.offset + self.amplitude_scaled * math.sin(2 * math.pi * self.frequency * t)
# #                 rounded_value = int(round(base_value))
# #                 all_channel_data.append(rounded_value)

# #             self.current_time += self.time_per_message

# #             # Interleave channel data (16384 = 4096 samples * 4 channels)
# #             interleaved = []
# #             for i in range(self.samples_per_channel):
# #                 for ch in range(self.num_channels):
# #                     interleaved.append(all_channel_data[i])  # Same data for all channels

# #             if len(interleaved) != self.samples_per_channel * self.num_channels:
# #                 logging.error(f"Interleaved data length incorrect: expected {self.samples_per_channel * self.num_channels}, got {len(interleaved)}")
# #                 return

# #             # Generate tacho frequency data (4096 samples, constant frequency)
# #             tacho_freq_data = [self.frequency] * self.samples_per_channel

# #             # Generate tacho trigger data (10 pulses at 1.0)
# #             tacho_trigger_data = [0] * self.samples_per_channel
# #             num_triggers = self.frequency  # 10 triggers per second
# #             step = self.samples_per_channel // num_triggers  # ~409 samples apart
# #             for i in range(num_triggers):
# #                 index = i * step
# #                 if index < self.samples_per_channel:
# #                     tacho_trigger_data[index] = 1  # Pulse at 1.0

# #             # Build header
# #             header = [
# #                 self.frame_index % 65535,  # Frame index low
# #                 self.frame_index // 65535,  # Frame index high
# #                 self.num_channels,         # Number of channels (4)header[2]
# #                 self.sample_rate,          # Sample rate (4096)
# #                 4096,                        # Bit depth
# #                 self.samples_per_channel,  # Samples per channel (4096)
# #                 self.num_tacho_channels,   # Number of tacho channels (2)header[6]
# #                 0, 0, 0                   # Reserved
# #             ]
# #             while len(header) < 100:
# #                 header.append(0)

# #             # Combine all data
# #             message_values = header + interleaved + tacho_freq_data + tacho_trigger_data
# #             total_expected = 100 + (self.samples_per_channel * self.num_channels) + (self.samples_per_channel * self.num_tacho_channels)
# #             if len(message_values) != total_expected:
# #                 logging.error(f"Message length incorrect: expected {total_expected}, got {len(message_values)}")
# #                 return

# #             # Log sample data for debugging
# #             logging.debug(f"Header: {header}")
# #             logging.debug(f"Main channel data (first 5): {interleaved[:5]}")
# #             logging.debug(f"Tacho freq data (first 5): {tacho_freq_data[:5]}")
# #             logging.debug(f"Tacho trigger data (first 20): {tacho_trigger_data[:20]}")

# #             # Convert to binary
# #             binary_message = struct.pack(f"<{len(message_values)}H", *message_values)

# #             # Publish to all topics
# #             for topic in self.topics:
# #                 try:
# #                     publish.single(topic, binary_message, hostname=self.broker, qos=1)
# #                     logging.info(f"[{self.count}] Published to {topic}: frame {self.frame_index}, {len(message_values)} values")
# #                 except Exception as e:
# #                     logging.error(f"Failed to publish to {topic}: {str(e)}")

# #             self.frame_index += 1
# #             self.count += 1
# #         except Exception as e:
# #             logging.error(f"Error in publish_message: {str(e)}")

# # if __name__ == "__main__":
# #     app = QApplication([])
# #     broker = "192.168.1.231"
# #     topics = ["sarayu/d1/topic1"]
# #     mqtt_publisher = MQTTPublisher(broker, topics)
# #     app.exec_()

# import math
# import struct
# import paho.mqtt.publish as publish
# from PyQt5.QtCore import QTimer, QObject
# from PyQt5.QtWidgets import QApplication
# import logging

# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s - %(levelname)s - %(message)s')


# class MQTTPublisher(QObject):
#     def __init__(self, broker, topics):
#         super().__init__()
#         self.broker = broker
#         self.topics = topics if isinstance(topics, list) else [topics]

#         # Internal frame counter
#         self.frame_counter = 1

#         # Frequency sweep
#         self.freq_start = 1
#         self.freq_end = 500
#         self.freq_step = 1
#         self.frequency = self.freq_start
#         self.sweep_direction = 1

#         # Signal parameters
#         self.amplitude = 1.0
#         self.offset = 32768
#         self.sample_rate = 4096
#         self.samples_per_channel = 4096
#         self.time_per_message = 0.5
#         self.current_time = 0.0

#         # Channels
#         self.num_signal_channels = 10   # 6 + 4
#         self.num_tacho_channels = 2

#         # Timer → 0.5 s
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.publish_message)
#         self.timer.start(500)

#         logging.info("MQTT Publisher running")

#     def publish_message(self):
#         try:
#             # ----- Decide header frame value -----
#             # Odd frame → 1 1, Even frame → 2 2
#             if self.frame_counter % 2 == 1:
#                 header_frame = 1
#             else:
#                 header_frame = 2

#             # ----- Frequency sweep -----
#             self.frequency += self.freq_step * self.sweep_direction
#             if self.frequency >= self.freq_end:
#                 self.frequency = self.freq_end
#                 self.sweep_direction = -1
#             elif self.frequency <= self.freq_start:
#                 self.frequency = self.freq_start
#                 self.sweep_direction = 1

#             amplitude_scaled = (self.amplitude * 0.5) / (3.3 / 65535)

#             # ----- Generate base sine -----
#             base_data = []
#             for i in range(self.samples_per_channel):
#                 t = self.current_time + (i / self.sample_rate)
#                 value = self.offset + amplitude_scaled * math.sin(
#                     2 * math.pi * self.frequency * t
#                 )
#                 base_data.append(int(round(value)))

#             self.current_time += self.time_per_message

#             # ----- Interleave 6 + 4 -----
#             interleaved = []
#             for i in range(self.samples_per_channel):
#                 for _ in range(6):
#                     interleaved.append(base_data[i])
#                 for _ in range(4):
#                     interleaved.append(base_data[i])

#             # ----- Tacho channels -----
#             tacho_freq = [int(self.frequency)] * self.samples_per_channel
#             tacho_trigger = [0] * self.samples_per_channel

#             triggers = int(self.frequency)
#             if triggers > 0:
#                 step = self.samples_per_channel // triggers
#                 for i in range(triggers):
#                     idx = i * step
#                     if idx < self.samples_per_channel:
#                         tacho_trigger[idx] = 1

#             # ----- Header -----
#             header = [
#                 header_frame,              # header[0]
#                 header_frame,              # header[1]
#                 self.num_signal_channels,
#                 self.sample_rate,
#                 4096,
#                 self.samples_per_channel,
#                 self.num_tacho_channels,
#                 0, 0, 0
#             ]

#             while len(header) < 100:
#                 header.append(0)

#             # ----- Build message -----
#             message = (
#                 header +
#                 interleaved +
#                 tacho_freq +
#                 tacho_trigger
#             )

#             expected_len = (
#                 100 +
#                 self.samples_per_channel * self.num_signal_channels +
#                 self.samples_per_channel * self.num_tacho_channels
#             )

#             if len(message) != expected_len:
#                 logging.error(f"Length mismatch {len(message)} != {expected_len}")
#                 return

#             # ----- Pack & publish -----
#             binary = struct.pack(f"<{len(message)}H", *message)

#             for topic in self.topics:
#                 publish.single(topic, binary, hostname=self.broker, qos=1)

#             logging.info(
#                 f"Published frame_counter={self.frame_counter}, "
#                 f"header={header_frame} {header_frame}, "
#                 f"freq={self.frequency} Hz"
#             )

#             self.frame_counter += 1

#         except Exception as e:
#             logging.error(f"Publish error: {e}")


# if __name__ == "__main__":
#     app = QApplication([])

#     broker = "192.168.1.231"
#     topics = ["sarayu/d1/topic1"]

#     publisher = MQTTPublisher(broker, topics)
#     app.exec_()

import math
import struct
import paho.mqtt.publish as publish
from PyQt5.QtCore import QTimer, QObject
from PyQt5.QtWidgets import QApplication
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class MQTTPublisher(QObject):
    def __init__(self, broker, topics):
        super().__init__()
        self.broker = broker
        self.topics = topics if isinstance(topics, list) else [topics]

        # Fixed frequencies (NO SWEEP)
        self.signal_frequency = 20
        self.tacho_fixed_freq = 10

        # Signal parameters
        self.amplitude = 1.0
        self.offset = 32768
        self.sample_rate = 4096
        self.samples_per_channel = 4096
        self.time_per_message = 0.5
        self.current_time = 0.0

        # Channels
        self.num_signal_channels = 10   # 6 + 4
        self.num_tacho_channels = 2

        # Timer → 0.5 s
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.publish_message)
        self.timer.start(500)

        logging.info("MQTT Publisher running (NO SWEEP)")


    def publish_message(self):
        try:
            # ----- Header frame: always 10 10 -----
            header_frame = 10

            amplitude_scaled = (self.amplitude * 0.5) / (3.3 / 65535)

            # ----- Generate base sine (FIXED frequency) -----
            base_data = []
            for i in range(self.samples_per_channel):
                t = self.current_time + (i / self.sample_rate)
                value = self.offset + amplitude_scaled * math.sin(
                    2 * math.pi * self.signal_frequency * t
                )
                base_data.append(int(round(value)))

            self.current_time += self.time_per_message

            # ----- Interleave 6 + 4 -----
            interleaved = []
            for i in range(self.samples_per_channel):
                for _ in range(6):
                    interleaved.append(base_data[i])
                for _ in range(4):
                    interleaved.append(base_data[i])

            # ----- Tacho channels (FIXED frequency) -----
            tacho_freq = [self.tacho_fixed_freq] * self.samples_per_channel
            tacho_trigger = [0] * self.samples_per_channel

            triggers = self.tacho_fixed_freq
            if triggers > 0:
                step = self.samples_per_channel // triggers
                for i in range(triggers):
                    idx = i * step
                    if idx < self.samples_per_channel:
                        tacho_trigger[idx] = 1

            # ----- Header -----
            header = [
                header_frame,
                header_frame,
                self.num_signal_channels,
                self.sample_rate,
                4096,
                self.samples_per_channel,
                self.num_tacho_channels,
                0, 0, 0
            ]

            while len(header) < 100:
                header.append(0)

            # ----- Build message -----
            message = (
                header +
                interleaved +
                tacho_freq +
                tacho_trigger
            )

            expected_len = (
                100 +
                self.samples_per_channel * self.num_signal_channels +
                self.samples_per_channel * self.num_tacho_channels
            )

            if len(message) != expected_len:
                logging.error(f"Length mismatch {len(message)} != {expected_len}")
                return

            # ----- Pack & publish -----
            binary = struct.pack(f"<{len(message)}H", *message)

            for topic in self.topics:
                publish.single(topic, binary, hostname=self.broker, qos=1)

            logging.info(
                f"Published header=10 10, "
                f"signal_freq={self.signal_frequency} Hz, "
                f"tacho_freq={self.tacho_fixed_freq}"
            )

        except Exception as e:
            logging.error(f"Publish error: {e}")


if __name__ == "__main__":
    app = QApplication([])

    broker = "192.168.1.231"
    topics = ["sarayu/d1/topic1"]

    publisher = MQTTPublisher(broker, topics)
    app.exec_()
