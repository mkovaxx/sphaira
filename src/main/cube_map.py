import numpy as np
from PIL import Image
from pyrr import Vector3

class CubeMap(object):

    @classmethod
    def from_image(self, image):
        array = np.array(image)
        faces = np.array([array] * 6)
        return CubeMap(faces)

    def __init__(self, faces):
        self.faces = faces
