import os, sys
import cv2
import imutils
import unittest
import numpy as np
from os.path import abspath, join
from collections import namedtuple
from imutils.contours import sort_contours

sys.path.append('../classes')
from sheetUtilities import SheetUtilities



class TestCaseSheetUtilities(unittest.TestCase):

    def setUp(self):
       self.su = SheetUtilities()


    def tearDown(self):
        self.su = None
    

    def test_instantiation(self):
        self.assertIsInstance(self.su, SheetUtilities)


    def test_members(self):
        pass


    def test_method_listToDict(self):
        myList = ['a', 'b', 'c']
        myDict = self.su.listToDict(myList)
        self.assertEqual( repr(myDict.keys()), 'dict_keys([1, 2, 3])' )
        self.assertEqual( repr(myDict.values()), "dict_values(['a', 'b', 'c'])" )


    def test_method_within(self):
        su = self.su
        self.assertTrue( su.within(1.5, 1.4, 1.6, False) )
        self.assertTrue( su.within(1.4, 1.4, 1.6, True) )
        self.assertTrue( su.within(1.6, 1.4, 1.6, True) )
        self.assertFalse( su.within(1.4, 1.4, 1.6, False) )
        self.assertFalse( su.within(1.6, 1.4, 1.6, False) )
        self.assertFalse( su.within(2.6, 1.4, 1.6, False) )
        self.assertFalse( su.within(2.6, 1.4, 1.6) )


    def test_method_close_to(self):
        s = self.su
        self.assertTrue( s.close_to(1.45, 1.5, 0.1) )
        self.assertFalse( s.close_to(1.45, 1.6, 0.1) )


    def test_method_coordinates_to_points(self):
        Point = namedtuple('Point', ['x', 'y'])
        s = self.su
        yCoords = [10, 20]
        xGroups = [[5, 15], [25, 35]]

        truth = {1: [s.Point(x=5,  y=10), s.Point(x=15, y=10)], 
                 2: [s.Point(x=5,  y=20), s.Point(x=15, y=20)], 
                 3: [s.Point(x=25, y=10), s.Point(x=35, y=10)]}

        points = s.coordinates_to_points(xGroups, yCoords, num_questions=3)

        self.assertIsInstance(points, dict)
        self.assertEqual(len(points), 3)
        self.assertIsInstance(points[1], list)
        self.assertTrue("Point" in repr(type(points[1][0])))
        self.assertEqual(points, truth)

        # same coordinates, different num of questions
        truth = {1: [s.Point(x=5,  y=10), s.Point(x=15, y=10)], 
                 2: [s.Point(x=5,  y=20), s.Point(x=15, y=20)], 
                 3: [s.Point(x=25, y=10), s.Point(x=35, y=10)], 
                 4: [s.Point(x=25, y=20), s.Point(x=35, y=20)]}

        points = s.coordinates_to_points(xGroups, yCoords, num_questions=4)
        self.assertEqual(len(points), 4)
        self.assertEqual(points, truth)


    def test_method_extract_unique_1D(self):
        vector = [11, 11, 12, 13, 25, 26, 26, 31, 32, 33]
        truth = [13, 26, 33]

        unique = self.su.extract_unique_1D(vector, 4)

        self.assertEqual(unique, truth)





def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestCaseSheetUtilities('test_instantiation'))
    suite.addTest(TestCaseSheetUtilities('test_members'))
    suite.addTest(TestCaseSheetUtilities('test_method_listToDict'))
    suite.addTest(TestCaseSheetUtilities('test_method_within'))
    suite.addTest(TestCaseSheetUtilities('test_method_close_to'))
    suite.addTest(TestCaseSheetUtilities('test_method_coordinates_to_points'))
    suite.addTest(TestCaseSheetUtilities('test_method_extract_unique_1D'))


    return suite



if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())

