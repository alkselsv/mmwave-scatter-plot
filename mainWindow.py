from PySide6 import QtWidgets, QtCore
import pyqtgraph as pg
import numpy as np
import time

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, radar):
        super().__init__()
        self.setWindowTitle('SignalFromNoise')

        # Виджеты
        centralWidget = QtWidgets.QWidget()
        startBtn = QtWidgets.QRadioButton('Start')
        stopBtn = QtWidgets.QRadioButton('Stop')

        self.fovRadar = QtWidgets.QSpinBox()
        self.fovRadar.setRange(0, 360)
        self.fovRadar.setValue(120)
        self.fovRadar.setSingleStep(2)

        self.rovRadar = QtWidgets.QSpinBox()
        self.rovRadar.setRange(0, 20)
        self.rovRadar.setValue(10)

        self.plotRadar = pg.PlotWidget(background='#04005f')
        grp = QtWidgets.QGroupBox('Manage')

        self.plotRadar.setAspectLocked()

        # Макеты
        layout = QtWidgets.QGridLayout()
        layoutGrpRadar = QtWidgets.QVBoxLayout()
        layoutGrpRadarView = QtWidgets.QGridLayout()

        # Настройка отображения
        self.setCentralWidget(centralWidget)

        centralWidget.setLayout(layout)

        layoutGrpRadar.addWidget(startBtn)
        layoutGrpRadar.addWidget(stopBtn)
        layoutGrpRadarView.addWidget(QtWidgets.QLabel('Fov'), 0, 0)
        layoutGrpRadarView.addWidget(QtWidgets.QLabel('Range'), 0, 1)
        layoutGrpRadarView.addWidget(self.fovRadar, 1, 0)
        layoutGrpRadarView.addWidget(self.rovRadar, 1, 1)

        layoutGrpRadar.addLayout(layoutGrpRadarView)

        grp.setLayout(layoutGrpRadar)

        grp.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                          QtWidgets.QSizePolicy.Fixed)

        stopBtn.setChecked(True)
        stopBtn.setCheckable(True)

        layout.addWidget(grp, 0, 0)
        layout.addWidget(self.plotRadar, 0, 1)

        self.plotRadar.setXRange(-5, 5)
        self.plotRadar.setYRange(0, 10)

        self.plotRadar.setLabel('left', text='Y position (m)')
        self.plotRadar.setLabel('bottom', text='X position (m)')
        self.plotRadar.showGrid(x=True, y=True)

        # Указатель на новый график с точками
        self.updateGridPlot()

        # Таймер
        self.timer = QtCore.QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.updatePlot)

        # Сигналы на продолжение и приостановку генерации
        startBtn.clicked.connect(self.start)
        stopBtn.clicked.connect(self.stop)

        self.fovRadar.valueChanged.connect(self.updateGridPlot)
        self.rovRadar.valueChanged.connect(self.updateGridPlot)

        #Радар
        self.radar = radar if radar else None

    def start(self):
        if self.radar:
            self.radar.startRadar()
        self.timer.start()

    def stop(self):
        if self.radar:
            self.radar.stopRadar()
        self.timer.stop()

    def updateGridPlot(self):
        fov = self.fovRadar.value()
        rov = self.rovRadar.value()
        self.plotRadar.clear()
        for r in range(1, rov + 1, 1):
            circle = QtWidgets.QGraphicsEllipseItem(-r, -r, r * 2, r * 2)
            circle.setPen(pg.mkPen(0.2))
            if fov < 360:
                emp = (180-fov)/2
                circle.setStartAngle(-emp * 16)
                circle.setSpanAngle((-180 + emp*2) * 16)
                self.plotRadar.addItem(circle)
            else:
                self.plotRadar.addItem(circle)
        self.new_points = self.plotRadar.plot([], [], pen=None, symbol='o')

    # Обновление графика
    def updatePlot(self):

        if self.radar:
            self.radar.updateData()

            if self.radar.dataOk:
                detObj = self.radar.detObj
                x = -detObj["x"]
                y = detObj["y"]
                self.new_points.setData(x, y)
        else:
            fov = self.fovRadar.value()
            rov = self.rovRadar.value()
            if fov < 360:
                mean = (180-fov)/2
                theta = np.linspace(np.deg2rad(mean), np.deg2rad(180-mean), 20)
                radius = np.random.uniform(0, rov, size=20)
            else:
                theta = np.linspace(0, 2*np.pi, 100)
                radius = np.random.uniform(0, rov, size=100)
            x = radius * np.cos(theta)
            y = radius * np.sin(theta)
            self.new_points.setData(x, y)
