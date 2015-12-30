import argparse
import numpy as np
from PIL import Image

from cube_map import CubeMap
from equirect import Equirect

def load_sphere(file_name, projection):
    image = Image.open(file_name).convert('RGBA')
    array = np.array(image, dtype=np.float32) / 255
    if projection == CubeMap:
        # decompose 3x2 mosaic into cube map faces
        (pos, neg) = np.vsplit(array, 2)
        (xp, yp, zp) = np.hsplit(pos, 3)
        (xn, yn, zn) = np.hsplit(neg, 3)
        array = np.stack([xp, xn, yp, yn, zp, zn])
    sphere = projection.from_array(array)
    return sphere


def save_sphere(sphere, file_name):
    array = np.array(sphere.array * 255, dtype=np.uint8)
    if array.ndim == 4:
        # combine cube map faces into a 3x2 mosaic
        array = np.vstack([
            np.hstack([array[0], array[2], array[4]]),
            np.hstack([array[1], array[3], array[5]]),
        ])
    image = Image.fromarray(array)
    image.save(file_name)


def main():
    parser = argparse.ArgumentParser(
        prog='convert',
        description='Sphaira converter for spherical data.',
    )
    parser.add_argument('input', help='INPUT')
    parser.add_argument('output', help='OUTPUT')
    args = parser.parse_args()
    sphere = load_sphere(args.input, projection=CubeMap)
    # sphere2 = CubeMap.from_sphere(sphere)
    save_sphere(sphere, args.output)


if __name__ == '__main__':
    main()
