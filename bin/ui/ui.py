#!python2
# coding: utf-8

"""
MAIN UI
Application's User Interface

DEPENDENCIES:
    - Python 2.7
    - Kivy 1.9.1 or 1.10.0
    - main_layout.kv
"""

from kivy.config import Config
Config.set("graphics", "height", 520)
Config.set("graphics", "width", 720)
Config.set("graphics", "minimum_height", 520)
Config.set("graphics", "minimum_width", 720)
Config.set("graphics", "multisamples", '0')  # Kivy not detecting OpenGL version bug
Config.set("input", "mouse", "mouse, disable_multitouch")

from kivy.core.window import Window
Window.minimum_height = 520
Window.minimum_width = 720

import csv
import datetime
import os
from random import random
import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import BooleanProperty, NumericProperty, StringProperty, ObjectProperty, DictProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
import bin.global_variables as global_variables
from bin.functions.equations import calculate_next_time_step, calculate_next_time_step_scenario2,\
    nutrients_for_bacteria_duplication_eq
from bin.functions.helper_functions import XMLTextParser

__author__ = 'Pedro HC David, https://github.com/Kronopt'
__credits__ = ['Pedro HC David']


kivy.require('1.9.1')


class ExponentButton(Spinner):
    pass


class OptionText(Label):
    pass


class SmallerSlider(Slider):
    pass


class TreatmentType(BoxLayout):

    def clear_treatment_widget(self):
        self.ids.treatment_options.clear_widgets()

    def reset_button_states(self):
        self.ids.toggle_classic.state = "normal"
        self.ids.toggle_adaptive.state = "normal"
        self.ids.toggle_user.state = "normal"


class DefaultValuesButton(Button):

    @staticmethod
    def default_values(app):
        """
        Reverts all scenario 1 parameters to their default values
        """
        # reset sliders to default
        app.root.ids.initial_density_s.value = app.default_parameters["sensitive_initial_density"]
        app.root.ids.growth_rate_s.value = app.default_parameters["sensitive_growth_rate"]
        app.root.ids.antibiotic_inhibition_s.value = app.default_parameters["sensitive_antibiotic_inhibition"]
        app.root.ids.initial_density_r.value = app.default_parameters["resistant_initial_density"]
        app.root.ids.growth_rate_r.value = app.default_parameters["resistant_growth_rate"]
        app.root.ids.antibiotic_inhibition_r.value = app.default_parameters["resistant_antibiotic_inhibition"]
        app.root.ids.lymphocyte_inhibition.value = app.default_parameters["lymphocyte_inhibition"]
        app.root.ids.density_host_death.value = app.default_parameters["host_death_density_value"]
        app.root.ids.initial_density_n.value = app.default_parameters["initial_precursor_cell_density"]
        app.root.ids.proliferation_rate.value = app.default_parameters["immune_cell_proliferation_rate"]
        app.root.ids.half_maximum_growth.value = app.default_parameters["immune_cell_half_maximum_growth"]
        app.root.ids.effector_cells_decay.value = app.default_parameters["effector_decay_rate"]
        app.root.ids.memory_cells_conversion.value = app.default_parameters["memory_cell_conversion_rate"]
        app.root.ids.mean_concentration.value = app.default_parameters["antibiotic_mean_concentration"]

        # reset exponent button to default
        app.root.ids.density_host_death_exponent_button.text = app.default_parameters["host_death_density_exponent"]
        app.root.ids.density_host_death_exponent_button.values.insert(0, ' e14')  # refresh value to refresh button
        app.root.ids.density_host_death_exponent_button.values.pop(0)

        # clear treatment type widget to allow parameters to reset to default
        app.root.ids.treatment_toggles.clear_treatment_widget()
        app.root.ids.treatment_toggles.reset_button_states()
        app.treatment_type = ""


class BacteriaAntibioticResistanceOptionsButton(BoxLayout):

    def default_values(self, bacteria, app):
        """
        Reverts all Antibiotic Resistance sliders to their default values (scenario 2)
        """
        default_values_dict = getattr(app, bacteria + "_default_antibiotic_inhibition")

        for child in self.ids.antibiotic_resistance_sliders.children:
            child.default_value = default_values_dict[child.antibiotic_name.lower()]


class AntibioticConcentrationBox(BoxLayout):

    def default_antibiotic_concentrations(self):
        """
        Reverts all Antibiotic Concentration sliders to their default values
        """
        for child in self.children:
            child.slider_id.value = child.slider_default_value

    def change_switch_state(self, state):
        """
        Turns off all antibiotic administration switches
        """
        for child in self.children:
            child.switch_id.active = state


class GraphsLayout(BoxLayout):
    """
    Graph Layout
    """
    bacteria_graph = ObjectProperty(None)
    antibiotic_graph = ObjectProperty(None)

    ###################
    # Values Scenario 1
    ###################

    # simulation progress values
    simulation_going_scenario_1_property = BooleanProperty(False)
    pause_scenario_1_property = BooleanProperty(False)
    restart_in_progress_scenario_1_property = BooleanProperty(False)
    # current button values
    button_values_scenario_1 = {"start_button.state": "normal", "start_button.disabled": False,
                                "restart_button.disabled": True, "pause_button.disabled": True,
                                "pause_button.pause_value": False}

    ###################
    # Values Scenario 2
    ###################

    # simulation progress values, gut enterotype 1
    simulation_going_scenario_2_ent_1_property = BooleanProperty(False)
    pause_scenario_2_ent_1_property = BooleanProperty(False)
    restart_in_progress_scenario_2_ent_1_property = BooleanProperty(False)
    # current button values
    button_values_enterotype_1 = {"start_button.state": "normal", "start_button.disabled": False,
                                  "restart_button.disabled": True, "pause_button.disabled": True,
                                  "pause_button.pause_value": False}

    # simulation progress values, gut enterotype 2
    simulation_going_scenario_2_ent_2_property = BooleanProperty(False)
    pause_scenario_2_ent_2_property = BooleanProperty(False)
    restart_in_progress_scenario_2_ent_2_property = BooleanProperty(False)
    # current button values
    button_values_enterotype_2 = {"start_button.state": "normal", "start_button.disabled": False,
                                  "restart_button.disabled": True, "pause_button.disabled": True,
                                  "pause_button.pause_value": False}

    # simulation progress values, gut enterotype 3
    simulation_going_scenario_2_ent_3_property = BooleanProperty(False)
    pause_scenario_2_ent_3_property = BooleanProperty(False)
    restart_in_progress_scenario_2_ent_3_property = BooleanProperty(False)
    # current button values
    button_values_enterotype_3 = {"start_button.state": "normal", "start_button.disabled": False,
                                  "restart_button.disabled": True, "pause_button.disabled": True,
                                  "pause_button.pause_value": False}

    # all dicts together
    button_values = {"scenario_1": button_values_scenario_1, "scenario_2": dict(button_values_scenario_1),
                     "gut_enterotype_1": button_values_enterotype_1, "gut_enterotype_2": button_values_enterotype_2,
                     "gut_enterotype_3": button_values_enterotype_3}

    def __init__(self, **kwargs):
        super(GraphsLayout, self).__init__()

        # Microbiomes and AntibioticAssortments
        self.scenario_1_bacteria = global_variables.BACTERIA_ASSORTMENT
        self.scenario_1_antibiotics = global_variables.ANTIBIOTIC_ASSORTMENT
        self.gut_enterotype_1 = global_variables.BACTERIA_ASSORTMENT_GUT1
        self.gut_enterotype_2 = global_variables.BACTERIA_ASSORTMENT_GUT2
        self.gut_enterotype_3 = global_variables.BACTERIA_ASSORTMENT_GUT3
        self.scenario_2_antibiotics_gut_1 = global_variables.ANTIBIOTIC_ASSORTMENT_GUT1
        self.scenario_2_antibiotics_gut_2 = global_variables.ANTIBIOTIC_ASSORTMENT_GUT2
        self.scenario_2_antibiotics_gut_3 = global_variables.ANTIBIOTIC_ASSORTMENT_GUT3

    def button_states(self, start_bt, pause_bt, restart_bt, new_scenario, new_microbiome, app):
        """
        Loads and saves button (start, pause, restart) states for each scenario
        Also updates the values of app.current_scenario and app.current_microbiome
        
        PARAMETERS:
            start_bt : object
                Start button object
            pause_bt : object
                Pause button object
            restart_bt : object
                Restart button object
            new_scenario : str
                New scenario, "scenario_1" or "scenario_2"
            new_microbiome : str
                New "gut_enterotype_1", "gut_enterotype_2" or "gut_enterotype_3"
            app : object
                App object
        """
        current_scenario = app.current_scenario  # str
        current_microbiome = app.current_microbiome  # str

        # check if scenario or microbiome changed
        if current_scenario != new_scenario or current_microbiome != new_microbiome:

            # select correct scenario or microbiome
            if current_scenario == "scenario_1":
                if new_scenario == "scenario_2" and current_microbiome == "":
                    save_button_values = self.button_values[current_scenario]
                    load_button_values = self.button_values[new_scenario]
                elif new_scenario == "scenario_2" and current_microbiome != "":
                    save_button_values = self.button_values[current_scenario]
                    load_button_values = self.button_values[new_microbiome]

            elif current_scenario == "scenario_2":
                if new_scenario == "scenario_1" and current_microbiome == "":
                    save_button_values = self.button_values[current_scenario]
                    load_button_values = self.button_values[new_scenario]
                elif new_scenario == "scenario_1" and current_microbiome != "":
                    save_button_values = self.button_values[current_microbiome]
                    load_button_values = self.button_values[new_scenario]
                elif new_scenario == "scenario_2" and current_microbiome == "":
                    save_button_values = self.button_values[current_scenario]
                    load_button_values = self.button_values[new_microbiome]
                else:
                    save_button_values = self.button_values[current_microbiome]
                    load_button_values = self.button_values[new_microbiome]

            else:  # current_scenario == "", which is the first screen
                load_button_values = self.button_values[new_scenario]

            # save current button configuration for current screen
            if current_scenario != "":
                # pause current simulation
                new_pause_value = pause_bt.pause_value
                if not pause_bt.disabled and not pause_bt.pause_value:
                    pause_bt.was_pressed = True
                    pause_bt.pause_value = True
                    new_pause_value = True

                save_button_values["start_button.state"] = start_bt.state
                save_button_values["start_button.disabled"] = start_bt.disabled
                save_button_values["restart_button.disabled"] = restart_bt.disabled
                save_button_values["pause_button.disabled"] = pause_bt.disabled
                save_button_values["pause_button.pause_value"] = new_pause_value

            # load stored button configuration for new screen
            start_bt.state = load_button_values["start_button.state"]
            start_bt.disabled = load_button_values["start_button.disabled"]
            restart_bt.disabled = load_button_values["restart_button.disabled"]
            pause_bt.disabled = load_button_values["pause_button.disabled"]
            pause_bt.pause_value = load_button_values["pause_button.pause_value"]

            # update current scenario and microbiome
            app.current_scenario = new_scenario
            app.current_microbiome = new_microbiome

    def scenario_graph(self, scenario, enterotype):
        """
        Selects correct graph for the scenario selected
        
        PARAMETERS:
            scenario : str
                Scenario selected ("Scenario 1" or "Scenario 2")
            enterotype : str
                Enterotype selected ("", "gut_enterotype_1", "gut_enterotype_2" or "gut_enterotype_3")
        """
        if scenario == "scenario_1":
            self.bacteria_graph.clear_widgets()
            self.antibiotic_graph.clear_widgets()

            self.bacteria_graph.add_widget(self.scenario_1_bacteria.get_graph_widget())
            self.antibiotic_graph.add_widget(self.scenario_1_antibiotics.get_graph_widget())

        elif scenario == "scenario_2":
            self.bacteria_graph.clear_widgets()
            self.antibiotic_graph.clear_widgets()

            if enterotype == "gut_enterotype_1":
                self.bacteria_graph.clear_widgets()
                self.antibiotic_graph.clear_widgets()

                self.bacteria_graph.add_widget(self.gut_enterotype_1.get_graph_widget())
                self.antibiotic_graph.add_widget(self.scenario_2_antibiotics_gut_1.get_graph_widget())

            elif enterotype == "gut_enterotype_2":
                self.bacteria_graph.clear_widgets()
                self.antibiotic_graph.clear_widgets()

                self.bacteria_graph.add_widget(self.gut_enterotype_2.get_graph_widget())
                self.antibiotic_graph.add_widget(self.scenario_2_antibiotics_gut_2.get_graph_widget())

            elif enterotype == "gut_enterotype_3":
                self.bacteria_graph.clear_widgets()
                self.antibiotic_graph.clear_widgets()

                self.bacteria_graph.add_widget(self.gut_enterotype_3.get_graph_widget())
                self.antibiotic_graph.add_widget(self.scenario_2_antibiotics_gut_3.get_graph_widget())

    def update_labels(self, labels, **kwargs):
        """
        Updates graphs labels with the given labels
        
        PARAMETERS:
            labels : dict[str]
                Labels for x-axis and both y-axis
            kwargs : 
                Grabs unnecessary arguments passed by kivy
        """
        update_bacteria_graph_scenario_1 = False
        update_antibiotic_graph_scenario_1 = False
        update_bacteria_graph_scenario_2 = False
        update_antibiotic_graph_scenario_2 = False

        if "x_axis" in labels:
            self.scenario_1_antibiotics.get_graph_widget().xlabel = labels["x_axis"]
            self.scenario_2_antibiotics_gut_1.get_graph_widget().xlabel = labels["x_axis"]
            self.scenario_2_antibiotics_gut_2.get_graph_widget().xlabel = labels["x_axis"]
            self.scenario_2_antibiotics_gut_3.get_graph_widget().xlabel = labels["x_axis"]
            update_antibiotic_graph_scenario_1 = True
            update_antibiotic_graph_scenario_2 = True
        if "bacteria_y_axis" in labels:
            self.scenario_1_bacteria.get_graph_widget().ylabel = labels["bacteria_y_axis"]
            update_bacteria_graph_scenario_1 = True
        if "antibiotic_y_axis" in labels:
            self.scenario_1_antibiotics.get_graph_widget().ylabel = labels["antibiotic_y_axis"]
            update_antibiotic_graph_scenario_1 = True
        if "scenario_2_bacteria_y_axis_relative_frequency" in labels:
            self.gut_enterotype_1.get_graph_widget().ylabel = labels["scenario_2_bacteria_y_axis_relative_frequency"]
            self.gut_enterotype_2.get_graph_widget().ylabel = labels["scenario_2_bacteria_y_axis_relative_frequency"]
            self.gut_enterotype_3.get_graph_widget().ylabel = labels["scenario_2_bacteria_y_axis_relative_frequency"]
            update_bacteria_graph_scenario_2 = True
        if "scenario_2_antibiotic_y_axis" in labels:
            self.scenario_2_antibiotics_gut_1.get_graph_widget().ylabel = labels["scenario_2_antibiotic_y_axis"]
            self.scenario_2_antibiotics_gut_2.get_graph_widget().ylabel = labels["scenario_2_antibiotic_y_axis"]
            self.scenario_2_antibiotics_gut_3.get_graph_widget().ylabel = labels["scenario_2_antibiotic_y_axis"]
            update_antibiotic_graph_scenario_2 = True

        # had to access protected methods to update language...
        if update_bacteria_graph_scenario_1:
            self.scenario_1_bacteria.get_graph_widget()._update_labels()
        if update_antibiotic_graph_scenario_1:
            self.scenario_1_antibiotics.get_graph_widget()._update_labels()
        if update_bacteria_graph_scenario_2:
            self.gut_enterotype_1.get_graph_widget()._update_labels()
            self.gut_enterotype_2.get_graph_widget()._update_labels()
            self.gut_enterotype_3.get_graph_widget()._update_labels()
        if update_antibiotic_graph_scenario_2:
            self.scenario_2_antibiotics_gut_1.get_graph_widget()._update_labels()
            self.scenario_2_antibiotics_gut_2.get_graph_widget()._update_labels()
            self.scenario_2_antibiotics_gut_3.get_graph_widget()._update_labels()


class PopupWarning(Popup):
    """
    Popup warning message dialog
    """
    warning_text = StringProperty()

    def show_message(self, title, warning_text):
        """
        Defines popup title, message content and shows it.
        
        PARAMETERS:
            title : str
                Title text of popup
            warning_text : str
                Message content
        
        RETURNS: True
        """
        self.title = title
        self.warning_text = warning_text
        self.open()

        return True


class TreatmentToggle(ToggleButton):
    """
    Button Toggle for treatment types (Classic, Adaptive, User)
    """
    classic_treatment = Builder.load_file(os.path.join('bin', 'ui', 'treatment_classic.kv'))
    adaptive_treatment = Builder.load_file(os.path.join('bin', 'ui', 'treatment_adaptive.kv'))
    user_treatment = Builder.load_file(os.path.join('bin', 'ui', 'treatment_user.kv'))

    def selected_treatment(self, treatment, app):
        """
        Defines which treatment layout should be shown
        
        PARAMETERS:
            treatment : str
                "Classic", "Adaptive" or "User"
            app : object
                App object
        
        RETURNS: Widget
            Layout widget
        """
        options_widget = None

        if treatment == "Classic":
            options_widget = TreatmentToggle.classic_treatment
            options_widget.language = self.language
            options_widget.delay_value = app.default_parameters["classic_delay"]
            options_widget.duration_value = app.default_parameters["classic_duration"]

        elif treatment == "Adaptive":
            options_widget = TreatmentToggle.adaptive_treatment
            options_widget.language = self.language
            options_widget.exponent_value = app.default_parameters["adaptive_symptoms_at_bacteria_density_exponent"]
            options_widget.slider_value = app.default_parameters["adaptive_symptoms_at_bacteria_density_value"]

        elif treatment == "User":
            options_widget = TreatmentToggle.user_treatment
            options_widget.language = self.language
            options_widget.active_value = app.default_parameters["user_administer"]

        options_widget.add_widget(Widget())

        return options_widget


# Main App
class SimulATeApp(App):
    """
    Main App
    """
    # current scenario/microbiome
    current_scenario = StringProperty("")
    current_microbiome = StringProperty("")

    # simulation speed
    simulation_speed = NumericProperty(1/(24*5.0))  # 24*5 steps per day

    ######################
    # Scenario 1 variables
    ######################

    # function instances
    clock_add_points = None
    data_generator_instance = None

    # plots
    sensitive_bacteria_plot = global_variables.BACTERIA_ASSORTMENT.get_bacteria()["Sensitive"].get_plot()
    resistant_bacteria_plot = global_variables.BACTERIA_ASSORTMENT.get_bacteria()["Resistant"].get_plot()
    total_bacteria_plot = global_variables.BACTERIA_ASSORTMENT.get_bacteria()["Total"].get_plot()
    antibiotic_plot = global_variables.ANTIBIOTIC_ASSORTMENT.get_antibiotics()["Generic Antibiotic"].get_plot()
    immune_system_plot = global_variables.IMMUNE_PLOT
    death_limit = global_variables.DEATH_LIMIT

    # Scenario 1 default parameters
    default_parameters = {"sensitive_initial_density": 10, "sensitive_growth_rate": 3.3,
                          "sensitive_antibiotic_inhibition": 1, "resistant_initial_density": 2,
                          "resistant_growth_rate": 1.1, "resistant_antibiotic_inhibition": 0.1,
                          "lymphocyte_inhibition": 10**-5, "host_death_density_value": 1,
                          "host_death_density_exponent": ' e14',
                          "initial_precursor_cell_density": 200,
                          "immune_cell_proliferation_rate": 2, "immune_cell_half_maximum_growth": 10**5,
                          "effector_decay_rate": 0.35, "memory_cell_conversion_rate": 0.1,
                          "antibiotic_mean_concentration": 6, "classic_delay": 3.5, "classic_duration": 7,
                          "adaptive_symptoms_at_bacteria_density_value": 1,
                          "adaptive_symptoms_at_bacteria_density_exponent": ' e06', "user_administer": False}

    # sensitive bacteria options
    sensitive_initial_density = NumericProperty(default_parameters["sensitive_initial_density"])
    sensitive_growth_rate = NumericProperty(default_parameters["sensitive_growth_rate"])
    sensitive_antibiotic_inhibition = NumericProperty(default_parameters["sensitive_antibiotic_inhibition"])

    # resistant bacteria options
    resistant_initial_density = NumericProperty(default_parameters["resistant_initial_density"])
    resistant_growth_rate = NumericProperty(default_parameters["resistant_growth_rate"])
    resistant_antibiotic_inhibition = NumericProperty(default_parameters["resistant_antibiotic_inhibition"])

    # both bacteria options
    lymphocyte_inhibition = NumericProperty(default_parameters["lymphocyte_inhibition"])
    host_death_density_value = NumericProperty(default_parameters["host_death_density_value"])
    host_death_density_exponent = NumericProperty(10 ** int(default_parameters["host_death_density_exponent"][-2:]))
    host_death_density = NumericProperty(default_parameters["host_death_density_value"] *
                                         10 ** int(default_parameters["host_death_density_exponent"][-2:]))

    # immune cell options
    initial_precursor_cell_density = NumericProperty(default_parameters["initial_precursor_cell_density"])
    immune_cell_proliferation_rate = NumericProperty(default_parameters["immune_cell_proliferation_rate"])
    immune_cell_half_maximum_growth = NumericProperty(default_parameters["immune_cell_half_maximum_growth"])
    effector_decay_rate = NumericProperty(default_parameters["effector_decay_rate"])
    memory_cell_conversion_rate = NumericProperty(default_parameters["memory_cell_conversion_rate"])

    # antibiotic option
    antibiotic_mean_concentration = NumericProperty(default_parameters["antibiotic_mean_concentration"])

    # treatment types
    treatment_type = StringProperty("")

    # treatment options
    classic_delay = NumericProperty(default_parameters["classic_delay"])
    classic_duration = NumericProperty(default_parameters["classic_duration"])
    adaptive_symptoms_at_bacteria_density_value = NumericProperty(
        default_parameters["adaptive_symptoms_at_bacteria_density_value"])
    adaptive_symptoms_at_bacteria_density_exponent = NumericProperty(
        10 ** int(default_parameters["adaptive_symptoms_at_bacteria_density_exponent"][-1:]))
    adaptive_symptoms_at_bacteria_density = NumericProperty(
        default_parameters["adaptive_symptoms_at_bacteria_density_value"] *
        10 ** int(default_parameters["adaptive_symptoms_at_bacteria_density_exponent"][-1:]))
    user_administer = BooleanProperty(default_parameters["user_administer"])

    ######################
    # Scenario 2 variables
    ######################

    # function instances
    clock_add_points_gut_1 = None
    clock_add_points_gut_2 = None
    clock_add_points_gut_3 = None
    data_generator_instance_gut_1 = None
    data_generator_instance_gut_2 = None
    data_generator_instance_gut_3 = None

    # enterotype 1 plots
    bacteroides_ent_1_plot = global_variables.BACTERIA_ASSORTMENT_GUT1.get_bacteria()["Bacteroides"].get_plot()
    faecalibacterium_ent_1_plot = global_variables.BACTERIA_ASSORTMENT_GUT1.get_bacteria()[
        "Faecalibacterium"].get_plot()
    roseburia_ent_1_plot = global_variables.BACTERIA_ASSORTMENT_GUT1.get_bacteria()["Roseburia"].get_plot()
    bifidobacterium_ent_1_plot = global_variables.BACTERIA_ASSORTMENT_GUT1.get_bacteria()["Bifidobacterium"].get_plot()
    lachnospiraceae_ent_1_plot = global_variables.BACTERIA_ASSORTMENT_GUT1.get_bacteria()["Lachnospiraceae"].get_plot()
    parabacteroides_ent_1_plot = global_variables.BACTERIA_ASSORTMENT_GUT1.get_bacteria()["Parabacteroides"].get_plot()
    alistipes_ent_1_plot = global_variables.BACTERIA_ASSORTMENT_GUT1.get_bacteria()["Alistipes"].get_plot()
    anaerostipes_ent_1_plot = global_variables.BACTERIA_ASSORTMENT_GUT1.get_bacteria()["Anaerostipes"].get_plot()
    acidaminococcus_ent_1_plot = global_variables.BACTERIA_ASSORTMENT_GUT1.get_bacteria()["Acidaminococcus"].get_plot()
    collinsella_ent_1_plot = global_variables.BACTERIA_ASSORTMENT_GUT1.get_bacteria()["Collinsella"].get_plot()

    bacteria_plots_ent_1 = {"bacteroides": bacteroides_ent_1_plot, "faecalibacterium": faecalibacterium_ent_1_plot,
                            "roseburia": roseburia_ent_1_plot, "bifidobacterium": bifidobacterium_ent_1_plot,
                            "lachnospiraceae": lachnospiraceae_ent_1_plot,
                            "parabacteroides": parabacteroides_ent_1_plot,
                            "alistipes": alistipes_ent_1_plot, "anaerostipes": anaerostipes_ent_1_plot,
                            "acidaminococcus": acidaminococcus_ent_1_plot,
                            "collinsella": collinsella_ent_1_plot}

    antibiotic_plots_ent_1 = {"lincosamides": global_variables.ANTIBIOTIC_ASSORTMENT_GUT1.get_antibiotics()[
        "Lincosamides"].get_plot(),
                              "macrolides": global_variables.ANTIBIOTIC_ASSORTMENT_GUT1.get_antibiotics()[
        "Macrolides"].get_plot(),
                              "penicillins": global_variables.ANTIBIOTIC_ASSORTMENT_GUT1.get_antibiotics()[
        "Penicillins"].get_plot(),
                              "quinolones": global_variables.ANTIBIOTIC_ASSORTMENT_GUT1.get_antibiotics()[
        "Quinolones"].get_plot(),
                              "streptogramins": global_variables.ANTIBIOTIC_ASSORTMENT_GUT1.get_antibiotics()[
        "Streptogramins"].get_plot(),
                              "sulfonamides": global_variables.ANTIBIOTIC_ASSORTMENT_GUT1.get_antibiotics()[
        "Sulfonamides"].get_plot(),
                              "tetacyclines": global_variables.ANTIBIOTIC_ASSORTMENT_GUT1.get_antibiotics()[
        "Tetacyclines"].get_plot(),
                              "trimethoprims": global_variables.ANTIBIOTIC_ASSORTMENT_GUT1.get_antibiotics()[
        "Trimethoprims"].get_plot()}

    # enterotype 2 plots
    prevotella_ent_2_plot = global_variables.BACTERIA_ASSORTMENT_GUT2.get_bacteria()["Prevotella"].get_plot()
    bacteroides_ent_2_plot = global_variables.BACTERIA_ASSORTMENT_GUT2.get_bacteria()["Bacteroides"].get_plot()
    faecalibacterium_ent_2_plot = global_variables.BACTERIA_ASSORTMENT_GUT2.get_bacteria()[
        "Faecalibacterium"].get_plot()
    lachnospiraceae_ent_2_plot = global_variables.BACTERIA_ASSORTMENT_GUT2.get_bacteria()["Lachnospiraceae"].get_plot()
    roseburia_ent_2_plot = global_variables.BACTERIA_ASSORTMENT_GUT2.get_bacteria()["Roseburia"].get_plot()
    collinsella_ent_2_plot = global_variables.BACTERIA_ASSORTMENT_GUT2.get_bacteria()["Collinsella"].get_plot()
    bifidobacterium_ent_2_plot = global_variables.BACTERIA_ASSORTMENT_GUT2.get_bacteria()["Bifidobacterium"].get_plot()
    alistipes_ent_2_plot = global_variables.BACTERIA_ASSORTMENT_GUT2.get_bacteria()["Alistipes"].get_plot()
    streptococcus_ent_2_plot = global_variables.BACTERIA_ASSORTMENT_GUT2.get_bacteria()["Streptococcus"].get_plot()
    coprococcus_ent_2_plot = global_variables.BACTERIA_ASSORTMENT_GUT2.get_bacteria()["Coprococcus"].get_plot()

    bacteria_plots_ent_2 = {"prevotella": prevotella_ent_2_plot, "bacteroides": bacteroides_ent_2_plot,
                            "faecalibacterium": faecalibacterium_ent_2_plot,
                            "lachnospiraceae": lachnospiraceae_ent_2_plot, "roseburia": roseburia_ent_2_plot,
                            "collinsella": collinsella_ent_2_plot, "bifidobacterium": bifidobacterium_ent_2_plot,
                            "alistipes": alistipes_ent_2_plot, "streptococcus": streptococcus_ent_2_plot,
                            "coprococcus": coprococcus_ent_2_plot}

    antibiotic_plots_ent_2 = {"lincosamides": global_variables.ANTIBIOTIC_ASSORTMENT_GUT2.get_antibiotics()[
        "Lincosamides"].get_plot(),
                              "macrolides": global_variables.ANTIBIOTIC_ASSORTMENT_GUT2.get_antibiotics()[
        "Macrolides"].get_plot(),
                              "penicillins": global_variables.ANTIBIOTIC_ASSORTMENT_GUT2.get_antibiotics()[
        "Penicillins"].get_plot(),
                              "quinolones": global_variables.ANTIBIOTIC_ASSORTMENT_GUT2.get_antibiotics()[
        "Quinolones"].get_plot(),
                              "streptogramins": global_variables.ANTIBIOTIC_ASSORTMENT_GUT2.get_antibiotics()[
        "Streptogramins"].get_plot(),
                              "sulfonamides": global_variables.ANTIBIOTIC_ASSORTMENT_GUT2.get_antibiotics()[
        "Sulfonamides"].get_plot(),
                              "tetacyclines": global_variables.ANTIBIOTIC_ASSORTMENT_GUT2.get_antibiotics()[
        "Tetacyclines"].get_plot(),
                              "trimethoprims": global_variables.ANTIBIOTIC_ASSORTMENT_GUT2.get_antibiotics()[
        "Trimethoprims"].get_plot()}

    # enterotype 3 plots
    bacteroides_ent_3_plot = global_variables.BACTERIA_ASSORTMENT_GUT3.get_bacteria()["Bacteroides"].get_plot()
    bifidobacterium_ent_3_plot = global_variables.BACTERIA_ASSORTMENT_GUT3.get_bacteria()["Bifidobacterium"].get_plot()
    faecalibacterium_ent_3_plot = global_variables.BACTERIA_ASSORTMENT_GUT3.get_bacteria()[
        "Faecalibacterium"].get_plot()
    lachnospiraceae_ent_3_plot = global_variables.BACTERIA_ASSORTMENT_GUT3.get_bacteria()["Lachnospiraceae"].get_plot()
    alistipes_ent_3_plot = global_variables.BACTERIA_ASSORTMENT_GUT3.get_bacteria()["Alistipes"].get_plot()
    akkermansia_ent_3_plot = global_variables.BACTERIA_ASSORTMENT_GUT3.get_bacteria()["Akkermansia"].get_plot()
    ruminococcus_ent_3_plot = global_variables.BACTERIA_ASSORTMENT_GUT3.get_bacteria()["Ruminococcus"].get_plot()
    collinsella_ent_3_plot = global_variables.BACTERIA_ASSORTMENT_GUT3.get_bacteria()["Collinsella"].get_plot()
    blautia_ent_3_plot = global_variables.BACTERIA_ASSORTMENT_GUT3.get_bacteria()["Blautia"].get_plot()
    roseburia_ent_3_plot = global_variables.BACTERIA_ASSORTMENT_GUT3.get_bacteria()["Roseburia"].get_plot()

    bacteria_plots_ent_3 = {"bacteroides": bacteroides_ent_3_plot, "bifidobacterium": bifidobacterium_ent_3_plot,
                            "faecalibacterium": faecalibacterium_ent_3_plot,
                            "lachnospiraceae": lachnospiraceae_ent_3_plot, "alistipes": alistipes_ent_3_plot,
                            "akkermansia": akkermansia_ent_3_plot, "ruminococcus": ruminococcus_ent_3_plot,
                            "collinsella": collinsella_ent_3_plot, "blautia": blautia_ent_3_plot,
                            "roseburia": roseburia_ent_3_plot}

    antibiotic_plots_ent_3 = {"lincosamides": global_variables.ANTIBIOTIC_ASSORTMENT_GUT3.get_antibiotics()[
        "Lincosamides"].get_plot(),
                              "macrolides": global_variables.ANTIBIOTIC_ASSORTMENT_GUT3.get_antibiotics()[
        "Macrolides"].get_plot(),
                              "penicillins": global_variables.ANTIBIOTIC_ASSORTMENT_GUT3.get_antibiotics()[
        "Penicillins"].get_plot(),
                              "quinolones": global_variables.ANTIBIOTIC_ASSORTMENT_GUT3.get_antibiotics()[
        "Quinolones"].get_plot(),
                              "streptogramins": global_variables.ANTIBIOTIC_ASSORTMENT_GUT3.get_antibiotics()[
        "Streptogramins"].get_plot(),
                              "sulfonamides": global_variables.ANTIBIOTIC_ASSORTMENT_GUT3.get_antibiotics()[
        "Sulfonamides"].get_plot(),
                              "tetacyclines": global_variables.ANTIBIOTIC_ASSORTMENT_GUT3.get_antibiotics()[
        "Tetacyclines"].get_plot(),
                              "trimethoprims": global_variables.ANTIBIOTIC_ASSORTMENT_GUT3.get_antibiotics()[
        "Trimethoprims"].get_plot()}

    # enterotype 1 bacteria dead status
    bacteria_dead_status_ent_1 = {"bacteroides": False, "faecalibacterium": False, "roseburia": False,
                                  "bifidobacterium": False, "lachnospiraceae": False, "parabacteroides": False,
                                  "alistipes": False, "anaerostipes": False, "acidaminococcus": False,
                                  "collinsella": False}

    # enterotype 2 bacteria dead status
    bacteria_dead_status_ent_2 = {"prevotella": False, "bacteroides": False, "faecalibacterium": False,
                                  "lachnospiraceae": False, "roseburia": False, "collinsella": False,
                                  "bifidobacterium": False, "alistipes": False, "streptococcus": False,
                                  "coprococcus": False}

    # enterotype 3 bacteria dead status
    bacteria_dead_status_ent_3 = {"bacteroides": False, "bifidobacterium": False, "faecalibacterium": False,
                                  "lachnospiraceae": False, "alistipes": False, "akkermansia": False,
                                  "ruminococcus": False, "collinsella": False, "blautia": False, "roseburia": False}

    # scenario 2 bacteria densities
    # default densities calculated from:
    #   Arumugam et al (2011). Enterotypes of the human gut microbiome.
    #   Nature, 473(7346), 174–180. https://doi.org/10.1038/nature09944

    # enterotype 1 bacteria densities
    bacteria_densities_ent_1 = {"bacteroides": 5793111, "faecalibacterium": 1166914, "roseburia": 832900,
                                "bifidobacterium": 623495, "lachnospiraceae": 464077, "parabacteroides": 322975,
                                "alistipes": 221911, "anaerostipes": 208595, "acidaminococcus": 208271,
                                "collinsella": 157744}

    # enterotype 2 bacteria densities
    bacteria_densities_ent_2 = {"prevotella": 5141001, "bacteroides": 1591226, "faecalibacterium": 771497,
                                "lachnospiraceae": 706805, "roseburia": 461321, "collinsella": 381627,
                                "bifidobacterium": 255327, "alistipes": 246779, "streptococcus": 231394,
                                "coprococcus": 213016}

    # enterotype 3 bacteria densities
    bacteria_densities_ent_3 = {"bacteroides": 2585052, "bifidobacterium": 1571051, "faecalibacterium": 1449116,
                                "lachnospiraceae": 913032, "alistipes": 909552, "akkermansia": 588316,
                                "ruminococcus": 553816, "collinsella": 506545, "blautia": 455794, "roseburia": 467722}

    # growth rate for each bacteria
    # default growth rate is the same as in scenario 1
    bacteria_growth_rate = {"bacteroides": 3.3, "faecalibacterium": 3.3, "roseburia": 3.3,
                            "bifidobacterium": 3.3, "lachnospiraceae": 3.3, "parabacteroides": 3.3,
                            "alistipes": 3.3, "anaerostipes": 3.3, "acidaminococcus": 3.3,
                            "collinsella": 3.3, "prevotella": 3.3, "streptococcus": 3.3,
                            "coprococcus": 3.3, "akkermansia": 3.3, "ruminococcus": 3.3, "blautia": 3.3}

    # enterotype 1 nutrient consumption rates
    bacteria_nutrient_consumption_ent_1 = {"bacteroides": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["bacteroides"], 0.01, 5, bacteria_densities_ent_1["bacteroides"]),
                                           "faecalibacterium": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["faecalibacterium"], 0.01, 5, bacteria_densities_ent_1["faecalibacterium"]),
                                           "roseburia": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["roseburia"], 0.01, 5, bacteria_densities_ent_1["roseburia"]),
                                           "bifidobacterium": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["bifidobacterium"], 0.01, 5, bacteria_densities_ent_1["bifidobacterium"]),
                                           "lachnospiraceae": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["lachnospiraceae"], 0.01, 5, bacteria_densities_ent_1["lachnospiraceae"]),
                                           "parabacteroides": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["parabacteroides"], 0.01, 5, bacteria_densities_ent_1["parabacteroides"]),
                                           "alistipes": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["alistipes"], 0.01, 5, bacteria_densities_ent_1["alistipes"]),
                                           "anaerostipes": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["anaerostipes"], 0.01, 5, bacteria_densities_ent_1["anaerostipes"]),
                                           "acidaminococcus": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["acidaminococcus"], 0.01, 5, bacteria_densities_ent_1["acidaminococcus"]),
                                           "collinsella": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["collinsella"], 0.01, 5, bacteria_densities_ent_1["collinsella"])}

    # enterotype 2 nutrient consumption rates
    bacteria_nutrient_consumption_ent_2 = {"prevotella": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["prevotella"], 0.01, 5, bacteria_densities_ent_2["prevotella"]),
                                           "bacteroides": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["bacteroides"], 0.01, 5, bacteria_densities_ent_2["bacteroides"]),
                                           "faecalibacterium": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["faecalibacterium"], 0.01, 5, bacteria_densities_ent_2["faecalibacterium"]),
                                           "lachnospiraceae": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["lachnospiraceae"], 0.01, 5, bacteria_densities_ent_2["lachnospiraceae"]),
                                           "roseburia": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["roseburia"], 0.01, 5, bacteria_densities_ent_2["roseburia"]),
                                           "collinsella": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["collinsella"], 0.01, 5, bacteria_densities_ent_2["collinsella"]),
                                           "bifidobacterium": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["bifidobacterium"], 0.01, 5, bacteria_densities_ent_2["bifidobacterium"]),
                                           "alistipes": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["alistipes"], 0.01, 5, bacteria_densities_ent_2["alistipes"]),
                                           "streptococcus": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["streptococcus"], 0.01, 5, bacteria_densities_ent_2["streptococcus"]),
                                           "coprococcus": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["coprococcus"], 0.01, 5, bacteria_densities_ent_2["coprococcus"])}

    # enterotype 3 nutrient consumption rates
    bacteria_nutrient_consumption_ent_3 = {"bacteroides": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["bacteroides"], 0.01, 5, bacteria_densities_ent_3["bacteroides"]),
                                           "bifidobacterium": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["bifidobacterium"], 0.01, 5, bacteria_densities_ent_3["bifidobacterium"]),
                                           "faecalibacterium": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["faecalibacterium"], 0.01, 5, bacteria_densities_ent_3["faecalibacterium"]),
                                           "lachnospiraceae": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["lachnospiraceae"], 0.01, 5, bacteria_densities_ent_3["lachnospiraceae"]),
                                           "alistipes": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["alistipes"], 0.01, 5, bacteria_densities_ent_3["alistipes"]),
                                           "akkermansia": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["akkermansia"], 0.01, 5, bacteria_densities_ent_3["akkermansia"]),
                                           "ruminococcus": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["ruminococcus"], 0.01, 5, bacteria_densities_ent_3["ruminococcus"]),
                                           "collinsella": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["collinsella"], 0.01, 5, bacteria_densities_ent_3["collinsella"]),
                                           "blautia": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["blautia"], 0.01, 5, bacteria_densities_ent_3["blautia"]),
                                           "roseburia": nutrients_for_bacteria_duplication_eq(
        bacteria_growth_rate["roseburia"], 0.01, 5, bacteria_densities_ent_3["roseburia"])}

    # TODO bibliography, default inhibition (remove random)
    # default antibiotic inhibition for each bacteria
    bacteroides_default_antibiotic_inhibition = {"lincosamides": random(), "macrolides": random(),
                                                 "penicillins": random(), "quinolones": random(),
                                                 "streptogramins": random(), "sulfonamides": random(),
                                                 "tetacyclines": random(), "trimethoprims": random()}
    faecalibacterium_default_antibiotic_inhibition = {"lincosamides": random(), "macrolides": random(),
                                                      "penicillins": random(), "quinolones": random(),
                                                      "streptogramins": random(), "sulfonamides": random(),
                                                      "tetacyclines": random(), "trimethoprims": random()}
    roseburia_default_antibiotic_inhibition = {"lincosamides": random(), "macrolides": random(),
                                               "penicillins": random(), "quinolones": random(),
                                               "streptogramins": random(), "sulfonamides": random(),
                                               "tetacyclines": random(), "trimethoprims": random()}
    bifidobacterium_default_antibiotic_inhibition = {"lincosamides": random(), "macrolides": random(),
                                                     "penicillins": random(), "quinolones": random(),
                                                     "streptogramins": random(), "sulfonamides": random(),
                                                     "tetacyclines": random(), "trimethoprims": random()}
    lachnospiraceae_default_antibiotic_inhibition = {"lincosamides": random(), "macrolides": random(),
                                                     "penicillins": random(), "quinolones": random(),
                                                     "streptogramins": random(), "sulfonamides": random(),
                                                     "tetacyclines": random(), "trimethoprims": random()}
    parabacteroides_default_antibiotic_inhibition = {"lincosamides": random(), "macrolides": random(),
                                                     "penicillins": random(), "quinolones": random(),
                                                     "streptogramins": random(), "sulfonamides": random(),
                                                     "tetacyclines": random(), "trimethoprims": random()}
    alistipes_default_antibiotic_inhibition = {"lincosamides": random(), "macrolides": random(),
                                               "penicillins": random(), "quinolones": random(),
                                               "streptogramins": random(), "sulfonamides": random(),
                                               "tetacyclines": random(), "trimethoprims": random()}
    anaerostipes_default_antibiotic_inhibition = {"lincosamides": random(), "macrolides": random(),
                                                  "penicillins": random(), "quinolones": random(),
                                                  "streptogramins": random(), "sulfonamides": random(),
                                                  "tetacyclines": random(), "trimethoprims": random()}
    acidaminococcus_default_antibiotic_inhibition = {"lincosamides": random(), "macrolides": random(),
                                                     "penicillins": random(), "quinolones": random(),
                                                     "streptogramins": random(), "sulfonamides": random(),
                                                     "tetacyclines": random(), "trimethoprims": random()}
    collinsella_default_antibiotic_inhibition = {"lincosamides": random(), "macrolides": random(),
                                                 "penicillins": random(), "quinolones": random(),
                                                 "streptogramins": random(), "sulfonamides": random(),
                                                 "tetacyclines": random(), "trimethoprims": random()}
    prevotella_default_antibiotic_inhibition = {"lincosamides": random(), "macrolides": random(),
                                                "penicillins": random(), "quinolones": random(),
                                                "streptogramins": random(), "sulfonamides": random(),
                                                "tetacyclines": random(), "trimethoprims": random()}
    streptococcus_default_antibiotic_inhibition = {"lincosamides": random(), "macrolides": random(),
                                                   "penicillins": random(), "quinolones": random(),
                                                   "streptogramins": random(), "sulfonamides": random(),
                                                   "tetacyclines": random(), "trimethoprims": random()}
    coprococcus_default_antibiotic_inhibition = {"lincosamides": random(), "macrolides": random(),
                                                 "penicillins": random(), "quinolones": random(),
                                                 "streptogramins": random(), "sulfonamides": random(),
                                                 "tetacyclines": random(), "trimethoprims": random()}
    akkermansia_default_antibiotic_inhibition = {"lincosamides": random(), "macrolides": random(),
                                                 "penicillins": random(), "quinolones": random(),
                                                 "streptogramins": random(), "sulfonamides": random(),
                                                 "tetacyclines": random(), "trimethoprims": random()}
    ruminococcus_default_antibiotic_inhibition = {"lincosamides": random(), "macrolides": random(),
                                                  "penicillins": random(), "quinolones": random(),
                                                  "streptogramins": random(), "sulfonamides": random(),
                                                  "tetacyclines": random(), "trimethoprims": random()}
    blautia_default_antibiotic_inhibition = {"lincosamides": random(), "macrolides": random(),
                                             "penicillins": random(), "quinolones": random(),
                                             "streptogramins": random(), "sulfonamides": random(),
                                             "tetacyclines": random(), "trimethoprims": random()}

    # enterotype 1 current antibiotic inhibition for each bacteria
    bacteroides_antibiotic_inhibition_ent_1 = DictProperty(dict(bacteroides_default_antibiotic_inhibition))
    faecalibacterium_antibiotic_inhibition_ent_1 = DictProperty(dict(faecalibacterium_default_antibiotic_inhibition))
    roseburia_antibiotic_inhibition_ent_1 = DictProperty(dict(roseburia_default_antibiotic_inhibition))
    bifidobacterium_antibiotic_inhibition_ent_1 = DictProperty(dict(bifidobacterium_default_antibiotic_inhibition))
    lachnospiraceae_antibiotic_inhibition_ent_1 = DictProperty(dict(lachnospiraceae_default_antibiotic_inhibition))
    parabacteroides_antibiotic_inhibition_ent_1 = DictProperty(dict(parabacteroides_default_antibiotic_inhibition))
    alistipes_antibiotic_inhibition_ent_1 = DictProperty(dict(alistipes_default_antibiotic_inhibition))
    anaerostipes_antibiotic_inhibition_ent_1 = DictProperty(dict(anaerostipes_default_antibiotic_inhibition))
    acidaminococcus_antibiotic_inhibition_ent_1 = DictProperty(dict(acidaminococcus_default_antibiotic_inhibition))
    collinsella_antibiotic_inhibition_ent_1 = DictProperty(dict(collinsella_default_antibiotic_inhibition))

    # enterotype 2 current antibiotic inhibition for each bacteria
    prevotella_antibiotic_inhibition_ent_2 = DictProperty(dict(prevotella_default_antibiotic_inhibition))
    bacteroides_antibiotic_inhibition_ent_2 = DictProperty(dict(bacteroides_default_antibiotic_inhibition))
    faecalibacterium_antibiotic_inhibition_ent_2 = DictProperty(dict(faecalibacterium_default_antibiotic_inhibition))
    lachnospiraceae_antibiotic_inhibition_ent_2 = DictProperty(dict(lachnospiraceae_default_antibiotic_inhibition))
    roseburia_antibiotic_inhibition_ent_2 = DictProperty(dict(roseburia_default_antibiotic_inhibition))
    collinsella_antibiotic_inhibition_ent_2 = DictProperty(dict(collinsella_default_antibiotic_inhibition))
    bifidobacterium_antibiotic_inhibition_ent_2 = DictProperty(dict(bifidobacterium_default_antibiotic_inhibition))
    alistipes_antibiotic_inhibition_ent_2 = DictProperty(dict(alistipes_default_antibiotic_inhibition))
    streptococcus_antibiotic_inhibition_ent_2 = DictProperty(dict(streptococcus_default_antibiotic_inhibition))
    coprococcus_antibiotic_inhibition_ent_2 = DictProperty(dict(coprococcus_default_antibiotic_inhibition))

    # enterotype 3 current antibiotic inhibition for each bacteria
    bacteroides_antibiotic_inhibition_ent_3 = DictProperty(dict(bacteroides_default_antibiotic_inhibition))
    bifidobacterium_antibiotic_inhibition_ent_3 = DictProperty(dict(bifidobacterium_default_antibiotic_inhibition))
    faecalibacterium_antibiotic_inhibition_ent_3 = DictProperty(dict(faecalibacterium_default_antibiotic_inhibition))
    lachnospiraceae_antibiotic_inhibition_ent_3 = DictProperty(dict(lachnospiraceae_default_antibiotic_inhibition))
    alistipes_antibiotic_inhibition_ent_3 = DictProperty(dict(alistipes_default_antibiotic_inhibition))
    akkermansia_antibiotic_inhibition_ent_3 = DictProperty(dict(akkermansia_default_antibiotic_inhibition))
    ruminococcus_antibiotic_inhibition_ent_3 = DictProperty(dict(ruminococcus_default_antibiotic_inhibition))
    collinsella_antibiotic_inhibition_ent_3 = DictProperty(dict(collinsella_default_antibiotic_inhibition))
    blautia_antibiotic_inhibition_ent_3 = DictProperty(dict(blautia_default_antibiotic_inhibition))
    roseburia_antibiotic_inhibition_ent_3 = DictProperty(dict(roseburia_default_antibiotic_inhibition))

    # enterotype 1 current antibiotic concentrations and uptake
    antibiotic_concentrations_ent_1 = DictProperty({"lincosamides": 6, "macrolides": 6,
                                                    "penicillins": 6, "quinolones": 6,
                                                    "streptogramins": 6, "sulfonamides": 6,
                                                    "tetacyclines": 6, "trimethoprims": 6})
    antibiotic_uptake_ent_1 = DictProperty({"lincosamides": 0, "macrolides": 0,
                                            "penicillins": 0, "quinolones": 0,
                                            "streptogramins": 0, "sulfonamides": 0,
                                            "tetacyclines": 0, "trimethoprims": 0})

    # enterotype 2 current antibiotic concentrations and uptake
    antibiotic_concentrations_ent_2 = DictProperty({"lincosamides": 6, "macrolides": 6,
                                                    "penicillins": 6, "quinolones": 6,
                                                    "streptogramins": 6, "sulfonamides": 6,
                                                    "tetacyclines": 6, "trimethoprims": 6})
    antibiotic_uptake_ent_2 = DictProperty({"lincosamides": 0, "macrolides": 0,
                                            "penicillins": 0, "quinolones": 0,
                                            "streptogramins": 0, "sulfonamides": 0,
                                            "tetacyclines": 0, "trimethoprims": 0})

    # enterotype 3 current antibiotic concentrations and uptake
    antibiotic_concentrations_ent_3 = DictProperty({"lincosamides": 6, "macrolides": 6,
                                                    "penicillins": 6, "quinolones": 6,
                                                    "streptogramins": 6, "sulfonamides": 6,
                                                    "tetacyclines": 6, "trimethoprims": 6})
    antibiotic_uptake_ent_3 = DictProperty({"lincosamides": 0, "macrolides": 0,
                                            "penicillins": 0, "quinolones": 0,
                                            "streptogramins": 0, "sulfonamides": 0,
                                            "tetacyclines": 0, "trimethoprims": 0})

    def start_simulation(self, graph_layout_instance, start_button, restart_button, pause_button, popup_warning, root):
        """
        Starts simulation
        
        PARAMETERS:
            graph_layout_instance : GraphsLayout object
                GraphsLayout object
            start_button : start_button object
                start_button id
            restart_button : restart_button object
                restart_button id
            pause_button : pause_button object
                pause_button id
            popup_warning : popup_warning object
                popup_warning id
            root : root object
                root id
        """
        if self.current_scenario == "scenario_1":
            if self.treatment_type != "":
                # buttons
                start_button.state = "down"
                start_button.disabled = True
                start_button.sliders_toggles_enabled = self.enable_disable("disable")
                restart_button.disabled = False
                pause_button.disabled = False

                # death limit
                self.death_limit.points = [(0, self.host_death_density), (10000, self.host_death_density)]

                # data generator
                self.data_generator_instance = self.data_generator()

                # clock
                self.clock_add_points = Clock.schedule_interval(self.add_points(
                    self.data_generator_instance, self.sensitive_bacteria_plot, self.resistant_bacteria_plot,
                    self.antibiotic_plot, self.immune_system_plot, self.total_bacteria_plot), 1/60.)

                graph_layout_instance.restart_in_progress_scenario_1_property = False
                graph_layout_instance.simulation_going_scenario_1_property = True

            else:
                popup_warning.show_message(global_variables.LANGUAGE["popup_missing_treatment_title"],
                                           global_variables.LANGUAGE["popup_missing_treatment_message"])

        elif self.current_scenario == "scenario_2":
            if self.current_microbiome != "":
                # buttons
                start_button.state = "down"
                start_button.disabled = True
                restart_button.disabled = False
                pause_button.disabled = False

                if self.current_microbiome == "gut_enterotype_1":
                    start_button.bacteria_buttons_ent_1_enabled = self.enable_disable("disable")

                    # data generator
                    self.data_generator_instance_gut_1 = self.data_generator()

                    # clock
                    self.clock_add_points_gut_1 = Clock.schedule_interval(self.add_points_scenario2(
                        self.data_generator_instance_gut_1, self.bacteria_plots_ent_1, self.antibiotic_plots_ent_1),
                        1/60.)

                    graph_layout_instance.restart_in_progress_scenario_2_ent_1_property = False
                    graph_layout_instance.simulation_going_scenario_2_ent_1_property = True

                elif self.current_microbiome == "gut_enterotype_2":
                    start_button.bacteria_buttons_ent_2_enabled = self.enable_disable("disable")

                    # data generator
                    self.data_generator_instance_gut_2 = self.data_generator()

                    # clock
                    self.clock_add_points_gut_2 = Clock.schedule_interval(self.add_points_scenario2(
                        self.data_generator_instance_gut_2, self.bacteria_plots_ent_2, self.antibiotic_plots_ent_2),
                        1/60.)

                    graph_layout_instance.restart_in_progress_scenario_2_ent_2_property = False
                    graph_layout_instance.simulation_going_scenario_2_ent_2_property = True

                elif self.current_microbiome == "gut_enterotype_3":
                    start_button.bacteria_buttons_ent_3_enabled = self.enable_disable("disable")

                    # data generator
                    self.data_generator_instance_gut_3 = self.data_generator()

                    # clock
                    self.clock_add_points_gut_3 = Clock.schedule_interval(self.add_points_scenario2(
                        self.data_generator_instance_gut_3, self.bacteria_plots_ent_3, self.antibiotic_plots_ent_3),
                        1/60.)

                    graph_layout_instance.restart_in_progress_scenario_2_ent_3_property = False
                    graph_layout_instance.simulation_going_scenario_2_ent_3_property = True

            else:
                popup_warning.show_message(global_variables.LANGUAGE["popup_missing_microbiome_title"],
                                           global_variables.LANGUAGE["popup_missing_microbiome_message"])

    def pause_simulation(self, graph_layout_instance, pause_button):
        """
        Pause/unpause simulation
        
        PARAMETERS:
            graph_layout_instance : GraphsLayout object
                GraphsLayout object
            pause_button : pause_button object
                pause_button id
        """
        if pause_button.was_pressed:
            if self.current_scenario == "scenario_1":
                if not graph_layout_instance.restart_in_progress_scenario_1_property:
                    # if not paused, cancel schedule
                    if (not graph_layout_instance.pause_scenario_1_property and
                            graph_layout_instance.simulation_going_scenario_1_property):
                        self.clock_add_points.cancel()
                        graph_layout_instance.simulation_going_scenario_1_property = False
                        graph_layout_instance.pause_scenario_1_property = True
                    # if paused, restart add_points schedule
                    elif (graph_layout_instance.pause_scenario_1_property
                          and not graph_layout_instance.simulation_going_scenario_1_property):
                        self.clock_add_points = Clock.schedule_interval(self.add_points(
                            self.data_generator_instance, self.sensitive_bacteria_plot, self.resistant_bacteria_plot,
                            self.antibiotic_plot, self.immune_system_plot, self.total_bacteria_plot), 1/60.)
                        graph_layout_instance.simulation_going_scenario_1_property = True
                        graph_layout_instance.pause_scenario_1_property = False
                else:
                    graph_layout_instance.pause_scenario_1_property = False

            elif self.current_scenario == "scenario_2":
                if self.current_microbiome == "gut_enterotype_1":
                    if not graph_layout_instance.restart_in_progress_scenario_2_ent_1_property:
                        # if not paused, cancel schedule
                        if (not graph_layout_instance.pause_scenario_2_ent_1_property and
                                graph_layout_instance.simulation_going_scenario_2_ent_1_property):
                            self.clock_add_points_gut_1.cancel()
                            graph_layout_instance.simulation_going_scenario_2_ent_1_property = False
                            graph_layout_instance.pause_scenario_2_ent_1_property = True
                        # if paused, restart add_points schedule
                        elif (graph_layout_instance.pause_scenario_2_ent_1_property
                              and not graph_layout_instance.simulation_going_scenario_2_ent_1_property):
                            self.clock_add_points_gut_1 = Clock.schedule_interval(self.add_points_scenario2(
                                self.data_generator_instance_gut_1, self.bacteria_plots_ent_1,
                                self.antibiotic_plots_ent_1), 1/60.)
                            graph_layout_instance.simulation_going_scenario_2_ent_1_property = True
                            graph_layout_instance.pause_scenario_2_ent_1_property = False
                    else:
                        graph_layout_instance.pause_scenario_2_ent_1_property = False

                elif self.current_microbiome == "gut_enterotype_2":
                    if not graph_layout_instance.restart_in_progress_scenario_2_ent_2_property:
                        # if not paused, cancel schedule
                        if (not graph_layout_instance.pause_scenario_2_ent_2_property and
                                graph_layout_instance.simulation_going_scenario_2_ent_2_property):
                            self.clock_add_points_gut_2.cancel()
                            graph_layout_instance.simulation_going_scenario_2_ent_2_property = False
                            graph_layout_instance.pause_scenario_2_ent_2_property = True
                        # if paused, restart add_points schedule
                        elif (graph_layout_instance.pause_scenario_2_ent_2_property
                              and not graph_layout_instance.simulation_going_scenario_2_ent_2_property):
                            self.clock_add_points_gut_2 = Clock.schedule_interval(self.add_points_scenario2(
                                self.data_generator_instance_gut_2, self.bacteria_plots_ent_2,
                                self.antibiotic_plots_ent_2), 1/60.)
                            graph_layout_instance.simulation_going_scenario_2_ent_2_property = True
                            graph_layout_instance.pause_scenario_2_ent_2_property = False
                    else:
                        graph_layout_instance.pause_scenario_2_ent_2_property = False

                elif self.current_microbiome == "gut_enterotype_3":
                    if not graph_layout_instance.restart_in_progress_scenario_2_ent_3_property:
                        # if not paused, cancel schedule
                        if (not graph_layout_instance.pause_scenario_2_ent_3_property and
                                graph_layout_instance.simulation_going_scenario_2_ent_3_property):
                            self.clock_add_points_gut_3.cancel()
                            graph_layout_instance.simulation_going_scenario_2_ent_3_property = False
                            graph_layout_instance.pause_scenario_2_ent_3_property = True
                        # if paused, restart add_points schedule
                        elif (graph_layout_instance.pause_scenario_2_ent_3_property
                              and not graph_layout_instance.simulation_going_scenario_2_ent_3_property):
                            self.clock_add_points_gut_3 = Clock.schedule_interval(self.add_points_scenario2(
                                self.data_generator_instance_gut_3, self.bacteria_plots_ent_3,
                                self.antibiotic_plots_ent_3), 1/60.)
                            graph_layout_instance.simulation_going_scenario_2_ent_3_property = True
                            graph_layout_instance.pause_scenario_2_ent_3_property = False
                    else:
                        graph_layout_instance.pause_scenario_2_ent_3_property = False

            pause_button.was_pressed = False

    def restart_simulation(self, graph_layout_instance, start_button, restart_button, pause_button):
        """
        Restarts simulation
        
        PARAMETERS:
            graph_layout_instance : GraphsLayout object
                GraphsLayout object
            start_button : start_button object
                start_button id
            restart_button : restart_button object
                restart_button id
            pause_button : pause_button object
                pause_button id
        """
        # buttons
        restart_button.disabled = True
        start_button.state = "normal"
        start_button.disabled = False
        pause_button.disabled = True
        pause_button.was_pressed = True
        pause_button.pause_value = False

        if self.current_scenario == "scenario_1":
            # re-enable sliders and toggles
            start_button.sliders_toggles_enabled = self.enable_disable("enable")

            # cancel add_points clock
            self.clock_add_points.cancel()

            # reset (x,y) points
            self.sensitive_bacteria_plot.points = [(0, 1)]
            self.resistant_bacteria_plot.points = [(0, 1)]
            self.total_bacteria_plot.points = [(0, 1)]
            self.immune_system_plot.points = [(0, 1)]
            self.antibiotic_plot.points = [(0, 0)]
            self.death_limit.points = []

            # resets xy resizes
            global_variables.BACTERIA_ASSORTMENT.get_graph_widget().xmax = 10
            global_variables.BACTERIA_ASSORTMENT.get_graph_widget().x_ticks_major = 1
            global_variables.BACTERIA_ASSORTMENT.get_graph_widget().ymax = 10**3
            global_variables.ANTIBIOTIC_ASSORTMENT.get_graph_widget().xmax = 10
            global_variables.ANTIBIOTIC_ASSORTMENT.get_graph_widget().x_ticks_major = 1
            global_variables.ANTIBIOTIC_ASSORTMENT.get_graph_widget().ymax = 20
            global_variables.ANTIBIOTIC_ASSORTMENT.get_graph_widget().y_ticks_major = 4

            # allows pause_simulation to not activate when a restart is made
            graph_layout_instance.restart_in_progress_scenario_1_property = True
            graph_layout_instance.simulation_going_scenario_1_property = False

        elif self.current_scenario == "scenario_2":
            if self.current_microbiome == "gut_enterotype_1":
                # re-enable buttons
                start_button.bacteria_buttons_ent_1_enabled = self.enable_disable("enable")

                # cancel add_points clock
                self.clock_add_points_gut_1.cancel()

                # resets bacteria death status
                for bacteria in self.bacteria_dead_status_ent_1:
                    self.bacteria_dead_status_ent_1[bacteria] = False

                # reset (x,y) points
                for bacteria_plot in self.bacteria_plots_ent_1.itervalues():
                    bacteria_plot.points = [(0, 1)]
                for antibiotic_plot in self.antibiotic_plots_ent_1.itervalues():
                    antibiotic_plot.points = [(0, 0)]

                # resets xy resizes
                global_variables.BACTERIA_ASSORTMENT_GUT1.get_graph_widget().xmax = 10
                global_variables.BACTERIA_ASSORTMENT_GUT1.get_graph_widget().x_ticks_major = 1
                global_variables.BACTERIA_ASSORTMENT_GUT1.get_graph_widget().ymax = 1
                global_variables.ANTIBIOTIC_ASSORTMENT_GUT1.get_graph_widget().xmax = 10
                global_variables.ANTIBIOTIC_ASSORTMENT_GUT1.get_graph_widget().x_ticks_major = 1
                global_variables.ANTIBIOTIC_ASSORTMENT_GUT1.get_graph_widget().ymax = 20
                global_variables.ANTIBIOTIC_ASSORTMENT_GUT1.get_graph_widget().y_ticks_major = 4

                # allows pause_simulation to not activate when a restart is made
                graph_layout_instance.restart_in_progress_scenario_2_ent_1_property = True
                graph_layout_instance.simulation_going_scenario_2_ent_1_property = False
            elif self.current_microbiome == "gut_enterotype_2":
                # re-enable buttons
                start_button.bacteria_buttons_ent_2_enabled = self.enable_disable("enable")

                # cancel add_points clock
                self.clock_add_points_gut_2.cancel()

                # resets bacteria death status
                for bacteria in self.bacteria_dead_status_ent_2:
                    self.bacteria_dead_status_ent_2[bacteria] = False

                # reset (x,y) points
                for bacteria_plot in self.bacteria_plots_ent_2.itervalues():
                    bacteria_plot.points = [(0, 1)]
                for antibiotic_plot in self.antibiotic_plots_ent_2.itervalues():
                    antibiotic_plot.points = [(0, 0)]

                # resets xy resizes
                global_variables.BACTERIA_ASSORTMENT_GUT2.get_graph_widget().xmax = 10
                global_variables.BACTERIA_ASSORTMENT_GUT2.get_graph_widget().x_ticks_major = 1
                global_variables.BACTERIA_ASSORTMENT_GUT2.get_graph_widget().ymax = 1
                global_variables.ANTIBIOTIC_ASSORTMENT_GUT2.get_graph_widget().xmax = 10
                global_variables.ANTIBIOTIC_ASSORTMENT_GUT2.get_graph_widget().x_ticks_major = 1
                global_variables.ANTIBIOTIC_ASSORTMENT_GUT2.get_graph_widget().ymax = 20
                global_variables.ANTIBIOTIC_ASSORTMENT_GUT2.get_graph_widget().y_ticks_major = 4

                # allows pause_simulation to not activate when a restart is made
                graph_layout_instance.restart_in_progress_scenario_2_ent_2_property = True
                graph_layout_instance.simulation_going_scenario_2_ent_2_property = False
            elif self.current_microbiome == "gut_enterotype_3":
                # re-enable buttons
                start_button.bacteria_buttons_ent_3_enabled = self.enable_disable("enable")

                # cancel add_points clock
                self.clock_add_points_gut_3.cancel()

                # resets bacteria death status
                for bacteria in self.bacteria_dead_status_ent_3:
                    self.bacteria_dead_status_ent_3[bacteria] = False

                # reset (x,y) points
                for bacteria_plot in self.bacteria_plots_ent_3.itervalues():
                    bacteria_plot.points = [(0, 1)]
                for antibiotic_plot in self.antibiotic_plots_ent_3.itervalues():
                    antibiotic_plot.points = [(0, 0)]

                # resets xy resizes
                global_variables.BACTERIA_ASSORTMENT_GUT3.get_graph_widget().xmax = 10
                global_variables.BACTERIA_ASSORTMENT_GUT3.get_graph_widget().x_ticks_major = 1
                global_variables.BACTERIA_ASSORTMENT_GUT3.get_graph_widget().ymax = 1
                global_variables.ANTIBIOTIC_ASSORTMENT_GUT3.get_graph_widget().xmax = 10
                global_variables.ANTIBIOTIC_ASSORTMENT_GUT3.get_graph_widget().x_ticks_major = 1
                global_variables.ANTIBIOTIC_ASSORTMENT_GUT3.get_graph_widget().ymax = 20
                global_variables.ANTIBIOTIC_ASSORTMENT_GUT3.get_graph_widget().y_ticks_major = 4

                # allows pause_simulation to not activate when a restart is made
                graph_layout_instance.restart_in_progress_scenario_2_ent_3_property = True
                graph_layout_instance.simulation_going_scenario_2_ent_3_property = False

    def save(self, graphs_box_id, directory, popup_warning_id, popup_warning_title_and_message):
        """
        Saves current plot data to a csv file and current options in use to a txt file
        
        PARAMETERS:
            graphs_box_id: object
                Graphs container object
            popup_warning_id : object
                PopupWarning object
            directory : str
                Directory where files should be saved
            popup_warning_title_and_message: Iterable[str]
                Iterable containing 2 elements [popup_saving_title, popup_saving_message]
        """
        # checks if directory exists
        if not os.path.isdir(directory):
            os.mkdir(directory)

        current_datetime = datetime.datetime.now()
        current_datetime = "-".join([str(current_datetime.year), str(current_datetime.month),
                                     str(current_datetime.day)]) + "_" + \
                           "-".join([str(current_datetime.hour), str(current_datetime.minute),
                                     str(current_datetime.second)])

        if self.current_scenario == "scenario_1":
            # saves screenshot of graph
            graphs_box_id.export_to_png(os.path.join(directory, "scenario_1_screenshot_" + current_datetime + ".png"))

            # save csv file with x-axis and y-axis values for each plot
            with open(os.path.join(directory, "scenario_1_plot_points_" + current_datetime + ".csv"), "wb") as csv_file:
                csv_writer = csv.writer(csv_file)

                # csv header
                csv_writer.writerow(["Time", "Total Bacteria Density", "Sensitive Bacteria Density",
                                     "Resistant Bacteria Density", "Immune System Density", "Antibiotic Concentration"])

                # csv rows
                # ignores first value, as it exists only to allow plot instantiation (first y value must not be zero)
                for i in xrange(len(self.total_bacteria_plot.points[1:])):
                    # gets time from total_bacteria_plot and y values for each plot
                    csv_writer.writerow([self.total_bacteria_plot.points[i + 1][0],  # x value, time
                                         self.total_bacteria_plot.points[i + 1][1],  # y value
                                         self.sensitive_bacteria_plot.points[i + 1][1],  # y value
                                         self.resistant_bacteria_plot.points[i + 1][1],  # y value
                                         self.immune_system_plot.points[i + 1][1],  # y value
                                         self.antibiotic_plot.points[i + 1][1]  # y value
                                         ])

            # save options used
            with open(os.path.join(directory, "scenario_1_options_used_" + current_datetime + ".txt"), "wb"
                      ) as options_used_file:
                options_used_file.writelines([
                    global_variables.LANGUAGE["antibiotic_sensitive_bacteria_label"].strip() + ", " +
                    global_variables.LANGUAGE["bacteria_initial_density"] + ": " + str(self.sensitive_initial_density) +
                    "\n",
                    global_variables.LANGUAGE["antibiotic_sensitive_bacteria_label"].strip() + ", " +
                    global_variables.LANGUAGE["bacteria_growth_rate"] + ": " + str(self.sensitive_growth_rate) + "\n",
                    global_variables.LANGUAGE["antibiotic_sensitive_bacteria_label"].strip() + ", " +
                    global_variables.LANGUAGE["bacteria_antibiotic_inhibition"] + ": " +
                    str(self.sensitive_antibiotic_inhibition) + "\n",
                    global_variables.LANGUAGE["antibiotic_resistant_bacteria_label"].strip() + ", " +
                    global_variables.LANGUAGE["bacteria_initial_density"] + ": " + str(self.resistant_initial_density) +
                    "\n",
                    global_variables.LANGUAGE["antibiotic_resistant_bacteria_label"].strip() + ", " +
                    global_variables.LANGUAGE["bacteria_growth_rate"] + ": " + str(self.resistant_growth_rate) + "\n",
                    global_variables.LANGUAGE["antibiotic_resistant_bacteria_label"].strip() + ", " +
                    global_variables.LANGUAGE["bacteria_antibiotic_inhibition"] + ": " +
                    str(self.resistant_antibiotic_inhibition) + "\n",
                    global_variables.LANGUAGE["both_bacteria_label"].strip() + ", " +
                    global_variables.LANGUAGE["both_bacteria_lymphocyte_inhibition"] + ": " +
                    str(self.lymphocyte_inhibition) + "\n",
                    global_variables.LANGUAGE["both_bacteria_label"].strip() + ", " +
                    global_variables.LANGUAGE["both_bacteria_density_death"] + ": " +
                    str(self.host_death_density) + "\n",
                    global_variables.LANGUAGE["immune_system_label"].strip() + ", " +
                    global_variables.LANGUAGE["immune_system_initial_density"] + ": " +
                    str(self.initial_precursor_cell_density) + "\n",
                    global_variables.LANGUAGE["immune_system_label"].strip() + ", " +
                    global_variables.LANGUAGE["immune_system_proliferation_rate"] + ": " +
                    str(self.immune_cell_proliferation_rate) + "\n",
                    global_variables.LANGUAGE["immune_system_label"].strip() + ", " +
                    global_variables.LANGUAGE["immune_system_half_maximum_growth"] + ": " +
                    str(self.immune_cell_half_maximum_growth) + "\n",
                    global_variables.LANGUAGE["immune_system_label"].strip() + ", " +
                    global_variables.LANGUAGE["immune_system_effector_decay_rate"] + ": " +
                    str(self.effector_decay_rate) + "\n",
                    global_variables.LANGUAGE["immune_system_label"].strip() + ", " +
                    global_variables.LANGUAGE["immune_system_memory_conversion"] + ": " +
                    str(self.memory_cell_conversion_rate) + "\n",
                    global_variables.LANGUAGE["antibiotic_label"].strip() + ", " +
                    global_variables.LANGUAGE["antibiotic_mean_concentration"] + ": " +
                    str(self.antibiotic_mean_concentration) + "\n",
                    global_variables.LANGUAGE["antibiotic_label"].strip() + ", " +
                    global_variables.LANGUAGE["toggle_classic"] + ", " +
                    global_variables.LANGUAGE["treatment_classic_delay"] + ": " + str(self.classic_delay) + "\n",
                    global_variables.LANGUAGE["antibiotic_label"].strip() + ", " +
                    global_variables.LANGUAGE["toggle_classic"] + ", " +
                    global_variables.LANGUAGE["treatment_classic_duration"] + ": " + str(self.classic_duration) + "\n",
                    global_variables.LANGUAGE["antibiotic_label"].strip() + ", " +
                    global_variables.LANGUAGE["toggle_adaptive"] + ", " +
                    global_variables.LANGUAGE["treatment_adaptive_symptoms"] + ": " +
                    str(self.adaptive_symptoms_at_bacteria_density) + "\n",
                    global_variables.LANGUAGE["antibiotic_label"].strip() + ", " +
                    global_variables.LANGUAGE["toggle_user"] + ", " +
                    global_variables.LANGUAGE["treatment_user_administer"] + ": " + str(self.user_administer)
                ])

            # popup warning message
            popup_warning_id.show_message(*popup_warning_title_and_message)

        elif self.current_scenario == "scenario_2":
            if self.current_microbiome == "gut_enterotype_1":
                # saves screenshot of graph
                graphs_box_id.export_to_png(os.path.join(directory, "scenario_2_gut_enterotype_1_screenshot_" +
                                                         current_datetime + ".png"))

                # save csv file with x-axis and y-axis values for each plot
                with open(os.path.join(directory, "scenario_2_gut_enterotype_1_plot_points_" + current_datetime +
                                                  ".csv"), "wb") as csv_file:
                    csv_writer = csv.writer(csv_file)

                    # csv header
                    csv_writer.writerow(["Time", "Bacteroides Density", "Faecalibacterium Density",
                                         "Roseburia Density", "Bifidobacterium Density",
                                         "Lachnospiraceae Density", "Parabacteroides Density", "Alistipes Density",
                                         "Anaerostipes Density", "Acidaminococcus Density", "Collinsella Density"])

                    # csv rows
                    # ignores first value as it exists only to allow plot instantiation (first y value must not be zero)
                    for i in xrange(len(self.bacteria_plots_ent_1["bacteroides"].points[1:])):
                        # gets time from bacteroides plot and y values for each plot
                        csv_writer.writerow([self.bacteria_plots_ent_1["bacteroides"].points[i + 1][0],  # x value, time
                                             self.bacteria_plots_ent_1["bacteroides"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_1["faecalibacterium"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_1["roseburia"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_1["bifidobacterium"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_1["lachnospiraceae"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_1["parabacteroides"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_1["alistipes"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_1["anaerostipes"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_1["acidaminococcus"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_1["collinsella"].points[i + 1][1],  # y value
                                             ])

                # save options used
                with open(os.path.join(directory, "scenario_2_gut_enterotype_1_options_used_" + current_datetime +
                                                  ".txt"), "wb") as options_used_file:

                    antibiotic_concentration_options = ""
                    go_for_antibiotics = True  # allows for antibiotic_concentration_options to be filled just once
                    for bacteria in sorted(self.bacteria_plots_ent_1):
                        for antibiotic in sorted(self.antibiotic_plots_ent_1):
                            options_used_file.writelines([
                                global_variables.LANGUAGE[bacteria] + ", " +
                                global_variables.LANGUAGE[antibiotic] + " inhibition: " +
                                str(getattr(self, bacteria + "_antibiotic_inhibition_ent_1")[antibiotic]) + "\n"
                            ])

                            if go_for_antibiotics:
                                antibiotic_concentration_options +=\
                                    global_variables.LANGUAGE[antibiotic] + " concentration: " +\
                                    str(self.antibiotic_concentrations_ent_1[antibiotic]) + "\n"

                        go_for_antibiotics = False

                    options_used_file.writelines([antibiotic_concentration_options])

                # popup warning message
                popup_warning_id.show_message(*popup_warning_title_and_message)

            elif self.current_microbiome == "gut_enterotype_2":
                # saves screenshot of graph
                graphs_box_id.export_to_png(os.path.join(directory, "scenario_2_gut_enterotype_2_screenshot_" +
                                                         current_datetime + ".png"))

                # save csv file with x-axis and y-axis values for each plot
                with open(os.path.join(directory, "scenario_2_gut_enterotype_2_plot_points_" + current_datetime +
                                                  ".csv"), "wb") as csv_file:
                    csv_writer = csv.writer(csv_file)

                    # csv header
                    csv_writer.writerow(["Time", "Prevotella Density", "Bacteroides Density",
                                         "Faecalibacterium Density", "Lachnospiraceae Density",
                                         "Roseburia Density", "Collinsella Density", "Bifidobacterium Density",
                                         "Alistipes Density", "Streptococcus Density", "Coprococcus Density"])

                    # csv rows
                    # ignores first value as it exists only to allow plot instantiation (first y value must not be zero)
                    for i in xrange(len(self.bacteria_plots_ent_2["prevotella"].points[1:])):
                        # gets time from prevotella plot and y values for each plot
                        csv_writer.writerow([self.bacteria_plots_ent_2["prevotella"].points[i + 1][0],  # x value, time
                                             self.bacteria_plots_ent_2["prevotella"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_2["bacteroides"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_2["faecalibacterium"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_2["lachnospiraceae"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_2["roseburia"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_2["collinsella"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_2["bifidobacterium"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_2["alistipes"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_2["streptococcus"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_2["coprococcus"].points[i + 1][1],  # y value
                                             ])

                # save options used
                with open(os.path.join(directory, "scenario_2_gut_enterotype_2_options_used_" + current_datetime +
                                                  ".txt"), "wb") as options_used_file:

                    antibiotic_concentration_options = ""
                    go_for_antibiotics = True  # allows for antibiotic_concentration_options to be filled just once
                    for bacteria in sorted(self.bacteria_plots_ent_2):
                        for antibiotic in sorted(self.antibiotic_plots_ent_2):
                            options_used_file.writelines([
                                global_variables.LANGUAGE[bacteria] + ", " +
                                global_variables.LANGUAGE[antibiotic] + " inhibition: " +
                                str(getattr(self, bacteria + "_antibiotic_inhibition_ent_2")[antibiotic]) + "\n"
                            ])

                            if go_for_antibiotics:
                                antibiotic_concentration_options += \
                                    global_variables.LANGUAGE[antibiotic] + " concentration: " + \
                                    str(self.antibiotic_concentrations_ent_2[antibiotic]) + "\n"

                        go_for_antibiotics = False

                    options_used_file.writelines([antibiotic_concentration_options])

                # popup warning message
                popup_warning_id.show_message(*popup_warning_title_and_message)

            elif self.current_microbiome == "gut_enterotype_3":
                # saves screenshot of graph
                graphs_box_id.export_to_png(os.path.join(directory, "scenario_2_gut_enterotype_3_screenshot_" +
                                                         current_datetime + ".png"))

                # save csv file with x-axis and y-axis values for each plot
                with open(os.path.join(directory, "scenario_2_gut_enterotype_3_plot_points_" + current_datetime +
                                                  ".csv"), "wb") as csv_file:
                    csv_writer = csv.writer(csv_file)

                    # csv header
                    csv_writer.writerow(["Time", "Bacteroides Density", "Bifidobacterium Density",
                                         "Faecalibacterium Density", "Lachnospiraceae Density",
                                         "Alistipes Density", "Akkermansia Density", "Ruminococcus Density",
                                         "Collinsella Density", "Blautia Density", "Roseburia Density"])

                    # csv rows
                    # ignores first value as it exists only to allow plot instantiation (first y value must not be zero)
                    for i in xrange(len(self.bacteria_plots_ent_3["bacteroides"].points[1:])):
                        # gets time from bacteroides plot and y values for each plot
                        csv_writer.writerow([self.bacteria_plots_ent_3["bacteroides"].points[i + 1][0],  # x value, time
                                             self.bacteria_plots_ent_3["bacteroides"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_3["bifidobacterium"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_3["faecalibacterium"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_3["lachnospiraceae"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_3["alistipes"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_3["akkermansia"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_3["ruminococcus"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_3["collinsella"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_3["blautia"].points[i + 1][1],  # y value
                                             self.bacteria_plots_ent_3["roseburia"].points[i + 1][1],  # y value
                                             ])

                # save options used
                with open(os.path.join(directory, "scenario_2_gut_enterotype_3_options_used_" + current_datetime +
                                                  ".txt"), "wb") as options_used_file:

                    antibiotic_concentration_options = ""
                    go_for_antibiotics = True  # allows for antibiotic_concentration_options to be filled just once
                    for bacteria in sorted(self.bacteria_plots_ent_3):
                        for antibiotic in sorted(self.antibiotic_plots_ent_3):
                            options_used_file.writelines([
                                global_variables.LANGUAGE[bacteria] + ", " +
                                global_variables.LANGUAGE[antibiotic] + " inhibition: " +
                                str(getattr(self, bacteria + "_antibiotic_inhibition_ent_3")[antibiotic]) + "\n"
                            ])

                            if go_for_antibiotics:
                                antibiotic_concentration_options += \
                                    global_variables.LANGUAGE[antibiotic] + " concentration: " + \
                                    str(self.antibiotic_concentrations_ent_3[antibiotic]) + "\n"

                        go_for_antibiotics = False

                    options_used_file.writelines([antibiotic_concentration_options])

                # popup warning message
                popup_warning_id.show_message(*popup_warning_title_and_message)

    def data_generator(self):
        """
        Generates time (x-axis) and data (y-axis) points for each variable/graph
        """
        if self.current_scenario == "scenario_1":
            # initial values
            current_time_point = 0.0
            sensitive_density = self.sensitive_initial_density
            resistant_density = self.resistant_initial_density
            precursor_density = self.initial_precursor_cell_density
            effector_density = 0.0
            memory_cells_density = 0.0

            while True:
                # initial values are yielded at first
                yield (current_time_point, sensitive_density, resistant_density, precursor_density, effector_density,
                       memory_cells_density)

                antibiotic_uptake_args = {}
                if self.treatment_type == "Classic":
                    # time is added in calculate_next_time_step()
                    antibiotic_uptake_args = {"delay": self.classic_delay, "duration": self.classic_duration}
                elif self.treatment_type == "Adaptive":
                    # total_bacteria_density is added in calculate_next_time_step()
                    antibiotic_uptake_args = {
                        "bacteria_density_causing_symptoms": self.adaptive_symptoms_at_bacteria_density}
                elif self.treatment_type == "User":
                    antibiotic_uptake_args = {"taking_antibiotic": self.user_administer}

                (current_time_point, sensitive_density, resistant_density, precursor_density, effector_density,
                 memory_cells_density) = calculate_next_time_step(current_time_point, sensitive_density,
                                                                  resistant_density, precursor_density,
                                                                  effector_density, memory_cells_density,
                                                                  self.immune_cell_proliferation_rate,
                                                                  self.lymphocyte_inhibition,
                                                                  self.memory_cell_conversion_rate,
                                                                  self.effector_decay_rate,
                                                                  self.antibiotic_mean_concentration,
                                                                  self.immune_cell_half_maximum_growth,
                                                                  self.treatment_type, antibiotic_uptake_args,
                                                                  (self.sensitive_growth_rate,
                                                                   self.sensitive_antibiotic_inhibition),
                                                                  (self.resistant_growth_rate,
                                                                   self.resistant_antibiotic_inhibition),
                                                                  self.simulation_speed)

        elif self.current_scenario == "scenario_2":
            if self.current_microbiome == "gut_enterotype_1":
                current_time_point = 0.0

                bacteria_densities = dict(self.bacteria_densities_ent_1)
                bacteria_densities_relative_frequency = {}

                nutrient_concentrations = {}
                for bacteria in bacteria_densities:
                    # bacterias, at initial density, are stable at this value, Qω/ψ-ω
                    nutrient_concentrations[bacteria] = (5 * 0.01) / (3.3 - 0.01)

                bacteria_antibiotic_inhibition = {"bacteroides": self.bacteroides_antibiotic_inhibition_ent_1,
                                                  "faecalibacterium": self.faecalibacterium_antibiotic_inhibition_ent_1,
                                                  "roseburia": self.roseburia_antibiotic_inhibition_ent_1,
                                                  "bifidobacterium": self.bifidobacterium_antibiotic_inhibition_ent_1,
                                                  "lachnospiraceae": self.lachnospiraceae_antibiotic_inhibition_ent_1,
                                                  "parabacteroides": self.parabacteroides_antibiotic_inhibition_ent_1,
                                                  "alistipes": self.alistipes_antibiotic_inhibition_ent_1,
                                                  "anaerostipes": self.anaerostipes_antibiotic_inhibition_ent_1,
                                                  "acidaminococcus": self.acidaminococcus_antibiotic_inhibition_ent_1,
                                                  "collinsella": self.collinsella_antibiotic_inhibition_ent_1}

                while True:
                    # relative frequency total density
                    total_density = 1.0  # (instead of 0.0) allows a single survivor bacteria genus to die
                    for bacteria, density in bacteria_densities.iteritems():
                        # if bacteria is dead set its value to 0.0000000001
                        if self.bacteria_dead_status_ent_1[bacteria]:
                            bacteria_densities[bacteria] = 0.0000000001
                        else:  # count towards total_density
                            total_density += density

                    # individual bacteria relative frequency
                    for bacteria, density in bacteria_densities.iteritems():
                        if self.bacteria_dead_status_ent_1[bacteria]:
                            bacteria_densities_relative_frequency[bacteria] = 0.0000000001
                        else:
                            bacteria_densities_relative_frequency[bacteria] = density/total_density

                    # initial values are yielded at first
                    yield [current_time_point, bacteria_densities_relative_frequency["bacteroides"],
                           bacteria_densities_relative_frequency["faecalibacterium"],
                           bacteria_densities_relative_frequency["roseburia"],
                           bacteria_densities_relative_frequency["bifidobacterium"],
                           bacteria_densities_relative_frequency["lachnospiraceae"],
                           bacteria_densities_relative_frequency["parabacteroides"],
                           bacteria_densities_relative_frequency["alistipes"],
                           bacteria_densities_relative_frequency["anaerostipes"],
                           bacteria_densities_relative_frequency["acidaminococcus"],
                           bacteria_densities_relative_frequency["collinsella"]]

                    current_time_point, bacteria_densities, nutrient_concentrations = \
                        calculate_next_time_step_scenario2(
                            current_time_point, bacteria_densities, self.bacteria_growth_rate,
                            bacteria_antibiotic_inhibition, self.antibiotic_concentrations_ent_1,
                            self.antibiotic_uptake_ent_1, nutrient_concentrations, 0.01,
                            self.bacteria_nutrient_consumption_ent_1, 5, self.simulation_speed)

            elif self.current_microbiome == "gut_enterotype_2":
                current_time_point = 0.0

                bacteria_densities = dict(self.bacteria_densities_ent_2)
                bacteria_densities_relative_frequency = {}

                nutrient_concentrations = {}
                for bacteria in bacteria_densities:
                    # bacterias, at initial density, are stable at this value, Qω/ψ-ω
                    nutrient_concentrations[bacteria] = (5 * 0.01) / (3.3 - 0.01)

                bacteria_antibiotic_inhibition = {"prevotella": self.prevotella_antibiotic_inhibition_ent_2,
                                                  "bacteroides": self.bacteroides_antibiotic_inhibition_ent_2,
                                                  "faecalibacterium": self.faecalibacterium_antibiotic_inhibition_ent_2,
                                                  "lachnospiraceae": self.lachnospiraceae_antibiotic_inhibition_ent_2,
                                                  "roseburia": self.roseburia_antibiotic_inhibition_ent_2,
                                                  "collinsella": self.collinsella_antibiotic_inhibition_ent_2,
                                                  "bifidobacterium": self.bifidobacterium_antibiotic_inhibition_ent_2,
                                                  "alistipes": self.alistipes_antibiotic_inhibition_ent_2,
                                                  "streptococcus": self.streptococcus_antibiotic_inhibition_ent_2,
                                                  "coprococcus": self.coprococcus_antibiotic_inhibition_ent_2}

                while True:
                    # relative frequency total density
                    total_density = 1.0  # (instead of 0.0) allows a single survivor bacteria genus to die
                    for bacteria, density in bacteria_densities.iteritems():
                        # if bacteria is dead set its value to 0.0000000001
                        if self.bacteria_dead_status_ent_2[bacteria]:
                            bacteria_densities[bacteria] = 0.0000000001
                        else:  # count towards total_density
                            total_density += density

                    # individual bacteria relative frequency
                    for bacteria, density in bacteria_densities.iteritems():
                        if self.bacteria_dead_status_ent_2[bacteria]:
                            bacteria_densities_relative_frequency[bacteria] = 0.0000000001
                        else:
                            bacteria_densities_relative_frequency[bacteria] = density / total_density

                    # initial values are yielded at first
                    yield [current_time_point, bacteria_densities_relative_frequency["prevotella"],
                           bacteria_densities_relative_frequency["bacteroides"],
                           bacteria_densities_relative_frequency["faecalibacterium"],
                           bacteria_densities_relative_frequency["lachnospiraceae"],
                           bacteria_densities_relative_frequency["roseburia"],
                           bacteria_densities_relative_frequency["collinsella"],
                           bacteria_densities_relative_frequency["bifidobacterium"],
                           bacteria_densities_relative_frequency["alistipes"],
                           bacteria_densities_relative_frequency["streptococcus"],
                           bacteria_densities_relative_frequency["coprococcus"]]

                    current_time_point, bacteria_densities, nutrient_concentrations = \
                        calculate_next_time_step_scenario2(
                            current_time_point, bacteria_densities, self.bacteria_growth_rate,
                            bacteria_antibiotic_inhibition, self.antibiotic_concentrations_ent_2,
                            self.antibiotic_uptake_ent_2, nutrient_concentrations, 0.01,
                            self.bacteria_nutrient_consumption_ent_2, 5, self.simulation_speed)

            elif self.current_microbiome == "gut_enterotype_3":
                current_time_point = 0.0

                bacteria_densities = dict(self.bacteria_densities_ent_3)
                bacteria_densities_relative_frequency = {}

                nutrient_concentrations = {}
                for bacteria in bacteria_densities:
                    # bacterias, at initial density, are stable at this value, Qω/ψ-ω
                    nutrient_concentrations[bacteria] = (5 * 0.01) / (3.3 - 0.01)

                bacteria_antibiotic_inhibition = {"bacteroides": self.bacteroides_antibiotic_inhibition_ent_3,
                                                  "bifidobacterium": self.bifidobacterium_antibiotic_inhibition_ent_3,
                                                  "faecalibacterium": self.faecalibacterium_antibiotic_inhibition_ent_3,
                                                  "lachnospiraceae": self.lachnospiraceae_antibiotic_inhibition_ent_3,
                                                  "alistipes": self.alistipes_antibiotic_inhibition_ent_3,
                                                  "akkermansia": self.akkermansia_antibiotic_inhibition_ent_3,
                                                  "ruminococcus": self.ruminococcus_antibiotic_inhibition_ent_3,
                                                  "collinsella": self.collinsella_antibiotic_inhibition_ent_3,
                                                  "blautia": self.blautia_antibiotic_inhibition_ent_3,
                                                  "roseburia": self.roseburia_antibiotic_inhibition_ent_3}

                while True:
                    # relative frequency total density
                    total_density = 1.0  # (instead of 0.0) allows a single survivor bacteria genus to die
                    for bacteria, density in bacteria_densities.iteritems():
                        # if bacteria is dead set its value to 0.0000000001
                        if self.bacteria_dead_status_ent_3[bacteria]:
                            bacteria_densities[bacteria] = 0.0000000001
                        else:  # count towards total_density
                            total_density += density

                    # individual bacteria relative frequency
                    for bacteria, density in bacteria_densities.iteritems():
                        if self.bacteria_dead_status_ent_3[bacteria]:
                            bacteria_densities_relative_frequency[bacteria] = 0.0000000001
                        else:
                            bacteria_densities_relative_frequency[bacteria] = density / total_density

                    # initial values are yielded at first
                    yield [current_time_point, bacteria_densities_relative_frequency["bacteroides"],
                           bacteria_densities_relative_frequency["bifidobacterium"],
                           bacteria_densities_relative_frequency["faecalibacterium"],
                           bacteria_densities_relative_frequency["lachnospiraceae"],
                           bacteria_densities_relative_frequency["alistipes"],
                           bacteria_densities_relative_frequency["akkermansia"],
                           bacteria_densities_relative_frequency["ruminococcus"],
                           bacteria_densities_relative_frequency["collinsella"],
                           bacteria_densities_relative_frequency["blautia"],
                           bacteria_densities_relative_frequency["roseburia"]]

                    current_time_point, bacteria_densities, nutrient_concentrations = \
                        calculate_next_time_step_scenario2(
                            current_time_point, bacteria_densities, self.bacteria_growth_rate,
                            bacteria_antibiotic_inhibition, self.antibiotic_concentrations_ent_3,
                            self.antibiotic_uptake_ent_3, nutrient_concentrations, 0.01,
                            self.bacteria_nutrient_consumption_ent_3, 5, self.simulation_speed)

    def add_points(self, data_yielder, sensitive_bacteria_plot, resistant_bacteria_plot, antibiotic_plot, immune_plot,
                   total_bacteria_plot):
        """
        Add points to scenario 1 plots

        PARAMETERS:
            data_yielder : generator
                Generator data_generator()
            sensitive_bacteria_plot : Plot
                Plot object
            resistant_bacteria_plot : Plot
                Plot object
            antibiotic_plot : Plot
                Plot object
            immune_plot : Plot
                Plot object
            total_bacteria_plot : Plot
                Plot object
            
        RETURNS: lambda function
        """
        def add_points_function(_self, _data_yielder, _sensitive_bacteria_plot, _resistant_bacteria_plot,
                                _antibiotic_plot, _immune_plot, _total_bacteria_plot):
            data = _data_yielder.next()

            time = data[0]

            # avoids zero division errors
            sensitive_bacteria_density = data[1] if data[1] > 0 else 0.0001
            resistant_bacteria_density = data[2] if data[2] > 0 else 0.0001
            immune_cells_density = data[3] + data[4] + data[5] if data[3] + data[4] + data[5] > 0 else 0.0001
            antibiotic_concentration = _self.antibiotic_mean_concentration

            # if both bacteria are dead or host death threshold is reached, stop generating values
            if (not (sensitive_bacteria_density < 1 and resistant_bacteria_density < 1)) and (
                            sensitive_bacteria_density + resistant_bacteria_density < _self.host_death_density):
                _sensitive_bacteria_plot.points.append((time, sensitive_bacteria_density))
                _resistant_bacteria_plot.points.append((time, resistant_bacteria_density))
                _immune_plot.points.append((time, immune_cells_density))
                _total_bacteria_plot.points.append((time, sensitive_bacteria_density + resistant_bacteria_density))

                # treatment type logic
                if _self.treatment_type == "Classic":
                    if _self.classic_delay < time < _self.classic_delay + _self.classic_duration:
                        _antibiotic_plot.points.append((time, antibiotic_concentration))
                    else:
                        _antibiotic_plot.points.append((time, 0))
                elif _self.treatment_type == "Adaptive":
                    if _self.adaptive_symptoms_at_bacteria_density <\
                                    sensitive_bacteria_density + resistant_bacteria_density:
                        _antibiotic_plot.points.append((time, antibiotic_concentration))
                    else:
                        _antibiotic_plot.points.append((time, 0))
                elif _self.treatment_type == "User":
                    if _self.user_administer:
                        _antibiotic_plot.points.append((time, antibiotic_concentration))
                    else:
                        _antibiotic_plot.points.append((time, 0))
            else:
                # cancel clock
                _self.clock_add_points.cancel()

                # checks whether host death or bacteria death
                if sensitive_bacteria_density + resistant_bacteria_density >= _self.host_death_density:
                    title = "popup_host_death_title"
                    message = "popup_host_death_message"
                else:
                    title = "popup_bacteria_death_title"
                    message = "popup_bacteria_death_message"

                # show popup message
                _self.root.ids.popup_warning.show_message(global_variables.LANGUAGE[title],
                                                          global_variables.LANGUAGE[message])

        return lambda _: add_points_function(self, data_yielder, sensitive_bacteria_plot, resistant_bacteria_plot,
                                             antibiotic_plot, immune_plot, total_bacteria_plot)

    def add_points_scenario2(self, data_yielder, bacteria_plot_dict, antibiotic_plot_dict):
        """
        Add points to scenario 2 plots 

        PARAMETERS:
            data_yielder : generator
                Generator data_generator()
            bacteria_plot_dict : dict[Plot]
                Dictionary associating bacteria with its Plot object, {"bacteria1: Plot, ...}
            antibiotic_plot_dict : dict[Plot]
                Dictionary associating antibiotic with its Plot object, {"antibiotic1: Plot, ...}

        RETURNS: lambda function
        """
        def add_points_scenario2_function(_self, _data_yielder, _bacteria_plot_dict, _antibiotic_plot_dict):
            data = _data_yielder.next()

            time = data[0]

            # assumes 0.0001 of relative frequency as bacteria death
            data[1] = data[1] if data[1] > 0.0001 else 0.0000000001
            data[2] = data[2] if data[2] > 0.0001 else 0.0000000001
            data[3] = data[3] if data[3] > 0.0001 else 0.0000000001
            data[4] = data[4] if data[4] > 0.0001 else 0.0000000001
            data[5] = data[5] if data[5] > 0.0001 else 0.0000000001
            data[6] = data[6] if data[6] > 0.0001 else 0.0000000001
            data[7] = data[7] if data[7] > 0.0001 else 0.0000000001
            data[8] = data[8] if data[8] > 0.0001 else 0.0000000001
            data[9] = data[9] if data[9] > 0.0001 else 0.0000000001
            data[10] = data[10] if data[10] > 0.0001 else 0.0000000001

            # check if bacteria are all dead
            all_bacteria_dead = False
            if sum(data[1:]) <= 0.000000001:
                all_bacteria_dead = True

            # this always happens if current_scenario == "scenario_2"
            if _self.current_microbiome == "gut_enterotype_1":
                bacteria_densities = {"bacteroides": data[1], "faecalibacterium": data[2],
                                      "roseburia": data[3], "bifidobacterium": data[4],
                                      "lachnospiraceae": data[5], "parabacteroides": data[6],
                                      "alistipes": data[7], "anaerostipes": data[8],
                                      "acidaminococcus": data[9], "collinsella": data[10]}
                for bacteria, density in bacteria_densities.iteritems():
                    # marks bacteria death
                    if density <= 0.0001:
                        _self.bacteria_dead_status_ent_1[bacteria] = True

                    # append bacteria plot points
                    _bacteria_plot_dict[bacteria].points.append((time, density))

                # append antibiotic plot points
                for antibiotic, uptake_value in _self.antibiotic_uptake_ent_1.iteritems():
                    if bool(uptake_value):
                        _antibiotic_plot_dict[antibiotic].points.append(
                            (time, _self.antibiotic_concentrations_ent_1[antibiotic]))
                    else:
                        _antibiotic_plot_dict[antibiotic].points.append((time, 0))

                # if all bacteria are dead, stop generating values
                if all_bacteria_dead:
                    # cancel clock
                    _self.clock_add_points_gut_1.cancel()

                    # show popup message
                    _self.root.ids.popup_warning.show_message(global_variables.LANGUAGE["popup_bacteria_death_title"],
                                                              global_variables.LANGUAGE["popup_bacteria_death_message"])

            elif _self.current_microbiome == "gut_enterotype_2":
                bacteria_densities = {"prevotella": data[1], "bacteroides": data[2],
                                      "faecalibacterium": data[3], "lachnospiraceae": data[4],
                                      "roseburia": data[5], "collinsella": data[6],
                                      "bifidobacterium": data[7], "alistipes": data[8],
                                      "streptococcus": data[9], "coprococcus": data[10]}
                for bacteria, density in bacteria_densities.iteritems():
                    # marks bacteria death
                    if density <= 0.0001:
                        _self.bacteria_dead_status_ent_2[bacteria] = True

                    # append bacteria plot points
                    _bacteria_plot_dict[bacteria].points.append((time, density))

                # append antibiotic plot points
                for antibiotic, uptake_value in _self.antibiotic_uptake_ent_2.iteritems():
                    if bool(uptake_value):
                        _antibiotic_plot_dict[antibiotic].points.append(
                            (time, _self.antibiotic_concentrations_ent_2[antibiotic]))
                    else:
                        _antibiotic_plot_dict[antibiotic].points.append((time, 0))

                # if all bacteria are dead, stop generating values
                if all_bacteria_dead:
                    # cancel clock
                    _self.clock_add_points_gut_2.cancel()

                    # show popup message
                    _self.root.ids.popup_warning.show_message(global_variables.LANGUAGE["popup_bacteria_death_title"],
                                                              global_variables.LANGUAGE["popup_bacteria_death_message"])

            else:  # _self.current_microbiome == "gut_enterotype_3":
                bacteria_densities = {"bacteroides": data[1], "bifidobacterium": data[2],
                                      "faecalibacterium": data[3], "lachnospiraceae": data[4],
                                      "alistipes": data[5], "akkermansia": data[6],
                                      "ruminococcus": data[7], "collinsella": data[8],
                                      "blautia": data[9], "roseburia": data[10]}

                for bacteria, density in bacteria_densities.iteritems():
                    # marks bacteria death
                    if density <= 0.0001:
                        _self.bacteria_dead_status_ent_3[bacteria] = True

                    # append bacteria plot points
                    _bacteria_plot_dict[bacteria].points.append((time, density))

                # append antibiotic plot points
                for antibiotic, uptake_value in _self.antibiotic_uptake_ent_3.iteritems():
                    if bool(uptake_value):
                        _antibiotic_plot_dict[antibiotic].points.append(
                            (time, _self.antibiotic_concentrations_ent_3[antibiotic]))
                    else:
                        _antibiotic_plot_dict[antibiotic].points.append((time, 0))

                # if all bacteria are dead, stop generating values
                if all_bacteria_dead:
                    # cancel clock
                    _self.clock_add_points_gut_3.cancel()

                    # show popup message
                    _self.root.ids.popup_warning.show_message(global_variables.LANGUAGE["popup_bacteria_death_title"],
                                                              global_variables.LANGUAGE["popup_bacteria_death_message"])

        return lambda _: add_points_scenario2_function(self, data_yielder, bacteria_plot_dict, antibiotic_plot_dict)

    def enable_disable(self, what):
        """
        Enables or disables sliders, toggles and buttons

        PARAMETERS:
            what : str
                "enable" or "disable"

        RETURNS: bool
            True if enabled, False if disabled
        """
        if self.current_scenario == "scenario_1":
            if what == "disable":
                for i in self.root.slider_ids + self.root.toggle_id.toggle_ids:
                    i.disabled = True
                if self.treatment_type != "User":
                    self.root.toggle_id.options.disabled = True
                return False
            elif what == "enable":
                for i in self.root.slider_ids + self.root.toggle_id.toggle_ids:
                    i.disabled = False
                self.root.toggle_id.options.disabled = False
                return True
        elif self.current_scenario == "scenario_2":
            if self.current_microbiome == "gut_enterotype_1":
                if what == "disable":
                    for i in self.root.bacteria_buttons_ids_ent_1:
                        i.ids.slider_box.disabled = True
                    return False
                elif what == "enable":
                    for i in self.root.bacteria_buttons_ids_ent_1:
                        i.ids.slider_box.disabled = False
                    return True
            elif self.current_microbiome == "gut_enterotype_2":
                if what == "disable":
                    for i in self.root.bacteria_buttons_ids_ent_2:
                        i.ids.slider_box.disabled = True
                    return False
                elif what == "enable":
                    for i in self.root.bacteria_buttons_ids_ent_2:
                        i.ids.slider_box.disabled = False
                    return True
            elif self.current_microbiome == "gut_enterotype_3":
                if what == "disable":
                    for i in self.root.bacteria_buttons_ids_ent_3:
                        i.ids.slider_box.disabled = True
                    return False
                elif what == "enable":
                    for i in self.root.bacteria_buttons_ids_ent_3:
                        i.ids.slider_box.disabled = False
                    return True

    @staticmethod
    def new_language(language):
        """
        Repopulates language dictionary with the strings from the selected language
        
        PARAMETERS:
            language : str
                Selected language ("en", "pt", etc)
        
        RETURNS: dict[str]
            New language dict
        """
        # reads options.txt
        with open(os.path.join("bin", "options.txt"), "r") as options:
            options_file = options.readlines()

        # overwrites default language option in options.txt file
        with open(os.path.join("bin", "options.txt"), "w") as options:
            count = 0
            correct_line = None
            for line in options_file:
                option = line.split(": ")
                if option[0] == "language":
                    correct_line = count
                count += 1

            options_file[correct_line] = "language: " + language
            options.writelines(options_file)

        # copies default (english) language dict and updates it with the selected language
        new_language_dict = dict(global_variables.DEFAULT_LANGUAGE)
        new_language_dict.update(XMLTextParser("string", language).parse(os.path.join("bin", "ui", "text.xml")))
        new_language_dict["selected_language"] = language

        # updates global_variables language
        global_variables.LANGUAGE = new_language_dict

        return new_language_dict

    def check_treatment(self, graph_layout_instance, button=None):
        """
        Gets the current treatment type button pressed
        
        PARAMETERS:
            graph_layout_instance : GraphsLayout object
                GraphsLayout object
            button : None or str
                Specifies which treatment type button to check
        
        RETURNS: str
            State of button
        """
        if button is None:
            return self.treatment_type if (graph_layout_instance.simulation_going_scenario_1_property or
                                           graph_layout_instance.pause_scenario_1_property) else ""

        elif button == "Classic" and (graph_layout_instance.simulation_going_scenario_1_property
                                      or graph_layout_instance.pause_scenario_1_property):
            return "normal" if self.treatment_type != button else "down"
        elif button == "Adaptive" and (graph_layout_instance.simulation_going_scenario_1_property
                                       or graph_layout_instance.pause_scenario_1_property):
            return "normal" if self.treatment_type != button else "down"
        elif button == "User" and (graph_layout_instance.simulation_going_scenario_1_property
                                   or graph_layout_instance.pause_scenario_1_property):
            return "normal" if self.treatment_type != button else "down"
        else:
            return "normal"

    def assign_treatment(self, value):
        """
        Sets treatment type option
        """
        self.treatment_type = value

    def on_host_death_density_value(self, *args):
        """
        Sets bacteria density causing host death value option
        """
        self.host_death_density = self.host_death_density_value * self.host_death_density_exponent

    def on_host_death_density_exponent(self, *args):
        """
        Sets bacteria density causing host death exponent option
        """
        self.host_death_density = self.host_death_density_value * self.host_death_density_exponent

    def on_adaptive_symptoms_at_bacteria_density_value(self, *args):
        """
        Sets adaptive symptoms at bacteria density value option
        """
        self.adaptive_symptoms_at_bacteria_density = (self.adaptive_symptoms_at_bacteria_density_value *
                                                      self.adaptive_symptoms_at_bacteria_density_exponent)

    def on_adaptive_symptoms_at_bacteria_density_exponent(self, *args):
        """
        Sets adaptive symptoms at bacteria density exponent option
        """
        self.adaptive_symptoms_at_bacteria_density = (self.adaptive_symptoms_at_bacteria_density_value *
                                                      self.adaptive_symptoms_at_bacteria_density_exponent)

    def on_pause(self, *args):
        """
        Needed to override so that the default behaviour was inhibited
        """
        pass

    def build(self):
        self.icon = os.path.join("bin", "ui", "icon.ico")
        self.title = "Simulator of Antibiotic Therapy Effects on the Dynamics of Bacterial Populations"
        return Builder.load_file(os.path.join('bin', 'ui', 'main_layout.kv'))


def start():
    """
    Initializes UI
    """
    SimulATeApp().run()
