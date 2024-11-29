import pandas as pd
import numpy as np
from PySide6.QtCore import Signal
from scipy.signal import find_peaks
from idp2023_example.peak_counter import PeakCounter

class SignalAnalyzer:
    update_chart_peaks = Signal(str, np.ndarray, np.ndarray)

    def __init__(self, csv_file_path, sample_rate=50000, duration_seconds=120):
        self.running = False
        self.csv_file_path = csv_file_path
        self.sample_rate = sample_rate
        self.duration_seconds = duration_seconds
        self.window_size = sample_rate * 10  # 10 sekuntia dataa
        self.x_array = np.zeros((self.window_size,))
        self.y1_array = np.zeros_like(self.x_array)  # Sensor 1 data
        self.y2_array = np.zeros_like(self.x_array)  # Sensor 2 data
        self.x_array_downsampled = None
        self.y1_array_downsampled = None
        self.peaks_y1 = None
        self.peak_counter = PeakCounter()

        self.load_csv_data()

    def load_csv_data(self):
        try:
            df = pd.read_csv(self.csv_file_path)
            self.data = df[['adc1', 'adc2']].to_numpy()
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            self.data = None

    def write_result_csv(self):
        # Make a starting dataframe with all times and their labels
        labels = np.full_like(self.x_array_downsampled, 'water', dtype=object)
        labels[self.peaks_y1] = 'tissue'
        dataframe = pd.DataFrame().from_dict(
            {'time': self.x_array_downsampled,
             'label': labels})
        # Group by label and duration time
        dataframe['group'] = (dataframe['label'] != dataframe['label'].shift()).cumsum()
        result = (dataframe.groupby(['group', 'label'])
                  .agg(startTime=('time', 'first'),
                       endTime=('time', 'last'))
                  .reset_index())
        # Format result dataframe to follow specs given on ELearn
        result = result.drop(columns='group')
        result['startTime'] = result['startTime'].apply(lambda x: "{:.5f}".format(x))
        result['endTime'] = result['endTime'].apply(lambda x: "{:.5f}".format(x))
        result = result[['startTime', 'endTime', 'label']]

        result.to_csv('detections.csv', index=False)

    def downsample(self, x, y, num_points):
        factor = len(x) // num_points
        x_downsampled = x[:factor * num_points].reshape(-1, factor).mean(axis=1)
        y_downsampled = y[:factor * num_points].reshape(-1, factor).mean(axis=1)
        return x_downsampled, y_downsampled

    def baseline_removal(self, y):
        window_size = 1000
        baseline = np.convolve(y, np.ones(window_size)/window_size, mode='same')
        corrected_signal = y - baseline
        corrected_signal[corrected_signal < 0] = 0
        return corrected_signal

    def _generate_data_array(self):
        if self.data is None:
            return
        self.x_array = np.arange(len(self.data))/50000
        self.y1_array = self.baseline_removal(self.data[:, 0])
        self.y2_array = self.baseline_removal(self.data[:, 1])
        num_points = 5000
        self.x_array_downsampled, self.y1_array_downsampled = self.downsample(self.x_array, self.y1_array, num_points)
        _, self.y2_array_downsampled = self.downsample(self.x_array, self.y2_array, num_points)

    def start(self,
              set_chart_axis_y=None,
              update_chart=None,
              update_chart_peaks=None,
              update_peak_counts=None,
              progress_callback=None):
        self.running = True
        self._generate_data_array()

        if update_chart:
            update_chart.emit("Sensor 1", self.x_array_downsampled, self.y1_array_downsampled)

        if set_chart_axis_y:
            set_chart_axis_y.emit(float(self.y1_array_downsampled.min()), float(self.y1_array_downsampled.max()))

        self.detect_and_classify_peaks(update_chart_peaks)

        if update_peak_counts:
            update_peak_counts.emit(
                self.peak_counter.large_peaks,
                self.peak_counter.medium_peaks,
                self.peak_counter.small_peaks
            )

        print('Writing output CSV...')
        self.write_result_csv()

        if progress_callback:
            progress_callback.emit(100)

    def detect_and_classify_peaks(self, update_chart_peaks=None):
        normalized_y1 = self.y1_array_downsampled / np.max(self.y1_array_downsampled)

        self.peaks_y1, properties = find_peaks(
            normalized_y1,
            height=0.015 * np.max(normalized_y1),
            prominence=0.015,
            distance=2
        )

        peak_x_y1 = self.x_array_downsampled[self.peaks_y1]
        peak_y_y1 = self.y1_array_downsampled[self.peaks_y1]
        peak_heights_y1 = properties['peak_heights']

        peaks_data = np.column_stack((peak_x_y1, peak_y_y1, peak_heights_y1))

        if update_chart_peaks:
            update_chart_peaks.emit("Sensor 1", peak_x_y1, peaks_data)

        self.peak_counter.count_peaks(peak_heights_y1)

    def stop(self):
        self.running = False