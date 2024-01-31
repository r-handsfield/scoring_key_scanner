# Experiment 6:  Try various morph operations to improve line marker detection.
#
# 

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


# Find line positions
lines = cv2.HoughLinesP(inv, 20, np.pi/2, 50, minLineLength=10)
# lines = cv2.HoughLinesP(inv, 20, np.pi/2, 1, minLineLength=1)
print(type(lines) , len(lines))
print(type(lines[0]) , len(lines[0]))
# print(lines[0])

pic = sk_image.copy()
for i in range(len(lines)):
    # pic = sk_image.copy() 
    l = lines[i][0]
    x1, y1, x2, y2 = l[0], l[1], l[2], l[3]
    w, h = abs(x2-x1), abs(y2-y1)

    if w/(h+.001) < 1:  # Skip verticals
        continue
    elif w < 3:  # Skip short lines 
        continue
    elif y1 < 80 or y2 < 80:
        continue
    elif y1 > 244 or y2 > 244:
        continue
    elif x1 < 60 or x2 < 60:
        continue

    cv2.line(pic, (x1, y1), (x2, y2), (0,0,255), 1, cv2.LINE_AA )
    print(l)

    cv2.imshow("Lines", pic)

    # if cv2.waitKey(0) == 27:  # Esc will kill the display loop
    #     cv2.destroyAllWindows()
    #     break

if cv2.waitKey(0) == 27:  # Esc will kill the display loop
    cv2.destroyAllWindows()
 

# Close contours to improve line detection
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,1))
gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
bin = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)[1]
inv = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)[1]

contours = cv2.findContours(inv, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
candidates = list(contours)
# print(type(candidates[0]))
# print(candidates[0])


print("")
for i in range( len(candidates)-1, -1, -1):
    x,y,w,h = cv2.boundingRect(candidates[i])
    area = w*h
    aspect = float(w)/h
    
    print(f"{i}: x = {x}\t y = {y}\t w = {w}  h = {h}\t area = {area}   aspect = {round(aspect,5)}")
    
    if aspect < 1:
        del(candidates[i])
    elif area < 20:
        del(candidates[i])
    elif w < 5 or w > 30 or h > 3:
        del(candidates[i])
    elif y < 80 or x < 60:
        del(candidates[i])
        

print(len(candidates))

bin =cv2.cvtColor(bin, cv2.COLOR_GRAY2BGR)
for c in candidates:
    cv2.drawContours(bin, [c], -1, (0,0,255), 1)

# bin = cv2.drawContours(bin, candidates, -1, (0,0,255), 1)
cv2.imshow("Contours", bin)

if cv2.waitKey(0) == 27:  # Esc will kill the display loop
    cv2.destroyAllWindows()


# Not working -- 219 lines after filtering
def filter_fcn(contour):
    c = contour
    x,y,w,h = cv2.boundingRect(candidates[i])
    area = w*h
    aspect = float(w)/h

    if (
        aspect < 1 or
        area < 20 or
        w < 5 or w > 30 or h > 3 or
        y < 80 or x < 60
    ):
        return False
    else:
        return True
    
lines = list(filter(filter_fcn, list(contours)))
print(len(lines))