# Copyright 2014 Patrick Wang (Chih-Kai Wang) <kk1fff@patrickz.net>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# coding: utf-8

from PIL import Image, ImageDraw, ImageColor, ImageFont
import sys, random, math

class BackgroundBuilder:
    """
    Give a input image as a base image to create background.
    Return a PIL image.
    """
    def drawBackground(self, im):
        raise Exception("Not implemented")

class BorderBuilder:
    """
    borderOuterSize is a tuple (width, height) which denotes
    the outer side dimension.
    """
    def drawBorder(self, im, borderOuterSize):
        raise Exception("Not implemented")

class CircleBackgroundBuilder(BackgroundBuilder):
    CIRCLEBACKCOLOR = ["#ffa0a0", "#ffff99", "#a0a0ff",
                       "#a0ffa0", "#ffffa0", "#33ccff"]
    def __init__(self):
        pass
    def drawBackground(self, im):
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

            imDrw = Image.new("RGB", imgSize, self.CIRCLEBACKCOLOR[color_index])
            color_index = (color_index + 1) % len(self.CIRCLEBACKCOLOR)
            mask = Image.new("L", imgSize, 0)
            drMask = ImageDraw.Draw(mask)
            drMask.ellipse([(0, 0), imgSize], 150)
            drMask.ellipse([(border, border),
                            (imgSize[0] - border, imgSize[1] - border)], 128)
            im.paste(imDrw, (randx - randr, randy - randr), mask)
        return im

class OldStyleBackgroundBuilder(BackgroundBuilder):
    @staticmethod
    def buildGradient(frm, to, step):
    # frm, to: (r, g, b)
        rstep = float(to[0] - frm[0]) / float(step)
        gstep = float(to[1] - frm[1]) / float(step)
        bstep = float(to[2] - frm[2]) / float(step)
        for i in range(step):
            yield (int(frm[0] + rstep * i),
                   int(frm[1] + gstep * i),
                   int(frm[2] + bstep * i))

    def drawBackground(self, im):
        # compute gradient
        dr = ImageDraw.Draw(im)
        count = 0
        for c in self.buildGradient(
                ImageColor.getrgb("#ffffcc"),
                ImageColor.getrgb("white"), 100):
            dr.rectangle([(count, count),
                          (im.size[0]-count, im.size[1]-count)],
                         fill = c)
            count = count + 1
        return im

class RandomBackgroundBuilder(BackgroundBuilder):
    def __init__(self):
        self.builders = []

    def addBackgroundBuilder(self, builder):
        self.builders.append(builder)

    def drawBackground(self, im):
        return self.builders[
            random.randint(0, len(self.builders) - 1)].drawBackground(im)

class BlackBorderBuilder(BorderBuilder):
    def drawBorder(self, im, dimension):
        width, height = dimension
        bdr = Image.new("RGB", (width, height), "#c0c0c0")
        bdr_alpha = Image.new("L", (width, height), 48)
        im.paste(bdr, (0, 0), bdr_alpha)
        return im

class Stylizer:
    # Size of result image.
    LSIDE = 3200 # px
    SSIDE = 2400 # px
    BORDER = 100 # px

    # Border around the photo
    THIN_BORDER = 5 # px
    THIN_BORDER_COLOR = "#303030"

    # photo ratio. No unit, just ratio
    PLSIDE = 1
    PSSIDE = 1

    # Default delegate
    BgBuilderClass = OldStyleBackgroundBuilder
    BdrBuilderClass = BlackBorderBuilder

    # Default font setting
    FONTSIZE = 64

    def __init__(self):
        self.long_side = self.LSIDE
        self.short_side = self.SSIDE
        self.border = self.BORDER
        self.p_long_side = self.PLSIDE
        self.p_short_side = self.PSSIDE
        self.bgBuilder = None
        self.bdrBuilder = None
        self.font = ImageFont.load_default()
        self.thin_border = self.THIN_BORDER
        self.thin_border_color = self.THIN_BORDER_COLOR

    def setOutputDimemsion(self, longSide, shortSide):
        self.long_side = longSide
        self.short_side = shortSide

    def setBorder(self, border):
        self.border = border;

    def setPhotoEdgeRatio(self, longSide, shortSide):
        self.p_long_side = longSide
        self.p_short_side = shortSide

    def setBgBuilder(self, bgBuilder):
        if not isinstance(bgBuilder, BackgroundBuilder):
            raise Exception("only instance of subclass of " +
                            "BackgroundBuilder can be passed to setBgBuilder")
        self.bgBuilder = bgBuilder

    def setBorderBuilder(self, bdrBuilder):
        if not isinstance(bgBuilder, BackgroundBuilder):
            raise Exception("only instance of subclass of " +
                            "BorderBuilder can be passed to setBorderBuilder")
        self.bdrBuilder = bdrBuilder

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
        # Create builder instances is they are not defined.
        if self.bgBuilder == None:
            self.bgBuilder = self.BgBuilderClass()

        if self.bdrBuilder == None:
            self.bdrBuilder = self.BdrBuilderClass()

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

        im = self.bgBuilder.drawBackground(im)

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
        im = self.bdrBuilder.drawBorder(im, (border_box_width, border_box_heigth))

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
