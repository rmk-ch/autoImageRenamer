# AutoImageRenamer
## Motivation and Principle
Have you ever moved images from multiple sources (devices, people, ...) into the same folder? Usually, this is a terrible mess in terms of filenames. If you open one file in most image viewers, navigating through the images drives me crazy.

The AutoImageRenamer solves this issue by reading all image and video file and tries to automatically extract the date and time where it has been taken. It parses the filename for date and time patterns as well as reading embedded EXIF metadata. As a last resort it could also take the filesystems creation date. It then takes the _oldest_ datetime found and renames the files in a computer-sortable manner, i.e. YYYY-MM-DD_HH-mm-ss and unifies extensions to lowercase.
An interactive mode allows checking the proposed changes before any actions are taken.

## Continuous Integration
[![Run Python Tests](https://github.com/rmk-ch/autoImageRenamer/actions/workflows/ci.yml/badge.svg)](https://github.com/rmk-ch/autoImageRenamer/actions/workflows/ci.yml)


## Usage
Requires Python installation, version 3.9 is tested. Python must be in $PATH.
Install from PowerShell terminal
```
$ git clone https://github.com/rmk-ch/autoImageRenamer.git
$ cd autoImageRenamer.git
$ python -m venv venv
$ .\venv\Scripts\Activate.ps1
$ pip install -r requirements.txt
```
See autoImageRenamer.ps1, call with --help for detailed usage.

## Author
Roman Koller, https://roman-koller.ch

## Notes
According to https://blog.ionelmc.ro/2014/05/25/python-packaging/

