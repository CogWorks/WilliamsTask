from savitzky_golay import savitzky_golay
from sg_filter import *
import numpy as np
import math

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
		self.fixsamples = [0, None, None]

		self.coeff = calc_coeff( 11, 2, 1 )

		self.winax = np.zeros( 11, dtype = float )
		self.winay = np.zeros( 11, dtype = float )
		self.winx = np.zeros( 11, dtype = float )
		self.winy = np.zeros( 11, dtype = float )
		self.d = None
		self.maxv = 0

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
		vx = smooth( self.winax, self.coeff )[6]
		vy = smooth( self.winay, self.coeff )[6]
		#ax = savitzky_golay( self.winax, 21, 2, 2 )[7]
		#ay = savitzky_golay( self.winay, 21, 2, 2 )[7]
		v = 500.0 * math.sqrt( vx ** 2 + vy ** 2 )
		return v, self.winx[6], self.winy[6]

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
		#print v, a
		print v
		if v == 0:# or v > self.blinkThreshold:
			self.fixsamples = [0, None, None]
			return None
		else:
			if v < 35:#self.threshold:
				ncount = self.fixsamples[0] + 1
				if self.fixsamples[1] == None:
					self.fixsamples[1] = x
				else:
					self.fixsamples[1] = ( self.fixsamples[0] * self.fixsamples[1] + x ) / ncount
				if self.fixsamples[2] == None:
					self.fixsamples[2] = y
				else:
					self.fixsamples[2] = ( self.fixsamples[0] * self.fixsamples[2] + y ) / ncount
				self.fixsamples[0] = ncount
				if self.fixsamples[0] >= self.minFix / 2:
					return ( self.fixsamples[1], self.fixsamples[2] )
				else:
					return None
			else:
				self.fixsamples = [0, None, None]
				return None


if __name__ == '__main__':
	from twisted.internet import reactor
	from twisted.internet.task import LoopingCall
	from pyviewx import iViewXClient, Dispatcher
	from pyviewx.pygamesupport import Calibrator

	import pygame
	import random

	pygame.display.init()
	pygame.font.init()

	state = -1

	#screen = pygame.display.set_mode( ( 1024, 768 ), 0 )
	screen = pygame.display.set_mode( ( 0, 0 ), pygame.FULLSCREEN )
	screen_rect = screen.get_rect()

	angle1 = random.uniform( 0, 360 )
	angle2 = random.uniform( 0, 360 )

	gaze = None
	fix = None

	d = Dispatcher()

	@d.listen( 'ET_SPL' )
	def iViewXEvent( inSender, inEvent, inResponse ):
		global gaze, fix, fp
		gaze = ( ( int( inResponse[2] ), int( inResponse[4] ) ), ( int( inResponse[3] ), int( inResponse[5] ) ) )
		t = int( inResponse[0] )
		x = np.mean( ( int( inResponse[2] ), int( inResponse[3] ) ) )
		y = np.mean( ( int( inResponse[4] ), int( inResponse[5] ) ) )
		ex = np.mean( ( float( inResponse[10] ), float( inResponse[11] ) ) )
		ey = np.mean( ( float( inResponse[12] ), float( inResponse[13] ) ) )
		ez = np.mean( ( float( inResponse[14] ), float( inResponse[15] ) ) )
		fix = fp.processData( t, x, y, ex, ey, ez )

	def update():
		global state, angle1, angle2, gaze, fix
		if state < 0:
			return
		screen.fill( ( 0, 0, 0 ) )
		pygame.draw.circle( screen, ( 255, 0, 0 ), screen_rect.center, 10, 0 )
		pygame.draw.circle( screen, ( 255, 0, 0 ), ( screen_rect.width / 10, screen_rect.height / 10 ), 10, 0 )
		pygame.draw.circle( screen, ( 255, 0, 0 ), ( screen_rect.width / 10, screen_rect.height / 10 * 9 ), 10, 0 )
		pygame.draw.circle( screen, ( 255, 0, 0 ), ( screen_rect.width / 10 * 9, screen_rect.height / 10 ), 10, 0 )
		pygame.draw.circle( screen, ( 255, 0, 0 ), ( screen_rect.width / 10 * 9, screen_rect.height / 10 * 9 ), 10, 0 )
		pygame.draw.circle( screen, ( 0, 0, 255 ), ( screen_rect.centerx + int( math.cos( angle1 ) * screen_rect.height / 6 ), screen_rect.centery + int( math.sin( angle1 ) * screen_rect.height / 6 ) ), 5, 0 )
		pygame.draw.circle( screen, ( 0, 0, 255 ), ( screen_rect.centerx + int( math.cos( angle2 ) * screen_rect.height / 3 ), screen_rect.centery + int( math.sin( angle2 ) * screen_rect.height / 3 ) ), 5, 0 )
		if gaze:
			pygame.draw.circle( screen, ( 255, 255, 0 ), gaze[0], 3, 1 )
			pygame.draw.circle( screen, ( 0, 255, 255 ), gaze[1], 3, 1 )
		if fix:
			pygame.draw.circle( screen, ( 255, 0, 255 ), map( int, fix ), 5, 1 )
		pygame.display.flip()

		angle1 += .05
		if angle1 >= 360:
			angle1 = 0

		angle2 -= .025
		if angle2 <= 0:
			angle2 = 360

	def cleanup( self, *args, **kwargs ):
		reactor.stop()

	def start( lc ):
		global state, update, client, cleanup
		state = 0
		client.addDispatcher( d )
		lc = LoopingCall( update )
		dd = lc.start( 1.0 / 30 )
		dd.addCallbacks( cleanup )

	client = iViewXClient( '192.168.1.100', 4444 )
	reactor.listenUDP( 5555, client )
	calibrator = Calibrator( client, screen, reactor = reactor )
	fp = VelocityFP()
	calibrator.start( start )
	reactor.run()
