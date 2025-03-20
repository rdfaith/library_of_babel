import pygame
import utils
from game_world import *
from animator_object import Animator


class GameObject:
    def __init__(self, position: pygame.Vector2, image: pygame.Surface) -> None:
        self.image = image
        self.rect = self.image.get_rect(topleft=position)

    def update(self, delta: float, game_world):
        pass

    def draw(self, screen, camera_pos):
        """Draw object on screen."""
        position = self.rect.topleft - camera_pos
        screen.blit(self.image, position)
        # Draw hit box, just for debugging:
        # pygame.draw.rect(screen, (255, 0, 0), self.rect.move(-camera_pos), 2)


class MovingObject(GameObject):
    def __init__(self, position: pygame.Vector2, image: pygame.Surface, gravity: bool) -> None:
        super().__init__(position, image)
        self.speed_x = 75
        self.speed_y = 600
        self.velocity = pygame.math.Vector2(0.0, 0.0)
        self.gravity = gravity
        self.has_collided = False

    def does_collide(self, rect, objects: list) -> bool:
        """Check if hit box collides with another object."""
        for o in objects:
            if rect.colliderect(o.rect):
                return True
        return False

    def is_grounded(self, objects: list):
        """Check if element is on the floor."""
        preview_rect = self.rect.move(0, 1)
        if self.does_collide(preview_rect, objects):
            return True
        else:
            return False

    def update(self, delta: float, game_world: GameWorld):
        """update hit box and position depending on collision"""
        # x axis
        preview_rect_x = self.rect.move(self.velocity.x * delta + 1 if self.velocity.x > 0 else -1, 0)
        if not self.does_collide(preview_rect_x, game_world.static_objects):
            self.rect.x += self.velocity.x * delta
        else:
            self.has_collided = True

        # y axis
        if not self.is_grounded(game_world.static_objects):
            self.velocity.y += 50
        preview_rect_y = self.rect.move(0, self.velocity.y * delta)
        if not self.does_collide(preview_rect_y, game_world.static_objects):
            self.rect.move_ip(0, self.velocity.y * delta)
        else:
            self.velocity.y = 0