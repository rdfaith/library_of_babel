import pygame
import utils
from animator_object import *
from utils import *


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
        self.speed_y = 400
        self.velocity = pygame.math.Vector2(0.0, 0.0)
        self.gravity = gravity
        self.has_collided = False

    def set_animation(self, animation) -> None:
        pass

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

    def update(self, delta: float, game_world):
        """update hit box and position depending on collision"""
        # x axis
        preview_rect_x = self.rect.move(self.velocity.x * delta + 1 if self.velocity.x > 0 else -1, 0)
        if not self.does_collide(preview_rect_x, game_world.static_objects):
            self.rect.x += self.velocity.x * delta
        else:
            self.has_collided = True

        # y axis
        if not self.is_grounded(game_world.static_objects):
            self.velocity.y += 30
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
        self.current_direction = 1
        self.is_jumping = False
        self.is_running = False

        # define animations
        self.run = Animation("run", get_path('assets/test/dino-run-test-Sheet.png'), 24, 24, 9, 10)
        self.idle = Animation("idle", get_path('assets/test/dino-test-idle-Sheet.png'), 24, 24, 6, 10)
        self.jump_up = Animation("jump_up", get_path('assets/test/dino-test-jump-up-Sheet.png'), 24, 24, 6, 10)
        self.fall = Animation("fall", get_path('assets/test/dino-test-fall-Sheet.png'), 24, 24, 8, 10)

        self.active_animation = self.idle
        self.animator = Animator(self.active_animation)

    def check_animation(self) -> None:
        if self.is_jumping:
            self.set_animation(self.jump_up)
        elif self.velocity.y > 0:
            self.set_animation(self.fall)
        elif self.is_running:
            self.set_animation(self.run)
        else:
            self.set_animation(self.idle)

    def set_animation(self, animation):
        if self.active_animation.name != animation.name:
            self.active_animation = animation
            self.animator = Animator(animation)
            self.animator.reset_animation(animation)

    def on_hit_by_enemy(self, enemy: GameObject):
        pass

    def do_interaction(self, game_world):
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
            self.current_direction = -1
            self.is_running = True
        elif keys[pygame.K_d]:
            self.velocity.x = self.speed_x  # Move right
            self.current_direction = 1
            self.is_running = True
        else:
            self.velocity.x = 0
            self.is_running = False

        # self.velocity.x += self.bounce_velocity_x
        if self.bounce_velocity_x != 0:
            self.velocity.x = self.bounce_velocity_x
            self.is_running = False

        # Move the player up based on keys pressed
        if keys[pygame.K_SPACE] and self.is_grounded(game_world.static_objects):  # and if is_grounded
            self.velocity.y = -self.speed_y
            self.is_jumping = True
        else:
            self.is_jumping = False

        self.check_animation()
        self.animator.update()

        #  Check collision and apply movement or not
        super().update(delta, game_world)

        if self.time_since_bounce < 0.7 and not self.is_grounded(game_world.static_objects):
            self.time_since_bounce += delta
        else:
            self.bounce_velocity_x = 0
            self.time_since_bounce = 0.0

    def draw(self, screen, camera_pos):
        position = self.rect.topleft - camera_pos
        screen.blit(self.animator.get_frame(self.current_direction), position)


class Enemy(MovingObject):

    def __init__(self, position: pygame.Vector2, image: pygame.Surface, gravity: bool):
        super().__init__(position, image, gravity)
        self.current_direction = 1

    def on_collide(self, player: Player, game_world) -> None:
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
        self.run = Animation("run", get_path('assets/test/worm-Sheet.png'), 32, 16, 5, 10)
        #self.die = Animation(get_path(), 32, 16, x, 10)

        self.active_animation = self.run
        self.animator = Animator(self.active_animation)

    def check_animation(self) -> None:
        # if self.is_dead:
        #   self.set_animation(self.die)
        # else:
        #   pass
        pass

    def set_animation(self, animation):
        if self.active_animation.name != animation.name:
            self.active_animation = animation
            self.animator = Animator(animation)
            self.animator.reset_animation(animation)

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
