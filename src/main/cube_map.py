import numpy as np
from pyrr import Vector3

class CubeMap(object):

    @classmethod
    def from_array(cls, array):
        faces = np.array([array] * 6)
        return CubeMap(faces)

    @classmethod
    def from_sphere(cls, sphere):
        projs = [
            lambda t, u: Vector3([+1, t, u]),
            lambda t, u: Vector3([-1, t, u]),
            lambda t, u: Vector3([u, -1, t]),
            lambda t, u: Vector3([u, +1, t]),
            lambda t, u: Vector3([t, u, +1]),
            lambda t, u: Vector3([t, u, -1]),
        ]
        size = 128
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
        self.faces = faces
