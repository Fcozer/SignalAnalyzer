import numpy as np
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import Qt, Slot, QPointF
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget, QHBoxLayout, QSizePolicy


class SignalWindowChartWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.series_dict = {}
        self.axis_x = QValueAxis()
        self.axis_y = QValueAxis()

        self.chart = QChart()
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.chart_view.setSizePolicy(size)
        self.main_layout.addWidget(self.chart_view)

        self.setLayout(self.main_layout)

        # Initialize axes
        self.axis_x.setTickCount(10)
        self.axis_x.setLabelFormat("%.2f")
        self.axis_x.setTitleText("Time")
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)

        self.axis_y.setTickCount(10)
        self.axis_y.setLabelFormat("%.2f")
        self.axis_y.setTitleText("Amplitude")
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)

    @Slot(float, float)
    def set_axis_y(self, min_y: float, max_y: float):
        self.axis_y.setMin(min_y)
        self.axis_y.setMax(max_y)

    def add_series(self, name: str):
        series = QLineSeries()
        series.setName(name)
        self.chart.addSeries(series)
        series.attachAxis(self.axis_x)
        series.attachAxis(self.axis_y)
        self.series_dict[name] = series

    @Slot(str, np.ndarray, np.ndarray)
    def replace_array(self, name: str, x: np.ndarray, y: np.ndarray):
        print(f"replace_array called with series name: {name}, data length: {len(x)}")
        if name not in self.series_dict:
            self.add_series(name)
        series = self.series_dict[name]
        points = [QPointF(float(xi), float(yi)) for xi, yi in zip(x, y)]
        series.replace(points)

        self.axis_x.setMin(float(x.min()))
        self.axis_x.setMax(float(x.max()))
        self.axis_y.setMin(float(y.min()))
        self.axis_y.setMax(float(y.max()))