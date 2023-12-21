import os, sys
import cv2 as cv
import unittest
import numpy as np
from os.path import abspath, join

sys.path.append('../classes')
from deshadower import Deshadower

PATH = "./test_files"
PATH_HOMO = abspath( join(PATH, "homography.png") )


class TestCaseDeshadower(unittest.TestCase):
	def setUp(self):
		img = cv.imread(PATH_HOMO)
		self.ds = Deshadower(img)


	def tearDown(self):
		ds = None


	def test_instantiation(self):
		ds = Deshadower()
		self.assertIsInstance(ds, Deshadower)

		img = cv.imread(PATH_HOMO)
		ds = Deshadower(img)
		self.assertIsInstance(ds, Deshadower)


	def test_members(self):
		img = cv.imread(PATH_HOMO)
		ds = Deshadower(img)
		self.assertIsInstance(ds.img, np.ndarray)


	def test_method_deshadow(self):
		img = cv.imread(PATH_HOMO)

		with self.subTest("Image is BGR"):
			ds = Deshadower(img)
			deshadowed = ds.deshadow(kernel=(7,7), ksize=21, threshold=230)
			self.assertIsInstance(deshadowed, np.ndarray)

		with self.subTest("Image is grayscale"):
			img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
			ds = Deshadower(img)
			deshadowed = ds.deshadow(kernel=(7,7), ksize=21, threshold=230)
			self.assertIsInstance(deshadowed, np.ndarray)

### END TEST METHODS ##############################################################




def suite():
	suite = unittest.TestSuite()
	suite.addTest(TestCaseDeshadower('test_instantiation'))
	suite.addTest(TestCaseDeshadower('test_members'))
	suite.addTest(TestCaseDeshadower('test_method_deshadow'))

	return suite


if __name__ == '__main__':
	runner = unittest.TextTestRunner()
	runner.run(suite())
