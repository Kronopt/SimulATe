#!python2
# coding: utf-8

"""
ANTIBIOTIC
Class that defines an antibiotic

DEPENDENCIES:
    - Python 2.7
"""

from colorsys import hsv_to_rgb
from bin.deps.kivy_graph import SmoothLinePlot
from bin.functions.helper_functions import NewColor

__author__ = 'Pedro HC David, https://github.com/Kronopt'
__credits__ = ['Pedro HC David']


class Antibiotic(object):
    """
    Defines an antibiotic
    """
    _total_antibiotics = 0  # int

    def __init__(self, name):
        """
        Instantiates antibiotic

        PARAMETERS:
            name : str
                Name of antibiotic
        """
        self._id = 'ant' + str(Antibiotic._total_antibiotics)  # str
        self._name = name  # str
        self._line_color = hsv_to_rgb(*NewColor.new_color())  # (R,G,B)
        self._plot = SmoothLinePlot(points=[(0, 0)], color=self._line_color, line_width=1.01)  # SmoothLinePlot

        Antibiotic._total_antibiotics += 1

    @staticmethod
    def get_total_antibiotics():
        """
        Gets total number of antibiotics

        RETURNS: int >= 0
            Total number of antibiotics
        """
        return Antibiotic._total_antibiotics

    def get_id(self):
        """
        Gets id of antibiotic

        RETURNS: str
            Id of antibiotic
        """
        return self._id

    def get_name(self):
        """
        Gets antibiotic name

        RETURNS: str
            Antibiotic name
        """
        return self._name

    def get_line_color(self):
        """
        Gets antibiotic graph line color

        RETURNS: (R, G, B)
            RGB line color of antibiotic
        """
        return self._line_color

    def get_plot(self):
        """
        Gets antibiotic plot

        RETURNS: SmoothLinePlot
            Antibiotic Plot
        """
        return self._plot
