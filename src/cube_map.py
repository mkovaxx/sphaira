import numpy as np
from pyrr import Vector3

import lib.sphaira as sphaira


class CubeMap(object):

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
        size = 8
        faces = np.zeros((6, size, size, 4), dtype=np.float32)
        for (face, proj) in enumerate(projs):
            for y in xrange(size):
                for x in xrange(size):
                    v = proj(2.0*x/size - 1, 2.0*y/size - 1)
                    faces[face, y, x] = sphere.sample(v)
        return CubeMap(faces)

    def __init__(self, faces):
        assert len(faces.shape) == 4
        (face_count, width, height, depth) = faces.shape
        assert face_count == 6
        assert width == height
        assert depth == 4
        assert sphaira.cube_map_check(faces) == 0
        self.faces = faces
