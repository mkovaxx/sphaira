import argparse
from ctypes import *
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective
from PIL import Image
from pyrr import Quaternion, Vector3, Matrix44
from PySide import QtCore
from PySide.QtGui import QMainWindow, QApplication, QDockWidget
from PySide.QtOpenGL import QGLWidget

import projection as proj
from geom import SphericalMesh
from glsl import Shader
from layer import Layer, LayerList, LayerListWithToolBar

class SphairaView(QGLWidget):

    def __init__(self, layers):
        super(SphairaView, self).__init__()
        self.mesh = SphericalMesh(4)
        self.old_pos = QtCore.QPoint(0, 0)
        self.setMouseTracking(True)
        self.layers = layers

    def load_file(self, filename, in_format):
        layer = Layer()
        layer.load_file(filename, in_format)
        self.layers.add_layer(layer)

    def initializeGL(self):
        pass

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(50, float(w) / h, .01, 100)

    def mouseMoveEvent(self, event):
        pos = event.pos()
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
        self.old_pos = pos
        self.update()

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
        glCullFace(GL_BACK)
        for layer in self.layers:
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glTranslatef(0, 0, -2.9)
            # draw stuff
            layer.shader.bind()
            layer.shader.uniformf('alphaFactor', layer.alpha())
            m = layer.orientation.matrix33
            array = (GLdouble * 9)()
            for i in xrange(3):
                for j in xrange(3):
                    array[3*i + j] = m[i,j]
            layer.shader.uniformf_m3x3('orientation', array)
            glActiveTexture(GL_TEXTURE0 + layer.texture_id)
            layer.sphere.bind_glsl_texture(layer.texture_id, layer.shader)
            self.mesh.draw_triangles()


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
    parser.add_argument('input', nargs='+', help='INPUT')
    (args, leftover) = parser.parse_known_args()
    in_format = proj.get_format(args.in_format)
    app = SphairaApp(leftover)
    for filename in args.input:
        app.load_file(filename, in_format)
    app.exec_()


if __name__ == '__main__':
    main()
