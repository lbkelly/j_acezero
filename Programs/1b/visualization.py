import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import datetime

"""
To help with the visualization of data
Saves the chart to a file, rather than displaying it.
"""

__author__ = 'lbkelly'


class Trace:
    def __init__(self):
        pass


def draw_plot(title, plot1, plot2, plot3, description1, description2, description3, x_label, y_label, x_min, y_min,
              y_buffer, name):
    plt.clf()
    plt.title(title)
    plt.plot(plot1, color='b')
    plt.plot(plot2, color='g')
    plt.plot(plot3, color='r')
    plt.legend([description1, description2, description3], loc='upper left')
    plt.axis([x_min, len(plot2), y_min, plot2[-1][0] + y_buffer])
    plt.xlabel(x_label)
    plt.ylabel(y_label)



    # plt.show()
    title = name + '.jpg'
    plt.savefig(title)
