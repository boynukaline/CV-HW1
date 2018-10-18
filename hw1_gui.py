import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, \
    QPushButton, QGroupBox, QAction, QFileDialog, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import cv2

##########################################
## Do not forget to delete "return NotImplementedError"
## while implementing a function
########################################

class App(QMainWindow):
    def __init__(self):
        super(App, self).__init__()

        self.title = 'Histogram Equalization'
        top = 100
        left = 100
        width = 680
        height = 500
        self.setGeometry(top, left, width, height)

        self.inputLoaded = None
        self.targetLoaded = None

        # You can define other things in here
        self.initUI()

    def openInputImage(self):
        # This function is called when the user clicks File->Input Image.
        self.inputLoaded = QFileDialog.getOpenFileName(self, 'Input Image', os.getenv('HOME'))
        self.input_img.setPixmap(QPixmap(self.inputLoaded[0]))
        print(self.inputLoaded[0])


    def openTargetImage(self):
        # This function is called when the user clicks File->Target Image.
        self.targetLoaded = QFileDialog.getOpenFileName(self, 'Target Image', os.getenv('HOME'))
        self.target_img.setPixmap(QPixmap(self.targetLoaded[0]))


    def initUI(self):
        # Write GUI initialization code
        menu = self.menuBar()
        file = menu.addMenu('File')

        input_Action = QAction('Open Input', self)

        target_Action = QAction('Open Target', self)

        exit_Action = QAction('Exit', self)

        equalize_hist_action = QAction('Equalize Histogram', self)
        toolbar = self.addToolBar('Toolbar')
        toolbar.addAction(equalize_hist_action)
        equalize_hist_action.triggered.connect(self.histogramButtonClicked)

        file.addAction(input_Action)
        file.addAction(target_Action)
        file.addAction(exit_Action)

        input_Action.triggered.connect(self.openInputImage)
        target_Action.triggered.connect(self.openTargetImage)
        exit_Action.triggered.connect(self.closeApp)


        inner_window = QWidget()
        input_box = QGroupBox('Input', inner_window)
        target_box = QGroupBox('Target', inner_window)
        result_box = QGroupBox('Result', inner_window)

        vbox_input = QVBoxLayout(self)
        input_box.setLayout(vbox_input)
        self.input_img = QLabel()
        vbox_input.addWidget(self.input_img)

        vbox_target = QVBoxLayout(self)
        target_box.setLayout(vbox_target)
        self.target_img = QLabel()
        vbox_target.addWidget(self.target_img)

        hbox = QHBoxLayout()
        hbox.addWidget(input_box)
        hbox.addWidget(target_box)
        hbox.addWidget(result_box)
        inner_window.setLayout(hbox)
        self.setCentralWidget(inner_window)


        #self.setLayout(vbox)

        self.show()

    def closeApp(self):
        self.close()

    def histogramButtonClicked(self):
        if not self.inputLoaded and not self.targetLoaded:
            # Error: "First load input and target images" in MessageBox
            QMessageBox.information(self,"Error", "First load input and target images")
            return None
        elif not self.inputLoaded:
            # Error: "Load input image" in MessageBox
            QMessageBox.information(self, "Error", "Load input image")
            return None
        elif not self.targetLoaded:
            # Error: "Load target image" in MessageBox
            QMessageBox.information(self, "Error", "Load target image")
            return None

        self.calcHistogram()



    def calcHistogram(self, I):
        # Calculate histogram
        return NotImplementedError

app = QApplication(sys.argv)
gui = App()
sys.exit(app.exec_())