from PIL import Image
import exif
from exif import DATETIME_STR_FORMAT
from datetime import datetime, timedelta
import random


class FileCreator:
    def __init__(self, filename : str, tagDict : dict) -> None:
        self.__filename = filename
        self.__tagDict = tagDict
        self.createEmptyImage(filename)
        self.addExif(filename, tagDict)

    def createEmptyImage(self, filename : str):

        width = 10
        height = 10

        img  = Image.new( mode = "RGB", size = (width, height), color = (209, 123, 193) )
        #img.show()
        img.save(filename)

    def addExif(self, filename : str, tagDict : dict):
        img = exif.Image(filename)
        for key, value in tagDict.items():
            img.set(key, value.strftime(DATETIME_STR_FORMAT))
        
        with open(filename, 'wb') as new_image_file:
            new_image_file.write(img.get_file())

def getRandomDatetime(min_year=1900, max_year=datetime.now().year):
    # generate a datetime in format yyyy-mm-dd hh:mm:ss.000000
    # from https://gist.github.com/rg3915/db907d7455a4949dbe69
    start = datetime(min_year, 1, 1, 00, 00, 00)
    years = max_year - min_year + 1
    end = start + timedelta(days=365 * years)
    return start + (end - start) * random.random()