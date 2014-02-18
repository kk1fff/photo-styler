# python

from PIL import Image, ImageDraw, ImageColor
import sys

# frm, to: (r, g, b)
def buildGradient(frm, to, step):
    rstep = float(to[0] - frm[0]) / float(step)
    gstep = float(to[1] - frm[1]) / float(step)
    bstep = float(to[2] - frm[2]) / float(step)
    for i in range(step):
        yield (int(frm[0] + rstep * i),
               int(frm[1] + gstep * i),
               int(frm[2] + bstep * i))

def DrawBackground(im):
    # compute gradient
    dr = ImageDraw.Draw(im);
    count = 0
    for c in buildGradient(ImageColor.getrgb("#ffffcc"),
                           ImageColor.getrgb("white"), 20):
        dr.rectangle([(count, count), (im.size[0]-count, im.size[1]-count)],
                      fill = c)
        count = count + 1
    return im

def DrawBorder(im, width, height):
    bdr = Image.new("RGB", (width, height), "#c0c0c0")
    bdr_alpha = Image.new("L", (width, height), 32)
    im.paste(bdr, (0, 0), bdr_alpha)
    return im

# Size of result image.
LSIDE = 1200 # px
SSIDE = 900 # px
BORDER = 50 #px

# photo ratio. No unit, just ratio
PLSIDE = 1
PSSIDE = 1

BgDrawingFunc = DrawBackground
BorderDrawingFunc = DrawBorder

# Load image
photo = Image.open(sys.argv[1])
photo_width = photo.size[0]
photo_height = photo.size[1]

# 0: vertical, 1: horizontal
orientation = 0 if photo_width <= photo_height else 1

# Crop if need
if orientation == 0:
    # verticle, crop upper and down piece
    crop_length = int(float(photo_width) / float(PSSIDE) * float(PLSIDE))
    if crop_length < photo_height:
        offset = (photo_height - crop_length) / 2
        photo = photo.crop((0, offset,
                            photo_width, crop_length + offset))
        photo_height = photo.size[1]
else:
    crop_length = int(float(photo_height) / float(PSSIDE) * float(PLSIDE))
    print photo_height, crop_length
    if crop_length < photo_width:
        offset = (photo_width - crop_length) / 2
        photo = photo.crop((offset, 0,
                            crop_length + offset, photo_height))
        photo_width = photo.size[0]

# recalculate orientation, to handle the case that photo become
# square after crop.
# 0: vertical, 1: horizontal
orientation = 0 if photo_width <= photo_height else 1

im_size = (SSIDE, LSIDE) if orientation == 0 else (LSIDE, SSIDE)
im = Image.new("RGB", im_size)

im = BgDrawingFunc(im)

# compute target size
target_width = 0
target_height = 0
if orientation == 0:
    target_width = im_size[0] - 2 * BORDER
    target_height = int(float(target_width) / float(photo_width) * float(photo_height))
else:
    target_height = im_size[1] - 2 * BORDER
    target_width = int(float(target_height) / float(photo_height) * float(photo_width))

# create border
border_box_width = 0
border_box_heigth = 0
if orientation == 0:
    border_box_width = im_size[0]
    border_box_heigth = target_height + 2 * BORDER
else:
    border_box_width = target_width + 2 * BORDER
    border_box_heigth = im_size[1]
im = DrawBorder(im, border_box_width, border_box_heigth)

# paste photo layer
photo = photo.resize((target_width, target_height))
im.paste(photo, (BORDER, BORDER))
if len(sys.argv) > 2:
    im.save(sys.argv[2])
else:
    im.show()
