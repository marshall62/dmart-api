from PIL import Image
import os
import pathlib
import PIL
import glob


def resize_dir (dir):
  images = [file for file in os.listdir(dir) if file.endswith(('jpeg', 'JPEG', 'JPG', 'png', 'jpg'))]
  if not os.path.exists(os.path.join(dir,"thumb")):
    os.mkdir(os.path.join(dir,"thumb"))
  if not os.path.exists(os.path.join(dir, "midsize")):
    os.mkdir(os.path.join(dir, "midsize"))
  for image in images:
      img = Image.open(os.path.join(dir,image))
      print(f"resizing {image}")
      img.thumbnail((700, 700))
      img.save(os.path.join(dir, "midsize", image), optimize=True, quality=100)

      img.thumbnail((100,100))
      img.save(os.path.join(dir,"thumb",image), optimize=True, quality=95)

resize_dir("/Users/marshald/dev/personal/dmart/api/test")
