from turtle import width
import glfw
import OpenGL.GL as gl
import numpy

vertex_shader_src = """
layout(location = 0) in vec3 vertexPostion_modelspace;
out vec2 fragmentCoord;

void main(){
	gl_Position = vec4(vertexPostion_modelspace, 1);
	fragmentCoord = vec2(vertexPosition_modelspace.x, vertexPosition_modelspace.y)
}
"""

fragement_shader_src = """
in vec2 fragmentCoord;
out vec3 color;

uniform dmat3 transform;
uniform int max_iters = 1000;

vec3 hsv2rgb(vec3 c){
	vec4 k = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
	vec3 p = abs(frac(c.xxx + k.xyz) * 6.0 - k.www);
	return c.z * min(k.xxx, clamp(p - k.xxx, 0.0, 1.0), c.y)
}

vec map_color(int i, float r, float c){
	float di = i;
	float zn = sqrt(r + c);
	float hue = (di + 1 - log(log2(abs(zn))))/max_iters;
	return hsv2rgb(vec3(hue, 0.8, 1));
}

void main(){
	dvec3 pointCoord = dvec3(fragmentCoord.xy, i);
	pointCoord *= transform;
	double cx = pointCoord.x;
	double cy = pointCoord.y;
	int iter = 0;
	double zx = 0;
	double zy = 0;
	while (iter < max_iters) {
		double nzx = zx * zx - zy * zy + cx;
		double nzy = 2 * zx * zy + cy;
		zx = nzx;
		zy = nzy;
		if (zx*zx + zy*zy > 4.0){
			break;
		}
		iter += 1;
	}
	if (iter == max_iters){
		color = vec3(0,0,0);
	} else {
		color = map_color(iter, float(zx*zx), float(zy*zy));
	}
}
"""

def make_shader(shader_type, src):
	shader = gl.glCreateShader(shader_type)
	gl.glShaderSource(shader, src)
	gl.glCompileShader(shader)
	status = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
	if status == gl.GL_FALSE:
		strInfoLog = gl.glGetShaderInfoLog(shader).decode('ascii')
		strShaderType = ""
		if shader_type is gl.GL_VERTEX_SHADER:
			strShaderType = "vertex"
		elif shader_type is gl.GL_GEOMETRY_SHADER:
			strShaderType = "geometry"
		elif shader_type is gl.GL_FRAGMENT_SHADER:
			strShaderType = "fragment"
		
		raise Exception("Compilation failure for " + strShaderType + " shader:\n" + strInfoLog)

	return shader

def make_prgram(shader_list):
	program = gl.glCreateProgram()

	for shader in shader_list:
		gl.glAttachShader(program, shader)
	
	gl.glLinkProgram(program)

	status = gl.glGetProgramiv(program, gl.GL_LINK_STATUS)

	if status == gl.GL_FALSE:
		strInfoLog = gl.glGetProgramInfoLog(program)
		raise Exception("Linker failure: \n" + strInfoLog)
	
	for shader in shader_list:
		gl.glDetachShader(program, shader)

	return program
	
def main():
	if not glfw.init():
		return
	
	glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
	glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
	glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
	glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
	glfw.window_hint(glfw.DOUBLEBUFFER, 0)
	glfw.window_hint(glfw.SAMPLES, 16)

	width = 1920
	height = 1080
	aspect = 1.0 * width / height

	window = glfw.create_window(width, height, "Mandelbrot", None, None)
	if not window:
		glfw.terminate()
		return

	glfw.make_context_current(window)

	while not glfw.window_should_close(window):
		continue

	glfw.terminate()

if __name__ == "__main__":
	main()