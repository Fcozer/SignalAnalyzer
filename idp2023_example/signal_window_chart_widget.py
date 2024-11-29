import numpy as np
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QScatterSeries
from PySide6.QtCore import Qt, Slot, QPointF
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QSizePolicy
from PySide6.QtCharts import QChartView
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent

class ZoomableChartView(QChartView):
    def __init__(self, chart, parent=None):
        super().__init__(chart, parent)
        self.setRubberBand(QChartView.NoRubberBand)

    def wheelEvent(self, event):
        zoom_factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.chart().zoom(zoom_factor)
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton:
            delta = self.start_pos - event.pos()
            self.start_pos = event.pos()
            self.chart().scroll(delta.x(), -delta.y())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)

class SignalWindowChartWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.series_dict = {}
        self.axis_x = QValueAxis()
        self.axis_y = QValueAxis()

        self.chart = QChart()
        self.chart_view = ZoomableChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.chart_view.setSizePolicy(size)
        self.main_layout.addWidget(self.chart_view)
        self.setLayout(self.main_layout)

        self.axis_x.setTickCount(10)
        self.axis_x.setLabelFormat("%.2f")
        self.axis_x.setTitleText("Time")
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)

        self.axis_y.setTickCount(10)
        self.axis_y.setLabelFormat("%.2f")
        self.axis_y.setTitleText("Amplitude")
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)

    def add_peak_markers(self, name: str, peak_x: np.ndarray, peaks_data: np.ndarray):
        red_series = QScatterSeries()
        orange_series = QScatterSeries()
        green_series = QScatterSeries()

        red_series.setName("Large peaks: 0")
        orange_series.setName("Medium peaks: 0")
        green_series.setName("Small peaks: 0")

        red_series.setMarkerSize(7)
        red_series.setColor(QColor("red"))

        orange_series.setMarkerSize(7)
        orange_series.setColor(QColor("orange"))

        green_series.setMarkerSize(7)
        green_series.setColor(QColor("green"))

        for x_val, y_val, height in peaks_data:
            point = QPointF(float(x_val), float(y_val))
            if height > 0.3:
                red_series.append(point)
            elif height > 0.1:
                orange_series.append(point)
            else:
                green_series.append(point)

        self.chart.addSeries(red_series)
        red_series.attachAxis(self.axis_x)
        red_series.attachAxis(self.axis_y)

        self.chart.addSeries(orange_series)
        orange_series.attachAxis(self.axis_x)
        orange_series.attachAxis(self.axis_y)

        self.chart.addSeries(green_series)
        green_series.attachAxis(self.axis_x)
        green_series.attachAxis(self.axis_y)

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
        if name not in self.series_dict:
            self.add_series(name)
        series = self.series_dict[name]
        points = [QPointF(float(xi), float(yi)) for xi, yi in zip(x, y)]
        series.replace(points)
        self.axis_x.setMin(float(x.min()))
        self.axis_x.setMax(float(x.max()))
        self.axis_y.setMin(float(y.min()))
        self.axis_y.setMax(float(y.max()))

    @Slot(int, int, int)
    def update_peak_counts(self, large: int, medium: int, small: int):
        for series in self.chart.series():
            if isinstance(series, QScatterSeries):
                if "Large peaks" in series.name():
                    series.setName(f"Large peaks: {large}")
                elif "Medium peaks" in series.name():
                    series.setName(f"Medium peaks: {medium}")
                elif "Small peaks" in series.name():
                    series.setName(f"Small peaks: {small}")