import numpy as np
from pyrr import Vector3

import lib.sphaira as sphaira


class Equirect(object):

    sampler = sphaira.equirect_get_sampler()

    @classmethod
    def check(cls, array):
        if array.dtype != np.float32:
            return 1
        if len(array.shape) != 3:
            return 2
        (height, width, depth) = array.shape
        if depth != 4:
            return 3
        if width != 2*height:
            return 4
        return 0

    @classmethod
    def from_array(self, array):
        return Equirect(array)

    def __init__(self, array):
        assert Equirect.check(array) == 0
        assert sphaira.equirect_check(array) == 0
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
