from setuptools import setup
import os.path

descr_file = os.path.join(os.path.dirname(__file__), 'README')

APP = ['williams/__main__.py']
DATA_FILES = ['williams/resources']
PLIST = {
         'CFBundleIdentifier': 'edu.rpi.cogsci.cogworks.williams'
         }
OPTIONS = {
           'argv_emulation': True,
           'iconfile': 'williams/resources/logo.icns',
           'plist': PLIST,
           'site_packages': True
           }

setup(
      app=APP,
      name="Williams' Search Task",
      version="0.99.0",
      author="Ryan M. Hope",
      packages=["williams"],
      description="A modern implementation of L.G. Williams' classic 1967 visual search task.",
      long_description=open(descr_file).read(),
      author_email="rmh3093@gmail.com",
      license='GPL-3',
      data_files=DATA_FILES,
      options={'py2app': OPTIONS},
      setup_requires=['py2app'],
      install_requires=[
                        'pyglet >= 1.2alpha1',
                        'cocos2d', 'twisted'
                        ],
      url='https://github.com/CogWorks/WilliamsTask',
      classifiers=[
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Framework :: Twisted',
                   'Programming Language :: Python :: 2',
                   'Topic :: Games/Entertainment'
                   ],
      entry_points={
                    'console_scripts': [
                                        'WilliamsSearchTask = williams.main:main'
                                        ]
                    }
)
