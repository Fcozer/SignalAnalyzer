import pandas as pd
import numpy as np
from PySide6.QtCore import Signal

from idp2023_example.signal_analyzer import SignalAnalyzer


class DataReader:
    """
    This class reads the given CSV file of signal data in predetermined chunks of size (rows_to_skip) into
    a pandas DataFrame, transforms the signals with SignalAnalyzer class and returns the resulting DataFrame.

    """
    def __init__(self, csv_file_path, rows_to_skip, window):
        self.running = False
        self.csv_file_path = csv_file_path
        self.rows_to_skip = rows_to_skip
        self.total_rows_skipped = rows_to_skip
        self.window = window
        self.x_axis = list(np.arange(self.total_rows_skipped))
        self.first_data_chunk = self.get_first_data_chunk()
        self.current_data_chunk = self.first_data_chunk
        self.output_csv_filename = 'detections.csv'

    def write_output_csv(self, dataframe):
        output_data = dataframe.filter(items=['timedelta', 'peak'])
        print(output_data.head())

    def get_first_data_chunk(self):
        self.first_data_chunk = pd.read_csv(self.csv_file_path, nrows=self.rows_to_skip)
        self.first_data_chunk['x_axis'] = self.x_axis
        self.first_data_chunk['timedelta'] = pd.to_timedelta(self.first_data_chunk['x_axis']/50, unit='ms')
        # Use signal analyzer class for transforming dataframe contents
        signal_analyzer = SignalAnalyzer(self.first_data_chunk)
        self.first_data_chunk = signal_analyzer.transform_data()
        self.write_output_csv(self.first_data_chunk)
        return self.first_data_chunk

    def get_signals_from_data_chunk(self):
        self.current_data_chunk = pd.read_csv(self.csv_file_path,
                                              skiprows=self.total_rows_skipped,
                                              nrows=self.rows_to_skip,
                                              names=['adc1', 'adc2'],
                                              header=None)
        self.total_rows_skipped = self.total_rows_skipped+self.rows_to_skip
        # X-axis should start to move when window size is reached
        if len(self.x_axis) < self.window:
            self.x_axis = list(np.arange(self.total_rows_skipped-self.rows_to_skip, self.total_rows_skipped))
            self.current_data_chunk['x_axis'] = self.x_axis
            self.current_data_chunk['timedelta'] = pd.to_timedelta(self.current_data_chunk['x_axis']/50, unit='ms')
        else:
            start = self.total_rows_skipped-self.window-self.rows_to_skip
            self.x_axis = list(np.arange(start, self.total_rows_skipped))
            self.current_data_chunk['x_axis'] = self.x_axis
            self.current_data_chunk['timedelta'] = pd.to_timedelta(self.current_data_chunk['x_axis']/50, unit='ms')

        # Use signal analyzer class for transforming dataframe contents
        signal_analyzer = SignalAnalyzer(self.current_data_chunk)
        self.current_data_chunk = signal_analyzer.transform_data()

        return self.current_data_chunk

    def _start(self, set_axis_y=None):
        """
        Tasks that should be done before starting the main loop of DataReader.
        """
        self.running = True
        if set_axis_y:
            min_y = min(self.current_data_chunk['adc1'].min(), self.current_data_chunk['adc2'].min())
            max_y = max(self.current_data_chunk['adc1'].max(), self.current_data_chunk['adc2'].max())
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
        while self.running:
            self.get_signals_from_data_chunk()
            # Update the chart with downsampled data
            if update_chart:
                # Emit baseline-removed data
                update_chart.emit("Sensor 1 - Baseline Removed",
                                  self.current_data_chunk['x_axis'],
                                  self.current_data_chunk['adc1'],
                                  1) # Signal identity number, adc1
                update_chart.emit("Sensor 2 - Baseline Removed",
                                  self.current_data_chunk['x_axis'],
                                  self.current_data_chunk['adc2'],
                                  2)

        if progress_callback:
            progress_callback.emit(100)