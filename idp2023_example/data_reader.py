import pandas as pd
import numpy as np
from idp2023_example.signal_analyzer import SignalAnalyzer

class DataReader:
    def __init__(self, csv_file_path, rows_to_skip):
        self.csv_file_path = csv_file_path
        self.rows_to_skip = rows_to_skip
        self.total_rows_skipped = rows_to_skip
        self.first_data_chunk = pd.read_csv(csv_file_path, nrows=rows_to_skip)
        self.current_data_chunk = self.first_data_chunk
        self.x_axis = list(np.arange(self.rows_to_skip))
        self.signal_analyzer = SignalAnalyzer(self) # Signal analyzer needs to be rewritten

    def getSignalsFromDataChunk(self):
        # We will take 10000 rows at a time, so 1/5th of a second
        self.current_data_chunk = pd.read_csv(self.csv_file_path,
                                              skiprows=self.total_rows_skipped,
                                              nrows=self.rows_to_skip,
                                              names=['adc1', 'adc2'],
                                              header=None)
        self.total_rows_skipped = self.total_rows_skipped+self.rows_to_skip
        if len(self.x_axis) > self.window:
            start = self.rows_to_skip-self.window-10000
            self.x_axis = list(np.arange(start, self.rows_to_skip))
        return self.current_data_chunk

