import pygame as pg


class LightSource:
    def __init__(self, position: pg.Vector2, color: pg.Color, intensity):
        self.position: pg.Vector2 = position
        self.color: pg.Color = color
        self.intensity: float = intensity


class LightMap:
    def __init__(self):
        self.light_sources: list[LightSource] = []

    def add_source(self, light_source: LightSource):
        self.light_sources.append(light_source)

    def clear_sources(self):
        self.light_sources.clear()
