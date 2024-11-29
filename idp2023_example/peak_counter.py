class PeakCounter:
    def __init__(self):
        self.large_peaks = 0
        self.medium_peaks = 0
        self.small_peaks = 0

    def count_peaks(self, peak_heights):
        self.large_peaks = sum(1 for height in peak_heights if height > 0.3)
        self.medium_peaks = sum(1 for height in peak_heights if 0.1 < height <= 0.3)
        self.small_peaks = sum(1 for height in peak_heights if height <= 0.1)