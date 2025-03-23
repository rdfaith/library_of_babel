import pygame as pg


class Hitbox:
    @staticmethod  # Eine "statische Methode" gehört zur Klasse, aber nicht zu einer bestimmten Instanz der Klasse.
    # Das bedeutet, dass sie keine Instanzvariablen benötigt und direkt über die Klasse aufgerufen werden kann,
    # z. B. mit Hitbox.generate(...).
    #
    # Die Annotation @staticmethod sagt Python, dass diese Methode keine "self"-Referenz erwartet und
    # ohne eine Instanz der Klasse aufgerufen werden kann.
    def generate(position: pg.Vector2, hitbox_image: pg.Surface, crop: bool = True):
        return Hitbox(*Hitbox._get_rect_and_offset(position, hitbox_image, crop))

    @staticmethod
    def _get_rect_and_offset(position: pg.Vector2, hitbox_image: pg.Surface, crop: bool = True) -> (pg.Rect, pg.Vector2):
        """
        Generiert eine rechteckige Hitbox basierend auf dem nicht-transparenten Bereich von hitbox_image und gibt die
        Offset-Position zurück. Falls crop False ist, wird die Hitbox genau die Größe des Eingabebilds haben,
        bei True werden transparente Bereiche entfernt.
        """
        if not crop:
            return hitbox_image.get_rect(topleft=position), pg.Vector2()

        bbox = hitbox_image.get_bounding_rect()  # Get bounding rectangle of non-transparent area

        if bbox.width > 0 and bbox.height > 0:
            # Calculate the hitbox rect and its offset from the top-left corner of the image
            rect = pg.Rect(position.x + bbox.x, position.y + bbox.y, bbox.width, bbox.height)
            offset = pg.Vector2(bbox.x, bbox.y)  # The offset between the image and the hitbox
        else:
            # If fully transparent, return a default empty hitbox and zero offset
            rect = pg.Rect(position.x, position.y, 0, 0)
            offset = pg.Vector2(0, 0)

        return rect, offset

    def __init__(self, rect: pg.Rect, sprite_offset: pg.Vector2):
        self._hitboxes = {
            "default": {"rect": rect, "offset": sprite_offset}
        }

        self._current_hitbox = "default"

    def _add_hitbox_to_dict(self, name: str, rect: pg.Rect, sprite_offset: pg.Vector2):
        self._hitboxes[name] = {"rect": rect, "offset": sprite_offset}

    def add_hitbox(self, name: str, position: pg.Vector2, hitbox_image: pg.Surface):
        self._add_hitbox_to_dict(name, *Hitbox._get_rect_and_offset(position, hitbox_image))

    def set_current(self, name: str):

        if self._hitboxes[name]:
            self._current_hitbox = name
        else:
            print("ERROR: Invalid hitbox", name)
            self._current_hitbox = "default"

    def get_current(self) -> str:
        return self._current_hitbox

    def get_offset_diff(self, hb1: str, hb2: str = None):
        """Returns sprite offset difference of two hitboxes.
        If second argument is None, the current hitbox will be used"""
        if hb2:
            return self._hitboxes[hb1]["offset"] - self._hitboxes[hb2]["offset"]
        else:
            return self.get_offset() - self._hitboxes[hb1]["offset"]

    def get_rect(self) -> pg.Rect:
        return self._hitboxes[self._current_hitbox]["rect"]

    def get_offset(self) -> pg.Vector2:
        return self._hitboxes[self._current_hitbox]["offset"]
