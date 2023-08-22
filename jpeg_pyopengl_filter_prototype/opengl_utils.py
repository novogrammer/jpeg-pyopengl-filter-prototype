from OpenGL.GL import *
# from OpenGL.GLUT import *

def load_shader(shader_type:GL_VERTEX_SHADER|GL_FRAGMENT_SHADER, shader_code:str)->GLuint:
  shader = glCreateShader(shader_type)
  glShaderSource(shader, shader_code)
  glCompileShader(shader)
  if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
    raise RuntimeError(glGetShaderInfoLog(shader))
  return shader

