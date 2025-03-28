from source import *
class TitleScreen:

    def __init__(self, state):

        self.light_map = LightMap()
        self.state = state
        self.time: float = 0.0
        self.moon_light_intensity: float = 1.0
        self.is_moonlight_on: bool = True
        self.moon_position: pg.Vector2 = pg.Vector2(64, 40)
        if self.state == "START":
            self.dino_anim = Animation("tower", get_path('assets/sprites/menu/babel_start_spritesheet.png'), 320, 180, 2, 1)
        else:
            self.dino_anim = Animation("tower", get_path('assets/sprites/anim/monkey-Sheet.png'), 32, 48,
                                       9, 4)
        self.dino_anim_pos = pg.Vector2((SCREEN_WIDTH - 32) // 2, (SCREEN_HEIGHT - 32) // 2)

        self.dino_animator: Animator = Animator(self.dino_anim)

    def do_updates(self, delta: float) -> None:

        if self.is_moonlight_on and self.moon_light_intensity < 1.0:
            self.moon_light_intensity += 0.3 * delta

        self.dino_animator.update()

        self.time += delta

    def do_render(self, shader):

        ui_screen = shader.get_ui_screen()
        game_screen = shader.get_game_screen()
        # normal_screen = shader.game_normal_screen

        bg_screens = shader.get_bg_screens()

        for screen in bg_screens:
            screen.fill((20, 20, 20, 20))

        game_screen.fill((20, 20, 20, 20))
        ui_screen.fill((20, 20, 20, 20))


        title_dino = self.dino_animator.get_frame()

        if self.state == "START":
            bg_screens[0].blit(title_dino, pg.Vector2())
        else:
            bg_screens[0].blit(title_dino, self.dino_anim_pos)

        # get light sources:
        self.light_map.clear_sources()
        self.light_map.add_source(LightSource(
            position=self.moon_position,
            offset=pg.Vector2(),
            radius=80.0,
            intensity=0.03,
            color=pg.Color(0, 0, 0)
        ))

        shader.set_moon_position(self.moon_position)
        shader.set_moon_light_intensity(self.moon_light_intensity)

