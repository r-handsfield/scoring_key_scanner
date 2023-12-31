# Exploratory code for identifying conversion tables on the relevant ACT pages.

import os, sys, cv2
import pickle
import numpy as np
from os.path import join, abspath
from dataclasses import dataclass
import pytesseract as pt
from pytesseract import Output

sys.path.append('./classes')
from classes.dewarper import Dewarper
from classes.deshadower import Deshadower
from classes.sheetScanner import Sheet

PATH = "./images"



# Functions #########################
@dataclass 
class Line():
    def __init__(contour):
        x,y,w,h = cv2.boundingRect(contour)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.area = w*h
        self.ratio = round(float(w)/h, 5) # aspect ratio


def extract_text(source):
    """
    
    Extracts question numbers and answers from an image.

    Parameters
    ----------
    source : CV_Image

    """
    # img = cv2.imread(image_paths[1])  # Math Key
    # src = img[94:94+585, 75:75+298]
    src = source
    col = src[77:77+508, 0:0+60]
    colG = cv2.cvtColor(col, cv2.COLOR_BGR2GRAY)
    colI = cv2.threshold(colG, 250, 255, cv2.THRESH_BINARY_INV)[1]
    cv2.imshow("Answer Key", colG)
    cv2.waitKey(0)

    rgb = cv2.cvtColor(col, cv2.COLOR_BGR2RGB)
    data = pt.image_to_data(rgb, config="--psm 11", output_type=Output.DICT)
    print(len(data['text']), len(data['top']), len(data['left']))
    print(data.keys(), '\n')
    # print(data['text'], data['left'], data['top'], sep='\t')
    text, conf = data['text'], data['conf']
    X,Y,W,H = data['left'], data['top'], data['width'], data['height']

    # Delete entries with low confidence
    for i in range( (len(X)-1), -1, -1 ):
        ar = round(float(W[i])/H[i], 3)
        if conf[i] < 1:
            del(conf[i])
            del(text[i])
            del(X[i])
            del(Y[i])
            del(W[i])
            del(H[i])
        elif ar < 1 or ar > 2:
            del(conf[i])
            del(text[i])
            del(X[i])
            del(Y[i])
            del(W[i])
            del(H[i])

    for i in range(len(X)):
        x,y,w,h = X[i], Y[i], W[i], H[i]
        ar = round(float(w)/h, 3)
        print(f"{i}\tconf = {conf[i]}\ttext = {text[i]} \t x = {x}\ty = {y}\tw = {w}\th = {h}\tar = {ar}")
        img = col.copy()
        cv2.rectangle(img, (x, y), (x+w, y+h), (0,0,255), 1)
        # cv2.rectangle(img, (1, 1), (50, 59), (0,0,255), 1)
        cv2.imshow("Text", img)
        if cv2.waitKey(0) == 27: 
            cv2.destroyAllWindows()
            break


def extract_lines(image, show=False):
    """
    image : CV_Image
    """
    if len(image.shape) < 3:
        gray = image
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY2)

    inv = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)[1]

    candidates = list(cv2.findContours(inv, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0])

    # Delete point contours
    for i in range( (len(candidates)-1), -1, -1 ):
        c = candidates[i]
        x,y,w,h = cv2.boundingRect(c)
        if float(w)/float(h) < 8 or w > 25:
            del(candidates[i])

    # Show line contours in column
    pic = image.copy()
    for i,c in enumerate(candidates):
        x,y,w,h = cv2.boundingRect(c)
        area = cv2.contourArea(c)
        ratio = float(w)/float(h)
        print(f"{i}\tx = {x}  y = {y}\t w = {w}  h = {h}\t area = {area}   aspect = {round(ratio,5)}")
        # pic = image.copy()
        cv2.drawContours(pic, [c], -1, (0,0,255), 1)
    
    cv2.imshow("C", pic)
    
    if cv2.waitKey(0) == 27:  # Esc will kill the method
        cv2.destroyAllWindows()
        # break

    return candidates


def extract_row_coords(y_coords):
    """
    Returns the coordinates of each row within the Key.

    Parameters
    ----------
    y_coords : list[int]
        A llist of y-coordinates

    Returns
    -------
    dict : {int:int}
        Key = a y-coordinate
        Val = a question number
    """
    rows = np.unique(y_coords)
    qNums = range(1, len(y_coords)+1)

    return dict(zip(rows, qNums))



# END Functions #########################


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
# m1 = img[94:94+585, 75:75+298]
m1 = img[94:94+585, 75:75+298]
lines = extract_lines(m1)
sys.exit()

Y = [None]*len(lines)
for i,c in enumerate(lines):
    x,y,w,h = cv2.boundingRect(c)
    Y[i] = y

rows = extract_row_coords(Y)
print(rows)
sys.exit(0)
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

sys.exit()
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

# Show line contours in column
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




### Identify row coordinates
m1 = cv2.cvtColor(m1, cv2.COLOR_GRAY2BGR)
for i in range(30):
    x, w = 5, 20+278
    y, h = int(88+i*16.65), 13
    pic = m1.copy()
    cv2.rectangle(pic, (x, y), (x+w, y+h), (0,0,255), 1)
    cv2.imshow("Y", pic)
    if cv2.waitKey(0) == 27:  # Esc will kill the method
        cv2.destroyAllWindows()
        break
# Extract text from Answer Key Column
# img = cv2.imread(image_paths[1])
# src = img[94:94+585, 75:75+298]
# extract_text(src)

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















