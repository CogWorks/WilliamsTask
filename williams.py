#!/usr/bin/env python
"""
This is a replicate of the classic Williams '67 visual search task with some
minor alterations.
"""
import sys, random, math, time, pygame, gc
import argparse, platform

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from pycogworks.fixation import FixationProcessor
sys.path.append( "PyViewX" )
from pyviewx import iViewXClient, Dispatcher
from pyviewx.pygamesupport import Calibrator

gc.disable()
pygame.display.init()
pygame.font.init()

def distance( p1, p2 ):
	math.sqrt( ( p2[0] - p1[0] ) * ( p2[0] - p1[0] ) + ( p2[1] - p1[1] ) * ( p2[1] - p1[1] ) )

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

		self.show_shape = None
		self.show_size = None
		self.show_color = None

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
			self.show_shape = self.shape
			self.elements.append( ( self.shape_t, self.shape_rect ) )
		if size:
			self.show_size = self.size
			self.elements.append( ( self.size_t, self.size_rect ) )
		if color:
			self.show_color = self.color
			self.elements.append( ( self.color_t, self.color_rect ) )

		random.shuffle( self.elements )

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

class Color( object ):

	def __init__( self, h, s, v ):
		self.color = pygame.Color( 0, 0, 0, 0 )
		self.color.hsva = ( h, s, v, 0 )
		self.color.set_length( 3 )

	def rgb( self ):
		return ( self.color.r, self.color.g, self.color.b )

	def __repr__( self ):
		return str( self.rgb() )


class World( object ):
	"""Main game application"""

	d = Dispatcher()

	def __init__( self, args ):

		self.args = args

		if self.args.logfile:
			self.output = open( args.logfile, 'w' )
		else:
			self.output = sys.stdout

		self.trial = 1
		pygame.mouse.set_visible( False )
		if self.args.fullscreen:
			self.screen = pygame.display.set_mode( ( 0, 0 ), pygame.FULLSCREEN )
		else:
			self.screen = pygame.display.set_mode( ( 1024, 768 ), 0 )
		self.worldsurf = self.screen.copy()
		self.worldsurf_rect = self.worldsurf.get_rect()
		self.search_rect = self.worldsurf_rect.copy()
		self.search_rect.width = self.search_rect.height
		self.search_rect.centerx = self.worldsurf_rect.centerx
		self.xoffset = ( self.worldsurf_rect.width - self.search_rect.width ) / 2

		self.side = 11
		self.query_cell = math.ceil( self.side * self.side / 2 )
		self.cell_side = self.worldsurf_rect.height / self.side
		self.probe_rect = pygame.Rect( 0, 0, self.cell_side + 2, self.cell_side + 2 )
		self.probe_rect.center = self.worldsurf_rect.center

		self.probeCues = None
		self.hint = False

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
					   "red": Color( 0, s, v ).rgb(),
					   "yellow": Color( 72, s, v ).rgb(),
					   "green": Color( 144, s, v ).rgb(),
					   "blue": Color( 216, s, v ).rgb(),
					   "purple": Color( 288, s, v ).rgb()
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
			self.fp = FixationProcessor( 3.55, sample_rate = 500 )
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

	def drawShapes( self ):
		self.drawProbe()
		obj = -1
		best = 99999
		for i in range( 0, len( self.objects ) ):
			self.objects[i].selected = False
			self.worldsurf.blit( self.objects[i].surface, self.objects[i].rect )
			self.worldsurf.blit( self.objects[i].id_t, self.objects[i].id_rect )
			if self.args.debug:
				pygame.draw.rect( self.worldsurf, ( 128, 128, 255 ), self.objects[i].arect, 1 )
			if self.args.hint and self.hint and self.objects[i].id == self.probe.id:
				pygame.draw.rect( self.worldsurf, ( 128, 255, 128 ), self.objects[i].arect, 3 )
			if self.args.eyetracker and self.fix_data and self.objects[i].rect.collidepoint( self.fix_data.fix_x, self.fix_data.fix_y ):
				d = distance( ( self.fix_data.fix_x, self.fix_data.fix_y ), self.objects[i].rect.center )
				if d < best:
					best = d
					obj = i
		if not obj < 0:
			self.objects[obj].selected = True
			pygame.draw.rect( self.worldsurf, ( 200, 200, 200 ), self.objects[obj].rect, 1 )

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

	def draw_fix( self ):
		if self.fix_data:
			pygame.draw.circle( self.worldsurf, ( 0, 228, 0 ), ( int( self.fix_data.fix_x ), int( self.fix_data.fix_y ) ), 5, 0 )

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
			result = [str( self.trial ), str( self.probe.id ), '-', '-', '-', "%.2f" % self.search_time]
			if self.probe.show_size: result[2] = self.probe.size
			if self.probe.show_color: result[3] = self.probe.color
			if self.probe.show_shape: result[4] = self.probe.shape
			self.output.write( '%s\n' % '\t'.join( result ) )
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

	@d.listen( 'ET_SPL' )
	def iViewXEvent( self, inSender, inEvent, inResponse ):
		if self.state < 0:
			return
		self.fix_data = self.fp.detect_fixation( int( float( inResponse[4] ) ) > 0, float( inResponse[2] ), float( inResponse[4] ) )

if __name__ == '__main__':

	parser = argparse.ArgumentParser( formatter_class = argparse.ArgumentDefaultsHelpFormatter )
	parser.add_argument( '-L', '--log', action = "store", dest = "logfile", help = 'Pipe results to file instead of stdout.' )
	parser.add_argument( '-F', '--fullscreen', action = "store_true", dest = "fullscreen", help = 'Run in fullscreen mode.' )
	parser.add_argument( '-R', '--random', action = "store_true", dest = "random", help = 'Run random trials indefinitely.' )
	parser.add_argument( '-e', '--eyetracker', action = "store", dest = "eyetracker", help = 'Use eyetracker.' )
	parser.add_argument( '-f', '--fixation', action = "store_true", dest = "showfixation", help = 'Overlay fixation.' )
	parser.add_argument( '-D', '--debug', action = "store_true", dest = "debug", help = 'Debug features.' )
	parser.add_argument( '-H', '--hint', action = "store_true", dest = "hint", help = 'Enable hint.' )

	args = parser.parse_args()

	w = World( args )
	w.run()