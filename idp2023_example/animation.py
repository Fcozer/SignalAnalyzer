import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Animation:
    def __init__(self, window, data_reader):

        self.window = window
        # instance of DataReader class, same instance used for Signal Analyzer
        self.data_reader = data_reader

    def initiate_animation(self):
        plt.plot(self.data_reader.x_axis, self.data_reader.first_data_chunk['adc1'])
        plt.plot(self.data_reader.x_axis, self.data_reader.first_data_chunk['adc2'])

    def animate(self):
        if self.data_reader.current_data_chunk.shape[0] < self.window:
            new_data = pd.concat([self.data_reader.current_data_chunk,
                                  self.data_reader.getSignalsFromDataChunk()])
        else:
            new_data = pd.concat([self.data_reader.current_data_chunk.iloc[-self.window:],
                                  self.data_reader.getSignalsFromDataChunk()])
        self.data_reader.current_data_chunk = new_data
        plt.cla()
        plt.plot(self.data_reader.x_axis, new_data['adc1'])
        plt.plot(self.data_reader.x_axis, new_data['adc2'])

    def display_animation(self):
        animated = FuncAnimation(plt.gcf(), animate=self.animate(), init_func=self.initiate_animation(), interval=200, blit=False)
        plt.show()