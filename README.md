# AutoImageRenamer
## Motivation and Principle
Have you ever moved images from multiple sources (devices, people, ...) into the same folder? Usually, this is a terrible mess in terms of filenames. If you open one file in most image viewers, navigating through the images drives me crazy.

The AutoImageRenamer solves this issue by reading all image and video file and tries to automatically extract the date and time where it has been taken. It parses the filename for date and time patterns as well as reading embedded EXIF metadata. As a last resort it could also take the filesystems creation date. It then takes the _oldest_ datetime found and renames the files in a computer-sortable manner, i.e. YYYY-MM-DD_HH-mm-ss and unifies extensions to lowercase.
An interactive mode allows checking the proposed changes before any actions are taken.

## Continuous Integration
[![Run Python Tests](https://github.com/rmk-ch/autoImageRenamer/actions/workflows/ci.yml/badge.svg)](https://github.com/rmk-ch/autoImageRenamer/actions/workflows/ci.yml)


## Installation
Requires Python installation, version 3.9 is tested. Python must be in $PATH.
Installation with PowerShell (clones git repository, goes to repository, installs poetry, installs autoImageRenamer):
```
$ git clone https://github.com/rmk-ch/autoImageRenamer.git
$ Set-Location autoImageRenamer.git
$ (Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -
$ poetry install
```

Set environment variable AUTO_IMAGE_RENAMER_PATH to the path where the repository is checked out.
Copy autoImageRenamer.ps1 to where you need it and adapt any calls as you like.

## Usage
In PowerShell:
```
$ Set-Location $env:AUTO_IMAGE_RENAMER_PATH
$ poetry run autoImageRenamer --help
```

## Author
Roman Koller, https://roman-koller.ch

