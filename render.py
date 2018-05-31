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
from cuberender import CubeRenderer

import magic

import cuberender as cr

# Global variables
g_vert_shader_source = ""
g_frag_shader_source = ""
g_shader_reload_timeout = 1.0
g_shader = None
g_vertex_array = None
g_coordinateSystemModel = None
g_cube = Cube()
g_squares = []
g_square_colors = []
g_square_normals = []
g_cube_move = -1
g_texture_id = None

g_light = [2.5, 10.0, 10.0]
g_cam = [5.0, 5.0, 5.0]
g_light_color = [0.7, 0.7, 0.75]
g_ambi_color = [0.15, 0.15, 0.18]
g_spec_color = [0.25, 0.25, 0.22]


def make_squares():
    """ Makes the vertices to draw """
    global g_cube
    global g_squares
    global g_square_colors
    global g_vertex_array
    global g_square_normals
    # Prepare the Squares with the cube renderer
    cube_renderer = CubeRenderer(g_cube)
    g_squares = cube_renderer.get_squares()
    g_square_colors = cube_renderer.get_colors()
    g_square_normals = cube_renderer.get_normals()
    # Prepare the VAO and VBO
    g_vertex_array = glGenVertexArrays(1)
    glBindVertexArray(g_vertex_array)
    position_buffer = glGenBuffers(1)
    # Prepare and upload the data
    flat_data = lu.flatten(g_squares)
    data_buffer = (c_float * len(flat_data))(*flat_data)
    glBindBuffer(GL_ARRAY_BUFFER, position_buffer)
    glBufferData(GL_ARRAY_BUFFER, data_buffer, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)


def make_texture_coords():
    """ Makes and buffers the list of texture coords """
    texture_coords = []
    for _ in range(len(g_square_colors)):
        texture_coords.extend([
            [0.0, 0.0],
            [0.0, 1.0],
            [1.0, 1.0],
            [1.0, 0.0],
        ])
    tex_coord_buffer = glGenBuffers(1)
    flat_data = magic.flatten(texture_coords)
    data_buffer = (c_float * len(flat_data))(*flat_data)
    glBindBuffer(GL_ARRAY_BUFFER, tex_coord_buffer)
    glBufferData(GL_ARRAY_BUFFER, data_buffer, GL_STATIC_DRAW)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(1)
    glBindAttribLocation(g_shader, 1, "textureCoord")
    # Unbind the buffers
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)


def render_frame(width, height):
    """ Renders the frame """
    global g_shader
    global g_squares
    global g_square_colors
    global g_square_normals
    global g_cam
    global g_light
    global g_light_color
    global g_ambi_color
    global g_spec_color
    # Make the camera position
    eye_pos = g_cam
    look_at = [1.5, 1.5, -1.5]
    up_dir = [0, 1, 0]
    y_fov = 45

    # Light constants
    light_color = g_light_color
    light_position = g_light
    ambient_light = g_ambi_color
    specular_light = g_spec_color

    world_to_view = lu.make_lookAt(eye_pos, look_at, up_dir)
    view_to_clip = lu.make_perspective(y_fov, width / height, 0.1, 50)
    world_to_clip = view_to_clip * world_to_view
    model_to_view_normal = lu.inverse(lu.transpose(lu.Mat3(world_to_view)))

    # Make openGL use transform from screen space to NDC
    glViewport(0, 0, width, height)
    # Set the clear colour (i.e. background colour)
    glClearColor(0.7, 0.8, 1.0, 1.0)

    make_squares()
    make_texture_coords()

    # Unbind the buffers
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    # Clear the colour and depth buffers
    glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

    # Buffer the world to clip transform matrix
    tfm_uniform_index = glGetUniformLocation(g_shader, "worldToClipTfm")
    glUseProgram(g_shader)
    glUniformMatrix4fv(tfm_uniform_index, 1, GL_TRUE, world_to_clip.getData())
    glBindVertexArray(g_vertex_array)

    model_uniform_index = glGetUniformLocation(g_shader, "modelToView")
    glUseProgram(g_shader)
    glUniformMatrix4fv(model_uniform_index, 1, GL_TRUE, world_to_view.getData())

    norm_uniform_index = glGetUniformLocation(g_shader, "modelToViewNormal")
    glUseProgram(g_shader)
    glUniformMatrix3fv(norm_uniform_index, 1, GL_TRUE,
                       model_to_view_normal.getData())

    lu.setUniform(g_shader, "lightColourAndIntensity", light_color)
    lu.setUniform(g_shader, "viewSpaceLightPosition", light_position)
    lu.setUniform(g_shader, "ambientLightColourAndIntensity", ambient_light)
    lu.setUniform(g_shader, "materialSpecular", specular_light)

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, g_texture_id)
    loc = glGetUniformLocation(g_shader, "plasticTexture")
    glUniform1i(loc, 0)

    for i in range(int(len(g_squares) / 4)):
        lu.setUniform(g_shader, "squareColorIndex", g_square_colors[i])
        lu.setUniform(g_shader, "squareNormal", g_square_normals[i])
        glDrawArrays(GL_TRIANGLE_FAN, i * 4, 4)

    magic.drawCoordinateSystem(view_to_clip, world_to_view)


def init_resources():
    """ Initialises the program's resources """
    global g_texture_id
    with Image.open("data/background-cement-concrete-242236.jpg") as image:
        g_texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, g_texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.size[0], image.size[1], 0,
                     GL_RGBA, GL_UNSIGNED_BYTE,
                     image.tobytes("raw", "RGBX", 0, -1))
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glBindTexture(GL_TEXTURE_2D, 0)
    reload_shader()


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

    magic.load_coord_sys()

    return window, impl


def setup_fbo(msaa_fbo,
              fbo_width,
              fbo_height,
              num_samples,
              color_render_buffer=0,
              depth_render_buffer=0):
    """ Adapted from lab 5 `magic.py` """
    if not color_render_buffer:
        color_render_buffer, depth_render_buffer = glGenRenderbuffers(2)
    glBindRenderbuffer(GL_RENDERBUFFER, color_render_buffer)
    glRenderbufferStorageMultisample(GL_RENDERBUFFER, num_samples, GL_RGB8,
                                     fbo_width, fbo_height)
    glBindRenderbuffer(GL_RENDERBUFFER, depth_render_buffer)
    glRenderbufferStorageMultisample(GL_RENDERBUFFER, num_samples,
                                     GL_DEPTH_COMPONENT32, fbo_width,
                                     fbo_height)
    glBindRenderbuffer(GL_RENDERBUFFER, 0)

    glBindFramebuffer(GL_FRAMEBUFFER, msaa_fbo)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
                              GL_RENDERBUFFER, color_render_buffer)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT,
                              GL_RENDERBUFFER, depth_render_buffer)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    return color_render_buffer, depth_render_buffer


def run_program(title, start_width, start_height):
    """ Adapted from lab5 `magic.py` """
    # Initialise GLFW
    if not glfw.init():
        sys.exit(1)
    window, impl = init_glfw_and_resources(title, start_width, start_height)

    # Add in initial time/mouse pos
    current_time = glfw.get_time()
    prev_mouse_x, prev_mouse_y = glfw.get_cursor_pos(window)

    # Create the MSAA FBO
    msaa_fbo = glGenFramebuffers(1)
    fbo_width = start_width
    fbo_height = start_height
    num_samples = 8
    color_render_buffer, depth_render_buffer = setup_fbo(
        msaa_fbo, fbo_width, fbo_height, num_samples)

    while not glfw.window_should_close(window):
        prev_time = current_time
        current_time = glfw.get_time()
        dt = current_time - prev_time

        update(dt)

        width, height = glfw.get_framebuffer_size(window)

        if fbo_width != width or fbo_height != height:
            fbo_width = max(width, fbo_width)
            fbo_height = max(height, fbo_height)
            color_render_buffer, depth_render_buffer = setup_fbo(
                msaa_fbo, fbo_width, fbo_height, num_samples,
                color_render_buffer, depth_render_buffer)

        glBindFramebuffer(GL_FRAMEBUFFER, msaa_fbo)

        render_frame(width, height)

        # Reset the frame buffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glBindFramebuffer(GL_READ_FRAMEBUFFER, msaa_fbo)
        # Copy the data from the render buffers attached to the MSAA FBO into the default FBO
        glBlitFramebuffer(0, 0, width, height, 0, 0, width, height,
                          GL_COLOR_BUFFER_BIT, GL_LINEAR)
        # Reset the 'GL_READ_FRAMEBUFFER' binding point, just in case...
        glBindFramebuffer(GL_READ_FRAMEBUFFER, 0)

        # Draw ImGui UI
        imgui.new_frame()
        imgui.set_next_window_position(5.0, 5.0, imgui.FIRST_USE_EVER)

        imgui.begin("Rubiks Cube Controls", 0)

        draw_ui(width, height)

        imgui.end()
        imgui.render()

        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()
        impl.process_inputs()


def add_move_buttons(move_name, move_func, btn_w):
    """
    Adds buttons for move, move2 and move'
    Performs moves if button pressed
    """
    if imgui.button(move_name, btn_w):
        move_func()
    imgui.same_line()
    if imgui.button(move_name + "2", btn_w):
        move_func()
        move_func()
    imgui.same_line()
    if imgui.button(move_name + "'", btn_w):
        move_func()
        move_func()
        move_func()


def draw_ui(width, height):
    """ Draws the imgui UI """
    global g_cube
    global g_cam
    global g_light
    global g_light_color
    global g_ambi_color
    global g_spec_color

    btn_w = 25
    imgui.set_window_font_scale(1.2)

    expanded, _ = imgui.collapsing_header("Controls", True)
    if expanded:
        # Rubiks Cube Moves
        imgui.begin_group()
        imgui.text("Moves:")

        add_move_buttons("F", g_cube.move_f, btn_w)
        imgui.same_line(spacing=20)
        add_move_buttons("B", g_cube.move_b, btn_w)
        add_move_buttons("R", g_cube.move_r, btn_w)
        imgui.same_line(spacing=20)
        add_move_buttons("L", g_cube.move_l, btn_w)
        add_move_buttons("U", g_cube.move_u, btn_w)
        imgui.same_line(spacing=20)
        add_move_buttons("D", g_cube.move_d, btn_w)

        imgui.end_group()

        imgui.same_line(spacing=50)

        # Cube Rotations
        imgui.begin_group()
        imgui.text("Rotations:")
        add_move_buttons("x", g_cube.rotate_x, btn_w)
        add_move_buttons("y", g_cube.rotate_y, btn_w)
        add_move_buttons("z", g_cube.rotate_z, btn_w)
        imgui.end_group()

    expanded, _ = imgui.collapsing_header("View Settings", True)
    if expanded:
        _, g_cam = imgui.slider_float3(
            "Camera Position", *g_cam, min_value=-20.0, max_value=20.0)
        _, g_light = imgui.slider_float3(
            "Light Position", *g_light, min_value=-20.0, max_value=20.0)
        _, g_light_color = imgui.color_edit3("Light Colour", *g_light_color)
        _, g_ambi_color = imgui.color_edit3("Ambient Light Colour",
                                            *g_ambi_color)
        _, g_spec_color = imgui.color_edit3("Specular Light Colour",
                                            *g_spec_color)
        g_cam = list(g_cam)
        g_light = list(g_light)
        g_light_color = list(g_light_color)
        g_ambi_color = list(g_ambi_color)
        g_spec_color = list(g_spec_color)


def update(dt):
    global g_shader_reload_timeout
    global g_cube
    global g_cube_move
    g_shader_reload_timeout -= dt
    if g_shader_reload_timeout <= 0:
        g_shader_reload_timeout = 5.0
        reload_shader()
        if g_cube_move == 0:
            g_cube.move_r()
            g_cube_move = 1
        elif g_cube_move == 1:
            g_cube.move_u()
            g_cube_move = 2
        elif g_cube_move == 2:
            g_cube.move_r()
            g_cube.move_r()
            g_cube.move_r()
            g_cube_move = 3
        elif g_cube_move == 3:
            g_cube.move_u()
            g_cube.move_u()
            g_cube.move_u()
            g_cube_move = 0


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
