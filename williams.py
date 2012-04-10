#!/usr/bin/env python
"""
This is a modern implementation of the L.G. Williams' classic 1967 visual search task.
"""
import sys, random, math, time, pygame, gc, os
import argparse, platform
import numpy as np

from twisted.internet import reactor
from twisted.internet.task import LoopingCall

useEyetracker = True

try:
	from pyfixation import FixationProcessor
except ImportError:
	useEyetracker = False
try:
	from pyviewx import iViewXClient, Dispatcher
	from pyviewx.pygamesupport import Calibrator
except ImportError:
	useEyetracker = False

from collisionROI import testCollision
from savitzky_golay import savitzky_golay

os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'

gc.disable()
pygame.display.init()
pygame.font.init()

class VelocityFP( object ):

	def __init__( self, resolutionX = 1680, resolutionY = 1050, screenWidth = 473.8, screenHeight = 296.1, threshold = 20, blinkThreshold = 1000, minFix = 40 ):
		self.resolutionX = resolutionX
		self.resolutionY = resolutionY
		self.centerx = self.resolutionX / 2.0
		self.centery = self.resolutionY / 2.0
		self.screenWidth = screenWidth
		self.screenHeight = screenHeight
		self.threshold = threshold
		self.blinkThreshold = blinkThreshold
		self.minFix = minFix
		self.fix = None
		self.fixsamples = [[], []]
		self.prevsample = None

		self.winax = np.zeros( 11, dtype = float )
		self.winay = np.zeros( 11, dtype = float )
		self.winx = np.zeros( 11, dtype = float )
		self.winy = np.zeros( 11, dtype = float )
		self.d = None

	def degrees2pixels( self, a, d, resolutionX, resolutionY, screenWidth, screenHeight ):
		a = a * math.pi / 180
		w = 2 * math.tan( a / 2 ) * d
		aiph = resolutionX * w / screenWidth
		aipv = resolutionY * w / screenHeight
		return aiph, aipv

	def appendWindow( self, ax, ay, x, y ):
		self.winax = np.append( self.winax[1:], ax )
		self.winay = np.append( self.winay[1:], ay )
		self.winx = np.append( self.winx[1:], x )
		self.winy = np.append( self.winy[1:], y )

	def processWindow( self ):
		vx = savitzky_golay( self.winax, 21, 2, 1 )[6]
		vy = savitzky_golay( self.winay, 21, 2, 1 )[6]
		return 500.0 * math.sqrt( vx ** 2 + vy ** 2 ), self.winx[6], self.winy[6]

	def distance2point( self, x, y, vx, vy, vz, rx, ry, sw, sh ):
		dx = x / rx * sw - rx / 2.0 + vx
		dy = y / ry * sh - ry / 2.0 - vy
		sd = math.sqrt( dx ** 2 + dy ** 2 )
		return math.sqrt( vz ** 2 + sd ** 2 )

	def subtendedAngle( self, x1, y1, x2, y2, vx, vy, vz, rx, ry, sw, sh ):
		d1 = self.distance2point( x1, y1, vx, vy, vz, rx, ry, sw, sh )
		d2 = self.distance2point( x2, y2, vx, vy, vz, rx, ry, sw, sh )
		dX = sw * ( ( x2 - x1 ) / rx )
		dY = sh * ( ( y2 - y1 ) / ry )
		dS = math.sqrt( dX ** 2 + dY ** 2 )
		rad = math.acos( max( min( ( d1 ** 2 + d2 ** 2 - dS ** 2 ) / ( 2 * d1 * d2 ), 1 ), -1 ) )
		return ( rad / ( 2 * math.pi ) ) * 360

	def processData( self, t, x, y, ex, ey, ez ):
		ax = self.subtendedAngle( x, self.centery, self.centerx, self.centery, ex, ey, ez, self.resolutionX, self.resolutionY, self.screenWidth, self.screenHeight )
		ay = self.subtendedAngle( self.centerx, y, self.centerx, self.centery, ex, ey, ez, self.resolutionX, self.resolutionY, self.screenWidth, self.screenHeight )
		self.appendWindow( ax, ay, x, y )
		v, x, y = self.processWindow()
		if v == 0 or v > self.blinkThreshold:
			self.fixsamples = [[], []]
			self.fix = None
		else:
			if v < self.threshold:
				self.fixsamples[0].append( x )
				self.fixsamples[1].append( y )
				if len( self.fixsamples[0] ) >= self.minFix / 2:
					self.fix = ( np.mean( self.fixsamples[0] ), np.mean( self.fixsamples[1] ) )
				else:
					self.fix = None
			else:
				self.fixsamples = [[], []]
				self.fix = None
		"""
		if self.prevsample != None:
			dT = t - self.prevsample[0]
			dVA = self.subtendedAngle( x, y, self.prevsample[1][0], self.prevsample[1][1], ex, ey, ez, self.resolutionX, self.resolutionY, self.screenWidth, self.screenHeight )
			if dT == 0:
				self.fixsamples = [[], []]
				self.fix = None
			else:
				v = dVA / dT
				threshold = ( self.threshold * dT ) / 1000.0
				if v < threshold:
					self.fixsamples[0].append( x )
					self.fixsamples[1].append( y )
					self.fix = ( numpy.mean( self.fixsamples[0] ), numpy.mean( self.fixsamples[1] ) )
				else:
					self.fixsamples = [[], []]
					self.fix = None
		self.prevsample = ( t, ( x, y ) )
		"""


def radialPoint( p1, p2, r ):
	l = ( p2[0] - p1[0], p2[1] - p1[1] )
	z = math.sqrt( l[0] * l[0] + l[1] * l[1] )
	l = ( r * l[0] / z, r * l[1] / z )
	return ( p1[0] + l[0], p1[1] + l[1] )

class Shape( object ):
	"""Shape object"""

	def __init__( self, world, size, name, color, id, location ):
		self.shape = name
		self.color = color
		self.size = size
		self.id = id
		self.selected = False
		self.surface = world.fonts[size].render( world.shapes[name], True, world.colors[color] )
		self.surface = pygame.transform.rotate( self.surface, random.randint( 0, 360 ) )
		self.rect = self.surface.get_rect()
		self.rect.center = location
		self.brect = self.surface.get_bounding_rect()
		self.brect.center = location
		self.arect = self.rect.copy()
		self.arect.width -= ( self.arect.width - self.brect.width ) / 2
		self.arect.height -= ( self.arect.height - self.brect.height ) / 2
		self.arect.center = location
		self.id_t = world.fonts["id"].render( "%02d" % id, True, ( 0, 0, 0 ) )
		self.id_rect = self.id_t.get_rect()
		self.id_rect.centerx = location[0]
		self.id_rect.centery = location[1]

	def clickCheck( self, position ):
		return self.rect.collidepoint( position )


class Probe( object ):
	"""Probe objects"""

	def __init__( self, world, shape, cues = 0 ):
		self.id = shape.id
		self.shape = shape.shape
		self.size = shape.size
		self.color = shape.color
		self.elements = list()

		self.id_t = world.fonts["probe"].render( "%02d" % self.id, True, ( 0, 0, 0 ) )
		self.id_rect = self.id_t.get_rect()
		self.shape_t = world.fonts["probe"].render( self.shape, True, ( 0, 0, 0 ) )
		self.shape_rect = self.shape_t.get_rect()
		self.size_t = world.fonts["probe"].render( self.size, True, ( 0, 0, 0 ) )
		self.size_rect = self.size_t.get_rect()
		self.color_t = world.fonts["probe"].render( self.color, True, ( 0, 0, 0 ) )
		self.color_rect = self.color_t.get_rect()

		self.show_shape = 0
		self.show_size = 0
		self.show_color = 0

		color = shape = size = 0
		if cues == 0:
			shape = random.randint( 0, 1 )
			size = random.randint( 0, 1 )
			color = random.randint( 0, 1 )
		else:
			if cues == 1 or cues == 4 or cues == 5 or cues == 7:
				color = 1
			if cues == 2 or cues == 4 or cues == 6 or cues == 7:
				size = 1
			if cues == 3 or cues == 5 or cues == 6 or cues == 7:
				shape = 1

		if shape:
			self.show_shape = True
			self.elements.append( ( self.shape_t, self.shape_rect, 'shape' ) )
		if size:
			self.show_size = True
			self.elements.append( ( self.size_t, self.size_rect, 'size' ) )
		if color:
			self.show_color = True
			self.elements.append( ( self.color_t, self.color_rect , 'color' ) )

		random.shuffle( self.elements )
		for i in range( 0, len( self.elements ) ):
			if self.elements[i][2] == 'shape':
				self.show_shape = i + 1
			elif self.elements[i][2] == 'size':
				self.show_size = i + 1
			elif self.elements[i][2] == 'color':
				self.show_color = i + 1
		self.id_rect.centerx = world.worldsurf_rect.centerx
		self.shape_rect.centerx = world.worldsurf_rect.centerx
		self.size_rect.centerx = world.worldsurf_rect.centerx
		self.color_rect.centerx = world.worldsurf_rect.centerx

		elmlen = len( self.elements )
		if elmlen == 0:
			self.id_rect.centery = world.worldsurf_rect.centery
		elif elmlen == 1:
			self.id_rect.bottom = world.worldsurf_rect.centery - 1
			self.elements[0][1].top = world.worldsurf_rect.centery + 1
		elif elmlen == 2:
			self.elements[0][1].centery = world.worldsurf_rect.centery
			self.id_rect.bottom = self.elements[0][1].top - 1
			self.elements[1][1].top = self.elements[0][1].bottom + 1
		elif elmlen == 3:
			self.elements[0][1].bottom = world.worldsurf_rect.centery - 1
			self.id_rect.bottom = self.elements[0][1].top - 1
			self.elements[1][1].top = world.worldsurf_rect.centery + 1
			self.elements[2][1].top = self.elements[1][1].bottom + 1

class Color( tuple ):

	def __new__( self, h, s, v ):
		self.color = pygame.Color( 0, 0, 0, 0 )
		self.color.hsva = ( h, s, v, 0 )
		self.color.set_length( 3 )
		return tuple.__new__( Color, ( self.color.r, self.color.g, self.color.b ) )


class World( object ):
	"""Main game application"""

	if useEyetracker:
		d = Dispatcher()

	def __init__( self, args ):

		self.args = args

		if self.args.logfile:
			self.output = open( args.logfile, 'w' )
		else:
			self.output = sys.stdout

		self.trial = 1
		pygame.mouse.set_visible( False )

		# Remove modes that are double the width of another mode
		# which indicates a dual monitor resolution
		modes = pygame.display.list_modes()
		for mode in modes:
			tmp = mode[0] / 2
			for m in modes:
				if tmp == m[0]:
					modes.remove( mode )
					break

		if self.args.fullscreen:
			self.screen = pygame.display.set_mode( ( 0, 0 ), pygame.FULLSCREEN )
		else:
			self.screen = pygame.display.set_mode( modes[1], 0 )
		self.worldsurf = self.screen.copy()
		self.worldsurf_rect = self.worldsurf.get_rect()
		self.search_rect = self.worldsurf_rect.copy()
		self.search_rect.height = int( self.search_rect.height )
		self.search_rect.width = self.search_rect.height
		self.search_rect.center = self.worldsurf_rect.center
		self.xoffset = ( self.worldsurf_rect.width - self.search_rect.width ) / 2

		self.side = 11
		self.query_cell = math.ceil( self.side * self.side / 2 )
		self.cell_side = self.worldsurf_rect.height / self.side
		self.probe_rect = pygame.Rect( 0, 0, self.cell_side + 2, self.cell_side + 2 )
		self.probe_rect.center = self.worldsurf_rect.center

		self.probeCues = None
		self.hint = False

		self.color_fixations = 0
		self.size_fixations = 0
		self.shape_fixations = 0
		self.fixations = 0
		self.curFixDuration = 0

		self.modifier = pygame.KMOD_CTRL
		if platform.system() == 'Darwin':
			self.modifier = pygame.KMOD_META

		self.score_font = pygame.font.Font( "freesans.ttf", self.cell_side / 3 )
		self.help_font = pygame.font.Font( "freesans.ttf", self.cell_side / 3 )

		self.title_font = pygame.font.Font( "freesans.ttf", self.worldsurf_rect.height / 10 )

		self.objects = None

		self.fonts = {
					  "large": pygame.font.Font( "cutouts.ttf", int( self.cell_side * 1.25 ) ),
					  "medium": pygame.font.Font( "cutouts.ttf", int( self.cell_side * .95 ) ),
					  "small": pygame.font.Font( "cutouts.ttf", int( self.cell_side * .65 ) ),
					  "id": pygame.font.Font( "freesans.ttf", self.cell_side / 7 ),
					  "probe": pygame.font.Font( "freesans.ttf", self.cell_side / 6 )
					  }
		self.shapes = {
					   "circle":"E",
					   "square":"K",
					   "oval":"F",
					   "diamond":"T",
					   "crescent":"Q",
					   "cross":"Y",
					   "star":"C",
					   "triangle":"A"
					   }
		s = 50
		v = 100
		self.colors = {
					   "red": Color( 0, s, v ),
					   "yellow": Color( 72, s, v ),
					   "green": Color( 144, s, v ),
					   "blue": Color( 216, s, v ),
					   "purple": Color( 288, s, v )
					   }
		self.exp_shapes = ["star", "cross", "crescent", "diamond", "oval"]
		self.exp_colors = ["red", "yellow", "green", "blue", "purple"]
		self.exp_sizes = ["large", "medium", "small"]

		self.nobjects = len( self.exp_colors ) * len( self.exp_shapes ) * len( self.exp_sizes )

		self.bgcolor = ( 32, 32, 32 )
		self.searchBG = ( 168, 168, 168 )

		self.probes = True
		if not self.args.random:
			self.probes = random.sample( [1, 2, 3, 4, 5, 6, 7, 8] * 25, 200 )

		self.regen = False

		self.fix_data = None
		if self.args.eyetracker:
			self.client = iViewXClient( self.args.eyetracker, 4444 )
			self.client.addDispatcher( self.d )
			#self.fp = FixationProcessor( 3.55, sample_rate = 500 )
			self.fp = VelocityFP()
			self.calibrator = Calibrator( self.client, self.screen, reactor = reactor )

		self.logo = pygame.image.load( "logo.png" )

	def setup( self, bounds = None, max = None, avoid = None ):

		if bounds is None:
			bounds = self.search_rect

		if avoid is None:
			avoid = [self.probe_rect]

		self.objects = list()
		ids = random.sample( range( 0, self.nobjects ), self.nobjects )
		objs = list()
		for i in range( 0, len( self.exp_sizes ) ):
			for j in range( 0, len( self.exp_shapes ) ):
				for k in range( 0, len( self.exp_colors ) ):
					objs.append( ( self.exp_sizes[i], self.exp_shapes[j], self.exp_colors[k] ) )
		random.shuffle( objs )

		tries = 1
		for obj in objs:
			id = ids.pop()
			s = Shape( self, obj[0], obj[1], obj[2], id, ( random.randrange( bounds.left, bounds.right, 1 ), random.randrange( bounds.top, bounds.bottom, 1 ) ) )
			cont = True
			while cont:
				new = False
				if not bounds.contains( s.arect ):
					new = True
				else:
					for a in avoid:
						if s.arect.colliderect( a ):
							new = True
							break
					if not new:
						for o in self.objects:
							if s.arect.colliderect( o.arect ):
								new = True
								break
				if new:
					s = Shape( self, obj[0], obj[1], obj[2], id, ( random.randrange( bounds.left, bounds.right, 1 ), random.randrange( bounds.top, bounds.bottom, 1 ) ) )
					tries += 1
				else:
					cont = False
			self.objects.append( s )
			if not max is None:
				if len( self.objects ) == max:
					break

		if self.args.debug:
			print "~~ Generating trial took %d tries" % tries

		if self.state > -1 and not self.regen:
			self.probeCues = self.probes.pop()
		if self.probeCues:
			self.probe = Probe( self, self.objects[random.randint( 0, len( self.objects ) - 1 )], self.probeCues )

	def drawSearchBG( self ):
		pygame.draw.rect( self.worldsurf, self.searchBG, self.search_rect )

	def drawProbe( self ):
		self.drawSearchBG()
		self.worldsurf.blit( self.probe.id_t, self.probe.id_rect )
		for pelm in self.probe.elements:
			self.worldsurf.blit( pelm[0], pelm[1] )
		pygame.draw.rect( self.worldsurf, ( 96, 96, 96 ), self.probe_rect, 1 )

	def getVertices( self, r ):
		return ( r.topleft, r.topright, r.bottomright, r.bottomleft )

	def drawShapes( self ):
		self.drawProbe()
		for i in range( 0, len( self.objects ) ):
			self.objects[i].selected = False
			self.worldsurf.blit( self.objects[i].surface, self.objects[i].rect )
			self.worldsurf.blit( self.objects[i].id_t, self.objects[i].id_rect )
			if self.args.debug > 1:
				pygame.draw.rect( self.worldsurf, ( 128, 128, 255 ), self.objects[i].arect, 1 )
			if self.args.hint and self.hint and self.objects[i].id == self.probe.id:
				pygame.draw.rect( self.worldsurf, ( 128, 255, 128 ), self.objects[i].arect, 3 )
			if self.args.eyetracker and self.fp.fix and testCollision( self.getVertices( self.objects[i].brect ), ( self.fp.fix[0], self.fp.fix[1] ), 23 ):
				self.objects[i].selected = True
				pygame.draw.rect( self.worldsurf, ( 200, 200, 200 ), self.objects[i].arect, 1 )

	def drawSearchTime( self ):
		self.draw_text( "Found target in %.2f seconds." % self.search_time, self.score_font, ( 255, 255, 0 ), self.worldsurf_rect.center )

	def draw_text( self, text, font, color, loc ):
		t = font.render( text, True, color )
		tr = t.get_rect()
		tr.center = loc
		self.worldsurf.blit( t, tr )
		return tr

	def dropShadow( self, text, font, fg, bg, loc, xoff = 3, yoff = 3 ):
		t1 = self.draw_text( text, font, bg, ( loc[0] + xoff, loc[1] + yoff ) )
		t2 = self.draw_text( text, font, fg, loc )
		return t1.union( t2 )

	def drawHelp( self ):
		title_rect = self.dropShadow( 'Williams Search Task', self.title_font, ( 36, 168, 36 ), ( 255, 255, 255 ), ( self.worldsurf_rect.centerx, self.worldsurf_rect.height / 5 ) )
		logo_rect = self.logo.get_rect()
		logo_rect.centerx = self.worldsurf_rect.centerx
		logo_rect.centery = self.worldsurf_rect.height / 5 * 2
		self.worldsurf.blit( self.logo, logo_rect )
		if not self.objects:
			self.setup( bounds = self.worldsurf_rect, avoid = ( title_rect, logo_rect ) )
		for i in range( 0, len( self.objects ) ):
			self.worldsurf.blit( self.objects[i].surface, self.objects[i].rect )

	def clear( self ):
		self.worldsurf.fill( self.bgcolor )

	def updateWorld( self ):
		self.screen.blit( self.worldsurf, self.worldsurf_rect )
		pygame.display.flip()

	def processEvents( self ):
		for event in pygame.event.get():
			if event.type == pygame.KEYUP:
				if ( pygame.key.get_mods() & self.modifier ):
					if event.key == pygame.K_h and self.args.hint:
						self.hint = False
				elif not ( pygame.key.get_mods() & self.modifier ):
					self.hint = False
			elif event.type == pygame.KEYDOWN:
				if ( pygame.key.get_mods() & self.modifier ):
					if event.key == pygame.K_q:
						self.cleanup()
					elif event.key == pygame.K_r and self.args.debug:
						if self.state == 3:
							self.regen = True
							self.state = 0
					elif event.key == pygame.K_h and self.args.hint:
						self.hint = True
				elif event.key == pygame.K_SPACE:
					if self.state == -1 or self.state == 1:
						self.state += 1
					elif self.state == 5:
						self.state = 0
					elif self.state == 3:
						self.search_time = time.time() - self.start_time
						for object in self.objects:
							if object.selected and object.id == self.probe.id:
								self.state = 4
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if self.state == -1 or self.state == 1:
					self.state += 1
				elif self.state == 5:
					self.state = 0
				elif self.state == 3:
					self.search_time = time.time() - self.start_time
					for object in self.objects:
						mousex, mousey = event.pos
						if object.clickCheck( ( mousex, mousey ) ):
							if object.id == self.probe.id:
								self.state = 4

	def processResults( self ):
		result = [
					self.trial, self.probe.id, self.probe.size, self.probe.color, self.probe.shape, \
					self.probe.show_size, self.probe.show_color, self.probe.show_shape, "%.2f" % self.search_time, \
					self.size_fixations, self.color_fixations, self.shape_fixations, self.fixations
				]
		self.output.write( '%s\n' % '\t'.join( map( str, result ) ) )

	def draw_fix( self ):
		"""
		if self.fix_data:
			pygame.draw.circle( self.worldsurf, ( 0, 228, 0 ), ( int( self.fix_data.fix_x ), int( self.fix_data.fix_y ) ), int( self.fp.gaze_deviation_thresh_px ), 1 )
		"""
		#if self.fp:
		#	for i in range( 0, len( self.fp.winx ) ):
		#		pygame.draw.circle( self.worldsurf, ( 228, 0, 0 ), ( int( self.fp.winx[i] ), int( self.fp.winy[i] ) ), 2, 0 )
		if self.fp.fix:
			pygame.draw.circle( self.worldsurf, ( 0, 228, 0 ), ( int( self.fp.fix[0] ), int( self.fp.fix[1] ) ), 23, 1 )

	def refresh( self ):
		self.clear()
		if self.state == -1:
			self.drawHelp()
		elif self.state == 0:
			self.bgcolor = ( 0, 0, 0 )
			self.setup()
			if self.regen:
				self.state = 2
			else:
				self.state = 1
			self.color_fixations = 0
			self.size_fixations = 0
			self.shape_fixations = 0
			self.fixations = 0
		elif self.state == 1:
			self.drawProbe()
		elif self.state == 2:
			if not self.args.eyetracker:
				pygame.mouse.set_pos( self.worldsurf_rect.centerx, self.worldsurf_rect.centery )
				pygame.mouse.set_visible( True )
			self.end_time = 0
			self.start_time = time.time()
			self.state = 3
		elif self.state == 3:
			self.drawShapes()
		elif self.state == 4:
			pygame.mouse.set_visible( False )
			self.processResults()
			self.trial = self.trial + 1
			self.regen = False
			self.state = 5
		elif self.state == 5:
			self.drawSearchTime()
		if self.args.eyetracker and self.args.showfixation:
			self.draw_fix()
		self.updateWorld()
		self.processEvents()

	def cleanup( self, *args, **kwargs ):
		if self.args.logfile:
			self.output.close()
		reactor.stop()

	def start( self, lc ):
		self.state = -1
		self.lc = LoopingCall( self.refresh )
		d = self.lc.start( 1.0 / 30 )
		d.addCallbacks( self.cleanup )

	def run( self ):
		self.state = -2
		if self.args.eyetracker:
			reactor.listenUDP( 5555, self.client )
			self.calibrator.start( self.start )
		else:
			self.start( None )
		reactor.run()

	if useEyetracker:
		@d.listen( 'ET_SPL' )
		def iViewXEvent( self, inSender, inEvent, inResponse ):
			if self.state < 0:
				return
			"""t = int( inResponse[0] )
			x = float( inResponse[2] )
			y = float( inResponse[4] )
			ex = np.mean( ( float( inResponse[10] ), float( inResponse[11] ) ) )
			ey = np.mean( ( float( inResponse[12] ), float( inResponse[13] ) ) )
			ez = np.mean( ( float( inResponse[14] ), float( inResponse[15] ) ) )"""
			#print t, x, y, ex, ey, ez
			self.fp.processData( inResponse )
			"""
			if self.state < 0:
				return
			self.fix_data = tmp = self.fp.detect_fixation( int( float( inResponse[4] ) ) > 0, float( inResponse[2] ), float( inResponse[4] ) )
			if self.state == 3 and self.fix_data.fix_duration < self.curFixDuration:
				self.fixations += 1
				for i in range( 0, len( self.objects ) ):
					if self.objects[i].arect.collidepoint( radialPoint( ( tmp.fix_x, tmp.fix_y ), self.objects[i].arect.center, self.fp.gaze_deviation_thresh_px ) ):
						if self.objects[i].color == self.probe.color:
							self.color_fixations += 1
						if self.objects[i].shape == self.probe.shape:
							self.shape_fixations += 1
						if self.objects[i].size == self.probe.size:
							self.size_fixations += 1
			self.curFixDuration = self.fix_data.fix_duration
			"""

if __name__ == '__main__':

	parser = argparse.ArgumentParser( formatter_class = argparse.ArgumentDefaultsHelpFormatter )
	parser.add_argument( '-L', '--log', action = "store", dest = "logfile", help = 'Pipe results to file instead of stdout.' )
	parser.add_argument( '-F', '--fullscreen', action = "store_true", dest = "fullscreen", help = 'Run in fullscreen mode.' )
	parser.add_argument( '-R', '--random', action = "store_true", dest = "random", help = 'Run random trials indefinitely.' )
	if useEyetracker:
		parser.add_argument( '-e', '--eyetracker', action = "store", dest = "eyetracker", help = 'Use eyetracker.' )
		parser.add_argument( '-f', '--fixation', action = "store_true", dest = "showfixation", help = 'Overlay fixation.' )
	parser.add_argument( '-D', '--debug', action = "store", dest = "debug", default = 0, type = int, help = 'Debug level.' )
	parser.add_argument( '-H', '--hint', action = "store_true", dest = "hint", help = 'Enable hint.' )

	args = parser.parse_args()
	if not useEyetracker:
		setattr( args, 'eyetracker', False )

	w = World( args )
	w.run()
