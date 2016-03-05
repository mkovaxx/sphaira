import numpy as np
from OpenGL.GL import *
from pyrr import Vector3

import external


class HealPix(object):

    sampler = None

    @classmethod
    def check_array(cls, array):
        if array.dtype != np.float32:
            return 1
        if array.ndim != 4:
            return 2
        (face_count, height, width, depth) = array.shape
        if depth != 4:
            return 3
        if face_count != 12:
            return 4
        if width != height:
            return 5
        return 0

    @classmethod
    def check_image_shape(cls, width, height):
        if 3*width != 4*height:
            return 1
        return 0

    @classmethod
    def from_array(cls, faces):
        assert cls.check_array(faces) == 0
        return HealPix(faces)

    @classmethod
    def from_image(cls, image):
        assert cls.check_image(image) == 0
        # decompose 4x3 mosaic into healpix faces
        (pos, mid, neg) = [np.hsplit(ring, 4) for ring in np.vsplit(image, 3)]
        array = np.stack(pos + mid + neg)
        return HealPix(array)

    def to_image(self):
        # combine cube map faces into a 3x2 mosaic
        return np.vstack([
            np.hstack([self.array[0], self.array[1], self.array[2], self.array[3]]),
            np.hstack([self.array[4], self.array[5], self.array[6], self.array[7]]),
            np.hstack([self.array[8], self.array[9], self.array[10], self.array[11]]),
        ])

    def to_gl(self, texture_id):
        # enable cube map texturing
        glEnable(GL_TEXTURE_2D)
        # generate and bind texture
        glBindTexture(GL_TEXTURE_2D_ARRAY, texture_id)
        # set up texturing parameters
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_GENERATE_MIPMAP, GL_FALSE)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_BASE_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAX_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        (faces, height, width, depth) = self.array.shape
        glTexImage3D(
            GL_TEXTURE_2D_ARRAY, 0, 4,
            width, height, 12, 0,
            GL_RGBA, GL_FLOAT, self.array,
        )

    def get_glsl_sampler(self):
        return '''
uniform sampler2DArray healpixMap;
const float M_PI = 3.141592653589793238462643383;
vec4 sample(vec3 v) {
    float az = 3 * abs(v.z);
    float phi = 2 * atan(v.y, v.x) / M_PI + 2;
    float t, u, face;
    if (az < 2) {
        float x = phi + 0.5;
        float y = v.z * 0.75;
        float t_i, u_i;
        t = modf(x + y, t_i);
        u = modf(x - y, u_i);
        face = min(t_i, u_i);
        face += 4 * (1 + sign(u_i - t_i) - step(4, face));
    } else {
        float phi_i;
        float phi_f = modf(phi, phi_i);
        float s = sqrt(3 - az);
        float dir = step(v.z, 0);
        t = mix(1 - dir, phi_f, s);
        u = mix(dir, phi_f, s);
        face = phi_i + 8 * dir;
    }
    return texture(healpixMap, vec3(t, u, face));
}
'''

    def bind_glsl_texture(self, texture_id, shader):
        glBindTexture(GL_TEXTURE_2D_ARRAY, texture_id)
        shader.uniformi('healpixMap', texture_id)

    @classmethod
    def from_sphere(cls, sphere, resolution=None):
        pass

    def __init__(self, faces):
        # sanity check
        #assert external.healpix_check(faces) == 0
        self.array = faces
        self.resolution = int(12 * faces.shape[1]**2)
