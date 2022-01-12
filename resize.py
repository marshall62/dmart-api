from PIL import Image
import os
import pathlib
import PIL
from PIL.ExifTags import TAGS
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

def resize_path (path):
    img = Image.open(path)
    path, ext = os.path.splitext(path)
    print("Saving thumbnail as ", path+"_thumb"+ext)
    # print(img._getexif().items())
    exif=dict((TAGS[k], v) for k, v in img._getexif().items() if k in TAGS)
    if orient:=exif['Orientation']:
        print(f"Exif orientation{orient} Rotating 90")
        if orient == 8:
          img = img.rotate(90, expand=True)
        elif orient == 2:
          img = img.rotate(270, expand=True)
    img.thumbnail((100,100), Image.ANTIALIAS)
    img.save(path+"_thumb"+ext)

import sys

if __name__ == '__main__':
    print("args: ", sys.argv)
    if len(sys.argv) > 1:
        resize_path(sys.argv[1])
    else:
        print("Need to give a path to image file")
