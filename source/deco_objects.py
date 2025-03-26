from source import pg, get_path, AnimatedObject, Animation, LightSource, SoundManager


class Candle(AnimatedObject):
    def __init__(self, position):
        animation = Animation(
            "idle",
            get_path('assets/sprites/anim/deco/candle1.png'),
            16,
            32,
            4,
            10
        )
        light_source = LightSource(
            position.copy(),
            pg.Vector2(9, 17),
            pg.Color((240, 120, 30)),
            40.0,
            0.1,
            flicker=True
        )
        super().__init__(position, animation, light_source=light_source)


class Hourglass(AnimatedObject):
    def __init__(self, position):
        animation = Animation(
            "idle",
            get_path('assets/sprites/anim/deco/hourglass1.png'),
            16,
            32,
            4,
            10
        )
        super().__init__(position, animation)

class Egg(AnimatedObject):
    def __init__(self, position):
        egg_framerate = 10
        animation: Animation = Animation("egg", get_path("assets/sprites/anim/egg-animation-Sheet.png"),
                                         40,
                                         44,
                                         60,
                                         egg_framerate,
                                         True)
        light_source = LightSource(
            position.copy(),
            pg.Vector2(20, 10),
            pg.Color((160, 220, 200)),
            40.0,
            0.05,
        )
        self.egg_anim_timer: float = 60 / 8.0  # Time animation takes (frames / frame rate)
        self.fade: float = 1.0
        self.fade_time: float = 2.0  # time to fade after animation ends
        self.is_animation_over = False

        self.sound_manager = SoundManager()

        super().__init__(position, animation, light_source=light_source)

    def draw(self, screen, camera_pos):
        self.animator.update()
        position = self.position - camera_pos

        match self.animator.get_frame_number():
            case 38:
                self.sound_manager.play_system_sound("squish")
            case 53:
                self.sound_manager.play_system_sound("squish")

        if self.animator.is_last_frame():
            self.fade = max(self.fade - 0.016 * self.fade_time, 0.0)

        sprite = self.animator.get_frame(1)
        sprite.set_alpha(255 * self.fade)
        screen.blit(sprite, position)

        if self.fade == 0.0:
            self.is_animation_over = True