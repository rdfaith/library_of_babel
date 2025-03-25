# Example file showing a basic pygame "game loop"
import pygame as pg
import object_classes
from game_world import GameWorld
import world_generation
from source.menu import GameState
from utils import *
from constants import *
from sound_manager import *
import os
#from menus import *
from enum import Enum
import menu

# Pygame event for player death


# pygame setup
pg.init()

menu.main(True)

