# Simulator of Antibiotic Therapy Effects on the Dynamics of Bacterial Populations
![icon](/bin/ui/icon.ico?raw=true "SimulATe Icon")

SimulATe (**Simul**ator of **A**ntibiotic **T**herapy **E**ffects on the dynamics of bacterial populations) is a program that simulates the effects of the administration of antibiotics on microbial populations. Its main goals are: a) to be used as a teaching tool for students, to facilitate learning about microbial population dynamics and, more precisely, the role of antibiotics as resistance selection agents and as microbiome disruption agents; and b) to be used as a testing tool for researchers in the field of antibiotic resistance.

Authors: **Pedro HC David**, **Teresa Nogueira**

![Screenshot](/screenshot.png?raw=true "SimulATe Screenshot")

# How to install

Note 1: Kivy requires OpenGL 2.0 or higher to run. This should not be a problem for most recent systems, as graphics cards drivers usually ship with some form of OpenGL 2.0 or higher. If for some reason you come across an error mentioning old OpenGL versions, you should try to update your graphics card drivers. If that isn't possible, this program won't be able to run on your system.

Note 2: `install_dependencies.py` requires an internet connection to install dependencies.

## Windows
The easiest way to install SimulATe on __Windows__ is by downloading the latest release available from the [releases page](https://github.com/Kronopt/SimulATe/releases) and unzipping. No extra dependencies required.

You can also download or clone this repository and install the following dependencies:
* [Python 2.7](https://www.python.org/downloads/release/python-2713/)
* Python Module dependencies (can be installed by running `install_dependencies.py`):
    * Kivy
    * kivy.deps.glew
    * kivy.deps.sdl2

## Linux
To install SimulATe on __Linux__, download or clone this repository and install the following dependencies:
* [Python 2.7](https://www.python.org/downloads/release/python-2713/)
* Kivy (follow the installation guide [here](https://kivy.org/docs/installation/installation-linux.html))

## MacOS
To install SimulATe on __MacOS__, download or clone this repository and install the following dependencies:
* [Python 2.7](https://www.python.org/downloads/release/python-2713/)
* Python Module dependencies (can be installed by running `install_dependencies.py`):
    * Cython
    * Kivy
* Kivy dependencies (can also be installed by running `install_dependencies.py`):
    * pkg-config
    * sdl2
    * sdl2_image
    * sdl2_ttf
    * sdl2_mixer
    * gstreamer

# How to use
If you downloaded the latest __Windows__ release, running SimulATe is as easy as launching the `SimulATe.exe` found inside the program folder.
If you downloaded or cloned this repository, run the `SimulATe.pyw` script with python 2.7, on all platforms.

When running the program you will first have to choose a simulation scenario:
* Single Population: Antibiotic effects on a single pathogenic bacterial population, composed of both antibiotic resistant and antibiotic sensitive bacteria. The host's immune system may or may not also come into play.
* Microbiome: Antibiotic effects on a human gut microbiome. Assumes equilibrium with the host's immune system, which means it will not directly come into play. This scenario aims at simulating the selective pressure exerced by antibiotics on the human gut microbial population.

In each scenario you will be presented with a lot of customizable parameters which allows the simulation to be tailored to your needs.

For a more detailed usage guide, please refer to the [wiki](https://github.com/Kronopt/SimulATe/wiki).

# Publication
Pedro H C David, Xana Sá-Pinto, Teresa Nogueira, Using SimulATe to model the effects of antibiotic selective pressure on the dynamics of pathogenic bacterial populations, Biology Methods and Protocols, Volume 4, Issue 1, 2019, bpz004, https://doi.org/10.1093/biomethods/bpz004

# Acknowledgments
* Francisco Dionísio
* Xana Sá-Pinto

# License
* SimulATe is distributed under the terms of the [GPL-3.0 License](https://github.com/Kronopt/SimulATe/blob/master/LICENSE)
* The icon was created by [dyogurt](https://github.com/dyogurt)
