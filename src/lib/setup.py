from distutils.core import setup, Extension
import numpy.distutils.misc_util

sphaira = Extension(
    'sphaira',
    sources=['sphaira.c'],
    include_dirs=numpy.distutils.misc_util.get_numpy_include_dirs(),
)

setup(
    name='sphaira',
    version='1.0',
    description='Sphaira C library.',
    ext_modules=[sphaira],
)
