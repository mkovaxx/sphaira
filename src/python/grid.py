import pyglet
from pyglet.gl import *

class Grid(object):

    def __init__(self, width, height):
        vertex_count = (width+1) * (height+1)

        columns = [ float(x)/width for x in range(width + 1) ]
        rows = [ float(y)/height for y in range(height + 1) ]
        vertices = []
        for r in rows:
            for c in columns:
                vertices.extend([r, c])

        indices = []
        for r in range(height):
            indices.append((width+1) * r)
            for c in range(width + 1):
                indices.append((width+1) * r + c)
                indices.append((width+1) * (r+1) + c)
            indices.append((width+1) * (r+1) + width)

        self.vertex_list = pyglet.graphics.vertex_list_indexed(
                vertex_count,
                indices,
                ('v2f/static', vertices))

    def draw_points(self):
        self.vertex_list.draw(GL_POINTS)

    def draw_triangles(self):
        self.vertex_list.draw(GL_TRIANGLE_STRIP)
