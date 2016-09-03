# Based on code by Tristam Macdonald.

from OpenGL.GL import *
from OpenGL.GL import shaders
from ctypes import *

class Shader:

    def __init__(self, vert = [], frag = []):
        self.handle = shaders.compileProgram(
            shaders.compileShader(vert, GL_VERTEX_SHADER),
            shaders.compileShader(frag, GL_FRAGMENT_SHADER),
        )

    def bind(self):
        # bind the program
        glUseProgram(self.handle)

    def unbind(self):
        # unbind whatever program is currently bound - not necessarily this program,
        # so this should probably be a class method instead
        glUseProgram(0)

    # upload a floating point uniform
    # this program must be currently bound
    def uniformf(self, name, *vals):
        # check there are 1-4 values
        if len(vals) in range(1, 5):
            # select the correct function
            { 1 : glUniform1f,
                2 : glUniform2f,
                3 : glUniform3f,
                4 : glUniform4f
                # retrieve the uniform location, and set
            }[len(vals)](glGetUniformLocation(self.handle, name), *vals)

    # upload an integer uniform
    # this program must be currently bound
    def uniformi(self, name, *vals):
        # check there are 1-4 values
        if len(vals) in range(1, 5):
            # select the correct function
            { 1 : glUniform1i,
                2 : glUniform2i,
                3 : glUniform3i,
                4 : glUniform4i
                # retrieve the uniform location, and set
            }[len(vals)](glGetUniformLocation(self.handle, name), *vals)

    # upload a vec3 uniform
    def uniformf_vec3(self, name, mat):
        # obtian the uniform location
        loc = glGetUniformLocation(self.handle, name)
        # uplaod the 3x3 floating point matrix
        glUniform3fv(loc, 1, (c_float * 3)(*mat))

    # upload a 3x3 matrix uniform
    def uniformf_m3x3(self, name, mat):
        # obtian the uniform location
        loc = glGetUniformLocation(self.handle, name)
        # uplaod the 3x3 floating point matrix
        glUniformMatrix3fv(loc, 1, False, (c_float * 9)(*mat))

    # upload a 4x4 matrix uniform
    def uniformf_m4x4(self, name, mat):
        # obtian the uniform location
        loc = glGetUniformLocation(self.handle, name)
        # uplaod the 4x4 floating point matrix
        glUniformMatrix4fv(loc, 1, False, (c_float * 16)(*mat))
