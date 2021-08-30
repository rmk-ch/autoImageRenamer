
import os
import sys
from loguru import logger
#from PIL import Image, ExifTags
import exifread
from datetime import datetime, timedelta
import re

logger.info('Hello')

class ImageRenamer:
    # Set list of valid file extensions
    __EXTENSIONS = [".jpg", ".jpeg", ".png", ".mov", ".arw"]
    __DATE_FORMAT = "%Y-%m-%d"
    __DATETIME_FORMAT = f"{__DATE_FORMAT}_%H-%M-%S"

    def __init__(self, inputFolder, outputFolder, dryRun, doCopy):
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
            if (fileExt.lower() not in self.__EXTENSIONS):
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
        self.doRename(finalRenames, doCopy)

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
        
        # create a dict that contains the number of entries
        allNewList = list(proposal.values())
        nEntriesTotalNew = dict.fromkeys(allNewList, 1)

        # find duplicates
        seen = set()
        duplicatesNew = set()
        for new in proposal.values():
            if new not in seen:
                seen.add(new)
            else:
                duplicatesNew.add(new)
                nEntriesTotalNew[new] = nEntriesTotalNew[new]+1
        
        # find all entries that have been marked as duplicates and rename them by adding a counter
        for old, new in proposal.items():
            if new in duplicatesNew:
                fileparts = os.path.splitext(new)
                newFilename = fileparts[0] + "_" +str(nEntriesTotalNew[new]).zfill(3) +fileparts[1]
                nEntriesTotalNew[new] = nEntriesTotalNew[new]-1
                proposal[old] = newFilename
                logger.info(f"Add duplicate-counter for old={old} to new={newFilename}")

        return proposal


    def doRename(self, finalFilenames, doCopy):
        # Rename the file
        for old, new in finalFilenames.items():
            if not self.__isDryRun:
                if doCopy:
                    logger.info(f"Copying {old} to {new}")
                    shutil.copyfile(old, new)
                else:
                    logger.info(f"Renaming {old} to {new}")
                    os.rename(old, new)
            else:
                if doCopy:
                    logger.info(f"Would copy {old} to {new}")
                else:
                    logger.info(f"Would rename {old} to {new}")


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

        try:
            times['creation'] = self.getFileCreated(filename)
        except:
            pass

        # Remove invalid entries
        times = { k:v for k, v in times.items() if v is not None }

        return times



    def getExifTime(self, filename):
        ## Extract EXIF image taken from filename and return datetime object
        # Open the image
        try:
            # Open image file for reading (binary mode)
            with open(filename, 'rb') as f:
                # Return Exif tags
                tags = exifread.process_file(f, details=False)
        except:
            logger.info(f"Opening file {filename} failed")
            raise ValueError()

        debugExif = 0
        if  debugExif == 1:
            for key, val in tags.items():
                logger.debug(f"{key}: \t {repr(val)}")

        tagIds = ['EXIF DateTimeOriginal', 'EXIF DateTimeDigitized', 'Image DateTime']
        datetime_objs = dict.fromkeys(tagIds)
        for tagId in tagIds:

            try:
                tagValue = tags[tagId]
            except:
                logger.info(f"EXIF tag ID {tagId} invalid for {filename}")
                datetime_objs[tagId] = None
                continue

            try:
                # extract relevant part
                datetime_str = tagValue.values
                datetime_objs[tagId] = datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
            except:
                logger.warning(f"EXIF tag {tagId} string {datetime_str} not parsable in {filename}")
                datetime_objs[tagId] = None
                continue

            logger.info(f"EXIF tag {tagId} parsed to {datetime_objs} from {filename}")

        # find oldest
        datetime_obj = self.findOldestTime(datetime_objs)
        logger.info(f"Extracted {datetime_obj} via EXIF from {filename}")

        return datetime_obj

    def getFilenameTime(self, filename):
        ## Extract date and time from file name and return datetime object

        filenameWithoutPath = os.path.basename(filename)

        datePattern = '^.*[^\d](\d{4})[-_]?(\d{2})[-_]?(\d{2}).*'
        timePattern = '(\d{2})[-_: ]?(\d{2})[-_: ]?(\d{2})[^\d]'
        datetimePattern = datePattern +'[-_ ]?' +timePattern

        # try full match at first
        reDateTime = re.match(datetimePattern, filenameWithoutPath)
        if reDateTime is not None:
            try:
                datetime_obj = datetime(year=int(reDateTime.group(1)), month=int(reDateTime.group(2)), day=int(reDateTime.group(3)), hour=int(reDateTime.group(4)), minute=int(reDateTime.group(5)), second=int(reDateTime.group(6)))
            except Exception as e:
                logger.warning(f"Datetime creation (A) failed with {e}")
        else:
            # if not found everything, try day only
            reDate = re.match(datePattern, filenameWithoutPath)
            if reDate is not None:
                try:
                    datetime_obj = datetime(year=int(reDate.group(1)), month=int(reDate.group(2)), day=int(reDate.group(3)))
                except Exception as e:
                    logger.warning(f"Datetime creation (A) failed with {e}")
            else:
                logger.info(f"Date pattern not found in filename {filename}")
                return None

        logger.info(f"Filename date/time {datetime_obj} extracted from {filename}")
        return datetime_obj

    def getFileCreated(self, filename):
        ## Get file creation date and time and return datetime object
        creationTimestamp = os.stat(filename).st_ctime
        datetime_obj = datetime.fromtimestamp(creationTimestamp)
        logger.info(f"File creation time {datetime_obj} found from {filename}")
        return datetime_obj


if __name__ == "__main__":
    # If folder path argument exists then use it
    # Else use the current running folder
    
    inputFolder = f"{os.getcwd()}/examples"
    outputFolder = f"{os.getcwd()}/output"
    dryRun = True
    doCopy = True
        
    #logFormat = '%(asctime)s\t%(name)s\t%(funcName)s\t%(levelname)s:\t%(message)s'
    x = ImageRenamer(inputFolder, outputFolder, dryRun, doCopy)
