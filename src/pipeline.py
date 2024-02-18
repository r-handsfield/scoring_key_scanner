# Pipeline
# Input pdf should contain only the ScoreKey pages and the Scoring Table page 
# (4 pages total)

import os, sys, cv2
import pickle
import argparse
import numpy as np
import pandas as pd
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
from scoreKey import Box, Marker, ScoreKey, Column
from sheetUtilities import SheetUtilities

util = SheetUtilities()

### Get CLI arguments
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

# print("\n", type(images['e']), sep='')

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
    if cv2.waitKey(0) == 27:
        break
cv2.destroyAllWindows()


### Find all category marks in the Scoring Box images
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
        

        # Offset used to insert the values from the 2nd image into the dict
        j0 = int(0.5*sk.num_questions + 0.5)
        y0 = int(j0*16.66 + 0.5)
        for j, c in enumerate(markers):

            if i == 0: key = j
            elif i == 1: key = j+j0
            else:
                raise ValueError("Something has gone terribly wrong.")
            
            sk.category_marks[key] = Marker(c)

        pic = image.copy()
        cv2.drawContours(pic, markers, -1, (0,0,255), 1)
        cv2.imshow(f"{code}{i+1} Markers", pic)
        # cv2.waitKey(0) 
    cv2.destroyAllWindows()


### Find the unique x, y coordinates of the category marks
for code in ('e', 'm', 'r', 's'):
    sk = score_keys[code]
    unique_x = set()
    unique_y = set()

    for line in sk.category_marks.values():
        unique_x.add(line.box.x) # adds unique values only
        unique_y.add(line.box.y)

    unique_x = pd.Series(sorted(unique_x))
    unique_y = pd.Series(sorted(unique_y))

    # Collapse unique values that are close together
    # - accounts for small pixel deviations
    for i in range(1, len(unique_x)):
        prev, curr = unique_x[i-1], unique_x[i]
        if util.close_to(prev, curr, 5):
             unique_x[i] = prev 

    unique_x = unique_x.unique()
    unique_y = unique_y.unique()

    for i in range(1, len(unique_y)):
        prev, curr = unique_y[i-1], unique_y[i]
        if util.close_to(prev, curr, 5):
            unique_y[i] = prev

    sk.unique_x = list(unique_x)
    sk.unique_y = list(unique_y)

    print(code, unique_x, sep=': ')
    # print(len(sk.category_marks))
    # print(len(unique_x))
    # print(len(unique_y), '\n')


### Build DataFrame to hold Category Values
for code in ('e', 'm', 'r', 's'):
    sk = score_keys[code]
    column_names = sk.column_names[1:]  # Omit the 'Key' (Answers) column

    num_rows = sk.num_questions
    num_cols = len(column_names)

    array = np.zeros((num_rows, num_cols), dtype='bool')
    df = pd.DataFrame(data=array, index=range(1, num_rows+1), columns=column_names)
    sk.category_dataframe = df

    # with pd.option_context('display.max_rows', None): 
    #     label = {'e':'English', 'm':'Math', 'r':'Reading', 's':'Science'}
    #     print(label[code])
    #     print(df, '\n\n')



### Populate dataframe with category data based on positions of marker lines
for code in ('e', 'm', 'r', 's'):
    sk = score_keys[code]
    df = sk.category_dataframe

    # Create dict of x-values and column names for indexing into the Key df
    column_names = sk.column_names[1:]  # Omit the 'Key' (Answers) column
    col_index =  dict(zip(sk.unique_x, column_names))
    print(col_index)

    for row, mark in sk.category_marks.items():
        x, y = mark.box.x, mark.box.y 

        x = min(sk.unique_x, key=lambda el:abs(el-x)) # Align x to closest unique value
        y = min(sk.unique_y, key=lambda el:abs(el-y)) # Align x to closest unique value

        col = col_index[x]
        # row = 1 + sk.unique_y.index(y) 

        # print(i, x, y, row, col)
        df.loc[row, col] = True
    
    
    with pd.option_context('display.max_rows', None): 
        label = {'e':'English', 'm':'Math', 'r':'Reading', 's':'Science'}
        print(label[code])
        print(df, '\n\n') 