import argparse
import numpy as np
from PIL import Image

from cube_map import CubeMap
from equirect import Equirect

def load_sphere(file_name, projection):
    image = Image.open(file_name).convert('RGBA')
    array = np.array(image, dtype=np.float32) / 255
    sphere = projection.from_image(array)
    return sphere


def save_sphere(sphere, file_name):
    array = np.array(sphere.to_image() * 255, dtype=np.uint8)
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
    sphere2 = Equirect.from_sphere(sphere)
    save_sphere(sphere2, args.output)


if __name__ == '__main__':
    main()
