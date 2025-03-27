from source import *
from source.object_classes import GameObject, MovingObject, MovingPlatform, Enemy, KeyPickUp

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

    def __init__(self, position: pg.Vector2):
        image = pg.image.load(get_path('assets/sprites/dino/test_dino.png')).convert()
        hitbox_image = pg.image.load(get_path('assets/sprites/dino/test_hitbox.png')).convert()
        hitbox_image_crouch = pg.image.load(get_path('assets/sprites/dino/test_hitbox_crouch.png')).convert()

        super().__init__(position, image, True, hitbox_image=hitbox_image)

        self.hitbox.add_hitbox("crouch", self.position, hitbox_image_crouch)

        self.light_source: LightSource = LightSource(
            self.position,
            pg.Vector2(5, 5),
            pg.Color((100, 180, 250)),
            25.0,
            0.03
        )

        self.speed_x = 90.0
        self.jump_force = 330.0
        self.gravity = 20.0
        self.max_y_velocity = 400.0
        self.player_lives = 3
        self.bounce_velocity_x = 0
        self.invincibility_time: float = 0.0
        self.current_direction: int = 1
        self.time_until_over = 5.0
        self.jump_timer = 0.0  # tracks how long player is jumping for variable jump height

        self.state = self.State.IDLE

        if DEBUG_MODE:
            self.is_jump_unlocked: bool = True
            self.is_crouch_unlocked: bool = True
            self.is_dash_unlocked: bool = True
            self.is_wall_jump_unlocked: bool = False
            self.is_double_jump_unlocked: bool = True
        else:
            self.is_jump_unlocked: bool = False
            self.is_crouch_unlocked: bool = False
            self.is_dash_unlocked: bool = False
            self.is_wall_jump_unlocked: bool = False
            self.is_double_jump_unlocked: bool = False

        self.letters_collected: list[str] = []
        self.word_animation_timer = 0.0
        self.has_wrong_word = False  # does player have nonsense word?
        self.last_word_completed = ""

        # Does Player Have Key?
        self.has_key = False

        # Has Player picked up time item this frame?
        self.picked_up_time = False

        # Dash Values
        self.dash_speed = 450.0  # Dash speed multiplier
        self.dash_time: float = 0.2  # Dash duration in seconds
        self.dash_cooldown: float = 0.7  # Cooldown before dashing again
        self.dash_timer = 0  # Time left in current dash
        self.dash_cooldown_timer = 0  # Cooldown timer after dash

        # Value for Double and Wall Jump
        self.jump_lock = False  # Makes sure that player has to jump multiple times and can't just keep Space pressed
        self.jumps_collected = 0
        self.wall_collected = False

        # Double Jump Values
        self.jump_counter = 0  # Counter for how many jumps since on ground
        self.jump_cooldown_time = 0.25  # Cooldown time until next jump possible
        self.jump_cooldown: float = 0.0  # Time left until cooldown

        # Wall Jump Values
        self.touching_wall_left = False
        self.touching_wall_right = False
        self.wall_jump_timer = 0.0  # Time left in current wall jump lock
        self.wall_jump_lock_time = 0.4  # Time that player movement is supposed to be locked
        self.is_wall_jumping = False

        # Define Animations
        self.run = Animation("run", get_path('assets/sprites/anim/dino-run-Sheet.png'), 24, 24, 9, 18)
        self.idle = Animation("idle", get_path('assets/sprites/anim/dino-idle-Sheet.png'), 24, 24, 6, 10)
        self.jump_up = Animation("jump_up", get_path('assets/sprites/anim/dino-jump-Sheet.png'), 24, 24, 3, 6, True)
        self.fall = Animation("fall", get_path('assets/sprites/anim/dino-fall-Sheet.png'), 24, 24, 3, 24, True)
        self.duck_walk = Animation("duck_run", get_path('assets/sprites/anim/dino-duck-walk-Sheet.png'), 24, 24, 6, 14)
        self.duck_idle = Animation("duck_idle", get_path('assets/sprites/anim/dino-duck-idle-Sheet.png'), 24, 24, 1, 10)
        self.dash = Animation("dash", get_path('assets/sprites/anim/dino-dash-Sheet.png'), 32, 24, 1, 1)
        self.dead = Animation("dead", get_path('assets/sprites/anim/dino-death-Sheet.png'), 24, 24, 8, 8)
        self.win = Animation("win", get_path('assets/sprites/anim/dino-win-Sheet.png'), 24, 24, 4, 8)
        self.still = Animation("still", get_path('assets/sprites/dino/dino-still.png'), 24, 24, 1)

        self.active_animation = self.idle
        self.animator = Animator(self.active_animation)

        self.sound_manager = SoundManager()

        self.got_damage = False

    def set_animation(self, animation: Animation) -> None:
        self.active_animation = animation
        self.animator = Animator(animation)
        self.animator.reset_animation()

    def on_player_death(self, reason: str):
        self.player_lives = 0
        self.state = self.State.DEAD
        self.on_state_changed(self.State.DEAD)

    def on_player_win(self):
        self.state = self.State.WIN
        self.on_state_changed(self.State.WIN)

    def on_hit_by_enemy(self, enemy: GameObject, direction: int):
        if self.invincibility_time == 0:
            self.bounce_velocity_x = -direction * 200
            self.velocity.y = -200
            self.invincibility_time = 0.7

            self.sound_manager.play_movement_sound("damage")

            if self.player_lives > 1:
                print("Aua")
                self.player_lives -= 1
            else:
                self.on_player_death("hit by enemy")

    def on_fell_out_of_bounds(self):
        self.on_player_death("fell out of bounds")

    def check_highscore(self, level, time):
        filename = LEVELS
        highscores = load_file(filename)
        minutes = int(time // 60)  # Ganze Minuten
        seconds = round((time % 60) / 100, 2)  # Sekunden als Dezimalanteil korrigiert
        current_time = minutes + seconds
        highscore_text = None
        if highscores[level] != "False":
            if float(highscores[level]) > current_time:
                highscores[level] = current_time
                update_file(filename, highscores)
                self.sound_manager.play_system_sound("new_highscore")
                highscore_text = FONT_8_BOLD.render(f"NEW HIGHSCORE! ({current_time})", True, (255, 255, 255))
                #print(f"New best Time for {level[:-4]} with {current_time}")

        else:
            highscores[level] = current_time
            update_file(filename, highscores)
            self.sound_manager.play_system_sound("new_highscore")
            highscore_text = FONT_8_BOLD.render(f"NEW HIGHSCORE! ({current_time})", True, (255, 255, 255))
            #print(f"New best Time for {level[:-4]} with {current_time}")
        return highscore_text

    def draw_highscore(self, highscore_text: str, screen):
        if highscore_text is not None:
            screen.blit(highscore_text, pg.Vector2((SCREEN_WIDTH - highscore_text.get_width()) // 2,
                                               (SCREEN_HEIGHT - highscore_text.get_height()) // 2))

    def on_pickup_key(self):
        self.has_key = True
        self.sound_manager.play_system_sound("collect")

    def on_pickup_heart(self):
        if self.player_lives < 3:
            self.player_lives += 1
            self.sound_manager.play_system_sound("collect")
            return True
        else:
            return False

    def on_pickup_time(self):
        self.sound_manager.play_system_sound("collect")
        self.picked_up_time = True
        return True

    def on_pickup_letter(self, letter: str, game_world) -> bool:
        """Called when player moves into collider of letter.
        Returns False if the letter can't be picked up, else True."""
        result = False
        self.completed_word = False

        if len(self.letters_collected) < 5:  # return True if can pick up
            self.letters_collected.append(letter)
            self.sound_manager.play_system_sound("collect")
            result = True

        word = "".join(self.letters_collected).upper()

        word_completed = False

        match word:
            case "JUMP":
                if self.wall_collected:
                    self.is_wall_jump_unlocked = True
                elif self.is_jump_unlocked:
                    self.is_double_jump_unlocked = True
                else:
                    self.is_jump_unlocked = True
                word_completed = True
            case "WALL":
                self.wall_collected = True
                word_completed = True
            case "DUCK":
                self.is_crouch_unlocked = True
                word_completed = True
            case "DASH":
                self.is_dash_unlocked = True
                word_completed = True
            case "KEY":
                game_world.interactable_objects.append(KeyPickUp(pg.Vector2(self.position.x + 48, self.position.y - 64)))
                word_completed = True
            case "BABEL":
                print("Yayy, you won!")
                self.highscore_text = self.check_highscore(game_world.level_name, game_world.level_timer)
                self.sound_manager.play_system_sound("wining")
                self.on_player_win()
            case "LIGHT":
                print("Es werde Licht!")
                pg.event.post(pg.event.Event(WORD_LIGHT))
                word_completed = True

        if word_completed:
            self.word_animation_timer = 1.0
            self.sound_manager.play_system_sound("magical_twinkle")
            self.last_word_completed = self.letters_collected.copy()
            self.letters_collected = []

        if len(self.letters_collected) >= 5 and not word_completed and word != "BABEL":
            self.has_wrong_word = True

        return result

    def check_is_wrong_word(self) -> bool:
        return self.has_wrong_word

    def on_state_changed(self, state: Enum, old_state=0):
        """Called when the player state (RUN, IDLE, JUMP, etc.) changes"""

        # Fall landing sound if previous state FALL
        if old_state == self.State.FALL and state in {self.State.IDLE, self.State.RUN, self.State.DEAD}:
            self.sound_manager.play_movement_sound("fall")

        # Change animation:
        match state:
            case self.State.FALL:
                self.set_animation(self.fall)
                self.sound_manager.play_movement_sound("idle")
            case self.State.JUMP:
                self.set_animation(self.jump_up)
                self.sound_manager.play_movement_sound("jump", loop=False, interrupt=True)
            case self.State.RUN:
                self.set_animation(self.run)
                self.sound_manager.play_movement_sound("run")
            case self.State.DUCK_IDLE:
                self.set_animation(self.duck_idle)
                self.sound_manager.play_movement_sound("idle")
            case self.State.DUCK_WALK:
                self.set_animation(self.duck_walk)
                self.sound_manager.play_movement_sound("run")
            case self.State.DASH:
                self.set_animation(self.dash)
                self.sound_manager.play_movement_sound("dash", False)
            case self.State.DEAD:
                self.set_animation(self.dead)
                self.sound_manager.play_system_sound("disappointed")
                self.sound_manager.play_movement_sound("idle")
            case self.State.WIN:
                self.set_animation(self.win)
                self.sound_manager.play_movement_sound("idle")
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

    def handle_movement(self, delta, game_world):
        """Updates the player's movement state based on input and game conditions."""

        # If dead, do nothing
        if self.state == self.State.DEAD or game_world.egg:
            return

        keys = pg.key.get_pressed()

        new_state = self.state
        is_grounded = self.check_is_grounded(game_world.static_objects)
        obj_below = is_grounded

        # Handle Input, input will be ignored if player is dashing or wall jumping
        if self.dash_timer > 0:  # if dashing
            self.velocity.y = 0  # no y velocity while dashing
        elif self.is_wall_jumping:
            pass
        else:  # if not dashing and not wall jumping
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

            if isinstance(obj_below, MovingPlatform):
                self.velocity.x += obj_below.current_direction * obj_below.speed_x

        # Update Jump Lock to check whether player has released the key in between jumps
        if not (keys[pg.K_SPACE] or keys[pg.K_w] or keys[pg.K_UP]):
            self.jump_lock = False

        # Update Wall Jump Timer
        if self.wall_jump_timer != 0.0:
            self.wall_jump_timer -= delta
            if self.wall_jump_timer <= 0:
                self.wall_jump_timer = 0.0
                self.is_wall_jumping = False

        has_jumped = False

        # Wall Jump
        if (self.touching_wall_right or self.touching_wall_left) and not is_grounded and self.wall_jump_timer == 0.0:
            self.jump_counter = 0
            if self.is_wall_jump_unlocked and (
                    keys[pg.K_SPACE] or keys[pg.K_w] or keys[pg.K_UP]) and not self.jump_lock:
                self.velocity.y = -self.jump_force
                new_state = self.State.JUMP
                self.jump_cooldown = self.jump_cooldown_time
                self.wall_jump_timer = self.wall_jump_lock_time
                self.is_wall_jumping = True
                self.jump_lock = True
                has_jumped = True
                if self.touching_wall_right:
                    self.current_direction = -1
                    self.velocity.x = -self.speed_x
                else:
                    self.current_direction = 1
                    self.velocity.x = self.speed_x

        # Jumping and Y-Velocity
        if self.jump_cooldown != 0.0:
            self.jump_cooldown -= delta
            if self.jump_cooldown <= 0:
                self.jump_cooldown = 0.0

        if is_grounded:
            self.jump_counter = 0
            self.got_damage = False
            # jump
            if self.is_jump_unlocked and (keys[pg.K_SPACE] or keys[pg.K_w] or keys[pg.K_UP]) and not self.jump_lock:
                self.velocity.y = -self.jump_force
                self.jump_timer = PLAYER_JUMP_TIMER  # timer for extended jumps
                self.jump_cooldown = self.jump_cooldown_time
                self.wall_jump_timer = self.wall_jump_lock_time
                self.jump_lock = True
                has_jumped = True
                new_state = self.State.JUMP
            elif self.is_crouch_unlocked and (keys[pg.K_LCTRL] or keys[pg.K_s] or keys[pg.K_DOWN]):
                if self.velocity.x != 0:
                    new_state = self.State.DUCK_WALK
                else:
                    new_state = self.State.DUCK_IDLE
        else:
            # double jump
            if self.jump_counter == 1 and self.jump_cooldown == 0.0 and self.is_double_jump_unlocked and (
                        keys[pg.K_SPACE] or keys[pg.K_w] or keys[pg.K_UP]) and not self.jump_lock:
                    self.velocity.y = -self.jump_force
                    self.jump_timer = PLAYER_JUMP_TIMER
                    new_state = self.State.JUMP
                    self.jump_lock = True
                    has_jumped = True
            elif self.velocity.y < 0:
                if not (keys[pg.K_SPACE] or keys[pg.K_w] or keys[pg.K_UP]) or self.jump_timer <= 0:
                    self.velocity.y *= 0.5  # Cut the jump short (micro jump)
                else: # if player is continuously pressing jump
                    self.velocity.y += -3  # counterbalance some gravity
                    self.jump_timer -= delta # Reduce jump hold time
                new_state = self.State.JUMP
            else:
                new_state = self.State.FALL
                if not self.got_damage:
                    if self.velocity.y > 600:
                        if self.player_lives > 1:
                            print("Aua")
                            self.sound_manager.play_movement_sound("damage")
                            self.player_lives -= 1
                            self.got_damage = True
                            self.invincibility_time = 0.7
                        else:
                            self.on_player_death("fell from block")
                            self.got_damage = True

        if has_jumped:
            self.jump_counter += 1

        # Dash
        if self.is_dash_unlocked and keys[pg.K_LSHIFT] and self.dash_cooldown_timer <= 0 and self.dash_timer <= 0:
            self.has_gravity = False
            self.dash_timer = self.dash_time  # Start dash duration
            self.dash_cooldown_timer = self.dash_cooldown  # Start cooldown
            self.invincibility_time = 2 * self.dash_time
            self.velocity.x = self.current_direction * self.dash_speed  # Apply dash speed
            new_state = self.State.DASH

        # Handle Dash Duration
        if self.dash_timer > 0:
            self.dash_timer -= delta
            if self.dash_timer <= 0:  # Dash ends
                self.dash_timer = 0.0
                self.velocity.x = 0 if not (keys[pg.K_LEFT] or keys[pg.K_RIGHT]) else self.velocity.x
                new_state = self.State.RUN if (keys[pg.K_LEFT] or keys[pg.K_RIGHT]) else self.State.IDLE
                self.has_gravity = True

        # Handle Dash Cooldown Timer
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= delta
            if self.dash_cooldown_timer <= 0:
                self.dash_cooldown_timer = 0.0

        # Not crouch -> crouch
        if (self.state != self.State.DUCK_IDLE or self.state != self.State.DUCK_WALK) and (
                new_state == self.state.DUCK_IDLE or new_state == self.state.DUCK_WALK):
            self.set_hitbox("crouch")
        # Crouch -> not crouch (disallow uncrouching when that would collide with ceiling)
        if (self.state == self.State.DUCK_IDLE or self.state == self.State.DUCK_WALK) and new_state != self.state.DUCK_IDLE and new_state != self.state.DUCK_WALK:
            if not self.try_set_hitbox("default", game_world):  # If switching hitbox to default fails
                if self.velocity.x != 0:
                    new_state = self.State.DUCK_WALK
                else:
                    new_state = self.State.DUCK_IDLE

        if self.dash_timer != 0:
            new_state = self.State.DASH

        if new_state != self.state or has_jumped:
            self.on_state_changed(new_state, self.state)
            self.state = new_state

    def update(self, delta: float, game_world):

        if self.word_animation_timer > 0:
            self.word_animation_timer = max(self.word_animation_timer - delta, 0)

        if self.state == self.State.DEAD or self.state == self.State.WIN:
            self.velocity.x = 0
            if self.time_until_over != 0 and self.position.y < game_world.level_height:
                self.time_until_over -= delta
                super().update(delta, game_world)
                self.animator.update()
                if self.time_until_over <= 0:
                    self.time_until_over = 0
            else:
                if self.state == self.State.DEAD:
                    pg.event.post(pg.event.Event(PLAYER_DIED, {"reason": "hit by enemy"}))
                elif self.state == self.State.WIN:
                    pg.event.post(pg.event.Event(PLAYER_WON, {"reason": "You're just that good!"}))
        else:

            # Check invincibility frames
            if self.invincibility_time > 0:
                self.invincibility_time -= delta
                if self.invincibility_time <= 0:
                    self.invincibility_time = 0

            # get player movement
            self.handle_movement(delta, game_world)

            if self.bounce_velocity_x != 0:
                if self.check_is_grounded(game_world.static_objects) and self.invincibility_time != 0.7:
                    self.bounce_velocity_x = 0
                else:
                    self.velocity.x = self.bounce_velocity_x

            self.touching_wall_left = False
            self.touching_wall_right = False

            for obj in game_world.static_objects:
                preview_rect_right = self.get_rect().move(1, 0)
                preview_rect_left = self.get_rect().move(-1, 0)
                if preview_rect_right.colliderect(obj.get_rect()):
                    self.touching_wall_right = True
                elif preview_rect_left.colliderect(obj.get_rect()):
                    self.touching_wall_left = True

            #  Interact with interactable game elements and call their on_collide function
            self.do_interaction(game_world)

            # Check collision and apply movement or not
            super().update(delta, game_world)

            self.animator.update()
            self.light_source.set_position(self.position)  # update position of light source

    def draw(self, screen, camera_pos):
        position = self.get_rect().topleft - camera_pos
        screen.blit(self.animator.get_frame(self.current_direction), position - self.get_sprite_offset())
        #HIGHSCORE
        if self.state == self.State.WIN:
            if self.time_until_over < 4:
                self.draw_highscore(self.highscore_text, screen)
                #self.sound_manager.play_system_sound("new_highscore")
        # Draw hit box, just for debugging:
        # self.draw_debug_hitbox(screen, camera_pos)
