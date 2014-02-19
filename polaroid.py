# coding: utf-8
# python

from PIL import Image, ImageDraw, ImageColor, ImageFont
import sys, random, math

CIRCLEBACKCOLOR = ["red", "yellow", "#a0a0ff", "#a0ffa0", "#ffffa0"]

def DrawCircleBackground(im):
    dr = ImageDraw.Draw(im)
    dr.rectangle([(0, 0), im.size], "white")
    dr = None

    diagonal = int(math.sqrt(float(im.size[0] * im.size[0] + im.size[1] * im.size[1])))
    maxr = diagonal / 20
    border = max(diagonal / 50, 1)

    for i in range(40):
        randx = random.randint(0, im.size[0])
        randy = random.randint(0, im.size[1])
        randr = random.randint(1, maxr if maxr > 1 else 1)
        imDrw = Image.new("RGB", im.size, "white")
        box = [randx - randr, randy - randr,
               randx + randr, randy + randr]
        outterbox = [box[0] - border, box[1] - border,
                     box[2] + border, box[3] + border]

        drImDrw = ImageDraw.Draw(imDrw)
        # drImDrw.ellipse(outterbox, CIRCLEBACKCOLOR[random.randint(0, len(CIRCLEBACKCOLOR) - 1)])
        drImDrw.ellipse(box, CIRCLEBACKCOLOR[random.randint(0, len(CIRCLEBACKCOLOR) - 1)])
        mask = Image.new("L", im.size, 0)
        drMask = ImageDraw.Draw(mask)
        drMask.ellipse(box, 127)
        im.paste(imDrw, mask)
    return im

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
    dr = ImageDraw.Draw(im)
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

# Default delegate
BgDrawingFunc = DrawCircleBackground
BorderDrawingFunc = DrawBorder

# Default font setting
FONTSIZE = 64

class Stylizer:
    def __init__(self):
        self.long_side = LSIDE
        self.short_side = SSIDE
        self.border = BORDER
        self.p_long_side = PLSIDE
        self.p_short_side = PSSIDE
        self.bgDrawer = BgDrawingFunc
        self.bdrDrawer = BorderDrawingFunc
        self.font = ImageFont.load_default()

    def setOutputDimemsion(self, longSide, shortSide):
        self.long_side = longSide
        self.short_side = shortSide

    def setBorder(self, border):
        self.border = border;

    def setPhotoEdgeRatio(self, longSide, shortSide):
        self.p_long_side = longSide
        self.p_short_side = shortSide

    # Pass a function that takes a PIL image as a parameter,
    # and return a PIL image.
    def setBgDrawer(self, bgDrawer):
        self.bgDrawer = bgDrawer

    # Pass function func(image, width, height)
    # which returns a PIL image.
    def setBorderDrawer(self, bdrDrawer):
        self.bdrDrawer = bdrDrawer

    def setFont(self, fontPath, fontSize):
        self.font = ImageFont.truetype(fontPath, fontSize)

    def wrapText(self, drw, txt, width):
        buf = ""
        isFirst = True
        for c in txt:
            if drw.textsize(buf + c, self.font)[0] <= width:
                buf = buf + c
            elif isFirst:
                # can't wrap even with only one character,
                # don't try to wrap then.
                return txt
            else:
                # need a line break
                buf = buf + "\n" + c
            isFirst = False
        return buf

    def draw(self, im, textOnImage = None):
        # Load image
        photo = im
        photo_width = photo.size[0]
        photo_height = photo.size[1]

        # 0: vertical, 1: horizontal
        orientation = 0 if photo_width <= photo_height else 1

        # Crop if need
        if orientation == 0:
            # verticle, crop upper and down piece
            crop_length = int(float(photo_width) / float(self.p_short_side) * float(self.p_long_side))
            if crop_length < photo_height:
                offset = (photo_height - crop_length) / 2
                photo = photo.crop((0, offset,
                                    photo_width, crop_length + offset))
                photo_height = photo.size[1]
        else:
            crop_length = int(float(photo_height) / float(self.p_short_side) * float(self.p_long_side))
            if crop_length < photo_width:
                offset = (photo_width - crop_length) / 2
                photo = photo.crop((offset, 0,
                                    crop_length + offset, photo_height))
                photo_width = photo.size[0]

        # recalculate orientation, to handle the case that photo become
        # square after crop.
        # 0: vertical, 1: horizontal
        orientation = 0 if photo_width <= photo_height else 1

        im_size = (self.short_side, self.long_side) if orientation == 0 else (self.long_side, self.short_side)
        im = Image.new("RGB", im_size)

        im = self.bgDrawer(im)

        # compute target size
        target_width = 0
        target_height = 0
        if orientation == 0:
            target_width = im_size[0] - 2 * self.border
            target_height = int(float(target_width) / float(photo_width) * float(photo_height))
        else:
            target_height = im_size[1] - 2 * self.border
            target_width = int(float(target_height) / float(photo_height) * float(photo_width))

        # create border
        border_box_width = 0
        border_box_heigth = 0
        if orientation == 0:
            border_box_width = im_size[0]
            border_box_heigth = target_height + 2 * self.border
        else:
            border_box_width = target_width + 2 * self.border
            border_box_heigth = im_size[1]
        im = self.bdrDrawer(im, border_box_width, border_box_heigth)

        # paste photo layer
        photo = photo.resize((target_width, target_height))
        im.paste(photo, (self.border, self.border))

        # Write text
        if textOnImage != None:
            txtDrw = ImageDraw.Draw(im)

            txtPos = None
            wrapWidth = 0
            # use white area.
            if orientation == 0:
                txtPos = (self.border, target_height + 2 * self.border)
                wrapWidth = im_size[0] - 2 * self.border
            else:
                txtPos = (target_width + 2 * self.border, self.border)
                wrapWidth = im_size[0] - 3 * self.border - target_width

            # textOnImage = self.wrapText(txtDrw, textOnImage, wrapWidth)

            # draw multi-line
            for s in textOnImage.split("\n"):
                txtDrw.text(txtPos, s, "black", self.font)
                txtPos = (txtPos[0], txtPos[1] + txtDrw.textsize(s)[1])
        return im

s = Stylizer()
s.setFont("sample.ttc", 64)
s.draw(Image.open(sys.argv[1]), None).save(sys.argv[2])
