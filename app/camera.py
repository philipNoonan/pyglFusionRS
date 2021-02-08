import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import glm
import numpy as np
import os

import pyrealsense2 as rs

def find_cameras(ctx):
    devices = ctx.devices

    data = {}

    for dev in devices:
        name = dev.get_info(rs.camera_info.name)
        serial_number = dev.get_info(rs.camera_info.serial_number)

        data[name] = serial_number
        print(
            f"found camera with name: {name} and serial number: {serial_number}"
        )

    return data

def start(useLiveCamera):
    global pipeline
    global depth_sensor
    pipeline = rs.pipeline()

    context = rs.context()
    camera_data = find_cameras(context)

    config = rs.config()

    if useLiveCamera == False:
        rs.config.enable_device_from_file(config, "C:\\Data\\20200827_082138.bag", True)
        
    else: 
        config.enable_stream(rs.stream.depth, width=640, height=480, format=rs.format.z16, framerate=30)
        config.enable_stream(rs.stream.color, width=1920, height=1080, format=rs.format.rgb8, framerate=30)
        #config.enable_device(camera_data["Intel RealSense D435"])
        #config.enable_device(camera_data["Intel RealSense L515"])

    conf = pipeline.start(config)

    depth_sensor = conf.get_device().first_depth_sensor()
    color_sensor = conf.get_device().first_color_sensor()


    dep = conf.get_stream(rs.stream.depth, 0).as_video_stream_profile()
    col = conf.get_stream(rs.stream.color, 0).as_video_stream_profile()


    d2cTemp = dep.get_extrinsics_to(col)
    c2dTemp = col.get_extrinsics_to(dep)

    d2c = glm.mat4(
        d2cTemp.rotation[0], d2cTemp.rotation[3], d2cTemp.rotation[6], 0,
        d2cTemp.rotation[1], d2cTemp.rotation[4], d2cTemp.rotation[7], 0,
        d2cTemp.rotation[2], d2cTemp.rotation[5], d2cTemp.rotation[8], 0,
        d2cTemp.translation[0], d2cTemp.translation[1], d2cTemp.translation[2], 1
    )

    c2d = glm.mat4(
        c2dTemp.rotation[0], c2dTemp.rotation[3], c2dTemp.rotation[6], 0,
        c2dTemp.rotation[1], c2dTemp.rotation[4], c2dTemp.rotation[7], 0,
        c2dTemp.rotation[2], c2dTemp.rotation[5], c2dTemp.rotation[8], 0,
        c2dTemp.translation[0], c2dTemp.translation[1], c2dTemp.translation[2], 1
    )

    K = glm.mat4(1.0)
    K[0, 0] = dep.intrinsics.fx # fx
    K[1, 1] = dep.intrinsics.fy # fy
    K[2, 0] = dep.intrinsics.ppx # cx
    K[2, 1] = dep.intrinsics.ppy # cy

    invK = glm.inverse(K)

    colK = glm.mat4(1.0)
    colK[0, 0] = col.intrinsics.fx # fx
    colK[1, 1] = col.intrinsics.fy # fy
    colK[2, 0] = col.intrinsics.ppx # cx
    colK[2, 1] = col.intrinsics.ppy # cy
    
    depth_scale = depth_sensor.get_depth_scale()
    
    # cal = json.loads(k4a.calibration_raw)
    # depthCal = cal["CalibrationInformation"]["Cameras"][0]["Intrinsics"]["ModelParameters"]
    # colorCal = cal["CalibrationInformation"]["Cameras"][1]["Intrinsics"]["ModelParameters"]
    # # https://github.com/microsoft/Azure-Kinect-Sensor-SDK/blob/61951daac782234f4f28322c0904ba1c4702d0ba/src/transformation/mode_specific_calibration.c
    # # from microsfots way of doing things, you have to do the maths here, rememberedding to -0.5f from cx, cy at the end
    # # this should be set from the depth mode type, as the offsets are different, see source code in link
    # #K = np.eye(4, dtype='float32')
    # K = glm.mat4(1.0)
    # K[0, 0] = depthCal[2] * cal["CalibrationInformation"]["Cameras"][0]["SensorWidth"] # fx
    # K[1, 1] = depthCal[3] * cal["CalibrationInformation"]["Cameras"][0]["SensorHeight"] # fy
    # K[2, 0] = (depthCal[0] * cal["CalibrationInformation"]["Cameras"][0]["SensorWidth"]) - 192.0 - 0.5 # cx
    # K[2, 1] = (depthCal[1] * cal["CalibrationInformation"]["Cameras"][0]["SensorHeight"]) - 180.0 - 0.5 # cy

    # invK = glm.inverse(K)

    # colK = glm.mat4(1.0)
    # colK[0, 0] = colorCal[2] * 1920.0# fx
    # colK[1, 1] = colorCal[3] * 1440.0 # fy # why 1440, since we are 1080p? check the link, the umbers are there, im sure they make sense ...
    # colK[2, 0] = (colorCal[0] * 1920.0) - 0 - 0.5 # cx
    # colK[2, 1] = (colorCal[1] * 1440.0) - 180.0 - 0.5 # cy

    # d2c = glm.mat4(
    #     cal["CalibrationInformation"]["Cameras"][1]["Rt"]["Rotation"][0], cal["CalibrationInformation"]["Cameras"][1]["Rt"]["Rotation"][3], cal["CalibrationInformation"]["Cameras"][1]["Rt"]["Rotation"][6], 0,
    #     cal["CalibrationInformation"]["Cameras"][1]["Rt"]["Rotation"][1], cal["CalibrationInformation"]["Cameras"][1]["Rt"]["Rotation"][4], cal["CalibrationInformation"]["Cameras"][1]["Rt"]["Rotation"][7], 0,
    #     cal["CalibrationInformation"]["Cameras"][1]["Rt"]["Rotation"][2], cal["CalibrationInformation"]["Cameras"][1]["Rt"]["Rotation"][5], cal["CalibrationInformation"]["Cameras"][1]["Rt"]["Rotation"][8], 0,
    #     cal["CalibrationInformation"]["Cameras"][1]["Rt"]["Translation"][0], cal["CalibrationInformation"]["Cameras"][1]["Rt"]["Translation"][1], cal["CalibrationInformation"]["Cameras"][1]["Rt"]["Translation"][2], 1
    #     )

    # c2d = glm.inverse(d2c)

    return d2c, c2d, K, invK, colK, depth_scale, dep.intrinsics.width, dep.intrinsics.height, col.intrinsics.width, col.intrinsics.height

def getFrames(useLiveCamera):
    if useLiveCamera == False:
        capture = pipeline.wait_for_frames()
        depth = capture.get_depth_frame()
        color = capture.get_color_frame()
    else:    
        capture = pipeline.wait_for_frames()
        depth = capture.get_depth_frame()
        color = capture.get_color_frame()

    return depth.get_data(), color.get_data()    

def setLaserPower(value):
    depth_sensor.set_option(rs.option.laser_power, int(value))


def stop():
    pipeline.stop()
