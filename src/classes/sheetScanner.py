import cv2
import imutils
import numpy as np
from collections import namedtuple
from typing import Union, List, Tuple, Dict, NoReturn, Any

from sheetUtilities import SheetUtilities


# Define type hints for the OpenCV contour and OpenCV image 
CV_Contour = 'np.ndarray[np.ndarray[np.ndarray[int]]]'
CV_Image = 'np.ndarray[int]'




class Sheet(SheetUtilities):
	"""
	Methods for processing any answer sheet. Assumes that the sheet contains
	answer bubbles.

	Attributes
	----------
	binary_threshold : int
		The pixel intensity to use when thresholding images. Must be in 
		between 0 and 255, exclusive. Values between 125 and 225 are typically
		appropriate for binarizing most answer sheets.

	image : ndarray, int
		The input image, compatible with OpenCV. May be grayscale or color.

	gray : ndarray, int
		Grayscale version of the input image. If the input is already grayscale,
		then, 'gray' will be identical to 'image'.

	edges : ndarray, int
		Edges of contours, extracted via the Canny algorithm. Currently unused.	
	
	binary : ndarray, int
		BW version of the input image. Threshold level is'binary_threshold'.

	inverted : ndarray, int
		WB version of the input image. Threshold level is'binary_threshold'.

	all_contours : list, Contour
		All external contours that are findable within the binary image, sorted
		descending by size. These are extracted by the constructor for 
		convenience.
	"""

	Point = namedtuple('Point', ['x', 'y'])


	def __init__(self, 
					image: Union[str, CV_Image], 
					binary_threshold: int=225
	) -> NoReturn:
		"""
		The constructor
		Parameter can be an opencv image (ndarray) or path to an image file

		Parameters
		----------
		image : str or ndarray 
			str = path/to/image.file
			ndarray = A numpy ndarray with 0, 1, or 3 channels

		binary_threshold : int
			The threshold to use when creating binary BW and inverted WB 
			versions of the input image. If the threshold value is bad,
			important sheet features will not be extracted. Values between
			100 and 225 are typically appropriate.

		"""
		if isinstance(image, str):
			self.image = cv2.imread(image)
		elif isinstance(image, np.ndarray):
			self.image = image
		else:
			raise TypeError(
				"""The input image must be either a file path (string), \nor an image (numpy ndarray with 2 or 3 channels.)"""
			)

		if isinstance(binary_threshold, int):
			self.binary_threshold = binary_threshold
		else:
			raise TypeError("The binary_threshold must be an integer.")

		p = self.preprocess(self.image)
		self.gray = p[0]
		self.edges = p[1]
		self.binary = p[2]
		self.inverted = p[3]
		self.all_contours = self.extract_contours()
		self.all_contours = self.sort_contours_by_size(self.all_contours)


	def preprocess(self, 
					image: Union[CV_Image, None], 
					binary_threshold: int=None
	) -> Tuple[CV_Image, CV_Image, CV_Image, CV_Image]:
		"""
		Creates some helper images. The same threshold is used to create both
		the binary and inverted images.
		(1) Grayscale image
		(2)	Edges via the Canny algorithm
		(3) Binary image
		(4) Inverted binary image.

		Parameters
		----------
		image : ndarray, None
			Any image. If an image is not passed, the original image from the
			instance member is used.

		binary_threshold : int
			Value (0 to 255) used to threshold the image. The same value is
			used for both binary and inverted binary thresholding. If the
			binary_threshold is None, self.binary_threshold will be used.

		Returns
		-------
		ndarray
			A grayscale image.

		ndarray
			An image with edges emphasized via the Canny algorithm.

		ndarray
			A binary black and white image.

		ndarray
			An inverted binary white and black image.
		"""
		# If RGB, convert to gray
		if len(image.shape) == 3:
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		else:
			gray = image

		if binary_threshold is None:
			binary_threshold = self.binary_threshold

		edges = cv2.Canny(gray, 30, 150)
		binary = cv2.threshold(gray, binary_threshold, 255, cv2.THRESH_BINARY)[1]
		# print(np.unique(gray), np.unique(binary))
		inverted = cv2.threshold(gray, binary_threshold, 255, cv2.THRESH_BINARY_INV)[1]
		return gray, edges, binary, inverted


	def get_circularity(self, contour: CV_Contour) -> float:
		"""
		Computes the circularity (a.k.a. roundness) of a contour according to 

			circularaity = 4*pi*area / (perimeter**2)

		Parameters
		----------
		contour : ndarray
			An OpenCV contour

		Returns
		-------
		float
			The circularity of the contour from 0 to 1.0
		"""
		area = cv2.contourArea(contour)
		perimeter = cv2.arcLength(contour, closed=True)
		circularity = 4*np.pi*area * perimeter**(-2)
		return circularity


	def extract_contours(self, 
							image: CV_Image=None, 
							threshold: int=0, 
							maxval: int=255
	) -> Tuple[CV_Contour]:
		"""
		Finds all external contours in an image. The inverted binary of the
		input image will be computed using the given threshold and maxval
		parameters

		Parameters
		----------
		image : ndarray
			The image in which to find the contours. If the image is BGR, it 
			will be converted to grayscale. If image is None, self.gray will be
			used.

		threshold : int
			The binary threshold. This param will be passed to cv2.threshold()

		maxval : int
			The maximum white value (Default is 255). This param will be passed 
			to cv2.threshold()

		Returns
		-------
		tuple[CV_Contour]
			All the external contours in the image

		"""
		if image is None:
			gray = self.gray
		elif len(image.shape) == 3:  # convert img to grayscale if it isn't already
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		elif len(image.shape) == 2:
			gray = image
		else:
			# something has gone horribly wrong
			pass	

		inverted = cv2.threshold(gray, threshold, maxval, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1] # doesn't work on BW test shapes, use binary from self.preprocess() instead
		all_contours = cv2.findContours(inverted, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		all_contours = imutils.grab_contours(all_contours)
		
		return all_contours


	def sort_contours_by_size(self, 
								all_contours: List[CV_Contour], 
								descending: bool=True
	) -> List[CV_Contour]:
		"""
		Sorts contours by size. Default is descending order.

		Parameters
		----------
		all_contours : list, ndarray
			A list of OpenCV contours. Ideally all the external contours on an
			ACT answer sheet.

		descending : bool
			If True  --> sorts in descending size order
			If False --> sorts in ascending  size order

		Returns
		-------
		list, ndarray
			The input list of contours, sorted by size
		"""
		return sorted(all_contours, key=cv2.contourArea, reverse=descending)


	def show_contours(self, 
						image: CV_Image, 
						title: str, 
						contours: List[CV_Contour], 
						individual: bool=False, 
						line: int=-1
	) -> bool:
		"""
		Draws contours for visual inspection. Exits on Esc.

		Parameters
		----------
		image : ndarray 
			The image to draw on

		title : str 
			A title for the display window

		contours : list, ndarray 
			The list of contours to draw

		individual : bool 
			If True, shows the bubbles one-at-a-time
			If False, shows them all at once (faster)

		line : int 
			The line weight. -1 == filled

		Returns
		-------
		bool
			True if this method executed without errors
		"""
		if len(image.shape) == 2:  # grayscale
			image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

		img = image.copy()
		if individual:
			for c in contours:
				cv2.drawContours(img, [c], -1, (0,0,255), line)
				cv2.imshow(title, img)

				# DEBUGGING CODE
				# x,y,w,h = cv2.boundingRect(c)
				# area = w*h
				# ratio = w/h
				# print(f"x = {x}\t y = {y}\t w = {w}  h = {h}\t area = {area}   aspect = {round(ratio,5)}")

				if cv2.waitKey(0) == 27:  # Esc will kill the method
					break
		elif not individual:
			# img = image.copy()
			for c in contours:
				cv2.drawContours(img, [c], -1, (0,0,255), line)
			cv2.imshow(title, img)
			cv2.waitKey(0)

		cv2.destroyAllWindows()
		return True




	def count_pixels_of_contours(self, 
									contours: List[CV_Contour], 
									show_counts: bool=False
	) -> Dict[str, List[int]]:
		"""
		Receives a 1D list of contours and returns both the black and white  
		pixel counts within each contour's region of the BW binarized image
		(self.binary) The list typically represents the group of answer 
		bubbles for a single question.

		Parameters
		----------
		contours : list, ndarray 
			A list of opencv contours representing a group of test answer 
			bubbles for a single question

		show_counts : bool
			If true, prints white & black counts to console. Used for 
			debugging.

		Returns
		------- 
		dict  
			Key = 'b', 'w': black or white 
			Value = list of integers - pixel counts
			{'b':[int, ... int], 'w':[int, ... int]}

			The black and white pixel counts for each bubble in the group. The 
			index of a count corresponds to the position of a bubble:
			The zeroth count = choice A,
			The  first count = choice B, etc.

		"""
		binr = self.binary # the bw image``
		inv = self.inverted # the inverted binary image: black <--> white

		counts = {'b':[], 'w':[]} 
		counts['b'] = [None for c in contours] # holds the black pixel count of each bubble
		counts['w'] = [None for c in contours] # holds the white pixel count of each bubble

		for i,c in enumerate(contours):
			# count black pixels
			mask = np.zeros(inv.shape, dtype="uint8")
			cv2.drawContours(mask, [c], -1, 255, -1)
			invMask = cv2.bitwise_and(inv, inv, mask=mask)
			counts['b'][i] = cv2.countNonZero(invMask)

			# count white pixels
			mask = np.zeros(binr.shape, dtype="uint8")
			cv2.drawContours(mask, [c], -1, 255, -1)
			binMask = cv2.bitwise_and(binr, binr, mask=mask)
			counts['w'][i] = cv2.countNonZero(binMask)

			if show_counts:
				print(f"{i}: The black pixel count is {counts['b'][i]}")
				print(f"{i}: The white pixel count is {counts['w'][i]}")
		# 		cv2.imshow("Inverted Masked", invMask.copy())
		# 		cv2.imshow("Binary Masked", binMask.copy())
		# 		if cv2.waitKey(0) == 27: 
		# 			cv2.destroyAllWindows()
		# 			break
		# cv2.destroyAllWindows()

		return counts




	def count_pixels(self, 
						elements: List[CV_Contour], 
						el_mode: str, 
						mask_shape: Union[None, Tuple[str, List[int]]]=None, 
						show_counts: bool=False
	) -> Dict[str, List[int]]:
		"""
		Wrapper method, calls one of 
			count_pixels_of_contours(),

		Receives a 1D list of elements and returns both the black and white 
		pixel counts within each contour's region of the BW binarized image
		(self.binary) The list typically represents the group of answer 
		bubbles for a single question.


		Parameters
		----------
		elements : list
			A list of CV_Contours

		el_mode : str
			The element mode.
			One of 'contours', 'points'. (Not case sensitive)
			The mode must match the types of elements passed in 'elements'.

		mask_shape : tuple
			el_mode='contours' | None
			el_mode='points'   | (shape, [dimensions])
							     ('rectangle', [width, height])
							     ('circle', [radius])
			Holds shape and dimension arguments required when passing
			a list of Point objects (a.k.a. a section map). Dimensions are in
			pixels. It is not needed when passing contours; its default value
			is None.

		show_counts : bool
			If true, prints white & black counts to console. Used for 
			debugging.

		Returns
		------- 
		dict  
			Key = 'b', 'w': black or white 
			Value = list of integers - pixel counts
			{'b':[int, ... int], 'w':[int, ... int]}

			The black and white pixel counts for each bubble in the group. The 
			index of a count corresponds to the position of a bubble:
			The zeroth count = choice A,
			The  first count = choice B, etc.
		"""

		if ('contour' in el_mode.lower()) and isinstance(elements[0], np.ndarray):
			return self.count_pixels_of_contours(elements, show_counts)
		else:
			raise ValueError("The mode must be one of: 'contours'.",
							"\n",
							"The 'elements' arg must contain either contours.")

		return counts


	def find_darkest_from_contours(self, contours: List[CV_Contour]) -> int:
		"""
		Returns the index of the darkest bubble. Intended for use when an
		answer has been erased and its bubble is no longer white. If multiple
		bubbles are equivalently dark, returns the index of the first one.
		This method implicitly sorts the contours left-to-right. 

		Parameters
		----------
		contours : list, ndarray 
			A list of OpenCV contours representing 1 group of answer bubbles

		Returns
		------- 
		index : int
			The list index of the darkest bubble
		"""
		gray = self.gray

		# init large value for the sum of pixel values in the darkest bubble
		darkest = gray.shape[0]*gray.shape[1] 
		ix_darkest = 0  # counter for min_shade position

		contours = imutils.contours.sort_contours(contours, 'left-to-right')[0]

		for i,c in enumerate(contours):
			mask = np.zeros(gray.shape, dtype='uint8')
			cv2.drawContours(mask, [c], -1, 255, -1)
			masked = cv2.bitwise_and(gray, gray, mask=mask)
			sum_pixels = np.sum(masked)	
			if sum_pixels < darkest:
				darkest = sum_pixels
				ix_darkest = i

		return ix_darkest





	




	
