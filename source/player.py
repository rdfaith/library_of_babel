import pygame
from utils import *
from object_classes import *
from animator_object import *
from enum import Enum

class State(Enum):
    IDLE = 1
    RUN = 2
    JUMP = 3
    FALL = 4
    DUCK = 5

class Player(MovingObject):

    def __init__(self, position: pygame.Vector2):
        image = pg.image.load(get_path('assets/sprites/dino/test_dino.png')).convert_alpha()
        hitbox_image = pg.image.load(get_path('assets/sprites/dino/test_hitbox.png')).convert_alpha()
        super().__init__(position, image, True, hitbox_image)
        self.letters_collected: list[str] = []
        self.speed_x = 70
        self.player_lives = 3
        self.bounce_velocity_x = 0
        self.time_since_hit: float = 0.0
        self.invincibility_time: float = 0.7
        self.current_direction = 1
        self.is_jumping = False
        self.is_running = False

        # define animations
        self.run = Animation("run", get_path('assets/test/dino-run-test-Sheet.png'), 24, 24, 9, 14)
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
                self.player_lives -= 1
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

    def draw(self, screen, camera_pos):
        position = self.rect.topleft - camera_pos
        screen.blit(self.animator.get_frame(self.current_direction), position - self.sprite_offset)
        # Draw hit box, just for debugging:
        # pygame.draw.rect(screen, (255, 0, 0), self.rect.move(-camera_pos), 2)