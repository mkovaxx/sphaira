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
        projs = [
            lambda t, u: Vector3([+1, -u, -t]), # +X
            lambda t, u: Vector3([-1, -u, +t]), # -X
            lambda t, u: Vector3([+t, +1, +u]), # +Y
            lambda t, u: Vector3([+t, -1, -u]), # -Y
            lambda t, u: Vector3([+t, -u, +1]), # +Z
            lambda t, u: Vector3([-t, -u, -1]), # -Z
        ]
        size = 1024
        faces = np.zeros((6, size, size, 4), dtype=np.float32)
        sphaira.cube_map_assign(faces, sphere.array, sphere.sampler)
        # for (face, proj) in enumerate(projs):
        #     for y in xrange(size):
        #         for x in xrange(size):
        #             v = proj(2.0*x/size - 1, 2.0*y/size - 1)
        #             faces[face, y, x] = sphere.sample(v)
        return CubeMap(faces)

    def __init__(self, faces):
        assert CubeMap.check(faces) == 0
        assert sphaira.cube_map_check(faces) == 0
        self.array = faces
