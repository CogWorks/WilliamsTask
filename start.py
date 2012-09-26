#!/usr/bin/env python

import argparse
from williams import *
import pycogworks.cwsubject as cwsubject

if __name__ == '__main__':

	parser = argparse.ArgumentParser( formatter_class = argparse.ArgumentDefaultsHelpFormatter )
	parser.add_argument( '-L', '--log', action = "store", dest = "logfile", help = 'Pipe results to file instead of stdout.' )
	parser.add_argument( '-F', '--fullscreen', action = "store_false", dest = "fullscreen", help = 'Disable fullscreen mode.' )
	parser.add_argument( '-r', '--replicates', action = "store", dest = "replicates", default = 20, type = int, help = 'Number of replicates.' )
	parser.add_argument( '-e', '--eyetracker', action = "store", dest = "eyetracker", default = '127.0.0.1', help = 'Use eyetracker.' )
	parser.add_argument( '-f', '--fixation', action = "store_true", dest = "showfixation", help = 'Overlay fixation.' )
	parser.add_argument( '-D', '--debug', action = "store", dest = "debug", default = 0, type = int, help = 'Debug level.' )
	parser.add_argument( '-d', '--logdir', action = "store", dest = "logdir", default = 'data', help = 'Log dir' )
	parser.add_argument( '-H', '--hint', action = "store_true", dest = "hint", help = 'Enable hint.' )
	parser.add_argument( '-S', '--subject', action = "store_true", dest = "subject", help = 'Get CogWorks subject info.' )

	args = parser.parse_args()

	subjectInfo = cwsubject.getSubjectInfo( minimal = True )
	if not subjectInfo:
		sys.exit()

	w = World( args, subjectInfo )
	w.run()