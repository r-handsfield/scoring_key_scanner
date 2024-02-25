# scoreKey.py
# A class representing the printed Scoring Keys

import cv2
import numpy as np
import pandas as pd
from dataclasses import dataclass
from collections import namedtuple
from typing import Union, List, Tuple, Dict, NoReturn, Any


# Define OpenCV Classes
CV_Image = 'np.ndarray[int]'
CV_Contour = 'np.ndarray[np.ndarray[np.ndarray[int]]]'


@dataclass
class Box():
    """
    A class representing a rectangular contour or region of a printed page. 
    A negative number should be used as a Dummy value for any attribute as
    necessary, although this is not enforced and Dummny values should be
    avoided.

    Attributes
    ----------
    x : int
        The horizontal position in pixels of the Box's top left corner

    y : int
        The vertical position in pixels of the Box's top left corner

    w : int
        The width in pixels of the Box

    h : int
        The height in pixels of the Box

    area : int 
        The area in pixels of the Box

    aspect : float
        The aspect ratio (w/h) of the Box
    """

    def __init__(self, x:int, y:int, w:int, h:int) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.area = w * h
        self.aspect = w / h

    def __str__(self):
        s  = f"(x: {self.x}, y: {self.y}, "
        s += f"w: {self.w}, h: {self.h}, "
        s += f"area: {self.area}, aspect: {round(self.aspect, 5)})"
        return(s)


@dataclass
class Marker(Box):
    """
    Represents a visual marker line within a scoring box image.

    Attributes
    ----------
    contour : CV_Contour
        The marker's contour (numpy array[uint8]).

    box : Box
        The contour's bounding box info (x, y, w, h) along with
        its computer area and aspect ratio.

    column : str
        The name of the column in which the marker resides.

    row : int
        The 1-indexed row number at which the marker resides.
    """
    def __init__(self, contour: CV_Contour) -> None:
        """
        Stores contour and bounding box information for 
        """
        x, y, w, h = cv2.boundingRect(contour)
        self.box = Box(x, y, w, h)
        self.contour = contour
        self.column = None
        self.row = None


@dataclass
class ScoreKey(Box):
    """
    Represents all the image and data attributes for the scoring key
    boxes of a single ACT section.

    Attributes
    ----------
    expected_table_parameters : dict
        Key : str
            'e1', 'e2', 'm1', 'm2', 'r1', 'r2', 's1', 's2'
        Val : Box
            [x-coord, y-coord, width, height, area, aspect_ratio]

    score_key_metadata : dict
        Key : str
            'e', 'm', 'r', 's'. 
        Val : dict 
            K : str
                'num_questions'
            V : int

    expected_column_names : dict
        Key : str
            'e', 'm', 'r', 's'. 
        Val : list[str]
            The name of the columns appearing in the source image of each scoring 
            key
    
    section_code : str
        One of 'e', 'm', 'r', 's'. 

    category_dataframe : pandas.DataFrame
        Represents the scoring key boxes using boolean values instead of 
        visual marker lines

    tables : list[Box]
        The expected table sizes for the section, used for subsetting the
        table images from the larger page.

    images : list[CV_Image]
        The images (np.array) of the individual scoring key boxes for the 
        section. These images are processed to extract the category marks.

    num_questions : int
        The number of questions in an exam section.

    category_marks : dict
        Key : int
            A question number
        Val : list[Marker]
            Marker objects containing position and contour info of category
            marker lines.

    column_names : list[str]
        String names of all the columns, used when creating the DataFrame.

    boxes : list[Box]
        The locations and sizes of the Scoring Key boxes.

    images : list[CV_Image]
        The images of the Scoring Key boxes.
    """
    

    def __init__(self, section_code: str, page: CV_Image=None) -> None:
        """
        The constructor

        Parameters
        ----------
        section_code : str
            One of 'e', 'm', 'r', 's'

        page : numpy.ndarray
            An image of the page containing the scoring key boxes

        Returns
        -------
        None
        """
        expected_table_parameters = {
            'e1' : Box( 74, 223, 164, 708),
            'e2' : Box(277, 223, 163, 691),
            'm1' : Box( 74,  94, 300, 586),
            'm2' : Box(476,  94, 300, 586),
            'r1' : Box( 74,  94, 164, 407),
            'r2' : Box(277,  94, 163, 407),
            's1' : Box( 74, 594, 164, 407),
            's2' : Box(277, 594, 163, 407),
        }

        score_key_metadata = {
            'e': {'num_questions': 75},
            'm': {'num_questions': 60},
            'r': {'num_questions': 40},
            's': {'num_questions': 40},
        }

        expected_column_names = {
            'e': ["Key", "POW", "KLA", "CSE"],
            'm': ["Key", "PHM-N", "PHM-A", "PHM-F", "PHM-G", "PHM-S", "IES", "MDL"],
            'r': ["Key", "KID", "CS", "IKI"],
            's': ["Key", "IOD", "SIN", "EMI"]
        }
        
        if not isinstance(section_code, str):
            raise TypeError(f"The section code must be a string, not {type(section_code)}")

        self.section_code = section_code.lower()

        if not section_code in ('e', 'm', 'r', 's'):
            raise ValueError(f"The section code must be one of ('e', 'm', 'r', 's'), not f{section_code}.")

        self.num_questions = score_key_metadata.get(self.section_code)['num_questions']
        self.column_names = expected_column_names[self.section_code]

        self.category_marks = dict.fromkeys(range(1, self.num_questions+1), [])

        self.category_dataframe = None

        self.tables = [None, None]
        self.images = [None, None]

        self.tables[0] = expected_table_parameters[f'{section_code}1']
        self.tables[1] = expected_table_parameters[f'{section_code}2']


        if page is None:
            pass
        elif isinstance(page, np.ndarray):
            self.load_page(page)
        else:
            raise TypeError(f"Page must be a numpy array of integers, not a {type(page)}.")


    def load_page(self, page: CV_Image) -> bool:
        """
        Subsets a pair of Scoring Key boxes from an 850 x 1100 px page image 
        and stores them as CV_Images (np.ndarray) in the 'images' attribute."

        Parameters
        ----------
        page : CV_Image
            An 850 x 1100 px full page image containing the Scoring Key box.

        Returns
        -------
        bool
            True if the method doensn't crash, False otherwise
        """
        if not isinstance(page, np.ndarray):
            raise TypeError(f"The page must be a numpy array of integers, not a {type(page)}.")
        
        w, h = page.shape[1], page.shape[0]
        if w != 850 or h != 1100:
                raise TypeError(f"The page must be 850 x 1100 pixels, not {w} x {h}.")
        if len(page.shape) < 3:
            page = cv2.cvtColor(page, cv2.COLOR_GRAY2BGR)
        
        for i, params in enumerate(self.tables):
            x, y, w, h = params.x, params.y, params.w, params.h
            box = page[y:y+h, x:x+w]
            self.images[i] = box

        return True
    

    def get_contours(self, image: CV_Image, 
                            min: int=250, 
                            max: int=255,
                            kernel: Tuple[int]=(5,1)
    ) -> Tuple[CV_Contour]:
        """
        Extracts from an image all contours after performing the following 
        operations:
        
        (1) Morphological Closing using the (width, height) kernel
        (2) Binary Threshold using the min and max parameters
        (3) Finding all contours

        The kernel is expected to be a horizontal line, and convolving it with
        the image emphasizes the horizontal marker lines within the image.

        Parameters
        ----------
        image : CV_Image
            A numpy ndarray representing an image

        min : int
            The threshold to use for the Binary Threshold operation

        max : int
            The max pixel intensity to use for the Binary Threshold operation

        kernel : Tuple[int, int]
            A solid rectangle of (width, height) that is convolved with the 
            image during the Morphological Closing operation. The convolution
            emphasizes contours of similar shapes, and the kernel is 
            expected to be a horizontal line: w >> h.

        Returns
        -------
        tuple(CV_Contour)
            A collection of OpenCV contours
        """
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        cv_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel)
        closed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, cv_kernel)
        closed_inv = cv2.threshold(closed, min, max, cv2.THRESH_BINARY_INV)[1]
        contours = cv2.findContours(closed_inv, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]

        # cv2.imshow("Inverted", closed_inv)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # pic = closed.copy()
        # pic = cv2.cvtColor(pic, cv2.COLOR_GRAY2BGR)
        # cv2.drawContours(pic, contours, -1, (0,0,255), 1)
        # cv2.imshow("All Contours", pic)
        # cv2.waitKey(0)

        return contours


    def filter_markers(self, contour: CV_Contour) -> bool:
        """
        A filter function that returns True if a contour is the same shape as
        a scoring key marker line. This function is passed to python's 'filter'
        function in self.extract_markers().

        Parameters
        ----------
        contour : CV_Contour
            A contour that may be a scoring key marker line
        
        Returns
        -------
        bool
            True if the contour has the same shape and postion as expected
            of a marker line.
        """
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
        
    
    def extract_markers(self, contours: list) -> list:
        """
        Filters marker lines from a list of contours.

        Parameters
        ----------
        contours : list[CV_Contour]
            The list of candidate contours returned by cv2.findContours( ... )

        Returns
        -------
        list[CV_Contour]
            The list of contours representing score key marker lines
        """
        markers = list(filter(self.filter_markers, list(contours)))
        return markers

    
    def get_unique_(self):
        """
        """
        pass


@dataclass()
class Column(Box):
    """
    
    Attributes
    ----------
    x : int
        The horizontal position in pixels of the Scoring Key's top left corner

    y : int
        The vertical position in pixels of the Scoring Key's top left corner

    w : int
        The width in pixels of the Scoring Key

    h : int
        The height in pixels of the Scoring Key

    area : int 
        The area in pixels of the Scoring Key

    aspect : float
        The aspect ratio (w/h) of the Scoring Key

    label : str
        The column heading. Headings are fixed for each section: English, Math, Reading, Science
    """

    def __init__(self, label, x, y, w, h):
        self.label = label
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.area = w*h
        self.aspect = w/h
        
        self.rows = []

    pass


@dataclass()
class Row():
    """
    
    Attributes
    ----------
    x : int
        The horizontal position in pixels of the Scoring Key's top left corner

    y : int
        The vertical position in pixels of the Scoring Key's top left corner

    yM : int
        The vertical position in pixels of the Scoring Key's top left corner

    w : int
        The width in pixels of the Scoring Key

    h : int
        The height in pixels of the Scoring Key

    ordinal : int
        The zero-indexed row number: 0, 1, 2, etc.
    """

    ordinal : int
    x: int
    y: int
    yM: int
    w: int
    h: int

    pass