from PIL import Image
import polaroid, sys, glob, os

concate = True

s = polaroid.Stylizer()
s.setOutputDimemsion(3200, 2400)
s.setBorder(100)

bgBuilder = polaroid.RandomBackgroundBuilder()
bgBuilder.addBackgroundBuilder(polaroid.OldStyleBackgroundBuilder())
bgBuilder.addBackgroundBuilder(polaroid.CircleBackgroundBuilder())
s.setBgBuilder(bgBuilder)
file_list = []
for i in sys.argv[1:]:
    file_list.extend(glob.glob(i))

file_list.sort()

prev_filename = "" # prevent repeat
count = 0
outputImg = None
for i in file_list:
    if prev_filename == i:
        continue
    fn = os.path.basename(i)
    fp = os.path.dirname(i)

    try:
        im = s.draw(Image.open(i))
    except:
        continue
    print("Processing: {0}".format(fn))

    if concate:
        if count % 2 == 0:
            outputImg = Image.new("RGB", (im.size[0] * 2, im.size[1]))
            outputImg.paste(im, (0, 0))
        else:
            outputImg.paste(im, (im.size[0], 0))
            outputImg.save("out-" + str(count/2) + ".jpg")
            outputImg = None
    else:
        im.save("M_" + fn)
    prev_filename = i
    count = count + 1

if outputImg != None:
    outputImg.save("out-" + str((count + 1)/2) + ".jpg")
    outputImg = None
