from source import pg

class LightSource:
    def __init__(self, position: pg.Vector2, offset: pg.Vector2, color: pg.Color, radius: float, intensity: float, flicker=False):
        self.position: pg.Vector2 = position + offset  # position of the light in world space
        self.offset: pg.Vector2 = offset  # offset from top left corner of sprite to point in sprite from where light should be emitted
        self.color: pg.Color = color
        self.radius: float = radius
        self.intensity: float = intensity
        self.flicker: bool = flicker

    def set_position(self, pos: pg.Vector2):
        self.position = pos + (self.offset.x, self.offset.y)


class LightMap:
    def __init__(self):
        self.light_sources: list[LightSource] = []

    def add_source(self, light_source: LightSource):
        self.light_sources.append(light_source)

    def clear_sources(self):
        self.light_sources.clear()

    def get_sources(self) -> list[LightSource]:
        return self.light_sources.copy()

    def get_positions(self, max_index: int) -> list[pg.Vector2]:
        """Returns exactly max_index entries, filling up with empties if necessary"""
        sources = [ls.position for ls in self.get_sources()]
        return sources[:max_index] + [pg.Vector2(0, 0)] * (max_index - len(sources))

    def get_colors(self, max_index: int) -> list[pg.Color]:
        sources = [ls.color for ls in self.get_sources()]
        return sources[:max_index] + [pg.Color(0, 0, 0, 0)] * (max_index - len(sources))

    def get_intensities(self, max_index: int) -> list[float]:
        sources = [ls.intensity for ls in self.get_sources()]
        return sources[:max_index] + [0.0] * (max_index - len(sources))

    def get_radii(self, max_index: int) -> list[float]:
        sources = [ls.radius for ls in self.get_sources()]
        return sources[:max_index] + [0.0] * (max_index - len(sources))

    def get_flickers(self, max_index: int):
        sources = [ls.flicker for ls in self.get_sources()]
        return sources[:max_index] + [False] * (max_index - len(sources))

    def get_first_source(self):
        return self.light_sources[0]