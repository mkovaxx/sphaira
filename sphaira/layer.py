from OpenGL.GL import *
from PySide.QtGui import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea

import projection as proj
from glsl import Shader


class LayerList(QScrollArea):

    def __init__(self):
        super(LayerList, self).__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addStretch()
        self.layers = []

    def add_layer(self, layer):
        self.layout.addWidget(layer)
        self.layers.append(layer)

    def __iter__(self):
        return self.layers.__iter__()


class Layer(QWidget):

    def __init__(self):
        super(Layer, self).__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.label = QLabel()
        self.label.setText('<empty>')
        self.layout.addWidget(self.label)

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
