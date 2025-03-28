from source import *
import moderngl
from array import array


class Shader:
    def __init__(self, screen_width, screen_height):
        self.light_debug_mode = LIGHT_DEBUG_MODE
        self.screen = pg.display.set_mode((screen_width, screen_height),
                                          pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE if DEBUG_MODE else pg.SCALED | pg.OPENGL | pg.DOUBLEBUF)

        self.bg_screens: list[pg.Surface] = [pg.Surface((screen_width, screen_height), flags=pg.SRCALPHA) for _ in
                                             range(NUM_BG_LAYERS)]  # 4 Parallax BG screens
        self.fg_screen = pg.Surface((screen_width, screen_height), flags=pg.SRCALPHA)  # screen for foreground parallax
        self.game_screen = pg.Surface((screen_width, screen_height), flags=pg.SRCALPHA)
        self.game_normal_screen = pg.Surface((screen_width, screen_height), flags=pg.SRCALPHA)

        self.ui_screen = pg.Surface((screen_width, screen_height), flags=pg.SRCALPHA).convert_alpha()

        self.ctx = moderngl.create_context()

        # self.ctx.viewport = (0, 0, 320, 180)

        self.quad_buffer = self.ctx.buffer(data=array('f', [
            # position (x, y), uv coordinates (x, y)
            -1.0, 1.0, 0.0, 0.0,  # top left
            1.0, 1.0, 1.0, 0.0,  # top right
            -1.0, -1.0, 0.0, 1.0,  # bottom left
            1.0, -1.0, 1.0, 1.0,  # bottom right
        ]))

        with open(get_path("source/shaders/vert_shader.glsl"), 'r') as file:
            self.vert_shader = file.read()
        with open(get_path("source/shaders/frag_shader.glsl"), 'r') as file:
            self.frag_shader = file.read()

        self.program = self.ctx.program(vertex_shader=self.vert_shader, fragment_shader=self.frag_shader)
        self.render_object = self.ctx.vertex_array(self.program, [(self.quad_buffer, '2f 2f', 'vert', 'texcoord')])

        self.light_map: LightMap = LightMap()

        # Fun shader properties here:
        self.time: float = 0.0  # for effects varying over time
        self.moon_light_intensity: float = 1.0
        self.light_source_intensity: float = 1.0
        self.moon_position: pg.Vector2 = pg.Vector2(62, 62)

    def set_moon_light_intensity(self, intensity: float):
        self.moon_light_intensity = intensity

    def set_light_source_intensity(self, intensity: float):
        self.light_source_intensity = intensity

    def set_moon_position(self, position: pg.Vector2):
        self.moon_position = position

    def get_game_screen(self):
        return self.game_screen

    def get_ui_screen(self):
        return self.ui_screen

    def get_bg_screens(self):
        return self.bg_screens

    def get_fg_screen(self):
        return self.fg_screen

    def get_normal_screen(self):
        return self.game_normal_screen

    def update(self, camera_pos: pg.Vector2 = pg.Vector2(), light_map: LightMap = LightMap()):
        def surf_to_texture(surf):
            tex = self.ctx.texture(surf.get_size(), 4)
            tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
            tex.swizzle = 'BGRA'
            tex.write(surf.get_view('1'))
            return tex

        self.time += 0.016

        screen_number = 0

        # Create background screen uniforms
        bg_texes = []
        for screen in self.bg_screens:
            tex = surf_to_texture(screen)
            tex.use(screen_number)
            self.program[f'bg{screen_number}Tex'] = screen_number
            bg_texes.append(tex)
            screen_number += 1

        ui_tex = surf_to_texture(self.ui_screen)
        ui_tex.use(screen_number)
        self.program['uiTex'] = screen_number
        screen_number += 1

        game_tex = surf_to_texture(self.game_screen)
        game_tex.use(screen_number)
        self.program['gameTex'] = screen_number
        screen_number += 1

        fg_tex = surf_to_texture(self.fg_screen)
        fg_tex.use(screen_number)
        self.program['fgTex'] = screen_number
        screen_number += 1

        # if LIGHT_DEBUG_MODE:
        #     game_normal = surf_to_texture(self.game_normal_screen)
        #     game_normal.use(screen_number)
        #     self.program['gameNormal'] = screen_number
        #     screen_number += 1

        num_lights = NUM_LIGHTS  # Has to be the same as in frag_shader.glsl!!

        light_positions = [(pos.x, pos.y) for pos in light_map.get_positions(num_lights)]
        light_colors = [(col.r, col.g, col.b) for col in light_map.get_colors(num_lights)]
        light_intensities = [i for i in light_map.get_intensities(num_lights)]
        light_radii = [i for i in light_map.get_radii(num_lights)]
        light_flicker = [f for f in light_map.get_flickers(num_lights)]

        self.program['lightPositions'] = light_positions
        self.program['lightColors'] = light_colors
        self.program['lightIntensities'] = light_intensities
        self.program['lightRadii'] = light_radii
        self.program['lightFlicker'] = light_flicker

        self.program['lightSourceIntensity'] = self.light_source_intensity
        self.program['moonLightIntensity'] = self.moon_light_intensity
        self.program['moonPosition'] = (int(self.moon_position.x), int(self.moon_position.y))

        self.program['time'] = self.time
        self.program['cameraPos'] = (camera_pos.x, camera_pos.y)

        self.program['lightDebugMode'] = self.light_debug_mode

        self.render_object.render(mode=moderngl.TRIANGLE_STRIP)

        pg.display.flip()

        for tex in bg_texes:
            tex.release()
        ui_tex.release()
        game_tex.release()
        fg_tex.release()

        # if LIGHT_DEBUG_MODE:
        #     game_normal.release()

class FakeShader():
    def __init__(self, screen_width, screen_height):
        self.screen = pg.display.set_mode((screen_width, screen_height), pg.DOUBLEBUF | pg.RESIZABLE if DEBUG_MODE else pg.SCALED | pg.DOUBLEBUF)

        self.light_map = None

    def set_moon_light_intensity(self, intensity: float):
        pass

    def set_light_source_intensity(self, intensity: float):
        pass

    def set_moon_position(self, moon_pos):
        pass

    def get_game_screen(self):
        return self.screen

    def get_ui_screen(self):
        return self.screen

    def get_bg_screens(self):
        return [self.screen for _ in range(NUM_BG_LAYERS)]

    def get_fg_screen(self):
        return self.screen

    def get_normal_screen(self):
        return self.screen

    def update(self, camera_pos: pg.Vector2 = pg.Vector2(), light_map: LightMap = LightMap()):
        pg.display.flip()


warnings.filterwarnings("ignore", category=FutureWarning, message=".*SCALED|OPENGL.*")
