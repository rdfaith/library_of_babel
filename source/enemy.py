import pygame
from player import Player
from object_classes import *


class Enemy(MovingObject):

    def __init__(self, position: pygame.Vector2, image: pygame.Surface, gravity: bool):
        super().__init__(position, image, gravity)
        self.current_direction = 1

    def on_collide(self, player: Player, game_world: GameWorld) -> None:
        """Is called on collision with player and reduces lives."""
        threshold = 5

        if player.velocity.y < 0 and player.rect.bottom <= self.rect.top + threshold:
            # If player jumps on top of it, enemy dies
            game_world.interactable_objects.remove(self)  # Remove enemy from the game
            player.velocity.y = -250
            player.bounce_velocity_x = 0
            player.velocity.x = 0

        else:
            player.player_lives -= 1
            player.bounce_velocity_x = self.current_direction * 250
            player.velocity.y = -300


class Worm(Enemy):
    def __init__(self, position: pygame.Vector2):
        super().__init__(position, pygame.image.load(get_path("assets/test/worm.png")), True)
        self.speed_x = 30
        self.distance = 0
        self.max_distance = 50
        self.animator = Animator(pygame.image.load(get_path('assets/test/worm-Sheet.png')), 32, 16, 5, 10)

    def update(self, delta: float, game_world):
        self.velocity.x = self.current_direction * self.speed_x
        self.animator.update()

        super().update(delta, game_world)

        if not self.has_collided:
            self.distance += abs(self.velocity.x * delta)

        if self.distance >= self.max_distance or self.has_collided:
            self.current_direction *= (-1)
            self.distance = 0
            self.has_collided = False

    def draw(self, screen, camera_pos):
        position = self.rect.topleft - camera_pos
        screen.blit(self.animator.get_frame(self.current_direction), position)
        # Draw hit box, just for debugging:
        pygame.draw.rect(screen, (255, 0, 0), self.rect.move(-camera_pos), 2)
