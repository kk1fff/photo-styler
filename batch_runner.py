from PIL import Image
import polaroid, sys, glob, os

s = polaroid.Stylizer()

file_list = []
for i in sys.argv[1:]:
    file_list.extend(glob.glob(i))

file_list.sort()
prev_filename = "" # prevent repeat
for i in file_list:
    if prev_filename == i:
        continue
    prev_filename = i
    fn = os.path.basename(i)
    fp = os.path.dirname(i)

    print("Processing: {0}".format(fn))

    s.draw(Image.open(i)).save(fp + "/M_" + fn)

