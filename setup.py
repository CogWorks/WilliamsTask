from setuptools import setup

APP = ['williams67.py']
DATA_FILES = ['freesans.ttf','cutouts.ttf']
OPTIONS = {
           'argv_emulation': True,
           'iconfile': 'eye.icns',
           }

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
