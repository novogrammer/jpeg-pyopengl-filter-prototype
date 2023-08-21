import pygame


# 関数の出口に終了処理を追加するデコレータ
def cleanup(func):
  def wrap(*args):
    print('cleanup')
    func(*args)
    pygame.quit()
  return wrap


class PyGame:
  def __init__(self):
    self._running = True
    self._screen = None

  def initialize(self, w, h):
    pygame.init()
    # OPENGL向けに初期化する
    self._screen = pygame.display.set_mode(
      (w, h), pygame.OPENGL | pygame.DOUBLEBUF)

    if not self._screen:
      return

    return True

  def on_event(self, event):
    if event.type == pygame.QUIT:
      self._running = False

  def update(self):
    pass

  def draw(self):
    pass

  @cleanup
  def execute(self, w, h):
    if not self.initialize(w, h):
      return

    while self._running:
      for event in pygame.event.get():
        self.on_event(event)
      self.update()
      self.draw()


if __name__ == "__main__" :
  game=PyGame()
  game.execute(640, 480)