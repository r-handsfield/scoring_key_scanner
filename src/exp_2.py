# Experiment 2:  Extract columns from the Scoring Key
# This approach works for English, Reading, and Science sections,
# but not for the Math section.

import cv2, io, sys
import numpy as np
from PIL import Image
from pypdf import PdfReader
from os.path import join, abspath
from collections import namedtuple
from pdf2image import convert_from_path
from imutils.contours import sort_contours

sys.path.append('classes')

from scoreKey import ScoreKey

PATH_E = abspath("./images/ske.pdf")
PATH_M = abspath("./images/skm.pdf")
PATH_R = abspath("./images/skr.pdf")
PATH_S = abspath("./images/sks.pdf")
PATH = PATH_S

### Convert PDF to CV_Image
pdf_image = convert_from_path(PATH)[0]  # <-- PIL Image
pdf_image = pdf_image.resize((850,1100))
pdf_image = np.asarray(pdf_image, dtype='uint8')  # <-- np array
pdf_image = cv2.cvtColor(pdf_image, cv2.COLOR_RGB2BGR)

# From Experiment 1:
# score_keys = dict.fromkeys(['e1', 'e2', 'm1', 'm2', 'r1', 'r2', 's1', 's2'])
# score_keys['e1'] = ScoreKey( 74, 223, 164, 708, 116112, 0.23164)
# score_keys['e2'] = ScoreKey(277, 223, 163, 691, 112633, 0.23589)
# score_keys['m1'] = ScoreKey( 74,  94, 300, 586, 175800, 0.51195)
# score_keys['m2'] = ScoreKey(476,  94, 300, 586, 175800, 0.51195)
# score_keys['r1'] = ScoreKey( 74,  94, 164, 407,  66748, 0.40295)
# score_keys['r2'] = ScoreKey(277,  94, 163, 407,  66341, 0.40049)
# score_keys['s1'] = ScoreKey( 74, 594, 164, 407,  66748, 0.40295)
# score_keys['s2'] = ScoreKey(277, 594, 163, 407,  66341, 0.40049)

score_keys = dict.fromkeys(['e', 'm', 'r', 's'])
score_keys['e'] = ScoreKey('e')
score_keys['m'] = ScoreKey('m')
score_keys['r'] = ScoreKey('r')
score_keys['s'] = ScoreKey('s')


### Subset Score Key from page
sk = score_keys['s']
params = sk.tables[0]
x, y, w, h = params.x, params.y, params.w, params.h
sk_image = pdf_image[y:y+h, x:x+w]
gray = cv2.cvtColor(sk_image, cv2.COLOR_BGR2GRAY)
bin = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)[1]
inv = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)[1]

# cv2.imshow("Score Key Img", sk_image)
# cv2.waitKey(0)

### Find the interior contours and extract the columns
candidates = list(cv2.findContours(inv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0])
print(len(candidates))
# delete candidates that are too small to be a column
for i in range( (len(candidates)-1), -1, -1 ):
    c = candidates[i]
    area = cv2.contourArea(c)
    if area < 10000:
        del(candidates[i])

print(len(candidates))

# Sort the columns left-to-rigth
candidates = sort_contours(candidates, method='left-to-right')[0]

for c in candidates:
    x,y,w,h = cv2.boundingRect(c)
    area = w*h  # More accurate than cv2.contourArea
    ratio = float(w)/float(h)
    print(f"x = {x}  y = {y}  w = {w}  h = {h}   area = {area}   aspect = {round(ratio,5)}")
    pic = sk_image.copy()
    cv2.drawContours(pic, [c], -1, (0,0,255), 1)
    cv2.imshow("C", pic)

    if cv2.waitKey(0) == 27:  # Esc will kill the display loop
        cv2.destroyAllWindows()
        break

