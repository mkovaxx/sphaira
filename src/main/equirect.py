import numpy as np
from pyrr import Vector3

class Equirect(object):

    @classmethod
    def from_array(self, array):
        return Equirect(array)

    def __init__(self, array):
        assert len(array.shape) == 3
        (height, width, depth) = array.shape
        assert width == 2*height
        assert depth == 4
        self.array = array

    def sample(self, v):
        (t, u) = _spherical_to_internal(v)
        (width, height) = self.array.shape
        return self.array[u*height, t*width]

    def _spherical_to_internal(self, v):
        phi = np.arctan2(v.y, v.x)
        theta = np.arccos(v.z / v.length)
        return (phi/(2*np.pi) + 1, theta/np.pi + 0.5)
