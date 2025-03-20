import object_classes
import pygame as pg
from constants import *
from utils import *

def smooth_movement(current_pos: pg.Vector2, target_pos: pg.Vector2, delay: float) -> pg.Vector2:
    return current_pos + (target_pos - current_pos) * delay

class GameWorld:
    def __init__(self, objects: list, collision_objects: list, interactable_objects: list) -> None:
        self.objects = objects
        self.static_objects = collision_objects
        self.interactable_objects = interactable_objects
        self.player = object_classes.Player(pg.Vector2(100, 100), pg.image.load(get_path('assets/sprites/test_dino.png')), True)
        self.camera_pos: pg.Vector2 = pg.Vector2(self.player.rect.x - SCREEN_WIDTH // 2, self.player.rect.y - SCREEN_HEIGHT // 2)
        self.bg_image = pg.image.load(get_path("assets/sprites/bg_skybox.png"))

    def do_updates(self, delta: float) -> None:
        self.player.update(delta, self)
        for i in self.interactable_objects:
            i.update(delta, self)

        #camera position
        target_pos: pg.Vector2 = pg.Vector2(self.player.rect.x - SCREEN_WIDTH // 2, self.player.rect.y - SCREEN_HEIGHT // 2)
        self.camera_pos = smooth_movement(self.camera_pos, target_pos, 0.1)
        self.camera_pos = pg.Vector2(max(0, min(self.player.rect.x - SCREEN_WIDTH // 2, LEVEL_WIDTH - SCREEN_WIDTH)), max(0, min(self.player.rect.y - SCREEN_HEIGHT // 2, LEVEL_HEIGHT - SCREEN_HEIGHT)))

    def do_render(self, screen):
        screen.fill("purple")
        screen.blit(self.bg_image, pg.Vector2())
        for o in self.objects + self.static_objects + self.interactable_objects:
            o.draw(screen, self.camera_pos)
        self.player.draw(screen, self.camera_pos)
