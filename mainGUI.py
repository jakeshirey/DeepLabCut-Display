import sys, time
from xml.etree.ElementTree import tostring

import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc

import slideshow as vid
import grapher
import globalEventListener as listener

class MainWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DeepLabCut Data Visualization Tool")
        #self.setWindowIcon(qtg.QIcon('window_icon.png'))

        self.programClosed = False
        quit = qtw.QAction("Quit", self)
        quit.triggered.connect(self.call_close)
        
        self.videoplayer = vid.VideoPlayer()
        self.videoplayer.setMinimumSize(480,270)
        
        self.graph = grapher.DataDisplay()
        self.graph.setMinimumSize(480, 270)

        self.videoplayer.set_graph_reference(self.graph)
        
        #ui feature to have resizeable widgets
        splitter = qtw.QSplitter()
        splitter.addWidget(self.videoplayer)
        splitter.addWidget(self.graph)
        #splitter.splitterMoved.connect(self.dynamic_scaling)

        outerLayout = qtw.QVBoxLayout()
        outerLayout.addWidget(splitter)
        self.setLayout(outerLayout)

        #supports syncronized scrubbing of graph alongside video
        self.videoplayer.slider.sliderMoved.connect(self.graph.video_position_changed)
        #self.videoplayer.mediaPlayer.positionChanged.connect(self.graph.video_position_changed)
        #self.videoplayer.mediaPlayer.durationChanged.connect(self.graph.video_duration_changed)
        #reverse connection - clicking on graph shifts video frame
        self.graph.plot.mpl_connect('button_press_event', self.videoplayer.click_graph)
        self.graph.plot.mpl_connect('motion_notify_event', self.videoplayer.move_mouse_graph)

        self.showMaximized()

        #listener.GlobalObject().add_event_listener('refresh', self.refresh)
        #listener.GlobalObject().dispatch_event('refresh')
    
    def refresh(self):
        if self.videoplayer.isPlaying:
            self.videoplayer.set_position(self.videoplayer.current_frame + 1)
        # display in GUI
        self.update()
        self.show()
        # sleep according to frame rate then send another refresh signal
        time.sleep(0.001)
        if self.programClosed: return
        listener.GlobalObject().dispatch_event('refresh')

    def call_close(self):
        self.programClosed = True


#Initialize
app = qtw.QApplication([])
mw = MainWindow()

#Run App
app.exec_()