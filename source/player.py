import pygame
import pygame as pg
from utils import *
from object_classes import *
from animator_object import *
from enum import Enum
from sound_manager import *
from light_source import LightSource

# Pygame event for player death
PLAYER_DIED = pygame.USEREVENT + 1  # Custom event ID 25 (USEREVENT starts at 24)
PLAYER_WON = pygame.USEREVENT + 2


class Player(MovingObject):
    # Player states
    class State(Enum):
        IDLE = 1
        RUN = 2
        JUMP = 3
        FALL = 4
        DUCK_IDLE = 5
        DUCK_WALK = 6
        DASH = 7
        DEAD = 8
        WIN = 9

    def __init__(self, position: pygame.Vector2):
        image = pg.image.load(get_path('assets/sprites/dino/test_dino.png')).convert_alpha()
        hitbox_image = pg.image.load(get_path('assets/sprites/dino/test_hitbox.png')).convert_alpha()
        hitbox_image_crouch = pg.image.load(get_path('assets/sprites/dino/test_hitbox_crouch.png')).convert_alpha()

        super().__init__(position, image, True, hitbox_image)

        self.hitbox.add_hitbox("crouch", self.position, hitbox_image_crouch)

        self.light_source: LightSource = LightSource(
            self.position,
            pg.Vector2(10, 12),
            pg.Color((100, 180, 250)),
            25.0,
            0.04
        )

        self.letters_collected: list[str] = []
        self.speed_x = 70
        self.jump_force = 400
        self.player_lives = 3
        self.bounce_velocity_x = 0
        self.invincibility_time: float = 0.7
        self.current_direction: int = 1

        self.state = self.State.IDLE

        if DEBUG_MODE:
            self.is_jump_unlocked: bool = True
            self.is_crouch_unlocked: bool = True
            self.is_dash_unlocked: bool = True
        else:
            self.is_jump_unlocked: bool = False
            self.is_crouch_unlocked: bool = False
            self.is_dash_unlocked: bool = False

        # dash values
        self.dash_speed = 600  # Dash speed multiplier
        self.dash_time: float = 0.2  # Dash duration in seconds
        self.dash_cooldown: float = 2.0  # Cooldown before dashing again
        self.dash_timer = 0  # Time left in current dash
        self.dash_cooldown_timer = 0  # Cooldown timer after dash

        # define animations
        self.run = Animation("run", get_path('assets/test/dino-run-test-Sheet.png'), 24, 24, 9, 14)
        self.idle = Animation("idle", get_path('assets/test/dino-test-idle-Sheet.png'), 24, 24, 6, 10)
        self.jump_up = Animation("jump_up", get_path('assets/test/dino-jump-up-Sheet.png'), 24, 24, 6, 30)
        self.fall = Animation("fall", get_path('assets/test/dino-fall-Sheet.png'), 24, 24, 8, 24)
        self.duck_walk = Animation("duck_run", get_path('assets/test/dino-duck-walk-Sheet.png'), 24, 24, 6, 10)
        self.duck_idle = Animation("duck_idle", get_path('assets/test/dino-duck-idle-Sheet.png'), 24, 24, 1, 10)
        self.dash = Animation("dash", get_path('assets/test/dino-run-test-Sheet.png'), 24, 24, 9, 10)
        self.dead = Animation("dead", get_path('assets/test/egg.png'), 24, 24, 1, 10)

        self.active_animation = self.idle
        self.animator = Animator(self.active_animation)

        self.sound_manager = SoundManager()

    def set_animation(self, animation: Animation) -> None:
        self.active_animation = animation
        self.animator = Animator(animation)
        self.animator.reset_animation()

    def on_player_death(self, reason: str):
        self.player_lives = 0
        self.state = self.State.DEAD
        self.on_state_changed(self.State.DEAD)
        self.set_animation(self.dead) # uncomment when death animation implemented
        pg.event.post(pygame.event.Event(PLAYER_DIED, {"reason": reason}))

    def on_player_win(self, reason: str):
        self.state = self.State.WIN
        self.on_state_changed(self.State.WIN)
        # self.set_animation(self.won) # uncomment when win animation implemented
        pg.event.post(pygame.event.Event(PLAYER_WON, {"reason": reason}))

    def on_hit_by_enemy(self, enemy: GameObject, direction: int):
        if self.invincibility_time == 0:
            self.bounce_velocity_x = -direction * 250
            self.velocity.y = -300
            self.invincibility_time = 0.7

            if self.player_lives > 1:
                print("Aua")
                self.sound_manager.play_movement_sound("damage")
                self.player_lives -= 1
            else:
                self.on_player_death("hit by enemy")

    def on_fell_out_of_bounds(self):
        self.on_player_death("fell out of bounds")

    def on_pickup_letter(self, letter: str) -> bool:
        """Called when player moves into collider of letter.
        Returns False if the letter can't be picked up, else True."""

        if len(self.letters_collected) >= 5:  # Break and return False if can't pick up
            return False

        self.letters_collected.append(letter)

        word = "".join(self.letters_collected).upper()

        word_completed = False

        match word:
            case "JUMP":
                self.is_jump_unlocked = True
                word_completed = True
            case "DUCK":
                self.is_crouch_unlocked = True
                word_completed = True
            case "DASH":
                self.is_dash_unlocked = True
                word_completed = True
            case "BABEL":
                print("Yayy, you won!")
            case "LIGHT":
                print("Es werde Licht")
                self.on_player_win("alle Buchstaben gesammelt")

        if word_completed:
            self.letters_collected = []

        return True

    def on_state_changed(self, state: Enum):
        """Called when the player state (RUN, IDLE, JUMP, etc.) changes"""

        # Change animation:
        match state:
            case self.State.FALL:
                self.set_animation(self.fall)
                self.sound_manager.play_movement_sound("fall")
            case self.State.JUMP:
                self.set_animation(self.jump_up)
                self.sound_manager.play_movement_sound("jump_up")
            case self.State.RUN:
                self.set_animation(self.run)
                self.sound_manager.play_movement_sound("run")
            case self.State.DUCK_IDLE:
                self.set_animation(self.duck_idle)
            case self.State.DUCK_WALK:
                self.set_animation(self.duck_walk)
            case self.State.DASH:
                self.set_animation(self.dash)
            case _:
                self.set_animation(self.idle)
                self.sound_manager.play_movement_sound("idle")

        # Change hitbox
        if self.state == self.State.DUCK_IDLE or self.state == self.State.DUCK_WALK:
            self.set_hitbox("crouch")
        else:
            self.set_hitbox("default")

    def do_interaction(self, game_world):
        """Check if player collides with interactable object and calls according on_collide function."""
        for o in game_world.interactable_objects:
            if self.get_rect().colliderect(o.get_rect()):
                o.on_collide(self, game_world)

    def handle_movement(self, keys, delta, game_world):
        """Sets player movement and state according to input and switches animation if necessary"""

        # If dead, do nothing
        if self.state == self.State.DEAD:
            return

        new_state = self.state
        is_grounded = self.check_is_grounded(game_world.static_objects)

        # Dash
        if self.is_dash_unlocked and keys[pg.K_LSHIFT] and self.dash_cooldown_timer <= 0 and self.dash_timer <= 0:
            self.has_gravity = False
            self.dash_timer = self.dash_time  # Start dash duration
            self.dash_cooldown_timer = self.dash_cooldown  # Start cooldown
            self.velocity.x = self.current_direction * self.dash_speed  # Apply dash speed
            new_state = self.State.DASH

        # Handle Input, input will be ignored if player is dashing
        if self.dash_timer <= 0:
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
                if self.is_jump_unlocked and (keys[pg.K_SPACE] or keys[pg.K_w] or keys[pg.K_UP]):
                    self.velocity.y = -self.jump_force
                    new_state = self.State.JUMP
                elif self.is_crouch_unlocked and (keys[pg.K_LCTRL] or keys[pg.K_s] or keys[pg.K_DOWN]):
                    if self.velocity.x != 0:
                        new_state = self.State.DUCK_WALK
                    else:
                        new_state = self.State.DUCK_IDLE
            elif self.velocity.y <= 0:
                new_state = self.State.JUMP
            else:
                new_state = self.State.FALL

        # Handle Dash Duration
        if self.dash_timer > 0:
            self.dash_timer -= delta
            if self.dash_timer <= 0:  # Dash ends
                self.velocity.x = 0 if not (keys[pg.K_LEFT] or keys[pg.K_RIGHT]) else self.velocity.x
                new_state = self.State.RUN if (keys[pg.K_LEFT] or keys[pg.K_RIGHT]) else self.State.IDLE
                self.has_gravity = True

        # Handle Dash Cooldown Timer
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= delta

        # Not crouch -> crouch
        if (self.state != self.State.DUCK_IDLE or self.state != self.State.DUCK_WALK) and (new_state == self.state.DUCK_IDLE or new_state == self.state.DUCK_WALK):
            self.set_hitbox("crouch")
        # Crouch -> not crouch (disallow uncrouching when that would collide with ceiling)
        if (self.state == self.State.DUCK_IDLE or self.state == self.State.DUCK_WALK) and new_state != self.state.DUCK_IDLE and new_state != self.state.DUCK_WALK:
            if not self.try_set_hitbox("default", game_world):  # If switching hitbox to default fails
                new_state = self.state  # Set back to DUCK

        if new_state != self.state:
            self.state = new_state
            self.on_state_changed(self.state)

    def update(self, delta: float, game_world):

        # get player movement
        keys = pygame.key.get_pressed()

        # Check invincibility frames
        if self.invincibility_time > 0:
            self.invincibility_time -= delta
            if self.invincibility_time <= 0:
                self.invincibility_time = 0

        #  Interact with interactable game elements and call their on_collide function
        self.do_interaction(game_world)

        self.handle_movement(keys, delta, game_world)

        if self.bounce_velocity_x != 0:
            if self.check_is_grounded(game_world.static_objects) and self.invincibility_time != 0.7:
                self.bounce_velocity_x = 0
            else:
                self.velocity.x = self.bounce_velocity_x

        # Check collision and apply movement or not
        super().update(delta, game_world)

        self.animator.update()
        self.light_source.set_position(self.position)  # update position of light source

    def draw(self, screen, camera_pos):
        position = self.get_rect().topleft - camera_pos
        screen.blit(self.animator.get_frame(self.current_direction), position - self.get_sprite_offset())
        # Draw hit box, just for debugging:
        # pygame.draw.rect(screen, (255, 0, 0), self.get_rect().move(-camera_pos), 2)
