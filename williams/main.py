#!/usr/bin/env python

from __future__ import division

import pygletreactor
pygletreactor.install()
from twisted.internet import reactor

from pyglet import image, font, text, clock
from pyglet.gl import *
from pyglet.window import key

from cocos.director import *
from cocos.layer import *
from cocos.sprite import *
from cocos.menu import *
from cocos.text import *
from cocos.scenes.transitions import *
from cocos.actions.interval_actions import *
from cocos.actions.base_actions import *
from cocos.actions.instant_actions import * 
from cocos.batch import BatchNode
from cocos.collision_model import *
import cocos.euclid as eu
from pyglet.media import StaticSource

from random import choice, randrange, uniform, sample, shuffle
import string

from primitives import Circle, Line

import platform

import sys, os
sys.path.append("/System/Library/Frameworks/Python.framework/Versions/2.7/Extras/lib/python/PyObjC")
import pyttsx
engine = pyttsx.init()
engine.startLoop(False)
def pyttsx_iterate(dt):
    engine.iterate()

from util import hsv_to_rgb, screenshot
from handler import DefaultHandler
from menu import BetterMenu, GhostMenuItem, BetterEntryMenuItem
from scene import Scene

from odict import OrderedDict

try:
    from pyviewx.client import iViewXClient, Dispatcher
    from calibrator import CalibrationLayer, HeadPositionLayer
    eyetracking = True
except ImportError:
    eyetracking = False
    
from pycogworks.logging import get_time, Logger, writeHistoryFile, getDateTimeStamp
from pycogworks.crypto import rin2id
from cStringIO import StringIO
import tarfile
import json

class OptionsMenu(BetterMenu):

    def __init__(self):
        super(OptionsMenu, self).__init__('Options')
        self.screen = director.get_window_size()
        
        ratio = self.screen[1] / self.screen[0]
        
        self.select_sound = StaticSource(pyglet.resource.media('move.wav'))
        
        self.font_title['font_name'] = 'Pipe Dream'
        self.font_title['font_size'] = self.screen[0] / 18
        self.font_title['color'] = (255, 255, 255, 255)
        
        self.font_item['font_name'] = 'Pipe Dream',
        self.font_item['color'] = (255, 255, 255, 255)
        self.font_item['font_size'] = self.screen[1] / 16 * ratio
        self.font_item_selected['font_name'] = 'Pipe Dream'
        self.font_item_selected['color'] = (0, 0, 255, 255)
        self.font_item_selected['font_size'] = self.screen[1] / 16 * ratio
        
        self.items = OrderedDict()
        
        self.items['fps'] = ToggleMenuItem('Show FPS:', self.on_show_fps, director.show_FPS)
        self.items['fullscreen'] = ToggleMenuItem('Fullscreen:', self.on_fullscreen, director.window.fullscreen)
        if eyetracking:
            self.items['eyetracker'] = ToggleMenuItem("EyeTracker:", self.on_eyetracker, director.settings['eyetracker'])
            self.items['eyetracker_ip'] = EntryMenuItem('EyeTracker IP:', self.on_eyetracker_ip, director.settings['eyetracker_ip'])
            self.items['eyetracker_in_port'] = EntryMenuItem('EyeTracker In Port:', self.on_eyetracker_in_port, director.settings['eyetracker_in_port'])
            self.items['eyetracker_out_port'] = EntryMenuItem('EyeTracker Out Port:', self.on_eyetracker_out_port, director.settings['eyetracker_out_port'])
            self.set_eyetracker_extras(director.settings['eyetracker'])
        
        self.create_menu(self.items.values(), zoom_in(), zoom_out())
        
    def on_enter(self):
        super(OptionsMenu, self).on_enter()
        self.orig_values = (director.settings['eyetracker_ip'],
                            director.settings['eyetracker_in_port'],
                            director.settings['eyetracker_out_port'])
    
    def on_exit(self):
        super(OptionsMenu, self).on_exit()
        new_values = (director.settings['eyetracker_ip'],
                            director.settings['eyetracker_in_port'],
                            director.settings['eyetracker_out_port'])
        if new_values != self.orig_values:
            director.scene.dispatch_event("eyetracker_info_changed")
        
    def on_show_fps(self, value):
        director.show_FPS = value
        
    def on_fullscreen(self, value):
        screen = pyglet.window.get_platform().get_default_display().get_default_screen()
        director.window.set_fullscreen(value, screen)
    
    def on_experiment(self, value):
        director.settings['experiment'] = value
    
    if eyetracking:
    
        def set_eyetracker_extras(self, value):
            self.items['eyetracker_ip'].visible = value
            self.items['eyetracker_in_port'].visible = value
            self.items['eyetracker_out_port'].visible = value
            
        def on_eyetracker(self, value):
            director.settings['eyetracker'] = value
            self.set_eyetracker_extras(value)
            
        def on_eyetracker_ip(self, ip):
            director.settings['eyetracker_ip'] = ip
        
        def on_eyetracker_in_port(self, port):
            director.settings['eyetracker_in_port'] = port
        
        def on_eyetracker_out_port(self, port):
            director.settings['eyetracker_out_port'] = port
            
    def on_quit(self):
        self.parent.switch_to(0)

class MainMenu(BetterMenu):

    def __init__(self):
        super(MainMenu, self).__init__("The Williams' Search Task")
        self.screen = director.get_window_size()
        
        ratio = self.screen[1] / self.screen[0]
                
        self.select_sound = StaticSource(pyglet.resource.media('move.wav'))

        self.font_title['font_name'] = 'Pipe Dream'
        self.font_title['font_size'] = self.screen[0] / 18
        self.font_title['color'] = (255, 255, 255, 255)

        self.font_item['font_name'] = 'Pipe Dream',
        self.font_item['color'] = (255, 255, 255, 255)
        self.font_item['font_size'] = self.screen[1] / 16 * ratio
        self.font_item_selected['font_name'] = 'Pipe Dream'
        self.font_item_selected['color'] = (0, 0, 255, 255)
        self.font_item_selected['font_size'] = self.screen[1] / 16 * ratio

        self.menu_anchor_y = 'center'
        self.menu_anchor_x = 'center'

        self.items = OrderedDict()
        
        self.items['mode'] = MultipleMenuItem('Mode: ', self.on_mode, director.settings['modes'], director.settings['modes'].index(director.settings['mode']))
        # self.items['tutorial'] = MenuItem('Tutorial', self.on_tutorial)
        self.items['start'] = MenuItem('Start', self.on_start)
        self.items['options'] = MenuItem('Options', self.on_options)
        self.items['quit'] = MenuItem('Quit', self.on_quit)
        
        self.create_menu(self.items.values(), zoom_in(), zoom_out())

    def on_mode(self, mode):
        director.settings['mode'] = director.settings['modes'][mode]
    
    def on_tutorial(self):
        director.push(SplitColsTransition(Scene(TutorialLayer())))
        
    def on_options(self):
        self.parent.switch_to(1)
        
    def on_start(self):
        if director.settings['mode'] == 'Experiment':
            self.parent.switch_to(2)
        else:
            filebase = "WilliamsSearch_%s" % (getDateTimeStamp())
            director.settings['filebase'] = filebase
            director.scene.dispatch_event('start_task')

    def on_quit(self):
        reactor.callFromThread(reactor.stop)
                
class ParticipantMenu(BetterMenu):

    def __init__(self):
        super(ParticipantMenu, self).__init__("Participant Information")
        self.screen = director.get_window_size()
        
        ratio = self.screen[1] / self.screen[0]
                
        self.select_sound = StaticSource(pyglet.resource.media('move.wav'))

        self.font_title['font_name'] = 'Pipe Dream'
        self.font_title['font_size'] = self.screen[0] / 18
        self.font_title['color'] = (255, 255, 255, 255)

        self.font_item['font_name'] = 'Pipe Dream',
        self.font_item['color'] = (255, 255, 255, 255)
        self.font_item['font_size'] = self.screen[1] / 16 * ratio
        self.font_item_selected['font_name'] = 'Pipe Dream'
        self.font_item_selected['color'] = (0, 0, 255, 255)
        self.font_item_selected['font_size'] = self.screen[1] / 16 * ratio

        self.menu_anchor_y = 'center'
        self.menu_anchor_x = 'center'

    def on_enter(self):
        super(ParticipantMenu, self).on_enter()
        self.items = OrderedDict()
        self.items['firstname'] = BetterEntryMenuItem('First Name:', self.on_info_change, "", validator=lambda x: x.isalpha())
        self.items['lastname'] = BetterEntryMenuItem('Last Name:', self.on_info_change, "", validator=lambda x: x.isalpha())
        self.items['rin'] = BetterEntryMenuItem('RIN:', self.on_info_change, "", max_length=9, validator=lambda x: unicode(x).isnumeric())
        self.items['start'] = MenuItem('Start', self.on_start)
        self.create_menu(self.items.values(), zoom_in(), zoom_out())
        self.items['start'].visible = False
        
    def on_exit(self):
        super(ParticipantMenu, self).on_exit()
        for c in self.get_children(): self.remove(c)
                
    def on_info_change(self, *args, **kwargs):
        firstname = ''.join(self.items['firstname']._value).strip()
        lastname = ''.join(self.items['lastname']._value).strip()
        rin = ''.join(self.items['rin']._value)
        if len(firstname) > 0 and len(lastname) > 0 and len(rin) == 9:
            self.items['start'].visible = True
        else:
            self.items['start'].visible = False
        
    def on_start(self):
        si = {}
        si['first_name'] = ''.join(self.items['firstname']._value).strip()
        si['last_name'] = ''.join(self.items['lastname']._value).strip()
        si['rin'] = ''.join(self.items['rin']._value)
        si['encrypted_rin'], si['cipher'] = rin2id(si['rin'])
        si['timestamp'] = getDateTimeStamp()
        director.settings['si'] = si
        filebase = "WilliamsSearch_%s_%s" % (si['timestamp'], si['encrypted_rin'][:8])
        director.settings['filebase'] = filebase
        writeHistoryFile("data/%s.history" % filebase, si)
        director.scene.dispatch_event('start_task')

    def on_quit(self):
        self.parent.switch_to(0)
        
class Shape(Sprite):

    def __init__(self, image, chunk=None, position=(0, 0), rotation=0, scale=1, opacity=255, color=(255, 255, 255)):
        super(Shape, self).__init__(image, rotation=rotation, scale=scale, opacity=opacity, color=color)
        self.chunk = chunk
        if platform.system() == 'Windows':
            rscale = .34
            if self.chunk:
                if self.chunk[0] == 'cross':
                    rscale = .28
                elif self.chunk[0] == 'diamond':
                    rscale = .31
        else:
            rscale = .55
            if self.chunk:
                if self.chunk[0] == 'diamond':
                    rscale = .52
                elif self.chunk[0] == 'oval':
                    rscale = .52
        self.radius = max(self.width, self.height) * rscale
        self.set_position(position[0], position[1])
    
    def set_position(self, x, y):

        self.cshape = CircleShape(eu.Vector2(x, y), self.radius)
        super(Shape, self).set_position(self.cshape.center[0], self.cshape.center[1])

class TutorialLayer(ColorLayer):
    
    is_event_handler = True
    
    def __init__(self):
        self.screen = director.get_window_size()
        super(TutorialLayer, self).__init__(168, 168, 168, 255, self.screen[0], self.screen[1])
        
        self.side = self.screen[1] / 11
        self.ratio = self.side / 128
        self.scales = [self.ratio * 2, self.ratio * 1.25, self.ratio * .5]
        self.sizes = ["large", "medium", "small"]
        
        self.batch = BatchNode()
        self.text_batch = BatchNode()
        self.add(self.batch)
        self.add(self.text_batch, z=1)
        
        s = 50
        v = 100
        self.colors = {"red": hsv_to_rgb(0, s, v),
                       "yellow": hsv_to_rgb(72, s, v),
                       "green": hsv_to_rgb(144, s, v),
                       "blue": hsv_to_rgb(216, s, v),
                       "purple": hsv_to_rgb(288, s, v)}
        
        self.shapes = {"oval":"F",
                       "diamond":"T",
                       "crescent":"Q",
                       "cross":"Y",
                       "star":"C"}
        self.font = font.load('Cut Outs for 3D FX', 128)
        for shape in self.shapes:
            self.shapes[shape] = self.font.get_glyphs(self.shapes[shape])[0].get_texture(True)
        
        self.lines = []
        
    def do_phase1(self):
        director.window.set_mouse_visible(False)
        
        label_color = (32, 32, 32, 255)
            
        ids = range(1, 76)
        shuffle(ids)
            
        j = 1
        for scale in self.scales:
            i = 0
            y = self.screen[1] / 2 + self.screen[1] / 5 * j + self.screen[1] / 20 
            x = self.screen[0] / 2 + self.screen[0] / 7 * (i - 2.75)
            
            l = text.Label("%s" % self.sizes[self.scales.index(scale)].upper(), font_size=36 * self.ratio,
                            x=x, y=y, font_name="Pipe Dream", color=label_color,
                            anchor_x='center', anchor_y='center', batch=self.text_batch.batch)
            
            i += 1
            for shape in self.shapes:
                img = self.shapes[shape].get_texture(True)
                img.anchor_x = 'center'
                img.anchor_y = 'center'
                x = self.screen[0] / 2 + self.screen[0] / 7 * (i - 2.75)
                sprite = Shape(img, scale=scale, position=(x, y), color=self.colors.values()[i - 1], rotation=randrange(0, 365))
                l = text.Label("%02d" % ids.pop(), font_size=14 * self.ratio,
                            x=x, y=y, font_name="Monospace", color=label_color,
                            anchor_x='center', anchor_y='center', batch=self.text_batch.batch)
                self.batch.add(sprite)
                if self.scales.index(scale) == 0:
                    yy = self.screen[1] / 2 + self.screen[1] / 5 * (j + .75) + self.screen[1] / 20
                    l = text.Label("%s" % self.colors.keys()[i - 1].upper(), font_size=36 * self.ratio,
                                   x=x, y=yy, font_name="Pipe Dream", color=label_color,
                                   anchor_x='center', anchor_y='center', batch=self.text_batch.batch)
                i += 1
                if self.scales.index(scale) == 2:
                    yy = self.screen[1] / 2 + self.screen[1] / 5 * (j - .75) + self.screen[1] / 20
                    l = text.Label("%s" % shape.upper(), font_size=36 * self.ratio,
                                   x=x, y=yy, font_name="Pipe Dream", color=label_color,
                                   anchor_x='center', anchor_y='center', batch=self.text_batch.batch)
                    
            
            j -= 1
        
        engine.say(',,,,In this task, your job will be to search for target objects.')
        engine.say('Each object in the search display will have a unique combination of shape, color and size.,,')
        engine.say('The 5 colors used in this task are:')
        engine.say('blue,,,,', 'blue')
        engine.say('purple,,,,', 'purple')
        engine.say('green,,,,', 'green')
        engine.say('yellow,,,,', 'yellow')
        engine.say('and red.,,,,', 'red')
        engine.say('The 5 shapes used in this task are:')
        engine.say('oval,,,,', 'oval')
        engine.say('diamond,,,,', 'diamond')
        engine.say('star,,,,', 'star')
        engine.say('crescent,,,,', 'crescent')
        engine.say('and cross.,,,,', 'cross')
        engine.say('The 3 sizes used in this task are:')
        engine.say('large,,,,', 'large')
        engine.say('medium,,,,', 'medium')
        engine.say('and small.,,,,', 'small')
        engine.say('The 5 colors, 5 shapes, and 3 sizes result in 75 unique combinations.')
        engine.say(',,,Note,, not all combinations are shown on this screen.')
        engine.say(',,,Each object will also have a randomly assigned numeric I D between 1 and 75.,,,', 'id')
        engine.say('Take a moment and study the shapes, colors and sizes.,,,,,,', 'phase1-done')

    def do_phase2(self):
        print "doing phase 2"

    def on_enter(self):
        if director.scene == self:
            super(TutorialLayer, self).on_enter()
            self.schedule(pyttsx_iterate)
            self.token_fu = engine.connect('finished-utterance', self.finished_utterance)
            self.token_su = engine.connect('started-utterance', self.started_utterance)
            self.do_phase1()
        
    def on_exit(self):
        if director.scene == self:
            super(TutorialLayer, self).on_exit()
            self.unschedule(pyttsx_iterate)
            engine.disconnect(self.token_fu)
            engine.disconnect(self.token_su)
    
    def draw(self):
        super(TutorialLayer, self).draw()
        for line in self.lines:
            line.render()

    def get_color_box(self, i):
        x1 = self.screen[0] / 2 + self.screen[0] / 7 * (i - 3.25)
        x2 = self.screen[0] / 2 + self.screen[0] / 7 * (i - 2.25)
        y = self.screen[1] / 5 + self.screen[1] / 40
        return [Line((x1, 1.25 * y), (x1, 4.5 * y - self.screen[1] / 40), stroke=2, color=(1, 1, 1, 1)),
                Line((x2, 1.25 * y), (x2, 4.5 * y - self.screen[1] / 40), stroke=2, color=(1, 1, 1, 1)),
                Line((x1, 1.25 * y), (x2, 1.25 * y), stroke=2, color=(1, 1, 1, 1)),
                Line((x1, 4.5 * y - self.screen[1] / 40), (x2, 4.5 * y - self.screen[1] / 40), stroke=2, color=(1, 1, 1, 1))]
        
    def get_shape_box(self, i):
        x1 = self.screen[0] / 2 + self.screen[0] / 7 * (i - 3.25)
        x2 = self.screen[0] / 2 + self.screen[0] / 7 * (i - 2.25)
        y = self.screen[1] / 5 + self.screen[1] / 40
        return [Line((x1, .5 * y), (x1, 4 * y - self.screen[1] / 40), stroke=2, color=(1, 1, 1, 1)),
                Line((x2, .5 * y), (x2, 4 * y - self.screen[1] / 40), stroke=2, color=(1, 1, 1, 1)),
                Line((x1, .5 * y), (x2, .5 * y), stroke=2, color=(1, 1, 1, 1)),
                Line((x1, 4 * y - self.screen[1] / 40), (x2, 4 * y - self.screen[1] / 40), stroke=2, color=(1, 1, 1, 1))]
    
    def get_size_box(self, i):
        x = self.screen[0] / 7
        y1 = self.screen[1] / 2 - self.screen[1] / 5 * (i - 1.5) + self.screen[1] / 20
        y2 = self.screen[1] / 2 - self.screen[1] / 5 * (i - 2.5) + self.screen[1] / 20
        return [
                Line((x * .25, y1), (x * 6.25, y1), stroke=2, color=(1, 1, 1, 1)),
                Line((x * .25, y2), (x * 6.25, y2), stroke=2, color=(1, 1, 1, 1)),
                Line((x * .25, y1), (x * .25, y2), stroke=2, color=(1, 1, 1, 1)),
                Line((x * 6.25, y1), (x * 6.25, y2), stroke=2, color=(1, 1, 1, 1))
                ]
    
    def started_utterance(self, name):
        if name == None:
            self.lines = []
            
        elif name == 'id':
            y = self.screen[1] / 2 - 5 + self.screen[1] / 20
            x = self.screen[0] / 2 + self.screen[0] / 7 * (3 - 2.75) + 5
            self.arrow = Sprite("cursor_arrow.png", position=(x, y))
            rect = self.arrow.get_rect()
            self.arrow.position = rect.bottomright
            self.arrow.do(Repeat(Blink(2, 1.5)))
            self.add(self.arrow)
            
        elif name == 'blue':
            self.lines = self.get_color_box(1)
        elif name == 'purple':
            self.lines = self.get_color_box(2)
        elif name == 'green':
            self.lines = self.get_color_box(3)
        elif name == 'yellow':
            self.lines = self.get_color_box(4)
        elif name == 'red':
            self.lines = self.get_color_box(5)
            
        elif name == 'oval':
            self.lines = self.get_shape_box(1)
        elif name == 'diamond':
            self.lines = self.get_shape_box(2)
        elif name == 'star':
            self.lines = self.get_shape_box(3)
        elif name == 'crescent':
            self.lines = self.get_shape_box(4)
        elif name == 'cross':
            self.lines = self.get_shape_box(5)
            
        elif name == 'large':
            self.lines = self.get_size_box(1)
        elif name == 'medium':
            self.lines = self.get_size_box(2)
        elif name == 'small':
            self.lines = self.get_size_box(3)
            
    def blink_continue(self, delta):
        if self.continue_label_alpha == 255:
            self.continue_label_alpha = 0
        else:
            self.continue_label_alpha = 255
        self.continue_label.set_style('color', (96, 96, 96, self.continue_label_alpha))
        
    def finished_utterance(self, name, completed):
        self.lines = []
        if name == 'id':
            self.remove(self.arrow)
        elif name == 'phase1-done':
            self.continue_label_alpha = 255
            self.continue_label = text.Label("Press the spacebar to continue", font_size=48 * self.ratio,
                                            x=self.screen[0] / 2, y=24, font_name="Pipe Dream", color=(96, 96, 96, self.continue_label_alpha),
                                            anchor_x='center', anchor_y='bottom', batch=self.text_batch.batch)
            self.schedule_interval(self.blink_continue, .75)
            
            
    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            director.pop()
        elif symbol == key.SPACE:
            self.do_phase2()

        
class BackgroundLayer(Layer):
    
    def __init__(self):
        super(BackgroundLayer, self).__init__()
        self.screen = director.get_window_size()
        self.batch = BatchNode()
        self.add(self.batch)
        
        self.shapes = {"circle":"E",
                       "square":"K",
                       "oval":"F",
                       "diamond":"T",
                       "crescent":"Q",
                       "cross":"Y",
                       "star":"C",
                       "triangle":"A"}
        
        self.font = font.load('Cut Outs for 3D FX', 128)
        self.glyphs = self.font.get_glyphs("".join(self.shapes.values()))
        
        ratio = 1 - self.screen[1] / self.screen[0]
        n = int(750 * ratio)
        for _ in range(0, n):
            img = choice(self.glyphs).get_texture(True)
            img.anchor_x = 'center'
            img.anchor_y = 'center'
            max_o = 96
            o = choice([0, max_o])
            speed = uniform(1, 10)
            sprite = Shape(img, rotation=randrange(0, 365), scale=uniform(ratio, 3 * ratio),
                            position=(randrange(0, self.screen[0]), randrange(0, self.screen[1])),
                            opacity=o, color=(randrange(0, 256), randrange(0, 256), randrange(0, 256)))
            if o == max_o:
                sprite.do(Repeat(FadeTo(0, speed) + FadeTo(max_o, speed)))
            else:
                sprite.do(Repeat(FadeTo(max_o, speed) + FadeTo(0, speed)))
            self.batch.add(sprite)

class Probe(Label):
    
    def __init__(self, chunk, s, width, position, font_size):
        
        self.chunk = chunk
        
        cid = "%02d" % self.chunk[3]
        color = self.chunk[1].upper()
        shape = self.chunk[0].upper()
        size = self.chunk[2].upper()        

        self.color_visible = False
        self.shape_visible = False
        self.size_visible = False
        
        if s == 7:
            cues = []
        elif s == 6:
            cues = [color]
            self.color_visible = True
        elif s == 5:
            cues = [shape]
            self.shape_visible = True
        elif s == 4:
            cues = [size]
            self.size_visible = True
        elif s == 3:
            cues = [color, shape]
            self.color_visible = True
            self.shape_visible = True
        elif s == 2:
            cues = [color, size]
            self.color_visible = True
            self.size_visible = True
        elif s == 1:
            cues = [shape, size]
            self.shape_visible = True
            self.size_visible = True
        elif s == 0:
            cues = [color, shape, size]
            self.color_visible = True
            self.shape_visible = True
            self.size_visible = True
        shuffle(cues)
        cues = tuple(cues + [cid])
        
        template = '\n'.join(["%s"] * len(cues))
        html = template % (cues)
        super(Probe, self).__init__(html, position=position, multiline=True, width=width,
                                    anchor_x='center', anchor_y='center', align='center',
                                    color=(64, 64, 64, 255), font_name="Monospace", font_size=font_size)
        self.cshape = CircleShape(eu.Vector2(position[0], position[1]), width * .6)

class TaskBackground(Layer):
    
    def __init__(self):
        super(TaskBackground, self).__init__()
        self.screen = director.get_window_size()
        
    def new_trial(self, current_trial, total_trials):
        for c in self.get_children(): self.remove(c)
        if total_trials:
            self.trial_display = Label("%d of %d" % (current_trial, total_trials), position=(self.screen[0] - 10, 10), font_name='', font_size=18, bold=True, color=(128, 128, 128, 128), anchor_x='right')
        else:
            self.trial_display = Label("%d" % (current_trial), position=(self.screen[0] - 10, 10), font_name='', font_size=18, bold=True, color=(128, 128, 128, 128), anchor_x='right')
        self.add(self.trial_display)

class Task(ColorLayer, pyglet.event.EventDispatcher):
    
    d = Dispatcher()
    
    states = ["INIT", "CALIBRATE", "WAIT", "STUDY", "SEARCH", "RESULTS"]
    STATE_INIT = 0
    STATE_CALIBRATE = 1
    STATE_WAIT = 2
    STATE_STUDY = 3
    STATE_SEARCH = 4
    STATE_RESULTS = 5
    
    is_event_handler = True
    
    def __init__(self, client):
        self.screen = director.get_window_size()
        super(Task, self).__init__(168, 168, 168, 255, self.screen[1], self.screen[1])
        self.state = self.STATE_INIT
        self.client = client
        self.calibration_interval = 192
        self.circles = []
        
    def on_enter(self):
        if isinstance(director.scene, TransitionScene): return
        super(Task, self).on_enter()
        
        header = []
        
        if director.settings['mode'] == 'Experiment':
            header += ["datestamp", "encrypted_rin"]
            
        header += ["system_time", "mode", "trial", "state", "event_source", "event_type",
                   "event_id", "screen_width", "screen_height", "mouse_x", "mouse_y",
                   "study_time", "search_time"]
        
        if director.settings['eyetracker'] and self.client:
            self.smi_spl_header = ["smi_time", "smi_type",
                                   "smi_sxl", "smi_sxr", "smi_syl", "smi_syr",
                                   "smi_dxl", "smi_dxr", "smi_dyl", "smi_dyr",
                                   "smi_exl", "smi_exr", "smi_eyl", "smi_eyr", "smi_ezl", "smi_ezr"]
            header += self.smi_spl_header + ["smi_fx", "smi_fy"]
            
        self.logger = Logger(header)
        self.tarfile = tarfile.open('data/%s.tar.gz' % director.settings['filebase'], mode='w:gz')
              
        self.position = ((self.screen[0] - self.screen[1]) / 2, 0)
        self.cm = CollisionManagerBruteForce()
        self.mono = font.load("Mono", 32)
        self.shapes = {"oval":"F",
                       # "diamond":"T",
                       "crescent":"Q",
                       "cross":"Y",
                       "star":"C"}
        # star 83x79       1.05     2581/6557  .39
        # oval 55x83        .66     3427/4565  .75
        # crescent 51x77    .66     1580/3927  .40
        # cross 61x62       .98     1783/3782  .47
        # rect 46x73.       .63     3358/3358  1
        # cross2 57x84      .67     1532/4788  .31
        self.shape_mod = {"oval":[1.0, 1.0, 1.0],
                          # "diamond":"T",
                          "crescent":[1.07, 1.07, 1.07],
                          "cross":[1.15, 1.15, 1.15],
                          "star":[1.0, 1.0, 1.0]} 
        self.font = font.load('Cut Outs for 3D FX', 128)
        for shape in self.shapes:
            self.shapes[shape] = self.font.get_glyphs(self.shapes[shape])[0].get_texture(True)
        s = 50
        v = 100
        self.colors = {"red": hsv_to_rgb(0, s, v),
                       "yellow": hsv_to_rgb(72, s, v),
                       "green": hsv_to_rgb(144, s, v),
                       # "purple": hsv_to_rgb(288, s, v),
                       "blue": hsv_to_rgb(216, s, v)}
        self.side = self.screen[1] / 11
        self.ratio = self.side / 128
        self.scales = [self.ratio * 2, self.ratio * 1.25, self.ratio * .5]
        self.sizes = ["large", "medium", "small"]
        self.current_trial = 0
        self.ready_label = Label("Click mouse when ready!",
                                 position=(self.width / 2, self.height / 2),
                                 font_name='Pipe Dream', font_size=24,
                                 color=(0, 0, 0, 255), anchor_x='center', anchor_y='center')
        
        self.total_trials = None
        if director.settings['mode'] == 'Experiment':
            self.gen_trials()
            
        if director.settings['eyetracker']:
            self.state = self.STATE_CALIBRATE
            self.dispatch_event("start_calibration", self.calibration_ok, self.calibration_bad)
        else:
            self.next_trial()
            
    def calibration_ok(self):
        self.dispatch_event("stop_calibration")
        self.next_trial()
        
    def calibration_bad(self):
        self.dispatch_event("stop_calibration")
        self.logger.close(True)
        self.tarfile.close()
        director.scene.dispatch_event("show_intro_scene")
        
    def on_exit(self):
        if isinstance(director.scene, TransitionScene): return
        super(Task, self).on_exit()
        for c in self.get_children():
            self.remove(c)
    
    def next_trial(self):
        if self.current_trial == self.total_trials:
            self.logger.close(True)
            self.tarfile.close()
            director.scene.dispatch_event("show_intro_scene")
        else:
            self.search_time = -1
            self.study_time = -1
            director.window.set_mouse_visible(False)
            self.clear_shapes()
            self.log_extra = {'screen_width':self.screen[0],
                              'screen_height': self.screen[1]}
            if director.settings['mode'] == 'Experiment':
                self.log_extra['datestamp'] = director.settings['si']['timestamp']
                self.log_extra['encrypted_rin'] = director.settings['si']['encrypted_rin']
            self.state = self.STATE_WAIT
            self.current_trial += 1
            self.gen_combos()
            self.add(self.ready_label)
            self.logger.open(StringIO())
            self.logger.write(system_time=get_time(), mode=director.settings['mode'], trial=self.current_trial,
                              event_source="TASK", event_type=self.states[self.state], state=self.states[self.state],
                              event_id="START", **self.log_extra)
            self.dispatch_event("new_trial", self.current_trial, self.total_trials)
            if self.client:
                self.dispatch_event("show_headposition")
    
    def trial_done(self):
        t = get_time()
        self.search_time = t - self.start_time
        self.logger.write(system_time=t, mode=director.settings['mode'], trial=self.current_trial,
                          event_source="TASK", event_type=self.states[self.state], state=self.states[self.state],
                          event_id="END", **self.log_extra)
        self.state = self.STATE_RESULTS
        self.logger.write(system_time=t, mode=director.settings['mode'], trial=self.current_trial,
                          event_source="TASK", event_type=self.states[self.state], state=self.states[self.state],
                          study_time=self.study_time, search_time=self.search_time, **self.log_extra)
        
        tmp = self.logger.file.getvalue()
        data = tarfile.TarInfo("%s/trial-%02d.txt" % (director.settings['filebase'], self.current_trial))
        data.size = len(tmp)
        self.tarfile.addfile(data, StringIO(tmp))
        
        tmp = StringIO()
        screenshot().save(tmp, "png")
        data = tarfile.TarInfo("%s/trial-%02d.png" % (director.settings['filebase'], self.current_trial))
        data.size = len(tmp.getvalue())
        tmp.seek(0)
        self.tarfile.addfile(data, tmp)
        
        self.logger.close()
        if director.settings['eyetracker'] and self.client:
            self.client.removeDispatcher(self.d)
            self.client.stopFixationProcessing()
            if self.calibration_interval and self.current_trial % self.calibration_interval == 0:
                self.state = self.STATE_CALIBRATE
                self.dispatch_event("start_calibration", self.calibration_ok, self.calibration_bad)
            else:
                self.next_trial()
        else:
            self.next_trial()
        
    def gen_trials(self):
        self.trials = []
        for scale in self.sizes:
            for color in self.colors:
                for shape in self.shapes:
                    for c in range(0, 8):
                        self.trials.append([shape, color, scale, c])
        self.total_trials = len(self.trials)
        shuffle(self.trials)
        
    def gen_combos(self):
        ids = range(1, len(self.sizes) * len(self.colors) * len(self.shapes) + 1)
        shuffle(ids)
        self.combos = []
        for scale in self.sizes:
            for color in self.colors:
                for shape in self.shapes:
                    self.combos.append([shape, color, scale, ids.pop()])
        
    def gen_probe(self):
        for c in self.get_children():
            self.remove(c)
        s = 0
        if director.settings['mode'] == 'Experiment':
            trial = self.trials.pop()
            for c in self.combos:
                if c[0] == trial[0] and c[1] == trial[1] and c[2] == trial[2]:
                    chunk = c
                    s = trial[3]
                    break
        else:
            if director.settings['mode'] == 'Moderate':
                s = choice(range(0, 4))
            elif director.settings['mode'] == 'Hard':
                s = choice(range(0, 7))
            elif director.settings['mode'] == 'Insane':
                s = choice(range(0, 8))
            chunk = choice(self.combos)
        self.probe = Probe(chunk, s, self.side, (self.screen[1] / 2, self.screen[1] / 2), 14 * self.ratio)
        self.add(self.probe)
        
    def clear_shapes(self):
        self.circles = []
        self.cm.clear()
        for c in self.get_children():
            self.remove(c)
        self.batch = BatchNode()
        self.id_batch = BatchNode()
    
    def show_shapes(self):
        self.cm.add(self.probe)
        ratio = self.side / 128
        self.circles = []
        shapeinfo = {}
        shapeinfo['probe'] = {"id": self.probe.chunk[3],
                              "color": self.probe.color_visible,
                              "shape": self.probe.shape_visible,
                              "size": self.probe.size_visible}
        for c in self.combos:
            img = self.shapes[c[0]]
            img.anchor_x = 'center'
            img.anchor_y = 'center'
            sprite = Shape(img, chunk=c, rotation=randrange(0, 365), color=self.colors[c[1]], scale=self.shape_mod[c[0]][self.sizes.index(c[2])] * self.scales[self.sizes.index(c[2])])
            pad = sprite.radius
            sprite.set_position(uniform(pad, self.screen[1] - pad), uniform(pad, self.screen[1] - pad))
            while self.cm.objs_colliding(sprite):
                sprite.set_position(uniform(pad, self.screen[1] - pad), uniform(pad, self.screen[1] - pad))
            text.Label("%02d" % c[3], font_size=14 * ratio,
                       x=sprite.position[0], y=sprite.position[1],
                       font_name="Monospace", color=(32, 32, 32, 255),
                       anchor_x='center', anchor_y='center', batch=self.id_batch.batch)
            shapeinfo[c[3]] = {'shape':c[0], 'color':c[1], 'size':c[2], 'id': c[3],
                               'radius':sprite.cshape.r, 'x':sprite.position[0], 'y':sprite.position[1]}
            self.circles.append(Circle(sprite.position[0] + (self.screen[0] - self.screen[1]) / 2, sprite.position[1], width=2 * sprite.cshape.r))
            self.cm.add(sprite)
            self.batch.add(sprite)
        self.circles.append(Circle(self.probe.position[0] + (self.screen[0] - self.screen[1]) / 2, self.probe.position[1], width=2 * self.probe.cshape.r))
        self.add(self.batch, z=1)
        self.add(self.id_batch, z=2)
        s = StringIO(json.dumps(shapeinfo, sort_keys=True, indent=4))
        data = tarfile.TarInfo("%s/trial-%02d.json" % (director.settings['filebase'], self.current_trial))
        data.size = len(s.getvalue())
        s.seek(0)
        self.tarfile.addfile(data, s)
    
    if eyetracking:
        @d.listen('ET_FIX')
        def iViewXEvent(self, inResponse):
            eyedata = {}
            eyedata.update(self.log_extra)
            eyedata["smi_type"] = inResponse[0]
            eyedata["smi_time"] = inResponse[1]
            eyedata["smi_fx"] = inResponse[2]
            eyedata["smi_fy"] = inResponse[3]
            self.logger.write(system_time=get_time(), mode=director.settings['mode'], state=self.states[self.state], 
                              trial=self.current_trial, event_source="SMI", event_type="ET_FIX", **eyedata)
            
        @d.listen('ET_SPL')
        def iViewXEvent(self, inResponse):
            eyedata = {}
            eyedata.update(self.log_extra)
            for i, _ in enumerate(self.smi_spl_header):
                eyedata[self.smi_spl_header[i]] = inResponse[i]
            self.logger.write(system_time=get_time(), mode=director.settings['mode'], state=self.states[self.state], 
                              trial=self.current_trial, event_source="SMI", event_type="ET_SPL", **eyedata)
    # def draw(self):
    #    super(Task, self).draw()
    #    for c in self.circles: c.render()
        
    def on_mouse_press(self, x, y, buttons, modifiers):
        if self.state == self.STATE_CALIBRATE: return
        if self.state == self.STATE_WAIT:
            self.logger.write(system_time=get_time(), mode=director.settings['mode'], trial=self.current_trial,
                              event_source="TASK", event_type=self.states[self.state], state=self.states[self.state],
                              event_id="END", **self.log_extra)
            self.gen_probe()
            self.state = self.STATE_STUDY
            t = get_time()
            self.start_time = t
            self.logger.write(system_time=t, mode=director.settings['mode'], trial=self.current_trial,
                              event_source="TASK", event_type=self.states[self.state], state=self.states[self.state], 
                              event_id="START", **self.log_extra)
            if director.settings['eyetracker'] and self.client:
                self.dispatch_event("hide_headposition")
                self.client.addDispatcher(self.d)
                self.client.startFixationProcessing()
        elif self.state == self.STATE_SEARCH:
            self.logger.write(system_time=get_time(), mode=director.settings['mode'], trial=self.current_trial,
                              event_source="USER", event_type=self.states[self.state], state=self.states[self.state], 
                              event_id="MOUSE_PRESS", mouse_x=x, mouse_y=y, **self.log_extra)
            x, y = director.get_virtual_coordinates(x, y)
            for obj in self.cm.objs_touching_point(x - (self.screen[0] - self.screen[1]) / 2, y):
                if obj.chunk == self.probe.chunk:
                    self.trial_done()
        else:
            t = get_time()
            self.study_time = t - self.start_time
            self.logger.write(system_time=t, mode=director.settings['mode'], trial=self.current_trial,
                              event_source="TASK", event_type=self.states[self.state], state=self.states[self.state], 
                              event_id="END", **self.log_extra)
            self.show_shapes()
            window = director.window.get_size()
            nx = int(window[0] / 2)
            ny = int(window[1] / 2 - self.probe.cshape.r * .75 * (window[1] / self.screen[1]))
            t = get_time()
            self.start_time = t
            self.state = self.STATE_SEARCH
            self.logger.write(system_time=t, mode=director.settings['mode'], trial=self.current_trial,
                              event_source="TASK", event_type=self.states[self.state], state=self.states[self.state], 
                              event_id="START", **self.log_extra)
            self.logger.write(system_time=t, mode=director.settings['mode'], trial=self.current_trial,
                              event_source="TASK", event_type=self.states[self.state], state=self.states[self.state], 
                              event_id="MOUSE_RESET", mouse_x=nx, mouse_y=ny, **self.log_extra)
            director.window.set_mouse_position(nx, ny)
            director.window.set_mouse_visible(True)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.state == self.STATE_CALIBRATE: return
        if self.state == self.STATE_SEARCH:
            self.logger.write(system_time=get_time(), mode=director.settings['mode'], trial=self.current_trial,
                              event_source="USER", event_type=self.states[self.state], state=self.states[self.state], 
                              event_id="MOUSE_MOTION", mouse_x=x, mouse_y=y, **self.log_extra)
        
    def on_key_press(self, symbol, modifiers):
        if self.state == self.STATE_CALIBRATE: return
        if symbol == key.ESCAPE:
            self.logger.close(True)
            self.tarfile.close()
            director.scene.dispatch_event("show_intro_scene")
            True
            
class EyetrackerScrim(ColorLayer):
    
    def __init__(self):
        self.screen = director.get_window_size()
        super(EyetrackerScrim, self).__init__(0, 0, 0, 224, self.screen[0], self.screen[1])
        l = Label("Reconnecting to eyetracker...", position=(self.screen[0] / 2, self.screen[1] / 2), font_name='', font_size=32, bold=True, color=(255, 255, 255, 255), anchor_x='center', anchor_y='center')
        self.add(l)

class WilliamsEnvironment(object):
    
    title = "The Williams' Search Task"
        
    def __init__(self):
        
        if not os.path.exists("data"): os.mkdir("data")
        
        pyglet.resource.path.append('resources')
        pyglet.resource.reindex()
        pyglet.resource.add_font('Pipe_Dream.ttf')
        pyglet.resource.add_font('cutouts.ttf')
        
        p = pyglet.window.get_platform()
        d = p.get_default_display()
        s = d.get_default_screen()
        
        director.init(width=s.width, height=s.height,
                  caption=self.title, visible=False, resizable=True)
        director.window.set_size(int(s.width / 2), int(s.height / 2))
        
        director.window.pop_handlers()
        director.window.push_handlers(DefaultHandler())
        
        director.fps_display = clock.ClockDisplay(font=font.load('', 18, bold=True))
        director.set_show_FPS(True)
        director.window.set_fullscreen(True)
        
        if platform.system() != 'Windows':
            director.window.set_icon(pyglet.resource.image('logo.png'))
            cursor = director.window.get_system_mouse_cursor(director.window.CURSOR_HAND)
            director.window.set_mouse_cursor(cursor)
            
        director.settings = {'eyetracker': True,
                             'eyetracker_ip': '127.0.0.1',
                             'eyetracker_out_port': '4444',
                             'eyetracker_in_port': '5555',
                             'mode': 'Experiment',
                             'modes': ['Easy', 'Moderate', 'Hard', 'Insane', 'Experiment']}

        if eyetracking:
            self.client = iViewXClient(director.settings['eyetracker_ip'], int(director.settings['eyetracker_out_port']))
            self.listener = reactor.listenUDP(int(director.settings['eyetracker_in_port']), self.client)
        else:
            self.client = None
        
        # Intro scene and its layers        
        self.introScene = Scene()
                    
        self.mainMenu = MainMenu()
        self.optionsMenu = OptionsMenu()
        self.participantMenu = ParticipantMenu()
        self.introBackground = BackgroundLayer()
        self.eyetrackerScrim = EyetrackerScrim()
        
        self.introScene.add(self.introBackground)
        self.mplxLayer = MultiplexLayer(self.mainMenu, self.optionsMenu, self.participantMenu)
        self.introScene.add(self.mplxLayer, 1)
        
        self.introScene.register_event_type('start_task')
        self.introScene.register_event_type('eyetracker_info_changed')
        self.introScene.push_handlers(self)
        
        # Task scene and its layers
        self.taskScene = Scene()
        
        self.taskBackgroundLayer = TaskBackground()
        self.taskLayer = Task(self.client)
        if self.client:
            self.calibrationLayer = CalibrationLayer(self.client)
            self.calibrationLayer.register_event_type('show_headposition')
            self.calibrationLayer.register_event_type('hide_headposition')
            self.calibrationLayer.push_handlers(self)
            self.headpositionLayer = HeadPositionLayer(self.client)
        
        self.taskLayer.register_event_type('new_trial')
        self.taskLayer.push_handlers(self.taskBackgroundLayer)
        self.taskLayer.register_event_type('start_calibration')
        self.taskLayer.register_event_type('stop_calibration')
        self.taskLayer.register_event_type('show_headposition')
        self.taskLayer.register_event_type('hide_headposition')
        self.taskLayer.push_handlers(self)
        
        self.taskScene.add(self.taskBackgroundLayer)
        self.taskScene.add(self.taskLayer, 1)
        
        self.taskScene.register_event_type('show_intro_scene')
        self.taskScene.push_handlers(self)
            
        director.window.set_visible(True)
        
    def start_calibration(self, on_success, on_failure):
        self.calibrationLayer.on_success = on_success
        self.calibrationLayer.on_failure = on_failure
        self.taskScene.add(self.calibrationLayer, 2)
        
    def stop_calibration(self):
        self.taskScene.remove(self.calibrationLayer)
    
    def show_headposition(self):
        self.taskScene.add(self.headpositionLayer, 3)
        
    def hide_headposition(self):
        self.taskScene.remove(self.headpositionLayer)
        
    def eyetracker_listen(self, _):
        self.listener = reactor.listenUDP(int(director.settings['eyetracker_in_port']), self.client)
        self.introScene.remove(self.eyetrackerScrim)
        self.introScene.enable_handlers(True)
        
    def eyetracker_info_changed(self):
        if self.client.remoteHost != director.settings['eyetracker_ip'] or \
        self.client.remotePort != int(director.settings['eyetracker_out_port']):
            self.client.remoteHost = director.settings['eyetracker_ip']
            self.client.remotePort = int(director.settings['eyetracker_out_port'])
        else:
            self.introScene.add(self.eyetrackerScrim, 2)
            self.introScene.enable_handlers(False)
            d = self.listener.stopListening()
            d.addCallback(self.eyetracker_listen)
        
    def show_intro_scene(self):
        director.window.set_mouse_visible(True)
        self.mplxLayer.switch_to(0)
        director.replace(self.introScene)
        
    def start_task(self):
        director.window.set_mouse_visible(False)
        director.replace(SplitRowsTransition(self.taskScene))
                 
def main():
    williams = WilliamsEnvironment()
    williams.show_intro_scene()
    reactor.run()
