with import <nixpkgs> {}; {
  sphairaEnv = stdenv.mkDerivation {
    name = "sphaira-env";
    buildInputs = [
      pythonPackages.numpy
      pythonPackages.pillow
      pythonPackages.pyglet
      pythonPackages.pyrr
      pythonPackages.pyside
    ];
  };
}
