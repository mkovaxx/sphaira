import numpy as np
from PIL import Image
import pyglet
from pyglet.gl import *
from pyrr import Quaternion, Vector3, Matrix44

from geom import SphericalMesh

class Sphaira(pyglet.window.Window):

    def __init__(self, **kwargs):
        super(Sphaira, self).__init__(**kwargs)
        self.maximize()
        self.t = 0.0
        self.orientation = Quaternion()
        self.zoom = 2.5
        self.mesh = SphericalMesh(4)
        self.load_texture()

    def load_texture(self):
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
            # pyglet reverses y axis
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y,
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z,
        )
        image = Image.open("resources/puppy.jpg")
        array = np.array(image)
        # the reverse direction: image = Image.fromarray(array)
        data = array.ctypes.data
        for cube_face in cube_faces:
            glTexImage2D(
                cube_face, 0,
                GL_RGB, image.width, image.height, 0,
                GL_RGB, GL_UNSIGNED_BYTE, data
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

    def update(self, dt):
        self.t += dt

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(50, width / float(height), .01, 100)
        glMatrixMode(GL_MODELVIEW)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        return pyglet.event.EVENT_HANDLED

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
                v.normalised,
                v.length * 0.002
            )
        # zoom on right-drag
        if buttons & 4:
            self.zoom += self.zoom * dy*0.01

    def on_draw(self):
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        self.clear()
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslatef(0, 0, -7.0)
        glScalef(self.zoom, self.zoom, self.zoom)
        m = self.orientation.matrix44
        array = (GLdouble * 16)()
        for i in xrange(4):
            for j in xrange(4):
                array[4*i + j] = m[i,j]
        glMultMatrixd(array)
        glPointSize(1.8)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        # draw stuff
        glColor3f(0.0, 0.5, 1.0)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        self.mesh.draw_triangles()
        glPopMatrix()


def main():
    config = pyglet.gl.Config(sample_buffers=1, samples=4, double_buffer=True, depth_size=24)
    window = Sphaira(caption='Sphaira', resizable=True, vsync=True, config=config)
    pyglet.clock.schedule_interval(window.update, (1.0/60))
    pyglet.app.run()

if __name__ == '__main__':
    main()
