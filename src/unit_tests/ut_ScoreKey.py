import sys, cv2
import unittest
import numpy as np
from PIL import Image

sys.path.append('../classes')
from scoreKey import Box, ScoreKey, Column, Row

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

            self.assertEqual(sk.column_names, [])
            self.assertEqual(sk.columns, {})
            self.assertEqual(sk.rows, [])

            self.assertEqual(sk.section_code, 'e')
            self.assertEqual(sk.images, [None, None])
            self.assertEqual(len(sk.tables), 2)
            
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
            ScoreKey(55, 12345)





    def method_load_image(self):
        # sk = self.scoreKey
        # sk.load_image(self.page_image)

        # self.assertIsInstance(sk.image, np.ndarray)

        # height, width = sk.image.shape[0], sk.image.shape[1]
        # self.assertEqual(height, sk.h)
        # self.assertEqual(width, sk.w)
        pass

        


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

    suite.addTest(TestCaseScoreKey('test_instantiation'))
    # suite.addTest(TestCaseScoreKey('method_load_image'))

    suite.addTest(TestCaseColumn('test_instantiation'))

    suite.addTest(TestCaseRow('test_instantiation'))

    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
