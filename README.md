# pyglFusion
An openGL GLSL implementation of Kinect Fusion using a python front end. We try and do as little as possible in python, because speed. Memory copies from or to the GPU are limited to the bare minimum of uploading the camera image frames. 

Currently implemented:

1. Point to Point (p2p) fusion as in Newcombe et al. 2011 https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/ismar2011.pdf
2. Point to Volume (p2v) fusion as in Canelhas et al 2013 "SDF Tracker: A parallel algorithm for on-line pose estimation and scene reconstruction from depth images"
3. Splatter (splat) fusion as in Keller et al 2013 http://reality.cs.ucl.ac.uk/projects/kinect/keller13realtime.html

Splatter fusion currently uses atomic counters which may be slower than implementing optimized transform feedback shaders. 

## Installation

Tested running on win10 with python 3.8 x64, and the Nvidia Jetson Xavier NX (python 3.6)

Prerequisities 
```shell
pip install glfw PyOpenGL opencv-python imgui 
```

https://github.com/IntelRealSense/librealsense/tree/master/wrappers/python contains instructions on how to install the realsense2 SDK with python wrappers. Essentially, build the standard SDK using cmake, but specify to enable BUILD_PYTHON_BINDINGS. Once the SDK has been built (ensuring that the pyrealsense2 wrapper projects are also built) you should see some newly created pyrealsense2.xxxxxxx.pyd and pybackend2.xxxxxxxx.pyd files. These files should be copied accross to either your global site-packages location, or next to the python script, as per the instructions in the link above.

The python wrappers for the realsense2 libs should also be installed in your site-packages, or simply copied across to be next to the pyglFusionRS.py script. Windows users will also need to copy the realsense2.dll to the same location as the pyrealsense2 pyd files.


```shell
$ git clone https://github.com/philipNoonan/pyglFusionK4a.git
```

You should be able to now run 

```shell
$ python .\app\pyglFusionRS.py
```
or 
```shell
$ python ./app/pyglFusionRS.py
```
The following is for experimental uses of pytorch and pycuda, they do not need to be used for the above fusion algorithms to be useable.

pycuda needs to be installed from source (i.e. not with pip install) with the following line added to the siteconf.py file created from running the configure.py script.

```
CUDA_ENABLE_GL = True
````


## Using pyglFusion


```
$ python app/pyglFusionK4A.py
```

Currently, you will have to edit the python file to select the recorded .mkv file. On success you will see a window showing the depth, normals, and color image from the kinect data.