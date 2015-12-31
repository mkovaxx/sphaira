import numpy as np
from pyrr import Vector3

import external


class CubeMap(object):

    sampler = external.cube_map_get_sampler()

    @classmethod
    def check_array(cls, array):
        if array.dtype != np.float32:
            return 1
        if array.ndim != 4:
            return 2
        (face_count, height, width, depth) = array.shape
        if depth != 4:
            return 3
        if face_count != 6:
            return 4
        if width != height:
            return 5
        return 0

    @classmethod
    def check_image(cls, image):
        if image.dtype != np.float32:
            return 1
        if image.ndim != 3:
            return 2
        (height, width, depth) = image.shape
        if depth != 4:
            return 3
        if 2*width != 3*height:
            return 4
        return 0

    @classmethod
    def from_array(cls, faces):
        assert cls.check_array(faces) == 0
        return CubeMap(faces)

    @classmethod
    def from_image(cls, image):
        assert cls.check_image(image) == 0
        # decompose 3x2 mosaic into cube map faces
        (pos, neg) = np.vsplit(image, 2)
        (xp, yp, zp) = np.hsplit(pos, 3)
        (xn, yn, zn) = np.hsplit(neg, 3)
        array = np.stack([xp, xn, yp, yn, zp, zn])
        return CubeMap(array)

    def to_image(self):
        # combine cube map faces into a 3x2 mosaic
        return np.vstack([
            np.hstack([self.array[0], self.array[2], self.array[4]]),
            np.hstack([self.array[1], self.array[3], self.array[5]]),
        ])

    @classmethod
    def from_sphere(cls, sphere, resolution=None):
        resolution = resolution or sphere.resolution
        size = int(np.sqrt(resolution / 6))
        faces = np.zeros((6, size, size, 4), dtype=np.float32)
        external.cube_map_assign(faces, sphere.array, sphere.sampler)
        return CubeMap(faces)

    def __init__(self, faces):
        # sanity check
        assert external.cube_map_check(faces) == 0
        self.array = faces
        self.resolution = int(6 * faces.shape[1]**2)
