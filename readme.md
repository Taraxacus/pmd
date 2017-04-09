# pmd - Experimenting with PyGame by trying to clone Pokémon Mystery Dungeon

Currently, `main01.py` (formerly `tiles.py`) is able to display a custom map
using a custom tileset. A player can be placed on the map with a custom avatar.
However the "player" can't actually _play_.

The programm `main02.py` is a rewritten version of `main01.py` that is aimed
at more general tilesheets. It will do roughly the same as `main01.py`.
The legend files (LEG files) of the tile sheets will be used to locate
the different tiles on the tile sheet. The player now has an animated sprite.
They can walk through the level and cannot walk over walls. Also, they can
enter the stairs by pressing `K`. Some music in the background adds to the
flair.

; Internally, Level.render
; now returns a PyGame surface instead of blitting the map directly onto the
; screen. Also, the code has been commented for better readability. Further
; commenting is planned. The code around the player is still very provisional.

## Installation

This programm was tested on Linux (Arch Linux at 2017-04-06) and Windows 7
using Python 3.6.0. If you want to run these programms on your system, 
download them or clone them using git. You need

* Python 3.5 or higher and 
* The Python modules `pygame` and, optionally, `easygui`

On the Python version: Some of the syntax used here require at least Python
3.5.

### Installing the Python modules

Installing the required packages can be done using PIP. On Windows run
`python -m pip install -r requirements.txt` in the commandline while in the
installation folder (alternatively substitute `requirements.txt` with the full
path to this file). On Linux use `pip install -r requirements.txt` with
similar considerations for the working directory.

You may have to use the commands `python3` and `pip3` instead of `python` and
`pip`! To check which version of Python `python` refers to, run
`python --version` on both Windows and Linux.

Alternatively you can install the packages manually. Go to their websites
([PyGame](http://www.pygame.org/news), and
[easygui](http://easygui.sourceforge.net/))
and follow the instructions given there.

## Introduction

As of now, these programms are fairly useless. You can close the displayed
window by pressing `X`. Also, you can create new levels, by copying the syntax
used in the INI files in the `levels` folder. Downloading additional tile
sheets is also possible if you can figure out the syntax in the LEG files and
create your own.
