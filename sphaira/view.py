import argparse
import numpy as np
from PIL import Image
import pyglet
from pyglet.gl import *
from pyrr import Quaternion, Vector3, Matrix44

import projection as proj
from geom import SphericalMesh

class Sphaira(pyglet.window.Window):

    def __init__(self, **kwargs):
        super(Sphaira, self).__init__(**kwargs)
        self.maximize()
        self.t = 0.0
        self.orientation = Quaternion()
        self.zoom = 2.5
        self.mesh = SphericalMesh(4)
        self.cube_map = None

    def load_file(self, file_name, in_format):
        sphere = proj.load_sphere(file_name, projection=in_format)
        in_format = sphere.__class__
        out_format = proj.CubeMap
        print('Loaded input %s from %s.' % (in_format.__name__, file_name))
        sphere = proj.convert_sphere(sphere, out_format)
        print('Converted %s to %s.' % (in_format.__name__, out_format.__name__))
        self.cube_map = sphere
        self.send_cube_map_to_gl(self.cube_map)

    def update(self, dt):
        self.t += dt

    def on_mouse_press(self, x, y, button, modifiers):
        # self.set_exclusive_mouse()
        return

    def on_mouse_release(self, x, y, button, modifiers):
        # self.set_exclusive_mouse(exclusive=False)
        return

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        # rotate on left-drag
        if buttons & 1:
            # the rotation vector is the displacement vector rotated by 90 degrees
            if dx == 0 and dy == 0:
                return
            v = Vector3([dy, -dx, 0])
            # update the current orientation
            self.orientation *= Quaternion.from_axis_rotation(
                -v.normalised,
                v.length * 0.002
            )
        # zoom on right-drag
        if buttons & 4:
            self.zoom += self.zoom * dy*0.01

    def on_draw(self):
        glViewport(0, 0, self.width, self.height)
        self.clear()
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(50, self.width / float(self.height), .01, 100)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslatef(0, 0, -0.9)
        m = self.orientation.matrix44
        array = (GLdouble * 16)()
        for i in xrange(4):
            for j in xrange(4):
                array[4*i + j] = m[i,j]
        glMultMatrixd(array)
        glPointSize(1.8)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        # draw stuff
        glColor3f(0.0, 0.5, 1.0)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        self.mesh.draw_triangles()
        glPopMatrix()

    def send_cube_map_to_gl(self, cube_map):
        # enable cube map texturing
        glEnable(GL_TEXTURE_CUBE_MAP)
        # generate and bind texture
        self.texture_id = (GLuint * 1)()
        glGenTextures(1, self.texture_id)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture_id[0])
        # set up texturing parameters
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_GENERATE_MIPMAP, GL_FALSE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_BASE_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAX_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
        # bind textures
        cube_faces = (GLenum * 6)(
            GL_TEXTURE_CUBE_MAP_POSITIVE_X,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X,
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z,
        )
        (face_count, height, width, depth) = cube_map.array.shape
        assert face_count == 6
        for (face_index, cube_face) in enumerate(cube_faces):
            data = cube_map.array[face_index].ctypes.data
            glTexImage2D(
                cube_face, 0,
                GL_RGBA, width, height, 0,
                GL_RGBA, GL_FLOAT, data
            )
        # set up texture coordinates
        glEnable(GL_TEXTURE_GEN_S)
        glEnable(GL_TEXTURE_GEN_T)
        glEnable(GL_TEXTURE_GEN_R)
        glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_OBJECT_LINEAR)
        glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_OBJECT_LINEAR)
        glTexGeni(GL_R, GL_TEXTURE_GEN_MODE, GL_OBJECT_LINEAR)
        x_axis = (GLfloat * 4)(1.0, 0.0, 0.0, 0.0)
        y_axis = (GLfloat * 4)(0.0, 1.0, 0.0, 0.0)
        z_axis = (GLfloat * 4)(0.0, 0.0, 1.0, 0.0)
        glTexGenfv(GL_S, GL_OBJECT_PLANE, x_axis)
        glTexGenfv(GL_T, GL_OBJECT_PLANE, y_axis)
        glTexGenfv(GL_R, GL_OBJECT_PLANE, z_axis)


def main():
    parser = argparse.ArgumentParser(
        prog='view',
        description='Sphaira viewer for spherical data.',
    )
    parser.add_argument('-i', '--in_format', help='IN_FORMAT')
    parser.add_argument('input', help='INPUT')
    args = parser.parse_args()
    in_format = proj.get_format(args.in_format)
    config = pyglet.gl.Config(sample_buffers=1, samples=4, double_buffer=True, depth_size=24)
    window = Sphaira(caption='Sphaira Viewer', resizable=True, vsync=True, config=config)
    window.load_file(args.input, in_format)
    pyglet.clock.schedule_interval(window.update, (1.0/60))
    pyglet.app.run()

if __name__ == '__main__':
    main()
