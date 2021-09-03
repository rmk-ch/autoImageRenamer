# pylint: disable=line-too-long

"""AutoImageRenamer"""

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup

import pathlib

def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as fh:
        return fh.read()

setup(
    name='AutoImageRenamer',
    description=__doc__,
    author="Roman Koller",
    author_email="github@roman-koller.ch",
    url="https://dev.roman-koller.ch",
    install_requires=[
        'loguru',
        'docopt',
        'ExifRead'
    ],
    extras_require={
        'dev_tools': [
            'astroid==2.5.6',
            'flake8==3.9.1',
            'flake8-2020==1.6.0',
            'flake8-annotations==2.6.2',
            'flake8-blind-except==0.2.0',
            'flake8-bugbear==21.4.3',
            'flake8-builtins==1.5.3',
            'flake8-comprehensions==3.4.0',
            'flake8-docstrings==1.6.0',
            'flake8-mutable==1.2.0',
            'flake8-pie==0.8.0',
            'flake8-print==4.0.0',
            'flake8-printf-formatting==1.1.2',
            'flake8-pytest==1.3',
            'flake8-quotes==3.2.0',
            'flake8-rst-docstrings==0.2.1',
            'flake8-simplify==0.14.0',
            'flake8-spellcheck==0.24.0',
            'flake8-string-format==0.3.0',
            'flake8-todos==0.1.5',
            'pip==21.1',
            'pydocstyle==6.0.0',
            'pylint==2.8.2',
            'pytest==6.2.3',
            'pytest-cov==2.11.1',
            'pytest-custom-exit-code==0.3.0',
            'pytest-repeat==0.9.1',
            'setuptools==56.0.0',
            'wheel==0.36.2'
        ],
    },
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.9',
    version='1.0.0',
    #entry_points={
    #    'console_scripts': [
    #        'imageRenamer:imageRenamer.main',
    #    ]
    #},
)
