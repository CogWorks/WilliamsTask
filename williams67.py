#/usr/bin/env python
"""
This is a replicate of the classic Williams '67 visual search task with some
minor alterations.
"""
import sys
import random
import math
import datetime
import pygame
import argparse

pygame.display.init()
pygame.font.init()

class Shape(object):
    """Shape object"""
    
    def __init__(self, world, size, name, color, id, location):
        super(Shape, self).__init__()
        self.shape = name
        self.color = color
        self.size = size
        self.id = id
        self.surface = world.fonts[size].render(world.shapes[name], True, world.colors[color])
        self.surface = pygame.transform.rotate(self.surface, random.randint(1, 360))
        self.rect = self.surface.get_rect()
        self.rect.centerx = location[0]
        self.rect.centery = location[1]
        self.bounding_rect = self.surface.get_bounding_rect()
        self.id_t = world.fonts["id"].render(str(id), True, (0, 0, 0))
        self.id_rect = self.id_t.get_rect()
        self.id_rect.centerx = location[0] + random.uniform(-world.jitter / 2, world.jitter / 2)
        self.id_rect.centery = location[1] + random.uniform(-world.jitter / 2, world.jitter / 2)

    def clickCheck(self, position):
        return self.rect.collidepoint(position)
        
    def printInfo(self):
        print self.id, self.size, self.color, self.shape


class Probe(object):
    """Probe objects"""
    
    def __init__(self, world, shape):
        super(Probe, self).__init__()
        
        self.id = shape.id
        self.shape = shape.shape
        self.size = shape.size
        self.color = shape.color
        self.elements = list()
        
        self.id_t = world.fonts["probe"].render(str(self.id), True, (0, 0, 0))
        self.id_rect = self.id_t.get_rect()
        self.shape_t = world.fonts["probe"].render(self.shape, True, (0, 0, 0))
        self.shape_rect = self.shape_t.get_rect()
        self.size_t = world.fonts["probe"].render(self.size, True, (0, 0, 0))
        self.size_rect = self.size_t.get_rect()
        self.color_t = world.fonts["probe"].render(self.color, True, (0, 0, 0))
        self.color_rect = self.color_t.get_rect()
        
        self.show_shape = random.randint(0, 1)
        self.show_size = random.randint(0, 1)
        self.show_color = random.randint(0, 1)
        
        if self.show_shape:
            self.elements.append((self.shape_t, self.shape_rect))
        if self.show_size:
            self.elements.append((self.size_t, self.size_rect))
        if self.show_color:
            self.elements.append((self.color_t, self.color_rect))
        random.shuffle(self.elements)
        
        self.id_rect.centerx = world.worldsurf_rect.centerx - world.xoffset
        self.shape_rect.centerx = world.worldsurf_rect.centerx - world.xoffset
        self.size_rect.centerx = world.worldsurf_rect.centerx - world.xoffset
        self.color_rect.centerx = world.worldsurf_rect.centerx - world.xoffset
        
        elmlen = len(self.elements)
        if elmlen == 0:
            self.id_rect.centery = world.worldsurf_rect.centery
        elif elmlen == 1:
            self.id_rect.centery = world.worldsurf_rect.centery - world.cell_side / 6 * .6
            self.elements[0][1].centery = world.worldsurf_rect.centery + world.cell_side / 6 * .6
        elif elmlen == 2:
            self.id_rect.centery = world.worldsurf_rect.centery - world.cell_side / 6 * 1.3
            self.elements[0][1].centery = world.worldsurf_rect.centery
            self.elements[1][1].centery = world.worldsurf_rect.centery + world.cell_side / 6 * 1.3
        elif elmlen == 3:
            self.id_rect.centery = world.worldsurf_rect.centery - world.cell_side / 6 * 1.9
            self.elements[0][1].centery = world.worldsurf_rect.centery - world.cell_side / 6 * .6
            self.elements[1][1].centery = world.worldsurf_rect.centery + world.cell_side / 6 * .6
            self.elements[2][1].centery = world.worldsurf_rect.centery + world.cell_side / 6 * 1.9


class World(object):
    """Main game application"""

    def __init__(self):
        super(World, self).__init__()
        
        pygame.mouse.set_visible(False)
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.current_x, self.current_y = self.screen.get_size()
        self.xoffset = self.current_x / 2 - self.current_y / 2
        self.jitter = self.current_y * 0.0125
        self.nrows = 13
        self.ncols = 13
        self.ncolors = 5
        self.nshapes = 5
        self.nsizes = 4
        self.nobjects = self.ncolors * self.nshapes * self.nsizes
        self.ncells = self.nrows * self.ncols
        self.query_cell = math.ceil(self.ncols * self.nrows / 2)
        self.cell_side = self.current_y / self.nrows
        self.worldsurf = pygame.Surface((self.current_y, self.current_y))
        self.worldsurf_rect = self.worldsurf.get_rect()
        self.worldsurf_rect.centerx = self.current_x / 2
        
        self.fonts = {
                      "large": pygame.font.Font("cutouts.ttf", self.cell_side),
                      "medium": pygame.font.Font("cutouts.ttf", int(self.cell_side * (1 - .5 / 3 * 1))),
                      "small": pygame.font.Font("cutouts.ttf", int(self.cell_side * (1 - .5 / 3 * 2))),
                      "tiny": pygame.font.Font("cutouts.ttf", int(self.cell_side * (1 - .5 / 3 * 3))),
                      "id": pygame.font.Font("freesans.ttf", self.cell_side / 7),
                      "probe": pygame.font.Font("freesans.ttf", self.cell_side / 6)
                      }
        self.shapes = {
                       "circle":"E",
                       "square":"K",
                       "oval":"F",
                       "diamond":"T",
                       "crescent":"Q",
                       "cross":"R",
                       "star":"C",
                       "triangle":"A"
                       }
        self.colors = {
                       "pink": (255, 192, 203),
                       "blue": (0, 0, 255),
                       "yellow": (255, 255, 0),
                       "orange": (255, 165, 0),
                       "green": (0, 255, 0)
                       }
        self.exp_shapes = ["star", "cross", "crescent", "diamond", "oval"]
        self.exp_colors = ["pink", "blue", "yellow", "green", "orange"]
        self.exp_sizes = ["large", "medium", "small", "tiny"]

    def setup(self):
        
        self.worldsurf.fill((127, 127, 127))
        
        self.cells = list()
        self.objects = list()
        used = list()
        ids = list() 
        
        while len(self.cells) < self.nobjects:
            i = random.randint(1, self.ncells)
            if i == self.query_cell: continue
            if self.cells.count(i) == 0:
                r = math.floor(i / self.ncols)
                c = i - r * self.ncols
                o = (self.exp_shapes[random.randint(0, 4)], self.exp_colors[random.randint(0, 4)], \
                     self.exp_sizes[random.randint(0, 3)])
                if used.count(o) == 0:
                    id = 0
                    while True:
                        id = random.randint(0, 99)
                        if ids.count(id) == 0: break
                    ids.append(id)
                    x = (c + .5) * self.cell_side + random.uniform(-self.jitter, self.jitter)
                    y = (r + .5) * self.cell_side + random.uniform(-self.jitter, self.jitter)
                    s = Shape(self, o[2], o[0], o[1], id, (x, y))
                    self.cells.append(i)
                    used.append(o)
                    self.objects.append(s)
        self.probe = Probe(self, self.objects[random.randint(0, 99)])
        
    def showProbe(self):
             
        self.worldsurf.blit(self.probe.id_t, self.probe.id_rect)
        for pelm in self.probe.elements:
            self.worldsurf.blit(pelm[0], pelm[1])
        self.screen.blit(self.worldsurf, self.worldsurf_rect)
        pygame.display.flip()
        
        cont = True
        while cont:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    cont = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                    else:
                        cont = False
                        break

    def showShapes(self):

        for object in self.objects:
            self.worldsurf.blit(object.surface, object.rect)
            self.worldsurf.blit(object.id_t, object.id_rect)
        self.screen.blit(self.worldsurf, self.worldsurf_rect)
        pygame.display.flip()
        
        self.end_time = 0
        pygame.mouse.set_pos(self.current_x / 2, self.current_y / 2)
        pygame.mouse.set_visible(True)
        self.start_time = datetime.datetime.now()
        
        cont = True
        while cont:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.end_time = datetime.datetime.now() - self.start_time
                        self.search_time = self.end_time.seconds * 1000 + self.end_time.microseconds * 0.001
                        for object in self.objects:
                            mousex, mousey = event.pos
                            mousex = mousex - self.xoffset
                            if object.clickCheck((mousex, mousey)):
                                if object.id == self.probe.id:
                                    cont = False
                                    break
                        if not cont: break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                        
    def showSearchTime(self):
        time_t = str(self.search_time)
        pygame.mouse.set_visible(False)
        print self.probe.id,
        if self.probe.show_size: print self.probe.size,
        if self.probe.show_color: print self.probe.color,
        if self.probe.show_shape: print self.probe.shape,
        print time_t
        score_font = pygame.font.Font("freesans.ttf", self.cell_side / 3)
        msg = "Found target in " + time_t + " miliseconds."
        time = score_font.render(msg, True, (255, 255, 255))
        time_rect = time.get_rect()
        time_rect.centerx = self.current_x / 2
        time_rect.centery = self.current_y / 2
        self.screen.fill((0, 0, 0))
        self.screen.blit(time, time_rect)
        pygame.display.flip()

        cont = True
        while cont:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    cont = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                    else:
                        cont = False
                        break

    def run(self):
        self.setup()
        self.showProbe()
        self.showShapes()
        self.showSearchTime()
                
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    cwgroup = parser.add_argument_group('CogWorld arguments:')
    cwgroup.add_argument('-a', action="store", dest="rpc_address", default='localhost', help='CogWorld RPC address')
    cwgroup.add_argument('-p', action="store", dest="rpc_port", default=3000, help='CogWorld RPC port')
    args = parser.parse_args()
    
    w = World()
    while True:
        w.run()
