from PIL import Image
import os
import pathlib
import PIL
from PIL.ExifTags import TAGS
import glob
import traceback

MIDSIZE=900
THUMBSIZE=100

# go over the whole dir and create subdirs for medium and thumb
def resize_dir(dir, make_thumbs=False, make_midsize=False):
    try:
        images = [file for file in os.listdir(dir) if file.endswith(('jpeg', 'JPEG', 'JPG', 'png', 'jpg'))]
        if make_thumbs and not os.path.exists(os.path.join(dir, "thumb")):
            os.mkdir(os.path.join(dir, "thumb"))
        if make_midsize and not os.path.exists(os.path.join(dir, "midsize")):
            os.mkdir(os.path.join(dir, "midsize"))

        for image in sorted(images):
            print(f"resizing {image}")
            # N.B. I need to create a new image for each time I wish to save a new resized
            # version of it because calling make_thumbnail on the image mutates it.
            if make_midsize:
                img = Image.open(os.path.join(dir, image))
                img = make_thumbnail(img, MIDSIZE)
                img.save(os.path.join(dir, "midsize", image), "JPEG")
            if make_thumbs:
                img = Image.open(os.path.join(dir, image))
                img = make_thumbnail(img, THUMBSIZE)
                img.save(os.path.join(dir, "thumb", image), "JPEG")
    except Exception as ex:
        print(''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__)))



# writes to the subdir
def resize_path(path, size=THUMBSIZE):
    img = Image.open(path)
    path, ext = os.path.splitext(path)
    img = make_thumbnail(img, size)
    img.save(path + f"_resized_{size}" + ext)


def make_thumbnail(img: Image, size=100):
    if img._getexif():
        exif = dict((TAGS[k], v) for k, v in img._getexif().items() if k in TAGS)
        if orient := exif.get('Orientation'):
            if orient == 8:
                img = img.rotate(90, expand=True)
            elif orient == 2:
                img = img.rotate(270, expand=True)
    img.thumbnail((size, size), Image.ANTIALIAS)
    return img

def resize_dir_toplev (dir, make_thumbs="False", make_midsize="False"):
    resize_dir(dir,make_thumbs.capitalize() == "True", make_midsize.capitalize() == "True")
import sys

# call it like : python resize.py /srv/dev/dmart-web/dmart/images False True
if __name__ == '__main__':
    print("args: ", sys.argv)
    if len(sys.argv) > 1:
        resize_dir_toplev(*sys.argv[1:])
    else:
        print("Need to give a path to image file")
