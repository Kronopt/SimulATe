#!python2
# coding: utf-8

"""
INSTALL DEPENDENCIES
Installs module dependencies on Windows and Mac systems

HOW TO RUN:
    - Directly, by double clicking the script.
    - Through the command line
"""

import platform
import subprocess
import sys

__author__ = 'Pedro HC David, https://github.com/Kronopt'
__credits__ = ['Pedro HC David']


def install_dependencies(python_path, system):
    """
    Installs dependencies on both windows and mac
    Assumes pip (on both windows and mac) and Homebrew (on mac) are installed

    PARAMETERS:
        python_path : str
            Python installation path
        system : str
            "windows" or "mac"
    """
    dependencies_windows = ["Kivy", "Kivy-Garden", "kivy.deps.glew", "kivy.deps.sdl2"]
    dependencies_mac = ["Cython", "Kivy"]
    dependencies_brew_mac = ["pkg-config", "sdl2", "sdl2_image", "sdl2_ttf", "sdl2_mixer", "gstreamer"]

    print "Installing dependencies..."

    if system == "windows":
        dependencies = " ".join(dependencies_windows)
    elif system == "mac":
        dependencies = " ".join(dependencies_mac)

        dependencies_brew = " ".join(dependencies_brew_mac)

        # Homebrew install dependencies
        subprocess.call("brew install " + dependencies_brew, shell=True)

    # Install module dependencies with pip
    subprocess.call(python_path + " -m pip install " + dependencies, shell=True)

if __name__ == '__main__':
    python_exe = sys.executable  # location of python executable, avoids dependency on PATH

    try:  # check if pip is installed
        subprocess.check_call(python_exe + " -m pip --version", shell=True)

    except subprocess.CalledProcessError:  # info about pip and exit script
        print
        print "Pip is the recommended tool for installing Python packages, and usually comes bundled with python."
        print "Without pip, dependencies are much harder to install..."
        print "Please install pip before trying to use this script again."
        print "Take a look at the installation guide if needed: https://pip.pypa.io/en/stable/installing/"
        print
        raw_input("Press any key to exit")
        sys.exit()

    # check if running on windows or mac
    current_system = platform.system().lower()

    if "windows" in current_system:  # windows
        install_dependencies(python_exe, "windows")

    elif "darwin" in current_system:  # mac
        try:  # check if Homebrew is installed
            subprocess.check_call("brew --version", shell=True)

        except subprocess.CalledProcessError:  # info about Homebrew, ask to install it or exit script
            print
            print "Homebrew is a package manager for MacOS (https://brew.sh/)."
            print "This script makes use of HomeBrew to install some dependencies."
            print "Homebrew can be installed right now with the following command:"
            print '> /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"'
            print

            answer = ""
            while answer not in ["y", "n"]:
                answer = raw_input("Do you want to install Homebrew? (y/n): ")

            if answer == "n":
                print "You will have to install Homebrew yourself if you want to use this script on a mac"
                print
                raw_input("Press any key to exit")
                sys.exit()

            else:  # install Homebrew
                print "Installing Homebrew..."
                subprocess.call('/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"',
                                shell=True)

        install_dependencies(python_exe, "mac")
    else:
        # when running on linux or other OS that is not windows or mac
        print "This script is meant to be run on Windows or Mac."

    print
    raw_input("Press any key to exit")
