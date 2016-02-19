sphaira
=======

Utility and library for viewing and editing spherical images.

## Version History

### 0.2.2

#### lib

- support for multiple image formats via Pillow
- auto-detect projection based on aspect ratio
- convert between projections
- conversion code complexity is O(n) instead of O(n^2) in number of projections
- supported projections: Equirect, CubeMap

#### viewer

- simple command-line and graphical UI using Pyglet and OpenGL
- quaternion based orientation
- GLSL based back-projection

#### convert

- simple command-line UI
- switches for overriding input and output projections
