import sys, cv2
import unittest
import numpy as np
from PIL import Image

sys.path.append('../classes')
sys.path.append('./test_files')
from scoreKey import Box, Marker, ScoreKey, Column, Row


class TestCaseBox(unittest.TestCase):

    def setUp(self):
        self.box = Box(1, 2, 3, 4)
        
    def test_instantiation(self):
        b = Box(1, 2, 3, 4)
        self.assertIsInstance(b, Box)


    def test_members(self):
        b = self.box
        self.assertIsInstance(b.x, int)
        self.assertIsInstance(b.y, int)
        self.assertIsInstance(b.w, int)
        self.assertIsInstance(b.h, int)
        self.assertIsInstance(b.area, int)
        self.assertIsInstance(b.aspect, float)
        
        self.assertEqual(b.x, 1)
        self.assertEqual(b.y, 2)
        self.assertEqual(b.w, 3)
        self.assertEqual(b.h, 4)
        self.assertEqual(b.area, 12)
        self.assertEqual(b.aspect, 0.75)

### END Box



class TestCaseMarker(unittest.TestCase):
    def setUp(self):
        image = cv2.imread('test_files/good_line.png')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inv = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)[1]
        line = cv2.findContours(inv, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0][0]
        self.marker = Marker(line)

    def test_instantiation(self):
        image = cv2.imread('test_files/good_line.png')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inv = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)[1]
        contours = cv2.findContours(inv, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
        line = contours[0]
        
        m = Marker(line)
        self.assertIsInstance(m, Marker)

    def test_members(self):
        m = self.marker
        self.assertIsInstance(m.box, Box)
        self.assertIsInstance(m.contour, np.ndarray)
        

### END Marker



class TestCaseScoreKey(unittest.TestCase):

    def setUp(self):
        page_image = Image.open("../images/ske.png")
        page_image = page_image.convert('RGB')
        page_image = page_image.resize((850,1100))
        self.page_image = np.asarray(page_image, dtype='uint8')
        self.scoreKey = ScoreKey('e', self.page_image)


    def test_instantiation(self):
        with self.subTest("Passing Section Code Only"):
            sk = ScoreKey('e')
            self.assertIsInstance(sk, ScoreKey)

            self.assertEqual(sk.columns, {})
            self.assertEqual(sk.rows, [])

            self.assertEqual(sk.section_code, 'e')
            self.assertEqual(sk.num_questions, 75)
            self.assertEqual(sk.column_names, ['Key', 'POW', 'KLA', 'CSE'])
            self.assertEqual(sk.category_marks, {})
            self.assertEqual(sk.images, [None, None])
            self.assertEqual(len(sk.tables), 2)
            self.assertIsNone(sk.category_dataframe)
            
            for box in sk.tables:
                self.assertIsInstance(box, Box)

        with self.subTest("Passing section code and page image"):
            sk = ScoreKey('e', page=self.page_image)
            self.assertIsInstance(sk, ScoreKey)

            self.assertEqual(sk.section_code, 'e')
            self.assertEqual(len(sk.tables), 2)
            self.assertEqual(len(sk.images), 2)
            
            for image in sk.images:
                self.assertIsInstance(image, np.ndarray)
                self.assertEqual(len(image.shape), 3)
                self.assertIsInstance(image[0][0][0], np.uint8)

        with self.assertRaises(TypeError):
            ScoreKey('e', 12345)

        with self.assertRaises(TypeError):
            ScoreKey(55)

        with self.assertRaises(TypeError):
            ScoreKey(55, 12345)

        with self.assertRaises(ValueError):
            ScoreKey('q')



    def method_load_page(self):
        sk = self.scoreKey
        self.assertTrue(sk.load_page(self.page_image))

        self.assertIsInstance(sk.images[0], np.ndarray)
        self.assertIsInstance(sk.images[1], np.ndarray)

        height, width = sk.images[0].shape[0], sk.images[0].shape[1]
        params = sk.tables[0]
        w, h = params.w, params.h
        self.assertEqual(height, h)
        self.assertEqual(width, w)

        with self.assertRaises(TypeError):
            sk.load_page(123)

        pass


    def method_filter_markers(self):
        sk = self.scoreKey
        image = cv2.imread('test_files/good_line.png')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inv = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)[1]
        contours = cv2.findContours(inv, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
        line = contours[0]

        if False:
            cv2.drawContours(image, line, -1, (0,0,255), 2)
            cv2.imshow("Contours", image)
            cv2.waitKey(0)

        self.assertTrue(sk.filter_markers(line))


    def method_extract_markers(self):
        sk = self.scoreKey
        image = cv2.imread('test_files/line_contours.png')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inv = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)[1]
        contours = cv2.findContours(inv, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]

        if False:
            pic = image.copy()
            cv2.drawContours(pic, contours, -1, (0,0,255), 1)
            cv2.imshow("Contours", pic)
            cv2.waitKey(0)

        self.assertEqual(len(contours), 25)

        correct_line = sk.extract_markers(contours)
        self.assertEqual(len(correct_line), 1)
        self.assertIsInstance(correct_line, list)

        if False:
            # The remaining contour should be line #4
            pic = image.copy()
            cv2.drawContours(pic, correct_line, -1, (0,0,255), 1)
            cv2.imshow("Marker Lines", pic)
            cv2.waitKey(0)

        x,y,w,h = cv2.boundingRect(correct_line[0])
        self.assertEqual(x, 70)
        self.assertEqual(y, 90)
        self.assertEqual(w, 24)
        self.assertEqual(h, 2)


### End ScoreKey
  

class TestCaseColumn(unittest.TestCase):

    def setUp(self):
        self.column = Column("Key", 1, 2, 3, 4)

    def test_instantiation(self):
        col = Column("Key", 1, 2, 3, 4)
        self.assertIsInstance(col, Column)

        self.assertEqual(col.x, 1)
        self.assertEqual(col.y, 2)
        self.assertEqual(col.w, 3)
        self.assertEqual(col.h, 4)
        self.assertEqual(col.area, 12)
        self.assertEqual(col.aspect, 0.75)
        self.assertEqual(col.label, "Key")

### End Column



class TestCaseRow(unittest.TestCase):

    def setUp(self):
        self.row = Row(0, 10, 20, 26, 250, 16)

    def test_instantiation(self):
        row = Row(0, 10, 20, 26, 250, 16)
        self.assertIsInstance(row, Row)

        self.assertEqual(row.ordinal, 0)
        self.assertEqual(row.x, 10)
        self.assertEqual(row.y, 20)
        self.assertEqual(row.yM, 26)
        self.assertEqual(row.w, 250)
        self.assertEqual(row.h, 16)

### End Row
  

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestCaseBox('test_instantiation'))
    suite.addTest(TestCaseBox('test_members'))

    suite.addTest(TestCaseMarker('test_instantiation'))
    suite.addTest(TestCaseMarker('test_members'))

    suite.addTest(TestCaseScoreKey('test_instantiation'))
    suite.addTest(TestCaseScoreKey('method_load_page'))
    suite.addTest(TestCaseScoreKey('method_filter_markers'))
    suite.addTest(TestCaseScoreKey('method_extract_markers'))

    suite.addTest(TestCaseColumn('test_instantiation'))

    suite.addTest(TestCaseRow('test_instantiation'))

    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
