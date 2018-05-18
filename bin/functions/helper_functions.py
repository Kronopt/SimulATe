#!python2
# coding: utf-8

"""
HELPER FUNCTIONS

DEPENDENCIES:
    - Python 2.7
"""

import xml.parsers.expat as xml
from math import sqrt
from random import random, seed

__author__ = 'Pedro HC David, https://github.com/Kronopt'
__credits__ = ['Pedro HC David']


class NewColor(object):
    """
    Generates a non-overlapping and pretty colors
    """
    golden_ratio = (1 + sqrt(5)) / 2

    seed(100)  # enables the same colors to be generated between simulations
    CURRENT_COLOR = (random(), 0.7, 0.95)  # (H,S,V), random initial color

    bacterias_already_colored = {}  # dict[HSV]

    @staticmethod
    def new_color(bacteria_name=None):
        """
        Generates a non-overlapping and pretty color based on the given color, using the golden ratio.
        Checks whether a bacteria already has a color or not, returning the same color in case it does

        RETURNS: (float, float, float)
            New color in HSV format
        """
        def update_random_color():
            # generates a new random hue, saves the new HSV and returns it
            new_h = (NewColor.CURRENT_COLOR[0] + 1 / NewColor.golden_ratio) % 1
            NewColor.CURRENT_COLOR = new_h, NewColor.CURRENT_COLOR[1], NewColor.CURRENT_COLOR[2]
            return NewColor.CURRENT_COLOR

        if bacteria_name is None:
            # if no name is provided, simply generate a new color and return it
            return update_random_color()
        else:
            # check if bacteria already has a color
            if bacteria_name in NewColor.bacterias_already_colored:
                # if it oes, returns it without generating a new color
                return NewColor.bacterias_already_colored[bacteria_name]
            else:
                # generates a new color, saves it, inserts its value into dict and returns it
                NewColor.bacterias_already_colored[bacteria_name] = update_random_color()
                return NewColor.bacterias_already_colored[bacteria_name]


class XMLTextParser(object):
    """
    XML parser to parse language, info and option strings
    """
    def __init__(self, element, lang):
        """
        Instantiates xml parser

        PARAMETERS:
            element : str
                Element to be parsed ("string", "options", etc)
            lang : str
                Language selected ("en", "pt", etc)
        """
        self.element = element
        self.lang = lang  # str
        self.xml_parser = xml.ParserCreate()  # xml
        self.corresponding_element = False  # bool
        self.last_element = ""  # str
        self.strings_dict = {}  # dict[str]

    def start_element(self, name, attributes):
        """
        Called by the xml.parsers.expat at each xml element start
        Creates an entry in self.strings_dict for the 'name' element's id if it corresponds to the specified language
        
        PARAMETERS:
            name : str
                Element name
            attributes : dict[str]
                Dictionary with every element's attribute
        """
        if name == self.element and attributes["language"] == self.lang:
            self.strings_dict[attributes["id"]] = None  # char_data then fills this
            self.last_element = attributes["id"]
            self.corresponding_element = True

    def char_data(self, data):
        """
        Called by the xml.parsers.expat at each xml data
        Fills the self.strings_dict entry created by start_element with it's corresponding data

        PARAMETERS:
            data : str
                Data
        """
        if data != "\n" and self.corresponding_element:
            self.strings_dict[self.last_element] = data
            self.corresponding_element = False

    def parse(self, xml_file):
        """
        Begins xml document parsing
        
        PARAMETERS
            xml_file : str
                XML file path (including extension)
        
        RETURNS: dict[str]
            Dictionary with each id and corresponding text
        """
        with open(xml_file, "r") as xml_file_object:
            self.xml_parser.StartElementHandler = self.start_element
            self.xml_parser.CharacterDataHandler = self.char_data

            self.xml_parser.ParseFile(xml_file_object)

        return self.strings_dict
