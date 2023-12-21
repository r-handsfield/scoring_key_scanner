# Experiment 1
# Extract images of the scoring keys from their pages.
import cv2, io, sys
import numpy as np
from PIL import Image
from pypdf import PdfReader
from os.path import join, abspath
from collections import namedtuple
from pdf2image import convert_from_path


PATH_E = abspath("./images/ske.pdf")
# PATH_M = abspath("./images/skm.pdf")
# PATH_R = abspath("./images/skr.pdf")
# PATH_S = abspath("./images/sks.pdf")

### Convert PDF to CV_Image
pdf_image = convert_from_path(PATH_E)[0]  # <-- PIL Image
pdf_image = pdf_image.resize((850,1100))
pdf_image = np.asarray(pdf_image, dtype='uint8')  # <-- np array
pdf_image = cv2.cvtColor(pdf_image, cv2.COLOR_RGB2BGR)
print(type(pdf_image), pdf_image.shape)

# cv2.imshow("Img", pdf_image)
# cv2.waitKey(0)


### Extract 5 Largest Contours
gray = cv2.cvtColor(pdf_image, cv2.COLOR_BGR2GRAY)
bin = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)[1]
inv = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)[1]
candidates = list(cv2.findContours(inv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0])

print(len(candidates))
# delete candidates that are too small to be a scoring key
for i in range( (len(candidates)-1), -1, -1 ):
    c = candidates[i]
    area = cv2.contourArea(c)
    if area < 1000:
        del(candidates[i])

print(len(candidates))
candidates= sorted(candidates, key=cv2.contourArea, reverse=True)[0:5]
print(len(candidates))

for c in candidates:
    x,y,w,h = cv2.boundingRect(c)
    area = w*h  # More accurate than cv2.contourArea
    ratio = float(w)/float(h)
    print(f"x = {x}  y = {y}  w = {w}  h = {h}\t area = {area}   aspect = {round(ratio,5)}")
    pic = pdf_image.copy()
    cv2.drawContours(pic, [c], -1, (0,0,255), 1)
    cv2.imshow("C", pic)

    if cv2.waitKey(0) == 27:  # Esc will kill the display loop
        cv2.destroyAllWindows()
        break

### Visual inspection yields the following parameters
# e1 x = 74  y = 223  w = 164  h = 708	 area = 116112   aspect = 0.23164
# e2 x = 277  y = 223  w = 163  h = 691	 area = 112633   aspect = 0.23589
# m1 x = 74  y = 94  w = 300  h = 586	 area = 175800   aspect = 0.51195
# m2 x = 476  y = 94  w = 300  h = 586	 area = 175800   aspect = 0.51195
# r1 x = 74  y = 94  w = 164  h = 407	 area = 66748   aspect = 0.40295
# r2 x = 277  y = 94  w = 163  h = 407	 area = 66341   aspect = 0.40049
# s1 x = 74  y = 594  w = 164  h = 407	 area = 66748   aspect = 0.40295
# s2 x = 277  y = 594  w = 163  h = 407	 area = 66341   aspect = 0.40049

# from visual inspection
ScoreKey = namedtuple('ScoreKey', ['x', 'y', 'w', 'h', 'area', 'aspect'])
score_keys = dict.fromkeys(['e1', 'e2', 'm1', 'm2', 'r1', 'r2', 's1', 's2'])
score_keys['e1'] = ScoreKey( 74, 223, 164, 708, 116112, 0.23164)
score_keys['e2'] = ScoreKey(277, 223, 163, 691, 112633, 0.23589)
score_keys['m1'] = ScoreKey( 74,  94, 300, 586, 175800, 0.51195)
score_keys['m2'] = ScoreKey(476,  94, 300, 586, 175800, 0.51195)
score_keys['r1'] = ScoreKey( 74,  94, 164, 407,  66748, 0.40295)
score_keys['r2'] = ScoreKey(277,  94, 163, 407,  66341, 0.40049)
score_keys['s1'] = ScoreKey( 74, 594, 164, 407,  66748, 0.40295)
score_keys['s2'] = ScoreKey(277, 594, 163, 407,  66341, 0.40049)

### Extract score key by subsetting region from original image
for label in ['e1']:
    sk = score_keys[label]
    key_image = pdf_image[sk.y:sk.y+sk.h, sk.x:sk.x+sk.w]
    print(sk)

cv2.imshow("Img", key_image)
cv2.waitKey(0)

