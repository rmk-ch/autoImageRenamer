import unittest
import sys
import os
from pathlib import Path
import shutil

sys.path.append(os.path.abspath('./src'))
from autoImageRenamer import autoImageRenamer


class Test_ArtificialDatasets(unittest.TestCase):

    def setUp(self):
        # settings
        self.__source = os.path.join(os.getcwd(), "tests", "artificialDataset")
        self.__target = self.__source
        self.__action = autoImageRenamer.AutoImageRenamer.Action.dryrun
        self.__interactive = False

        # setup test directory
        try:
            shutil.rmtree(self.__source)
        except:
            pass

        os.mkdir(self.__source)

    def tearDown(self) -> None:
        try:
            shutil.rmtree(self.__source)
        except:
            pass
        return super().tearDown()
        

    def test_fromFilenameOnly(self):
        # create some files
        mapping = dict()
        mapping["20000930-153429-98.jpg"] = "2000-09-30_15-34-29.jpg"
        mapping["2000 09 30 15 34 55.jpg"] = "2000-09-30_15-34-55.jpg"
        mapping["2000-09-30_15-34-52-11.JPG"] = "2000-09-30_15-34-52.jpg"
        mapping["2000-09-30.arw"] = "2000-09-30.arw"


        for old in mapping.keys():
            # create empty files
            Path(os.path.join(self.__source, old)).touch()


        # run DUT
        ir = autoImageRenamer.AutoImageRenamer( self.__source, self.__target, self.__action, self.__interactive)
        actual = ir.getFinalRenames()


        sourcePath_norm = os.path.normpath(self.__source)
        targetPath_norm = os.path.normpath(self.__target)

        expected = dict()
        for sourceFile, targetFile in mapping.items():
            key = os.path.join(sourcePath_norm, sourceFile)
            value = os.path.join(targetPath_norm, targetFile)
            expected[key] = value

        # Compare
        self.assertEqual(actual.keys(), expected.keys())
        for sourceFile, targetFile in expected.items():
            self.assertEqual(actual[sourceFile], targetFile)

    @unittest.skip("to be implemented")
    def test_fromExif(self):
        # create some files
        mapping = dict()
        mapping["somefile.jpg"] = "2002-01-10_00-01-02.jpg"


        for old in mapping.keys():
            # create empty files
            Path(os.path.join(self.__source, old)).touch()


        # run DUT
        ir = autoImageRenamer.AutoImageRenamer( self.__source, self.__target, self.__action, self.__interactive)
        actual = ir.getFinalRenames()


        sourcePath_norm = os.path.normpath(self.__source)
        targetPath_norm = os.path.normpath(self.__target)

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
        ir = autoImageRenamer.AutoImageRenamer( self.__source, self.__target, self.__action, self.__interactive)


if __name__ == '__main__':
    unittest.main()
