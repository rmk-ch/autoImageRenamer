import unittest
import sys
import os
from pathlib import Path
import shutil

sys.path.append(os.path.abspath("./tests"))
import TestHelpers

sys.path.append(os.path.abspath("./src"))
from autoImageRenamer import autoImageRenamer


class Test_ArtificialDatasets(unittest.TestCase):
    def setUp(self):
        # settings
        self.__source = os.path.join(os.getcwd(), "tests", "tempIn")
        self.__target = os.path.join(os.getcwd(), "tests", "tempOut")
        self.__action = autoImageRenamer.AutoImageRenamer.Action.dryrun
        self.__interactive = False
        self.__append = False

        self.__DATE_FORMAT = "%Y-%m-%d"
        self.__DATETIME_FORMAT = f"{self.__DATE_FORMAT}_%H-%M-%S"

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
        mapping = dict()  # @TODO: Make this random similar to exif testcase
        mapping["20000930-153429-98.jpg"] = "2000-09-30_15-34-29.jpg"
        mapping["2000 09 30 15 34 55.jpg"] = "2000-09-30_15-34-55.jpg"
        mapping["1940 01 02 01 02 03.jpg"] = "1940-01-02_01-02-03.jpg"
        mapping[
            "Photo-2021-06-21-10-17-40_8255.JPG"
        ] = "2021-06-21_10-17-40.jpg"  # iPhone
        mapping["2000-09-30.arw"] = "2000-09-30.arw"
        mapping[
            "Video-2021-06-22-10-12-58_8280.MOV"
        ] = "2021-06-22_10-12-58.mov"  # iPhone Video

        for old in mapping.keys():
            # create empty files
            Path(os.path.join(self.__source, old)).touch()

        # run DUT
        ir = autoImageRenamer.AutoImageRenamer(
            self.__source, self.__target, self.__action, self.__interactive, self.__append
        )
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

    def test_fromExif(self):
        # create datetime objects and files randomly
        nFiles = 50
        tagIds = ["datetime_original", "datetime_digitized", "datetime"]
        dtime = dict()
        mapping = dict()

        for f in range(0, nFiles):
            filename = f"f{f}.jpg"
            dtime = TestHelpers.getRandomDatetime(1900)
            mapping[filename] = dtime.strftime(self.__DATETIME_FORMAT) + ".jpg"
            tagDict = dict()
            tagDict[tagIds[f % len(tagIds)]] = dtime
            TestHelpers.FileCreator(os.path.join(self.__source, filename), tagDict)

        # run DUT
        ir = autoImageRenamer.AutoImageRenamer(
            self.__source, self.__target, self.__action, self.__interactive, self.__append
        )
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

    def test_duplicates(self):
        # create a few files with same content and some with different content
        dtime = TestHelpers.getRandomDatetime(1900)
        mapping = dict()
        colors = [(1, 2, 3), (2, 3, 4), (4, 5, 255), (1, 2, 3)]
        # isContentDuplicate = [True, False, False, False]
        # duplicateIndicator = [0,1,2,3]
        isContentDuplicate = [False, False, False, True]
        duplicateIndicator = [1, 2, 3, 0]

        someDateTimeStr = dtime.strftime("%Y%m%d_%H%M%S")
        targetDateTimeStr = dtime.strftime(self.__DATETIME_FORMAT)
        for f in range(0, len(colors)):
            filename = f"{someDateTimeStr}_{f}.jpg"
            if isContentDuplicate[f]:
                mapping[filename] = f"DUPLICATE_{filename}"
            else:
                mapping[
                    filename
                ] = f"{targetDateTimeStr}_{duplicateIndicator[f]:0>3}.jpg"
            tagDict = dict()
            TestHelpers.FileCreator(
                os.path.join(self.__source, filename), tagDict, colors[f]
            )

        # run DUT
        ir = autoImageRenamer.AutoImageRenamer(
            self.__source, self.__target, self.__action, self.__interactive, self.__append
        )
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

    def test_exitAndFilename_exifIsOldest(self):
        dtime = dict()
        dtime[0] = TestHelpers.getRandomDatetime(1900)
        dtime[1] = TestHelpers.getRandomDatetime(1900)
        if dtime[0] > dtime[1]:
            dtime_older = dtime[1]
            dtime_newer = dtime[0]
        else:
            dtime_older = dtime[0]
            dtime_newer = dtime[1]

        mapping = dict()
        mapping[
            f"{dtime_newer.strftime(self.__DATETIME_FORMAT)}.jpg"
        ] = f"{dtime_older.strftime(self.__DATETIME_FORMAT)}.jpg"

        for old in mapping.keys():
            tagDict = dict()
            tagDict["datetime_original"] = dtime_older
            TestHelpers.FileCreator(os.path.join(self.__source, old), tagDict)

        # run DUT
        ir = autoImageRenamer.AutoImageRenamer(
            self.__source, self.__target, self.__action, self.__interactive, self.__append
        )
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

    def test_exitAndFilename_filenameIsOldest(self):
        dtime = dict()
        dtime[0] = TestHelpers.getRandomDatetime(1900)
        dtime[1] = TestHelpers.getRandomDatetime(1900)
        if dtime[0] > dtime[1]:
            dtime_older = dtime[1]
            dtime_newer = dtime[0]
        else:
            dtime_older = dtime[0]
            dtime_newer = dtime[1]

        mapping = dict()
        mapping[
            f"{dtime_older.strftime(self.__DATETIME_FORMAT)}.jpg"
        ] = f"{dtime_older.strftime(self.__DATETIME_FORMAT)}.jpg"

        for old in mapping.keys():
            tagDict = dict()
            tagDict["datetime_original"] = dtime_newer
            TestHelpers.FileCreator(os.path.join(self.__source, old), tagDict)

        # run DUT
        ir = autoImageRenamer.AutoImageRenamer(
            self.__source, self.__target, self.__action, self.__interactive, self.__append
        )
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
        ir = autoImageRenamer.AutoImageRenamer(
            self.__source, self.__target, self.__action, self.__interactive, self.__append
        )


    @unittest.skip("Found no way to create an artificial MOV file similar to the one created by new IPHONES.... Tested with private dataset")
    def test_mov(self):
        assert(False)



if __name__ == "__main__":
    unittest.main()
