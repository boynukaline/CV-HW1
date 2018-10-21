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


class App(QMainWindow):
    def __init__(self):
        super(App, self).__init__()

        self.title = 'Histogram Equalization'
        top = 100
        left = 100
        width = 1500
        height = 900
        self.setGeometry(top, left, width, height)

        self.inputLoaded = None
        self.targetLoaded = None


        # a figure instance to plot the histograms on
        self.figure_plotinput = Figure(figsize=(3,3))
        self.inputcanvas = FigureCanvas(self.figure_plotinput)
        self.figure_plottarget = Figure(figsize=(3,3))
        self.targetcanvas = FigureCanvas(self.figure_plottarget)
        self.figure_result = Figure(figsize=(3,3))
        self.resultcanvas = FigureCanvas(self.figure_result)


        # You can define other things in here
        self.initUI()

    def openInputImage(self):
        # Load image for showing on gui
        self.inputLoaded = QFileDialog.getOpenFileName(self, 'Input Image', os.getenv('HOME'))
        self.input_img.setPixmap(QPixmap(self.inputLoaded[0]).scaled(500,500))

        # read and convert img to rgb format
        input_img = cv2.imread(self.inputLoaded[0], 1)
        self.input_rgb = cv2.cvtColor(input_img, cv2.COLOR_BGR2RGB)
        self.vbox_input.addWidget(self.inputcanvas)

        self.plotHistogram(self.input_rgb, self.inputcanvas, self.figure_plotinput)


    def openTargetImage(self):
        # This function is called when the user clicks File->Target Image.
        self.targetLoaded = QFileDialog.getOpenFileName(self, 'Target Image', os.getenv('HOME'))
        self.target_img.setPixmap(QPixmap(self.targetLoaded[0]).scaled(500, 500))
        # read and convert img to rgb format
        target_img = cv2.imread(self.targetLoaded[0], 1)
        self.target_rgb = cv2.cvtColor(target_img, cv2.COLOR_BGR2RGB)
        self.vbox_target.addWidget(self.targetcanvas)

        self.plotHistogram(self.target_rgb, self.targetcanvas, self.figure_plottarget)

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

        self.vbox_input = QVBoxLayout(self)
        input_box.setLayout(self.vbox_input)
        self.input_img = QLabel()
        self.vbox_input.addWidget(self.input_img)


        self.vbox_target = QVBoxLayout(self)
        target_box.setLayout(self.vbox_target)
        self.target_img = QLabel()
        self.vbox_target.addWidget(self.target_img)

        self.vbox_result = QVBoxLayout(self)
        result_box.setLayout(self.vbox_result)
        self.result_img = QLabel()
        self.vbox_result.addWidget(self.result_img)


        hbox = QHBoxLayout()
        hbox.addWidget(input_box)
        hbox.addWidget(target_box)
        hbox.addWidget(result_box)
        inner_window.setLayout(hbox)
        self.setCentralWidget(inner_window)


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

        # Calculate the resulting image by histogram matching
        result = self.calcImg(self.input_rgb, self.target_rgb)

        # Show the resulting image in gui
        height, width, channel = result.shape
        bytesPerLine = 3 * width
        qImg = QImage(result.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.result_img.setPixmap(QPixmap(qImg).scaled(500,500))

        # Show the histograms of the resulting image in gui
        self.vbox_result.addWidget(self.resultcanvas)
        self.plotHistogram(result, self.resultcanvas, self.figure_result)


    # Shows and plots the histograms of each channel
    def plotHistogram(self, rgb_img, canvas, figure):

        self.input_r, self.input_g, self.input_b = cv2.split(rgb_img)
        # find R, G, B channel pdf
        pdf_r = self.findPdf(self.input_r)
        pdf_g = self.findPdf(self.input_g)
        pdf_b = self.findPdf(self.input_b)


        # create axis
        ax1 = figure.add_subplot(311)
        ax2 = figure.add_subplot(312)
        ax3 = figure.add_subplot(313)

        # clear old axes
        ax1.clear()
        ax2.clear()
        ax3.clear()

        # Padding between histograms
        figure.tight_layout()

        # plot data
        ax1.bar(range(256), pdf_r, width=0.7, align='center', color='red')
        ax2.bar(range(256), pdf_g, width=0.7, align='center', color='green')
        ax3.bar(range(256), pdf_b, width=0.7, align='center', color='blue')

        canvas.draw()


    # Returns the probability distribution histogram of each channel in an image
    def findPdf(self, channel):
        flat = channel.flatten()
        frequency = np.zeros((256), dtype=int)

        for i in flat:
            frequency[i] += 1

        pdf = frequency / np.sum(frequency)

        return pdf

    # Calculates resulting image by histogram matching, returns the result
    def calcImg(self, input, target):
        # Calculate histogram

        input_r, input_g, input_b = cv2.split(input)
        target_r, target_g, target_b = cv2.split(target)

        pdf_input_r = self.findPdf(input_r)
        pdf_input_g = self.findPdf(input_g)
        pdf_input_b = self.findPdf(input_b)
        pdf_target_r = self.findPdf(input_r)
        pdf_target_g = self.findPdf(input_g)
        pdf_target_b = self.findPdf(input_b)

        cdf_input_r = np.cumsum(pdf_input_r)
        cdf_input_g = np.cumsum(pdf_input_g)
        cdf_input_b = np.cumsum(pdf_input_b)
        cdf_target_r = np.cumsum(pdf_target_r)
        cdf_target_g = np.cumsum(pdf_target_g)
        cdf_target_b = np.cumsum(pdf_target_b)

        # calculate the resulting images from each channel
        result_r = self.histogramMatch(input_r, target_r, cdf_input_r, cdf_target_r)
        result_g = self.histogramMatch(input_g, target_g, cdf_input_g, cdf_target_g)
        result_b = self.histogramMatch(input_b, target_b, cdf_input_b, cdf_target_b)

        # merge channels and convert image format to uint8
        result_rgb = cv2.merge((result_r, result_g, result_b))
        result_rgb = np.uint8(result_rgb)

        return result_rgb

    # Histogram Matching algorithm returns a channel for resulting image using matching algorithm
    def histogramMatch(self, input, target, cdf_input, cdf_target):
        R, C = input.shape
        img = np.zeros((R, C), dtype=int)

        mi = np.min(input)
        Mi = np.max(input)
        gj = np.min(target)

        for gi in range(mi, Mi):

            while gj < 255 and cdf_target[gj] < cdf_input[gi]:
                gj += 1

            img = img + (gj * (input == gi))

        return img


app = QApplication(sys.argv)
gui = App()
sys.exit(app.exec_())