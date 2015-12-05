import numpy as np
from pyrr import Vector3

class EquiRect(object):

    @classmethod
    def from_array(self, array):
        return EquiRect(array)

    def __init__(self, array):
        assert len(array.shape) == 3
        (width, height, depth) = array.shape
        assert width == 2*height
        self.array = array
