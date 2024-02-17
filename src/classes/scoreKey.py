# scoreKey.py
# A class representing the printed Scoring Keys

import cv2
import numpy as np
from dataclasses import dataclass
from collections import namedtuple


CV_Image = 'np.ndarray[int]'


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



@dataclass
class ScoreKey(Box):
    """
    Represents all the image and data attributes for the scoring key
    boxes of a single ACT section.

    Attributes
    ----------
    expected_box_parameters : dict
        Key : str
            'e1', 'e2', 'm1', 'm2', 'r1', 'r2', 's1', 's2'
        Val : Box
            [x-coord, y-coord, width, height, area, aspect_ratio]
    
    section_code : str
        One of 'e', 'm', 'r', 's'. 

    tables : list[Box]
        The expected table sizes for the section, used for subsetting the
        table images from the larger page.

    images : list[CV_Image]
        The images (np.array) of the individual scoring key boxes for the 
        section. These images are processed to extract the category marks.

    column_names : list[str]
        String names of all the columns, used when creating the DataFrame.

    columns : list[Column]
        All the columns of the Scoring Key, ordered from left to right. A 
        "column" is the box containing the data; it excludes the heading box.

    rows : list[Row]
        All the rows of the Scoring Key, ordered from top to bottom.

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
        expected_box_parameters = {
            'e1' : Box( 74, 223, 164, 708),
            'e2' : Box(277, 223, 163, 691),
            'm1' : Box( 74,  94, 300, 586),
            'm2' : Box(476,  94, 300, 586),
            'r1' : Box( 74,  94, 164, 407),
            'r2' : Box(277,  94, 163, 407),
            's1' : Box( 74, 594, 164, 407),
            's2' : Box(277, 594, 163, 407),
        }
        
        if not isinstance(section_code, str):
            raise TypeError(f"The section code must be a string, not {type(section_code)}")

        self.section_code = section_code.lower()

        self.rows : list = []
        self.columns : dict = {}
        self.column_names = []
        self.tables = [None, None]
        self.images = [None, None]

        self.tables[0] = expected_box_parameters[f'{section_code}1']
        self.tables[1] = expected_box_parameters[f'{section_code}2']

        if page is None:
            pass
        elif isinstance(page, np.ndarray):
            self.load_page(page)
            # w, h = page.shape[1], page.shape[0]

            # if w != 850 or h != 1100:
            #     raise TypeError(f"The page must be 850 x 1100 pixels, not {w} x {h}.")
            # if len(page.shape) < 3:
            #     page = cv2.cvtColor(page, cv2.COLOR_GRAY2BGR)

            # x, y = self.tables[0].x, self.tables[0].y
            # w, h = self.tables[0].w, self.tables[0].h
            # box = page[y:y+h, x:x+w]
            # self.images[0] = box 

            # x, y = self.tables[1].x, self.tables[1].y
            # w, h = self.tables[1].w, self.tables[1].h
            # box = page[y:y+h, x:x+w]
            # self.images[1] = box 
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