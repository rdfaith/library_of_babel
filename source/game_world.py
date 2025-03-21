import object_classes
import pygame as pg
from constants import *
from utils import *


class GameWorld:
    def __init__(self, objects: list, collision_objects: list, interactable_objects: list, player_pos: pg.Vector2,
                 level_size: tuple[int, int]) -> None:
        self.objects = objects
        self.static_objects = collision_objects
        self.interactable_objects = interactable_objects
        self.player = object_classes.Player(player_pos)
        self.camera_pos: pg.Vector2 = pg.Vector2(self.player.rect.x - SCREEN_WIDTH // 2,
                                                 self.player.rect.y - SCREEN_HEIGHT // 2)
        self.level_width, self.level_height = level_size
        self.play_start_position = player_pos
    def set_player_position(self, pos: pg.Vector2) -> None:
        """Sets player position, used when initialising level"""
        self.player.rect.x = pos.x
        self.player.rect.y = pos.y

    def do_updates(self, delta: float) -> None:
        # check if the player has fallen
        fallen: bool = False
        if self.player.rect.y > self.level_height:
            fallen = True

        self.player.update(delta, self, fallen)

        for o in self.interactable_objects:
            o.update(delta, self)

    def do_render(self, screen):

        #region Functions
        def set_camera_position() -> None:

            def smooth_movement(current_pos: float, target_pos: float, delay: float) -> float:
                return current_pos + (target_pos - current_pos) * (delay / 100)

            """Sets self.camera_pos to the correct position for this frame"""

            # Zielposition der Kamera
            target_pos: pg.Vector2 = pg.Vector2(
                self.player.rect.x - SCREEN_WIDTH // 2,
                self.player.rect.y - SCREEN_HEIGHT // 2
            )

            self.camera_pos.x = smooth_movement(self.camera_pos.x, target_pos.x, CAMERA_DELAY_X)
            if abs(target_pos.y - self.camera_pos.y) > DEAD_ZONE_Y:
                self.camera_pos.y = smooth_movement(self.camera_pos.y, target_pos.y, CAMERA_DELAY_Y)
            self.camera_pos.x = max(0, min(self.camera_pos.x, self.level_width - SCREEN_WIDTH))
            self.camera_pos.y = max(0, min(self.camera_pos.y, self.level_height - SCREEN_HEIGHT))

        def draw_ui():
            ui_bg = pg.image.load(get_path("assets/sprites/ui/ui_bg.png"))
            ui_heart = pg.image.load(get_path("assets/sprites/ui/ui_heart.png"))
            screen.blit(ui_bg, pg.Vector2())

            for i in range(self.player.player_lives):
                screen.blit(ui_heart, UI_HEART_POSITIONS[i])

            for i in range(len(self.player.letters_collected)):
                letter = self.player.letters_collected[i]
                screen.blit(LETTER_IMAGES[letter], UI_LETTER_POSITIONS[i])

        def draw_parallax_layer(layer, max_depth, y_parallax=True):
            depth: int = layer["depth"]
            parallax_factor: float = 1 - (depth / max_depth)  # Dynamische Berechnung des Parallax-Faktors

            # Berechnung der versetzten Hintergrundposition (x und y)
            offset_y: int = layer["offset_y"]

            x_pos = -self.camera_pos.x * parallax_factor
            y_pos = offset_y - self.camera_pos.y * parallax_factor / 2 if y_parallax else offset_y - self.camera_pos.y
            bg_pos: pg.Vector2 = pg.Vector2(x_pos, y_pos)

            # Hintergrund zeichnen
            screen.blit(layer["image"], bg_pos)

        def draw_bg_parallax():
            max_depth: int = max(layer["depth"] for layer in BG_LAYERS)  # Maximale Tiefe bestimmen
            for layer in BG_LAYERS:
                if layer["depth"] > 0:
                    draw_parallax_layer(layer, max_depth, True)

        def draw_fg_parallax():
            max_depth: int = max(layer["depth"] for layer in BG_LAYERS)  # Maximale Tiefe bestimmen
            for layer in BG_LAYERS:
                if layer["depth"] <= 0:
                    draw_parallax_layer(layer, max_depth, False)

        #endregion

        # Kameraposition setzen
        set_camera_position()

        # draw background parallax
        draw_bg_parallax()

        # draw objects
        for o in self.objects + self.static_objects + self.interactable_objects:
            o.draw(screen, self.camera_pos)

        # draw player
        self.player.draw(screen, self.camera_pos)

        # draw foreground parallax
        draw_fg_parallax()

        # draw UI
        draw_ui()
