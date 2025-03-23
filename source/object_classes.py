import pygame as pg
from utils import *
from hitbox import Hitbox
from animator_object import *
from constants import *


class GameObject:
    def __init__(self, position: pg.Vector2, image: pg.Surface):
        self.image = image.convert_alpha()  # Sprite image
        self.position = position.copy()

    def update(self, delta: float, game_world):
        pass

    def draw(self, screen, camera_pos):
        """Draw object on screen."""
        position = self.position - camera_pos
        screen.blit(self.image, position)


class AnimatedObject(GameObject):
    """Base class for objects that are animated. No colliders or hitboxes. Used for decorative objects."""

    def __init__(self, position: pg.Vector2, animation: Animation):
        self.animation: Animation = animation
        self.animator: Animator = Animator(animation)
        super().__init__(position, self.animator.get_frame(1))

    def draw(self, screen, camera_pos):
        self.animator.update()
        position = self.position - camera_pos
        screen.blit(self.animator.get_frame(1), position)


class ColliderObject(GameObject):
    """Base class for all object with a collider"""

    def __init__(self, position: pg.Vector2, image: pg.Surface, hitbox_image: pg.Surface = None):
        super().__init__(position, image)

        # Use image to generate hitbox if no other hitbox is provided:
        if hitbox_image:
            self.hitbox = Hitbox.generate(position, hitbox_image, True)
        else:
            self.hitbox = Hitbox.generate(position, image, False)

    def get_rect(self) -> pg.Rect:
        return self.hitbox.get_rect()

    def get_sprite_offset(self) -> pg.Vector2:
        return self.hitbox.get_offset()

    def set_hitbox(self, hitbox_name: str):
        self.position -= self.hitbox.get_offset_diff(hitbox_name)  # Adjust position for new hitbox
        self.hitbox.set_current(hitbox_name)

    def try_set_hitbox(self, hitbox_name: str, game_world) -> bool:
        """Switches hitbox to hitbox_name if it doesn't cause collision, else doesn't switch.
        Returns True if switched, else False."""
        previous_hitbox: str = self.hitbox.get_current()

        # Set new hitbox
        self.set_hitbox(hitbox_name)
        rect = self.get_rect()
        rect.topleft = self.position

        if self.check_collision(rect, game_world.static_objects) is None:  # No collision detected
            return True
        else:
            self.set_hitbox(previous_hitbox)  # Go back to original hitbox
            return False

    def check_collision(self, rect, collider_objects):
        """Checks for collision and returns the GameObject of the first collision it finds.
        If there are no collisions detected, returns None."""

        for col_obj in collider_objects:
            if rect.colliderect(col_obj.get_rect()):  # Check collision
                return col_obj
        return None

    def draw(self, screen, camera_pos):
        """Draw object on screen."""
        rect = self.get_rect()
        sprite_offset = self.get_sprite_offset()
        position = rect.topleft - camera_pos
        screen.blit(self.image, position - sprite_offset)


class InteractableObject(ColliderObject):
    """Base class for all objects that define special behaviour when colliding with player"""

    def on_collide(self, player, game_world) -> None:
        pass


class MovingObject(InteractableObject):
    """Base class for all moving objects with physical collision handling"""

    def __init__(self, position: pg.Vector2, image: pg.Surface, has_gravity: bool,
                 hitbox_image: pg.Surface = None):
        super().__init__(position, image, hitbox_image)
        self.max_y_velocity = 800.0
        self.gravity = 30.0
        self.speed_x = 75.0
        self.speed_y = 400.0
        self.velocity = pg.Vector2(0.0, 0.0)
        self.has_gravity = has_gravity
        self.has_collided = False

    def set_animation(self, animation) -> None:
        pass

    def does_collide(self, rect, objects: list) -> bool:
        """Check if hit box collides with another object."""
        for o in objects:
            if rect.colliderect(o.get_rect()):
                return True
        return False

    def check_is_grounded(self, objects: list) -> bool:
        """Check if element is on the floor."""
        preview_rect = self.get_rect().move(0, 1)
        if self.does_collide(preview_rect, objects):
            return True
        else:
            return False

    def update(self, delta: float, game_world):
        """update hit box and position depending on collision"""

        # Apply gravity
        if self.has_gravity:
            self.velocity.y = min(self.velocity.y + self.gravity, self.max_y_velocity)

        # Calculate movement
        dx, dy = self.velocity * delta

        # Move x and check collisions
        rect = self.get_rect()
        self.position.x += dx
        rect.topleft = self.position

        self.has_collided = False

        colliding_object = self.check_collision(rect, game_world.static_objects)
        if colliding_object:
            self.has_collided = True
            if dx > 0:  # Moving right
                rect.right = colliding_object.get_rect().left
            elif dx < 0:  # Moving left
                rect.left = colliding_object.get_rect().right
            self.position.x, _ = rect.topleft  # Reset precise position

        # move y and check collisions
        self.position.y += dy
        rect.topleft = self.position

        colliding_object = self.check_collision(rect, game_world.static_objects)
        if colliding_object:
            if dy > 0:  # Falling down
                rect.bottom = colliding_object.get_rect().top
                self.velocity.y = 0
                # self.on_ground = True
            elif dy < 0:  # Hitting the ceiling
                rect.top = colliding_object.get_rect().bottom
                self.velocity.y = 0
            _, self.position.y = rect.topleft  # Reset precise position


class LetterPickUp(InteractableObject):
    def __init__(self, position: pg.Vector2, letter: str):
        self.letter = letter
        image = LETTER_IMAGES[letter]
        super().__init__(position, image, image)

    def on_collide(self, player, game_world) -> None:
        if player.on_pickup_letter(self.letter):  # If player picks up (doesn't pick up if inventory full)
            game_world.interactable_objects.remove(self)


class Enemy(MovingObject):

    def __init__(self, position: pg.Vector2, image: pg.Surface, gravity: bool):
        super().__init__(position, image, gravity)
        self.current_direction = 1

    def on_collide(self, player, game_world) -> None:
        """Is called on collision with player and reduces lives."""
        threshold = 5

        if player.velocity.y < 0 and player.get_rect().bottom <= self.get_rect().top + threshold:
            # If player jumps on top of it, enemy dies
            player.velocity.y = -250
            player.bounce_velocity_x = 0
            player.velocity.x = 0
            game_world.interactable_objects.remove(self)  # Remove enemy from the game
        else:
            player.on_hit_by_enemy(self, self.current_direction)


class Worm(Enemy):
    def __init__(self, position: pg.Vector2):
        super().__init__(position, pg.image.load(get_path("assets/test/worm.png")), True)
        self.speed_x = 10
        self.distance = 0
        self.max_distance = 50
        self.run = Animation("run", get_path('assets/sprites/anim/worm_walk.png'), 32, 16, 5, 10)
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

        super().update(delta, game_world)

        if not self.has_collided:
            self.distance += abs(self.velocity.x * delta)

        if self.distance >= self.max_distance or self.has_collided:
            self.current_direction *= (-1)
            self.distance = 0
            self.has_collided = False

        self.animator.update()

    def draw(self, screen, camera_pos):
        position = self.get_rect().topleft - camera_pos
        screen.blit(self.animator.get_frame(self.current_direction), position)
        # Draw hit box, just for debugging:
        # pg.draw.rect(screen, (255, 0, 0), self.get_rect().move(-camera_pos), 2)
