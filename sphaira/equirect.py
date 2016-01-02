import numpy as np
from pyglet.gl import *
from pyrr import Vector3

import external


class Equirect(object):

    sampler = external.equirect_get_sampler()

    @classmethod
    def check_array(cls, array):
        if array.dtype != np.float32:
            return 1
        if array.ndim != 3:
            return 2
        (height, width, depth) = array.shape
        if depth != 4:
            return 3
        if width != 2*height:
            return 4
        return 0

    @classmethod
    def check_image(cls, image):
        return cls.check_array(image)

    @classmethod
    def from_array(cls, array):
        assert cls.check_array(array) == 0
        return Equirect(array)

    @classmethod
    def from_image(cls, image):
        return cls.from_array(image)

    def to_image(self):
        return self.array

    def to_gl(self, texture_id):
        # enable cube map texturing
        glEnable(GL_TEXTURE_2D)
        # generate and bind texture
        glBindTexture(GL_TEXTURE_2D, texture_id)
        # set up texturing parameters
        glTexParameteri(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_FALSE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        (height, width, depth) = self.array.shape
        data = self.array.ctypes.data
        glTexImage2D(
            GL_TEXTURE_2D, 0,
            GL_RGBA, width, height, 0,
            GL_RGBA, GL_FLOAT, data
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
    return texture(rectMap, vec2(t, u));
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
        faces = np.zeros((height, width, 4), dtype=np.float32)
        external.equirect_assign(faces, sphere.array, sphere.sampler)
        return Equirect(faces)

    def __init__(self, array):
        # sanity check
        assert external.equirect_check(array) == 0
        self.array = array
        self.resolution = int(2 * array.shape[1]**2)

    def sample(self, v):
        (t, u) = self._spherical_to_internal(v)
        (height, width, _) = self.array.shape
        return self.array[u*(height - 1), t*(width - 1)]

    def _spherical_to_internal(self, v):
        phi = np.arctan2(v.y, v.x)
        theta = np.arccos(v.z / v.length)
        return (phi/(2*np.pi) + 0.5, theta/np.pi)
