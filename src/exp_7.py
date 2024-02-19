# Experiment 7:  Convert one-hot dataframe to category strings
#
# 

import cv2, io, sys
import numpy as np
import pandas as pd
from PIL import Image
from pypdf import PdfReader
from os.path import join, abspath
from collections import namedtuple
from pdf2image import convert_from_path
from imutils.contours import sort_contours

sys.path.append('classes')

from scoreKey import ScoreKey
from sheetUtilities import SheetUtilities

util = SheetUtilities()

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

# Find number row postions
for q in range(38):
    pic = sk_image.copy()
    x0, y0 = 4, 87 + int(q*16.66)
    x1, y1 = x0+226, y0+16
    # cv2.rectangle(pic, (x0, y0), (x1, y1), (0,0,255), 1)
    # cv2.imshow("Rectangle", pic)

    # if cv2.waitKey(0) == 27:  # Esc will kill the display loop
    #     cv2.destroyAllWindows()
    #     break



# Close contours to improve line detection
# Kernel is a horizontal line (cols, rows)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,1))
closed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
closed_bin = cv2.threshold(closed, 250, 255, cv2.THRESH_BINARY)[1]
closed_inv = cv2.threshold(closed, 250, 255, cv2.THRESH_BINARY_INV)[1]

contours = cv2.findContours(closed_inv, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
candidates = list(contours)


### Filter the marker lines using a function
def filter_fcn(contour):
    c = contour
    x,y,w,h = cv2.boundingRect(c)
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
    
# the marker lines
lines = list(filter(filter_fcn, list(contours)))
print(len(lines))

# Build dict of marker line contour attributes
marks = {}
for i, l in enumerate(lines):
    x,y,w,h = cv2.boundingRect(l)
    area = w*h
    aspect = float(w)/h

    marks[i] = {'x':x, 'y':y, 'w':w, 'h':h, 'area':area, 'aspect':aspect}

### DataFrame Version ######################################################
# 
# This version builds dataframes and interates through them to match the
# marker position to a question and category.

# Use the dict to build a dataframe for easy viewing & operations
df_contours = pd.DataFrame(data=marks).T
print(df_contours, '', sep='\n')

# Get unique x, y valued of marker lines
unique_x = sorted(df_contours.x.unique()) 
unique_y = sorted(df_contours.y.unique())
print("Unique x coordinates", unique_x, sep='\n')

if len(unique_x) > 7:
    for i in range(1, len(unique_x)):
        prev, curr = unique_x[i-1], unique_x[i]

        # Collapse values that are within 5px of each other
        if util.close_to(prev, curr, 5):
             unique_x[i] = prev       

unique_x = pd.Series(unique_x).unique()
print(unique_x, '', sep='\n')

if len(unique_y) != 30:
    raise ValueError(f"There shold be 30 rows, not {len(unique_y)}.")

# Create dict of x-values and column names for indexing into the Key df
col_labels = ['N', 'A', 'F', 'G', 'S', 'IES', 'MDL']
col_index =  dict(zip(unique_x, col_labels))

# Initialize dataframe to hold category data
df_scorekey = pd.DataFrame(data=np.zeros((30, 7), dtype='bool'), index=range(1,31), columns=col_labels)

# Fill dataframe with category data based on position of marker lines.
for i in range(len(df_contours)):
    x, y = df_contours.loc[i, 'x'], df_contours.loc[i, 'y']
    row = 1 + unique_y.index(y) 
    x = min(unique_x, key=lambda el:abs(el-x)) # Align x to closest unique value
    col = col_index[x]
    # print(i, x, y, row, col)
    df_scorekey.loc[row, col] = True
print("Category Dataframe", df_scorekey, '', sep='\n')



### Create template variable dict for injection into category template
# row = df_scorekey.loc[7, :]
# print(row.index, row.values, sep='\n')
# cols = (row.index*row.values).unique() 
# cols = tuple(filter(None, cols))
# print(cols, '\n')

small = df_scorekey.loc[1:7, :]
print(small, '\n')
def cnames(row):
    cols = (row.index*row.values).unique() 
    cols = list(filter(None, cols))
    cols = tuple( cols )
    return cols

all_cols = []
for r in range(len(small.index)):
    row = small.loc[r+1, :]
    all_cols.append(cnames(row))

# print(all_cols)
# for r in range(1, len(small.index)+1):
#     print(r, small.loc[])

sid = 'm'
all_cols = {}
for r in range(len(df_scorekey.index)):
    row = df_scorekey.loc[r+1, :]
    key = f'{sid}C{r+31}'
    all_cols[key] = cnames(row)
print(all_cols, '\n')

for k, v in all_cols.items():
    txt = ''
    for c in v:
        txt += f'"{c}",'
    txt = txt[:-1]
    all_cols[k] = txt

print(all_cols)



