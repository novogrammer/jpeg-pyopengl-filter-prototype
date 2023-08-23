from dotenv import load_dotenv
load_dotenv()

from typing import Any,Optional,List
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

vertices:List[float]=[
  -1,-1,0,
  +1,-1,0,
  +1,+1,0,
  -1,+1,0,
]
coords:List[float]=[
  0,0,
  1,0,
  1,1,
  0,1,
]
indices:List[int]=[
  0,1,2,
  0,2,3,
]


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
  pbo:GLuint
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
      # 有効にしたままにする
      glBindTexture(GL_TEXTURE_2D, self.texture)
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

      # 有効にしたままにする
      glEnableClientState(GL_VERTEX_ARRAY)
      glEnableClientState(GL_TEXTURE_COORD_ARRAY)
      glVertexPointer(3,GL_FLOAT,0,vertices)
      glTexCoordPointer(2,GL_FLOAT,0,coords)

      self.pbo=glGenBuffers(1)
      glBindBuffer(GL_PIXEL_UNPACK_BUFFER,self.pbo)
      glBufferData(GL_PIXEL_UNPACK_BUFFER,IMAGE_WIDTH * IMAGE_HEIGHT * 3,None,GL_STREAM_DRAW)
      glBindBuffer(GL_PIXEL_UNPACK_BUFFER,0)


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
        image_before_data:bytes = image_before.tobytes()

      # with MyTimer('glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_before_data)'):
      #   glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB
      #   , width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_before_data)

      with MyTimer('copy pbo'):
        glBindBuffer(GL_PIXEL_UNPACK_BUFFER,self.pbo)
        pbo_addr = glMapBuffer(GL_PIXEL_UNPACK_BUFFER, GL_WRITE_ONLY)
        ctypes.memmove(pbo_addr, image_before_data, IMAGE_WIDTH * IMAGE_HEIGHT * 3)
        glUnmapBuffer(GL_PIXEL_UNPACK_BUFFER)
        with MyTimer('glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)'):
          glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB
          , width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glBindBuffer(GL_PIXEL_UNPACK_BUFFER,0)



      with MyTimer('glUseProgram(self.program)'):
        glUseProgram(self.program)

      # glClearColor(1.0, 0.0, 0.0, 1.0)  # 赤色でクリア
      with MyTimer('glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)'):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
      # テクスチャは選択済みと仮定する
      # VBOは有効と仮定する
      with MyTimer('glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, indices)'):
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, indices)


      glBindBuffer(GL_PIXEL_PACK_BUFFER, self.pbo)
      with MyTimer('rendered_data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)'):
        glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE,ctypes.c_void_p(0))
      pbo_addr=glMapBuffer(GL_PIXEL_PACK_BUFFER, GL_READ_WRITE)
      rendered_data = ctypes.string_at(pbo_addr,IMAGE_WIDTH * IMAGE_HEIGHT * 3)
        
      with MyTimer('image_after = Image.frombytes("RGB", (width, height), rendered_data)'):
        image_after = Image.frombytes("RGB", (width, height), rendered_data)
      
      glUnmapBuffer(GL_PIXEL_PACK_BUFFER)
      glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

      with MyTimer('pygame.display.flip()'):
        pygame.display.flip()
      with MyTimer('image_after = ImageOps.flip(image_after)'):
        image_after = ImageOps.flip(image_after)

    return image_after

filter_invert = FilterInvert()

run(filter_invert)

del filter_invert