import sys

import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg

import videoplayer as vid
import grapher

class MainWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Horse Data Visualization Tool")
        #self.setWindowIcon(qtg.QIcon('window_icon.png'))
        
        self.videoplayer = vid.VideoPlayer()
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
        self.videoplayer.mediaPlayer.positionChanged.connect(self.graph.video_position_changed)
        self.videoplayer.mediaPlayer.durationChanged.connect(self.graph.video_duration_changed)
        #reverse connection - clicking on graph shifts video frame
        self.graph.plot.mpl_connect('button_press_event', self.videoplayer.click_graph)
        self.graph.plot.mpl_connect('motion_notify_event', self.videoplayer.move_mouse_graph)

        self.showMaximized()

        self.update()
        self.show()
    #def move_line(self, position):
    #   self.graph.axes


#Initialize
app = qtw.QApplication([])
mw = MainWindow()

#Run App
app.exec_()