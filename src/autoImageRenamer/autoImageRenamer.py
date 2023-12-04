import os
import shutil
from enum import Enum
from datetime import datetime
from loguru import logger
import exifread
import hachoir.parser
import hachoir.metadata
import re
import hashlib
import traceback as tb



def getFileHash(filename: str):
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(filename, "rb") as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()


def findDuplicates(inputs: dict) -> dict:
    ## General duplicate finder. Input is a dictionary with keys and values.
    # Returns a dictionary having:
    # 1. keys that correspond to the duplicate values
    # 2. set of values that contain the keys of the input dict

    # find duplicate target names
    seen = set()
    duplicates = dict()
    for value in inputs.values():
        if value not in seen:
            seen.add(value)
        else:
            duplicates[value] = list()

    # now find the keys to the duplicate values
    duplicateKeys = duplicates.keys()
    for k, v in inputs.items():
        if v in duplicateKeys:
            duplicates[v].append(k)

    return duplicates


class AutoImageRenamer:
    # Set list of valid file extensions
    __EXTENSIONS = [".jpg", ".jpeg", ".png", ".mov", ".mp4", ".arw"]
    __DATE_FORMAT = "%Y-%m-%d"
    __DATETIME_FORMAT = f"{__DATE_FORMAT}_%H-%M-%S"

    class Action(Enum):
        copy = 1
        rename = 2
        dryrun = 3

    def __init__(self, inputFolder, outputFolder, action, interactive, append):
        self.__inputFolder = inputFolder
        self.__outputFolder = outputFolder
        self.__action = action
        self.__interactive = interactive
        self.__append = append

        logger.info(f"Doing {action.name} from {inputFolder} to {outputFolder}")

        # Get all files from folder
        fileNames = os.listdir(self.__inputFolder)
        fileNames.sort()

        proposedRenames = dict()
        self.__fromMethods = dict()

        # For each file
        for fileName in fileNames:

            # Get the file extension
            filenameParts = os.path.splitext(fileName)
            fileExt = filenameParts[1]
            fileNoext = filenameParts[0]

            # If the file does not have a valid file extension
            # then skip it
            if fileExt.lower() not in self.__EXTENSIONS:
                continue

            # Create the old file path
            oldFilePath = os.path.normpath(os.path.join(self.__inputFolder, fileName))

            # try various options
            times = self.getTimes(oldFilePath, fileExt)
            if len(times) < 1:
                logger.warning(
                    f"Found no suitable time to rename for file {oldFilePath}. Skipping this file."
                )
                continue

            # Find oldest timestamp to select
            (oldest, self.__fromMethods[oldFilePath]) = self.findOldestTime(times)

            # Propose new file name and file extension in a mapping
            if (
                oldest.hour == 23
                and oldest.minute == 59
                and oldest.second == 59
                and oldest.microsecond == 999
            ):
                format = self.__DATE_FORMAT
            else:
                format = self.__DATETIME_FORMAT
            if self.__append:
                append = f"-{fileNoext}"
            else:
                append = ""
            newFilename = oldest.strftime(format) + append + fileExt.lower()
            proposedRenames[oldFilePath] = os.path.join(outputFolder, newFilename)

        # Find collisions in proposal
        self.__finalRenames = self.fixCollisions(proposedRenames)

        # Print interactively
        if self.__interactive:
            self.takeAction(self.__finalRenames, self.Action.dryrun)
            if self.__action == self.Action.dryrun:
                logger.info(
                    "Finished. If you're happy, rerun it with actual rename/copy command"
                )
                return
            userinp = input("Do you want to continue? [Y/n]: ")
            logger.debug(f"Entered '{userinp}'")
            if userinp != "y" and userinp != "Y" and len(userinp) > 0:
                logger.info(f"Finished")
                return
            logger.info("Continuing...")

        # Actual Renames
        self.takeAction(self.__finalRenames, self.__action)
        logger.info("All done! Byebye!")

    def findOldestTime(self, times):
        if len(times) < 1:
            logger.error("No times entry to select")
            raise ValueError()

        oldestValue = min(times.values())
        methods = [key for key in times if times[key] == oldestValue]

        # TODO: If oldestValue is date, then datetime is later and therefore not chosen. TO BE FIXED
        logger.debug(
            f"Oldest value ({oldestValue.strftime(self.__DATETIME_FORMAT)}) found by method(s) {methods}"
        )
        return (oldestValue, methods)

    def fixCollisions(self, proposals: dict[str, str]):
        ## Find collisions new filename and append incrementing number

        # find duplicate target names
        duplicatesNewFilenames = findDuplicates(proposals)

        for newFilename, oldFilenames in duplicatesNewFilenames.items():
            # find duplicate content per (duplicate) newFilename
            hashes = dict()
            for oldFilename in oldFilenames:
                hashes[oldFilename] = getFileHash(oldFilename)

            # and remove the duplicates from our local duplicate list
            duplicatesOldFilenames = findDuplicates(hashes)
            for sameHash in duplicatesOldFilenames.values():
                isFirst = True
                for oldFilename in sameHash:
                    if isFirst:
                        isFirst = False
                        continue
                    filepartsNew = os.path.split(proposals[oldFilename])
                    filepartsOld = os.path.split(oldFilename)
                    newFilename = os.path.join(
                        filepartsNew[0], f"DUPLICATE_{filepartsOld[1]}"
                    )
                    proposals[oldFilename] = newFilename
                    oldFilenames.remove(oldFilename)
                    logger.debug(f"Removing {oldFilename} due to content duplicate")

            # finally, rename remaining duplicates by adding a counter
            nEntries = 1
            for oldFilename in oldFilenames:
                fileparts = os.path.splitext(proposals[oldFilename])
                newFilename = fileparts[0] + "_" + str(nEntries).zfill(3) + fileparts[1]
                nEntries += 1
                proposals[oldFilename] = newFilename
                logger.debug(
                    f"Add duplicate-counter for oldFilename={oldFilename} to new={newFilename}"
                )

        return proposals

    def takeAction(self, finalFilenames, action):
        # Setup action
        if action == self.Action.rename:

            def act(old, new, methods):
                logger.info(f"Renaming {old} to {new} (methods {methods})")
                try:
                    os.rename(old, new)
                except Exception as e:
                    logger.error(f"Renaming excepted with {''.join(tb.format_exception(type(e), e, None))}")

        elif action == self.Action.copy:

            def act(old, new, methods):
                logger.info(f"Copying {old} to {new} (methods {methods})")
                shutil.copyfile(old, new)

        else:

            def act(old, new, methods):
                oldBasename = os.path.basename(old)
                newBasename = os.path.basename(new)
                logger.info(
                    f"Proposing {oldBasename} to {newBasename} (methods {methods})"
                )

        # Act!
        for old, new in finalFilenames.items():
            act(old, new, self.__fromMethods[old])

    def getTimes(self, filename : str, fileExt : str):

        times = dict()
        if fileExt.lower() == ".mov":
            times["mov"] = self.getFileHachoir(filename)
        else:
            try:
                exifTimes = self.getExifTimes(filename)
                times.update(exifTimes)
            except:
                pass

        try:
            times["filename"] = self.getFilenameTime(filename)
        except:
            pass

        # we could also take into account file creation date on filesystem. this seems very inaccurate though and we prefer no rename at all
        # try:
        #    times['creation'] = self.getFileCreated(filename)
        # except:
        #    pass

        # Remove invalid entries
        times = {k: v for k, v in times.items() if v is not None}

        return times

    def getExifTimes(self, filename):
        ## Extract EXIF image taken from filename and return datetime object
        # Open the image
        try:
            # Open image file for reading (binary mode)
            with open(filename, "rb") as f:
                # Return Exif tags
                tags = exifread.process_file(f, details=False)
        except:
            logger.debug(f"Opening file {filename} failed")
            raise ValueError()

        debugExif = 0
        if debugExif == 1:
            for key, val in tags.items():
                logger.debug(f"{key}: \t {repr(val)}")

        tagIds = ["EXIF DateTimeOriginal", "EXIF DateTimeDigitized", "Image DateTime"]
        datetime_objs = dict.fromkeys(tagIds)
        for tagId in tagIds:

            try:
                tagValue = tags[tagId]
            except:
                logger.debug(f"EXIF tag ID {tagId} invalid for {filename}")
                datetime_objs[tagId] = None
                continue

            try:
                # extract relevant part
                datetime_str = tagValue.values
                datetime_objs[tagId] = datetime.strptime(
                    datetime_str, "%Y:%m:%d %H:%M:%S"
                )
            except:
                logger.warning(
                    f"EXIF tag {tagId} string {datetime_str} not parsable in {filename}"
                )
                datetime_objs[tagId] = None
                continue

            logger.debug(f"EXIF tag {tagId} parsed to {datetime_objs} from {filename}")

        logger.debug(f"Extracted {datetime_objs} from {filename}")

        return datetime_objs

    def getFilenameTime(self, filename : str) -> datetime:
        ## Extract date and time from file name and return datetime object

        filenameWithoutPath = os.path.basename(filename)

        datePattern = "^.*?(\d{4})[-_ ]?(\d{2})[-_ ]?(\d{2}).*?"
        timePattern = "(\d{2})[-_: ]?(\d{2})[-_: ]?(\d{2})"
        datetimePattern = datePattern + "[-_ ]?" + timePattern

        # try full match at first
        reDateTime = re.match(datetimePattern, filenameWithoutPath)
        if reDateTime is not None:
            try:
                year = int(reDateTime.group(1))
                month = int(reDateTime.group(2))
                day = int(reDateTime.group(3))
                hour = int(reDateTime.group(4))
                minute = int(reDateTime.group(5))
                second = int(reDateTime.group(6))

                datetime_obj = datetime(
                    year=year,
                    month=month,
                    day=day,
                    hour=hour,
                    minute=minute,
                    second=second,
                )
            except Exception as e:
                logger.warning(f"Datetime creation of file {filename} (A) failed (extracted date would be {year}-{month}-{day} {hour}-{minute}-{second} (y-m-d h-m-s)) with {e}")
        else:
            # if not found everything, try day only
            reDate = re.match(datePattern, filenameWithoutPath)
            if reDate is not None:
                try:
                    year = int(reDate.group(1))
                    month = int(reDate.group(2))
                    day = int(reDate.group(3))
                    # set datetime to end of day for later minimum usage. Mark microsecond to maximum to revert
                    datetime_obj = datetime(
                        year=year,
                        month=month,
                        day=day,
                        hour=23,
                        minute=59,
                        second=59,
                        microsecond=999,
                    )
                except Exception as e:
                    logger.warning(f"Datetime creation of file {filename} (B) failed (extracted date would be {year}-{month}-{day} (y-m-d)) with {e}")
            else:
                logger.debug(
                    f"Neither datetime nor date pattern found in filename {filename}"
                )
                return None

        logger.debug(f"Filename date/time {datetime_obj} extracted from {filename}")
        return datetime_obj

    def getFileCreated(self, filename):
        ## Get file creation date and time and return datetime object
        creationTimestamp = os.stat(filename).st_ctime
        datetime_obj = datetime.fromtimestamp(creationTimestamp)
        logger.debug(f"File creation time {datetime_obj} found from {filename}")
        return datetime_obj
    

    def getFileHachoir(self, filename):
        """ Get hachcoir metadata for MOV files """
        try:
            parser = hachoir.parser.createParser(filename)
            metadata = hachoir.metadata.extractMetadata(parser)
            datetime_obj = metadata.get('creation_date')
        except Exception as e:
            logger.debug(f"Parsing of file {filename} failed with hachoir.")
            datetime_obj = None
        return datetime_obj

    def getFinalRenames(self):
        return self.__finalRenames
