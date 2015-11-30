import pyglet
from pyglet.gl import *
from pyrr import Vector3

class SphericalMesh(object):

    def __init__(self):
        phi = 1.61803398
        fs = [
            lambda a, b: [0, a, b],
            lambda a, b: [a, b, 0],
            lambda a, b: [b, 0, a],
        ]
        seed_vertices = [
            Vector3(f(a, b))
            for f in fs
            for a in (+phi, -phi)
            for b in (+1, -1)
        ]
        seed_edges = {
            (i, j)
            for j in xrange(0, 12)
            for i in xrange(0, j)
            if (seed_vertices[i] - seed_vertices[j]).length < 3
        }
        seed_triangles = [
            (i, j, k)
            if seed_vertices[i] ^ seed_vertices[j] | seed_vertices[k] > 0 else
            (j, i, k)
            for k in xrange(0, 12)
            for j in xrange(0, k)
            for i in xrange(0, j)
            if {(i, j), (i, k), (j, k)}.issubset(seed_edges)
        ]
        vertices = seed_vertices
        indices = []
        for (i, j, k) in seed_triangles:
            indices.extend([i, j, k])
        self.vertex_list = pyglet.graphics.vertex_list_indexed(
            len(vertices),
            indices,
            ('v3d/static', [
                coord
                for vector in vertices
                for coord in vector
            ]),
        )

    def draw_triangles(self):
        self.vertex_list.draw(gl.GL_TRIANGLES)
