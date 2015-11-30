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
        self.seed_indices = []
        for i in xrange(3):
            for j in xrange(2):
                self.seed_indices.extend([4*i + 0, 4*i + 1, 4*i + 4])
                self.seed_indices.extend([4*i + 1, 4*i + 0, 4*i + 6])
                self.seed_indices.extend([4*i + 3, 4*i + 2, 4*i + 5])
                self.seed_indices.extend([4*i + 2, 4*i + 3, 4*i + 7])
        self.vertex_list = pyglet.graphics.vertex_list_indexed(
            len(self.seed_vertices),
            map(lambda x: x % 12, self.seed_indices),
            ('v3d/static', [
                coord
                for vector in self.seed_vertices
                for coord in vector
            ]),
        )

    def draw_points(self):
        self.vertex_list.draw(gl.GL_POINTS)

    def draw_triangles(self):
        self.vertex_list.draw(gl.GL_TRIANGLES)
