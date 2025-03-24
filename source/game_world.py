import pygame as pg
from player import Player
from constants import *
from utils import *
from light_source import *

class GameWorld:
    def __init__(self, objects: list, collision_objects: list, interactable_objects: list, player_pos: pg.Vector2,
                 level_size: tuple[int, int]) -> None:
        self.objects = objects
        self.static_objects = collision_objects
        self.interactable_objects = interactable_objects
        self.player = Player(player_pos)

        self.light_map: LightMap = LightMap()  # object that stores all light sources

        self.camera_pos: pg.Vector2 = pg.Vector2(self.player.get_rect().x - SCREEN_WIDTH // 2,
                                                 self.player.get_rect().y - SCREEN_HEIGHT // 2)
        self.level_width, self.level_height = level_size
        self.play_start_position = player_pos

    def set_player_position(self, pos: pg.Vector2) -> None:
        """Sets player position, used when initialising level"""
        self.player.get_rect().x = pos.x
        self.player.get_rect().y = pos.y

    def get_light_map(self) -> LightMap:
        return self.light_map

    def do_updates(self, delta: float) -> None:

        # check if the player has fallen out of bounds
        if self.player.get_rect().y > self.level_height:
            self.player.on_fell_out_of_bounds()

        self.player.update(delta, self)

        for o in self.interactable_objects:
            o.update(delta, self)

    def do_render(self, game_screen, ui_screen):

        #region Functions
        def set_camera_position() -> None:
            """Sets self.camera_pos to the correct position for this frame"""

            def smooth_movement(current_pos: float, target_pos: float, delay: float) -> float:
                return current_pos + (target_pos - current_pos) * (delay / 100)

            # Zielposition der Kamera
            target_pos: pg.Vector2 = pg.Vector2(
                self.player.get_rect().x - SCREEN_WIDTH // 2,
                self.player.get_rect().y - SCREEN_HEIGHT // 2
            )

            self.camera_pos.x = smooth_movement(self.camera_pos.x, target_pos.x, CAMERA_DELAY_X)
            if abs(target_pos.y - self.camera_pos.y) > DEAD_ZONE_Y:
                self.camera_pos.y = smooth_movement(self.camera_pos.y, target_pos.y, CAMERA_DELAY_Y)
            self.camera_pos.x = max(0, min(self.camera_pos.x, self.level_width - SCREEN_WIDTH))
            self.camera_pos.y = max(0, min(self.camera_pos.y, self.level_height - SCREEN_HEIGHT))

        def draw_ui():
            ui_screen.fill((0, 0, 0, 0))

            ui_bg = pg.image.load(get_path("assets/sprites/ui/ui_bg.png")).convert_alpha()
            ui_heart = pg.image.load(get_path("assets/sprites/ui/ui_heart.png")).convert_alpha()
            ui_screen.blit(ui_bg, pg.Vector2(0, 0))

            for i in range(self.player.player_lives):
                ui_screen.blit(ui_heart, UI_HEART_POSITIONS[i])

            for i in range(len(self.player.letters_collected)):
                if i > 5:  # Break if more than 5 letters would have to be displayed
                    break
                letter = self.player.letters_collected[i]
                ui_screen.blit(LETTER_IMAGES[letter], UI_LETTER_POSITIONS[i])

        def draw_parallax_layer(layer, max_depth, y_parallax=True):
            depth: int = layer["depth"]
            parallax_factor: float = 1 - (depth / max_depth)  # Dynamische Berechnung des Parallax-Faktors

            # Berechnung der versetzten Hintergrundposition (x und y)
            offset_y: int = layer["offset_y"]

            x_pos = -self.camera_pos.x * parallax_factor
            y_pos = offset_y - self.camera_pos.y * parallax_factor / 2 if y_parallax else offset_y - self.camera_pos.y
            bg_pos: pg.Vector2 = pg.Vector2(x_pos, y_pos)

            # Hintergrund zeichnen
            game_screen.blit(layer["image"], bg_pos)

        def draw_bg_parallax():
            """Draws the background parallax layers"""
            max_depth: int = max(layer["depth"] for layer in BG_LAYERS)  # Maximale Tiefe bestimmen
            for layer in BG_LAYERS:
                if layer["depth"] > 0:
                    draw_parallax_layer(layer, max_depth, True)

        def draw_fg_parallax():
            """Draws the foreground parallax layers"""
            max_depth: int = max(layer["depth"] for layer in BG_LAYERS)  # Maximale Tiefe bestimmen
            for layer in BG_LAYERS:
                if layer["depth"] <= 0:
                    draw_parallax_layer(layer, max_depth, False)

        def draw_post_processing():
            """Adds visual effects and post-processing"""
            vignette = VIGNETTE.convert_alpha()
            player_position = self.player.get_rect().topleft - self.player.get_sprite_offset() - self.camera_pos
            vignette_position = player_position - pg.Vector2(vignette.get_width() / 2, vignette.get_height() / 2)
            game_screen.blit(VIGNETTE, vignette_position)

        #endregion

        # Kameraposition setzen
        set_camera_position()

        # draw background parallax
        draw_bg_parallax()

        # draw objects
        for o in self.static_objects + self.objects + self.interactable_objects:  # Static -> Deco -> Interactive
            o.draw(game_screen, self.camera_pos)

        # get light sources:
        self.light_map.clear_sources()
        for o in self.objects:
            light_source = o.get_light_source()
            if light_source:
                self.light_map.add_source(light_source)

        # draw player
        self.player.draw(game_screen, self.camera_pos)

        # draw foreground parallax
        draw_fg_parallax()

        # Visual effects
        # draw_post_processing()

        # draw UI
        draw_ui()
