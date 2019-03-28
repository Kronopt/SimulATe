#!python2
# coding: utf-8

"""
MICROBIOME
Class that defines a microbiome

DEPENDENCIES:
    - Python 2.7
"""

from kivy.clock import Clock
from bin.deps.kivy_graph import Graph
from bin.functions.graphs import xy_max_resize

__author__ = 'Pedro HC David, https://github.com/Kronopt'
__credits__ = ['Pedro HC David']


class Microbiome(object):
    """
    Defines a Microbiome
    """
    _total_microbiomes = 0  # int

    def __init__(self, name, bacteria, language, graph_y_axis, relative_frequency=False):
        """
        Instantiates microbiome

        PARAMETERS:
            name : str
                Name of microbiome
            bacteria : dict[Bacteria]
                Bacteria belonging to this microbiome
            language : dict[str]
                Language dictionary
            graph_y_axis : str
                Y-axis label id in the language dict
            relative_frequency : bool
                Flag that allows graph to be shown in relative frequencies (between 0 and 1)
        """
        if relative_frequency:
            ymin = 0.0001
            ymax = 1
        else:
            ymin = 1
            ymax = 10**3

        self._graph_widget = Graph(ylabel=language[graph_y_axis],
                                   xmin=0, xmax=10, x_ticks_major=1, x_ticks_minor=4, x_grid_label=True,
                                   ymin=ymin, ymax=ymax, y_ticks_major=1, y_ticks_minor=7, y_grid_label=True,
                                   ylog=True,
                                   padding=5, **{'background_color': (0.15, 0.15, 0.15),
                                                 'border_color': (0.17, 0.17, 0.17),
                                                 'tick_color': (0.5, 0.5, 0.5)})  # Graph

        self._id = 'mic' + str(Microbiome._total_microbiomes)  # str
        self._name = name  # str
        self._bacteria = bacteria  # dict[Bacteria]

        # scheduled function calls (clocks) must be strong referenced, otherwise will not work
        self._clocks = []  # list[Clock]
        for _bacteria in sorted(self._bacteria.iterkeys(), reverse=True):  # sorted so that "total" plots come in first
            self._clocks.append(
                Clock.schedule_interval(xy_max_resize(self._bacteria[_bacteria].get_plot(), self._graph_widget,
                                                      "log"), 1/60.))

            # add each bacteria plot to the main graph
            self._graph_widget.add_plot(self._bacteria[_bacteria].get_plot())

        Microbiome._total_microbiomes += 1

    @staticmethod
    def get_total_microbiomes():
        """
        Gets total number of microbiomes

        RETURNS: int >= 0
            Total number of microbiomes
        """
        return Microbiome._total_microbiomes

    def get_graph_widget(self):
        """
        Gets microbiome graph widget

        RETURNS: Graph object
            Microbiome graph widget
        """
        return self._graph_widget

    def get_id(self):
        """
        Gets id of microbiome

        RETURNS: str
            Id of microbiome
        """
        return self._id

    def get_name(self):
        """
        Gets microbiome name

        RETURNS: str
            Microbiome name
        """
        return self._name

    def get_bacteria(self):
        """
        Gets bacteria belonging to this microbiome

        RETURNS: dict[Bacteria]
            Bacterias belonging to this microbiome
        """
        return self._bacteria

    def get_clocks(self):
        """
        Gets scheduled function calls to xy_max_resize() of every plot

        RETURNS: list[Clock]
        """
        return self._clocks
