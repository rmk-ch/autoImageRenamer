"""AutoImageRenamer:
Automatic image and video renaming targeting a filename with the date and time of the image taken.
The strategy is first to figure out the date and time from filename, exif data and file creation date and 
subsequently selecting the oldest of these datetimes. The file mode is then either to rename or copy the file
from A to B.

Usage:
    autoImageRenamer.py rename [<source>] [<target>] [-i] [-l [<logfile>]]
    autoImageRenamer.py copy [<source>] [<target>] [-i] [-l [<logfile>]]
    autoImageRenamer.py dryrun [<source>] [<target>] [-i] [-l [<logfile>]]

Options:
    <source>            Source directory [default: .]
    <target>            Target directory [default: <source>]
    -i --interactive    Ask for confirmation before action
    -l --logfile        Target logfile [default: ./autoImageRenamer.log]
"""

import os
import sys
from docopt import docopt
from loguru import logger

from . import AutoImageRenamer

def main():
    arguments = docopt(__doc__, version='1.0.0')

    if arguments['<source>'] is None:
        arguments['<source>'] = os.getcwd()

    if arguments['<target>'] is None:
        arguments['<target>'] = arguments['<source>']

    if arguments['copy']:
        action = AutoImageRenamer.Action.copy
    elif arguments['rename']:
        action = AutoImageRenamer.Action.rename
    elif arguments['dryrun']:
        action = AutoImageRenamer.Action.dryrun

    logger.remove(None)
    logger.add(sys.stdout, level="INFO")
    if arguments['--logfile']:
        if arguments['<logfile>'] is None:
            logfile = "autoImageRenamer.log"
        else:
            logfile = arguments['<logfile>']
        logger.add(logfile, level="DEBUG")


    x = AutoImageRenamer( arguments['<source>'], arguments['<target>'], action, arguments['--interactive'])

if __name__ == '__main__':
    main()