import argparse
import numpy as np
from PIL import Image
import pyglet
from pyglet.gl import *
from pyrr import Quaternion, Vector3, Matrix44

import projection as proj
from geom import SphericalMesh
from glsl import Shader

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
        self.sphere = proj.load_sphere(file_name, projection=in_format)
        in_format = self.sphere.__class__
        print('Loaded input %s from %s.' % (in_format.__name__, file_name))
        self.texture_id = (GLuint * 1)()
        glGenTextures(1, self.texture_id)
        self.sphere.to_gl(self.texture_id[0])
        self.shader = Shader(
            vert=VERTEX_SHADER,
            frag=[
                FRAGMENT_SHADER,
                self.sphere.get_glsl_sampler(),
            ]
        )

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
        self.shader.bind()
        glActiveTexture(GL_TEXTURE0 + self.texture_id[0])
        self.sphere.bind_glsl_texture(self.texture_id[0], self.shader)
        self.mesh.draw_triangles()
        glPopMatrix()


VERTEX_SHADER = '''
#version 130
attribute vec4 vert;
varying vec3 texCoord;
void main()
{
    gl_Position = gl_ModelViewProjectionMatrix * vert;
    texCoord = vert.xyz;
}
'''

FRAGMENT_SHADER = '''
#version 130
varying vec3 texCoord;
vec4 sample(vec3 v);
void main()
{
    gl_FragColor = sample(texCoord);
}
'''


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
