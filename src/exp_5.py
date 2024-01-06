# Experiment 5
# Extract all ScoreKey images from a single pdf

import cv2, io, sys
import numpy as np
from PIL import Image
from pypdf import PdfReader
from os.path import join, abspath
from collections import namedtuple
from pdf2image import convert_from_path


PATH = abspath("./images/all.pdf")
print(PATH)

### Get PDF pages
pils = convert_from_path(PATH)#[0]  # <-- PIL Image
for i, p in enumerate(pils):
    print(type(p))
    # p.show()
    p = p.resize((850, 1100))
    p = np.asanyarray(p, dtype='uint8')
    pils[i] = p
    p = cv2.cvtColor(p, cv2.COLOR_RGB2BGR)
    print(type(p), type(pils[i]))
    # cv2.imshow("Page", p)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


images = dict.fromkeys(['e', 'm', 'r', 's', 'score_tabe'])
images['e'] = pils[0]
images['m'] = pils[1]
images['r'] = pils[2]
images['s'] = pils[3]
images['score_tabe'] = pils[4]

print("\n", type(images['e']), sep='')

