from setuptools import setup

APP = ['src/williams.py']
DATA_FILES = ['src/resources']
PLIST = {'CFBundleIdentifier': 'edu.rpi.cogsci.cogworks.williams'}
OPTIONS = {'argv_emulation': True,
           'iconfile': 'src/resources/logo.icns',
            'plist': PLIST}

setup(
    app=APP,
    name="Williams' Search Task",
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
