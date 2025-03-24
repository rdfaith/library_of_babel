import pygame as pg
from object_classes import AnimatedObject
from animator_object import Animation
from utils import *
from light_source import LightSource

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
        light_source = LightSource(
            position,
            pg.Color((255, 0, 0)),
            5.0
        )
        super().__init__(position, animation, light_source)


class Hourglass(AnimatedObject):
    def __init__(self, position):
        animation = Animation(
            "idle",
            get_path('assets/sprites/anim/deco/hourglass1.png'),
            16,
            32,
            4,
            10
        )
        super().__init__(position, animation)
