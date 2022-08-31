#Standard Library
from ast import main
import sys
import glob
import os
import cv2
import numpy as np

#PyQt5
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc

#Matplotlib
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.axis import Axis

#Files in same folder
import grapher

'''
class MainWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.update()
        self.show()
        
    def init_ui(self):
        self.setWindowTitle("Horse Data Visualization Tool")
        
        videoplayer = Videoplayer()

        outerLayout = qtw.QVBoxLayout()
        outerLayout.addWidget(videoplayer)
        self.setLayout(outerLayout)

        self.showMaximized()

        self.update()
'''
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class VideoPlayer(qtw.QWidget):
    def __init__(self):
        super().__init__()

        #create list of frames as Pixmap objects
        self.frames = []

        #bool to describe state of pause/play
        self.isPlaying = False

        #store a reference to the grapher obj
        self.graph_reference = None

        #store reference to the current frame number being displayed
        self.current_frame = 0

        #store aspect ratio of frames
        self.aspect_ratio = 0

        self.init_ui()
        self.show()
    
    def init_ui(self):
        #create image surface using Pixmap on Label

        self.imageSurface = qtw.QLabel(self)
        self.imageSurface.setScaledContents(True)
        image_policy = qtw.QSizePolicy(qtw.QSizePolicy.Preferred, qtw.QSizePolicy.Preferred)
        image_policy.setHeightForWidth(True)
        self.imageSurface.setSizePolicy(image_policy)

        pal = self.palette()
        pal.setColor(qtg.QPalette.Background, qtc.Qt.black)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        #self.imageSurface = MplCanvas(self, width=5, height=4, dpi=100)


        #create margins for the image surface to maintain aspect ratio
        '''
        self.topMargin = qtw.QLabel()
        self.bottomMargin = qtw.QLabel()
        self.topMargin.setStyleSheet("background-color: black")
        self.bottomMargin.setStyleSheet("background-color: black")
        self.topMargin.setSizePolicy(qtw.QSizePolicy.Ignored, qtw.QSizePolicy.Ignored)
        self.bottomMargin.setSizePolicy(qtw.QSizePolicy.Ignored, qtw.QSizePolicy.Ignored)
        '''

        #create open button
        openBtn = qtw.QPushButton('Open Video')
        openBtn.clicked.connect(self.open_file)

        #create save button
        saveBtn = qtw.QPushButton('Save Current Frame')
        saveBtn.clicked.connect(self.save_frame_to_file)

        #create play button
        self.playBtn = qtw.QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(self.style().standardIcon(qtw.QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.change_play_state)

        #create scrubbing slider
        self.slider = qtw.QSlider(qtc.Qt.Horizontal)
        self.slider.setRange(0,0)
        self.slider.sliderMoved.connect(self.set_position)

        #create frame label
        self.frameLabel = qtw.QLabel()
        self.frameLabel.setSizePolicy(qtw.QSizePolicy.Preferred, qtw.QSizePolicy.Maximum)
        self.frameLabelString = "Frame: {} / {}"
        self.frameLabel.setText(self.frameLabelString)

        #create hbox layout
        hboxLayout = qtw.QHBoxLayout()
        hboxLayout.setContentsMargins(0,0,0,0)

        #set widgets to the hbox layout
        hboxLayout.addWidget(openBtn)
        hboxLayout.addWidget(self.playBtn)
        hboxLayout.addWidget(saveBtn)

        #create vbox layout
        mainLayout = qtw.QVBoxLayout()
        #mainLayout.addWidget(self.topMargin)
        mainLayout.addWidget(self.imageSurface)
        #mainLayout.addWidget(self.bottomMargin)
        mainLayout.addWidget(self.frameLabel)
        mainLayout.addWidget(self.slider)
        mainLayout.addLayout(hboxLayout)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(mainLayout)
    
    #EVENTS=============================================================
    def resizeEvent(self, _event: qtg.QResizeEvent = None) -> None:
        if self.frames:
            rect = self.geometry()
            size = qtc.QSize(rect.width(), rect.height())

            # Don't waste CPU generating a new pixmap if the resize didn't
            # alter the dimension that's currently bounding its size
            pixmap_size = self.imageSurface.pixmap().size()
            if (pixmap_size.width() == size.width() and
              pixmap_size.height() <= size.height()):
                return
            if (pixmap_size.height() == size.height() and
              pixmap_size.width() <= size.width()):
                return

            self.imageSurface.setPixmap(self.frames[self.current_frame].scaled(size,
                qtc.Qt.KeepAspectRatio, qtc.Qt.SmoothTransformation))
            self.imageSurface.setFixedHeight(int(size.width() / self.aspect_ratio))


    #FILE HANDLING======================================================
    def open_file(self):
        try:
            filename, _ = qtw.QFileDialog.getOpenFileName(self, "Open Video")

            if filename:
                self.extract_frames(filename)

                self.slider.setRange(0, len(self.frames) - 1)

                self.imageSurface.setPixmap(self.frames[self.current_frame])
                 
                self.aspect_ratio = self.frames[self.current_frame].width() / self.frames[self.current_frame].height()
                self.resizeEvent()
                #self.imageSurface.axes.imshow(self.frames[self.current_frame])

                self.playBtn.setEnabled(True)
                self.set_position(0)
        except Exception as e:
                show_warning_messagebox("Error occured when opening video. Please check format of file.")
                print(str(e))
    
    def extract_frames(self, path):

        # Path to video file
        vidObj = cv2.VideoCapture(path)
    
        # Used as counter variable
        count = 0
    
        # checks whether frames were extracted
        success = 1
    
        while success:
    
            # vidObj object calls read
            # function extract frames
            success, image = vidObj.read()

            if success:
                image = qtg.QImage(image.data, image.shape[1], image.shape[0], qtg.QImage.Format_RGB888).rgbSwapped()
                image = qtg.QPixmap.fromImage(image)
                #image = image.scaled(720, 720, qtc.Qt.KeepAspectRatio)
                self.frames.append(image)
    
            # Saves the frames with frame-count
            #cv2.imwrite("frame%d.jpg" % count, image)
    
            count += 1

    def save_frame_to_file(self):
        photo = self.frames[self.current_frame]
        filename, _ = qtw.QFileDialog.getSaveFileName(self, "Save File", '', '*.jpg')
        photo.save(filename)

    #VIDEOPLAYER CORE FUNCTIONS============================================
    def change_play_state(self):
        if self.isPlaying:
            self.isPlaying = False
            self.playBtn.setIcon(self.style().standardIcon(qtw.QStyle.SP_MediaPlay))
        else:
            self.isPlaying = True
            self.playBtn.setIcon(self.style().standardIcon(qtw.QStyle.SP_MediaPause))

    def set_position(self, position):
        #self.imageSurface.axes.imshow(self.frames[position])
        self.current_frame = position
        self.imageSurface.setPixmap(self.frames[self.current_frame])
        currFrameString = self.frameLabelString.format(position, len(self.frames) - 1)
        self.frameLabel.setText(currFrameString)
        self.slider.setSliderPosition(position)

    #GRAPH INTERACTIVITY======================================================
    def set_graph_reference(self, graph: grapher.DataDisplay):
        self.graph_reference = graph

    def click_graph(self, event):
        if event.inaxes != self.graph_reference.plot.axes: return
        
        position = round(event.xdata)
        self.set_position(position)
        self.slider.setValue(position)
    
    def move_mouse_graph(self, event):
        if self.graph_reference.mouse_hold:
            if event.inaxes != self.graph_reference.plot.axes: return
        
            position = round(event.xdata)
            self.set_position(position)
            self.slider.setValue(position)


def show_warning_messagebox(message):
    msg = qtw.QMessageBox()
    msg.setIcon(qtw.QMessageBox.Warning)

    # setting message for Message Box
    msg.setText(message)
  
    # setting Message box window title
    msg.setWindowTitle("Warning")
  
    # declaring buttons on Message Box
    msg.setStandardButtons(qtw.QMessageBox.Ok)
  
    # start the warning gui
    retval = msg.exec_()