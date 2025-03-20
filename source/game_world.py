import object_classes
import pygame as pg
from constants import *
from utils import *

def smooth_movement(current_pos: float, target_pos: float, delay: float) -> float:
    return current_pos + (target_pos - current_pos) * (delay/100)

class GameWorld:
    def __init__(self, objects: list, collision_objects: list, interactable_objects: list) -> None:
        self.objects = objects
        self.static_objects = collision_objects
        self.interactable_objects = interactable_objects
        self.player = object_classes.Player(pg.Vector2(100, 100), pg.image.load(get_path('assets/sprites/test_dino.png')), True)
        self.camera_pos: pg.Vector2 = pg.Vector2(self.player.rect.x - SCREEN_WIDTH // 2, self.player.rect.y - SCREEN_HEIGHT // 2)
        self.bg_image = pg.image.load(get_path("assets/sprites/bg_skybox.png"))

    def set_player_position(self, pos: pg.Vector2) -> None:
        """Sets player position, used when initialising level"""
        self.player.rect.x = pos.x
        self.player.rect.y = pos.y

    def do_updates(self, delta: float) -> None:
        self.player.update(delta, self)
        for i in self.interactable_objects:
            i.update(delta, self)

            # Zielposition der Kamera
            target_pos: pg.Vector2 = pg.Vector2(
                self.player.rect.x - SCREEN_WIDTH // 2,
                self.player.rect.y - SCREEN_HEIGHT // 2
            )
            self.camera_pos.x = smooth_movement(self.camera_pos.x, target_pos.x, CAMERA_DELAY_X)
            if abs(target_pos.y - self.camera_pos.y) > DEAD_ZONE_Y:
                self.camera_pos.y = smooth_movement(self.camera_pos.y, target_pos.y, CAMERA_DELAY_Y)
            self.camera_pos.x = max(0, min(self.camera_pos.x, LEVEL_WIDTH - SCREEN_WIDTH))
            self.camera_pos.y = max(0, min(self.camera_pos.y, LEVEL_HEIGHT - SCREEN_HEIGHT))
    def do_render(self, screen):
        screen.fill("purple")
        screen.blit(self.bg_image, pg.Vector2())
        for o in self.objects + self.static_objects + self.interactable_objects:
            o.draw(screen, self.camera_pos)
        self.player.draw(screen, self.camera_pos)
