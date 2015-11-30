import pyglet
from pyglet.gl import *

class SphericalMesh(object):

    def __init__(self):
        phi = 1.61803398
        fs = [
            lambda a, b: (0, a, b),
            lambda a, b: (a, b, 0),
            lambda a, b: (b, 0, a),
        ]
        self.seed_vertices = [
            f(a, b)
            for f in fs
            for a in (+phi, -phi)
            for b in (+1, -1)
        ]
        self.vertex_list = pyglet.graphics.vertex_list(
            len(self.seed_vertices),
            ('v3d/static', [
                coord
                for vector in self.seed_vertices
                for coord in vector
            ]),
        )

    def draw_points(self):
        self.vertex_list.draw(gl.GL_POINTS)

    def draw_triangles(self):
        self.vertex_list.draw(gl.GL_TRIANGLE_STRIP)
