import numpy as np
from OpenGL.GL import *
from pyrr import Vector3

import external


class Equirect(object):

    sampler = external.equirect_get_sampler()

    @classmethod
    def check_array(cls, array):
        if array.dtype != np.float32:
            return 1
        if array.ndim != 4:
            return 2
        (layers, height, width, depth) = array.shape
        if depth != 4:
            return 3
        if layers != 1:
            return 4
        if width != 2*height:
            return 5
        return 0

    @classmethod
    def check_image_shape(cls, width, height):
        if width != 2*height:
            return 1
        return 0

    @classmethod
    def from_array(cls, array):
        assert cls.check_array(array) == 0
        return Equirect(array)

    @classmethod
    def from_image(cls, image):
        array = np.expand_dims(image, 0)
        return cls.from_array(array)

    def to_image(self):
        return self.array[0]

    def to_gl(self, texture_id):
        # enable texturing
        #glEnable(GL_TEXTURE_2D)
        # generate and bind texture
        glBindTexture(GL_TEXTURE_2D, texture_id)
        # set up texturing parameters
        #glTexParameteri(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_FALSE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        (layers, height, width, depth) = self.array.shape
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA32F,
            width, height, 0, GL_RGBA, GL_FLOAT, self.array,
        )

    def get_glsl_sampler(self):
        return '''
uniform sampler2D rectMap;
const float M_PI = 3.141592653589793238462643383;
vec4 sample(vec3 v) {
    float phi = atan(v.y, v.x);
    float r = length(v);
    float theta = acos(v.z / r);
    float t = 0.5*phi/M_PI + 0.5;
    float u = theta/M_PI;
    return texture2D(rectMap, vec2(t, u));
}
'''

    def bind_glsl_texture(self, texture_id, shader):
        glBindTexture(GL_TEXTURE_2D, texture_id)
        shader.uniformi('rectMap', texture_id)

    @classmethod
    def from_sphere(cls, sphere, resolution=None):
        resolution = resolution or sphere.resolution
        height = int(np.sqrt(resolution / 2))
        width = 2*height
        faces = np.zeros((1, height, width, 4), dtype=np.float32)
        external.equirect_assign(faces, sphere.array, sphere.sampler)
        return Equirect(faces)

    def __init__(self, array):
        # sanity check
        assert external.equirect_check(array) == 0
        self.array = array
        self.resolution = int(2 * array.shape[1]**2)

    def sample(self, v):
        (t, u) = self._spherical_to_internal(v)
        (_, height, width, _) = self.array.shape
        return self.array[0, u*(height - 1), t*(width - 1)]

    def _spherical_to_internal(self, v):
        phi = np.arctan2(v.y, v.x)
        theta = np.arccos(v.z / v.length)
        return (phi/(2*np.pi) + 0.5, theta/np.pi)
