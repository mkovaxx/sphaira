import numpy as np
from pyrr import Vector3

import external


class Equirect(object):

    sampler = external.equirect_get_sampler()

    @classmethod
    def check(cls, array):
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
    def from_array(cls, array):
        return Equirect(array)

    @classmethod
    def from_image(cls, image):
        return Equirect(image)

    def to_image(self):
        return self.array

    @classmethod
    def from_sphere(cls, sphere, resolution=None):
        resolution = resolution or sphere.resolution
        height = int(np.sqrt(resolution / 2))
        width = 2*height
        faces = np.zeros((height, width, 4), dtype=np.float32)
        external.equirect_assign(faces, sphere.array, sphere.sampler)
        return Equirect(faces)

    def __init__(self, array):
        assert Equirect.check(array) == 0
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
