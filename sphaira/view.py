import argparse
from ctypes import *
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective
from PIL import Image
from pyrr import Quaternion, Vector3, Matrix44
from PySide import QtCore
from PySide.QtGui import QMainWindow, QApplication
from PySide.QtOpenGL import QGLWidget

import projection as proj
from geom import SphericalMesh
from glsl import Shader

class SphairaView(QGLWidget):

    def __init__(self, **kwargs):
        super(SphairaView, self).__init__(**kwargs)
        self.orientation = Quaternion()
        self.mesh = SphericalMesh(4)
        self.old_pos = QtCore.QPoint(0, 0)
        self.setMouseTracking(True)

    def load_file(self, file_name, in_format):
        self.sphere = proj.load_sphere(file_name, projection=in_format)
        in_format = self.sphere.__class__
        print('Loaded input %s from %s.' % (in_format.__name__, file_name))
        self.texture_id = (GLuint * 1)()
        self.texture_id = [glGenTextures(1)]
        self.sphere.to_gl(self.texture_id[0])
        print 1
        self.shader = Shader(
            vert=VERTEX_SHADER,
            frag=[
                FRAGMENT_SHADER,
                self.sphere.get_glsl_sampler(),
            ]
        )

    def initializeGL(self):
        pass

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(50, w / h, .01, 100)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        # rotate on left-drag
        if event.buttons() & QtCore.Qt.LeftButton > 0:
            # the rotation vector is the displacement vector rotated by 90 degrees
            dx = pos.x() - self.old_pos.x()
            dy = pos.y() - self.old_pos.y()
            if dx == 0 and dy == 0:
                return
            v = Vector3([dy, -dx, 0])
            # update the current orientation
            self.orientation *= Quaternion.from_axis_rotation(
                -v.normalised,
                v.length * 0.002
            )
        self.old_pos = pos
        self.update()

    def paintGL(self):
        glClearColor(0, 0, 0, 1);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -3.9)
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
    gl_FragColor = vec4(1, 1, 1, 1); //sample(texCoord);
}
'''


class SphairaApp(QApplication):

    def __init__(self, args):
        super(SphairaApp, self).__init__(args)
        self.setApplicationName("Sphaira Viewer")
        self.mainWindow = QMainWindow()
        self.gl_widget = SphairaView()
        self.mainWindow.setCentralWidget(self.gl_widget)
        self.mainWindow.resize(1024, 768)
        self.mainWindow.show()

    def load_file(self, file_name, in_format):
        return self.gl_widget.load_file(file_name, in_format)


def main():
    parser = argparse.ArgumentParser(
        prog='view',
        description='Sphaira viewer for spherical data.',
    )
    parser.add_argument('-i', '--in_format', help='IN_FORMAT')
    parser.add_argument('input', help='INPUT')
    (args, leftover) = parser.parse_known_args()
    in_format = proj.get_format(args.in_format)
    app = SphairaApp(leftover)
    app.load_file(args.input, in_format)
    app.exec_()


if __name__ == '__main__':
    main()
