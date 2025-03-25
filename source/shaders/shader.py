import pygame as pg
import moderngl
from array import array
from source.utils import *
from source.constants import *
from source.light_source import *


class Shader:
    def __init__(self, screen_width, screen_height, ):
        self.screen = pg.display.set_mode((screen_width, screen_height), pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)

        self.bg_screens: list[pg.Surface] = [pg.Surface((screen_width, screen_height), flags=pg.SRCALPHA) for _ in
                                             BG_LAYERS]

        self.game_screen = pg.Surface((screen_width, screen_height), flags=pg.SRCALPHA)
        self.game_normal_screen = pg.Surface((screen_width, screen_height), flags=pg.SRCALPHA)

        self.ui_screen = pg.Surface((screen_width, screen_height), flags=pg.SRCALPHA)

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

        # Fun shader properties here:
        self.moon_light_intensity: float = 0.0

    def set_moon_light_intensity(self, intensity: float):
        self.moon_light_intensity = intensity

    def get_game_screen(self):
        return self.game_screen

    def get_ui_screen(self):
        return self.ui_screen

    def update(self, camera_pos: pg.Vector2 = pg.Vector2(), light_map: LightMap = LightMap()):
        def surf_to_texture(surf):
            tex = self.ctx.texture(surf.get_size(), 4)
            tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
            tex.swizzle = 'BGRA'
            tex.write(surf.get_view('1'))
            return tex

        screen_number = 0

        # Create background screen uniforms
        for screen in self.bg_screens:
            tex = surf_to_texture(screen)
            tex.use(screen_number)
            self.program[f'bg{screen_number}Tex'] = screen_number
            screen_number += 1

        # bg0_tex = surf_to_texture(self.bg_screens[0])
        # bg0_tex.use(screen_number)
        # self.program['bg0Tex'] = screen_number
        # screen_number += 1

        ui_tex = surf_to_texture(self.ui_screen)
        ui_tex.use(screen_number)
        self.program['uiTex'] = screen_number
        screen_number += 1

        game_tex = surf_to_texture(self.game_screen)
        game_tex.use(screen_number)
        self.program['gameTex'] = screen_number
        screen_number += 1

        # game_normal = surf_to_texture(self.game_normal_screen)
        # game_normal.use(screen_number)
        # self.program['gameNormal'] = screen_number
        # screen_number += 1

        NUM_LIGHTS = 50  # Has to be the same as in frag_shader.glsl!!

        light_positions = [(pos.x, pos.y) for pos in light_map.get_positions(NUM_LIGHTS)]
        light_colors = [(col.r, col.g, col.b) for col in light_map.get_colors(NUM_LIGHTS)]
        light_intensities = [i for i in light_map.get_intensities(NUM_LIGHTS)]
        light_radii = [i for i in light_map.get_radii(NUM_LIGHTS)]

        self.program['lightPositions'] = light_positions
        self.program['lightColors'] = light_colors
        self.program['lightIntensities'] = light_intensities
        self.program['lightRadii'] = light_radii

        self.program['moonLightIntensity'] = self.moon_light_intensity

        self.program['cameraPos'] = (camera_pos.x, camera_pos.y)

        self.render_object.render(mode=moderngl.TRIANGLE_STRIP)

        pg.display.flip()

        ui_tex.release()
        game_tex.release()
