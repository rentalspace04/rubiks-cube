import sys
import math
from OpenGL.GL import *
import imgui
import glfw
from imgui.integrations.glfw import GlfwRenderer as ImGuiGlfwRenderer
from ctypes import sizeof, c_float, c_void_p, c_uint, string_at
from PIL import Image

import lab_utils as lu
from cube import Cube, CubeMove

def initResources():
    pass

def drawUi(width, height):
    pass

def renderFrame(width, height):
    # Make openGL use transform from screen space to NDC
    glViewport(0, 0, width, height)
    # Set the clear colour (i.e. background colour) 
    glClearColor(0.6, 0.7, 1.0, 1.0)
    # Clear the colour and depth buffers
    glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

def initGlFwAndResources(title, startWidth, startHeight, initResources):
    """ Adapted from lab5 `magic.py` """
    global g_mousePos

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.SRGB_CAPABLE, 1)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)


    window = glfw.create_window(startWidth, startHeight, title, None, None)
    if not window:
        glfw.terminate()
        sys.exit(1)

    glfw.make_context_current(window)


    print("--------------------------------------\nOpenGL\n  Vendor: %s\n  Renderer: %s\n  Version: %s\n--------------------------------------\n" % (glGetString(GL_VENDOR).decode("utf8"), glGetString(GL_RENDERER).decode("utf8"), glGetString(GL_VERSION).decode("utf8")), flush=True)

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

    if initResources:
        initResources()

    return window,impl

def runProgram(title, startWidth, startHeight, renderFrame, initResources = None, drawUi = None, update = None):
    """ Adapted from lab5 `magic.py` """
    # Initialise GLFW
    if not glfw.init():
        sys.exit(1)
    window, impl = initGlFwAndResources(title, startWidth, startHeight, initResources)
    
    # Add in initial time/mouse pos
    currentTime = glfw.get_time()
    prevMouseX,prevMouseY = glfw.get_cursor_pos(window)

    while not glfw.window_should_close(window):
        prevTime = currentTime
        currentTime = glfw.get_time()
        dt = currentTime - prevTime

        width, height = glfw.get_framebuffer_size(window)

        imgui.new_frame()

        imgui.set_next_window_position(5.0, 5.0, imgui.FIRST_USE_EVER)
        #imgui.set_next_window_size(400.0, 620.0, imgui.FIRST_USE_EVER)
        imgui.begin("UI", 0)

        if drawUi:
            drawUi(width, height)

        renderFrame(width, height)
    
        #mgui.show_test_window()

        imgui.end()

        imgui.render()
        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()
        impl.process_inputs()



if __name__ == "__main__":
    runProgram("Rubik's Cube", 640, 640, renderFrame, initResources, drawUi)