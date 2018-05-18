#!python2
# coding: utf-8

"""
ANTIBIOTIC ASSORTMENT
Class that defines an assortment of antibiotics

DEPENDENCIES:
    - Python 2.7
"""

from kivy.clock import Clock
from bin.deps.kivy_graph import Graph
from bin.functions.graphs import xy_max_resize

__author__ = 'Pedro HC David, https://github.com/Kronopt'
__credits__ = ['Pedro HC David']


class AntibioticAssortment(object):
    """
    Defines an assortment of Antibiotics
    """
    def __init__(self, antibiotics, language, graph_y_axis):
        """
        Instantiates antibiotic assortment

        PARAMETERS:
            antibiotics : dict[Antibiotic]
                Antibiotics belonging to this assortment
            language : dict[str]
                Language dictionary
            graph_y_axis : str
                Y-axis label id in the language dict
        """
        self._graph_widget =\
            Graph(xlabel=language["graph_x_axis"], ylabel=language[graph_y_axis],
                  xmin=0, xmax=10, x_ticks_major=1, x_ticks_minor=4, x_grid_label=True,
                  ymin=0, ymax=20, y_ticks_major=4, y_ticks_minor=5, y_grid_label=True,
                  padding=5, **{'background_color': (0.15, 0.15, 0.15),
                                'border_color': (0.17, 0.17, 0.17),
                                'tick_color': (0.5, 0.5, 0.5)})  # Graph

        self._antibiotics = antibiotics  # dict[Antibiotic]

        # scheduled function calls (clocks) must be strong referenced, otherwise will not work
        self._clocks = []  # list[Clock]
        for _antibiotic in self._antibiotics.itervalues():
            self._clocks.append(
                Clock.schedule_interval(
                    xy_max_resize(_antibiotic.get_plot(), self._graph_widget), 1/60.))

            # add each antibiotic plot to the main graph
            self._graph_widget.add_plot(_antibiotic.get_plot())

    def get_graph_widget(self):
        """
        Gets the Antibiotic Assortment graph widget

        RETURNS: Graph
            Antibiotic Assortment graph widget
        """
        return self._graph_widget

    def get_antibiotics(self):
        """
        Gets antibiotics belonging to this antibiotic assortment

        RETURNS: dict[Antibiotic]
            Antibiotics belonging to this antibiotic assortment
        """
        return self._antibiotics

    def get_clocks(self):
        """
        Gets scheduled function calls to xy_max_resize() of every plot
        
        RETURNS: list[Clock]
        """
        return self._clocks
