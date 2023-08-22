
from PIL import Image

from runner import run


def filter_copy(image_before:Image.Image)->Image.Image:
    image_after=image_before.copy()
    return image_after

run(filter_copy)
