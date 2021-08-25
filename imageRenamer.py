
import os
import sys
from loguru import logger
from PIL import Image, ExifTags
from datetime import datetime, timedelta
import re

logger.info('Hello')

class ImageRenamer:
    # Set list of valid file extensions
    __EXTENSIONS = [".jpg", ".jpeg", ".png"]
    __DATE_FORMAT = "%Y-%m-%d"
    __DATETIME_FORMAT = f"{__DATE_FORMAT}_%H-%M-%S"

    def __init__(self, inputFolder, outputFolder):
        self.__inputFolder = inputFolder
        self.__outputFolder = outputFolder
        self.__isDryRun = True

        logger.info(f"Renaming images from {inputFolder} to {outputFolder}")

        # Get all files from folder
        fileNames = os.listdir(self.__inputFolder)

        proposedRenames = dict()

        # For each file
        for fileName in fileNames:
                
            # Get the file extension
            fileExt = os.path.splitext(fileName)[1]

            # If the file does not have a valid file extension
            # then skip it
            if (fileExt not in self.__EXTENSIONS):
                continue

            # Create the old file path
            oldFilePath = os.path.join(self.__inputFolder, fileName)

            # try various options
            times = self.getTimes(oldFilePath)
            if len(times) < 1:
                logger.warning(f"Found no suitable time to rename for file {oldFilePath}. Skipping this file.")
                continue

            # Find oldest timestamp to select
            oldest = self.findOldestTime(times)

            # Propose new file name and file extension in a mapping
            if oldest.hour == 0 and oldest.minute == 0 and oldest.second == 0:
                format = self.__DATE_FORMAT
            else:
                format = self.__DATETIME_FORMAT
            newFilename = oldest.strftime(format) + fileExt.lower()
            proposedRenames[oldFilePath] =  os.path.join(outputFolder, newFilename)

        # Find collisions in proposal
        finalRenames = self.fixCollisions(proposedRenames)

        # Actual Renames
        self.doRename(finalRenames)

    def findOldestTime(self, times):
        if len(times) < 1:
            logger.error('No times entry to select')
            raise ValueError()

        oldestValue = min(times.values())
        res = [key for key in times if times[key] == oldestValue]
        logger.debug(f"Oldest value ({oldestValue.strftime(self.__DATETIME_FORMAT)}) found by method {res}")
        return oldestValue

        
    def fixCollisions(self, proposal):
        ## Find collisions new filename and append incrementing number
        #allTargets = list(proposal.values())
        # find duplicates
        logger.warning('Collision fixing not implemented. Returning with potential duplicates!')
        return proposal #uniquified


    def doRename(self, finalFilenames):
        # Rename the file
        for old, new in finalFilenames.items():
            if ~self.__isDryRun:
                logger.info(f"Renaming/moving {old} to {new}")
                #os.rename(old, new)
            else:
                logger.info(f"Would rename/move {old} to {new}")

    def getTimes(self, filename):
    
        times = dict()
        try:
            times['exif'] = self.getExifTime(filename)
        except:
            pass
            
        try:
            times['filename'] = self.getFilenameTime(filename)
        except:
            pass
        # try:
        #     times['filenameWA'] = self.getFromFilenameWA(filename)
        # except:
        #     logging.warn('No filenameWA time found')

        # Remove invalid entries
        times = { k:v for k, v in times.items() if v is not None }

        return times



    def getExifTime(self, filename):
        ## Extract EXIF image taken from filename and return datetime object
        # Open the image
        try:
            image = Image.open(filename)
        except:
            logger.info(f"Opening file {filename} failed within Image")
            raise ValueError()

        # Get the date taken from EXIF metadata
        exifDict = image.getexif()

        # Close the image
        image.close()

        debugExif = 1
        if  debugExif == 1:
            for key, val in exifDict.items():
                if key in ExifTags.TAGS:
                    logger.debug(f"{key}: {ExifTags.TAGS[key]} \t {repr(val)}")
                else:
                    logger.debug(f"{key}: n/a \t {repr(val)}")

        try:
            datetime_str = exifDict[306]
        except:
            logger.info(f"EXIF data entry invalid for {filename}")
            return None

        try:
            datetime_obj = datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
        except:
            logger.error(f"EXIF entry string {datetime_str} not parsable in {filename}")
            raise ValueError(f"EXIF entry string {datetime_str} not parsable in {filename}")

        logger.info(f"EXIF date {datetime_obj} extracted from {filename}")

        return datetime_obj

    def getFilenameTime(self, filename):
        ## Extract date and time from file name and return datetime object

        filenameWithoutPath = os.path.basename(filename)

        datePattern = '^.*(\d{4})[-_]?(\d{2})[-_]?(\d{2}).*'
        result = re.match(datePattern, filenameWithoutPath)
        if result is None:
            logger.info(f"Date pattern not found in filename {filename}")
            return None
        
        datetime_obj = datetime(year=int(result.group(1)), month=int(result.group(2)), day=int(result.group(3)))

        timePattern = '(\d{2})[-_: ]?(\d{2})[-_: ]?(\d{2})'
        datetimePattern = datePattern +'[-_ ]?' +timePattern
        result = re.match(datetimePattern, filenameWithoutPath)
        if result is not None:
            datetime_obj += timedelta(hours=int(result.group(4)), minutes=int(result.group(5)), seconds=int(result.group(6)))

        logger.info(f"Filename time {datetime_obj} extracted from {filename}")

        return datetime_obj


if __name__ == "__main__":
    # If folder path argument exists then use it
    # Else use the current running folder
    
    inputFolder = f"{os.getcwd()}/examples"
    outputFolder = f"{os.getcwd()}/output"
        
    #logFormat = '%(asctime)s\t%(name)s\t%(funcName)s\t%(levelname)s:\t%(message)s'
    x = ImageRenamer(inputFolder, outputFolder)
