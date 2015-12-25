import numpy as np
from pyrr import Vector3

import lib.sphaira as sphaira


class CubeMap(object):

    @classmethod
    def check(cls, array):
        if array.dtype != np.float32:
            return 1
        if len(array.shape) != 4:
            return 2
        (face_count, width, height, depth) = array.shape
        if depth != 4:
            return 4
        if face_count != 6:
            return 2
        if width != height:
            return 3
        return 0

    @classmethod
    def from_array(cls, array):
        faces = np.array([array] * 6)
        return CubeMap(faces)

    @classmethod
    def from_sphere(cls, sphere):
        size = 1024
        faces = np.zeros((6, size, size, 4), dtype=np.float32)
        sphaira.cube_map_assign(faces, sphere.array, sphere.sampler)
        return CubeMap(faces)

    def __init__(self, faces):
        assert CubeMap.check(faces) == 0
        assert sphaira.cube_map_check(faces) == 0
        self.array = faces
