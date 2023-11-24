import os, sys
import cv2 as cv
import unittest
import numpy as np
from os.path import abspath, join

sys.path.append('../classes')
from dewarper import Dewarper

PATH = "./test_files"
PATH_HOMO = abspath( join(PATH, "homography.png") )
PATH_ROT = abspath( join(PATH, "homography_rotated.png") )
# print(PATH_HOMO)

FLAG_SHOW_DISPLAY_METHODS = False


class TestCaseDewarper(unittest.TestCase):
	def setUp(self):
		pass


	def tearDown(self):
		pass


	def test_instantiation(self):
		with self.subTest("No args"):
			dw = Dewarper()
			self.assertIsInstance(dw, Dewarper)
		with self.subTest("Args are string paths"):
			dw = Dewarper(PATH_HOMO, PATH_HOMO)
			self.assertIsInstance(dw, Dewarper)
		with self.subTest("Args are images"):
			ref = cv.imread(PATH_HOMO)
			img = cv.imread(PATH_ROT)
			dw = Dewarper(ref, img)


	def test_members(self):
		dw = Dewarper()
		self.assertIsInstance(dw.MIN_MATCH_COUNT, int)
		self.assertIsInstance(dw.MATCH_RATIO, float)

		self.assertIsInstance(dw.matches, list)
		self.assertEqual(len(dw.matches), 0)
		self.assertIsInstance(dw.good_matches, list)
		self.assertEqual(len(dw.good_matches), 0)

		self.assertIsInstance(dw.sifter, cv.SIFT)
		self.assertIsInstance(dw.fanner, cv.FlannBasedMatcher)

		self.assertIsNone(dw.ref)
		self.assertIsNone(dw.og)
		self.assertIsNone(dw.img)
		self.assertIsNone(dw.dewarped)
		self.assertIsNone(dw.dewarped_gray)

		self.assertIsNone(dw.transformation_matrix)
		self.assertIsNone(dw.homo_mask)
		self.assertIsNone(dw.perspective_transform)

		dw = Dewarper(PATH_HOMO, PATH_HOMO)

		self.assertIsInstance(dw.ref, np.ndarray)
		self.assertIsInstance(dw.og,  np.ndarray)
		self.assertIsInstance(dw.img, np.ndarray)
		# print(dw.ref.shape)

		# verify that images are 2D grayscale (no 3rd dim) -- OG should be BGR
		self.assertEqual(len(dw.ref.shape), 2)
		self.assertEqual(len(dw.img.shape), 2)
		self.assertEqual(len(dw.og.shape),  3)

		self.assertEqual(repr(type(dw.kpd_ref)), "<class 'dewarper.Kpd'>")
		self.assertEqual(repr(type(dw.kpd_img)), "<class 'dewarper.Kpd'>")


	def test_method_load(self):
		dw = Dewarper()

		dw.load(PATH_HOMO, 'ref')
		self.assertEqual(len(dw.ref.shape), 2)

		dw.load(PATH_HOMO, 'img')
		self.assertEqual(len(dw.og.shape), 3)
		self.assertEqual(len(dw.img.shape), 2)

		# raise error if 'flag' param is not one of 'ref', 'r', 'img', 'i'
		with self.assertRaises(ValueError):
			dw.load(PATH_HOMO, 'bad_arg')


	def test_method_sift(self):
		# The homography image should have 124 keypoints. 
		# Each kp will have 128 descriptor values by default.
		dw = Dewarper(PATH_HOMO, PATH_HOMO)

		dw.sift('ref')
		kpdr = dw.kpd_ref
		self.assertEqual(len(kpdr.kp), 124)
		self.assertEqual(kpdr.des.shape, (124,128))

		dw.sift('img')
		kpdi = dw.kpd_img
		self.assertEqual(len(kpdi.kp), 124)
		self.assertEqual(kpdi.des.shape, (124,128))

		# @TODO Implement value checks of intermediate objects
		# dw = Dewarper(PATH_HOMO, PATH_ROT)
		# dw.sift('ref')
		# kpdr = dw.kpd_ref
		# dw.sift('img')
		# kpdi = dw.kpd_img
		# sf = pickle.load(PATH_SF)
		# skpr = sf['ref']['kp']
		# skpi = sf['img']['kp']


	def test_method_fann(self):
		dw = Dewarper(PATH_HOMO, PATH_HOMO)
		dw.sift('ref')
		dw.sift('img')
		dw.fann()

		self.assertEqual(len(dw.matches), 124)
		self.assertEqual(len(dw.matches[0]), 2)
		self.assertIsInstance(dw.matches[0][0], cv.DMatch)
		self.assertIsInstance(dw.matches[0][1], cv.DMatch)


	def test_method_filter_matches(self):
		dw = Dewarper(PATH_HOMO, PATH_HOMO)
		dw.sift('ref')
		dw.sift('img')
		dw.fann()
		dw.filter_matches()

		self.assertEqual(len(dw.good_matches), 120)


	def test_method_get_homography(self):
		dw = Dewarper(PATH_HOMO, PATH_HOMO)
		dw.sift('ref')
		dw.sift('img')
		dw.fann()
		dw.filter_matches()
		dw.get_homography()

		M = dw.transformation_matrix
		mask = dw.homo_mask
		self.assertIsInstance(M, np.ndarray)
		self.assertEqual(M.shape, (3,3))
		self.assertIsInstance(mask, list)
		self.assertEqual(len(mask), 120)


	def test_method_apply_transform(self):
		dw = Dewarper(PATH_HOMO, PATH_HOMO)
		dw.sift('ref')
		dw.sift('img')
		dw.fann()
		dw.filter_matches()
		dw.get_homography()
		dw.apply_transform()

		pTrans = dw.perspective_transform
		self.assertIsInstance(pTrans, np.ndarray)
		self.assertEqual(pTrans.shape, (4,1,2))


	def test_method_show_homography(self):
		dw = Dewarper(PATH_HOMO, PATH_ROT)
		dw.sift('ref')
		dw.sift('img')
		dw.fann()
		dw.filter_matches()
		dw.get_homography()
		dw.apply_transform()

		if FLAG_SHOW_DISPLAY_METHODS == True:
			dw.show_homography()


	def test_method_dewarp_image(self):
		dw = Dewarper(PATH_HOMO, PATH_HOMO)
		dw.sift('ref')
		dw.sift('img')
		dw.fann()
		dw.filter_matches()
		dw.get_homography()
		dw.dewarp_image()

		with self.subTest("Dewarped image is class member"):
			self.assertEqual(len(dw.og.shape), len(dw.dewarped.shape))
			self.assertEqual(len(dw.ref.shape), len(dw.dewarped_gray.shape))
			self.assertEqual(dw.ref.shape, dw.dewarped.shape[0:2])
			self.assertEqual(dw.ref.shape, dw.dewarped_gray.shape)
			similarity = cv.matchTemplate(dw.dewarped_gray, dw.ref, 3).round(3)
			self.assertEqual(similarity[0][0], 1.0)

		with self.subTest("Dewarped image is returned"):
			dewarped = dw.dewarp_image()
			self.assertEqual(len(dw.ref.shape), len(dewarped.shape))
			self.assertEqual(dw.ref.shape, dewarped.shape[0:2])


	def test_method_dewarp(self):
		with self.subTest("Basic Homography - Identical Images"):
			dw = Dewarper(PATH_HOMO, PATH_HOMO)
			dw.dewarp()

			self.assertEqual(len(dw.og.shape), len(dw.dewarped.shape))
			self.assertEqual(len(dw.ref.shape), len(dw.dewarped_gray.shape))
			self.assertEqual(dw.ref.shape, dw.dewarped.shape[0:2])
			self.assertEqual(dw.ref.shape, dw.dewarped_gray.shape)
			similarity = cv.matchTemplate(dw.dewarped_gray, dw.ref, 3).round(3)
			self.assertEqual(similarity[0][0], 1.0)

			dw = Dewarper()
			with self.assertRaises(ValueError):
				dw.dewarp()

			dw = Dewarper()
			with self.assertRaises(ValueError):
				# Should print: "The warped image is missing. Pass the file path explicitly."
				dw.dewarp(ref=PATH_HOMO)

			dw = Dewarper()
			with self.assertRaises(ValueError):
				# Should print: "The reference image is missing. Pass the file paths explicitly."
				dw.dewarp(img=PATH_HOMO)


		with self.subTest("Basic Homography - Rotated Image"):
			dw = Dewarper()
			dw.dewarp(PATH_HOMO, PATH_ROT)

			self.assertEqual(len(dw.og.shape), len(dw.dewarped.shape))
			self.assertEqual(len(dw.ref.shape), len(dw.dewarped_gray.shape))
			self.assertEqual(dw.ref.shape, dw.dewarped.shape[0:2])
			self.assertEqual(dw.ref.shape, dw.dewarped_gray.shape)
			similarity = cv.matchTemplate(dw.dewarped_gray, dw.ref, 3).round(3)
			self.assertGreater(similarity[0][0], 0.99)


		with self.subTest("Passing Images Directly to Method"):
			ref = cv.imread(PATH_HOMO)
			img = cv.imread(PATH_HOMO)

			dw = Dewarper()
			dw.dewarp(ref, img)

			self.assertEqual(len(dw.og.shape), len(dw.dewarped.shape))
			self.assertEqual(len(dw.ref.shape), len(dw.dewarped_gray.shape))
			self.assertEqual(dw.ref.shape, dw.dewarped.shape[0:2])
			self.assertEqual(dw.ref.shape, dw.dewarped_gray.shape)
			similarity = cv.matchTemplate(dw.dewarped_gray, dw.ref, 3).round(3)
			self.assertEqual(similarity[0][0], 1.0)

			# Returning the result from the method
			dewarped = dw.dewarp(ref, img)
			self.assertEqual(dw.ref.shape, dewarped.shape[0:2])	


### END TEST METHODS ##############################################################




def suite():
	suite = unittest.TestSuite()
	suite.addTest(TestCaseDewarper('test_instantiation'))
	suite.addTest(TestCaseDewarper('test_members'))
	suite.addTest(TestCaseDewarper('test_method_load'))
	suite.addTest(TestCaseDewarper('test_method_sift'))
	suite.addTest(TestCaseDewarper('test_method_fann'))
	suite.addTest(TestCaseDewarper('test_method_filter_matches'))
	suite.addTest(TestCaseDewarper('test_method_get_homography'))
	suite.addTest(TestCaseDewarper('test_method_apply_transform'))
	suite.addTest(TestCaseDewarper('test_method_show_homography'))
	suite.addTest(TestCaseDewarper('test_method_dewarp_image'))
	suite.addTest(TestCaseDewarper('test_method_dewarp'))

	return suite


if __name__ == '__main__':
	runner = unittest.TextTestRunner()
	runner.run(suite())
