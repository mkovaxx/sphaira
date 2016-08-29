import numpy as np
from PIL import Image

from cube_map import CubeMap
from equirect import Equirect
from fisheye import Fisheye
from healpix import HealPix

PROJECTION_BY_NAME = {projection.__name__: projection for projection in {
    CubeMap,
    Equirect,
    Fisheye,
    HealPix,
}}


def convert_sphere(sphere, projection):
    return (
        sphere if projection is None or isinstance(sphere, projection)
        else projection.from_sphere(sphere)
    )


def load_sphere(file_name, projection):
    image = Image.open(file_name)
    width = image.width
    height = image.height
    if projection is not None:
        if projection.check_image_shape(width, height) != 0:
            raise RuntimeError(
                'The contents of %s are not in %s format.'
                % (file_name, projection.__name__)
            )
    else:
        formats = detect_format(width, height)
        if len(formats) < 1:
            raise LookupError('Unknown format.')
        if len(formats) > 1:
            raise LookupError('Ambiguous format: %s.' % formats)
        projection = formats[0]
    normalized_image = np.array(image.convert('RGBA'), dtype=np.float32) / 255
    sphere = projection.from_image(normalized_image)
    return sphere


def save_sphere(file_name, sphere):
    array = np.array(sphere.to_image() * 255, dtype=np.uint8)
    image = Image.fromarray(array)
    image.save(file_name)


def detect_format(width, height):
    compatible_projections = []
    for projection in PROJECTION_BY_NAME.itervalues():
        if projection.check_image_shape(width, height) == 0:
            compatible_projections.append(projection)
    return compatible_projections


def get_format(name):
    return PROJECTION_BY_NAME.get(name)
