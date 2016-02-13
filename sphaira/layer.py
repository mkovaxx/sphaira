from OpenGL.GL import *
from PySide.QtGui import QWidget, QLabel, QTableWidget

import projection as proj
from glsl import Shader


class LayerList(QTableWidget):

    def __init__(self):
        super(LayerList, self).__init__(0, 1)
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
        self.label = QLabel()
        self.label.setText('<empty>')

    def setup_ui(self, table, row):
        table.setCellWidget(row, 0, self.label)

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
