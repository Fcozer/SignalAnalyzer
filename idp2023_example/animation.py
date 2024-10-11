import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Animation:
    def __init__(self, csv_file_path, window, rows_to_skip):
        self.csv_file_path = csv_file_path
        self.window = window
        self.rows_to_skip = rows_to_skip
        self.total_rows_skipped = rows_to_skip
        self.first_data_chunk = pd.read_csv(csv_file_path, nrows=rows_to_skip)
        self.current_data_chunk = self.first_data_chunk
        self.x_axis = list(np.arange(self.rows_to_skip))

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
        # Signal processing implementation at this point!
        return self.current_data_chunk

    def initiate_animation(self):
        plt.plot(self.x_axis, self.first_data_chunk['adc1'])
        plt.plot(self.x_axis, self.first_data_chunk['adc2'])

    def animate(self):
        if self.current_data_chunk.shape[0] < self.window:
            new_data = pd.concat([self.current_data_chunk, self.getSignalsFromDataChunk()])
        else:
            new_data = pd.concat([self.current_data_chunk.iloc[-self.window:], self.getSignalsFromDataChunk()])
        self.current_data_chunk = new_data
        plt.cla()
        plt.plot(self.x_axis, new_data['adc1'])
        plt.plot(self.x_axis, new_data['adc2'])

    def display_animation(self):
        animated = FuncAnimation(plt.gcf(), animate=self.animate(), init_func=self.initiate_animation(), interval=200, blit=False)
        plt.show()
