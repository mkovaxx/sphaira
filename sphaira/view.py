import argparse
from ctypes import *
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective
from PIL import Image
from pyrr import Quaternion, Vector3, Matrix44, matrix44
from PySide import QtCore
from PySide.QtGui import QMainWindow, QApplication, QDockWidget
from PySide.QtOpenGL import QGLWidget, QGLFormat

import projection as proj
from geom import SphericalMesh, intersectRayUnitSphere
from glsl import Shader
from layer import Layer, LayerList, LayerListWithToolBar

class SphairaView(QGLWidget):

    def __init__(self, layers):
        format = QGLFormat()
        format.setVersion(3, 2)
        format.setProfile(QGLFormat.CoreProfile)
        QGLFormat.setDefaultFormat(format)
        super(SphairaView, self).__init__()
        self.old_pos = QtCore.QPoint(0, 0)
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.layers = layers
        self.zoom = 0.9

    def load_file(self, filename, in_format):
        layer = Layer()
        layer.load_file(filename, in_format)
        self.layers.add_layer(layer)

    def initializeGL(self):
        print(
            'OpenGL version: {0}'.format(glGetString(GL_VERSION))
        )
        print(
            'GLSL version: {0}'.format(glGetString(GL_SHADING_LANGUAGE_VERSION))
        )
        self.mesh = SphericalMesh(4)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        self.viewport = (w, h)
        self.projTransform = Matrix44.perspective_projection(
            50, float(w) / h,
            0.01, 100.0,
        )

    def mouseMoveEvent(self, event):
        pos = event.pos()
        # compute point on sphere under pointer
        (w, h) = self.viewport
        t = self.old_pos.x() / float(w)
        t = 2*t - 1
        u = self.old_pos.y() / float(h)
        u = 2*u - 1
        u = u * h/float(w)
        # compute inverse of view transform ignoring rotation
        m = Matrix44.from_translation(Vector3([0, 0, -self.zoom])) * self.projTransform
        m = matrix44.inverse(m)
        rayOri = m * Vector3([0, 0, 0])
        rayEnd = m * Vector3([t, u, 1])
        rayDir = rayEnd - rayOri
        self.picked = intersectRayUnitSphere(rayOri, rayDir)
        # rotate on left-drag
        if event.buttons() & QtCore.Qt.LeftButton > 0:
            # the rotation vector is the displacement vector rotated by 90 degrees
            dx = pos.x() - self.old_pos.x()
            dy = pos.y() - self.old_pos.y()
            if dx == 0 and dy == 0:
                return
            v = Vector3([dy, dx, 0])
            # update the current orientation
            self.layers.multiplyOrientation(Quaternion.from_axis_rotation(
                -v.normalised,
                -v.length * 0.002,
            ))
        elif event.buttons() & QtCore.Qt.RightButton > 0:
            dz = pos.y() - self.old_pos.y()
            self.zoom = max(0, self.zoom + dz / 100.0)
        self.old_pos = pos
        self.update()

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Space:
            print "picked:", self.picked

    def paintGL(self):
        glClearColor(0, 0, 0, 1);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_CULL_FACE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glFrontFace(GL_CCW)
        glCullFace(GL_BACK if self.zoom > 1.0 else GL_FRONT)
        self.mesh.bind()
        for layer in self.layers:
            layer.shader.bind()
            layer.shader.uniformf('alphaFactor', layer.alpha())
            m = layer.orientation.matrix33
            array = (GLdouble * 9)()
            for i in xrange(3):
                for j in xrange(3):
                    array[3*i + j] = m[i,j]
            layer.shader.uniformf_m3x3('orientation', array)
            # setup view transform
            m = self.projTransform
            m = Matrix44.from_translation(Vector3([0, 0, -self.zoom])) * m
            array = (GLdouble * 16)()
            for i in xrange(4):
                for j in xrange(4):
                    array[4*i + j] = m[i,j]
            layer.shader.uniformf_m4x4('viewTransform', array)
            glActiveTexture(GL_TEXTURE0 + layer.texture_id)
            layer.sphere.bind_glsl_texture(layer.texture_id, layer.shader)
            self.mesh.draw_triangles(layer.shader.handle)


class SphairaApp(QApplication):

    def __init__(self, args):
        super(SphairaApp, self).__init__(args)
        name = 'Sphaira Viewer'
        self.setApplicationName(name)
        self.layer_widget = QDockWidget('Layers')
        self.layer_widget.setFeatures(
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetFloatable
        )
        self.layer_list = LayerListWithToolBar()
        self.layer_widget.setWidget(self.layer_list)
        self.gl_widget = SphairaView(self.layer_list)
        self.mainWindow = QMainWindow()
        self.mainWindow.setWindowTitle(name)
        self.mainWindow.setCentralWidget(self.gl_widget)
        self.mainWindow.addDockWidget(
            QtCore.Qt.DockWidgetArea.BottomDockWidgetArea,
            self.layer_widget,
        )
        self.mainWindow.resize(800, 600)
        self.mainWindow.showMaximized()

    def load_file(self, file_name, in_format):
        return self.gl_widget.load_file(file_name, in_format)


def main():
    parser = argparse.ArgumentParser(
        prog='view',
        description='Sphaira viewer for spherical data.',
    )
    parser.add_argument('-i', '--in_format', help='IN_FORMAT')
    parser.add_argument('input', nargs='*', help='INPUT')
    (args, leftover) = parser.parse_known_args()
    in_format = proj.get_format(args.in_format)
    app = SphairaApp(leftover)
    for filename in args.input:
        app.load_file(filename, in_format)
    app.exec_()


if __name__ == '__main__':
    main()
