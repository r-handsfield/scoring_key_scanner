# Pipeline
# Input pdf should contain only the ScoreKey pages and the Scoring Table page 
# (4 pages total)

import os, sys, cv2
import pickle
import argparse
import numpy as np
from os.path import join, abspath
from dataclasses import dataclass
import pytesseract as pt
from pytesseract import Output
from pdf2image import convert_from_path
from imutils.contours import sort_contours


sys.path.append('./classes')
from classes.dewarper import Dewarper
from classes.deshadower import Deshadower
from classes.sheetScanner import Sheet
from scoreKey import ScoreKey, Column


ap = argparse.ArgumentParser()
ap.add_argument('--pdf_path', '-p', required=True, help='path/to/pdf_file')
args = ap.parse_args()

PATH = abspath(args.pdf_path)
PATH_REF = abspath("./images/all.pdf")
print(PATH)

### Get reference images
refs = convert_from_path(PATH_REF)
for i, p in enumerate(refs):
    p = p.resize((850, 1100))
    p = np.asarray(p, dtype='uint8')
    refs[i] = p


### Get PDF pages, convert to each PNG
pils = convert_from_path(PATH)#[0]  # <-- PIL Image
for i, p in enumerate(pils):
    p = p.resize((850, 1100))
    p = np.asanyarray(p, dtype='uint8')
    p = cv2.cvtColor(p, cv2.COLOR_RGB2BGR)
    
    # Introduces color artifacts
    # d = Deshadower(p)
    # p = d.deshadow()

    d = Dewarper(refs[i], p)
    d.dewarp()
    pils[i] = d.dewarped


# Full page images
images = dict.fromkeys(['e', 'm', 'r', 's', 'score_table'])
images['e'] = pils[0]
images['m'] = pils[1]
images['r'] = pils[2]
images['s'] = pils[2]
images['score_table'] = pils[3]

print("\n", type(images['e']), sep='')

### Extract the Scorekeys from Each Page
# @TODO Extract the Scoring Table from final page
score_keys = dict.fromkeys(['e1', 'e2', 'm1', 'm2', 'r1', 'r2', 's1', 's2'])
score_keys['e'] = ScoreKey('e', images['e'])
score_keys['m'] = ScoreKey('m', images['m'])
score_keys['r'] = ScoreKey('r', images['r'])
score_keys['s'] = ScoreKey('s', images['s'])

for code in ('e', 'm', 'r', 's'):
    cv2.imshow(f'{code}1', score_keys[code].images[0])
    cv2.imshow(f'{code}2', score_keys[code].images[1])
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Find all category marks in the Scoring Box
# @TODO Iterate through both images in each ScoreKey object
for code in ('e', 'm', 'r', 's'):
    sk = score_keys[code]

    for i, image in enumerate(sk.images):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,1))
        closed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        closed_bin = cv2.threshold(closed, 250, 255, cv2.THRESH_BINARY)[1]
        closed_inv = cv2.threshold(closed, 250, 255, cv2.THRESH_BINARY_INV)[1]

        contours = cv2.findContours(closed_inv, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
        
        markers = sk.extract_markers(contours)

        pic = image.copy()
        cv2.drawContours(pic, markers, -1, (0,0,255), 1)
        cv2.imshow(f"{code}{i+1} Markers", pic)
        cv2.waitKey(0) 
    cv2.destroyAllWindows()


    # for c in candidates:
    #     x,y,w,h = cv2.boundingRect(c)
    #     area = w*h  # More accurate than cv2.contourArea
    #     ratio = float(w)/float(h)
    #     print(f"x = {x}  y = {y}  w = {w}  h = {h}   area = {area}   aspect = {round(ratio,5)}")
    #     pic = sk.image.copy()
    #     cv2.drawContours(pic, [c], -1, (0,0,255), 1)
    #     cv2.imshow("C", pic)

    #     if cv2.waitKey(0) == 27:  # Esc will kill the display loop
    #         cv2.destroyAllWindows()
    #         break

