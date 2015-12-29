from distutils.core import setup, Extension
import numpy.distutils.misc_util

setup(
    name = 'sphaira',
    version = '0.1',
    description = 'Work with spherical data.',
    url = 'http://sphaira.org',
    author = 'Mate Kovacs',
    author_email = 'mkovaxx@gmail.com',
    license = 'AllRightsReserved',
    packages = [
        'sphaira',
    ],
    ext_modules = [
        Extension(
            'sphaira.external',
            ['sphaira/external.c'],
            include_dirs = numpy.distutils.misc_util.get_numpy_include_dirs(),
        ),
    ],
    install_requires = [
        'pillow',
        'pyglet',
        'pyrr',
    ],
)
