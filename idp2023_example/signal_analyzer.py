import pandas as pd
import numpy as np
import time
from PySide6.QtCore import Signal
from scipy.signal import butter, filtfilt


class SignalAnalyzer:
    """
    A "signal analyzer" that just generates an array of cosine function values.

    Instances of this class are intended to be run from a worker thread. Data
    is emitted through callbacks back to the parent thread.
    """

    def __init__(self, csv_file_path, sample_rate=50000, duration_seconds=120):
        self.running = False
        self.csv_file_path = csv_file_path
        self.sample_rate = sample_rate
        self.duration_seconds = duration_seconds
        self.window_size = 50000  # We'll display a sliding window of 50,000 samples (1 second worth of data at 50kHz)
        self.x = 0  # To track the current index in the data
        self.data = None
        self.x_array = np.zeros((self.window_size,))
        self.y1_array = np.zeros_like(self.x_array)  # Sensor 1 (adc1) data
        self.y2_array = np.zeros_like(self.x_array)  # Sensor 2 (adc2) data

        # Number of rows to read (1 minute of data -> one second is 50k samples and 2 min is 6 million samples)
        self.num_rows_to_read = sample_rate * duration_seconds

        # Read the CSV file
        self.load_csv_data()

    def load_csv_data(self):
        try:
            # At first, we are just reading only the first 6 million rows
            df = pd.read_csv(self.csv_file_path, nrows=self.num_rows_to_read)
            # adc1 and adc2 columns represent sensor data
            self.data = df[['adc1', 'adc2']].to_numpy()
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            self.data = None

    # Polynomial fitting algorithm for baseline removal
    def remove_baseline(self, data, **kwargs):
        degree = kwargs.get('degree', 2)
        x = np.arange(len(data))
        coeffs = np.polyfit(x, data, degree)
        baseline = np.polyval(coeffs, x)
        return data - baseline

    # Downsamples the data to a specified number of points using averaging.
    def downsample(self, x, y, num_points):
        factor = len(x) // num_points
        x_downsampled = x[:factor * num_points].reshape(-1, factor).mean(axis=1)
        y_downsampled = y[:factor * num_points].reshape(-1, factor).mean(axis=1)
        return x_downsampled, y_downsampled

    # Returns smoothed version of data using moving average.
    # Adjust the window parameter to determine how many datapoints are used
    # when calculating the average.
    def calculate_moving_average(self, data, window_size):
        if len(data) < window_size:
            return
        # We start counting averages only from the end of the original window.
        # The beginning of averaged signal remains the same
        averaged = data[:window_size-1]
        i = window_size
        while i < len(data):
            start_index = i-window_size
            averaged[i] = np.mean(data[start_index:i])
            i += 1
        return averaged

    def _generate_data_array(self) -> None:
        if self.data is None:
            return

        # Process the entire data
        self.x_array = np.arange(len(self.data))
        self.y1_array = self.data[:, 0]
        self.y2_array = self.data[:, 1]

        # baseline removal
        self.y1_array = self.remove_baseline(self.y1_array, degree=2)
        self.y2_array = self.remove_baseline(self.y2_array, degree=2)

        # Downsample the data
        num_points = 5000
        self.x_array_downsampled, self.y1_array_downsampled = self.downsample(self.x_array, self.y1_array, num_points)
        _, self.y2_array_downsampled = self.downsample(self.x_array, self.y2_array, num_points)

    def _start(self, set_axis_y=None):
        """
        Tasks that should be done before starting the main loop of SignalAnalyzer.
        """
        self.running = True
        if set_axis_y:
            min_y = min(self.y1_array.min(), self.y2_array.min())
            max_y = max(self.y1_array.max(), self.y2_array.max())
            set_axis_y.emit(float(min_y), float(max_y))

    def stop(self):
        """
        Stops the main loop.
        """
        self.running = False

    def start(
        self,
        set_chart_axis_y: Signal | None = None,
        update_chart: Signal | None = None,
        progress_callback: Signal | None = None,
    ):
        self._start(set_chart_axis_y)
        self._generate_data_array()

        # Update the chart with downsampled data
        if update_chart:
            # Emit baseline-removed data
            update_chart.emit("Sensor 1 - Baseline Removed", self.x_array_downsampled, self.y1_array_downsampled)
            update_chart.emit("Sensor 2 - Baseline Removed", self.x_array_downsampled, self.y2_array_downsampled)

        if progress_callback:
            progress_callback.emit(100)