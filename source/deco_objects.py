import pygame as pg
from object_classes import AnimatedObject
from animator_object import Animation
from utils import *


class Candle(AnimatedObject):
    def __init__(self, position):
        animation = Animation(
            "idle",
            get_path('assets/sprites/anim/deco/candle1.png'),
            16,
            32,
            4,
            10
        )
        super().__init__(position, animation)
