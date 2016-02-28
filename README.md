sphaira
=======

Open-source toolset for spherical imaging.

## Version History

### 0.3.3

#### view

- lower requirements to OpenGL 2.1 and GLSL 120
- log OpenGL and GLSL version info for the acquired context

### 0.3.2

#### view

- add zoom
- fix horizontal alignment of checkboxes on the Layer UI

### 0.3.1

#### view

- add Layer memory usage indicator
- allow invocation without inputs

### 0.3.0

#### view

- switch to PySide for graphical UI
- layers, layer list view
- per-layer controls: visibility, alpha, moving, orientation, file name
- layer list controls: drag and drop, add (open file) & remove layers

### 0.2.2

#### lib

- support for multiple image formats via Pillow
- auto-detect projection based on aspect ratio
- convert between projections
- conversion code complexity is O(n) instead of O(n^2) in number of projections
- supported projections: Equirect, CubeMap

#### view

- simple command-line and graphical UI using Pyglet and OpenGL
- quaternion based orientation
- GLSL based back-projection

#### convert

- simple command-line UI
- switches for overriding input and output projections
