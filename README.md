# OMR Extraction of Categorical Information from ACT Scoring Keys

## Motivation
The ACT exam contains questions from several different categories in each exam section. Machine readable answer keys are trivial to create by hand: one can manually convert the printed key to JSON in about 5 minutes. The question categories however are more numerous and complex. 

It is not practical to manually create a machine readable object for each set of categories. This project attempts to use computer vision and optical mark recognition (OMR) to extract the categorical information from the printed scoring keys and convert it to JSON.

## Results
ACT category information can be extracted from the printed scoring keys and written to a JSON file, and a python pipeline for doing so was written. The pipeline can be broadly broken into three parts: Image Processing, Mark Extraction, and Category Mapping. 


## Discussion
### Image Processing
The Image Processing is fairly straightforward and typical of an OMR operation. An image is loaded, orthogonalized, and binarized. An interesting addition is a morphological closing with a horizontal line kernel. The closing emphasizes the desired horizontal line markers and deemphasizes everything else to improve contour detection.

### Mark Extraction
The category markers in the scoring key tables appear to be quadruple ASCII underscores forming horizontal lines roughly 30 pixels long and 1 pixel high. All contours are extracted from the image, and the extracted contours are filtered for the expected line geometry, reliably yielding an accurate list of marker contours. 

With the list of marker contours, an intricate process of aligning each mark to a specific row/column location is performed. The process of obtaining unique the x and y coordinates of a mark requires care. The source images can experience pixel drift at any stage of processing: marks in the same row or column may have slightly different (x,y) coordinates. To acount for potential drift, nearby values are collapsed to generate a single x-value for each table column and a single y-value for each table row. A marker's coordinates are finally overwritten by the nearest collapsed xy values, leaving markers that are integer-aligned to a table row (question number) and table column (category). For later use, indexing dictionaries are created by merging the unique x values with the category labels and unique y values with the question numbers. 

The above alignment procedure obviates the need to detect table column positions and bypasses much of the work required of Experiments 2, 3, and 4.

### Category Mapping
In the final phase of the pipeline, Category Mapping, the indexing dictionaries are used to create mappings between question numbers (keys) and category strings (values). The keys are formatted to be compatible with template variables from the `Jinja 2` templating engine. The resulting maps are then used to inject the category strings into an appropriately formatted JSON string and written to a file. 


## Experiments
### 1 Extracting a Scoring Key from a Page
The scoring keys are printed on the final pages of published ACT exams. Each key consists of 2 large rectangular boxes and appears to be in the same page location on each different exam. The source pdf used for this experiment was compiled from a digital source and is orthogonally aligned and high quality. As seen in Figure 1, the scoring key to a single ACT section is displayed as a pair of boxes in the upper left corner of the page.

#### 1 Method
1) Extract all the closed contours from the page
2) Sort the contours by size and keep the candidates with the largest areas
3) Visually inspect the candidates to determine the location and dimensions (in pixels) of the scoreing key boxes.

#### 1 Results
Scoring Keys were found by finding the largest contours in the page. The location and dimensions of those contours were used to extract the Scoring Key from the page by subsetting the page's image (numpy array). 

For example, the first scoring box on any English key page is positioned at roughly (74, 223) pixels, has W, H dimensions of [164, 708] px, an area of roughly 11,600 px<sup>2</sup>, and an aspect ratio of 0.23. 

With those paramaters, it is trivial to identify that scoring box and subset it from the 2D image tensor. 



Fig. 1: The scoring keys to an ACT English section. The red boxes indicate large contours that passed the initial filter.        |  Fig. 2: The first scoring box subset from the page. 
:-------------------------:|:-------------------------:
<img src="https://github.com/r-handsfield/scoring_key_scanner/blob/master/images_display/11_e_contours.png" alt="Fig. 1" height="550" width="425"/>  | ![Fig. 2](https://github.com/r-handsfield/scoring_key_scanner/blob/master/images_display/12_e_score_box.png)

### 2 Identifying Columns within the Scoring Keys
Because OCR text extration has proven unreliable, I instead assume that columns are uniform within each Key, use their positions and dimensions to locate features within each column. Each column is situated in its own rectangular box; it should be easy to locate each box as a contour. Columns have slightly different headings in the different test sections.

#### 2 Method
1) Extract all closed contours from the Scoring Key image
2) Delete small contours from the list of candidates
3) Sort the remaining candidate contours by size
4) Inspect those to determine the locating coordinates

#### 2 Results
By subsetting, Column regions were extracted from the English, Reading, and Math Scoring Keys. The Math Scoring Keys contain columns separated by dotted lines rather solid, so those columns' contours cannot be read. A different method is needed.

During this experiment, it's become clear that a data structure is needed to represent each Scoring Key box. It's time to write a class.

The Box class contains position, dimensions, area, and aspect ratio. Various classes representing box-like visual features inherit from it: ScoreKey, Column, and Row

|                           |                                 
:-------------------------:
| <img src="https://github.com/r-handsfield/scoring_key_scanner/blob/master/images_display/21_column_contours.png" alt="Fig. 3" width="164" />  |
|Fig. 3: Each red rectangle denotes a feature that is recognized by the scanner. The interior rectangles are recognized as columns; their horizontal positions are mapped to their headers: Key, IOD, SIN, EMI. |

### 3 Identifying Columns within the Math Scoring Keys
Because the Math columns are separated by dotted lines, one cannot read them as contours. Instead, I created virtual contours by using the known values of x<sub>0</sub>, y<sub>0</sub>, w, h; y<sub>0</sub> and h may be obtained from the Key column, which is solid-bounded. x0 and w may be obtained from the solid-bounded heading boxes.

#### 3 Method
1) Extract the few closed contours from the Scoring Key image
2) Delete very small contours from the list of candidates
3) Sort the remaining candidate contours left-to-right
4) Inspect those to determine locating coordinates
5) Obtain x<sub>0</sub>, y<sub>0</sub>, w, h the few solid-bounded columns
6) From the inspected data, collect x<sub>0</sub>, y<sub>0</sub>, w, h, for the desired column
7) Create a virtual contour by enclosing the collection in a doubly nested numpy array (the Open CV data structure)
8) Inspect the real and virtual contours to determine the locating coordinates

#### 3 Results
Coordinates for all columns in all Scoring Keys were determined and recorded in `box_positions.py`. While this method assumes good rectilinear box features of uniform size on each page, the columns contain enough whitespace that it should still work on imperfect, scanned images. 

Fig. 4: All contours detected within a Math scoring box; the columns in the PHM group are bounded by dotted lines.  |  Fig. 5: Due to the dashed lines, the PHM columns cannot be detected by filtering bounding contours. | Fig. 6: Creating virtual contours from known table features allows all the columns to be detected.
:-------------------------:|:-------------------------:|:-------------------------:
<img src="https://github.com/r-handsfield/scoring_key_scanner/blob/master/images_display/31_all_contours.png" alt="Fig. 4" />  | ![Fig. 5](https://github.com/r-handsfield/scoring_key_scanner/blob/master/images_display/32_actual_contours.png) |  ![Fig. 6](https://github.com/r-handsfield/scoring_key_scanner/blob/master/images_display/33_virtual_contours.png) |  

### 4 Identifying Rows within the Scoring Keys
Each Scoring Key contains rows of several columns:

* A question number (i.e. ordinal)
* The correct answer
* One or more marks designating inclusion within a subject category 

The scoring keys appear to be created using legacy word processors, and the category marks appear to be quadruple underscores, therefore appearing at the bottom of a row rather than the middle. To capture the row ordinal and the category marks, there need to be 2 rows: 1 for the ordinal and another (vertically offset) for the marks. 

#### 4 Method
Using a Scoring Key image, extract the row ordinals:
1) Draw a rectangle around the first ordinal
2) Guess a vertical stride value
3) Displace the rectangle by the v-stride unit, hoping to enclose the second ordinal
4) Adjust the v-stride value until the rectangle consecutively lines up with each ordinal in the table

Extract the category marks:
1) Draw a rectangle the full width of the Scoring Key, at the first ordinal
2) Adjust its starting y-position until it encloses the  category marks 
3) Check that the previous v-stride works with all rows of category marks

#### 4 Results
All Scoring Keys have the same vertical stride: 16.66 px (12 pt + whitespace padding). A row/rectangle height of 16 px works pretty well, and the category marks are consistently offset by 6 px from the ordinal row position. Each row position can be determined by the triordinates `x<sub>0</sub>, y<sub>0</sub>, y<sub>M</sub>`, to distinguish between the ordinal _y_ and marker _y_ positions.

Identifying horizontal marker lines by a Hough Line Transform appears to fail regardless of the parameters used. Upon inspection, many of the line contours have zero height and small gaps among them. Filtering all the line contours may be a better way of extracting the marker lines.

### 5 Extracting All ScoreKey Pages from a Single PDF
Previous experiments have shown that the ScoreKey images (2 per page) can be extracted from a 1-page PDF, which contains the ScoreKeys for a single ACT section. It would be very convenient to use a single PDF containing the ScoreKeys for all the sections, rather than a collection of 4 single-page PDFs.

#### 5 Method
1) Load a multi-page PDF document
2) Split the pages
3) Convert each page to a CV_Image (numpy array)
4) Orthogonalize each CV_Image

#### 5 Results
This turned out to be really easy. The `pdf2image` library contains built-in functions that load a pdf and burst the pages as `PIL` images into an iterable. Resizing the pages is also done in-library and orthogonalizing is done with an OpenCV pipeline after converting the `PIL` images to numpy arrays.

### 6 Finding Marker Lines by Contour Filtering
The Hough Line Transform does not reliably return all the marker lines. Instead, try finding all the image contours and filtering them by expected line geometry.

#### 6 Method
1) Find all the image contours
2) Delete contours that don't match the expected line geometry
3) Examine the remaining candidates

#### 6 Results
Simply grabbing the image contours often returns a list that includes the marker lines, but not always. It's more reliable to perform a Morphological Closing with a horizontal line kernel. The closing operation convolves the kernel with the image, emphasizing contours that are already similar shapes to the kernel. Using a 5 by 1 px horiontal line kernel yeilds the following convolved image: the marker lines are the dominant contours which can be found reliably and further filtered for accuracy.

### 7 Converting a One-Hot Dataframe to Category Strings
The ACT Scoring Key tables label columns with an abbreviated category name. Those labels are easily transcribed as lists of strings. The marker x-positions must be mapped to a category label. This might be done using a dataframe.

#### 7 Method
From a list of marker bounding boxes
1) Initialize a boolean dataframe with category labels as columns and question numbers as rows.
2) Create dictionaries mapping x and y values to categories and question numbers
3) Populate the dataframe with boolean Trues
4) Compare the dataframe to the original table image -- examine for accuracy
5) Convert the dataframe to a dict with question numbers as keys and categories as values 

#### 7 Results
The dataframe is indispensable for comparing category assignments to the original table. However, performing the various conversion and processing steps through the dataframe seems unnecessary. Working with dictionary maps might be better. 

###Errata & Unused

Recent available exams are high quality PDF files, while older exams are scans of printed sheets. 
