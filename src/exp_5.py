# Experiment 5
# Extract all ScoreKey images from a single pdf

import cv2, io, sys
import numpy as np
from PIL import Image
from pypdf import PdfReader
from os.path import join, abspath
from collections import namedtuple
from pdf2image import convert_from_path

sys.path.append('./classes')
from classes.dewarper import Dewarper
from classes.deshadower import Deshadower


PATH = abspath("./images/all.pdf")
PATH_REF = abspath("./images/all.pdf")
print(PATH)

# ap = argparse.ArgumentParser()
# ap.add_argument('--pdf_path', '-p', required=True, help='path/to/pdf_file')
# ap.add_argument('--page_nums', '-n', required=True, help='page numbers, format = first-last')
# args = ap.parse_args()

# PATH = args.pdf_path

# pages = args.page_nums
# first = int(pages.split('-')[0])
# last = int(pages.split('-')[1])
# print(first, last)

### Get reference images
refs = convert_from_path(PATH_REF)
for i, p in enumerate(refs):
    p = p.resize((850, 1100))
    p = np.asarray(p, dtype='uint8')
    refs[i] = p


### Get PDF pages
pils = convert_from_path(PATH)#[0]  # <-- PIL Image
for i, p in enumerate(pils):
    print(type(p))
    # p.show()
    # refs[i].show()
    p = p.resize((850, 1100))
    p = np.asanyarray(p, dtype='uint8')
    p = cv2.cvtColor(p, cv2.COLOR_RGB2BGR)
    
    d = Deshadower(p)
    p = d.deshadow()

    d = Dewarper(refs[i], p)
    # d.sift('ref')
    # d.sift('img')
    # d.fann()
    # d.filter_matches()
    # d.get_homography()
    # d.apply_transform()
    # d.show_homography()
    d.dewarp()

    pils[i] = d.dewarped
    print(type(p), type(pils[i]))
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

