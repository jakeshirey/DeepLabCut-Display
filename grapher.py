from cProfile import label
from cmath import inf
import sys
from xml.etree.ElementTree import tostring

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.axis import Axis

import pandas as pd
import csv
import string

import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self):
        self.fig, self.axes = plt.subplots(2, 1, constrained_layout = True)
        super(MplCanvas, self).__init__(self.fig)

class DataDisplay(qtw.QWidget):
    def __init__(self):
        super().__init__()

        self.mouse_hold = False #bool for mouse being currently held down
        self.num_frames = 0
        self.current_frame = 0 #stores current frame for vertical line plotting
        self.video_duration = 1 #prevents a divide by zero error when video_position_changed initially executes

        #create an empty data frame using pandas API
        self.data_frame = pd.DataFrame()

        self.init_ui()
        self.show()

    def init_ui(self):
        #create a label for the graph
        self.graph_label = qtw.QLabel("Ankle Position by Time")
        self.graph_label.setFont(qtg.QFont(''))
        self.graph_label.setFixedHeight(50)

        #create open-file button
        self.openBtn = qtw.QPushButton('Open CSV Data')
        self.openBtn.clicked.connect(self.open_file)
        
        # Create the maptlotlib FigureCanvas object
        self.plot = MplCanvas()
        self.plot.axes[0].set_title('X Coordinate by Frame')
        self.plot.axes[1].set_title('Y Coordinate by Frame')
        #self.plot.setMinimumSize(480, 270)
        self.plot.mpl_connect('button_press_event', self.click_graph)
        self.plot.mpl_connect('scroll_event', self.zoom)
        self.plot.mpl_connect('button_release_event', self.release_graph)
        self.plot.mpl_connect('motion_notify_event', self.move_mouse)


        #create a listWidget to control plotted variables
        self.listWidget = qtw.QListWidget()
        self.listWidget.setMaximumWidth(200)
        self.listWidget.setSelectionMode(2) #2 == MultiSelection, 3 == ExtendedSelection
        self.listWidget.itemClicked.connect(self.change_plotted_data)
        self.listWidget.itemSelectionChanged.connect(self.change_plotted_data)

        #add widgets to layout
        graphLayout = qtw.QHBoxLayout()
        plotLayout = qtw.QVBoxLayout()
        plotLayout.addWidget(self.plot)
        plotLayout.addWidget(self.openBtn)
        graphLayout.addLayout(plotLayout)
        graphLayout.addWidget(self.listWidget)
        self.setLayout(graphLayout)


    #Open CSV data, Plot on Graph
    def open_file(self):
        filename, _ = qtw.QFileDialog.getOpenFileName(self, "Open CSV Data")

        if filename: 
            try:
                #load data into pandas dataframe
                self.data_frame = pd.read_csv(filename)
                #clean data by combining labels and reindexing
                bodyparts_labels = self.data_frame.loc[0]
                coords_labels = self.data_frame.loc[1]
                labels = [i + "_" + j for i, j in zip(bodyparts_labels, coords_labels)]
                self.data_frame.columns = labels
                self.data_frame = self.data_frame.iloc[2: , : ]
                self.data_frame.index = range(len(self.data_frame.index))
                self.data_frame.rename({'bodyparts_coords': 'frame_number'}, axis= 'columns', inplace= True)

                #this regex line raises a FutureWarning and could break in later versions of PyQt
                self.data_frame.columns = self.data_frame.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
                #create a list of the bodyparts add to the list widget: only add one for each triplet of x,y, likelihood
                bodypart_list = []
                for col in self.data_frame.columns:
                    #convert dtype from object to float64
                    self.data_frame[col] = pd.to_numeric(self.data_frame[col],errors = 'coerce')
                    #add column label to listWidget
                    bodyparts_label = str(col).split('_')[0]
                    if bodyparts_label not in bodypart_list:
                        bodypart_list.append(bodyparts_label)
                        item = qtw.QListWidgetItem(bodyparts_label)
                        self.listWidget.addItem(item)
                
                self.num_frames = len(self.data_frame.index)
                self.plot.axes[0].clear()
                self.plot.axes[1].clear()
                #self.plot.axes.plot(self.data_frame.iloc[:,0], self.data_frame.iloc[:,0], label = self.data_frame.columns[0])
                self.plot.axes[0].set_xlabel('Frame Number')
                self.plot.axes[0].set_ylabel('Pixel Coordinate (X)')
                self.plot.axes[1].set_xlabel('Frame Number')
                self.plot.axes[1].set_ylabel('Pixel Coordinate (Y)')
                self.plot.axes[0].margins(x=0, y=0)
                self.plot.axes[1].margins(x=0, y=0)
                self.plot.axes[0].legend()
                self.plot.axes[1].legend()
                self.plot.axes[0].axvline(x = 0, color = 'r', label = 'current frame')
                self.plot.axes[1].axvline(x = 0, color = 'r', label = 'current frame')

                self.plot.draw_idle()
            except Exception as e:
                show_warning_messagebox(str(e))
                print(str(e))
    
    #switch the data plotted on the graph
    def change_plotted_data(self):
        while self.plot.axes[0].lines:
            self.plot.axes[0].lines.pop()
        while self.plot.axes[1].lines:
            self.plot.axes[1].lines.pop()    
        
        items = self.listWidget.selectedItems()
        #grab max/min y to set plot bounds
        minx, maxx, miny, maxy = 0, 1, 0, 1 #initialized for case of empty plot
        if items:
            minx = inf
            maxx = -inf
            miny = inf
            maxy = -inf

        for i in items:
            x_label = i.text() + "_x"
            y_label = i.text() + "_y"
            self.plot.axes[0].plot(self.data_frame.loc[:,'frame_number'], self.data_frame.loc[:, x_label], label = i.text())
            self.plot.axes[1].plot(self.data_frame.loc[:,'frame_number'], self.data_frame.loc[:, y_label], label = i.text())

            if (minx > min(self.data_frame.loc[:, x_label])):
                minx = min(self.data_frame.loc[:, x_label])
            if (maxx < max(self.data_frame.loc[:, x_label])):
                maxx = max(self.data_frame.loc[:, x_label])
            if (miny > min(self.data_frame.loc[:, y_label])):
                miny = min(self.data_frame.loc[:, y_label])
            if (maxy < max(self.data_frame.loc[:, y_label])):
                maxy = max(self.data_frame.loc[:, y_label])
        
        self.plot.axes[0].axvline(x = self.current_frame, color = 'r', label = 'current frame')
        self.plot.axes[1].axvline(x = self.current_frame, color = 'r', label = 'current frame')

        self.plot.axes[0].legend()
        self.plot.axes[1].legend()
        #reset vertical axis range
        dx = (maxx - minx)*0.1
        dy = (maxy - miny)*0.1
        self.plot.axes[0].set_ylim(minx-dx, maxx+dx)
        self.plot.axes[1].set_ylim(miny-dy, maxy+dy)

        self.plot.draw_idle()

    #=======GRAPH INTERACTIVITY========
    def click_graph(self, event):
        self.mouse_hold = True
        if all(event.inaxes != ax for ax in self.plot.axes): return
        if self.plot.axes[0].lines and self.plot.axes[1].lines:
            self.plot.axes[0].lines.pop()
            self.plot.axes[1].lines.pop()
            self.current_frame = int(event.xdata)
            self.plot.axes[0].axvline(x = self.current_frame, color = 'r', label = 'current frame')
            self.plot.axes[1].axvline(x = self.current_frame, color = 'r', label = 'current frame')
            self.plot.draw_idle()
            #print("grapher_click_graph")
    
    def release_graph(self, event):
        self.mouse_hold = False
    
    def move_mouse(self, event):
        if self.mouse_hold:
            if all(event.inaxes != ax for ax in self.plot.axes): return
            if self.plot.axes[0].lines and self.plot.axes[1].lines:
                self.plot.axes[0].lines.pop()
                self.plot.axes[1].lines.pop()
                self.current_frame = int(event.xdata)
                self.plot.axes[0].axvline(x = self.current_frame, color = 'r', label = 'current frame')
                self.plot.axes[1].axvline(x = self.current_frame, color = 'r', label = 'current frame')
                self.plot.draw_idle()
                #print("grapher_click_graph")

    def zoom(self, event):
        cur_xlim = self.plot.axes[0].get_xlim()
        #cur_ylim = self.graph.axes.get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
        #cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5
        xdata = event.xdata # get event x location
        #ydata = event.ydata # get event y location
        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1/1.5 # <-------- change this to change magnitude of zoom
        elif event.button == 'down':
            # deal with zoom out
            scale_factor = 1.5 # <----------
        else:
            # deal with something that should never happen
            scale_factor = 1
        # set new limits
        xmin = xdata - cur_xrange*scale_factor
        xmax = xdata + cur_xrange*scale_factor
        if xmin < 0: xmin = 0
        if xmax > self.num_frames: xmax = self.num_frames
        self.plot.axes[0].set_xlim([xmin, xmax])
        self.plot.axes[1].set_xlim([xmin, xmax])
        #self.graph.axes.set_ylim([ydata - cur_yrange*scale_factor,
                     #ydata + cur_yrange*scale_factor])
        self.plot.draw_idle()

    #========VIDEO FUNCTIONALITY=========
    #Slide a vertical line along the graph as the video frame changes
    def video_position_changed(self, position):

        #convert from a video position in milliseconds to a frame number
        frame = round(position)
        self.current_frame = frame

        if self.plot.axes[0].lines and self.plot.axes[1].lines:
            self.plot.axes[0].lines.pop()
            self.plot.axes[1].lines.pop()
            self.plot.axes[0].axvline(x = self.current_frame, color = 'r', label = 'current frame')
            self.plot.axes[1].axvline(x = self.current_frame, color = 'r', label = 'current frame')
            self.plot.draw_idle()

    #Store the duration of video in graph object, supports vertical line scrubbing function.
    def video_duration_changed(self, duration):
        self.video_duration = duration
#end of class==============

def show_warning_messagebox(message):
    msg = qtw.QMessageBox()
    msg.setIcon(qtw.QMessageBox.Warning)
  
    # setting message for Message Box
    msg.setText(message)
      
    # setting Message box window title
    msg.setWindowTitle("Warning")
      
    # declaring buttons on Message Box
    msg.setStandardButtons(qtw.QMessageBox.Ok)
      
    # start the app
    retval = msg.exec_()