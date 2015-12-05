import numpy as np
from pyrr import Vector3

class CubeMap(object):

    @classmethod
    def from_array(self, array):
        faces = np.array([array] * 6)
        return CubeMap(faces)

    def __init__(self, faces):
        self.faces = faces
