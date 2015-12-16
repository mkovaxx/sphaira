let
  pkgs = import <nixpkgs> {};
in
{ stdenv ? pkgs.stdenv
, python ? pkgs.python
, pillow ? pkgs.pythonPackages.pillow
, pyglet ? pkgs.pythonPackages.pyglet
, pyrr ? pkgs.pythonPackages.pyrr
}:

stdenv.mkDerivation {
  name = "python-nix";
  version = "0.1.0.0";
  src = ./.;
  buildInputs = [
    python
    pyglet
    pyrr
  ];
}
