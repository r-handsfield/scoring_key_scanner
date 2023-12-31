# OMR Extraction of Categorical Information from ACT Scoring Keys

### Motivation

The ACT exam contains questions from several different categories in each exam section. Machine readable answer keys are trivial to create by hand: one can manually convert the printed key to JSON in about 5 minutes. The question categories however are more numerous and complex. It is not practical to manually create a machine readable object for each set of categories. This project attempts to use computer vision and optical character recognition (OCR) to extract the categorical information from the printed scoring keys and convert it to JSON.

### Experiments
#### 1 Extracting a Scoring Key from a Page
The scoring keys are printed on the final pages of published ACT exams. Each key is consists of 2 large rectangular boxes and appears to be in the same page location on each different exam. The source pdf used for this experiment was compiled from a digital source and is orthogonally aligned and high quality.

1) Extract all the closed contours from the page
2) Sort by the contours by size and keep the 5 largest candidates
3) Visually inspect the candidates to determine the location and dimensions (in pixels) of the scoreing key boxes.

##### Exp 1 Results
Scoring Keys were found by finding the largest contours in the page. The location and dimensions of those contours were used to extractb the Scoring Key from the page by subsetting the page's image (numpy array)

#### 2 Identifying Columns within the Scoring Keys
Because OCR text extration has proven unreliable, I assume that columns are uniform within each Key, and I will use their positions and dimensions to locate features within each column. Each column is situated in its own rectangular box; it should be easy to locate each box as a contour. Columns have slightly different headings in the different test sections.

1) Extract all closed contours from the Scoring Key image
2) Delete small contours from the list of candidates
3) Sort the remaining candidate contours by size
4) Inspect those to determine the locating coordinates

##### Exp 2 Results
The method of Experiment 2 extracted Column regions from the English, Reading, and Math Scoring Keys. The Math Scoring Keys contain columns separated by dotted lines rather solid, so those columns' contours cannot be read. A different method is needed.

During this experiment, it's become clear that a data structure is needed to represent each Scoring Key box. It's time to write a class.

The Box class contains position, dimensions, area, and aspect ratio. Various classes representing box-like visual features inherit from it: ScoreKey, Column, Row

#### 3 Identifying Columns within the Math Scoring Keys
Because the Math columns are separated by dotted lines, I can't just read the columns as contours. Instead, created virtual contours by using the known values of x0, y0, w, h. y0 and h may be obtained from the Key column, which is solid-bounded. x0 and w may be obtained from the solid-bounded heading boxes.

1) Extract the few closed contours from the Scoring Key image
2) Delete very small contours from the list of candidates
3) Sort the remaining candidate contours left-to-right
4) Inspect those to determine locating coordinates
5) Obtain x0, y0, w, h the few solid-bounded columns
6) From the inspected data, collect x0, y0, w, h, for the desired column
7) Create a virtual contour by enclosing the collection in a doubly nested numpy array (the Open CV data structure)
8) Inspect the real and virtual contours to determine the locating coordinates

##### Exp 3 Results
Locating coordinates for all columns in all Scoring Keys were determined and recorded in `box_positions.py`. While this method assumes good rectilinear box features of uniform size on each page, the columns contain enough whitespace that it should still work on imperfect scanned images. 

#### 4 Identifying Rows within the Scoring Keys
Each Scoring Key contains rows of several columns:

* A question number (i.e. ordinal)
* The correct answer
* One or more marks designating inclusion within a subject category 

The scoring keys are created using legacy word processors, and the category marks appear to be quadruple underscores, therefore appearing at the bottom of a row rather than the middle. To capture the row ordinal and the category marks, there need to be 2 rows: 1 for the ordinal and another (vertically offset) for the marks. 

Using a Scoring Key image, extract the row ordinals:
1) Draw a rectangle around the first ordinal
2) Guess a vertical stride value
3) Displace the rectangle by the v-stride unit, hoping to enclose the second ordinal
4) Adjust the v-stride value until the rectangle correctly lines up with all the ordinals in turn. 

Extract the category marks:
1) Draw a rectangle the full width of the Scoring Key, at the first ordinal
2) Adjust the starting y-position until the category marks are centered within the rectangle
3) Check that the previous v-stride works with all rows of category marks

##### Exp 4 Results
All Scoring Keys have the same vertical stride: 16.66 px (12 pt + whitespace padding). A row height of 16 px works pretty well, and the category marks are consistently offset by 6 px from the ordinal row position. Each row position can be determined by the triordinates `x0, y0, yM`, to distinguish between the ordinal _y_ and marker _y_ positions.





###Errata & Unused
Recent available exams are high quality PDF files, while older exams are scans of printed sheets. 