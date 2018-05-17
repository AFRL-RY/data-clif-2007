# example script on how to read a NITF file in Python
# tested with CLIF 2007 data that has been truthed
# assumes you are using Enthought Canopy version 1.5 which comes with GDAL
import gdal
from gdalconst import *
import argparse
import sys
import numpy as np
import matplotlib.pyplot as plt
#import cv2 as cv # only needed if you want to convert the image

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--fileNameNITF",
		help="name of NITF file to read full path",
		action="store", required=True)
	args = parser.parse_args()
	data = {}
	data['args'] = args
	data['fileNameNITF'] = args.fileNameNITF
	dataset = gdal.Open( data['fileNameNITF'], GA_ReadOnly )
	if dataset is None:
		print("dataset is None that is bad")
		sys.exit(2)
	print 'Driver: ', dataset.GetDriver().ShortName, '/', dataset.GetDriver().LongName
	print 'Size is ', dataset.RasterXSize, 'x', dataset.RasterYSize, 'x', dataset.RasterCount
	print 'Projection is ', dataset.GetProjection()

	geotransform = dataset.GetGeoTransform()
	if not geotransform is None:
		print 'Origin = (',geotransform[0], ',',geotransform[3],')'
		print 'Pixel Size = (',geotransform[1], ',',geotransform[5],')'

	band = dataset.GetRasterBand(1)

	print 'Band Type=',gdal.GetDataTypeName(band.DataType)

	min = band.GetMinimum()
	max = band.GetMaximum()
	if min is None or max is None:
		(min,max) = band.ComputeRasterMinMax(1)
	print 'Min=%.3f, Max=%.3f' % (min,max)

	if band.GetOverviewCount() > 0:
		print 'Band has ', band.GetOverviewCount(), ' overviews.'

	if not band.GetRasterColorTable() is None:
		print 'Band has a color table with ', \
		band.GetRasterColorTable().GetCount(), ' entries.'

	# Read the data from the NITF file and place into a numpy array
	# ReadAsArray(self, xoff=0, yoff=0, win_xsize=None, win_ysize=None, 
	# buf_xsize=None, buf_ysize=None, buf_obj=None)	
	# band.XSize is how many pixels in left to right
	# band.YSize is how many pixels up to down
	# this grabs the OSU stadium in frame ~/data/CLIF2007/20071028142502-01000100-VIS.ntf.r0
	# you can display the entire frame but matplot lib is slow
	#scanlineArray = band.ReadAsArray(6000, 5000, 1000, 1000, 
	#	1000, 1000)
	#
	# reads the entire image at full resolution, this will put the track on the
	# correct vehicle
	scanlineArray = band.ReadAsArray(0, 0, dataset.RasterXSize, 
		dataset.RasterYSize, dataset.RasterXSize, dataset.RasterYSize)
	print scanlineArray.shape
	print type(scanlineArray[0][0])
	# this line saves the image data as a jpg a good way to do conversion, if 
	# you want to get the data out of the NITF file format, you can use OpenCV
	# and imwrite the image out as a jpeg file
	# cv.imwrite("/Users/rovitotv/temp/output.jpg", scanlineArray)

	plt.imshow(scanlineArray, cmap=plt.cm.gray)
	# # a truth track is here in frame 101 with file name 20071028142503-01000101-VIS.ntf.r0
	# # "40.0042089249342","-83.0158241043238"
	# x_track = (-83.0158241043238 - geotransform[0]) * (1.0/geotransform[1]) # lon
	# y_track = (40.0042089249342 - geotransform[3]) * (1.0/geotransform[5])  # lat
	# plt.plot(x_track, y_track, 'ro')
	# print("x_track: %d y_track: %d" % (x_track, y_track))
	plt.show()



	



