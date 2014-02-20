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
