import pygame
from enemy import Enemy
from object_classes import *


class Player(MovingObject):

    def __init__(self, position: pygame.Vector2, image: pygame.Surface, gravity: bool):
        super().__init__(position, image, gravity)
        self.speed_x = 100
        self.player_lives = 3
        self.bounce_velocity_x = 0
        self.time_since_bounce: float = 0.0

    def on_hit_by_enemy(self, enemy: Enemy):
        pass

    def do_interaction(self, game_world: GameWorld):
        """Check if player collides with interactable object and calls according on_collide function."""
        for o in game_world.interactable_objects:
            if self.rect.colliderect(o.rect):
                o.on_collide(self, game_world)

    def update(self, delta: float, game_world):
        #  Interact with interactable game elements and call their on_collide function
        self.do_interaction(game_world)

        # get player movement
        keys = pygame.key.get_pressed()

        # Move the player left/right based on the keys pressed
        if keys[pygame.K_a]:
            self.velocity.x = -self.speed_x  # Move left
        elif keys[pygame.K_d]:
            self.velocity.x = self.speed_x  # Move right
        else:
            self.velocity.x = 0

        # self.velocity.x += self.bounce_velocity_x
        if self.bounce_velocity_x != 0:
            self.velocity.x = self.bounce_velocity_x

        # Move the player up based on keys pressed
        if keys[pygame.K_SPACE] and self.is_grounded(game_world.static_objects):  # and if is_grounded
            self.velocity.y = -self.speed_y

        #  Check collision and apply movement or not
        super().update(delta, game_world)

        if self.time_since_bounce < 0.7 and not self.is_grounded(game_world.static_objects):
            self.time_since_bounce += delta
        else:
            self.bounce_velocity_x = 0
            self.time_since_bounce = 0.0
