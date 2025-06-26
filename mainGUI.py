import sys, time
import logging

import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc

import videoplayer
import grapher


class MainWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DeepLabCut-Display")
        
        self.videoplayer = videoplayer.VideoPlayer()
        self.videoplayer.setMinimumSize(480,270)
        
        self.graph = grapher.DataDisplay()
        self.graph.setMinimumSize(480, 270)

        self.videoplayer.set_graph_reference(self.graph)
        
        #ui feature to have resizeable widgets
        splitter = qtw.QSplitter()
        splitter.addWidget(self.videoplayer)
        splitter.addWidget(self.graph)

        outerLayout = qtw.QVBoxLayout()
        outerLayout.addWidget(splitter)
        self.setLayout(outerLayout)

        #supports syncronized scrubbing of graph alongside video
        self.videoplayer.slider.sliderMoved.connect(self.graph.video_position_changed)
        #reverse connection - clicking on graph shifts video frame
        self.graph.plot.mpl_connect('button_press_event', self.videoplayer.click_graph)
        self.graph.plot.mpl_connect('motion_notify_event', self.videoplayer.move_mouse_graph)

        self.showMaximized()

#Initialize
app = qtw.QApplication([])
mw = MainWindow()

#Run App
app.exec_()