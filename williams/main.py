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
from cocos.scene import *
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

import sys
sys.path.append("/System/Library/Frameworks/Python.framework/Versions/2.7/Extras/lib/python/PyObjC")
import pyttsx
engine = pyttsx.init()
engine.startLoop(False)
def pyttsx_iterate(dt):
    engine.iterate()

###
from util import hsv_to_rgb
from handler import DefaultHandler
from menu import BetterMenu, GhostMenuItem
###

from odict import OrderedDict

try:
    from pyviewx.client import iViewXClient, Dispatcher
    from calibrator import CalibrationLayer, HeadPositionLayer
    eyetracking = True
except ImportError:
    eyetracking = False
    
from pycogworks.logging import get_time, Logger

class OptionsMenu(BetterMenu):

    def __init__(self, settings):
        super(OptionsMenu, self).__init__('Options')
        self.screen = director.get_window_size()
        self.settings = settings
        
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
            self.items['eyetracker'] = ToggleMenuItem("EyeTracker:", self.on_eyetracker, self.settings['eyetracker'])
            self.items['eyetracker_ip'] = EntryMenuItem('EyeTracker IP:', self.on_eyetracker_ip, self.settings['eyetracker_ip'])
            self.items['eyetracker_port'] = EntryMenuItem('EyeTracker Port:', self.on_eyetracker_port, self.settings['eyetracker_port'])
            self.set_eyetracker_extras(self.settings['eyetracker'])
        
        self.create_menu(self.items.values(), zoom_in(), zoom_out())
        
    def on_show_fps(self, value):
        director.show_FPS = value
        
    def on_fullscreen(self, value):
        screen = pyglet.window.get_platform().get_default_display().get_default_screen()
        director.window.set_fullscreen(value, screen)
    
    def on_experiment(self, value):
        self.settings['experiment'] = value
    
    if eyetracking:
    
        def set_eyetracker_extras(self, value):
            self.items['eyetracker_ip'].visible = value
            self.items['eyetracker_port'].visible = value
            
        def on_eyetracker(self, value):
            self.settings['eyetracker'] = value
            self.set_eyetracker_extras(value)
            
        def on_eyetracker_ip(self, ip):
            self.settings['eyetracker_ip'] = ip
        
        def on_eyetracker_port(self, port):
            self.settings['eyetracker_port'] = port
            
    def on_quit(self):
        self.parent.switch_to(0)

class MainMenu(BetterMenu):

    def __init__(self, settings):
        super(MainMenu, self).__init__("The Williams' Search Task")
        self.screen = director.get_window_size()
        self.settings = settings
        
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
        
        self.items['mode'] = MultipleMenuItem('Mode: ', self.on_mode, self.settings['modes'], self.settings['modes'].index(self.settings['mode']))
        self.items['tutorial'] = MenuItem('Tutorial', self.on_tutorial)
        self.items['start'] = MenuItem('Start', self.on_start)
        self.items['options'] = MenuItem('Options', self.on_options)
        self.items['quit'] = MenuItem('Quit', self.on_quit)
        
        self.create_menu(self.items.values(), zoom_in(), zoom_out())

    def on_mode(self, mode):
         self.settings['mode'] = self.settings['modes'][mode]
    
    def on_tutorial(self):
        director.push(SplitColsTransition(Scene(TutorialLayer(self.settings))))
        
    def on_options(self):
        self.parent.switch_to(1)
        
    def on_start(self):
        if self.settings['mode'] == "Experiment":
            self.parent.switch_to(2)
        else:
            director.push(SplitRowsTransition(TaskScene(self.settings)))

    def on_quit(self):
        reactor.callFromThread(reactor.stop)
        
class ParticipantMenu(BetterMenu):

    def __init__(self, settings):
        super(ParticipantMenu, self).__init__("Participant Information")
        self.screen = director.get_window_size()
        self.settings = settings
        
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
        
        self.items['name'] = EntryMenuItem('Full Name:', self.on_name, "")
        self.items['rin'] = EntryMenuItem('RIN:', self.on_rin, "", max_length=9)
        self.items['start'] = MenuItem('Start', self.on_start)
        
        self.create_menu(self.items.values(), zoom_in(), zoom_out())
        
    def on_exit(self):
        super(ParticipantMenu, self).on_exit()
        for c in self.get_children(): self.remove(c)
                
    def on_name(self, name):
        print "on_name", name
        
    def on_rin(self, rin):
        try:
            int(rin, 10)
        except ValueError:
            self.items[1].do(shake() + shake_back())
            self.items[1].value = rin[:-1]
        
    def on_start(self):
        self.parent.switch_to(0)
        director.push(SplitRowsTransition(TaskScene(self.settings)))

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
        self.radius = max(self.width, self.height) * rscale
        self.set_position(position[0], position[1])
    
    def set_position(self, x, y):

        self.cshape = CircleShape(eu.Vector2(x, y), self.radius)
        super(Shape, self).set_position(self.cshape.center[0], self.cshape.center[1])

class TutorialLayer(ColorLayer):
    
    is_event_handler = True
    
    def __init__(self, settings):
        self.settings = settings
        self.screen = director.get_window_size()
        super(TutorialLayer, self).__init__(168, 168, 168, 255, self.screen[0], self.screen[1])
        
        self.side = self.screen[1] / 11
        self.ratio = self.side / 128
        self.scales = [self.ratio * 1.5, self.ratio, self.ratio * .5]
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
        
        self.transition = False
        self.phase = 0
        
    def do_phase1(self):
        self.phase = 1
        
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
        super(TutorialLayer, self).on_enter()
        self.schedule(pyttsx_iterate)
        self.token_fu = engine.connect('finished-utterance', self.finished_utterance)
        self.token_su = engine.connect('started-utterance', self.started_utterance)
        if self.transition and self.phase == 0:
            self.do_phase1()
        self.transition = True
        
    def on_exit(self):
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
            
            self.phase = 2
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
    
    def __init__(self, app, mode, width, position, font_size):
        
        s = 0
        
        if mode == 'Experiment':
            trial = app.trials.pop()
            if app.bg: app.bg.update(app.current_trial, app.total_trials)
            for c in app.combos:
                if c[0] == trial[0] and c[1] == trial[1] and c[2] == trial[2]:
                    self.chunk = c
                    s = trial[3]
                    break
        else:
            self.chunk = choice(app.combos)
        
        id = "%02d" % self.chunk[3]
        color = self.chunk[1].upper()
        shape = self.chunk[0].upper()
        size = self.chunk[2].upper()        

        if mode != 'Experiment':
            if mode == 'Moderate':
                s = choice(range(0, 4))
            elif mode == 'Hard':
                s = choice(range(0, 7))
            elif mode == 'Insane':
                s = choice(range(0, 8))

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
        cues = tuple(cues + [id])
        
        template = '\n'.join(["%s"] * len(cues))
        html = template % (cues)
        super(Probe, self).__init__(html, position=position, multiline=True, width=width,
                                    anchor_x='center', anchor_y='center', align='center',
                                    color=(64, 64, 64, 255), font_name="Monospace", font_size=font_size)
        self.cshape = CircleShape(eu.Vector2(position[0], position[1]), width * .6)

class TaskScene(Scene):
    
    def __init__(self, settings):
        super(TaskScene, self).__init__()
        self.settings = settings
        
        self.listener = None
        if eyetracking and self.settings['eyetracker']:
            self.client = iViewXClient(self.settings['eyetracker_ip'], int(self.settings['eyetracker_port']))
            self.cbl = CalibrationLayer(self.client, None)
            self.add(self.cbl, z=2)
            self.hpl = HeadPositionLayer(self.client)
            self.add(self.hpl, z=3)
        else:
            self.client = None
            self.hpl = None
            self.cbl = None
            
        self.tb = TaskBackground()
        self.add(self.tb, z=0)
        
        self.t = Task(self.settings, self.tb, self.client, self.cbl, self.hpl)
        self.add(self.t, z=1)
        
    def on_enter(self):
        super(TaskScene, self).on_enter()
        if self.client and not self.listener:
            self.listener = reactor.listenUDP(5555, self.client)
        
    def on_exit(self):
        super(TaskScene, self).on_exit()
        if self.listener:
            d = self.listener.stopListening()
            print d
            d = yield d
            print d
        

class TaskBackground(Layer):
    
    def __init__(self):
        super(TaskBackground, self).__init__()
        self.screen = director.get_window_size()
        
    def update(self, current_trial, total_trials):
        for c in self.get_children(): self.remove(c)
        self.trial_display = Label("%d of %d" % (current_trial, total_trials), position=(self.screen[0] - 10, 10), font_name='', font_size=18, bold=True, color=(128, 128, 128, 128), anchor_x='right')
        self.add(self.trial_display)

class Task(ColorLayer):
    
    d = Dispatcher()
    
    states = ["INIT","CALIBRATE","WAIT","STUDY","SEARCH","RESULTS"]
    STATE_INIT = 0
    STATE_CALIBRATE = 1
    STATE_WAIT = 2
    STATE_STUDY = 3
    STATE_SEARCH = 4
    STATE_RESULTS = 5
    
    is_event_handler = True
    
    def __init__(self, settings, bg=None, client=None, cbl=None, hpl=None):
        
        self.settings = settings
        
        header = ["system_time", "mode", "trial", "event_source", "event_type",
              "event_id", "mouse_x", "mouse_y", "study_time", "search_time",
              "probe_id", "probe_color", "probe_shape", "probe_size"]
        
        self.client = client
        self.cbl = cbl
        self.hpl = hpl
        if self.client:
            self.smi_spl_header = ["smi_time", "smi_type",
                                   "smi_sxl", "smi_sxr", "smi_syl", "smi_syr",
                                   "smi_dxl", "smi_dxr", "smi_dyl", "smi_dyr",
                                   "smi_exl", "smi_exr", "smi_eyl", "smi_eyr", "smi_ezl", "smi_ezr"]
            header += self.smi_spl_header
        
        for i in range(1, 76):
            header.append("shape%02d_color" % i)
            header.append("shape%02d_shape" % i)
            header.append("shape%02d_size" % i)
            header.append("shape%02d_radius" % i)
            header.append("shape%02d_x" % i)
            header.append("shape%02d_y" % i)
            
        self.logger = Logger(header, file="../test.dat")

        self.bg = bg
        self.screen = director.get_window_size()
        super(Task, self).__init__(168, 168, 168, 255, self.screen[1], self.screen[1])        
        self.position = ((self.screen[0] - self.screen[1]) / 2, 0)
        self.cm = CollisionManagerBruteForce()
        self.mono = font.load("Mono", 32)
        self.shapes = {"oval":"F",
                       "diamond":"T",
                       "crescent":"Q",
                       "cross":"Y",
                       "star":"C"}
        self.font = font.load('Cut Outs for 3D FX', 128)
        for shape in self.shapes:
            self.shapes[shape] = self.font.get_glyphs(self.shapes[shape])[0].get_texture(True)
        s = 50
        v = 100
        self.colors = {"red": hsv_to_rgb(0, s, v),
                       "yellow": hsv_to_rgb(72, s, v),
                       "green": hsv_to_rgb(144, s, v),
                       "blue": hsv_to_rgb(216, s, v),
                       "purple": hsv_to_rgb(288, s, v)}
        self.side = self.screen[1] / 11
        self.ratio = self.side / 128
        self.scales = [self.ratio * 1.5, self.ratio, self.ratio * .5]
        self.sizes = ["large", "medium", "small"]
        self.current_trial = 0
        self.ready_label = Label("Click mouse when ready!",
                                 position=(self.width / 2, self.height / 2),
                                 font_name='Pipe Dream', font_size=24,
                                 color=(0, 0, 0, 255), anchor_x='center', anchor_y='center')
        self.gen_trials()
        self.state = self.STATE_INIT
    
    def next_trial(self):
        self.search_time = -1
        self.study_time = -1
        director.window.set_mouse_visible(False)
        self.clear_shapes()
        self.log_extra = {}
        self.state = self.STATE_WAIT
        self.current_trial += 1
        self.gen_combos()
        self.add(self.ready_label)
        self.logger.write(system_time=get_time(), mode=self.settings['mode'], trial=self.current_trial,
                          event_source="TASK", event_type=self.states[self.state], event_id="START")
    
    def trial_done(self):
        t = get_time()
        self.search_time = t - self.start_time
        self.logger.write(system_time=t, mode=self.settings['mode'], trial=self.current_trial,
                          event_source="TASK", event_type=self.states[self.state], event_id="END", **self.log_extra)
        self.state = self.STATE_RESULTS
        self.logger.write(system_time=t, mode=self.settings['mode'], trial=self.current_trial,
                          event_source="TASK", event_type=self.states[self.state], study_time=self.study_time, search_time=self.search_time, **self.log_extra)
        if self.client:
            self.client.removeDispatcher(self.d)
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
        ids = range(1, 76)
        shuffle(ids)
        self.combos = []
        for scale in self.sizes:
            for color in self.colors:
                for shape in self.shapes:
                    self.combos.append([shape, color, scale, ids.pop()])
        
    def gen_probe(self):
        for c in self.get_children():
            self.remove(c)
        self.probe = Probe(self, self.settings['mode'], self.side, (self.screen[1] / 2, self.screen[1] / 2), 14 * self.ratio)
        self.add(self.probe)
        self.log_extra = {"probe_id": self.probe.chunk[3],
                     "probe_color": self.probe.color_visible,
                     "probe_shape": self.probe.shape_visible,
                     "probe_size": self.probe.size_visible}
        
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
        self.shape_log = {}
        for c in self.combos:
            img = self.shapes[c[0]]
            img.anchor_x = 'center'
            img.anchor_y = 'center'
            sprite = Shape(img, chunk=c, rotation=randrange(0, 365), color=self.colors[c[1]], scale=self.scales[self.sizes.index(c[2])])
            pad = sprite.radius
            sprite.set_position(uniform(pad, self.screen[1] - pad), uniform(pad, self.screen[1] - pad))
            while self.cm.objs_colliding(sprite):
                sprite.set_position(uniform(pad, self.screen[1] - pad), uniform(pad, self.screen[1] - pad))
            text.Label("%02d" % c[3], font_size=14 * ratio,
                       x=sprite.position[0], y=sprite.position[1],
                       font_name="Monospace", color=(32, 32, 32, 255),
                       anchor_x='center', anchor_y='center', batch=self.id_batch.batch)
            self.shape_log["shape%02d_color" % c[3]] = c[1]
            self.shape_log["shape%02d_shape" % c[3]] = c[0]
            self.shape_log["shape%02d_size" % c[3]] = c[2]
            self.shape_log["shape%02d_radius" % c[3]] = sprite.cshape.r
            self.shape_log["shape%02d_x" % c[3]] = sprite.position[0]
            self.shape_log["shape%02d_y" % c[3]] = sprite.position[1]
            self.circles.append(Circle(sprite.position[0] + (self.screen[0] - self.screen[1]) / 2, sprite.position[1], width=2 * sprite.cshape.r))
            self.cm.add(sprite)
            self.batch.add(sprite)
        self.circles.append(Circle(self.probe.position[0] + (self.screen[0] - self.screen[1]) / 2, self.probe.position[1], width=2 * self.probe.cshape.r))
        self.add(self.batch, z=1)
        self.add(self.id_batch, z=2)
        self.log_extra.update(self.shape_log)
    
    if eyetracking:
        @d.listen('ET_SPL')
        def iViewXEvent(self, inResponse):
            eyedata = {}
            for i, _ in enumerate(self.smi_spl_header):
                eyedata[self.smi_spl_header[i]] = inResponse[i]
            #eyedata.update(self.log_extra)
            self.logger.write(system_time=get_time(), mode=self.settings['mode'], trial=self.current_trial, event_source="SMI", **eyedata)
        
    # def draw(self):
    #    super(Task, self).draw()
    #    for c in self.circles: c.render()
        
    def on_mouse_press(self, x, y, buttons, modifiers):
        if self.state != self.STATE_CALIBRATE:
            if self.state == self.STATE_WAIT:
                self.logger.write(system_time=get_time(), mode=self.settings['mode'], trial=self.current_trial,
                                  event_source="TASK", event_type=self.states[self.state], event_id="END")
                self.gen_probe()
                self.state = self.STATE_STUDY
                t = get_time()
                self.start_time = t
                self.logger.write(system_time=t, mode=self.settings['mode'], trial=self.current_trial,
                                  event_source="TASK", event_type=self.states[self.state], event_id="START", **self.log_extra)
                if self.client:
                    self.client.addDispatcher(self.d)
            elif self.state == self.STATE_SEARCH:
                x, y = director.get_virtual_coordinates(x, y)
                for obj in self.cm.objs_touching_point(x - (self.screen[0] - self.screen[1]) / 2, y):
                    if obj.chunk == self.probe.chunk:
                        self.trial_done()
            else:
                t = get_time()
                self.study_time = t - self.start_time
                self.logger.write(system_time=t, mode=self.settings['mode'], trial=self.current_trial,
                                  event_source="TASK", event_type=self.states[self.state], event_id="END", **self.log_extra)
                self.show_shapes()
                window = director.window.get_size()
                nx = int(window[0] / 2)
                ny = int(window[1] / 2 - self.probe.cshape.r * .75 * (window[1] / self.screen[1]))
                t = get_time()
                self.start_time = t
                self.state = self.STATE_SEARCH
                self.logger.write(system_time=t, mode=self.settings['mode'], trial=self.current_trial,
                                  event_source="TASK", event_type=self.states[self.state], event_id="START", **self.log_extra)
                self.logger.write(system_time=t, mode=self.settings['mode'], trial=self.current_trial,
                                  event_source="TASK", event_type=self.states[self.state], event_id="MOUSE_RESET", mouse_x=nx, mouse_y=ny, **self.log_extra)
                director.window.set_mouse_position(nx, ny)
                director.window.set_mouse_visible(True)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.state == self.STATE_SEARCH:
            self.logger.write(system_time=get_time(), mode=self.settings['mode'], trial=self.current_trial,
                              event_source="USER", event_type=self.states[self.state], event_id="MOUSE_MOTION", mouse_x=x, mouse_y=y, **self.log_extra)
        
    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            director.pop()
            True
            
    def on_enter(self):
        super(Task, self).on_enter()
        if self.state == self.STATE_INIT:
            if self.client:
                self.state = self.STATE_CALIBRATE
                self.cbl.on_success = self.next_trial
                self.cbl.on_failure = director.pop
                self.add(self.cbl)
            else:
                self.next_trial()    
                 
def main():
    engine = pyttsx.init()
    
    screen = pyglet.window.get_platform().get_default_display().get_default_screen()
    
    pyglet.resource.path.append('resources')
    pyglet.resource.reindex()
    
    pyglet.resource.add_font('Pipe_Dream.ttf')
    pyglet.resource.add_font('cutouts.ttf')
    
    settings = {'eyetracker': True,
                'eyetracker_ip': '127.0.0.1',
                'eyetracker_port': '4444',
                'mode': 'Experiment',
                'modes': ['Easy', 'Moderate', 'Hard', 'Insane', 'Experiment']}
    
    director.init(width=screen.width, height=screen.height,
                  caption="The Williams' Search Task",
                  visible=False, resizable=True)

    if platform.system() != 'Windows':
        director.window.set_icon(pyglet.resource.image('logo.png'))
        cursor = director.window.get_system_mouse_cursor(director.window.CURSOR_HAND)
        director.window.set_mouse_cursor(cursor)
    
    director.window.set_size(int(screen.width / 2), int(screen.height / 2))
    # director.window.set_fullscreen(True)

    director.window.pop_handlers()
    director.window.push_handlers(DefaultHandler())
    
    director.fps_display = clock.ClockDisplay(font=font.load('', 18, bold=True))
    director.set_show_FPS(True)
    
    scene = Scene()
    scene.add(MultiplexLayer(
                        MainMenu(settings),
                        OptionsMenu(settings),
                        ParticipantMenu(settings),
                    ), z=0)
    
    scene.add(BackgroundLayer(), z= -1)
    
    director.window.set_visible(True)
    
    director.replace(scene)
    
    reactor.run()
