with import <nixpkgs> {}; {
  sphairaEnv = stdenv.mkDerivation {
    name = "sphaira-env";
    buildInputs = [
      pythonPackages.numpy
      pythonPackages.pillow
      pythonPackages.pyglet
      pythonPackages.pyopengl
      pythonPackages.pyrr
      pythonPackages.pyside
    ];
  };
}
