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
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)


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


class Player(MovingObject):

    def __init__(self, position: pygame.Vector2, image: pygame.Surface, gravity: bool):
        super().__init__(position, image, gravity)
        self.speed_x = 100
        self.player_lives = 3
        self.bounce_velocity_x = 0
        self.time_since_bounce: float = 0.0

    def on_hit_by_enemy(self, enemy: GameObject, direction: int):
        self.bounce_velocity_x = direction * 250
        self.velocity.y = -300

        if self.player_lives > 0:
            self.player_lives -= 1

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
        
        if keys[pygame.K_a] and self.player_lives >0:
            self.velocity.x = -self.speed_x  # Move left
        elif keys[pygame.K_d] and self.player_lives >0:
            self.velocity.x = self.speed_x  # Move right
        else:
            self.velocity.x = 0

        # self.velocity.x += self.bounce_velocity_x
        if self.bounce_velocity_x != 0:
            self.velocity.x = self.bounce_velocity_x

        # Move the player up based on keys pressed
        if self.player_lives >0:
            if keys[pygame.K_SPACE] and self.is_grounded(game_world.static_objects):  # and if is_grounded
                self.velocity.y = -self.speed_y

        #  Check collision and apply movement or not
        super().update(delta, game_world)

        if self.time_since_bounce < 0.7 and not self.is_grounded(game_world.static_objects):
            self.time_since_bounce += delta
        else:
            self.bounce_velocity_x = 0
            self.time_since_bounce = 0.0


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
            player.on_hit_by_enemy(self, self.current_direction)


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
