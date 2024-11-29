import numpy as np
from PySide6.QtCore import QThreadPool, Signal, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from idp2023_example.signal_analyzer import SignalAnalyzer
from idp2023_example.signal_window_chart_widget import SignalWindowChartWidget
from idp2023_example.worker import Worker


class SignalAppWidget(QWidget):
    chart_set_axis_y = Signal(float, float)
    chart_update_data = Signal(str, np.ndarray, np.ndarray)
    chart_update_peaks = Signal(str, np.ndarray, np.ndarray)
    chart_update_peak_counts = Signal(int, int, int)

    def __init__(self):
        super().__init__()

        self.signal_window_chart = SignalWindowChartWidget()

        self.chart_set_axis_y.connect(self.signal_window_chart.set_axis_y)
        self.chart_update_data.connect(self.signal_window_chart.replace_array)
        self.chart_update_peaks.connect(self.signal_window_chart.add_peak_markers)
        self.chart_update_peak_counts.connect(self.signal_window_chart.update_peak_counts)

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")

        self.start_button.pressed.connect(self.start_signal_analyser)
        self.stop_button.pressed.connect(self.stop_signal_analyser)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        self.layout.addWidget(self.signal_window_chart)

        self.threadpool = QThreadPool()
        self.signal_analyzer = SignalAnalyzer("../group4.csv")

    def start_signal_analyser(self):
        worker = Worker(
            self.signal_analyzer.start,
            set_chart_axis_y=self.chart_set_axis_y,
            update_chart=self.chart_update_data,
            update_chart_peaks=self.chart_update_peaks,
            update_peak_counts=self.chart_update_peak_counts
        )
        worker.signals.result.connect(self.print_output)
        worker.signals.error.connect(self.handle_worker_error)
        self.threadpool.start(worker)

    def print_output(self, data):
        print("Data sent to chart:", data)

    def handle_worker_error(self, error):
        exctype, value, traceback_str = error
        print(f"Error in worker thread: {value}")
        print(traceback_str)

    @Slot()
    def stop_signal_analyser(self):
        self.signal_analyzer.stop()