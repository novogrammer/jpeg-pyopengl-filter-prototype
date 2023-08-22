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

IMAGE_WIDTH=int(os.getenv("SENDER_IMAGE_WIDTH","480"))
IMAGE_HEIGHT=int(os.getenv("SENDER_IMAGE_HEIGHT","270"))


class FilterInvert():
  def __init__(self):
    # Initialize pygame and OpenGL
    pygame.init()
    pygame.display.set_mode((IMAGE_WIDTH, IMAGE_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)

    # Compile shaders
    self.vertex_shader = load_shader(GL_VERTEX_SHADER, vertex_code)
    self.fragment_shader = load_shader(GL_FRAGMENT_SHADER, fragment_code)

    # Create shader program
    self.program = glCreateProgram()
    glAttachShader(self.program, self.vertex_shader)
    glAttachShader(self.program, self.fragment_shader)
    glLinkProgram(self.program)

  def __del__(self):
    pass
    
  def __call__(self,image_before:Optional[Image.Image]=None) -> Image.Image|None:

    if not image_before:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()
      return

    image_before=ImageOps.flip(image_before)
    image_before=image_before.convert("RGBA")
    width = image_before.width
    height = image_before.height
    image_before_data = image_before.tobytes()

    # Create texture
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_before_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glUseProgram(self.program)

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
    image_after = Image.frombytes("RGBA", (width, height), rendered_data)
    pygame.display.flip()
    image_after = ImageOps.flip(image_after)

    return image_after

filter_invert = FilterInvert()

run(filter_invert)

del filter_invert