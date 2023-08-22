from OpenGL.GL import *
# from OpenGL.GLUT import *

def load_shader(shader_type, shader_code):
  shader = glCreateShader(shader_type)
  glShaderSource(shader, shader_code)
  glCompileShader(shader)
  if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
    raise RuntimeError(glGetShaderInfoLog(shader))
  return shader

