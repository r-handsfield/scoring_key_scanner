# scoreKey.py
# A class representing the printed Scoring Keys

from dataclasses import dataclass


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

    x: int
    y: int
    w: int
    h: int
    area: int
    aspect: float


    # def __init__(self, x=None, y=None, w=None, h=None, area=None, aspect=None):
    # def __init__(self, x=None, y=None, w=None, h=None, area=None, aspect=None):
        # self.x = x
        # self.y = y
        # self.w = w
        # self.h = h
        # self.area = area
        # self.aspect = aspect




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
    """


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

   
    pass