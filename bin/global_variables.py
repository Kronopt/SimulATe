#!python2
# coding: utf-8

"""
GLOBALS
Global variables

DEPENDENCIES:
    - Python 2.7
"""

import os
from colorsys import hsv_to_rgb
from kivy.clock import Clock
from bin.deps.kivy_graph import SmoothLinePlot
from bin.classes.Antibiotic import Antibiotic
from bin.classes.AntibioticAssortment import AntibioticAssortment
from bin.classes.Bacteria import Bacteria
from bin.classes.Microbiome import Microbiome
from bin.functions.graphs import xy_max_resize
from bin.functions.helper_functions import NewColor, XMLTextParser

__author__ = 'Pedro HC David, https://github.com/Kronopt'
__credits__ = ['Pedro HC David']


##########
# Language
##########

language = "en"
# if translations are missing, defaults to english
LANGUAGE = XMLTextParser("string", language).parse(os.path.join("bin", "ui", "text.xml"))

DEFAULT_LANGUAGE = dict(LANGUAGE)  # copy language dict
DEFAULT_LANGUAGE["selected_language"] = language

with open(os.path.join("bin", "options.txt"), "r") as options:
    for line in options:
        option = line.split(": ")
        if option[0] == "language":
            if option[1] != language:
                language = option[1]
                LANGUAGE.update(XMLTextParser("string", language).parse(os.path.join("bin", "ui", "text.xml")))
LANGUAGE["selected_language"] = language

############
# Scenario 1
############

# Antibiotics
ANTIBIOTICS = {"Generic Antibiotic": Antibiotic("Generic Antibiotic")}
ANTIBIOTIC_ASSORTMENT = AntibioticAssortment(ANTIBIOTICS, LANGUAGE, "graph_antibiotic_y_axis")

# Bacteria
BACTERIA = {"Sensitive": Bacteria("Sensitive"),
            "Resistant": Bacteria("Resistant"),
            "Total": Bacteria("Total", (0.4, 0.4, 0.4))}
BACTERIA_ASSORTMENT = Microbiome("Generic Microbiome", BACTERIA, LANGUAGE, "graph_bacteria_y_axis")

# Immune System
immune_system_color = hsv_to_rgb(*NewColor.new_color())
IMMUNE_PLOT = SmoothLinePlot(points=[(0, 1)], color=immune_system_color, line_width=1.01)
immune_plot_clock = Clock.schedule_interval(xy_max_resize(IMMUNE_PLOT, BACTERIA_ASSORTMENT.get_graph_widget(), "log"),
                                            1/60.)

# Density limit
DEATH_LIMIT = SmoothLinePlot(points=[], color=(1, 1, 1))

BACTERIA_ASSORTMENT.get_graph_widget().add_plot(IMMUNE_PLOT)
BACTERIA_ASSORTMENT.get_graph_widget().add_plot(DEATH_LIMIT)

############
# Scenario 2
############

# Gut Enterotype 1

# Antibiotics
ANTIBIOTICS_GUT1 = {"Lincosamides": Antibiotic("Lincosamides"), "Macrolides": Antibiotic("Macrolides"),
                    "Penicillins": Antibiotic("Penicillins"), "Quinolones": Antibiotic("Quinolones"),
                    "Streptogramins": Antibiotic("Streptogramins"), "Sulfonamides": Antibiotic("Sulfonamides"),
                    "Tetacyclines": Antibiotic("Tetacyclines"), "Trimethoprims": Antibiotic("Trimethoprims")}
ANTIBIOTIC_ASSORTMENT_GUT1 = AntibioticAssortment(ANTIBIOTICS_GUT1, LANGUAGE, "scenario_2_antibiotic_y_axis")

# Bacteria
BACTERIA_GUT1 = {"Bacteroides": Bacteria("Bacteroides"), "Faecalibacterium": Bacteria("Faecalibacterium"),
                 "Roseburia": Bacteria("Roseburia"), "Bifidobacterium": Bacteria("Bifidobacterium"),
                 "Lachnospiraceae": Bacteria("Lachnospiraceae"), "Parabacteroides": Bacteria("Parabacteroides"),
                 "Alistipes": Bacteria("Alistipes"), "Anaerostipes": Bacteria("Anaerostipes"),
                 "Acidaminococcus": Bacteria("Acidaminococcus"), "Collinsella": Bacteria("Collinsella")}
BACTERIA_ASSORTMENT_GUT1 = Microbiome("Gut Enterotype 1", BACTERIA_GUT1, LANGUAGE,
                                      "scenario_2_bacteria_y_axis_relative_frequency", True)

# Gut Enterotype 2

# Antibiotics
ANTIBIOTICS_GUT2 = {"Lincosamides": Antibiotic("Lincosamides"), "Macrolides": Antibiotic("Macrolides"),
                    "Penicillins": Antibiotic("Penicillins"), "Quinolones": Antibiotic("Quinolones"),
                    "Streptogramins": Antibiotic("Streptogramins"), "Sulfonamides": Antibiotic("Sulfonamides"),
                    "Tetacyclines": Antibiotic("Tetacyclines"), "Trimethoprims": Antibiotic("Trimethoprims")}
ANTIBIOTIC_ASSORTMENT_GUT2 = AntibioticAssortment(ANTIBIOTICS_GUT2, LANGUAGE, "scenario_2_antibiotic_y_axis")

# Bacteria
BACTERIA_GUT2 = {"Prevotella": Bacteria("Prevotella"), "Bacteroides": Bacteria("Bacteroides"),
                 "Faecalibacterium": Bacteria("Faecalibacterium"), "Lachnospiraceae": Bacteria("Lachnospiraceae"),
                 "Roseburia": Bacteria("Roseburia"), "Collinsella": Bacteria("Collinsella"),
                 "Bifidobacterium": Bacteria("Bifidobacterium"), "Alistipes": Bacteria("Alistipes"),
                 "Streptococcus": Bacteria("Streptococcus"), "Coprococcus": Bacteria("Coprococcus")}
BACTERIA_ASSORTMENT_GUT2 = Microbiome("Gut Enterotype 2", BACTERIA_GUT2, LANGUAGE,
                                      "scenario_2_bacteria_y_axis_relative_frequency", True)

# Gut Enterotype 3

# Antibiotics
ANTIBIOTICS_GUT3 = {"Lincosamides": Antibiotic("Lincosamides"), "Macrolides": Antibiotic("Macrolides"),
                    "Penicillins": Antibiotic("Penicillins"), "Quinolones": Antibiotic("Quinolones"),
                    "Streptogramins": Antibiotic("Streptogramins"), "Sulfonamides": Antibiotic("Sulfonamides"),
                    "Tetacyclines": Antibiotic("Tetacyclines"), "Trimethoprims": Antibiotic("Trimethoprims")}
ANTIBIOTIC_ASSORTMENT_GUT3 = AntibioticAssortment(ANTIBIOTICS_GUT3, LANGUAGE, "scenario_2_antibiotic_y_axis")

# Bacteria
BACTERIA_GUT3 = {"Bacteroides": Bacteria("Bacteroides"), "Bifidobacterium": Bacteria("Bifidobacterium"),
                 "Faecalibacterium": Bacteria("Faecalibacterium"), "Lachnospiraceae": Bacteria("Lachnospiraceae"),
                 "Alistipes": Bacteria("Alistipes"), "Akkermansia": Bacteria("Akkermansia"),
                 "Ruminococcus": Bacteria("Ruminococcus"), "Collinsella": Bacteria("Collinsella"),
                 "Blautia": Bacteria("Blautia"), "Roseburia": Bacteria("Roseburia")}
BACTERIA_ASSORTMENT_GUT3 = Microbiome("Gut Enterotype 3", BACTERIA_GUT3, LANGUAGE,
                                      "scenario_2_bacteria_y_axis_relative_frequency", True)
