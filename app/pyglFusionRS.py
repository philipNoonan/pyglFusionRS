import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from glob import glob
import cv2
import re
import os
import imgui
from imgui.integrations.glfw import GlfwRenderer
from pathlib import Path

import pyrealsense2 as rs


def main():

    # initialize glfw
    if not glfw.init():
        return
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    #creating the window
    window = glfw.create_window(1600, 900, "PyGLFusion", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    pipeline = rs.pipeline()
    pipeline.start()


    imgui.create_context()
    impl = GlfwRenderer(window)

    while not glfw.window_should_close(window):

        glfw.poll_events()
        impl.process_inputs()
        imgui.new_frame()

        # Create a pipeline object. This object configures the streaming camera and owns it's handle
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue
        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        cv2.imshow("depth", depth_colormap)
        cv2.imshow("color", color_image)

        cv2.waitKey(1)



        imgui.render()

        impl.render(imgui.get_draw_data())

        glfw.swap_buffers(window)        

    glfw.terminate()
    


if __name__ == "__main__":
    main()    