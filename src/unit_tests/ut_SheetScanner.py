import os, sys
import cv2
import imutils
import unittest
import numpy as np
from os.path import abspath, join
from collections import namedtuple
from imutils.contours import sort_contours

sys.path.append("../classes")
from sheetScanner import Sheet


PATH = './'
PATH_ANSWER_SHEET = abspath("./test_files/ACT Answer Sheet v04.png")
PATH_SQUARE_PNG = abspath("./test_files/square.png")
PATH_SOLID_SQUARE = abspath("./test_files/solid_square.png")
PATH_MULTISIZE_SQUARES = abspath("./test_files/multisize_squares.png")
PATH_MULTISIZE_CIRCLES = abspath("./test_files/multisize_circles.png")
PATH_ROW_SINGLE = abspath("./test_files/row_single.png")
PATH_ROW_PARTIAL = abspath("./test_files/row_partial_filled.png")
PATH_ROW_MULTIPLE = abspath("./test_files/row_multiple.png")
PATH_ROW_DARKEST = abspath("./test_files/row_darkest.png")
PATH_ROW_EMPTY = abspath("./test_files/row_empty.png")
PATH_GRID_CIRCLES = abspath("./test_files/grid_circles.png")

FLAG_TEST_DISPLAY_METHODS = False

Point = namedtuple('Point', ['x', 'y'])


class TestCaseSheetScanner(unittest.TestCase):

    def setUp(self):
        self.sheet = Sheet(PATH_ANSWER_SHEET)


    def tearDown(self):
        self.sheet = None
        pass


    def test_instantiation(self):
        self.assertIsInstance(self.sheet, Sheet)

        img = cv2.imread(PATH_SQUARE_PNG)
        sheet = Sheet(image=img, binary_threshold=225)
        self.assertIsInstance(sheet, Sheet)


    def test_members(self):
        self.assertIsInstance(self.sheet.binary_threshold, int)
        self.assertIn(self.sheet.binary_threshold, range(1, 254))

        self.assertIsInstance(self.sheet.image, np.ndarray)
        self.assertEqual(len(self.sheet.image.shape), 3)

        self.assertIsInstance(self.sheet.gray, np.ndarray)
        self.assertEqual(len(self.sheet.gray.shape), 2)
        self.assertEqual(len(np.unique(self.sheet.gray)), 256)

        self.assertIsInstance(self.sheet.edges, np.ndarray)
        self.assertEqual(len(self.sheet.edges.shape), 2)
        self.assertEqual(len(np.unique(self.sheet.edges)), 2)

        self.assertIsInstance(self.sheet.binary, np.ndarray)
        self.assertEqual(len(self.sheet.binary.shape), 2)
        self.assertEqual(len(np.unique(self.sheet.binary)), 2)
        self.assertEqual(cv2.countNonZero(self.sheet.binary), 758206)

        self.assertIsInstance(self.sheet.inverted, np.ndarray)
        self.assertEqual(len(self.sheet.inverted.shape), 2)
        self.assertEqual(len(np.unique(self.sheet.inverted)), 2)
        self.assertEqual(cv2.countNonZero(self.sheet.inverted), 103490)

        self.assertIsInstance(self.sheet.all_contours[0], np.ndarray)

        p = self.sheet.Point(1,2)
        self.assertEqual(p.x, 1)
        self.assertEqual(p.y, 2)

        with self.subTest("Instantiation from Image"):
            img = cv2.imread(PATH_SQUARE_PNG)
            sheet = Sheet(img)
            self.assertIsInstance(sheet.image, np.ndarray)

        with self.subTest("Instantiation from Path"):
            sheet = Sheet(PATH_SQUARE_PNG)
            self.assertIsInstance(sheet.image, np.ndarray)

        with self.subTest("Instantiaion with Bad Image Argument"):
            with self.assertRaises(TypeError):
                sheet = Sheet(6)
                sheet = Sheet(PATH_SQUARE_PNG, 106.5)


    def test_method_preprocess(self):
        with self.subTest("Constructor takes a string"):
            gray, edges, binary, inverted = self.sheet.preprocess(self.sheet.image)

            # debugging block
            if False:
                cv2.imshow("Gray", gray)
                cv2.imshow("Edges", edges)
                cv2.imshow("Binary", binary)
                cv2.waitKey(0);

            self.assertIsInstance(gray, np.ndarray)
            self.assertIsInstance(edges, np.ndarray)
            self.assertIsInstance(binary, np.ndarray)
            self.assertIsInstance(inverted, np.ndarray)

            self.assertEqual(len(gray.shape), 2)
            self.assertEqual(len(edges.shape), 2)
            self.assertEqual(len(binary.shape), 2)
            self.assertEqual(len(inverted.shape), 2)

            self.assertEqual(len(np.unique(gray)), 256)

            self.assertEqual(len(np.unique(edges)), 2)
            self.assertEqual(np.unique(edges)[0], 0)
            self.assertEqual(np.unique(edges)[1], 255)

            self.assertEqual(len(np.unique(binary)), 2)
            self.assertEqual(np.unique(binary)[0], 0)
            self.assertEqual(np.unique(binary)[1], 255)
            self.assertEqual(cv2.countNonZero(self.sheet.binary), 758206)

            self.assertEqual(len(np.unique(inverted)), 2)
            self.assertEqual(np.unique(inverted)[0], 0)
            self.assertEqual(np.unique(inverted)[1], 255)
            self.assertEqual(cv2.countNonZero(self.sheet.inverted), 103490)

        with self.subTest("Constructor takes an RGB image (H,W,C)"):
            img = cv2.imread(PATH_ANSWER_SHEET)
            sheet = Sheet(img)
            gray, edges, binary, inverted = self.sheet.preprocess(self.sheet.image)

            self.assertIsInstance(gray, np.ndarray)
            self.assertIsInstance(edges, np.ndarray)
            self.assertIsInstance(binary, np.ndarray)
            self.assertIsInstance(inverted, np.ndarray)

            self.assertEqual(len(gray.shape), 2)
            self.assertEqual(len(edges.shape), 2)
            self.assertEqual(len(binary.shape), 2)
            self.assertEqual(len(inverted.shape), 2)

            self.assertEqual(len(np.unique(gray)), 256)

            self.assertEqual(len(np.unique(edges)), 2)
            self.assertEqual(np.unique(edges)[0], 0)
            self.assertEqual(np.unique(edges)[1], 255)

            self.assertEqual(len(np.unique(binary)), 2)
            self.assertEqual(np.unique(binary)[0], 0)
            self.assertEqual(np.unique(binary)[1], 255)
            self.assertEqual(cv2.countNonZero(self.sheet.binary), 758206)

            self.assertEqual(len(np.unique(inverted)), 2)
            self.assertEqual(np.unique(inverted)[0], 0)
            self.assertEqual(np.unique(inverted)[1], 255)
            self.assertEqual(cv2.countNonZero(self.sheet.inverted), 103490)

        with self.subTest("Constructor takes a grayscale image (H,W)"):
            img = cv2.imread(PATH_ANSWER_SHEET, 0)
            sheet = Sheet(img)
            gray, edges, binary, inverted = sheet.preprocess(sheet.image)

            self.assertIsInstance(gray, np.ndarray)
            self.assertIsInstance(edges, np.ndarray)
            self.assertIsInstance(binary, np.ndarray)
            self.assertIsInstance(inverted, np.ndarray)

            self.assertEqual(len(gray.shape), 2)
            self.assertEqual(len(edges.shape), 2)
            self.assertEqual(len(binary.shape), 2)
            self.assertEqual(len(inverted.shape), 2)

            self.assertEqual(len(np.unique(gray)), 256)

            self.assertEqual(len(np.unique(edges)), 2)
            self.assertEqual(np.unique(edges)[0], 0)
            self.assertEqual(np.unique(edges)[1], 255)

            self.assertEqual(len(np.unique(binary)), 2)
            self.assertEqual(np.unique(binary)[0], 0)
            self.assertEqual(np.unique(binary)[1], 255)
            self.assertEqual(cv2.countNonZero(self.sheet.binary), 758206)

            self.assertEqual(len(np.unique(inverted)), 2)
            self.assertEqual(np.unique(inverted)[0], 0)
            self.assertEqual(np.unique(inverted)[1], 255)
            self.assertEqual(cv2.countNonZero(self.sheet.inverted), 103490)

        with self.subTest("Passing Parameters"):
            gray, edges, binary, inverted = self.sheet.preprocess(self.sheet.image, 225)

            self.assertIsInstance(gray, np.ndarray)
            self.assertIsInstance(edges, np.ndarray)
            self.assertIsInstance(binary, np.ndarray)
            self.assertIsInstance(inverted, np.ndarray)

            self.assertEqual(len(gray.shape), 2)
            self.assertEqual(len(edges.shape), 2)
            self.assertEqual(len(binary.shape), 2)
            self.assertEqual(len(inverted.shape), 2)

            self.assertEqual(len(np.unique(gray)), 256)

            self.assertEqual(len(np.unique(edges)), 2)
            self.assertEqual(np.unique(edges)[0], 0)
            self.assertEqual(np.unique(edges)[1], 255)

            self.assertEqual(len(np.unique(binary)), 2)
            self.assertEqual(np.unique(binary)[0], 0)
            self.assertEqual(np.unique(binary)[1], 255)
            self.assertEqual(cv2.countNonZero(self.sheet.binary), 758206)

            self.assertEqual(len(np.unique(inverted)), 2)
            self.assertEqual(np.unique(inverted)[0], 0)
            self.assertEqual(np.unique(inverted)[1], 255)
            self.assertEqual(cv2.countNonZero(self.sheet.inverted), 103490)

        with self.subTest("Passing the Binarization Threshold"):
            img = cv2.imread(PATH_SOLID_SQUARE, 0)
            square = Sheet(img)

            # The square is gray 127, 61x61 pixels
            # Background is white 255, 101x101 pixels
            wht = square.preprocess(square.gray, 100)[2]  # Make the gray square white
            blk = square.preprocess(square.gray, 150)[2]  # Make the gray square black

            self.assertEqual(cv2.countNonZero(wht), 101*101)
            self.assertEqual(cv2.countNonZero(blk), 101**2 - 61**2)

        with self.subTest("Contour Sorting"):
            contours = self.sheet.all_contours

            for i in range(1, len(contours)):
                curr = cv2.contourArea(contours[i])
                prev = cv2.contourArea(contours[i-1])
                self.assertLessEqual(curr, prev)


    def test_method_get_circularity(self):
        sheet = Sheet(PATH_MULTISIZE_CIRCLES)
        contours = sheet.extract_contours()
        contours = sort_contours(contours, "left-to-right")[0]
        contours = sort_contours(contours, "top-to-bottom")[0]
        
        circ = round( sheet.get_circularity(contours[0]), 3 )
        self.assertEqual(circ, 0.874) 

        circ = round( sheet.get_circularity(contours[1]), 3 )
        self.assertEqual(circ, 0.735) 

        circ = round( sheet.get_circularity(contours[2]), 3 )
        self.assertEqual(circ, 0.829) 

        circ = round( sheet.get_circularity(contours[3]), 3 )
        self.assertEqual(circ, 0.897) 

        circ = round( sheet.get_circularity(contours[4]), 3 )
        self.assertEqual(circ, 0.815) 


    def test_method_extract_contours(self):
        sheet = Sheet(PATH_GRID_CIRCLES)
        circles = sheet.extract_contours(sheet.image, 0, 255)
        self.assertEqual(len(circles), 56)

        circles = sheet.extract_contours()
        self.assertEqual(len(circles), 56)


    def test_method_sort_contours_by_size(self):
        sheet = Sheet(PATH_MULTISIZE_SQUARES)

        with self.subTest("Descending Order"):
            contours = sheet.sort_contours_by_size(sheet.all_contours, descending=True)

            self.assertEqual(cv2.contourArea(contours[0]), 1600)
            self.assertEqual(cv2.contourArea(contours[1]), 900)
            self.assertEqual(cv2.contourArea(contours[2]), 400)
            self.assertEqual(cv2.contourArea(contours[3]), 100)

        with self.subTest("Ascending Order"):
            contours = sheet.sort_contours_by_size(sheet.all_contours, descending=False)

            self.assertEqual(cv2.contourArea(contours[0]), 100)
            self.assertEqual(cv2.contourArea(contours[1]), 400)
            self.assertEqual(cv2.contourArea(contours[2]), 900)
            self.assertEqual(cv2.contourArea(contours[3]), 1600)


  
    def test_method_show_contours(self):
        sheet = Sheet(PATH_GRID_CIRCLES)
        circles = sheet.extract_contours(sheet.image)
        self.assertTrue( sheet.show_contours(sheet.image, "Contours - Individual", circles, True) )
        self.assertTrue( sheet.show_contours(sheet.image, "Contours - All", circles, False) )



    def test_method_count_pixels_of_contours(self):
        s1 = Sheet(PATH_ROW_SINGLE)
        s2 = Sheet(PATH_ROW_EMPTY)
        s3 = Sheet(PATH_ROW_MULTIPLE)
        s4 = Sheet(PATH_ROW_PARTIAL)

        # 1 Filled, Contour
        with self.subTest("1 Filled"):
            c1 = sort_contours(s1.all_contours, method='left-to-right')[0]

            counts = s1.count_pixels_of_contours(c1, False)
            self.assertEqual(len(counts['b']), 4)
            self.assertEqual(len(counts['w']), 4)

            truth_b = ( 375,  375, 2088,  375)
            truth_w = (1713, 1713,    0, 1713)

            for i in range(4):
                self.assertEqual(counts['b'][i], truth_b[i], f"Bubble {i+1}")
                self.assertEqual(counts['w'][i], truth_w[i], f"Bubble {i+1}")


        # 0 Filled, Contour
        with self.subTest("0 Filled"):
            c2 = sort_contours(s2.all_contours, method='left-to-right')[0]

            counts = s2.count_pixels_of_contours(c2, False)
            self.assertEqual(len(counts['b']), 4)
            self.assertEqual(len(counts['w']), 4)

            truth_b = ( 382,  382,  382,  382)
            truth_w = (1713, 1713, 1713, 1713)

            for i in range(4):
                self.assertEqual(counts['b'][i], truth_b[i], f"Bubble {i+1}")
                self.assertEqual(counts['w'][i], truth_w[i], f"Bubble {i+1}")


        # 4 Filled, Contour
        with self.subTest("4 Filled"):
            c3 = sort_contours(s3.all_contours, method='left-to-right')[0]

            counts = s3.count_pixels_of_contours(c3, False)
            self.assertEqual(len(counts['b']), 4)
            self.assertEqual(len(counts['w']), 4)

            truth_b = (2082, 2082, 2082, 2082)
            truth_w = (   0,    0,    0,    0)

            for i in range(4):
                self.assertEqual(counts['b'][i], truth_b[i], f"Bubble {i+1}")
                self.assertEqual(counts['w'][i], truth_w[i], f"Bubble {i+1}")


        # 1 Partially Filled, Contour
        with self.subTest("1 Partially Filled"):
            c4 = sort_contours(s4.all_contours, method='left-to-right')[0]

            counts = s4.count_pixels_of_contours(c4, False)
            self.assertEqual(len(counts['b']), 4)
            self.assertEqual(len(counts['w']), 4)

            truth_b = ( 375,  375, 1828,  375)
            truth_w = (1713, 1713,  269, 1713)

            for i in range(4):
                self.assertEqual(counts['b'][i], truth_b[i], f"Bubble {i+1}")
                self.assertEqual(counts['w'][i], truth_w[i], f"Bubble {i+1}")

  

    def test_method_count_pixels(self):
        s1 = Sheet(PATH_ROW_SINGLE)
        s2 = Sheet(PATH_ROW_EMPTY)
        s3 = Sheet(PATH_ROW_MULTIPLE)
        s4 = Sheet(PATH_ROW_PARTIAL)


        with self.assertRaises(ValueError):
            s1.count_pixels([1,2], 'bad mode', None, False)

        # 1 Filled, Contour
        with self.subTest("Mode = Contours, 1 Filled"):
            c1 = sort_contours(s1.all_contours, method='left-to-right')[0]

            counts = s1.count_pixels(c1, 'contours', None, False)
            self.assertEqual(repr(counts.keys()), "dict_keys(['b', 'w'])")
            self.assertEqual(len(counts['b']), 4)
            self.assertEqual(len(counts['w']), 4)

            truth_b = ( 375,  375, 2088,  375)
            truth_w = (1713, 1713,    0, 1713)

            for i in range(4):
                self.assertEqual(counts['b'][i], truth_b[i], f"Bubble {i+1}")
                self.assertEqual(counts['w'][i], truth_w[i], f"Bubble {i+1}")
        # -----


        # 0 Filled, Contour
        with self.subTest("Mode = Contours, 0 Filled"):
            c2 = sort_contours(s2.all_contours, method='left-to-right')[0]

            counts = s2.count_pixels(c2, 'contours', None, False)
            self.assertEqual(len(counts['b']), 4)
            self.assertEqual(len(counts['w']), 4)

            truth_b = ( 382,  382,  382,  382)
            truth_w = (1713, 1713, 1713, 1713)

            for i in range(4):
                self.assertEqual(counts['b'][i], truth_b[i], f"Bubble {i+1}")
                self.assertEqual(counts['w'][i], truth_w[i], f"Bubble {i+1}")
        # -----


        # 4 Filled, Contour
        with self.subTest("Mode = Contours, 4 Filled"):
            c3 = sort_contours(s3.all_contours, method='left-to-right')[0]

            counts = s3.count_pixels(c3, 'contours', None, False)
            self.assertEqual(len(counts['b']), 4)
            self.assertEqual(len(counts['w']), 4)

            truth_b = (2082, 2082, 2082, 2082)
            truth_w = (   0,    0,    0,    0)

            for i in range(4):
                self.assertEqual(counts['b'][i], truth_b[i], f"Bubble {i+1}")
                self.assertEqual(counts['w'][i], truth_w[i], f"Bubble {i+1}")
        # -----


        # 1 Partially Filled, Contour
        with self.subTest("Mode = Contours, 1 Partially Filled"):
            c4 = sort_contours(s4.all_contours, method='left-to-right')[0]

            counts = s4.count_pixels(c4, 'contours', None, False)
            self.assertEqual(len(counts['b']), 4)
            self.assertEqual(len(counts['w']), 4)

            truth_b = ( 375,  375, 1828,  375)
            truth_w = (1713, 1713,  269, 1713)

            for i in range(4):
                self.assertEqual(counts['b'][i], truth_b[i], f"Bubble {i+1}")
                self.assertEqual(counts['w'][i], truth_w[i], f"Bubble {i+1}")
        # -----

        
   
  
    def test_method_find_darkest_from_contours(self):
        s1 = Sheet(PATH_ROW_DARKEST)
        darkest = s1.find_darkest_from_contours(s1.all_contours)
        self.assertEqual(darkest, 3)

        img = cv2.imread(PATH_ROW_DARKEST)
        img = cv2.flip(img, flipCode=1)
        s1 = Sheet(img)
        darkest = s1.find_darkest_from_contours(s1.all_contours)
        self.assertEqual(darkest, 0)


 
 
 
  
  
  
 
  
   

def suite():
    suite = unittest.TestSuite()

    suite.addTest(TestCaseSheetScanner('test_instantiation'))
    suite.addTest(TestCaseSheetScanner('test_members'))
    suite.addTest(TestCaseSheetScanner('test_method_preprocess'))
    suite.addTest(TestCaseSheetScanner('test_method_get_circularity'))
    suite.addTest(TestCaseSheetScanner('test_method_extract_contours'))
    suite.addTest(TestCaseSheetScanner('test_method_sort_contours_by_size'))
    suite.addTest(TestCaseSheetScanner('test_method_count_pixels_of_contours'))
    suite.addTest(TestCaseSheetScanner('test_method_count_pixels'))
    suite.addTest(TestCaseSheetScanner('test_method_find_darkest_from_contours'))



    if FLAG_TEST_DISPLAY_METHODS:
        suite.addTest(TestCaseSheetScanner('test_method_show_contours'))
        pass


    return suite



if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())

