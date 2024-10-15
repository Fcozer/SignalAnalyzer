import numpy as np
import pandas as pd
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import Qt, Slot, QPointF
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget, QHBoxLayout, QSizePolicy


class SignalWindowChartWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.window = 100000 # determines max length of y1_points and y2_points
        self.y1_points = None
        self.y2_points = None
        self.moving_x_axis = None

        # Helpers for dynamically updating axes
        self.x_min = None
        self.x_max = None
        self.y_min = None
        self.y_max = None

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

    def update_points(self, series, x, y, points_attr):
        # Update x and y axis
        if self.x_min is None:
            self.x_min = float(x.min())
            self.x_max = float(x.max())
            self.y_min = float(y.min())
            self.y_max = float(y.max())

        points = getattr(self, points_attr)

        if points is None:
            self.moving_x_axis = x.values
            points = [QPointF(float(xi), float(yi)) for xi, yi in zip(x, y)]
            series.replace(points)
        elif len(points) < self.window:
            new_points = points + [QPointF(float(xi), float(yi)) for xi, yi in zip(x, y)]
            series.replace(new_points)
            points = new_points
            self.moving_x_axis = np.concatenate((self.moving_x_axis, x.values))
            self.update_axes(x, 'x_min', 'x_max')
            self.update_axes(y, 'y_min', 'y_max')
        else:
            new_points = points[-self.window+10000:] + [QPointF(float(xi), float(yi)) for xi, yi in zip(x, y)]
            series.replace(new_points)
            points = new_points
            self.moving_x_axis = np.concatenate((self.moving_x_axis[-self.window+10000:], x.values))
            self.x_min = float(self.moving_x_axis.min())
            self.x_max = float(self.moving_x_axis.max())
            self.update_axes(y, 'y_min', 'y_max')
        print(f"updated y_points length: {len(points)}")
        setattr(self, points_attr, points)
        self.axis_x.setMin(self.x_min)
        self.axis_x.setMax(self.x_max)
        self.axis_y.setMin(self.y_min)
        self.axis_y.setMax(self.y_max)

    def update_axes(self, axes, min_attr, max_attr):
        current_min = getattr(self, min_attr)
        current_max = getattr(self, max_attr)
        min_candidate = float(axes.min())
        max_candidate = float(axes.max())
        if min_candidate < current_min:
            setattr(self, min_attr, min_candidate)
        if max_candidate > current_max:
            setattr(self, max_attr, max_candidate)


    @Slot(str, np.ndarray, np.ndarray, int)
    def replace_array(self, name: str, x: np.ndarray, y: np.ndarray, y_identity: int):
        #(f"replace_array called with series name: {name}")
        if name not in self.series_dict:
            self.add_series(name)
        series = self.series_dict[name]
        if y_identity == 1:
            self.update_points(series, x, y, 'y1_points')
        elif y_identity == 2:
            self.update_points(series, x, y, 'y2_points')
