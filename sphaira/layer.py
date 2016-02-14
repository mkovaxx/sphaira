from OpenGL.GL import *
from PySide import QtCore
from PySide.QtGui import (
    QTableWidget,
    QHeaderView,
    QLabel,
    QCheckBox,
    QSlider,
    QLineEdit,
    QDoubleSpinBox,
)

import projection as proj
from glsl import Shader


class LayerList(QTableWidget):

    def __init__(self):
        super(LayerList, self).__init__(0, 6)
        self.setHorizontalHeaderLabels([
            'S', 'alpha', '',
            'M', 'orientation (w, x, y, z)',
            'file'
        ])
        hheader = self.horizontalHeader()
        hheader.setStretchLastSection(True)
        hheader.setResizeMode(0, QHeaderView.ResizeToContents)
        hheader.setResizeMode(2, QHeaderView.ResizeToContents)
        hheader.setResizeMode(3, QHeaderView.ResizeToContents)
        vheader = self.verticalHeader()
        vheader.setResizeMode(QHeaderView.ResizeToContents)
        self.layers = []

    def add_layer(self, layer):
        self.layers.append(layer)
        self.insertRow(0)
        layer.setup_ui(self, 0)

    def __iter__(self):
        return self.layers.__iter__()


class Layer(object):

    def __init__(self):
        super(Layer, self).__init__()
        self.show = QCheckBox()
        self.show.setChecked(True)
        self.alpha_slider = QSlider(QtCore.Qt.Orientation.Horizontal)
        self.alpha_slider.setRange(0, 1024)
        self.alpha_slider.setValue(1024)
        self.alpha_number = QDoubleSpinBox()
        self.alpha_number.setDecimals(3)
        self.alpha_number.setSingleStep(0.01)
        self.alpha_number.setRange(0, 1)
        self.alpha_number.setValue(1)
        self.alpha_slider.valueChanged.connect(self._alphaSliderChanged)
        self.alpha_number.valueChanged.connect(self._alphaNumberChanged)
        self.move = QCheckBox()
        self.move.setChecked(True)
        self.quat = QLineEdit()
        self.quat.setInputMask('#0.000, #0.000, #0.000, #0.000')
        self.quat.setMaxLength(30)
        self.quat.setText('+0.000, +1.000, +0.000, +0.000')
        self.label = QLabel()
        self.label.setText('<empty>')

    def _alphaSliderChanged(self):
        self.alpha_number.setValue(self.alpha_slider.value() / 1024.0)

    def _alphaNumberChanged(self):
        self.alpha_slider.setValue(1024 * self.alpha_number.value())

    def setup_ui(self, table, row):
        table.setCellWidget(row, 0, self.show)
        table.setCellWidget(row, 1, self.alpha_slider)
        table.setCellWidget(row, 2, self.alpha_number)
        table.setCellWidget(row, 3, self.move)
        table.setCellWidget(row, 4, self.quat)
        table.setCellWidget(row, 5, self.label)

    def load_file(self, file_name, in_format):
        self.sphere = proj.load_sphere(file_name, projection=in_format)
        in_format = self.sphere.__class__
        print('Loaded input %s from %s.' % (in_format.__name__, file_name))
        self.texture_id = glGenTextures(1)
        self.sphere.to_gl(self.texture_id)
        self.shader = Shader(
            vert=VERTEX_SHADER,
            frag=FRAGMENT_SHADER + self.sphere.get_glsl_sampler(),
        )
        self.label.setText(file_name)


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
    gl_FragColor.a = 0.5;
}
'''
