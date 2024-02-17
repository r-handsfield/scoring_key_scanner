# Experiment 6:  Try various morph operations to improve line marker detection.
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
# score_keys = dict.fromkeys(['e1', 'e2', 'm1', 'm2', 'r1', 'r2', 's1', 's2'])
# score_keys['e1'] = ScoreKey( 74, 223, 164, 708, 116112, 0.23164)
# score_keys['e2'] = ScoreKey(277, 223, 163, 691, 112633, 0.23589)
# score_keys['m1'] = ScoreKey( 74,  94, 300, 586, 175800, 0.51195)
# score_keys['m2'] = ScoreKey(476,  94, 300, 586, 175800, 0.51195)
# score_keys['r1'] = ScoreKey( 74,  94, 164, 407,  66748, 0.40295)
# score_keys['r2'] = ScoreKey(277,  94, 163, 407,  66341, 0.40049)
# score_keys['s1'] = ScoreKey( 74, 594, 164, 407,  66748, 0.40295)
# score_keys['s2'] = ScoreKey(277, 594, 163, 407,  66341, 0.40049)


### Subset Score Key from page
sk = ScoreKey('m', pdf_image)
sk_image = sk.images[1]
gray = cv2.cvtColor(sk_image, cv2.COLOR_BGR2GRAY)
bin = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)[1]
inv = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)[1]

# Find number row postions
for q in range(38):
    pic = sk_image.copy()
    x0, y0 = 4, 87 + int(q*16.66)
    x1, y1 = x0+226, y0+16
    # x0, y0 = 4, 81 + int(q*16.66)
    # x1, y1 = x0+26, y0+16
    cv2.rectangle(pic, (x0, y0), (x1, y1), (0,0,255), 1)
    cv2.imshow("Rectangle", pic)

    if cv2.waitKey(0) == 27:  # Esc will kill the display loop
        cv2.destroyAllWindows()
        break



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

pic = gray.copy()
pic = cv2.cvtColor(pic, cv2.COLOR_GRAY2BGR)
cv2.drawContours(pic, lines, -1, (0,0,255), 1)
cv2.imshow("Marker Lines", pic)

cv2.waitKey(0)
# cv2.destroyAllWindows()
# if cv2.waitKey(0) == 27:  # Esc will kill the display loop
#     cv2.destroyAllWindows()

# Build dict of marker line contour attributes
marks = {}
for i, l in enumerate(lines):
    x,y,w,h = cv2.boundingRect(l)
    area = w*h
    aspect = float(w)/h

    marks[i] = {'x':x, 'y':y, 'w':w, 'h':h, 'area':area, 'aspect':aspect}

### DataFrame Version ######################################################yy
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


# Convert dataframe to dict just to test how it's done
# print("Category Dict")
# score_key = df_scorekey.T.to_dict()
# for k, v in score_key.items():
#     print(k, ':', v)

# Create template variable dict for injection into category template
row = df_scorekey.loc[7, :]
# print(row.index, row.values, sep='\n')
# cols = (row.index*row.values).unique() 
# cols = tuple(filter(None, cols))
# print(cols, '\n')

small = df_scorekey.loc[1:7, :]
print(small)
def cnames(i, row):
    cols = (row.index*row.values).unique() 
    cols = list(filter(None, cols))
    cols = tuple( [i, cols] )
    return cols

all_cols = []
for r in range(len(small.index)):
    row = small.loc[r+1, :]
    all_cols.append(cnames(r, row))

print(all_cols)
# for r in range(1, len(small.index)+1):
#     print(r, small.loc[])

print("\n### END DataFrame Version", "\n\n\n\n")

### END DataFrame Version ######################################################yy


sys.exit()
###
### NDArray Version #####################################################
# 
print("### Begin ndArray Version \n")

# Sort by y, x for convenience
marker_lines = dict(sorted(marks.items(), key=lambda m: (m[1]['y'], m[1]['x'])))  # dict of marker line contour attributes
# for k, v in marker_lines.items():
#     print(k, v)

unique_x = np.zeros(len(marker_lines), dtype='uint16')
unique_y = np.zeros(len(marker_lines), dtype='uint16')

for i, attrs in marker_lines.items():
    unique_x[i] = attrs['x']
    unique_y[i] = attrs['y']

# print("All x coordinates", unique_x, '', sep='\n')

# Get unique x, y values of marker lines
unique_x = sorted(np.unique(unique_x)) 
unique_y = sorted(np.unique(unique_y))

# print("Unique x coordinates", unique_x, sep='\n')

# Collapse similar x values
if len(unique_x) > 7:
    for i in range(1, len(unique_x)):
        prev, curr = unique_x[i-1], unique_x[i]

        # Collapse values that are within 5px of each other
        if util.close_to(prev, curr, 5):
             unique_x[i] = prev       


# Collapse similar y values
if len(unique_y) > 30:
    for i in range(1, len(unique_y)):
        prev, curr = unique_x[i-1], unique_x[i]
        
        # Collapse values that are within 5px of each other
        if util.close_to(prev, curr, 5):
             unique_y[i] = prev       


# Get unique x, y after collapsing similar values
unique_x = sorted(np.unique(unique_x)) 
unique_y = sorted(np.unique(unique_y))
if len(unique_y) != 30:
    raise ValueError(f"There shold be 30 rows, not {len(unique_y)}.")

print(unique_x, '', sep='\n')


# Create dict of x-values and category names for indexing
cat_labels = ['N', 'A', 'F', 'G', 'S', 'IES', 'MDL']
cat_index =  dict(zip(unique_x, cat_labels))

# Preallocate the array
cat_array = np.zeros((len(unique_y), len(unique_x)), dtype='bool')

# Fill array with category data based on position of marker lines.
for i in range(len(df_contours)):
    x, y = df_contours.loc[i, 'x'], df_contours.loc[i, 'y']
    row = unique_y.index(y) 

    x = min(unique_x, key=lambda el:abs(el-x)) # Align x to closest unique value
    col = unique_x.index(x)
    # print(i, x, y, row, col)
    cat_array[row, col] = True
print("Category Array", cat_array, '', sep='\n')

###
### Dict Version #####################################################
# 
# This version skips the dataframes and constructs indexing dicts that
# are used to match the marker's position with the questions and category
# 
# Results: The dict version requires mgmt of too many indices, data 
# structures, and argument types. The DataFrame version is better.
#

sys.exit()
sys.exit()
print("### Begin Dict Version \n")

# Sort by y, x for convenience
marker_lines = dict(sorted(marks.items(), key=lambda m: (m[1]['y'], m[1]['x'])))  # dict of marker line contour attributes
for k, v in marker_lines.items():
    print(k, v)

unique_x = np.zeros(len(marker_lines), dtype='uint16')
unique_y = np.zeros(len(marker_lines), dtype='uint16')

for i, attrs in marker_lines.items():
    unique_x[i] = attrs['x']
    unique_y[i] = attrs['y']

print("All x coordinates", unique_x, '', sep='\n')

# Get unique x, y values of marker lines
unique_x = sorted(np.unique(unique_x)) 
unique_y = sorted(np.unique(unique_y))

print("Unique x coordinates", unique_x, sep='\n')

# Collapse similar x values
if len(unique_x) > 7:
    for i in range(1, len(unique_x)):
        prev, curr = unique_x[i-1], unique_x[i]

        # Collapse values that are within 5px of each other
        if util.close_to(prev, curr, 5):
             unique_x[i] = prev       


# Collapse similar y values
if len(unique_y) > 30:
    for i in range(1, len(unique_y)):
        prev, curr = unique_x[i-1], unique_x[i]
        
        # Collapse values that are within 5px of each other
        if util.close_to(prev, curr, 5):
             unique_y[i] = prev       


# Get unique x, y after collapsing similar values
unique_x = sorted(np.unique(unique_x)) 
unique_y = sorted(np.unique(unique_y))
if len(unique_y) != 30:
    raise ValueError(f"There shold be 30 rows, not {len(unique_y)}.")

print(unique_x, '', sep='\n')


# Create dict of x-values and category names for indexing
cat_labels = ['N', 'A', 'F', 'G', 'S', 'IES', 'MDL']
cat_index =  dict(zip(unique_x, cat_labels))

# Create dict of y-values and question numbers for indexing
row_index = dict(zip(unique_y, range(1, len(unique_y)+1)))
print(cat_index, '', sep='\n')

results = {}
for m in marker_lines.values():
    q = row_index[m['y']]

    el = m['x']
    x = min(unique_x, key=lambda el:abs(el-x)) # Align x to closest unique value
    cat = cat_index[x]

    if results.get(q, False): # If the question already has a category,
        results[q] += f', {cat}' # append the additional category
    else:
        results[q] = cat

for k, v in results.items():
    print(k, ':', v)



