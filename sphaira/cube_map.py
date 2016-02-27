import numpy as np
from OpenGL.GL import *
from pyrr import Vector3

import external


class CubeMap(object):

    sampler = external.cube_map_get_sampler()

    @classmethod
    def check_array(cls, array):
        if array.dtype != np.float32:
            return 1
        if array.ndim != 4:
            return 2
        (face_count, height, width, depth) = array.shape
        if depth != 4:
            return 3
        if face_count != 6:
            return 4
        if width != height:
            return 5
        return 0

    @classmethod
    def check_image(cls, image):
        if image.dtype != np.float32:
            return 1
        if image.ndim != 3:
            return 2
        (height, width, depth) = image.shape
        if depth != 4:
            return 3
        if 2*width != 3*height:
            return 4
        return 0

    @classmethod
    def from_array(cls, faces):
        assert cls.check_array(faces) == 0
        return CubeMap(faces)

    @classmethod
    def from_image(cls, image):
        assert cls.check_image(image) == 0
        # decompose 3x2 mosaic into cube map faces
        (pos, neg) = np.vsplit(image, 2)
        (xp, yp, zp) = np.hsplit(pos, 3)
        (xn, yn, zn) = np.hsplit(neg, 3)
        array = np.stack([xp, xn, yp, yn, zp, zn])
        return CubeMap(array)

    def to_image(self):
        # combine cube map faces into a 3x2 mosaic
        return np.vstack([
            np.hstack([self.array[0], self.array[2], self.array[4]]),
            np.hstack([self.array[1], self.array[3], self.array[5]]),
        ])

    def to_gl(self, texture_id):
        # enable cube map texturing
        glEnable(GL_TEXTURE_CUBE_MAP)
        # generate and bind texture
        glBindTexture(GL_TEXTURE_CUBE_MAP, texture_id)
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
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z,
        )
        (face_count, height, width, depth) = self.array.shape
        for (face_index, cube_face) in enumerate(cube_faces):
            glTexImage2D(
                cube_face, 0, 4,
                width, height, 0,
                GL_RGBA, GL_FLOAT, self.array[face_index],
            )

    def get_glsl_sampler(self):
        return '''
uniform samplerCube cubeMap;
vec4 sample(vec3 v) {
    return textureCube(cubeMap, v);
}
'''

    def bind_glsl_texture(self, texture_id, shader):
        glBindTexture(GL_TEXTURE_CUBE_MAP, texture_id)
        shader.uniformi('cubeMap', texture_id)

    @classmethod
    def from_sphere(cls, sphere, resolution=None):
        resolution = resolution or sphere.resolution
        size = int(np.sqrt(resolution / 6))
        faces = np.zeros((6, size, size, 4), dtype=np.float32)
        external.cube_map_assign(faces, sphere.array, sphere.sampler)
        return CubeMap(faces)

    def __init__(self, faces):
        # sanity check
        assert external.cube_map_check(faces) == 0
        self.array = faces
        self.resolution = int(6 * faces.shape[1]**2)
