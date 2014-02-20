# coding: utf-8
# python

from PIL import Image, ImageDraw, ImageColor, ImageFont
import sys, random, math

CIRCLEBACKCOLOR = ["#ffa0a0", "#ffff99", "#a0a0ff",
                   "#a0ffa0", "#ffffa0", "#33ccff"]

def DrawCircleBackground(im):
    dr = ImageDraw.Draw(im)
    dr.rectangle([(0, 0), im.size], "white")
    dr = None

    diagonal = int(math.sqrt(float(im.size[0] * im.size[0] + im.size[1] * im.size[1])))
    maxr = max(diagonal / 20, 10)
    minr = max(maxr / 2, 5)
    border = 5 # max(diagonal / 50, 1)
    color_index = 0

    for i in range(40):
        randx = random.randint(0, im.size[0])
        randy = random.randint(0, im.size[1])
        randr = random.randint(minr, maxr)
        imgSize = (randr * 2, randr * 2)

        imDrw = Image.new("RGB", imgSize, CIRCLEBACKCOLOR[color_index])
        color_index = (color_index + 1) % len(CIRCLEBACKCOLOR)
        mask = Image.new("L", imgSize, 0)
        drMask = ImageDraw.Draw(mask)
        drMask.ellipse([(0, 0), imgSize], 150)
        drMask.ellipse([(border, border),
                        (imgSize[0] - border, imgSize[1] - border)], 128)
        im.paste(imDrw, (randx - randr, randy - randr), mask)
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
                           ImageColor.getrgb("white"), 100):
        dr.rectangle([(count, count), (im.size[0]-count, im.size[1]-count)],
                      fill = c)
        count = count + 1
    return im

def DrawBorder(im, width, height):
    bdr = Image.new("RGB", (width, height), "#c0c0c0")
    bdr_alpha = Image.new("L", (width, height), 48)
    im.paste(bdr, (0, 0), bdr_alpha)
    return im

# Size of result image.
LSIDE = 3600 # px
SSIDE = 2400 # px
BORDER = 100 # px

# Border around the photo
THIN_BORDER = 5 #px
THIN_BORDER_COLOR = "#303030"

# photo ratio. No unit, just ratio
PLSIDE = 1
PSSIDE = 1

# Default delegate
BgDrawingFunc = DrawCircleBackground
BgDrawingFuncs = [DrawCircleBackground, DrawBackground]
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
        self.thin_border = THIN_BORDER
        self.thin_border_color = THIN_BORDER_COLOR
        self.is_background_style_rand = True

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

    def setRandomBackgroundStyle(self, isRandom):
        self.is_background_style_rand = isRandom

    def draw(self, im, textOnImage = None):
        # decide background style
        if self.is_background_style_rand:
            self.bgDrawer = BgDrawingFuncs[random.randint(0, len(BgDrawingFuncs) - 1)]

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

        # draw thin border
        drwThinBorder = ImageDraw.Draw(im)
        drwThinBorder.rectangle([self.border - self.thin_border,
                                 self.border - self.thin_border,
                                 self.border + target_width + self.thin_border,
                                 self.border + target_height + self.thin_border],
                                self.thin_border_color)
        drwThinBorder = None

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

if __name__ == "__main__":
    s = Stylizer()
    s.draw(Image.open(sys.argv[1]), None).save(sys.argv[2])
