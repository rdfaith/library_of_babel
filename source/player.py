import pygame
import pygame as pg
from utils import *
from object_classes import *
from animator_object import *
from enum import Enum

# Pygame event for player death
PLAYER_DIED = pygame.USEREVENT + 1  # Custom event ID 25 (USEREVENT starts at 24)

class Player(MovingObject):
    # Player states
    class State(Enum):
        IDLE = 1
        RUN = 2
        JUMP = 3
        FALL = 4
        DUCK = 5
        DEAD = 6

    def __init__(self, position: pygame.Vector2):
        image = pg.image.load(get_path('assets/sprites/dino/test_dino.png')).convert_alpha()
        hitbox_image = pg.image.load(get_path('assets/sprites/dino/test_hitbox.png')).convert_alpha()
        super().__init__(position, image, True, hitbox_image)

        self.letters_collected: list[str] = []
        self.speed_x = 70
        self.jump_force = 400
        self.player_lives = 3
        self.bounce_velocity_x = 0
        self.time_since_hit: float = 0.0
        self.invincibility_time: float = 0.7
        self.current_direction = 1

        self.state = None

        self.is_jumping = False
        self.is_running = False

        # define animations
        self.run = Animation("run", get_path('assets/test/dino-run-test-Sheet.png'), 24, 24, 9, 14)
        self.idle = Animation("idle", get_path('assets/test/dino-test-idle-Sheet.png'), 24, 24, 6, 10)
        self.jump_up = Animation("jump_up", get_path('assets/test/dino-test-jump-up-Sheet.png'), 24, 24, 6, 10)
        self.fall = Animation("fall", get_path('assets/test/dino-test-fall-Sheet.png'), 24, 24, 8, 10)

        self.active_animation = self.idle
        self.animator = Animator(self.active_animation)

    def set_animation(self, animation: Animation) -> None:
        self.active_animation = animation
        self.animator = Animator(animation)
        self.animator.reset_animation(animation)

    def on_player_death(self, reason: str):
        self.player_lives = 0
        self.state = self.State.DEAD
        # self.set_animation(self.dead) # uncomment when death animation implemented
        pg.event.post(pygame.event.Event(PLAYER_DIED, {"reason": reason}))

    def on_hit_by_enemy(self, enemy: GameObject, direction: int):
        if self.time_since_hit != 0.0:
            self.bounce_velocity_x = direction * 250
            self.velocity.y = -300

            if self.player_lives > 1:
                self.player_lives -= 1
            else:
                self.on_player_death("hit by enemy")

    def on_fell_out_of_bounds(self):
        self.on_player_death("fell out of bounds")

    def on_pickup_letter(self, letter: str):
        self.letters_collected.append(letter)

    def on_state_changed(self, state: Enum):
        """Called when the player state (RUN, IDLE, JUMP, etc.) changes"""

        # Change animation:
        match state:
            case self.State.FALL:
                self.set_animation(self.fall)
            case self.State.JUMP:
                self.set_animation(self.jump_up)
            case self.State.RUN:
                self.set_animation(self.run)
            case _:
                self.set_animation(self.idle)

    def do_interaction(self, game_world):
        """Check if player collides with interactable object and calls according on_collide function."""
        for o in game_world.interactable_objects:
            if self.rect.colliderect(o.rect):
                o.on_collide(self, game_world)

    def handle_movement(self, keys, game_world):
        """Sets player movement and state according to input and switches animation if necessary"""

        # If dead, do nothing
        if self.state == self.State.DEAD:
            return

        new_state = self.state
        is_grounded = self.check_is_grounded(game_world.static_objects)

        if keys[pg.K_a] or keys[pg.K_LEFT]:
            self.velocity.x = -self.speed_x  # Move left
            self.current_direction = -1
            new_state = self.State.RUN
        elif keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.velocity.x = self.speed_x  # Move right
            self.current_direction = 1
            new_state = self.State.RUN
        elif is_grounded:
            self.velocity.x = 0
            new_state = self.State.IDLE

        if is_grounded:
            if keys[pg.K_SPACE]:
                self.velocity.y = -self.jump_force
                new_state = self.State.JUMP
            elif keys[pg.K_DOWN] or keys[pg.K_s]:

                new_state = self.State.DUCK
        elif self.velocity.y <= 0:
            new_state = self.State.JUMP
        else:
            new_state = self.State.FALL

        if new_state != self.state:
            self.state = new_state
            self.on_state_changed(self.state)

    def update(self, delta: float, game_world):
        #  Interact with interactable game elements and call their on_collide function
        WALK_SOUND = pg.mixer.Sound(get_path('assets/sounds/walk_sound.wav'))

        self.do_interaction(game_world)

        # get player movement
        keys = pygame.key.get_pressed()

        self.handle_movement(keys, game_world)

        # Check invincibility frames
        if self.time_since_hit < self.invincibility_time:
            self.time_since_hit += delta
            if self.bounce_velocity_x != 0:
                self.velocity.x = self.bounce_velocity_x
        else:
            self.bounce_velocity_x = 0
            self.time_since_hit = 0.0


        # Check collision and apply movement or not
        super().update(delta, game_world)

        self.animator.update()

    def draw(self, screen, camera_pos):
        position = self.rect.topleft - camera_pos
        screen.blit(self.animator.get_frame(self.current_direction), position - self.sprite_offset)
        # Draw hit box, just for debugging:
        # pygame.draw.rect(screen, (255, 0, 0), self.rect.move(-camera_pos), 2)
