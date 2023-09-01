import sys
import numpy as np
import sounddevice as sd
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PyQt5.QtCore import QTimer
from pydub import AudioSegment

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 400
FPS = 30

class SystemAudioVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a PyQTGraph PlotWidget
        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)

        # Set window properties
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowTitle('System Audio Visualizer')

        # Create a plot curve
        self.curve = self.plot_widget.plot(pen=pg.mkPen('b', width=2))

        # Initialize the timer for updating the plot
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_audio)
        self.timer.start(int(1000 / FPS))  # Convert to integer

        # Initialize the audio stream
        self.audio_stream = sd.InputStream(callback=self.audio_callback)

    def audio_callback(self, indata, frames, time, status):
        if status:
            print('Audio callback status:', status)
        if any(indata):
            self.curve.setData(indata)

    def update_plot(self):
        pass  # Plot is updated through the audio callback

class AudioVisualizerApp(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.visualizer = SystemAudioVisualizer()
        self.visualizer.show()

        # Create a button to open the audio file dialog
        self.open_audio_button = QPushButton('Open Audio File')
        self.open_audio_button.clicked.connect(self.open_audio_file)

        # Create a layout for the button
        layout = QVBoxLayout()
        layout.addWidget(self.visualizer.plot_widget)
        layout.addWidget(self.open_audio_button)

        # Create a central widget to hold the layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.visualizer.setCentralWidget(central_widget)

        self.selected_audio_file = None

    def open_audio_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(
            self.visualizer,
            "Open Audio File",
            "",
            "Audio Files (*.wav *.mp3);;All Files (*)",
            options=options
        )

        if file_path:
            self.selected_audio_file = file_path
            self.visualizer.setWindowTitle(f'System Audio Visualizer - {self.selected_audio_file}')

            self.audio_data = AudioSegment.from_file(self.selected_audio_file)
            self.audio_data = np.array(self.audio_data.get_array_of_samples())
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_audio)
            self.timer.start(1000 / FPS)

    def update_audio(self):
        if self.selected_audio_file:
            audio_chunk_size = int(len(self.audio_data) / (WINDOW_WIDTH * 2))  # Adjust for plot width
            chunk_start = int(self.visualizer.curve.xData[-1] * len(self.audio_data))
            chunk_end = chunk_start + audio_chunk_size
            if chunk_end >= len(self.audio_data):
                chunk_end = len(self.audio_data) - 1
            audio_chunk = self.audio_data[chunk_start:chunk_end]
            sd.play(audio_chunk, samplerate=44100, blocking=False)

if __name__ == '__main__':
    app = AudioVisualizerApp()
    sys.exit(app.exec_())
