from source import *


class GameObject:
    def __init__(self, position: pg.Vector2, image: pg.Surface, normal: pg.Surface = None, light_source: LightSource = None):
        self.image = image.convert_alpha()  # Sprite image
        self.normal: pg. Surface = normal if normal else None
        self.position = position.copy()

        # Cosmetic stuff
        self.light_source = light_source  # Leave None if no light source
        self.do_wave_animation = False

    def update(self, delta: float, game_world):
        pass

    def draw(self, screen, camera_pos):
        """Draw object on screen."""
        position = self.position - camera_pos
        screen.blit(self.image, position)

    def draw_normal(self, screen, camera_pos):
        """Draw normal of object on screen."""
        if self.normal:
            position = self.position - camera_pos
            screen.blit(self.normal, position)

    def get_light_source(self):
        return self.light_source

    def get_normal(self) -> pg.Surface:
        return self.normal


class AnimatedObject(GameObject):
    """Base class for objects that are animated. No colliders or hit boxes. Used for decorative objects."""

    def __init__(self, position: pg.Vector2, animation: Animation, light_source: LightSource = None):
        self.animation: Animation = animation
        self.animator: Animator = Animator(animation)
        super().__init__(position, self.animator.get_frame(1), light_source=light_source)

    def draw(self, screen, camera_pos):
        self.animator.update()
        position = self.position - camera_pos
        screen.blit(self.animator.get_frame(1), position)


class ColliderObject(GameObject):
    """Base class for all object with a collider"""

    def __init__(self, position: pg.Vector2, image: pg.Surface, hitbox_image: pg.Surface = None, normal_image: pg.Surface = None, light_source=None):
        super().__init__(position, image, normal=normal_image, light_source=light_source)

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
            if col_obj.position.distance_to(self.position) < 70:
                if rect.colliderect(col_obj.get_rect()):  # Check collision
                    if self != col_obj:
                        return col_obj
        return None

    def draw_debug_hitbox(self, screen, camera_pos):
        # Draw hit box, just for debugging:
        if DEBUG_HITBOXES:
            rect = self.get_rect().move(-camera_pos)
            pg.draw.rect(screen, (255, 0, 0), rect, 2)

    def draw(self, screen, camera_pos):
        """Draw object on screen."""
        sprite_offset = self.get_sprite_offset()
        position = self.position - camera_pos
        screen.blit(self.image, position - sprite_offset)

        self.draw_debug_hitbox(screen, camera_pos)


class InteractableObject(ColliderObject):
    """Base class for all objects that define special behaviour when colliding with player"""

    def on_collide(self, player, game_world) -> None:
        pass


class MovingObject(InteractableObject):
    """Base class for all moving objects with physical collision handling"""

    def __init__(self, position: pg.Vector2, image: pg.Surface, has_gravity: bool,
                 hitbox_image: pg.Surface = None, light_source=None):
        super().__init__(position, image, hitbox_image, light_source=light_source)
        self.max_y_velocity = 800.0
        self.gravity = 20.0
        self.speed_x = 75.0
        self.speed_y = 0.0
        self.velocity = pg.Vector2(0.0, 0.0)
        self.has_gravity = has_gravity
        self.has_collided = False

    def set_animation(self, animation) -> None:
        pass

    def does_collide(self, rect, objects: list) -> GameObject:
        """Check if hit box collides with another object."""
        for o in objects:
            if o.position.distance_to(self.position) < 70:
                if rect.colliderect(o.get_rect()):
                    return o
        return None

    def check_is_grounded(self, objects: list) -> GameObject:
        """Check if element is on the floor."""
        preview_rect = self.get_rect().move(0, 1)
        obj_below = self.does_collide(preview_rect, objects)
        if obj_below:
            return obj_below
        else:
            return None

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
            if self.position.x < colliding_object.position.x:  # Moving right
                rect.right = colliding_object.get_rect().left
            elif self.position.x > colliding_object.position.x:  # Moving left
                rect.left = colliding_object.get_rect().right
            self.position.x, _ = rect.topleft  # Reset precise position

        # move y and check collisions
        if self.position.y > 2000:  # that's way too far away bruh
            print("You too far down dawg (object_classes.py:MovingObject)")  # to prevent endless falling
            return
        self.position.y += dy
        rect.topleft = self.position

        colliding_object = self.check_collision(rect, game_world.static_objects)
        if colliding_object:
            if self.position.y < colliding_object.position.y:  # Falling down
                rect.bottom = colliding_object.get_rect().top
                self.velocity.y = 0
                # self.on_ground = True
            elif self.position.y > colliding_object.position.y:  # Hitting the ceiling
                rect.top = colliding_object.get_rect().bottom
                self.velocity.y = 0
            _, self.position.y = rect.topleft  # Reset precise position


class LetterPickUp(InteractableObject):
    def __init__(self, position: pg.Vector2, letter: str):
        self.letter = letter
        image = LETTER_IMAGES[letter]
        offset = pg.Vector2(0, -1)
        light_source = LightSource(
            position.copy(),
            pg.Vector2(4, 4) + offset,
            COLOR_GOLD,
            10.0,
            0.05
        )
        super().__init__(position.copy() + offset, image, light_source=light_source)
        self.do_wave_animation = True

    def on_collide(self, player, game_world) -> None:
        if player.on_pickup_letter(self.letter, game_world):  # If player picks up (doesn't pick up if inventory full)
            game_world.interactable_objects.remove(self)

class HeartPickUp(InteractableObject):
    def __init__(self, position: pg.Vector2):
        image = pg.image.load(get_path("assets/sprites/ui/ui_heart.png"))
        offset = pg.Vector2(1, 0)
        light_source = LightSource(
            position.copy(),
            pg.Vector2(6, 5) + offset,
            COLOR_GOLD,
            10.0,
            0.05
        )
        super().__init__(position.copy() + offset, image, light_source=light_source)
        self.do_wave_animation = True

    def on_collide(self, player, game_world) -> None:
        if player.on_pickup_heart():  # If player picks up (doesn't pick up if inventory full)
            game_world.interactable_objects.remove(self)

class TimePickUp(InteractableObject):
    def __init__(self, position: pg.Vector2):
        image = pg.image.load(get_path("assets/sprites/hourglass.png"))
        offset = pg.Vector2(2, 0)
        light_source = LightSource(
            position.copy(),
            pg.Vector2(6, 6) + offset,
            COLOR_GOLD,
            10.0,
            0.05
        )
        super().__init__(position.copy() + offset, image, light_source=light_source)
        self.do_wave_animation = True

    def on_collide(self, player, game_world) -> None:
        if player.on_pickup_time():  # If player picks up (doesn't pick up if inventory full)
            game_world.interactable_objects.remove(self)


class Door(ColliderObject):

    class State(Enum):
        LOCKED = 1
        UNLOCKED = 2

    def __init__(self, position: pg.Vector2):
        self.unlocking = Animation("unlocking", get_path('assets/test/door-unlocking-Sheet.png'), 16, 32, 17, 6)
        self.animator = Animator(self.unlocking)
        self.current_direction = 1
        self.state = self.State.LOCKED
        self.time_until_open = 2.5

        hitbox_image = pg.image.load(get_path('assets/sprites/dino/test_hitbox.png')).convert()

        image = pg.image.load(get_path('assets/sprites/tiles/door.png')).convert()
        hitbox_image = pg.image.load(get_path('assets/sprites/tiles/door_collider.png')).convert()
        super().__init__(position, image, hitbox_image=hitbox_image)

    def unlock(self, game_world):
        """Remove the door's hit box when unlocked."""
        self.state = self.State.UNLOCKED

    def update(self, delta, game_world):
        if self.state == self.State.UNLOCKED:
            self.animator.update()
            if self.time_until_open != 0:
                self.time_until_open -= delta
                if self.time_until_open <= 0:
                    self.time_until_open = 0
            else:
                game_world.static_objects.remove(self)

    def draw(self, screen, camera_pos):
        if self.state == self.State.UNLOCKED:
            position = self.get_rect().topleft - camera_pos
            screen.blit(self.animator.get_frame(self.current_direction), position - self.get_sprite_offset())
        else:
            super().draw(screen, camera_pos)


class Keyhole(InteractableObject):
    def __init__(self, position: pg.Vector2):
        super().__init__(position, pg.image.load(get_path('assets/sprites/tiles/keyhole.png')))

    def on_collide(self, player, game_world) -> None:
        if player.has_key:
            print("Door unlocked!")
            player.has_key = False
            pg.event.post(pg.event.Event(DOOR_UNLOCKED))
        else:
            print("The door is locked. You need a key.")


class KeyPickUp(MovingObject):

    def __init__(self, position):
        image = pg.image.load(get_path('assets/test/key.png'))
        light_source = LightSource(
            position.copy(),
            pg.Vector2(4, 4),
            COLOR_GOLD,
            10.0,
            0.02
        )
        super().__init__(position.copy(), image, True, light_source=light_source)

    def on_collide(self, player, game_world) -> None:
        player.on_pickup_key()
        game_world.interactable_objects.remove(self)


class MovingPlatform(MovingObject):
    def __init__(self, position: pg.Vector2, has_max_distance: bool = True):
        super().__init__(position, pg.image.load(get_path('assets/sprites/tiles/platform.png')), False, pg.image.load(get_path("assets/sprites/tiles/platform_collider.png")))
        self.speed_x = 20
        self.distance = 0
        self.has_max_distance = has_max_distance
        if self.has_max_distance:
            self.max_distance = 90
        else:
            self.max_distance = 100000
        self.current_direction = 1

    def update(self, delta: float, game_world):
        self.velocity.x = self.current_direction * self.speed_x

        super().update(delta, game_world)

        if not self.has_collided:
            self.distance += abs(self.velocity.x * delta)

        if self.distance >= self.max_distance or self.has_collided:
            self.current_direction *= (-1)
            self.distance = 0
            self.has_collided = False


class Enemy(MovingObject):

    def __init__(self, position: pg.Vector2, image: pg.Surface, gravity: bool, hitbox_image = None):
        super().__init__(position, image, gravity, hitbox_image=hitbox_image)
        self.current_direction = 1
        self.time_until_death = 3.5
        self.sound_manager = SoundManager()

        self.is_playing_sound = False
        self.audio_channel = None

    class State(Enum):
        ALIVE = 1
        DEAD = 2

    def on_collide(self, player, game_world) -> None:
        """Is called on collision with player."""
        # threshold = 5
        if self.state != self.State.DEAD:
            if player.velocity.y > 0 and not player.check_is_grounded(game_world.static_objects):
                    #and player.get_rect().bottom <= self.get_rect().top + 10)
                # If player jumps on top of it, enemy dies
                player.velocity.y = -250
                player.bounce_velocity_x = 0
                player.velocity.x = 0
                self.state = self.State.DEAD
                self.on_state_changed(self.State.DEAD)
            else:
                player.on_hit_by_enemy(self, player.current_direction)

    def on_state_changed(self, state: Enum):
        pass

    def set_animation(self, animation):
        if self.active_animation.name != animation.name:
            self.active_animation = animation
            self.animator = Animator(animation)
            self.animator.reset_animation()

    def draw(self, screen, camera_pos):
        position = self.get_rect().topleft - camera_pos

        frame = self.animator.get_frame(self.current_direction)
        if self.state == self.State.DEAD and self.time_until_death <= 2:
            frame.set_alpha(255 - (2 - self.time_until_death) * 255)

        screen.blit(frame, position)

        # debug mode hitbox
        self.draw_debug_hitbox(screen, position)


class Worm(Enemy):

    def __init__(self, position: pg.Vector2):
        super().__init__(position, pg.image.load(get_path("assets/test/worm.png")), True)
        self.speed_x = 10
        self.distance = 0
        self.max_distance = 50
        self.state = self.State.ALIVE

        self.walk = Animation("walk", get_path('assets/sprites/anim/worm-walk-Sheet.png'), 32, 16, 6, 10)
        self.dead = Animation("dead", get_path('assets/sprites/anim/worm-dead-Sheet.png'), 32, 16, 1, 10)

        self.active_animation = self.walk
        self.animator = Animator(self.active_animation)
        self.audio_channel = None

    def on_state_changed(self, state: Enum):
        """Called when the player state (RUN, IDLE, JUMP, etc.) changes"""

        # Change animation:
        match state:
            case self.State.ALIVE:
                self.set_animation(self.walk)
            case self.State.DEAD:
                self.set_animation(self.dead)


    def update(self, delta: float, game_world):

        if self.state == self.State.DEAD:
            # switch off sounds
            if self.is_playing_sound:
                self.sound_manager.play_enemy_sound("idle")
                self.sound_manager.play_system_sound("squish")
                self.is_playing_sound = False
                self.audio_channel =  None

            if self.time_until_death != 0:
                self.time_until_death -= delta
                if self.time_until_death <= 0:
                    self.time_until_death = 0
            else:
                game_world.interactable_objects.remove(self)

        else:
            self.velocity.x = self.current_direction * self.speed_x

            #region Do sound stuff
            player_pos = game_world.player.position
            if self.position.distance_to(player_pos) < 150 and not self.is_playing_sound:
                self.audio_channel = self.sound_manager.play_enemy_sound("bug_scuttle")
                self.is_playing_sound = True
            elif self.position.distance_to(player_pos) > 150 and self.is_playing_sound:
                self.sound_manager.play_enemy_sound("idle")
                self.is_playing_sound = False
                self.audio_channel = None
            if self.audio_channel:
                panning: float = (self.position.x - player_pos.x) / self.position.distance_to(player_pos)
                left_volume: float = 1.0 - (panning + 1.0) / 2.0
                right_volume: float = (panning + 1.0) / 2.0
                self.audio_channel.set_volume(left_volume, right_volume)
            #endregion sound stuff

            super().update(delta, game_world)

            if not self.has_collided:
                self.distance += abs(self.velocity.x * delta)

            if self.distance >= self.max_distance or self.has_collided:
                self.current_direction *= (-1)
                self.distance = 0
                self.has_collided = False

            self.animator.update()


class FlyingBook(Enemy):

    def __init__(self, position: pg.Vector2):
        hitbox_image = pg.image.load(get_path("assets/sprites/anim/flying_book_hitbox.png"))

        super().__init__(position, hitbox_image, False, hitbox_image=hitbox_image)
        self.speed_y = 20
        self.distance = 0
        self.max_distance = 100
        self.state = self.State.ALIVE

        self.fly = Animation("fly", get_path('assets/sprites/anim/flying_book-fly-Sheet.png'), 43, 23, 10, 10)
        self.dead = Animation("dead", get_path('assets/sprites/anim/flying_book-dead-Sheet.png'), 43, 23, 1)

        self.active_animation = self.fly
        self.animator = Animator(self.active_animation)
        self.audio_channel = None

    def on_state_changed(self, state: Enum):
        """Called when the player state (RUN, IDLE, JUMP, etc.) changes"""

        # Change animation:
        match state:
            case self.State.ALIVE:
                self.set_animation(self.fly)
            case self.State.DEAD:
                self.set_animation(self.dead)

    def update(self, delta: float, game_world):

        if self.state == self.State.DEAD:

            # switch off sounds
            if self.is_playing_sound:
                self.sound_manager.play_enemy_sound("idle")
                self.sound_manager.play_system_sound("squish")
                self.is_playing_sound = False
                self.audio_channel = None

            self.has_gravity = True
            super().update(delta, game_world)
            self.animator.update()
            if self.time_until_death != 0:
                self.time_until_death -= delta
                if self.time_until_death <= 0:
                    self.time_until_death = 0
            else:
                game_world.interactable_objects.remove(self)

        else:
            self.velocity.y = self.current_direction * self.speed_y

            # region Do sound stuff
            player_pos = game_world.player.position
            distance = self.position.distance_to(player_pos)
            max_distance = 200  # Distance at which volume starts to fade
            if distance < max_distance and not self.is_playing_sound:
                self.audio_channel = self.sound_manager.play_enemy_sound("paper_flutter")
                self.is_playing_sound = True
            elif distance > max_distance and self.is_playing_sound:
                self.sound_manager.play_enemy_sound("idle")
                self.is_playing_sound = False
                self.audio_channel = None
            if self.audio_channel:
                # Normalize distance (closer = louder)
                volume_factor = max(0.7, 1.0 - (distance / max_distance))  # Min 50% volume at max_distance
                # Calculate stereo panning (-1 left, 1 right)
                panning = (self.position.x - player_pos.x) / max(distance, 1)  # Avoid division by zero
                left_volume = volume_factor * (1.0 - (panning + 1.0) / 2.0)
                right_volume = volume_factor * ((panning + 1.0) / 2.0)
                self.audio_channel.set_volume(left_volume, right_volume)  # Apply volume
            # endregion sound stuff

            super().update(delta, game_world)

            if not self.has_collided:
                self.distance += abs(self.velocity.y * delta)

            if self.distance >= self.max_distance or self.has_collided:
                self.current_direction *= (-1)
                self.distance = 0
                self.has_collided = False

            self.animator.update()


class Monkey(Enemy):
    def __init__(self, position: pg.Vector2):
        super().__init__(position,pg.image.load(get_path("assets/test/monkey_test.png")), True)
        self.speed_x = 0
        self.distance = 0
        self.max_distance = 0
