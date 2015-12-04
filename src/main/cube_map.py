import numpy as np
from PIL import Image
from pyglet.gl import *
from pyrr import Vector3

class CubeMap(object):

    @classmethod
    def from_image(self, image):
        array = np.array(image)
        faces = np.array([array] * 6)
        return CubeMap(faces)

    def __init__(self, faces):
        self.faces = faces

    def send_to_gl(self):
        # enable cube map texturing
        glEnable(GL_TEXTURE_CUBE_MAP)
        # generate and bind texture
        self.texture_id = (GLuint * 1)()
        glGenTextures(1, self.texture_id)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture_id[0])
        # set up texturing parameters
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_GENERATE_MIPMAP, GL_FALSE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_BASE_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAX_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
        # bind textures
        cube_faces = (GLenum * 6)(
            GL_TEXTURE_CUBE_MAP_POSITIVE_X,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X,
            # pyglet reverses y axis
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y,
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z,
        )
        # the reverse direction: image = Image.fromarray(array)
        for (face_index, cube_face) in enumerate(cube_faces):
            (face_count, width, height, depth) = self.faces.shape
            assert face_count == 6
            data = self.faces[face_index].ctypes.data
            glTexImage2D(
                cube_face, 0,
                GL_RGB, width, height, 0,
                GL_RGB, GL_UNSIGNED_BYTE, data
            )
        # set up texture coordinates
        glEnable(GL_TEXTURE_GEN_S)
        glEnable(GL_TEXTURE_GEN_T)
        glEnable(GL_TEXTURE_GEN_R)
        glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_OBJECT_LINEAR)
        glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_OBJECT_LINEAR)
        glTexGeni(GL_R, GL_TEXTURE_GEN_MODE, GL_OBJECT_LINEAR)
        x_axis = (GLfloat * 4)(1.0, 0.0, 0.0, 0.0)
        y_axis = (GLfloat * 4)(0.0, 1.0, 0.0, 0.0)
        z_axis = (GLfloat * 4)(0.0, 0.0, 1.0, 0.0)
        glTexGenfv(GL_S, GL_OBJECT_PLANE, x_axis)
        glTexGenfv(GL_T, GL_OBJECT_PLANE, y_axis)
        glTexGenfv(GL_R, GL_OBJECT_PLANE, z_axis)
