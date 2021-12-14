import tkinter as tk
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
        FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt


class ChartView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.figure = Figure(figsize = (6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master = self)

        # Add Toolbar
        # self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.canvas.get_tk_widget().pack(fill='both',expand='True')

        # Set up axes
        self.axes = self.figure.add_subplot(1,1,1)
        # self.axes.set_xlabel(x_axis)
        # self.axes.set_ylabel(y_axis)

        # Setup for legend
        self.lines = []
        self.line_labels = []

    # def draw_lines(self, data):
    def draw_pie(self, title, fracts, labels, explode, autopct, shadow=True, startangle=90):
        self.axes.clear()
        self.axes.set_title(title)
        self.axes.pie(fracts, explode=explode, labels=labels, autopct=autopct)
        self.canvas.draw()

    def draw_bars(self, title, size, labels):
        self.axes.clear()
        self.axes.set_title(title)
        self.axes.bar(labels, size)
        self.canvas.draw()

    def clear(self):
        self.axes.clear()
        self.canvas.draw()
