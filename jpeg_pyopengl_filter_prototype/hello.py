import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
import io
from PIL import Image

def load_shader(shader_type, shader_code):
  shader = glCreateShader(shader_type)
  glShaderSource(shader, shader_code)
  glCompileShader(shader)
  if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
    raise RuntimeError(glGetShaderInfoLog(shader))
  return shader

def apply_invert_filter(input_jpeg_binary):

  
  # Load the image from binary

  image = Image.open(io.BytesIO(input_jpeg_binary))
  image=image.convert("RGBA")
  width=image.width
  height=image.height
  image_data = image.tobytes()
  
  # Initialize pygame and OpenGL
  pygame.init()
  pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)

  depth_buffer_obj = glGenRenderbuffers(1)
  glBindRenderbuffer(GL_RENDERBUFFER, depth_buffer_obj)
  glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, width, height)

  color_buffer_obj = glGenRenderbuffers(1)
  glBindRenderbuffer(GL_RENDERBUFFER, color_buffer_obj)
  glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA, width, height)

  fb_obj = glGenFramebuffers(1)
  glBindFramebuffer(GL_FRAMEBUFFER, fb_obj)
  glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth_buffer_obj)
  glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, color_buffer_obj)

  status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
  if status != GL_FRAMEBUFFER_COMPLETE:
      print("incomplete framebuffer object")

  # Create texture
  texture = glGenTextures(1)
  glBindTexture(GL_TEXTURE_2D, texture)
  glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
  
  # Vertex shader
  vertex_code = """
  void main(void) {
      gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
      gl_TexCoord[0] = gl_MultiTexCoord0;
  }
  """
  
  # Fragment shader for inversion
  fragment_code = """
  uniform sampler2D texture;
  void main(void) {
      vec4 color = texture2D(texture, gl_TexCoord[0].st);
      gl_FragColor = vec4(1.0 - color.r, 1.0 - color.g, 1.0 - color.b, color.a);
  }
  """
  
  # Compile shaders
  vertex_shader = load_shader(GL_VERTEX_SHADER, vertex_code)
  fragment_shader = load_shader(GL_FRAGMENT_SHADER, fragment_code)
  
  # Create shader program
  program = glCreateProgram()
  glAttachShader(program, vertex_shader)
  glAttachShader(program, fragment_shader)
  glLinkProgram(program)
  glUseProgram(program)
  
  # Render the image with the invert filter
  # glClearColor(1.0, 0.0, 0.0, 1.0)  # 赤色でクリア
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
  glBindTexture(GL_TEXTURE_2D, texture)
  glBegin(GL_QUADS)
  glTexCoord2f(0, 0); glVertex2f(-1, -1)
  glTexCoord2f(1, 0); glVertex2f(1, -1)
  glTexCoord2f(1, 1); glVertex2f(1, 1)
  glTexCoord2f(0, 1); glVertex2f(-1, 1)
  glEnd()
  
  # Read the rendered image
  rendered_data = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
  output_image = Image.frombytes("RGBA", (width, height), rendered_data)
  output_image = output_image.convert("RGB")

  
  # Convert the image to JPEG binary
  output_buffer = io.BytesIO()
  output_image.save(output_buffer, format="JPEG")
  output_jpeg_binary = output_buffer.getvalue()
  
  return output_jpeg_binary

# Example usage
with open("input.jpg", "rb") as f:
  input_jpeg_binary = f.read()

output_jpeg_binary = apply_invert_filter(input_jpeg_binary)

with open("output.jpg", "wb") as f:
  f.write(output_jpeg_binary)
