from source import *

class TitleScreen:

    def __init__(self):

        self.light_map = LightMap()
        self.time: float = 0.0
        self.moon_light_intensity: float = 1.0
        self.is_moonlight_on: bool = True
        self.moon_position: pg.Vector2 = pg.Vector2(64, 40)

        self.dino_anim = Animation("tower", get_path('assets/sprites/menu/title_dino_anim.png'), 11, 17, 9, 5)
        self.dino_anim_pos = pg.Vector2(154, 147)
        self.text_anim = Animation("tower", get_path('assets/sprites/menu/title_text_anim.png'), 320, 160, 9, 5)

        self.dino_animator: Animator = Animator(self.dino_anim)
        self.text_animator: Animator = Animator(self.text_anim)

    def do_updates(self, delta: float) -> None:

        if self.is_moonlight_on and self.moon_light_intensity < 1.0:
            self.moon_light_intensity += 0.3 * delta

        self.dino_animator.update()
        self.text_animator.update()

        self.time += delta

    def do_render(self, shader):

        ui_screen = shader.get_ui_screen()
        game_screen = shader.get_game_screen()
        # normal_screen = shader.game_normal_screen

        bg_screens = shader.get_bg_screens()

        for screen in bg_screens:
            screen.fill((0, 0, 0, 0))

        game_screen.fill((0, 0, 0, 0))
        ui_screen.fill((0, 0, 0, 0))


        title_sky = pg.image.load(get_path('assets/sprites/menu/title_sky_bg.png'))
        title_dino = self.dino_animator.get_frame()
        title_text = self.text_animator.get_frame()

        bg_screens[0].blit(title_sky, pg.Vector2())
        bg_screens[1].blit(title_dino, self.dino_anim_pos)
        bg_screens[2].blit(title_text, pg.Vector2())

        # get light sources:
        self.light_map.clear_sources()
        self.light_map.add_source(LightSource(
            position=self.moon_position,
            offset=pg.Vector2(),
            radius=80.0,
            intensity=0.03,
            color=pg.Color(120, 220, 250)
        ))

        shader.set_moon_position(self.moon_position)
        shader.set_moon_light_intensity(self.moon_light_intensity)

