import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "sphaira",
    version = "0.0.1",
    packages = find_packages('src'),
    package_dir = {'':'src'},
    install_requires = ['pyglet', 'pyrr'],
    entry_points = {
        'gui_scripts': [
            'sphaira = main:main',
        ]
    },
    package_data = {
        'resources': '*',
    },
    author = "Mate Kovacs",
    author_email = "mkovaxx@gmail.com",
    description = ("View and edit spherical images."),
    license = "AllRightsReserved",
    keywords = "spherical panorama imaging",
    url = "http://sphaira.org",
    long_description = read('README.md'),
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: Other/Proprietary License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Topic :: Multimedia",
    ],
)
