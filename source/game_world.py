import math

from source import *


class GameWorld:
    def __init__(self, objects: list, collision_objects: list, interactable_objects: list, player_pos: pg.Vector2,
                 level_size: tuple[int, int], level_name: str, egg_pos=None) -> None:

        self.objects = objects
        self.static_objects = collision_objects
        self.interactable_objects = interactable_objects

        self.player = Player(player_pos)
        self.egg = Egg(egg_pos) if egg_pos else None
        self.level_timer: float = 0.0

        self.camera_pos: pg.Vector2 = pg.Vector2(self.player.get_rect().x - SCREEN_WIDTH // 2,
                                                 self.player.get_rect().y - SCREEN_HEIGHT // 2)
        self.level_width, self.level_height = level_size
        self.play_start_position = player_pos
        # self.start_interactable_objects = interactable_objects.copy()  # Used to reset the game

        self.is_moonlight_on = level_name != "HEX_1.csv"
        self.moon_light_intensity: float = 0.0
        self.is_light_sources_on = True
        self.light_source_intensity: float = 1.0  # Light intensity of all light sources in the game
        self.time: float = 0.0

        self.word_animation_timer = 0.0

        self.timer_anim: Animation = Animation("timer", get_path('assets/sprites/ui/ui_timer_anim.png'), 58, 16, 4, 8)
        self.timer_animator: Animator = Animator(self.timer_anim)

        self.level_name: str = level_name
        self.highscores = load_file(get_path("saves/levels.sav"))

        self.sound_manager: SoundManager = SoundManager()

        # Initialise Light Map
        self.light_map = LightMap()
        self.light_map.add_source(self.player.light_source)
        for o in self.get_all_objects():
            # get light source
            light_source = o.get_light_source()
            if light_source:
                self.light_map.add_source(light_source)


        # Initialise Parallax bgs
        self.BG_LAYERS = [
            {"image": pg.image.load(get_path('assets/sprites/parallax/parallax_bg_sky.png')), "offset_y": -0,
             "depth": 20},
            {"image": pg.image.load(get_path('assets/sprites/parallax/parallax_bg_3.png')), "offset_y": -100,
             "depth": 16},
            {"image": pg.image.load(get_path('assets/sprites/parallax/parallax_bg_2.png')), "offset_y": -100,
             "depth": 12},
            {"image": pg.image.load(get_path('assets/sprites/parallax/parallax_bg_1.png')), "offset_y": -100,
             "depth": 5},
        ]

        self.FG_LAYERS = [
            {"image": pg.image.load(get_path('assets/sprites/parallax/parallax_bg_-1.png')), "offset_y": 100,
             "depth": -5}
        ]

        self.SPRITES = {
            "ui_bg": pg.image.load(get_path("assets/sprites/ui/ui_bg.png")),
            "ui_heart": pg.image.load(get_path("assets/sprites/ui/ui_heart.png")),
            "ui_key": pg.image.load(get_path("assets/test/key.png")),
            "ui_question_mark": pg.image.load(get_path("assets/sprites/ui/ui_question_mark.png")),
            "ui_backspace": pg.image.load(get_path("assets/sprites/ui/ui_backspace.png")).convert_alpha()
        }

    def get_all_objects(self):
        return self.static_objects + self.objects + self.interactable_objects

    def set_player_position(self, pos: pg.Vector2) -> None:
        """Sets player position, used when initialising level"""
        self.player.get_rect().x = pos.x
        self.player.get_rect().y = pos.y

    def get_light_map(self) -> LightMap:
        if self.egg:
            light_map = LightMap()
            light_map.add_source(self.egg.light_source)
            return light_map
        else:
            return self.light_map

    def on_player_collected_light(self):
        self.is_moonlight_on = True

    def do_updates(self, delta: float) -> None:

        if delta > 0.025:
            delta = 0.016

        self.level_timer += delta
        if self.player.picked_up_time:
            self.level_timer = max(self.level_timer - TIME_ITEM_VALUE, 0.0)
            self.player.picked_up_time = False

        # check if the player has fallen out of bounds
        if self.player.position.y > self.level_height:
            self.player.on_fell_out_of_bounds()

        self.player.update(delta, self)
        self.light_map.get_first_source().set_position(self.player.position)

        for o in self.interactable_objects:
            if o.position.distance_to(self.player.position) < 400:
                o.update(delta, self)

        for o in self.static_objects:
            if o.position.distance_to(self.player.position) < 400:
                if isinstance(o, MovingPlatform) or isinstance(o, Door):
                    o.update(delta, self)

        if self.is_moonlight_on and self.moon_light_intensity < 1.0:
            self.moon_light_intensity += 0.3 * delta

        if self.is_light_sources_on and self.light_source_intensity < 1.0:
            self.light_source_intensity += 0.1 * delta

        self.timer_animator.update()
        self.time += delta

    def do_render(self, shader):
        def set_camera_position() -> None:
            """Sets self.camera_pos to the correct position for this frame"""

            def smooth_movement(current_pos: float, target_pos: float, delay: float) -> float:
                # Berechne nur dann, wenn sich die Position signifikant verändert hat
                if abs(target_pos - current_pos) > 1:
                    return current_pos + (target_pos - current_pos) * (delay / 100)
                return current_pos

            # Zielposition der Kamera
            target_pos: pg.Vector2 = pg.Vector2(
                self.player.get_rect().x - SCREEN_WIDTH // 2,
                self.player.get_rect().y - SCREEN_HEIGHT // 2
            )

            self.camera_pos.x = smooth_movement(self.camera_pos.x, target_pos.x, CAMERA_DELAY_X)
            if abs(target_pos.y - self.camera_pos.y) > DEAD_ZONE_Y:
                self.camera_pos.y = smooth_movement(self.camera_pos.y, target_pos.y, CAMERA_DELAY_Y)
            self.camera_pos.x = max(0, min(self.camera_pos.x, self.level_width - SCREEN_WIDTH))
            self.camera_pos.y = max(0, min(self.camera_pos.y, self.level_height - SCREEN_HEIGHT))

        ui_screen = shader.get_ui_screen()
        game_screen = shader.get_game_screen()
        normal_screen = shader.get_normal_screen()

        bg_screens = shader.get_bg_screens()
        fg_screen = shader.get_fg_screen()

        for screen in bg_screens:
            screen.fill((0, 0, 0, 0))
        fg_screen.fill((0, 0, 0, 0))
        normal_screen.fill((0, 0, 0, 0))
        game_screen.fill((0, 0, 0, 0))
        ui_screen.fill((0, 0, 0, 0))

        set_camera_position()

        self.render_game(shader, ui_screen, game_screen, normal_screen, bg_screens, fg_screen)

    def render_game(self, shader, ui_screen, game_screen, normal_screen, bg_screens, fg_screen):
        sprites = self.SPRITES
        BG_LAYERS = self.BG_LAYERS
        FG_LAYERS = self.FG_LAYERS

        def draw_ui():
            def draw_timer():
                time = self.level_timer
                settings = sound_manager.load_file(SETTINGS)
                current_highscore = self.highscores.get(self.level_name)
                ui_timer = self.timer_animator.get_frame()
                minutes = int(time // 60)  # Ganze Minuten
                seconds = int(time % 60)  # Sekunden als Dezimalanteil korrigiert
                current_time = minutes + round(seconds / 100, 2)
                current_highscore = 99.99 if self.highscores[self.level_name] == "None" else current_highscore
                ui_time_text = FONT_8.render(f"{minutes:02}:{seconds:02}", True,
                                              "#F2A81D" if current_time > float(current_highscore) else "#36733F")
                if settings["TIMER"] == "True":
                    ui_screen.blit(ui_timer, pg.Vector2(131, 0))
                    ui_screen.blit(ui_time_text, pg.Vector2(151, 4))

            ui_screen.blit(sprites["ui_bg"], pg.Vector2(0, 0))
            draw_timer()

            for i in range(self.player.player_lives):
                ui_screen.blit(sprites["ui_heart"], UI_HEART_POSITIONS[i])

            lerp_value = 0
            if self.player.word_animation_timer > 0:
                letters = self.player.last_word_completed
                min_offset = pg.Vector2()
                max_offset = pg.Vector2(120, -50)
                lerp_value: float = 1 - self.player.word_animation_timer
                offset = min_offset.lerp(max_offset, lerp_value)
            else:
                letters = self.player.letters_collected
                offset = pg.Vector2()

            for i in range(len(letters)):
                if i > 5:  # Break if more than 5 letters would have to be displayed
                    break
                letter = letters[i]
                ui_screen.blit(LETTER_IMAGES[letter], UI_LETTER_POSITIONS[i] - offset)

            if self.player.has_key:
                ui_screen.blit(sprites["ui_key"], UI_KEY_POSITION)

            if self.player.check_is_wrong_word():
                time = (math.sin(self.time * 3) + 1)
                sprites["ui_backspace"].set_alpha(int(time * 255))
                ui_screen.blit(sprites["ui_question_mark"], pg.Vector2(241, 2))
                ui_screen.blit(sprites["ui_backspace"], pg.Vector2(261, 20))

        def draw_parallax_layer(layer, max_depth, y_parallax=True, screen=game_screen):
            depth: int = layer["depth"]
            parallax_factor: float = 1 - (depth / max_depth)  # Dynamische Berechnung des Parallax-Faktors
            y_parallax_factor: float = 0.1  # Größer -> stärkeres Y-parallax, niedriger -> schwächeres Y-parallax

            # Berechnung der versetzten Hintergrundposition (x und y)
            offset_y: int = layer["offset_y"]
            x_pos = (-self.camera_pos.x + (self.play_start_position.x - SCREEN_WIDTH // 2)) * parallax_factor
            y_pos = offset_y - self.camera_pos.y * parallax_factor * y_parallax_factor if y_parallax else offset_y - self.camera_pos.y
            bg_pos: pg.Vector2 = pg.Vector2(x_pos, y_pos)
            bg_width = layer["image"].get_width()
            mod_x = bg_pos.x % bg_width

            # Hintergrund zeichnen
            screen.blit(layer["image"], pg.Vector2(mod_x, bg_pos.y))
            screen.blit(layer["image"], pg.Vector2(mod_x - bg_width, bg_pos.y))

        def draw_bg_parallax():
            """Draws the background parallax layers"""

            max_depth: int = max(layer["depth"] for layer in BG_LAYERS)  # Maximale Tiefe bestimmen
            for i in range(len(BG_LAYERS)):
                if BG_LAYERS[i]["depth"] > 0:
                    draw_parallax_layer(BG_LAYERS[i], max_depth, True, bg_screens[i])

        def draw_fg_parallax():
            """Draws the foreground parallax layers"""

            max_depth: int = max(layer["depth"] for layer in BG_LAYERS)  # Maximale Tiefe bestimmen
            for layer in FG_LAYERS:
                if layer["depth"] <= 0:
                    draw_parallax_layer(layer, max_depth, False, screen=fg_screen)

        def draw_normals(screen):
            for o in self.get_all_objects():
                o.draw_normal(screen, camera_pos=self.camera_pos)

        # draw background parallax
        draw_bg_parallax()

        # dynamic light sources (comment out for static lighting)
        self.light_map.clear_sources()
        self.light_map.add_source(self.player.light_source)

        # draw objects
        for o in self.objects + self.static_objects + self.interactable_objects:  # Static -> Deco -> Interactive
            if self.camera_pos.x - 16 < o.position.x < self.camera_pos.x + SCREEN_WIDTH + 32:  # Only draw if within camera bounds + 64px
                if self.camera_pos.y - 16 < o.position.y < self.camera_pos.y + SCREEN_HEIGHT + 32:
                    pos = self.camera_pos.copy()
                    if o.do_wave_animation:
                        pos += pg.Vector2(0, math.sin(self.time * 2.5))
                    o.draw(game_screen, pos)
                    if o.get_light_source():
                        self.light_map.add_source(o.get_light_source())



        # Draw egg and return if egg animation is running
        if self.egg:
            if self.egg.is_animation_over:
                self.egg = None
                self.level_timer = 0.0
                self.is_light_sources_on = True
                self.player.set_animation(self.player.idle)
            else:
                self.player.set_animation(self.player.still)
                self.player.draw(game_screen, self.camera_pos)
                self.egg.draw(game_screen, self.camera_pos)
                shader.set_moon_light_intensity(0.0)
                shader.set_light_source_intensity(0.0)
                return

        self.player.draw(game_screen, self.camera_pos)


        shader.set_moon_light_intensity(self.moon_light_intensity)
        shader.set_light_source_intensity(self.light_source_intensity)


        # draw foreground parallax
        draw_fg_parallax()

        # Normal map
        draw_normals(normal_screen)

        # Visual effects
        # draw_post_processing()

        # draw UI
        draw_ui()
