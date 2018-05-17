# This Python script was created for tutorial on parallel processing with
# Python.  It will read in CLIF data equalize and output a png or pmg.
#
# 11/20/2013: Updated script to use argparse and dictionary to hold global
# information
#
import numpy as np
import glob as glob
import os as os
import sys
import argparse
from skimage import io
from skimage import exposure
import PIL
import PIL.ImageDraw as image_draw
import PIL.ImageFont as image_font


def getFrameNumber(data):
    sensorDataFileNameBase = os.path.basename(data['posFileName'])
    frameNumberString = sensorDataFileNameBase[7:13]
    data['frameNumber'] = int(frameNumberString)


def readSensorData(data):
    print("readSensorData:%s" % (data['posFileName']))
    data['sensorData'] = np.zeros((data['sensorHeight'],
                                   data['sensorWidth'], 6),
                                  dtype=np.int32)
    # build the sensor data file names
    sensorDataFileNameList = []
    for sensorNumber in range(0, 6):
        sensorEndPath = "%06d-%06d.raw" % (sensorNumber, data['frameNumber'])
        if sensorNumber <= 0:
            sensorDirectory = "Camera_0"
        else:
            sensorDirectory = "Fix_Camera%d" % sensorNumber

        sensorDataFileName = (data['inputDirectory'] + "/" + sensorDirectory +
                              "/" + sensorEndPath)
        sensorDataFileNameList.append(sensorDataFileName)
    for sensorIndex in range(0, 6):
        fd = open(sensorDataFileNameList[sensorIndex], 'rb')
        data['sensorData'][:, :, sensorIndex] = (
            np.fromfile(fd, dtype=np.uint8).reshape(
                (data['sensorHeight'], data['sensorWidth'])))
        fd.close()


def writePGM(image, outputFileName):
    f = open(outputFileName, 'wb')
    f.write('P5 ')
    f.write(str(image.shape[1]) + ' ' + str(image.shape[0]) + ' ')
    f.write('255\n')
    image.tofile(f)
    f.close()


def calculateOutputFileName(data, endFileName):
    savePath = data['outputDirectory']
    fileType = data['fileType']
    sensorEndPath = "%06d-%06d%s.%s" % (0, data['frameNumber'], endFileName,
                                        fileType)
    sensorDataFileName = "%s/%s" % (savePath, sensorEndPath)
    return sensorDataFileName

def embedCameraNumbers(data):
    '''
        uses pillow to embeed camera number in respective camera
    '''
    img = PIL.Image.fromarray(data['rawStitch'])
    draw = image_draw.Draw(img)
    font = image_font.truetype("/Library/Fonts/Arial.ttf", 960)
    for sensorIndex in range(0, 6):
        if sensorIndex == 0:
            widthOffset = data['sensorHeight']
            heightOffset = data['sensorWidth']
        elif sensorIndex == 1:
            widthOffset = data['sensorHeight']
            heightOffset = 0
        elif sensorIndex == 2:
            widthOffset = 0
            heightOffset = data['sensorWidth']
        elif sensorIndex == 3:
            widthOffset = 0
            heightOffset = 0
        elif sensorIndex == 4:
            widthOffset = 2 * data['sensorHeight']
            heightOffset = data['sensorWidth']
        elif sensorIndex == 5:
            widthOffset = 2 * data['sensorHeight']
            heightOffset = 0

        x = widthOffset + ( (data['sensorHeight'] / 2) - 200)
        y = heightOffset + ( (data['sensorWidth'] / 2) - 200)
        draw.text((x, y), ("%d" % sensorIndex), font=font, fill=(255, 255, 255, 192))

    data['rawStitch'] = np.array(img)

def drawBorderOutlines(data):
    # now draw lines to define the camera borders
    for column in range(data['sensorHeight'] - 5, data['sensorHeight'] + 5):
        data['rawStitch'][:, column] = 255
    for column in range(data['sensorHeight'] * 2 - 5, data['sensorHeight'] * 2 + 5):
        data['rawStitch'][:, column] = 255
    for row in range(data['sensorWidth'] - 5, data['sensorWidth'] + 5):
        data['rawStitch'][row, :] = 255


def saveSensorDataAsStitchedFrame(data, endFileName):
    print("savingSensordataAsStitchedFrame: %s" % (data['posFileName']))
    sensorDataFullFileName = calculateOutputFileName(data, endFileName)
    rawStitch = np.zeros((2*data['sensorWidth'], 3*data['sensorHeight']),
                         dtype=np.uint8)
    for sensorIndex in range(0, 6):
        if sensorIndex == 0:
            widthOffset = data['sensorHeight']
            heightOffset = data['sensorWidth']
            rot90Direction = 1
        elif sensorIndex == 1:
            widthOffset = data['sensorHeight']
            heightOffset = 0
            rot90Direction = -1
        elif sensorIndex == 2:
            widthOffset = 0
            heightOffset = data['sensorWidth']
            rot90Direction = 1
        elif sensorIndex == 3:
            widthOffset = 0
            heightOffset = 0
            rot90Direction = -1
        elif sensorIndex == 4:
            widthOffset = 2 * data['sensorHeight']
            heightOffset = data['sensorWidth']
            rot90Direction = 1
        elif sensorIndex == 5:
            widthOffset = 2 * data['sensorHeight']
            heightOffset = 0
            rot90Direction = -1
        dataClipped = np.zeros((data['sensorHeight'], data['sensorWidth']),
                               dtype=np.uint32)
        np.clip(data['sensorData'][:, :, sensorIndex], 0, 255, out=dataClipped)
        originalData = dataClipped.astype('uint8')
        rawRotate90 = np.rot90(originalData, rot90Direction)
        raw = np.fliplr(rawRotate90)
        rawStitch[heightOffset:heightOffset+data['sensorWidth'],
                  widthOffset:widthOffset+data['sensorHeight']] = raw
    data['stitchedFrameFullFileName'] = sensorDataFullFileName
    data['rawStitch'] = rawStitch
    # the code below rescales all the intensities to make the entire image
    # brighter.  
    v_min, v_max = np.percentile(data['rawStitch'], (0.75, 99.0))
    data['rawStitch'] = exposure.rescale_intensity(data['rawStitch'], in_range=(v_min, v_max))
    if data['showCameraNumbers']:
        embedCameraNumbers(data)
    if data['borderOutline']:
        drawBorderOutlines(data)
    if data['fileType'] == 'png':
        io.imsave(sensorDataFullFileName, data['rawStitch'])
    else:
        writePGM(data['rawStitch'], sensorDataFullFileName)


def CDFrameProcess(data):
    fileNameEqual = calculateOutputFileName(data, "equal")
    if not os.path.exists(fileNameEqual):
        readSensorData(data)
        data['averageBasePixelValue'] = data['sensorData'][:, :, 0].mean()
        for sensorIndex in range(1, 6):
            averagePixelValue = data['sensorData'][:, :, sensorIndex].mean()
            delta = data['averageBasePixelValue'] - averagePixelValue
            data['sensorData'][:, :, sensorIndex] = (
                data['sensorData'][:, :, sensorIndex] + delta)
            print("sensorIndex: %d delta: %d" % (sensorIndex, delta))
        saveSensorDataAsStitchedFrame(data, "equal")
        del data['sensorData']
    else:
        print("pos file: %s skipped because output already exists" %
              (data['posFileName']))


def CDFrameEqualization(data):
    '''function that does most of the processing'''
    print("file type: %s" % data['fileType'])
    print("input directory: %s" % data['inputDirectory'])
    print("output directory: %s" % data['outputDirectory'])
    # get the directory listing
    dataPathFilter = data['inputDirectory'] + "/txt_files/*.txt"
    posFiles = glob.glob(dataPathFilter)
    posFiles.sort()     # make sure the pos files are sorted
    # posFiles becomes a global task list that each thread has on its own
    for k in range(0, len(posFiles)):
        posFileName = posFiles[k]
        data['posFileName'] = posFileName
        # check to make sure this frame should be processed by this worker
        getFrameNumber(data)
        data['posFileName'] = posFiles[k]
        CDFrameProcess(data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Stitch CLIF 2007 data')
    parser.add_argument('-f', '--fileType', required=True,
                        help='file type for the output pgm or png')
    parser.add_argument('-o', '--outputDirectory', required=True,
                        help='directory for the output')
    parser.add_argument('-i', '--inputDirectory', required=True,
                        help='input directory of raws and pos files')
    parser.add_argument('-n', '--numberOfThreads', required=True, type=int,
                        help='number of threads to create')
    parser.add_argument('-s', '--showCameraNumbers', required=False,
        help="To show camera numbers specify true or True")
    parser.add_argument('-b', '--borderOutline', required=False,
        help="To show border outline specify true or True")
    args = parser.parse_args()
    data = {}
    data['args'] = args
    data['fileType'] = args.fileType
    data['outputDirectory'] = args.outputDirectory
    data['inputDirectory'] = args.inputDirectory
    data['numberOfThreads'] = args.numberOfThreads
    if args.showCameraNumbers:
        data['showCameraNumbers'] = True
    else:
        data['showCameraNumbers'] = False
    if args.borderOutline:
        data['borderOutline'] = True
    else:
        data['borderOutline'] = False
    data['sensorWidth'] = 4016
    data['sensorHeight'] = 2672
    # now create a process (aka thread) and process the data
    CDFrameEqualization(data)
    print("stitch and convert completed")
