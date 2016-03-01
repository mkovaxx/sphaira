import copy
import numpy as np
from OpenGL.arrays import vbo
from OpenGL.GL import *
from pyrr import Vector3

class SphericalMesh(object):

    def __init__(self, resolution):
        seed = Icosahedron()
        for i in xrange(0, resolution):
            seed = seed.subdivide()
        self.vertices = seed.vertices
        self.indices = []
        for abc in seed.triangles:
            self.indices.extend(abc)
        for i in xrange(len(self.vertices)):
            self.vertices[i].normalise()
        vertex_array = np.array(self.vertices, dtype=np.float32)
        self.vertex_buffer = vbo.VBO(vertex_array)
        index_array = np.array(self.indices, dtype=np.uint32)
        self.index_buffer = vbo.VBO(index_array, target=GL_ELEMENT_ARRAY_BUFFER)
        self.index_count = len(self.indices)
        # init vertex array object
        self.vao = glGenVertexArrays(1)

    def bind(self):
        glBindVertexArray(self.vao)
        self.vertex_buffer.bind()
        self.index_buffer.bind()

    def draw_triangles(self, shader):
        location = glGetAttribLocation(shader, 'vert')
        glEnableVertexAttribArray(location)
        glVertexAttribPointer(location, 3, GL_FLOAT, False, 0, None)
        glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, None)


class TriangleMesh(object):

    def __init__(self, vertices, edges, triangles):
        self.vertices = vertices
        self.edges = edges
        self.triangles = triangles

    def subdivide(self):
        vertices = copy.deepcopy(self.vertices)
        edge_midpoint = {}
        edges = set()
        for (a, b) in self.edges:
            m_ab = len(vertices)
            vertices.append((vertices[a] + vertices[b]) / 2)
            edge_midpoint[(a, b)] = m_ab
            edge_midpoint[(b, a)] = m_ab
            edges.add((a, m_ab))
            edges.add((b, m_ab))
        triangles = []
        for (a, b, c) in self.triangles:
            m_ab = edge_midpoint[(a, b)]
            m_ac = edge_midpoint[(a, c)]
            m_bc = edge_midpoint[(b, c)]
            triangles.extend([
                (a, m_ab, m_ac),
                (b, m_bc, m_ab),
                (c, m_ac, m_bc),
                (m_ab, m_bc, m_ac),
            ])
            edges.add((m_ab, m_bc))
            edges.add((m_bc, m_ac))
            edges.add((m_ac, m_ab))
        return TriangleMesh(vertices, edges, triangles)


class Icosahedron(TriangleMesh):

    def __init__(self):
        phi = 1.61803398
        fs = [
            lambda a, b: [0, a, b],
            lambda a, b: [a, b, 0],
            lambda a, b: [b, 0, a],
        ]
        vertices = [
            Vector3(f(a, b)).normalised
            for f in fs
            for a in (+phi, -phi)
            for b in (+1, -1)
        ]
        edges = {
            (i, j)
            for j in xrange(0, 12)
            for i in xrange(0, j)
            if (vertices[i] - vertices[j]).length < 1.5
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
