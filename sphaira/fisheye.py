import numpy as np
from OpenGL.GL import *
from pyrr import Vector3

import external

# hard-wired FOV for the BublCam
FISHEYE_FOV = 160.0*np.pi / 180.0


class Fisheye(object):

    sampler = external.fisheye_get_sampler()

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
        if width != height:
            return 5
        return 0

    @classmethod
    def check_image_shape(cls, width, height):
        if width != height:
            return 1
        return 0

    @classmethod
    def from_array(cls, array):
        assert cls.check_array(array) == 0
        return Fisheye(array)

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
        shader = '''
uniform sampler2D fishMap;
const float M_PI = 3.141592653589793238462643383;
const float FOV = %f;
vec4 sample(vec3 v) {
    float phi = atan(v.y, v.x);
    float theta = atan(sqrt(v.x*v.x + v.y*v.y), v.z);
    float r = theta / FOV;
    float t = 0.5 + r*cos(phi);
    float u = 0.5 + r*sin(phi);
    return r > 0.5 ? vec4(0.0) : texture2D(fishMap, vec2(t, u));
}
'''
        return shader % FISHEYE_FOV

    def bind_glsl_texture(self, texture_id, shader):
        glBindTexture(GL_TEXTURE_2D, texture_id)
        shader.uniformi('fishMap', texture_id)

    @classmethod
    def from_sphere(cls, sphere, resolution=None):
        resolution = resolution or sphere.resolution
        width = int(np.sqrt(resolution))
        height = width
        faces = np.zeros((1, height, width, 4), dtype=np.float32)
        external.fisheye_assign(faces, sphere.array, sphere.sampler)
        return Fisheye(faces)

    def __init__(self, array):
        # sanity check
        assert external.fisheye_check(array) == 0
        self.array = array
        self.resolution = int(array.shape[1]**2)

    def sample(self, v):
        (t, u) = self._spherical_to_internal(v)
        (_, height, width, _) = self.array.shape
        return self.array[0, u*(height - 1), t*(width - 1)]

    def _spherical_to_internal(self, v):
        phi = np.arctan2(v.y, v.x)
        theta = np.arctan2(np.sqrt(v.x*v.x + v.y*v.y), v.z)
        r = theta / FISHEYE_FOV
        return (0.5 + r*cos(phi), 0.5 + r*sin(phi))
