import pygame as pg
import moderngl
from array import array
from source.utils import *
from source.constants import *


class Shader:
    def __init__(self, screen_width, screen_height):
        self.screen = pg.display.set_mode((screen_width, screen_height), pg.SCALED | pg.OPENGL | pg.DOUBLEBUF)
        self.ctx = moderngl.create_context()

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

    def update(self, display: pg.Surface):
        def surf_to_texture(surf):
            tex = self.ctx.texture(surf.get_size(), 4)
            tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
            tex.swizzle = 'BGRA'
            tex.write(surf.get_view('1'))
            return tex

        frame_tex = surf_to_texture(display)
        frame_tex.use(0)
        self.program['tex'] = 0

        self.render_object.render(mode=moderngl.TRIANGLE_STRIP)

        pg.display.flip()

        frame_tex.release()
