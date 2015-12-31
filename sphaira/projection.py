import numpy as np
from PIL import Image

from cube_map import CubeMap
from equirect import Equirect

PROJECTION_BY_NAME = {projection.__name__: projection for projection in {
    CubeMap,
    Equirect,
}}


def convert_sphere(sphere, projection):
    return (
        sphere if isinstance(sphere, projection)
        else projection.from_sphere(sphere)
    )


def load_sphere(file_name, projection):
    image = Image.open(file_name).convert('RGBA')
    array = np.array(image, dtype=np.float32) / 255
    if not projection:
        formats = detect_format(array)
        if len(formats) < 1:
            raise LookupError('Unknown format.')
        if len(formats) > 1:
            raise LookupError('Ambiguous format: %s.' % formats)
        projection = formats[0]
    sphere = projection.from_image(array)
    return sphere


def save_sphere(file_name, sphere):
    array = np.array(sphere.to_image() * 255, dtype=np.uint8)
    image = Image.fromarray(array)
    image.save(file_name)


def detect_format(image):
    compatible_projections = []
    for projection in PROJECTION_BY_NAME.itervalues():
        if projection.check_image(image) == 0:
            compatible_projections.append(projection)
    return compatible_projections


def get_format(name):
    return PROJECTION_BY_NAME.get(name)
