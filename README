#OCR Extraction of Categorical Information from ACT Scoring Keys

###Motivation

The ACT exam contains questions from several different categories in each exam section. Machine readable answer keys are trivial to create by hand: one can manually convert the printed key to JSON in about 5 minutes. The question categories however are more numerous and complex. It is not practical to manually create a machine readable object for each set of categories. This project attempts to use computer vision and optical character recognition (OCR) to extract the categorical information from the printed scoring keys and convert it to JSON.

###Experiments
####1 Extracting a Scoring Key from a Page
The scoring keys are printed on the final pages of published ACT exams. Each key is consists of 2 large rectangular boxes and appears to be in the same page location on each different exam. The source pdf used for this experiment was compiled from a digital source and is orthogonally aligned and high quality.

1) Extract all the closed contours from the page
2) Sort by the contours by size and keep the 5 largest candidates
3) Visually inspect the candidates to determine the location and dimensions (in pixels) of the scoreing key boxes.

#####Exp 1 Results
Scoring Keys were found by finding the largest contours in the page. The location and dimensions of those contours were used to extract the Scoring Key from the page by subsetting the page's image (numpy array)

####2 Identifying Rows and Columns within the Scoring Key
Because OCR text extration has proven unreliable, I assume that rows and columns are uniform within each Key and will use their positions and dimensions to locate features within each row and column. Each column is situated in its own rectangular box; it should be easy to locate each box as a contour. Columns have slightly different headings in the different test sections.

1) Extract all closed contours from the Scoring Key image
2) Delete small contours from the list of candidates
3) Sort the remaining candidate contours by size
4) Inspect those to determine locating coordinates

During this experiment, it's become clear that a data structure is needed to represent each 
Scoring Key box. It's time to write a class.

###Errata & Unused
Recent available exams are high quality PDF files, while older exams are scans of printed sheets. 