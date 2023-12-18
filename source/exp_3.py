# Experiment 3:  E, R, S columns are bounded by closed contours. Howevver,
# several of the Math columns are bounded by dotted lines, requiring a
# different approach to determine their Box parameters. (See the Box class)

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

PATH_M = abspath("./images/skm.pdf")
PATH = PATH_M

### Convert PDF to CV_Image
pdf_image = convert_from_path(PATH)[0]  # <-- PIL Image
pdf_image = pdf_image.resize((850,1100))
pdf_image = np.asarray(pdf_image, dtype='uint8')  # <-- np array
pdf_image = cv2.cvtColor(pdf_image, cv2.COLOR_RGB2BGR)

# From Experiment 1:
score_keys = dict.fromkeys(['e1', 'e2', 'm1', 'm2', 'r1', 'r2', 's1', 's2'])
score_keys['m1'] = ScoreKey( 74,  94, 300, 586, 175800, 0.51195)
score_keys['m2'] = ScoreKey(476,  94, 300, 586, 175800, 0.51195)

### Subset Score Key from page
sk = score_keys['m2']
x, y, w, h = sk.x, sk.y, sk.w, sk.h
sk_image = pdf_image[y:y+h, x:x+w]
gray = cv2.cvtColor(sk_image, cv2.COLOR_BGR2GRAY)
bin = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)[1]
inv = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)[1]


### Close the dashed lines between some of the columns
# closed = gray.copy()
# closed = cv2.GaussianBlur(gray, (3, 3), 0)
# closed = cv2.morphologyEx(closed, cv2.MORPH_CLOSE, kernel)

# inv = cv2.threshold(closed, 250, 255, cv2.THRESH_BINARY_INV)[1]
# cv2.imshow("Score Key Img", gray)
# cv2.imshow("Closed Img", closed)
# cv2.waitKey(0)

# RESULT: The column contours are shifted and imprecise. Use alternate
# box locations instead.


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
candidates = list(sort_contours(candidates, method='left-to-right')[0])
tmp = candidates[0]
print(type(tmp), len(tmp), type(tmp[0]), type(tmp[0][0]), type(tmp[0][0][0]))
print(tmp)
tmp = candidates[1]
print(type(tmp), len(tmp))
print(tmp)

# Show the contours
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

# Create virtual contours for the dotted line columns
print("")
phm = candidates[2] # The PHM contour
X,Y,W,H = cv2.boundingRect(phm)
for i in range(5):
    x = X + i*34
    y = Y
    w = W//5
    h = H
    area = w*h  # More accurate than cv2.contourArea
    ratio = float(w)/float(h)
    print(f"x = {x}  y = {y}  w = {w}  h = {h}   area = {area}   aspect = {round(ratio,5)}")

    # Append virtual contour to candidates
    vc = np.array([[[x,y]], [[x+w,y]], [[x+w, y+h]], [[x,y+h]]], dtype='int32')
    # tmp = vc
    # print(type(tmp), len(tmp), type(tmp[0]), type(tmp[0][0]), type(tmp[0][0][0]))
    candidates.append(vc)


    pic = sk_image.copy()
    cv2.rectangle(pic, (x, y), (x+w, y+h), (0,0,255), 1)
    cv2.imshow("Rectangle", pic)

    if cv2.waitKey(0) == 27:  # Esc will kill the display loop
        cv2.destroyAllWindows()
        break
    

### Sort and display new candidate list
print("\n")
candidates = list(sort_contours(candidates, method='left-to-right')[0])
# del(candidates[2]) # Remove the PHM supercolumn
for c in candidates:
    x,y,w,h = cv2.boundingRect(c)
    area = w*h  # More accurate than cv2.contourArea
    ratio = float(w)/float(h)
    print(f"x = {x}  y = {y}  w = {w}  h = {h}   area = {area}   aspect = {round(ratio,5)}")
    pic = sk_image.copy()
    cv2.drawContours(pic, [c], -1, (0,0,255), 1)
    cv2.imshow("With Virtual Contours", pic)

    if cv2.waitKey(0) == 27:  # Esc will kill the display loop
        cv2.destroyAllWindows()
        break    
