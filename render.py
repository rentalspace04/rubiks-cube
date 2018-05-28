""" Renders the program """
import sys
import math
from ctypes import sizeof, c_float, c_void_p, c_uint, string_at

from OpenGL.GL import *  #pylint: disable=unused-wildcard-import,wildcard-import
import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer as ImGuiGlfwRenderer
from PIL import Image

import lab_utils as lu
from cube import Cube, CubeMove

# Global variables
g_vert_shader_source = ""
g_frag_shader_source = ""
g_shader_reload_timeout = 1.0
g_shader = None
g_vertex_array = None

vertices = [
    [-0.9, -0.1, 0],
    [-0.9, -0.9, 0],
    [-0.1, -0.9, 0],
    [-0.1, -0.1, 0],
    [0.9, 0.1, 0],
    [0.9, 0.9, 0],
    [0.1, 0.9, 0],
    [0.1, 0.1, 0],
]


def init_resources():
    """ Initialises the program's resources """
    global g_vertex_array
    global vertices
    # Prepare the VAO and VBO
    g_vertex_array = glGenVertexArrays(1)
    glBindVertexArray(g_vertex_array)
    position_buffer = glGenBuffers(1)
    # Prepare and upload the data
    flat_data = lu.flatten(vertices)
    data_buffer = (c_float * len(flat_data))(*flat_data)
    glBindBuffer(GL_ARRAY_BUFFER, position_buffer)
    glBufferData(GL_ARRAY_BUFFER, data_buffer, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)
    # Unbind the buffers
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    reload_shader()


def draw_ui(width, height):
    """ Draws the imgui UI """
    pass


def render_frame(width, height):
    """ Renders the frame """
    # Make openGL use transform from screen space to NDC
    glViewport(0, 0, width, height)
    # Set the clear colour (i.e. background colour)
    glClearColor(0.6, 0.7, 1.0, 1.0)
    # Clear the colour and depth buffers
    glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
    glUseProgram(g_shader)
    glBindVertexArray(g_vertex_array)
    half = int(len(vertices) / 2)
    glDrawArrays(GL_TRIANGLE_FAN, 0, half)
    glDrawArrays(GL_TRIANGLE_FAN, half, half)


def init_glfw_and_resources(title, start_width, start_height):
    """ Adapted from lab5 `magic.py` """
    global g_mousePos

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.SRGB_CAPABLE, 1)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

    window = glfw.create_window(start_width, start_height, title, None, None)
    if not window:
        glfw.terminate()
        sys.exit(1)

    glfw.make_context_current(window)

    print(
        ("--------------------------------------\nOpenGL\n  Vendor: {}\n" +
         "  Renderer: {}\n  Version: {}\n--------------------------------------\n"
        ).format(
            glGetString(GL_VENDOR).decode("utf8"),
            glGetString(GL_RENDERER).decode("utf8"),
            glGetString(GL_VERSION).decode("utf8")),
        flush=True)

    impl = ImGuiGlfwRenderer(window)

    #glDebugMessageCallback(GLDEBUGPROC(debugMessageCallback), None)

    # (although this glEnable(GL_DEBUG_OUTPUT) should not have been needed when
    # using the GLUT_DEBUG flag above...)
    #glEnable(GL_DEBUG_OUTPUT)
    # This ensures that the callback is done in the context of the calling
    # function, which means it will be on the stack in the debugger, which makes it
    # a lot easier to figure out why it happened.
    #glEnable(GL_DEBUG_OUTPUT_SYNCHRONOUS)

    glDisable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    #glEnable(GL_DEPTH_CLAMP)

    init_resources()

    return window, impl


def run_program(title, start_width, start_height):
    """ Adapted from lab5 `magic.py` """
    # Initialise GLFW
    if not glfw.init():
        sys.exit(1)
    window, impl = init_glfw_and_resources(title, start_width, start_height)

    # Add in initial time/mouse pos
    current_time = glfw.get_time()
    prev_mouse_x, prev_mouse_y = glfw.get_cursor_pos(window)

    while not glfw.window_should_close(window):
        prev_time = current_time
        current_time = glfw.get_time()
        dt = current_time - prev_time

        update(dt)

        width, height = glfw.get_framebuffer_size(window)

        imgui.new_frame()
        imgui.set_next_window_position(5.0, 5.0, imgui.FIRST_USE_EVER)

        imgui.begin("UI", 0)

        draw_ui(width, height)
        render_frame(width, height)

        imgui.end()
        imgui.render()

        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()
        impl.process_inputs()


def update(dt):
    global g_shader_reload_timeout
    g_shader_reload_timeout -= dt
    if g_shader_reload_timeout <= 0:
        g_shader_reload_timeout = 1.0
        reload_shader()


def reload_shader():
    """ Tries to reload the shader from source """
    global g_vert_shader_source
    global g_frag_shader_source
    global g_shader
    vert_shader = ""
    frag_shader = ""
    with open("vertShader.glsl") as source:
        vert_shader = source.read()
    with open("fragShader.glsl") as source:
        frag_shader = source.read()
    if vert_shader != g_vert_shader_source or frag_shader != g_frag_shader_source:
        new_shader = lu.buildShader(vert_shader, frag_shader,
                                    {"ndcPositionAttr": 0})
        if new_shader:
            if g_shader:
                glDeleteProgram(g_shader)
            g_shader = new_shader
            print("Reloaded shader, ok!")
            g_frag_shader_source = frag_shader
            g_vert_shader_source = vert_shader


if __name__ == "__main__":
    run_program("Rubik's Cube", 640, 640)
