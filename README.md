# rubiks-cube
Rubik's Cube OpenGL rendering project

# Installation

This was developed on Mac (so it's possible there may be cross platform issues) using the basic lab setup (that is `pip install`s of `opengl`, `imgui[glfw]`, `glfw` `pillow` etc.).

# Running

To run, start `render.py` with Python 3.6

# Overview

`cube.py` contains the model of the Rubik's cube, along with code related to affecting it (i.e. parsing and performing moves).

`cuberender.py` generates the information used to render the cube, based on the current state (i.e. makes vertices, colours and normals for all of the squares of the cube).

`render.py` contains the rendering logic.

`lab_utils.py` was taken mostly from the set project (and altered somewhat where required).

`fragShader.glsl` and `vertShader.glsl` are what they say on the box: the fragment and vertex shaders.