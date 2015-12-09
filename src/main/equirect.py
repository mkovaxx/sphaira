import numpy as np
from pyrr import Vector3

lib = ctypes.cdll.LoadLibrary('./libsphaira.so')
equirect_sample = lib.equirect_sample

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
        (t, u) = self._spherical_to_internal(v)
        (height, width, _) = self.array.shape
        return self.array[u*(height - 1), t*(width - 1)]

    def _spherical_to_internal(self, v):
        phi = np.arctan2(v.y, v.x)
        theta = np.arccos(v.z / v.length)
        return (phi/(2*np.pi) + 0.5, theta/np.pi)
