# Experiment 4:  Extract question positions and line markers from a column.
#
# Results:
# E: x0, y0, yL, vStride
#     4, 70, 76, 16.66 px   
# M: x0, y0, yL, vStride
#     4, 81, 87, 16.66 px   
# R: x0, y0, yL, vStride
#     4, 70, 76, 16.66 px   
# S: x0, y0, yL, vStride
#     4, 70, 76, 16.66 px   
# 
# By trial and error, we determine that the row height is 16.66 px; the 
# starting position is the same for ERS table data, and a bit lower for
# M table data.

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
PATH = PATH_M

### Convert PDF to CV_Image
pdf_image = convert_from_path(PATH)[0]  # <-- PIL Image
pdf_image = pdf_image.resize((850,1100))
pdf_image = np.asarray(pdf_image, dtype='uint8')  # <-- np array
pdf_image = cv2.cvtColor(pdf_image, cv2.COLOR_RGB2BGR)

# From Experiment 1:
score_keys = dict.fromkeys(['e1', 'e2', 'm1', 'm2', 'r1', 'r2', 's1', 's2'])
score_keys['e1'] = ScoreKey( 74, 223, 164, 708, 116112, 0.23164)
score_keys['e2'] = ScoreKey(277, 223, 163, 691, 112633, 0.23589)
score_keys['m1'] = ScoreKey( 74,  94, 300, 586, 175800, 0.51195)
score_keys['m2'] = ScoreKey(476,  94, 300, 586, 175800, 0.51195)
score_keys['r1'] = ScoreKey( 74,  94, 164, 407,  66748, 0.40295)
score_keys['r2'] = ScoreKey(277,  94, 163, 407,  66341, 0.40049)
score_keys['s1'] = ScoreKey( 74, 594, 164, 407,  66748, 0.40295)
score_keys['s2'] = ScoreKey(277, 594, 163, 407,  66341, 0.40049)

### Subset Score Key from page
sk = score_keys['m2']
x, y, w, h = sk.x, sk.y, sk.w, sk.h
sk_image = pdf_image[y:y+h, x:x+w]
gray = cv2.cvtColor(sk_image, cv2.COLOR_BGR2GRAY)
bin = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)[1]
inv = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)[1]

# Find number/answer postions
for q in range(38):
    pic = sk_image.copy()
    x0, y0 = 4, 87 + int(q*16.66)
    x1, y1 = x0+226, y0+16
    # x0, y0 = 4, 81 + int(q*16.66)
    # x1, y1 = x0+26, y0+16
    cv2.rectangle(pic, (x0, y0), (x1, y1), (0,0,255), 1)
    cv2.imshow("Rectangle", pic)

    if cv2.waitKey(0) == 27:  # Esc will kill the display loop
        cv2.destroyAllWindows()
        break

# E: x0, y0, yL, vStride
#     4, 70, 76, 16.66 px   
# M: x0, y0, yL, vStride
#     4, 81, 87, 16.66 px   
# R: x0, y0, yL, vStride
#     4, 70, 76, 16.66 px   
# S: x0, y0, yL, vStride
#     4, 70, 76, 16.66 px   
 

