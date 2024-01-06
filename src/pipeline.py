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


sys.path.append('./classes')
from classes.dewarper import Dewarper
from classes.deshadower import Deshadower
from classes.sheetScanner import Sheet
from scoreKey import ScoreKey


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


### Get PDF pages
pils = convert_from_path(PATH)#[0]  # <-- PIL Image
for i, p in enumerate(pils):
    # print(type(p))
    # p.show()
    # refs[i].show()
    p = p.resize((850, 1100))
    p = np.asanyarray(p, dtype='uint8')
    p = cv2.cvtColor(p, cv2.COLOR_RGB2BGR)
    
    d = Deshadower(p)
    p = d.deshadow()

    d = Dewarper(refs[i], p)
    d.dewarp()
    pils[i] = d.dewarped
    # print(type(p), type(pils[i]))
    # cv2.imshow("Page", p)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

images = dict.fromkeys(['e', 'm', 'r', 's', 'score_tabe'])
images['e'] = pils[0]
images['m'] = pils[1]
images['r'] = pils[2]
images['s'] = pils[2]
images['score_tabe'] = pils[3]

print("\n", type(images['e']), sep='')

### Extract the Scorekeys from Each Page
score_keys = dict.fromkeys(['e1', 'e2', 'm1', 'm2', 'r1', 'r2', 's1', 's2'])
score_keys['e1'] = ScoreKey( 74, 223, 164, 708, 116112, 0.23164)
score_keys['e2'] = ScoreKey(277, 223, 163, 691, 112633, 0.23589)
score_keys['m1'] = ScoreKey( 74,  94, 300, 586, 175800, 0.51195)
score_keys['m2'] = ScoreKey(476,  94, 300, 586, 175800, 0.51195)
score_keys['r1'] = ScoreKey( 74,  94, 164, 407,  66748, 0.40295)
score_keys['r2'] = ScoreKey(277,  94, 163, 407,  66341, 0.40049)
score_keys['s1'] = ScoreKey( 74, 594, 164, 407,  66748, 0.40295)
score_keys['s2'] = ScoreKey(277, 594, 163, 407,  66341, 0.40049)


