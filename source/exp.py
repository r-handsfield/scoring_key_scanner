# Exploratory code for identifying conversion tables on the relevant ACT pages.

import os, sys, cv2
import pickle
import numpy as np
from os.path import join, abspath

sys.path.append('./classes')
from classes.dewarper import Dewarper
from classes.deshadower import Deshadower
from classes.sheetScanner import Sheet

PATH = "./images"

image_paths = []
for f in os.listdir(PATH):
    if f.split('.')[1] == 'png':
        # print(f)
        image_paths.append(abspath(join(PATH, f)))
image_paths = sorted(image_paths)
# print(image_paths)

### Deskew the image
# dw = Dewarper(path_ref, path_img)
# dw.dewarp()
# conf_image = dw.dewarped

### Remove shadows and lighting artifacts
# ds = Deshadower(dw.dewarped)
# thr_img = ds.deshadow()

# cv2.imshow("Dewarped", conf_image)
# cv2.imshow("Dehsadowed", thr_img)
# print("Deshadowed Sum", np.sum(thr_img))
# cv2.imshow("Binary", s.binary)
# print("Binary Sum", np.sum(s.binary))
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# for p in image_paths:
    # s = Sheet(p)
    # s.show_contours(s.image, "Biggest 5 Contours", s.all_contours[0:5], 2)
    # for c in s.all_contours[0:5]:
    #     x,y,w,h = cv2.boundingRect(c)
    #     area = cv2.contourArea(c)
    #     ratio = float(w)/float(h)
        # print(f"x = {x}\t y = {y}\t w = {w}  h = {h}\t area = {area}   aspect = {round(ratio,5)}")
        # s.show_contours(s.image, "Contour", [c], 0) 


# s = Sheet(image_paths[1])

### Table in page
img = cv2.imread(image_paths[1], flags=cv2.IMREAD_GRAYSCALE)
m1 = img[94:94+585, 75:75+298]
m1i = cv2.threshold(m1, 250, 255, cv2.THRESH_BINARY_INV)[1]
cv2.imshow("Ref", m1i)
cv2.waitKey(0)

candidates = list(cv2.findContours(m1i, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0])

# Delete point contours
for i in range( (len(candidates)-1), -1, -1 ):
    c = candidates[i]
    x,y,w,h = cv2.boundingRect(c)
    area = cv2.contourArea(c)
    if area < 1:
        del(candidates[i])

print(len(candidates), type(candidates))

m1 = cv2.cvtColor(m1, cv2.COLOR_GRAY2BGR)
for i,c in enumerate(candidates):
    x,y,w,h = cv2.boundingRect(c)
    area = cv2.contourArea(c)
    ratio = float(w)/float(h)
    if area < 10000:
        continue
    print(f"{i}\tx = {x}  y = {y}\t w = {w}  h = {h}\t area = {area}   aspect = {round(ratio,5)}")
    pic = m1.copy()
    cv2.drawContours(pic, [c], -1, (0,0,255), 1)
    cv2.imshow("C", pic)

    if cv2.waitKey(0) == 27:  # Esc will kill the method
        cv2.destroyAllWindows()
        break

### Column in Table
m1 = cv2.cvtColor(m1, cv2.COLOR_BGR2GRAY)
col = m1[77:77+508, 263:263+35]
coli = cv2.threshold(col, 250, 255, cv2.THRESH_BINARY_INV)[1]
cv2.imshow("Ref", coli)
cv2.waitKey(0)

candidates = list(cv2.findContours(coli, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0])

# Delete point contours
for i in range( (len(candidates)-1), -1, -1 ):
    c = candidates[i]
    x,y,w,h = cv2.boundingRect(c)
    if float(w)/float(h) < 1 or w > 25:
        del(candidates[i])

col = cv2.cvtColor(col, cv2.COLOR_GRAY2BGR)
for i,c in enumerate(candidates):
    x,y,w,h = cv2.boundingRect(c)
    area = cv2.contourArea(c)
    ratio = float(w)/float(h)
    print(f"{i}\tx = {x}  y = {y}\t w = {w}  h = {h}\t area = {area}   aspect = {round(ratio,5)}")
    pic = col.copy()
    cv2.drawContours(pic, [c], -1, (0,0,255), 1)
    cv2.imshow("C", pic)

    if cv2.waitKey(0) == 27:  # Esc will kill the method
        cv2.destroyAllWindows()
        break
sys.exit()


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















