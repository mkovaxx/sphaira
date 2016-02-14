from OpenGL.GL import *
from pyrr import Quaternion, Vector3, Matrix44
from PySide import QtCore
from PySide.QtGui import (
    QTableWidget,
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QCheckBox,
    QSlider,
    QLineEdit,
    QFont,
    QFontMetrics,
    QDoubleSpinBox,
)

import projection as proj
from glsl import Shader


class LayerList(QTableWidget):

    def __init__(self):
        super(LayerList, self).__init__(0, 6)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setHorizontalHeaderLabels([
            'S', 'alpha', '',
            'M', 'orientation (w, x, y, z)',
            'file'
        ])
        hheader = self.horizontalHeader()
        hheader.setStretchLastSection(True)
        hheader.setResizeMode(QHeaderView.ResizeToContents)
        hheader.setResizeMode(1, QHeaderView.Interactive)
        vheader = self.verticalHeader()
        vheader.setResizeMode(QHeaderView.ResizeToContents)
        self.layers = []

    def add_layer(self, layer):
        self.layers.append(layer)
        self.insertRow(0)
        layer.setup_ui(self, 0)

    def __iter__(self):
        return self.layers.__iter__()

    def multiplyOrientation(self, quat):
        for layer in self.layers:
            if layer.move.isChecked():
                layer.multiplyOrientation(quat)


class Layer(object):

    def __init__(self):
        super(Layer, self).__init__()
        self.orientation = Quaternion()
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
        font = QFont('monospace')
        font.setStyleHint(QFont.TypeWriter)
        self.quat.setFont(font)
        default_quat = '+0.000, +1.000, +0.000, +0.000'
        margins = self.quat.textMargins()
        self.quat.setFixedWidth(
            # HACK -------------------------------------------v
            QFontMetrics(self.quat.font()).width(default_quat + '  ') +
            margins.left() + margins.right()
        )
        self.quat.setInputMask('#0.000, #0.000, #0.000, #0.000')
        self.quat.setMaxLength(30)
        self.quat.setText(default_quat)
        self.quat.editingFinished.connect(self._orientationChanged)
        self.label = QLabel()
        self.label.setText('<empty>')

    def multiplyOrientation(self, quat):
        self.setOrientation(quat * self.orientation)

    def setOrientation(self, quat):
        self.orientation = quat
        self.quat.setText(
            '%+1.3f, %+1.3f, %+1.3f, %+1.3f' % (
                self.orientation.w,
                self.orientation.x,
                self.orientation.y,
                self.orientation.z,
            )
        )

    def _orientationChanged(self):
        text = self.quat.text()
        print 'orientation changed to: %s' % text

    def alpha(self):
        return self.alpha_number.value() if self.show.isChecked() else 0.0

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
uniform float alphaFactor;
uniform mat3x3 orientation;
varying vec3 texCoord;
vec4 sample(vec3 v);
void main()
{
    gl_FragColor = sample(orientation * texCoord);
    gl_FragColor.a *= alphaFactor;
}
'''
