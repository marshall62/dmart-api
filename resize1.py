# resize a single image into a thumbnail and a midsize
# First run the rename_images.py on a full size image so that it has a correct
# david_marshall_XXX.jpg type of name
import os
import sys
import resize
from PIL import Image

def resize_single_file (pathToFile):
    print(f"Resizing file: {pathToFile}")
    dir = os.path.dirname(pathToFile)
    filename = os.path.basename(pathToFile)
    img = Image.open(pathToFile)
    thumb = resize.make_thumbnail(img,size=resize.THUMBSIZE)
    # create the image again because make_thumbnail mutated it.
    img = Image.open(pathToFile)
    midsize = resize.make_thumbnail(img,size=resize.MIDSIZE)
    path = os.path.join(dir, "midsize", filename)
    midsize.save(path, "JPEG")
    print(f"Saved {path}")
    path = os.path.join(dir, "thumb", filename)
    thumb.save(path, "JPEG")
    print(f"Saved {path}")



if __name__ == '__main__':
    print("args: ", sys.argv)
    if len(sys.argv) > 1:
        resize_single_file(*sys.argv[1:])
    else:
        print("Need to give a path to image file")
        # For debugging:
        # resize_single_file('/srv/dev/dmart-web/dmart-api/tmp/david_marshall_201.jpg')