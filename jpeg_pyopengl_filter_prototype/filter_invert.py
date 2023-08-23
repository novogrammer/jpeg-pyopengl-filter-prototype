from dotenv import load_dotenv
load_dotenv()

from typing import Any,Optional
from PIL import Image,ImageOps

import pygame
# from pygame.locals import *
from OpenGL.GL import *
# from OpenGL.GLUT import *

from runner import run
from opengl_utils import load_shader

import os
import sys
from my_timer import MyTimer


vertex_code = """
void main(void) {
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    gl_TexCoord[0] = gl_MultiTexCoord0;
}
"""

fragment_code = """
uniform sampler2D texture;
void main(void) {
    vec4 color = texture2D(texture, gl_TexCoord[0].st);
    gl_FragColor = vec4(1.0 - color.r, 1.0 - color.g, 1.0 - color.b, color.a);
}
"""

IMAGE_WIDTH=int(os.getenv("SENDER_IMAGE_WIDTH","480"))
IMAGE_HEIGHT=int(os.getenv("SENDER_IMAGE_HEIGHT","270"))


class FilterInvert():
  program:GLuint
  texture:GLuint
  def __init__(self):
    with MyTimer('FilterInvert.__init__()'):
      pygame.init()
      pygame.display.set_mode((IMAGE_WIDTH, IMAGE_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)

      vertex_shader = load_shader(GL_VERTEX_SHADER, vertex_code)
      fragment_shader = load_shader(GL_FRAGMENT_SHADER, fragment_code)

      self.program = glCreateProgram()
      glAttachShader(self.program, vertex_shader)
      glAttachShader(self.program, fragment_shader)
      glLinkProgram(self.program)

      glDeleteShader(vertex_shader)
      glDeleteShader(fragment_shader)

      self.texture = glGenTextures(1)
      glBindTexture(GL_TEXTURE_2D, self.texture)
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

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

      with MyTimer('glUseProgram(self.program)'):
        glUseProgram(self.program)

      # glClearColor(1.0, 0.0, 0.0, 1.0)  # 赤色でクリア
      with MyTimer('glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)'):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
      # テクスチャは選択済みと仮定する
      with MyTimer('draw vertices'):
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(-1, -1)
        glTexCoord2f(1, 0); glVertex2f(1, -1)
        glTexCoord2f(1, 1); glVertex2f(1, 1)
        glTexCoord2f(0, 1); glVertex2f(-1, 1)
        glEnd()


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