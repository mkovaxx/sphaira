import pyglet
from pyglet.gl import *
from pyrr import Quaternion, Vector3, Matrix44

from geom import SphericalMesh

class Sphaira(pyglet.window.Window):

    def __init__(self, **kwargs):
        super(Sphaira, self).__init__(**kwargs)
        self.t = 0.0
        self.orientation = Quaternion()
        self.zoom = 1.0
        self.grid = SphericalMesh()

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
        glMultMatrixd(array);
        glPointSize(1.8)
        glPolygonMode(GL_FRONT, GL_LINE)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        self.grid.draw_triangles()
        glPopMatrix()


def main():
    config = pyglet.gl.Config(sample_buffers=1, samples=4, double_buffer=True, depth_size=24)
    window = Sphaira(caption='Sphaira', resizable=True, vsync=True, config=config)
    pyglet.clock.schedule_interval(window.update, (1.0/60))
    pyglet.app.run()

if __name__ == '__main__': main()
