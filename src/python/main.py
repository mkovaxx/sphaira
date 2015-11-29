import pyglet
from pyglet import gl

from grid import *
from vqm import *


class Sphaira(pyglet.window.Window):

    def __init__(self, **kwargs):
        super(Sphaira, self).__init__(**kwargs)
        self.t = 0.0
        self.orientation = Quat(1, Vec3(0,0,0))
        self.zoom = 1.0
        self.grid = Grid(100, 100)

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
            v = Vec3(dy, -dx, 0).scale(0.002)
            # update the current orientation
            self.orientation = self.orientation * v.rotation()
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
        r = self.orientation.conj().matrix()
        # column-major order
        m = [r.X.x, r.X.y, r.X.z, 0,
             r.Y.x, r.Y.y, r.Y.z, 0,
             r.Z.x, r.Z.y, r.Z.z, 0,
                 0,     0,     0, 1,]
        array = (GLfloat * len(m))()
        for index, value in enumerate(m):
            array[index] = value
        glMultMatrixf(array);
        glPointSize(1.8)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        self.grid.draw_triangles()
        glPopMatrix()


def main():
    config = pyglet.gl.Config(sample_buffers=1, samples=4, double_buffer=True, depth_size=24)
    window = Sphaira(caption='Sphaira', resizable=True, vsync=True, config=config)
    pyglet.clock.schedule_interval(window.update, (1.0/60))
    pyglet.app.run()

if __name__ == '__main__': main()
