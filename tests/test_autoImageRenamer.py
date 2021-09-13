import unittest
import sys
import os

sys.path.append(os.path.abspath('../src/autoImageRenamer'))
from autoImageRenamer import autoImageRenamer


class Testing(unittest.TestCase):

    def test_predefinedDataset(self):
        # settings
        action = autoImageRenamer.AutoImageRenamer.Action.dryrun
        source = os.path.join(os.getcwd(), "tests", "testdata")
        target = os.path.join(os.getcwd(), "tests", "testdataout")
        interactive = False


        # run DUT
        ir = autoImageRenamer.AutoImageRenamer( source, target, action, interactive)
        actual = ir.getFinalRenames()

        # Set up expected
        mapping = dict()
        mapping["2021-01-12.jpg"]                     = "2021-01-12.jpg" # Date only, no EXIF
        mapping["20210605_153227.jpg"]                = "2021-06-05_15-32-27.jpg" # Samsung A51
        mapping["DSC07863.ARW"]                       = "2021-06-21_10-46-36.arw" # Sony RX100
        mapping["IMG_20210605_152957.jpeg"]           = "2021-06-05_15-29-57_001.jpeg" # Signal
        mapping["IMG_20210605_152957-0033.jpeg"]      = "2021-06-05_15-29-57_002.jpeg" # Copy of previous
        mapping["Photo-2021-06-21-10-17-40_8255.JPG"] = "2021-06-21_10-17-40.jpg" # iPhone
        mapping["Video-2021-06-22-10-12-58_8280.MOV"] = "2021-06-22_10-12-58.mov" # iPhone Video


        sourcePath_norm = os.path.normpath(source)
        targetPath_norm = os.path.normpath(target)

        expected = dict()
        for sourceFile, targetFile in mapping.items():
            key = os.path.join(sourcePath_norm, sourceFile)
            value = os.path.join(targetPath_norm, targetFile)
            expected[key] = value

        # Compare
        self.assertEqual(actual.keys(), expected.keys())
        for sourceFile, targetFile in expected.items():
            self.assertEqual(actual[sourceFile], targetFile)



    def test_emptyFolder_noException(self):
        source = os.path.join(os.getcwd(), "tests", "emptydirectory")
        target = source
        action = autoImageRenamer.AutoImageRenamer.Action.dryrun
        interactive = False

        # setup test directory
        try:
            os.rmdir(source)
        except:
            pass

        os.mkdir(source)

        ir = autoImageRenamer.AutoImageRenamer( source, target, action, interactive)

        os.rmdir(source)

if __name__ == '__main__':
    unittest.main()
