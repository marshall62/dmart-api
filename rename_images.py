import os
import shutil

def rename_images (source_dir, target_dir=None):
  '''
  All images files in the source_dir are renamed and copied to the target_dir.

  target_dir defaults to source_dir/renamed

  To rename within the same dir (preserving files with david_marshall prefix) call this function
  with the same directory as arg 1 and 2.

  If the image file name begins with david_marshall we do not rename it.  We merely copy it to the target.
  All files with jpg-like extensions are renamed to use only ".jpg"

  Files that get renamed will increment from the maximum suffix number associated with a david_marshall_XXX.jpg
  file in the source dir.

  Note:  There is an optional fill-gaps arg (true/false) that will notice if there are non-sequential suffixes among the
  existing david_marshall_XXX files and will first fill them before going into new suffixes.

  This makes it safe to run this function on a directory that is a mixture of converted files (i.e. ones that begin
  with david_marshall) and ones that have free-form names to get a result that only renames the free-form ones.
  '''
  image_filenames = [file for file in os.listdir(source_dir) if file.endswith(('jpeg', 'JPEG', 'JPG', 'png', 'jpg'))]
  if not target_dir:
    target_dir = os.path.join(source_dir,"renamed")
    print(f'Using default target dir: {target_dir}')
  if not os.path.exists(target_dir):
    os.mkdir(target_dir)
  print(f'Renaming image files in {source_dir} to {target_dir}')
  max_suffix, gap_suffixes = process_suffixes(image_filenames)
  gaps_filled = {"value": False}

  suffix = max_suffix
  for filename in image_filenames:
      if filename.startswith('david_marshall_'):
        if source_dir == target_dir:
          continue
        print(f'copying {filename} to {target_dir}')
        shutil.copy(os.path.join(source_dir,filename),target_dir)
      else:
        suffix = next_suffix(suffix, max_suffix, gap_suffixes, gaps_filled)
        new_name = rename_file(filename, suffix)
        print(f'renaming {filename} to {os.path.join(target_dir,new_name)}')
        shutil.copy(os.path.join(source_dir,filename), os.path.join(target_dir,new_name))
        if target_dir == source_dir:
          os.remove(os.path.join(source_dir,filename))
  print('done')
  print('*: files that filled gaps (and may already have a Mongo artwork record)')

def next_suffix (suffix, max_suffix, gap_suffixes, gaps_filled):
  if len(gap_suffixes) > 0:
    print("*",end='')
    suffix = gap_suffixes.pop(0)
    if len(gap_suffixes) == 0:
      gaps_filled['value'] = True
  else: # once we are done gap-filling we need to switch to start from max_suffix and then increment from there.
    if gaps_filled.get('value'):
      suffix = max_suffix
      del gaps_filled['value'] # remove once we make the switch
    suffix += 1
  return suffix

def rename_file (filename, suffix):
  ext = os.path.splitext(filename)[1]
  if ext.upper() in ['.JPG', '.JPEG']:
    ext = '.jpg'
  new_name = f'david_marshall_{suffix}{ext}'
  return new_name

def process_suffixes (image_filenames):
  image_filenames.sort(
    key=lambda x: int(os.path.splitext(x)[0].split('_')[2]) if x.startswith("david_marshall_") else 0)
  gap_suffixes = []
  max_suffix = last_suffix = 0
  for filename in image_filenames:
      if filename.startswith('david_marshall_'):
        suffix = int(os.path.splitext(filename)[0].split('_')[2])
        if suffix != last_suffix + 1:
          for i in range(last_suffix+1,suffix):
            gap_suffixes.append(i)
        last_suffix = suffix
        max_suffix = max(max_suffix, suffix)
  return max_suffix, gap_suffixes

# N.B. This will work within one directory preserving files that have already been converted
# and renaming those that haven't
if __name__ == '__main__':
  root_dir = "/srv/dev/dmart"
  # root_dir = "/User/marshald/dev/personal/dmart"
  # rename_images(root_dir + "/images", root_dir + "/images")
  rename_images(root_dir + "/images")
