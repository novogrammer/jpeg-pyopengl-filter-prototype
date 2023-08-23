import time

class MyTimer():
  def __init__(self, name=None):
    self.name = name

  def __enter__(self):
    self.start = time.perf_counter()
    return self

  def __exit__(self, *args):
    self.end = time.perf_counter()
    name_str = f"'{self.name}' " if self.name else ""
    print(f"{name_str}Elapsed time: {(self.end - self.start)*1000.0:.2f}[ms]")
