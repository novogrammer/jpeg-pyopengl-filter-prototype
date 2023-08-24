from dotenv import load_dotenv
load_dotenv()

from typing import Any,Optional
from PIL import Image,ImageOps

import pygame
# from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL import shaders
# from OpenGL.GLUT import *

from runner import run

import os
import sys
from my_timer import MyTimer

import numpy as np


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

IMAGE_WIDTH=int(os.getenv("SENDER_IMAGE_WIDTH","480"))
IMAGE_HEIGHT=int(os.getenv("SENDER_IMAGE_HEIGHT","270"))


class FilterInvert():
  texture:GLuint
  shader_program:shaders.ShaderProgram
  position_location:GLuint
  uv_location:GLuint
  texture_location:GLuint
  def __init__(self):
    with MyTimer('FilterInvert.__init__()'):
      pygame.init()
      pygame.display.set_mode((IMAGE_WIDTH, IMAGE_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)

      vertex_shader = shaders.compileShader(vertex_code,GL_VERTEX_SHADER)
      fragment_shader = shaders.compileShader(fragment_code,GL_FRAGMENT_SHADER)

      self.shader_program = shaders.compileProgram(
        vertex_shader,
        fragment_shader,
      )

      self.texture = glGenTextures(1)
      glBindTexture(GL_TEXTURE_2D, self.texture)
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

      self.position_location = glGetAttribLocation(self.shader_program, 'position')
      self.uv_location = glGetAttribLocation(self.shader_program, 'uv')
      self.texture_location = glGetUniformLocation(self.shader_program, 'texture')

  def __del__(self):
    pygame.quit()
    pass
  def __call__(self,image_before:Optional[Image.Image]=None) -> Image.Image|None:

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        # SystemExit例外が発生する
        sys.exit()
    if not image_before:
      return

    with MyTimer('FilterInvert.__call__(Image)'):
      with MyTimer('ImageOps.flip(image_before)'):
        image_before=ImageOps.flip(image_before)
      width = image_before.width
      height = image_before.height
      with MyTimer('image_before.tobytes()'):
        image_before_data = image_before.tobytes()

      # テクスチャは選択済みと仮定する
      with MyTimer('glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_before_data)'):
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_before_data)

      # glClearColor(1.0, 0.0, 0.0, 1.0)  # 赤色でクリア
      with MyTimer('glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)'):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        with self.shader_program:
          with MyTimer('draw vertices'):
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

            glEnableVertexAttribArray(self.position_location)
            glVertexAttribPointer(self.position_location,3,GL_FLOAT,False,3*ctypes.sizeof(ctypes.c_float),position_array)

            glEnableVertexAttribArray(self.uv_location)
            glVertexAttribPointer(self.uv_location,2,GL_FLOAT,False,2*ctypes.sizeof(ctypes.c_float),uv_array)

            glUniform1i(self.texture_location,0)
            glDrawElements(GL_TRIANGLES,6,GL_UNSIGNED_INT,index_array)



      with MyTimer('rendered_data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)'):
        rendered_data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
      with MyTimer('image_after = Image.frombytes("RGB", (width, height), rendered_data)'):
        image_after = Image.frombytes("RGB", (width, height), rendered_data)
      with MyTimer('pygame.display.flip()'):
        pygame.display.flip()
      with MyTimer('image_after = ImageOps.flip(image_after)'):
        image_after = ImageOps.flip(image_after)

    return image_after

filter_invert = FilterInvert()

run(filter_invert)

del filter_invert