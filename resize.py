from PIL import Image
import os
import pathlib
import PIL
from PIL.ExifTags import TAGS
import glob


# go over the whole dir and create subdirs for medium and thumb
def resize_dir (dir, make_thumbs="False", make_midsize="False"):
  make_thumbs = make_thumbs == "True"
  make_midsize = make_midsize == 'True'
  images = [file for file in os.listdir(dir) if file.endswith(('jpeg', 'JPEG', 'JPG', 'png', 'jpg'))]
  if make_thumbs and not os.path.exists(os.path.join(dir,"thumb")):
    os.mkdir(os.path.join(dir,"thumb"))
  if make_midsize and not os.path.exists(os.path.join(dir, "midsize")):
    os.mkdir(os.path.join(dir, "midsize"))
  for image in sorted(images):     
      print(f"resizing {image}")
      if make_midsize:
        img = Image.open(os.path.join(dir,image))
        img = make_thumbnail(img,700)
        img.save(os.path.join(dir, "midsize", image), "JPEG")
      if make_thumbs:
        img = Image.open(os.path.join(dir,image))
        img = make_thumbnail(img,100)
        img.save(os.path.join(dir,"thumb",image), "JPEG")

# writes to the subdir
def resize_path (path, size=100):
    img = Image.open(path)
    path, ext = os.path.splitext(path)
    img = make_thumbnail(img, size)
    img.save(path+f"_resized_{size}"+ext)

def make_thumbnail (img: Image, size=100):
  if img._getexif():
    exif=dict((TAGS[k], v) for k, v in img._getexif().items() if k in TAGS) 
    if orient:=exif.get('Orientation'):
        if orient == 8:
          img = img.rotate(90, expand=True)
        elif orient == 2:
          img = img.rotate(270, expand=True)
  img.thumbnail((size, size), Image.ANTIALIAS)
  return img

import sys

if __name__ == '__main__':
    print("args: ", sys.argv)
    if len(sys.argv) > 1:
        resize_dir(*sys.argv[1:])
    else:
        print("Need to give a path to image file")
