import sys
import unittest

sys.path.append('../classes')
from scoreKey import Box, ScoreKey, Column

class TestCaseBox(unittest.TestCase):

    def setUp(self):
        self.box = Box(1, 2, 3, 4, 12, 0.75)
        
    def test_instantiation(self):
        b = Box(1, 2, 3, 4, 12, 0.75)
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
        self.scoreKey = ScoreKey(1, 2, 3, 4, 12, 0.75)

    def test_instantiation(self):
        sk = ScoreKey(1, 2, 3, 4, 12, 0.75)
        self.assertIsInstance(sk, ScoreKey)

### End ScoreKey
  
class TestCaseColumn(unittest.TestCase):

    def setUp(self):
        self.column = Column(1, 2, 3, 4, 12, 0.75)

    def test_instantiation(self):
        col = Column(1, 2, 3, 4, 12, 0.75)
        self.assertIsInstance(col, Column)

### End Column
  

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestCaseBox('test_instantiation'))
    suite.addTest(TestCaseBox('test_members'))

    suite.addTest(TestCaseScoreKey('test_instantiation'))

    suite.addTest(TestCaseColumn('test_instantiation'))

    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
