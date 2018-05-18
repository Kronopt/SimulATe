#!python2
# coding: utf-8

"""
BACTERIA
Class that defines a bacteria population

DEPENDENCIES:
    - Python 2.7
"""

from colorsys import hsv_to_rgb
from bin.deps.kivy_graph import SmoothLinePlot
from bin.functions.helper_functions import NewColor

__author__ = 'Pedro HC David, https://github.com/Kronopt'
__credits__ = ['Pedro HC David']


class Bacteria(object):
    """
    Defines a bacteria population
    """
    _total_bacteria_populations = 0  # int

    def __init__(self, genus, color=None):
        """
        Instantiates bacteria

        PARAMETERS:
            genus : str
                Genus of bacteria
            color : (R, G, B)
                Color of bacteria
        """
        self._id = 'bac' + str(Bacteria._total_bacteria_populations)  # str
        self._genus = genus  # str
        if color is None:
            self._line_color = hsv_to_rgb(*NewColor.new_color(genus))  # (R,G,B)
        else:
            self._line_color = color
        self._plot = SmoothLinePlot(points=[(0, 1)], color=self._line_color, line_width=1.01)  # SmoothLinePlot

        Bacteria._total_bacteria_populations += 1

    @staticmethod
    def get_total_bacteria_populations():
        """
        Gets total number of bacteria populations

        RETURNS: int >= 0
            Total number of bacteria populations
        """
        return Bacteria._total_bacteria_populations

    def get_id(self):
        """
        Gets id of bacteria

        RETURNS: str
            Id of bacteria
        """
        return self._id

    def get_genus(self):
        """
        Gets bacteria genus

        RETURNS: str
            Bacteria genus
        """
        return self._genus

    def get_line_color(self):
        """
        Gets bacteria graph line color

        RETURNS: (R, G, B)
            RGB line color of bacteria
        """
        return self._line_color

    def get_plot(self):
        """
        Gets antibiotic plot

        RETURNS: SmoothLinePlot
            Antibiotic Plot
        """
        return self._plot
