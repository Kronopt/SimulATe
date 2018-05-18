#!python2
# coding: utf-8

"""
GRAPHS
Functions related to graphs design

DEPENDENCIES:
    - Python 2.7
    - Kivy 1.9.1
    - Kivy Garden Graph
"""

__author__ = 'Pedro HC David, https://github.com/Kronopt'
__credits__ = ['Pedro HC David']


def xy_max_resize(plot, graph_widget, axis_type="linear"):
    """
    Resize graph x and y axis when values exceeds set limit

    PARAMETERS:
        plot : LinePlot
            instantiated plot to check
        graph_widget : Graph
            graph to be updated
        axis_type : str
            "linear" or "log" (defaults to "linear")
    
    RETURNS: func
        lambda(_) function that resizes x and y axis
    """
    def resize_x(which_widget):
        which_widget.xmax += 10
        which_widget.x_ticks_major += 1

    def resize_y_linear(which_widget):
        which_widget.ymax += 20
        which_widget.y_ticks_major += 4

    def resize_y_log(which_widget):
        which_widget.ymax *= 10

    def lambda_func(_plot, _graph_widget, _axis_type):
        # x-axis
        # x represents time, and, in this case, is always linear
        if _plot.points[-1][0] > _graph_widget.xmax:
            resize_x(_graph_widget)

        # y-axis
        if _axis_type == "linear":
            if _plot.points[-1][1] > _graph_widget.ymax:
                resize_y_linear(_graph_widget)
        elif _axis_type == "log":
            if _plot.points[-1][1] > _graph_widget.ymax:
                resize_y_log(_graph_widget)

    return lambda _: lambda_func(plot, graph_widget, axis_type)
