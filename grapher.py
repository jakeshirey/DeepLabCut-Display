from cProfile import label
from cmath import inf
import sys
from tkinter import Y
from turtle import color
from xml.etree.ElementTree import tostring

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.axis import Axis

import numpy as np
import pandas as pd
import csv
import string
import traceback

import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc

import gait_parameters

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
        self.bodypart_list = [] #stores the names of all the unique body parts in string
        self.threshold = 0 #likelihood threshold for filtering points, by default set to 0 (all points meet threshold)

        #create an empty data frame using pandas API
        self.data_frame = pd.DataFrame()

        self.init_ui()
        self.show()

    def init_ui(self):

        #create open-file button
        self.openBtn = qtw.QPushButton('Open CSV Data')
        self.openBtn.clicked.connect(self.open_file)

        #create toggle points by threshold button
        self.thresholdBtn = qtw.QPushButton('Set Likelihood Threshold')
        self.thresholdBtn.clicked.connect(self.set_likelihood_threshold)

        #create calculate a new column button
        self.calcBtn = qtw.QPushButton("Calculate Gait Parameters")
        self.calcBtn.clicked.connect(self.calc_gait_parameters)

        #create save data button
        self.saveBtn = qtw.QPushButton('Save Data')
        self.saveBtn.clicked.connect(self.save_filtered_data)
        
        # Create the maptlotlib FigureCanvas object
        self.plot = MplCanvas()
        self.plot.axes[0].set_title('X Coordinate by Frame')
        self.plot.axes[1].set_title('Y Coordinate by Frame')
        #self.plot.setMinimumSize(480, 270)
        self.plot.mpl_connect('button_press_event', self.click_graph)
        self.plot.mpl_connect('scroll_event', self.zoom)
        self.plot.mpl_connect('button_release_event', self.release_graph)
        self.plot.mpl_connect('motion_notify_event', self.move_mouse)


        #create a list_widget to control plotted variables
        self.list_widget = qtw.QListWidget()
        self.list_widget.setMaximumWidth(200)
        self.list_widget.setSelectionMode(2) #2 == MultiSelection, 3 == ExtendedSelection
        self.list_widget.itemClicked.connect(self.change_plotted_data)
        self.list_widget.itemSelectionChanged.connect(self.change_plotted_data)

        #add widgets to layout
        graphLayout = qtw.QHBoxLayout()
        plotLayout = qtw.QVBoxLayout()
        buttonLayout = qtw.QHBoxLayout()
        plotLayout.addWidget(self.plot)
        buttonLayout.addWidget(self.openBtn)
        buttonLayout.addWidget(self.thresholdBtn)
        buttonLayout.addWidget(self.calcBtn)
        buttonLayout.addWidget(self.saveBtn)
        plotLayout.addLayout(buttonLayout)
        graphLayout.addLayout(plotLayout)
        graphLayout.addWidget(self.list_widget)
        self.setLayout(graphLayout)


    #Open CSV data, Plot on Graph
    def open_file(self):
        filename, _ = qtw.QFileDialog.getOpenFileName(self, "Open Spreadsheet Data")

        if filename: 
            try:
                #load data into pandas dataframe
                if filename.endswith(".csv"):
                    self.data_frame = pd.read_csv(filename)
                elif filename.endswith(".xlsx"):
                    self.data_frame = pd.read_excel(filename)
                else:
                    raise ValueError("Unsupported file type. Only CSV and Excel are allowed.")

                #clean data by combining labels and reindexing
                bodyparts_labels = self.data_frame.loc[0]
                coords_labels = self.data_frame.loc[1]
                labels = [i + "_" + j for i, j in zip(bodyparts_labels, coords_labels)]
                self.data_frame.columns = labels
                self.data_frame = self.data_frame.iloc[2: , : ]
                self.data_frame.index = range(len(self.data_frame.index))
                self.data_frame = self.data_frame.drop(columns=["bodyparts_coords"])

                #create a list of the bodyparts add to the list widget: only add one for each triplet of x,y, likelihood
                self.bodypart_list.clear()
                for col in self.data_frame.columns:
                    #convert dtype from object to float64
                    self.data_frame[col] = pd.to_numeric(self.data_frame[col],errors = 'coerce')
                    #add column label to list_widget
                    bodyparts_label = str(col).split('_')[0]
                    if bodyparts_label not in self.bodypart_list:
                        self.bodypart_list.append(bodyparts_label)
                        item = qtw.QListWidgetItem(bodyparts_label)
                        self.list_widget.addItem(item)
                
                self.num_frames = len(self.data_frame.index)
                self.plot.axes[0].clear()
                self.plot.axes[1].clear()
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
                traceback.print_exc()

    #save the data w/ current threshold to file
    def save_filtered_data(self):
        save_path, _ = qtw.QFileDialog.getSaveFileName(self, "Save Filtered Data Points to File", '', '*.csv')

        data = []
        columns = []
        for body_part in self.bodypart_list:
            x_data = self.data_frame.loc[:, body_part + "_x"]
            y_data = self.data_frame.loc[:, body_part + "_y"]
            likelihood_data = self.data_frame.loc[:, body_part + "_likelihood"]

            x_data = x_data.to_numpy()
            y_data = y_data.to_numpy()
            likelihood_data = likelihood_data.to_numpy()

            x_data = np.ma.masked_where(likelihood_data < self.threshold, x_data)
            y_data = np.ma.masked_where(likelihood_data < self.threshold, y_data)

            x_data = np.ma.filled(x_data, np.nan)
            y_data = np.ma.filled(x_data, np.nan)

            columns.append(body_part+"_x")
            columns.append(body_part+"_y")
            columns.append(body_part+"_likelihood")

            data.append(x_data)
            data.append(y_data)
            data.append(likelihood_data)
        data = np.swapaxes(data, 0, 1)      
        df = pd.DataFrame(data=data, columns=columns)
        df.to_csv(save_path)
  
    #switch the data plotted on the graph
    def change_plotted_data(self):
        while self.plot.axes[0].lines:
            self.plot.axes[0].lines.pop()
        while self.plot.axes[1].lines:
            self.plot.axes[1].lines.pop()    
        
        items = self.list_widget.selectedItems()
        #grab max/min y to set plot bounds
        minx, maxx, miny, maxy = 0, 1, 0, 1 #initialized for case of empty plot
        if items:
            minx = inf
            maxx = -inf
            miny = inf
            maxy = -inf

        for i in items:

            #update this function to incorporate threshold member variable when plotting
            x_data = self.data_frame.loc[:, i.text() + "_x"]
            y_data = self.data_frame.loc[:, i.text() + "_y"]
            likelihood_data = self.data_frame.loc[:, i.text() + "_likelihood"]
            x_data = x_data.to_numpy()
            y_data = y_data.to_numpy()
            likelihood_data = likelihood_data.to_numpy()
            x_data = np.ma.masked_where(likelihood_data < self.threshold, x_data)
            y_data = np.ma.masked_where(likelihood_data < self.threshold, y_data)

            #cmap = matplotlib.colormaps['plasma']
            #colored = [cmap(tl) for tl in likelihood_data]


            self.plot.axes[0].plot(range(len(x_data)), x_data, label = i.text(), marker='.')
            self.plot.axes[1].plot(range(len(y_data)), y_data, label = i.text(), marker='.')

            #catch runtime warning when all nans (from threshold == 1)
            if (minx > np.nanmin(x_data)):
                minx = np.nanmin(x_data)
            if (maxx < np.nanmax(x_data)):
                maxx = np.nanmax(x_data)
            if (miny > np.nanmin(y_data)):
                miny = np.nanmin(y_data)
            if (maxy < np.nanmax(y_data)):
                maxy = np.nanmax(y_data)
        
        self.plot.axes[0].axvline(x = self.current_frame, color = 'r', label = 'current frame')
        self.plot.axes[1].axvline(x = self.current_frame, color = 'r', label = 'current frame')

        self.plot.axes[0].legend()
        self.plot.axes[1].legend()
        #reset vertical axis range
        dx = (maxx - minx)*0.1
        dy = (maxy - miny)*0.1
        try:
            self.plot.axes[0].set_ylim(minx-dx, maxx+dx)
            self.plot.axes[1].set_ylim(miny-dy, maxy+dy)
        except ValueError as e:
            self.plot.axes[0].set_ylim(0, 1)
            self.plot.axes[0].set_ylim(0, 1)


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

    #========DATA MANIPULATION===========
    def set_likelihood_threshold(self):
        self.threshold, done = qtw.QInputDialog.getDouble(self,
         "Threshold Dialog",
         "Enter a likelihood value between 0-1. Graph will only display points above this threshold.",
          value=0, min=0, max=1, decimals=3)
        self.change_plotted_data()

    def calc_gait_parameters(self):
        items = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]

        if items:
            dialog = gait_parameters.ParameterInputDialog(items, self.data_frame)
            if dialog.exec_() == qtw.QDialog.Accepted:
                print("Landmarks:", dialog.confirmed_landmarks)
                print("Gait Parameters:", dialog.queried_gait_parameters)
                print("Summary Statistics:", dialog.summ_stats)

        else:
            qtw.QMessageBox.warning(self, "No landmarks are available! Try loading a data file.")
            return
        
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