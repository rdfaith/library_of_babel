import object_classes
import pygame as pg


class GameWorld:
    def __init__(self, objects: list, collision_objects: list, interactable_objects: list) -> None:
        self.objects = objects
        self.static_objects = collision_objects
        self.interactable_objects = interactable_objects
        self.player = object_classes.Player((100, 100), 'assets/test/egg.png', True)
        self.camera_pos: pg.Vector2 = pg.Vector2(0, 0)

    def do_updates(self, delta: float) -> None:
        self.player.update(delta, self.static_objects)

    def do_render(self, screen):
        screen.fill("purple")
        for o in self.objects + self.static_objects + self.interactable_objects:
            o.draw(screen)
        self.player.draw(screen)
