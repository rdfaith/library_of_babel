import pygame
import utils
from animator_object import *
from utils import *


def generate_hitbox(position: pygame.Vector2, hitbox_image: pygame.Surface) -> (pygame.Rect, pygame.Vector2):
    """Generates a rectangular hitbox based on the non-transparent part of hitbox_image, and returns the offset."""
    bbox = hitbox_image.get_bounding_rect()  # Get bounding rectangle of non-transparent area

    if bbox.width > 0 and bbox.height > 0:
        # Calculate the hitbox rect and its offset from the top-left corner of the image
        hitbox = pygame.Rect(position.x + bbox.x, position.y + bbox.y, bbox.width, bbox.height)
        offset = pygame.Vector2(bbox.x, bbox.y)  # The offset between the image and the hitbox
    else:
        # If fully transparent, return a default empty hitbox and zero offset
        hitbox = pygame.Rect(position.x, position.y, 0, 0)
        offset = pygame.Vector2(0, 0)

    return hitbox, offset


class GameObject:
    def __init__(self, position: pygame.Vector2, image: pygame.Surface, hitbox_image: pygame.Surface = None):
        self.image = image.convert_alpha()  # Sprite image

        # Use image to generate hitbox if no other hitbox is provided:
        if hitbox_image:
            rect, offset = generate_hitbox(position, hitbox_image)
            self.rect = rect
            self.sprite_offset = offset
        else:
            self.rect = self.image.get_rect(topleft=position)
            self.sprite_offset = pg.Vector2()  # null vector for no offset

    def update(self, delta: float, game_world):
        pass

    def draw(self, screen, camera_pos):
        """Draw object on screen."""
        position = self.rect.topleft - camera_pos
        screen.blit(self.image, position - self.sprite_offset)
        # Draw hit box, just for debugging:
        # pygame.draw.rect(screen, (255, 0, 0), self.rect.move(-camera_pos), 2)


class InteractableObject(GameObject):
    def on_collide(self, player, game_world) -> None:
        pass


class MovingObject(InteractableObject):
    def __init__(self, position: pygame.Vector2, image: pygame.Surface, gravity: bool,
                 hitbox_image: pygame.Surface = None):
        super().__init__(position, image, hitbox_image)
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

    def __init__(self, position: pygame.Vector2):
        image = pg.image.load(get_path('assets/sprites/dino/test_dino.png')).convert_alpha()
        hitbox_image = pg.image.load(get_path('assets/sprites/dino/test_hitbox.png')).convert_alpha()
        super().__init__(position, image, True, hitbox_image)
        self.letters_collected: list[str] = []
        self.speed_x = 100
        self.player_lives = 3
        self.bounce_velocity_x = 0
        self.time_since_hit: float = 0.0
        self.invincibility_time: float = 0.7
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

    def on_hit_by_enemy(self, enemy: GameObject, direction: int):
        if self.time_since_hit != 0.0:
            self.bounce_velocity_x = direction * 250
            self.velocity.y = -300

            if self.player_lives > 0:
                # self.player_lives -= 1
                pass

    def on_pickup_letter(self, letter: str):
        self.letters_collected.append(letter)

    def do_interaction(self, game_world):
        """Check if player collides with interactable object and calls according on_collide function."""
        for o in game_world.interactable_objects:
            if self.rect.colliderect(o.rect):
                o.on_collide(self, game_world)

    def update(self, delta: float, game_world, fallen: bool):
        #  Interact with interactable game elements and call their on_collide function
        WALK_SOUND = pg.mixer.Sound(get_path('assets/sounds/walk_sound.wav'))
        self.do_interaction(game_world)

        if fallen:
            self.player_lives = 0
        # get player movement
        keys = pygame.key.get_pressed()

        # Move the player left/right based on the keys pressed

        if keys[pygame.K_a] or keys[pygame.K_LEFT] and self.player_lives > 0:
            self.velocity.x = -self.speed_x  # Move left
            self.current_direction = -1
            self.is_running = True
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT] and self.player_lives > 0:
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
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.is_grounded(game_world.static_objects):  # and if is_grounded
            self.velocity.y = -self.speed_y
            self.is_jumping = True
        else:
            self.is_jumping = False

        self.check_animation()
        self.animator.update()

        #  Check collision and apply movement or not
        if self.velocity.x != 0:
            WALK_SOUND.play(loops=-1)
        super().update(delta, game_world)

        if self.time_since_hit < self.invincibility_time and not self.is_grounded(game_world.static_objects):
            self.time_since_hit += delta
        else:
            self.bounce_velocity_x = 0
            self.time_since_hit = 0.0


class LetterPickUp(InteractableObject):
    def __init__(self, position: pygame.Vector2, letter: str):
        self.letter = letter
        image = LETTER_IMAGES[letter]
        super().__init__(position, image, image)

    def on_collide(self, player, game_world) -> None:
        player.on_pickup_letter(self.letter)
        game_world.interactable_objects.remove(self)

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
            player.velocity.y = -250
            player.bounce_velocity_x = 0
            player.velocity.x = 0
            game_world.interactable_objects.remove(self)  # Remove enemy from the game
        else:
            player.on_hit_by_enemy(self, self.current_direction)


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
        # pygame.draw.rect(screen, (255, 0, 0), self.rect.move(-camera_pos), 2)
