from OpenGL.GL import *
from pyrr import Quaternion, Vector3, Matrix44
from PySide import QtCore
from PySide.QtGui import (
    QWidget,
    QVBoxLayout,
    QToolBar,
    QIcon,
    QFileDialog,
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

class LayerListWithToolBar(QWidget):

    def __init__(self):
        super(LayerListWithToolBar, self).__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.list = LayerList()
        self.toolbar = QToolBar()
        add_action = self.toolbar.addAction(
            QIcon.fromTheme('list-add'),
            'add',
        ).triggered.connect(self._add)
        remove_action = self.toolbar.addAction(
            QIcon.fromTheme('list-remove'),
            'remove',
        ).triggered.connect(self._remove)
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.list)

    def _add(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setViewMode(QFileDialog.Detail)
        fileNames = dialog.selectedFiles() if dialog.exec_() else []
        for fileName in fileNames:
            layer = Layer()
            layer.load_file(fileName, None)
            self.list.add_layer(layer)

    def _remove(self):
        rows = sorted({index.row() for index in self.list.selectedIndexes()})
        for row in reversed(rows):
            self.list.remove_layer(row)

    def add_layer(self, layer):
        self.list.add_layer(layer)

    def __iter__(self):
        return self.list.__iter__()

    def multiplyOrientation(self, quat):
        self.list.multiplyOrientation(quat)


class LayerList(QTableWidget):

    def __init__(self):
        super(LayerList, self).__init__(0, 7)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setHorizontalHeaderLabels([
            'S',
            'V', 'alpha', '',
            'M', 'orientation (w, x, y, z)',
            'file'
        ])
        hheader = self.horizontalHeader()
        hheader.setStretchLastSection(True)
        hheader.setResizeMode(QHeaderView.ResizeToContents)
        hheader.setResizeMode(2, QHeaderView.Interactive)
        vheader = self.verticalHeader()
        vheader.setResizeMode(QHeaderView.ResizeToContents)
        self.layers = []

    def dropEvent(self, event):
        if event.source() != self:
            QTableView.dropEvent(event)
            return
        src_row = self.selectedIndexes()[0].row()
        dst_row = self.rowAt(event.pos().y())
        if dst_row == -1:
            dst_row = self.rowCount()
        self.move_layer(src_row, dst_row)
        if src_row < dst_row:
            dst_row -= 1
        self.selectRow(dst_row)
        event.accept()

    def move_layer(self, src_row, dst_row):
        self.insert_layer(dst_row, self.layers[src_row])
        if dst_row < src_row:
            src_row += 1
        self.remove_layer(src_row)

    def insert_layer(self, index, layer):
        self.layers.insert(index, layer)
        self.insertRow(index)
        layer.setup_ui(self, index)

    def remove_layer(self, index):
        self.removeRow(index)
        del self.layers[index]

    def add_layer(self, layer):
        self.insert_layer(0, layer)

    def __iter__(self):
        return reversed(self.layers)

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
        table.setCellWidget(row, 1, self.show)
        table.setCellWidget(row, 2, self.alpha_slider)
        table.setCellWidget(row, 3, self.alpha_number)
        table.setCellWidget(row, 4, self.move)
        table.setCellWidget(row, 5, self.quat)
        table.setCellWidget(row, 6, self.label)

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
