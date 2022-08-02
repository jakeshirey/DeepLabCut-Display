#Standard Library
import sys
import glob
import os
import cv2
import numpy as np

#PyQt5
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc

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

        self.init_ui()
        self.show()
    
    def init_ui(self):
        #create image surface using Pixmap on Label
        self.imageSurface = qtw.QLabel(self)

        #create open button
        openBtn = qtw.QPushButton('Open Video')
        openBtn.clicked.connect(self.open_file)

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

        #create vbox layout
        mainLayout = qtw.QVBoxLayout()
        mainLayout.addWidget(self.imageSurface)
        mainLayout.addWidget(self.frameLabel)
        mainLayout.addWidget(self.slider)
        mainLayout.addLayout(hboxLayout)

        self.setLayout(mainLayout)
    
    #FILE HANDLING=====================
    def open_file(self):
        try:
            filename, _ = qtw.QFileDialog.getOpenFileName(self, "Open Video")

            if filename:
                self.extract_frames(filename)

                self.slider.setRange(0, len(self.frames) - 1)

                self.imageSurface.setPixmap(self.frames[self.current_frame])
                self.imageSurface.setScaledContents(True)
                self.imageSurface.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)

                self.playBtn.setEnabled(True)
        except:
                show_warning_messagebox()
    
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

    #VIDEOPLAYER CORE FUNCTIONS=======
    def change_play_state(self):
        if self.isPlaying:
            self.isPlaying = False
            self.playBtn.setIcon(self.style().standardIcon(qtw.QStyle.SP_MediaPlay))
        else:
            self.isPlaying = True
            self.playBtn.setIcon(self.style().standardIcon(qtw.QStyle.SP_MediaPause))

    def set_position(self, position):
        self.imageSurface.setPixmap(self.frames[position])
        self.current_frame = position
        currFrameString = self.frameLabelString.format(position, len(self.frames) - 1)
        self.frameLabel.setText(currFrameString)

    #GRAPH INTERACTIVITY===============
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


def show_warning_messagebox():
    msg = qtw.QMessageBox()
    msg.setIcon(qtw.QMessageBox.Warning)

    # setting message for Message Box
    msg.setText("Exception thrown when opening video. Please check format of video.")
  
    # setting Message box window title
    msg.setWindowTitle("Warning")
  
    # declaring buttons on Message Box
    msg.setStandardButtons(qtw.QMessageBox.Ok)
  
    # start the warning gui
    retval = msg.exec_()