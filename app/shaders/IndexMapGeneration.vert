#version 430

// Data structure
struct gMapData
{
	vec4 data;	// Confidence, radius, timestamp, and empty data 
	vec4 vert;	// Vertex
	vec4 norm;	// Normal
	vec4 color;	// Color
};

layout(std430, binding = 0) buffer poseBuffer
{
    mat4 pose;
    mat4 inversePose;
    mat4 splatPose;
    mat4 inverseSplatPose;
    float result[6];
};

// Distance global map
layout(std430, binding = 1) buffer gMap
{
	gMapData elems[];
};

uniform vec2 imSize;
uniform vec4 cam;
uniform float maxDepth;
uniform mat4 K;

flat out int idx;

// vec3 projectPoint(vec3 p)
// {
//     return vec3(((((cam.z * p.x) / p.z) + cam.x) - (imSize.x * 0.5)) / (imSize.x * 0.5),
//                 ((((cam.w * p.y) / p.z) + cam.y) - (imSize.y * 0.5)) / (imSize.y * 0.5),
//                 p.z / maxDepth);
// }

vec3 projectPoint(vec3 p)
{
    return vec3(((((K[0][0] * p.x) / p.z) + K[2][0]) - (imSize.x * 0.5)) / (imSize.x * 0.5),
                ((((K[1][1] * p.y) / p.z) + K[2][1]) - (imSize.y * 0.5)) / (imSize.y * 0.5),
                p.z / maxDepth);
}

vec3 projectPointImage(vec3 p)
{
    return vec3(((cam.z * p.x) / p.z) + cam.x,
                ((cam.w * p.y) / p.z) + cam.y,
                p.z);
}
vec4 transPtForGL(vec4 v)
{
	if (v.w == 0) {
		return vec4(-1.0f);
	}
	v = inversePose * v;
	return vec4(projectPoint(vec3(v.xy, v.z)), 1.0f);
	//return P * vec4(v.xy, -v.z, 1.0);
}

void main()
{
	idx = gl_VertexID;

	vec4 tempPos = transPtForGL(elems[idx].vert);

	if (tempPos.z < 0)
	{
		gl_Position = vec4(10000,10000,0,0);
	}
	else
	{
		gl_Position = tempPos;
	}

	
}