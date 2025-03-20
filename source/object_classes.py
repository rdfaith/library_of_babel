import pygame
import utils
from game_world import *


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
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)


class MovingObject(GameObject):
    def __init__(self, position: pygame.Vector2, image: pygame.Surface, gravity: bool) -> None:
        super().__init__(position, image)
        self.speed_x = 100
        self.speed_y = 600
        self.velocity = pygame.math.Vector2(0.0, 0.0)
        self.gravity = gravity
        self.has_collided = False

    def does_collide(self, rect, objects: list):
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


class Player(MovingObject):

    def __init__(self, coords: tuple, image_path: str, gravity: bool):
        super().__init__(coords, image_path, gravity)
        self.player_lives = 3
        self.bounce_velocity_x = 0
        self.time_since_bounce: float = 0.0

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

        #self.velocity.x += self.bounce_velocity_x
        if self.bounce_velocity_x != 0:
            self.velocity.x = self.bounce_velocity_x

        # Move the player up based on keys pressed
        if keys[pygame.K_SPACE] and self.is_grounded(game_world.static_objects):  # and if is_grounded
            self.velocity.y = -self.speed_y

        #  Check collision and apply movement or not
        super().update(delta, game_world)

        if self.time_since_bounce < 0.5:
            self.time_since_bounce += delta
        else:
            self.bounce_velocity_x = 0
            self.time_since_bounce = 0.0

class Enemy(MovingObject):

    def __init__(self, coords: tuple, image_path: str, gravity: bool):
        super().__init__(coords, image_path, gravity)
        self.current_direction = 1

    def on_collide(self, player: Player, game_world: GameWorld) -> None:
        """Is called on collision with player and reduces lives."""
        threshold = 5

        # player can currently run into the enemy and kill them with the bounce back they should experience

        if player.velocity.y < 0 and player.rect.bottom <= self.rect.top + threshold:
            print(player.rect.bottom)
            print(self.rect.top + threshold)
            # If player jumps on top of it, enemy dies
            game_world.interactable_objects.remove(self)  # Remove enemy from the game
            player.velocity.y = -250

        else:
            player.player_lives -= 1
            player.bounce_velocity_x = self.current_direction * 200
            player.velocity.y = -250
            self.has_collided = True


class Worm(Enemy):
    def __init__(self, coords: tuple, image_path: str, gravity: bool):
        super().__init__(coords, image_path, gravity)
        self.speed_x = 40
        self.distance = 0
        self.max_distance = 50

    def update(self, delta: float, game_world):
        self.velocity.x = self.current_direction * self.speed_x

        super().update(delta, game_world)

        if not self.has_collided:
            self.distance += abs(self.velocity.x * delta)

        if self.distance >= self.max_distance or self.has_collided:
            self.current_direction *= (-1)
            self.distance = 0
            self.has_collided = False

