import numpy as np
from pyrr import Vector3

class CubeMap(object):

    @classmethod
    def from_array(self, array):
        faces = np.array([array] * 6)
        return CubeMap(faces)

    def __init__(self, faces):
        assert len(faces.shape) == 4
        (face_count, width, height, depth) = faces.shape
        assert face_count == 6
        assert width == height
        assert depth == 4
        self.faces = faces
