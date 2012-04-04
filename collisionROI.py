from __future__ import division
import math, random, sys

def intersection1( ( m1, b1 ), ( m2, b2 ) ):
	x = ( b2 - b1 ) / ( m1 - m2 )
	y = m1 * x + b1
	return ( x, y )

def intersection2( ( m1, b1 ), x ):
	return ( x, m1 * x + b1 )

def lineComponents( p1, p2 ):
	m = slope( p1, p2 )
	b = p1[1] - m * p1[0]
	return ( m, b )

def distance( p1, p2 ):
	return math.sqrt( ( p2[0] - p1[0] ) ** 2 + ( p2[1] - p1[1] ) ** 2 )

def centroid( vertices ):
	x = sum( [x[0] for x in vertices] ) / len( vertices )
	y = sum( [y[1] for y in vertices] ) / len( vertices )
	return ( x, y )

def slope( p1, p2 ):
	return ( p2[1] - p1[1] ) / ( p2[0] - p1[0] )

def nearestPoint( vertices, p1 ):
	dists = {}
	for v in vertices:
		dists[distance( p1, v )] = v
	return dists[min( dists )]

def nearestSides( vertices, p1 ):
	np = nearestPoint( vertices, p1 )
	i = vertices.index( np )
	m = len( vertices ) - 1
	if i > 0 and i < m:
		return ( i - 1, i, i + 1 )
	if i == 0:
		return ( m, 0, 1 )
	if i == m:
		return ( m - 1, m, 0 )

def nearestEdge( vertices, p1 ):
	ns = nearestSides( vertices, p1 )
	print ns
	p2 = centroid( vertices )
	c1 = lineComponents( p1, p2 )
	c2 = lineComponents( vertices[ns[1]], vertices[ns[0]] )
	c3 = lineComponents( vertices[ns[1]], vertices[ns[2]] )
	i1 = intersection1( c1, c2 )
	i2 = intersection1( c1, c3 )
	dists = {}
	dists[distance( p2, i1 )] = i1
	dists[distance( p2, i2 )] = i2
	return ( dists[min( dists )], min( dists ) )

def testCollision( vertices, p1, r ):
	ne = nearestEdge( vertices, p1 )
	p2 = centroid( vertices )
	if distance( p1, p2 ) - r <= ne[1]:
		return True
	return False

if __name__ == '__main__':

	def rotate2d( degrees, point, origin ):
		x = point[0] - origin[0]
		yorz = point[1] - origin[1]
		newx = ( x * math.cos( math.radians( degrees ) ) ) - ( yorz * math.sin( math.radians( degrees ) ) )
		newyorz = ( x * math.sin( math.radians( degrees ) ) ) + ( yorz * math.cos( math.radians( degrees ) ) )
		newx += origin[0]
		newyorz += origin[1]
		return newx, newyorz

	def genPolygon( sides, center, radius ):
		deg = ( 2.0 * math.pi ) / sides
		rot = random.uniform( 0, 360 )
		points = []
		for i in range( 0, sides ):
			x = center[0] + radius * math.cos( i * deg )
			y = center[1] + radius * math.sin( i * deg )
			points.append( rotate2d( rot, ( x, y ), center ) )
		return points

	import pygame
	pygame.display.init()
	pygame.font.init()
	screen = pygame.display.set_mode( ( 0, 0 ), pygame.FULLSCREEN )
	screen_rect = screen.get_rect()

	def drawTest():
		screen.fill( ( 0, 0, 0 ) )
		poly = genPolygon( random.choice( range( 3, 9 ) ), screen_rect.center, random.choice( range( 40, 141 ) ) )
		fix = map( int, ( random.triangular( screen_rect.centerx / 4, screen_rect.centerx + screen_rect.centerx / 4, screen_rect.centerx ), random.triangular( screen_rect.centery / 4, screen_rect.centery + screen_rect.centery / 4, screen_rect.centery ) ) )
		r = random.choice( range( 10, 31 ) )
		ns = nearestSides( poly, fix )
		ne = nearestEdge( poly, fix )
		pygame.draw.line( screen, ( 255, 255, 0 ), fix, screen_rect.center )
		pygame.draw.polygon( screen, ( 255, 0, 0 ), poly, 1 )
		pygame.draw.circle( screen, ( 255, 0, 0 ), map( int, poly[ns[1]] ), 5, 1 )
		pygame.draw.circle( screen, ( 0, 0, 255 ), map( int, poly[ns[0]] ), 5, 1 )
		pygame.draw.circle( screen, ( 0, 0, 255 ), map( int, poly[ns[2]] ), 5, 1 )
		pygame.draw.circle( screen, ( 255, 255, 0 ), map( int, ne[0] ), 5, 1 )
		pygame.draw.circle( screen, ( 0, 255, 0 ), fix, r , int( not testCollision( poly, fix, r ) ) )
		pygame.display.flip()

	drawTest()
	while ( True ):
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					sys.exit( 0 )
				elif event.key == pygame.K_SPACE:
					drawTest()


