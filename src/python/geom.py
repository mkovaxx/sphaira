import pyglet
from pyglet.gl import *
from pyrr import Vector3

class SphericalMesh(object):

    def __init__(self, resolution):
        self.resolution = resolution
        seed = Icosahedron()
        self.vertices = []
        self.indices = []
        for (i, j, k) in seed.triangles:
            self._subdiv_triangle(
                seed.vertices[i],
                seed.vertices[j],
                seed.vertices[k],
            )
        self.vertex_list = pyglet.graphics.vertex_list_indexed(
            len(self.vertices),
            self.indices,
            ('v3d/static', [
                coord
                for vector in self.vertices
                for coord in vector
            ]),
        )

    def _subdiv_triangle(self, a, b, c):
        base = len(self.vertices)
        dx = (b - a) / self.resolution
        dy = (c - a) / self.resolution
        for j in xrange(0, self.resolution + 1):
            cnt = self.resolution + 1 - j
            for i in xrange(0, cnt):
                self.vertices.append((a + i*dx + j*dy).normalised)
            for i in xrange(0, cnt - 1):
                self.indices.extend([
                    base + i,
                    base + i + 1,
                    base + cnt + i
                ])
            base += cnt

    def draw_triangles(self):
        self.vertex_list.draw(gl.GL_TRIANGLES)


class Icosahedron(object):

    def __init__(self):
        phi = 1.61803398
        fs = [
            lambda a, b: [0, a, b],
            lambda a, b: [a, b, 0],
            lambda a, b: [b, 0, a],
        ]
        vertices = [
            Vector3(f(a, b))
            for f in fs
            for a in (+phi, -phi)
            for b in (+1, -1)
        ]
        edges = {
            (i, j)
            for j in xrange(0, 12)
            for i in xrange(0, j)
            if (vertices[i] - vertices[j]).length < 3
        }
        triangles = [
            (i, j, k)
            if vertices[i] ^ vertices[j] | vertices[k] > 0 else
            (j, i, k)
            for k in xrange(0, 12)
            for j in xrange(0, k)
            for i in xrange(0, j)
            if {(i, j), (i, k), (j, k)}.issubset(edges)
        ]
        self.vertices = vertices
        self.edges = edges
        self.triangles = triangles
