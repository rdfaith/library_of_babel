import os
import sys
import math
import random
import csv
import pathlib
from enum import Enum
import pygame as pg

# Import core utilities
from .constants import *
from .utils import get_path

# Import major classes and objects
from .sound_manager import SoundManager
from .light_source import LightSource, LightMap
from .animator_object import Animator, Animation
from .hitbox import Hitbox

# Import game components
from .player import Player
from .object_classes import *
from .deco_objects import *
from .game_world import GameWorld
from .world_generation import *

# Import UI and Menus
from .menu import In_Game_Menu, GameState, menu_main
from .title_screen import TitleScreen

# Import shaders
from .shaders.shader import Shader, FakeShader

# Define what should be imported when using `from package import *`
# __all__ = [
#     "math", "random", "csv", "pathlib", "pg",
#     "constants", "get_path", "sound_manager",
#     "LightSource", "Player", "GameWorld", "GameState",
#     "Shader", "FakeShader", "TitleScreen", "GameObject"
# ]
