import pygame
from pygame.locals import *
if False:
  from OpenGL.GLES2 import *
  from OpenGL.GLES2 import shaders
else:
  from OpenGL.GL import *
  from OpenGL.GL import shaders

import numpy as np
from OpenGL.GLU import *
import io
import sys
from PIL import Image



def __checkOpenGLError():
  """Print OpenGL error message."""
  err = glGetError()
  if ( err != GL_NO_ERROR ):
    print(f"GLERROR: {gluErrorString( err )}")
    sys.exit()


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

  print(f"glGetString(GL_VERSION): {glGetString(GL_VERSION)}")


  # Create texture
  texture = glGenTextures(1)
  glBindTexture(GL_TEXTURE_2D, texture)
  glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
  
  position_array=np.array([
    [-1.0,-1.0,0.0],
    [+1.0,-1.0,0.0],
    [+1.0,+1.0,0.0],
    [-1.0,+1.0,0.0],
  ],dtype=np.float32)


  uv_array=np.array([
    [0.0,0.0],
    [1.0,0.0],
    [1.0,1.0],
    [0.0,1.0],
  ],dtype=np.float32)

  index_array=np.array([
    0,1,2,
    0,2,3,
  ],dtype=np.uint)

  # Vertex shader
  vertex_code = """
    #version 120
    attribute vec3 position;
    attribute vec2 uv;
    varying vec2 vUv;
    void main() {
      vUv=uv;
      gl_Position = vec4( position, 1.0 );
    }
  """
  
  # Fragment shader for inversion
  fragment_code = """
    #version 120
    varying vec2 vUv;
    uniform sampler2D texture;
    void main() {
      vec4 col = texture2D(texture, vUv);
      gl_FragColor = vec4(1.0 - col.r, 1.0 - col.g, 1.0 - col.b, col.a);
      // gl_FragColor=vec4(0.0,1.0,0.0,1.0);
    }
  """
  

  # Compile shaders
  vertex_shader = shaders.compileShader(vertex_code,GL_VERTEX_SHADER)
  __checkOpenGLError()
  fragment_shader = shaders.compileShader(fragment_code,GL_FRAGMENT_SHADER)
  __checkOpenGLError()
  
  shader_program = shaders.compileProgram(
    vertex_shader,
    fragment_shader,
  )
  __checkOpenGLError()
  
  # Render the image with the invert filter
  glClearColor(1.0, 0.0, 0.0, 1.0)  # 赤色でクリア
  __checkOpenGLError()
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
  __checkOpenGLError()
  glBindTexture(GL_TEXTURE_2D, texture)
  __checkOpenGLError()

  position_location = glGetAttribLocation(shader_program, 'position')
  __checkOpenGLError()
  uv_location = glGetAttribLocation(shader_program, 'uv')
  __checkOpenGLError()

  texture_location = glGetUniformLocation(shader_program, 'texture')
  __checkOpenGLError()

  with shader_program:

    glEnableVertexAttribArray(position_location)
    glVertexAttribPointer(position_location,3,GL_FLOAT,False,3*ctypes.sizeof(ctypes.c_float),position_array)

    glEnableVertexAttribArray(uv_location)
    glVertexAttribPointer(uv_location,2,GL_FLOAT,False,2*ctypes.sizeof(ctypes.c_float),uv_array)

    glUniform1i(texture_location,0)
    glDrawElements(GL_TRIANGLES,6,GL_UNSIGNED_INT,index_array)
    __checkOpenGLError()
  
  # Read the rendered image
  rendered_data = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
  __checkOpenGLError()
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
