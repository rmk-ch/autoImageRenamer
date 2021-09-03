
import os

import unittest

from imageRenamer import ImageRenamer


class TestSimple(unittest.TestCase):

    def test_add_one(self):
        self.assertEqual(add_one(5), 6)


if __name__ == '__main__':
    unittest.main()
def main():
    action = ImageRenamer.Action.testrun
    source = f"{os.getcwd()}/../examples"
    target = f"{os.getcwd()}/../out"
    x = ImageRenamer( source, target, action, True)