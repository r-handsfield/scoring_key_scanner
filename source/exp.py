# Exploratory code for identifying conversion tables on the relevant ACT pages.

import os, sys, cv2
import pickle
import numpy as np
from os.path import join, abspath

sys.path.append('./classes')
from classes.dewarper import Dewarper
from classes.deshadower import Deshadower
from classes.sheetScanner import Sheet

PATH = "./"

### Deskew the image
dw = Dewarper(path_ref, path_img)
dw.dewarp()
conf_image = dw.dewarped

### Remove shadows and lighting artifacts
ds = Deshadower(dw.dewarped)
thr_img = ds.deshadow()

# cv2.imshow("Dewarped", conf_image)
# cv2.imshow("Dehsadowed", thr_img)
# print("Deshadowed Sum", np.sum(thr_img))
# cv2.imshow("Binary", s.binary)
# print("Binary Sum", np.sum(s.binary))
# cv2.waitKey(0)
# cv2.destroyAllWindows()

s = Sheet(thr_img)
# s.show_contours(s.image, "Biggest 5 Contours", s.all_contours[0:5], 2)


#############################################################################

print("Extracting Section Contours\n-----------------------------------")
candidates = s.all_contours[0:5]
for i in range( (len(candidates)-1), -1, -1 ):
    c = candidates[i]
    x,y,w,h = cv2.boundingRect(c)
    area = cv2.contourArea(c)
    ratio = float(w)/float(h)
    print(f"x = {x}\t y = {y}\t w = {w}  h = {h}\t area = {area}   aspect = {round(ratio,5)}")
    s.show_contours(s.image, "Contour", c, 2) 















