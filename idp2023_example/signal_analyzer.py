import numpy as np
from scipy.signal import savgol_filter, find_peaks


class SignalAnalyzer:
    """
    A signal analyzer that receives a DataFrame object and runs signal processing and analysis transformations on it.

    """

    def __init__(self, dataframe):
        self.data = dataframe

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

    def transform_data(self):
        if self.data is None:
            return

        # baseline removal
        self.data['adc1'] = self.remove_baseline(self.data['adc1'], degree=2)
        self.data['adc2'] = self.remove_baseline(self.data['adc2'], degree=2)

        # Smoothing
        self.data['adc1'] = savgol_filter(self.data['adc1'], 2500, 3)
        self.data['adc2'] = savgol_filter(self.data['adc2'], 2500, 3)

        # Downsample the data
    #    num_points = 5000
    #    self.data['x_axis'], self.data['adc1'] = self.downsample(self.data['x_axis'], self.data['adc1'], num_points)
    #    _, self.data['adc2'] = self.downsample(self.data['x_axis'], self.data['adc2'], num_points

        # Peak finding
        signal = self.data['adc1']
        peaks = find_peaks(signal, height=1.5)
        found_peaks = np.zeros(shape=len(signal))
        for peak in peaks[0]:
            found_peaks[peak] = 1
            print(f'Peak found: {peak}')
        self.data['peaks'] = found_peaks

        return self.data
