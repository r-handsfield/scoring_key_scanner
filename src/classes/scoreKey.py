# scoreKey.py
# A class representing the printed Scoring Keys

import cv2
from dataclasses import dataclass

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

    columns : list[Column]
        All the columns of the Scoring Key, ordered from left to right. A 
        "column" is the box containing the data; it excludes the heading box.

    rows : list[Row]
        All the rows of the Scoring Key, ordered from top to bottom.

    image : CV_Image
        The image of one of the Scoring Key boxes.
    """

    def __init__(self, x, y, w, h, area=None, aspect=None) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.image = None
        
        if area is None:
            self.area = w*h
        else:
            self.area = area

        if aspect is None:
            self.aspect = w/h
        else:
            self.aspect = aspect
        
        self.rows : list = []
        self.columns : list = []

    pass


    def load_image(self, image: CV_Image) -> None:
        """
        Subsets a Scoring Key box from an 850 x 1100 px page image and stores
        it as a CV_Image (np.ndarray) in the 'image' attribute."

        Parameters
        ----------
        image : CV_Image
            An 850 x 1100 px full page image containing the Scoring Key box.

        Returns
        -------
        CV_Image
            The image of the Scoring Key box
        """
        x, y, w, h = self.x, self.y, self.w, self.h
        score_key_box = image[y:y+h, x:x+w]
        self.image = score_key_box

        return score_key_box



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
        self.columns = []

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