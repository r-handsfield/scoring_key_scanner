import os, sys
import numpy as np
from collections import namedtuple
from typing import Union, List, Tuple, Dict, NoReturn, Any

sys.path.append('./classes')



class SheetUtilities():
    """
    Non-Image methods for working with ACT answer sheets. Contains methods
    for comparing numbers, converting lists to dicts, etc.
    """

    Point = namedtuple('Point', ['x', 'y'])



    def __init__(self) -> NoReturn:
        pass


    def listToDict(self, aList: List) -> Dict[int, Any]:
        """
        Stores list values in a dict with: key = (index+1)

        Parameters
        ----------
        aList : list
            A list of anything

        Returns
        -------
        dict
            A dict compatible with the 'ACT Scorer module'. 
            Keys are 1-indexed to match question numbers.
        """
        d = {}

        for i,v in enumerate(aList):
            k = i+1
            d[k] = v

        return d



    def within(self, 
                element: Any, 
                minimum: Any, 
                maximum: Any, 
                inclusive: bool=False
    ) -> bool:
        """
        Checks whether a target element is within the given range.
        Used primarily for filtering aspect ratios. Non-numeric types
        are implicitly cast to numerics in the LLVM.

        Parameters
        ----------
        element : any
            The element (primitive type) to check
        minimum : any
            The lower boundary
        maximum : any
            The upper boundary
        inclusive : bool 
            Whether the target can be equal to the min and max

        Returns
        -------
        bool
            True if the element is in between the maximum and minimum
            False otherwise

        """
        if inclusive == False:
            if minimum < element and element < maximum:
                return True
        elif inclusive == True:
            if minimum <= element and element <= maximum:
                return True
        
        return False



    def close_to(self, 
                    element: Union[int, float], 
                    target: Union[int, float], 
                    delta: Union[int, float], 
                    inclusive: bool=False
    ) -> bool:
        """
        Checks whether an element is within one delta of the target.
        Primarily used for filtering aspect ratios.

        Parameters
        ----------
        element : int, float 
            The number that will be checked against the target
        target : int, float 
            The target value
        delta : int, float
            The distance between the element and target (full domain = 2*delta)
        inclusive : bool
            Whether to include the domain boundaries (target +/- delta)

        Returns
        -------
        bool 
            True if the element is within 1 delta of the target
            False otherwise

        Examples
        --------
        >>> self.close_to( 5, target=7, delta=2, inclusive=False )
            False

        >>> self.close_to( 5, target=7, delta=2, inclusive=True )
            True
        """
        minimum = target - delta
        maximum = target + delta

        return self.within(element, minimum, maximum, inclusive)


    def coordinates_to_points(self, 
                                xGroups: List[List[int]], 
                                yCoords: List[int], 
                                num_questions: int
    ) -> Dict[int, List[Point]]:
        """
        Generates a map of bubble positions for an exam indices. A bubble 
        position is defined as the (x,y) location of the center of the 
        bubble contour's bounding box. Each location is stored in the named
        tuple: Point(x,y). Each dict key contains a list of Points, length 
        determined by the group length in 'xGroups'

        The parameter xGroups contains lists of x-coordinates; yCoords contains
        y-coordinates. The returned map is created by combining all the 
        x and y coordinates to generate a grid of unique Point objects 
        representing all the answer bubbles for an ACT indices of length
        'num_questions'.

        Parameters
        ----------
        xGroups : list[list, list, ...], int 
            A nested list of rows of x-coordinates representing all column groups 
            in a indices.

        yCoords : list, int
            A flat list of y-coordinates representing all rows in a indices

        num_questions : int
            The total number of questions in a test indices

        Returns
        ------- 
        dict
            Key = question number
            Value = list of Point tuples; list has same length as inner lists
            of 'xGroups'
            { 1:[Point(x,y), Point(x,y) ...], 2:[Point(x,y), ... ], ... }

        See Also
        --------
        kmeans_centers
        xCoordinates_to_groups
        """
        sMap = {}

        q = 1
        for group in xGroups:
            for y in yCoords:
                if q > num_questions: break
                row = []
                for x in group:
                    p = self.Point(x,y)
                    row.append(p)
                sMap[q] = row
                q += 1

        return sMap

    
    def extract_unique_1D(self, 
                            values: List[int], 
                            delta: int
    ) -> List[int]:
        """
        Extracts unique features from a 1D vector and implicitly sorts them 
        low to high.

        Graphical features in the same row or col can have slightly different
        pixel coordinates. This method grabs the unique coordinates and 
        collapses values that are within 1 delta of each other by extracting 
        the final value within +/- 1 delta.

        Parameters
        ----------
        values : list[int]
            Pixel values representing the positions of graphical features

        delta : int
            A number of pixels 

        Returns
        -------
        list[int] 
            The values representing unique features -- usually uniques rows or
            columns within a section.

        Examples
        --------
        >>> vector = [11, 11, 12, 13, 25, 26, 26, 31, 32, 33]
        >>> extract_unique_1D(vector, 4)

        [13, 26, 33]
        """
        values[:] = np.unique(values)
        for i in reversed(range(1, len(values))):
            v1 = values[i]
            v2 = values[i-1]
            # print(i, ':', v1, v2)

            if self.close_to(v2, v1, delta, True):
                del(values[i-1])

        return values


