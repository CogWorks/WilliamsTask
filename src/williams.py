#!/usr/bin/env python

from __future__ import division

import pygletreactor
pygletreactor.install()
from twisted.internet import reactor

from pyglet import image, font, text
from pyglet.gl import *
from pyglet.window import key

from cocos.director import *
from cocos.layer import *
from cocos.scene import *
from cocos.sprite import *
from cocos.menu import *
from cocos.text import *
from cocos.actions.interval_actions import *
from cocos.actions.base_actions import *
from cocos.actions.instant_actions import * 
from cocos.batch import BatchNode
from cocos.collision_model import *
import cocos.euclid as eu
from pyglet.media import StaticSource

from random import choice, randrange, uniform, sample, shuffle
import string

import colorsys

from primitives import Circle

def hsv_to_rgb(h, s, v):
    return tuple(map(lambda x: int(x * 255), list(colorsys.hsv_to_rgb(h / 360., s / 100., v / 100.))))

class ExperimentHandler(object):
    def __init__(self):
        super(ExperimentHandler, self).__init__()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.F and (modifiers & key.MOD_ACCEL):
            director.window.set_fullscreen(not director.window.fullscreen)
            return True

        elif symbol == key.X and (modifiers & key.MOD_ACCEL):
            director.show_FPS = not director.show_FPS
            return True

        elif symbol == key.S and (modifiers & key.MOD_ACCEL):
            import time
            pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot-%d.png' % (int(time.time())))
            return True

class BetterMenu(Menu):
    
    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.on_quit()
            return True
        elif symbol in (key.ENTER, key.NUM_ENTER):
            self._activate_item()
            return True
        elif symbol in (key.DOWN, key.UP):
            if symbol == key.DOWN:
                mod = 1
            elif symbol == key.UP:
                mod = -1
            new_idx = (self.selected_index + mod) % len(self.children)
            while self.children[ new_idx ][1].visible == False:
                new_idx = (new_idx + mod) % len(self.children)
            self._select_item(new_idx)
            return True
        else:
            ret = self.children[self.selected_index][1].on_key_press(symbol, modifiers)
            if ret and self.activate_sound:
                self.activate_sound.play()
            return ret

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
        
        self.items = []
        
        self.items.append(ToggleMenuItem('Show FPS:', self.on_show_fps, director.show_FPS))
        self.items.append(ToggleMenuItem('Fullscreen:', self.on_fullscreen, director.window.fullscreen))
        self.items.append(ToggleMenuItem("EyeTracker:", self.on_eyetracker, self.settings['eyetracker']))
        self.items.append(EntryMenuItem('EyeTracker IP:', self.on_eyetracker_ip, self.settings['eyetracker_ip']))
        self.items.append(EntryMenuItem('EyeTracker Port:', self.on_eyetracker_port, self.settings['eyetracker_port']))
        self.set_eyetracker_extras(self.settings['eyetracker'])
        
        self.create_menu(self.items, zoom_in(), zoom_out())
        
    def on_show_fps(self, value):
        director.show_FPS = value
        
    def on_fullscreen(self, value):
        screen = pyglet.window.get_platform().get_default_display().get_default_screen()
        director.window.set_fullscreen(value, screen)
    
    def on_experiment(self, value):
        self.settings['experiment'] = value
    
    def set_eyetracker_extras(self, value):
        self.items[3].visible = value
        self.items[4].visible = value
        
    def on_eyetracker(self, value):
        self.settings['eyetracker'] = value
        self.set_eyetracker_extras(value)
        
    def on_eyetracker_ip(self, ip):
        self.settings['eyetracker_ip'] = ip
    
    def on_eyetracker_port(self, port):
        self.settings['eyetracker_port'] = port
            
    def on_quit(self):
        self.parent.switch_to(0)

class GhostMenuItem(MenuItem):
    def __init__(self):
        super(GhostMenuItem, self).__init__('', lambda: _)
        self.visible = False

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

        self.items = []
        
        self.items.append(MultipleMenuItem('Mode: ', self.on_mode, self.settings['modes']))
        self.items.append(MenuItem('Start', self.on_start))
        self.items.append(MenuItem('Options', self.on_options))
        self.items.append(MenuItem('Quit', self.on_quit))
        
        self.create_menu(self.items, zoom_in(), zoom_out())

    def on_mode(self, mode):
         self.settings['mode'] = self.settings['modes'][mode]
        
    def on_options(self):
        self.parent.switch_to(1)
        
    def on_start(self):
        if self.settings['mode'] == "Experiment":
            self.parent.switch_to(2)
        else:
            scene = Scene()
            scene.add(Task(self.settings), z=0)
            director.push(scene)

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

        self.items = []
        
        self.items.append(EntryMenuItem('Full Name:', self.on_name, ""))
        self.items.append(EntryMenuItem('RIN:', self.on_rin, "", max_length=9))
        self.items.append(MenuItem('Start', self.on_start))
    
        
        self.create_menu(self.items, zoom_in(), zoom_out())
        
    def on_name(self, name):
        print "on_name", name
        
    def on_rin(self, rin):
        try:
            int(rin, 10)
        except ValueError:
            self.items[1].do(shake() + shake_back())
            self.items[1].value = rin[:-1]
        
    def on_start(self):
        scene = Scene()
        scene.add(Task(self.settings), z=0)
        director.push(scene)

    def on_quit(self):
        self.parent.switch_to(0)
        
class Shape(Sprite):

    def __init__(self, image, chunk=None, position=(0, 0), rotation=0, scale=1, opacity=255, color=(255, 255, 255)):
        super(Shape, self).__init__(image, rotation=rotation, scale=scale, opacity=opacity, color=color)
        self.chunk = chunk
        self.set_position(position[0], position[1])
        self.on_enter_action = None
    
    def set_position(self, x, y):
        self.cshape = CircleShape(eu.Vector2(x, y), max(self.width, self.height) * .55)
        super(Shape, self).set_position(self.cshape.center[0], self.cshape.center[1])
        
    def on_enter(self):
        super(Shape, self).on_enter()
        if self.on_enter_action: self.do(self.on_enter_action)
        
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
                sprite.on_enter_action = Repeat(FadeTo(0, speed) + FadeTo(max_o, speed))
            else:
                sprite.on_enter_action = Repeat(FadeTo(max_o, speed) + FadeTo(0, speed))
            self.batch.add(sprite)

class Probe(Label):
    
    def __init__(self, mode, id, color, shape, size, width, position, font_size):
        if mode == 'Easy':
            s = 3
        elif mode == 'Moderate':
            s = choice([2, 3])
        elif mode == 'Hard':
            s = choice([1, 2, 3])
        elif mode == 'Insane':
            s = choice([0, 1, 2, 3])
        else: #Experiment mode needs fixing
            s = choice([0, 1, 2, 3])
        cues = tuple(sample([color, shape, size], s) + [id])
        template = '\n'.join(["%s"] * len(cues))
        html = template % (cues)
        super(Probe, self).__init__(html, position=position, anchor_x='center', anchor_y='center',
                                    multiline=True, width=width, height=width, align='center',
                                    color=(64, 64, 64, 255), font_name="Monospace", font_size=font_size)
        self.cshape = CircleShape(eu.Vector2(position[0], position[1]), width * .6)

class Task(ColorLayer):
    
    is_event_handler = True
    
    def __init__(self, settings):
        self.settings = settings
        self.screen = director.get_window_size()
        super(Task, self).__init__(168, 168, 168, 255, self.screen[1], self.screen[1])        
        xmin = (self.screen[0] - self.screen[1]) / 2
        self.position = (xmin, 0)
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
        self.shapes_visible = False
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
        self.gen_combos()
        self.gen_probe()
        self.batch = BatchNode()
        self.id_batch = BatchNode()
        director.window.set_mouse_visible(False)
        self.responding = False
        self.circles = []
        
    def gen_combos(self):
        ids = range(1, 76)
        shuffle(ids)
        self.combos = []
        for scale in self.scales:
            for color in self.colors:
                for shape in self.shapes:
                    self.combos.append([shape, color, scale, ids.pop()])
        
    def gen_probe(self):
        sizes = ["LARGE", "MEDIUM", "SMALL"]
        combo = choice(self.combos)
        print combo
        id = "%02d" % combo[3]
        color = combo[1].upper()
        shape = combo[0].upper()
        size = sizes[self.scales.index(combo[2])]
        self.probe = Probe(self.settings['mode'], id, color, shape, size, self.side, (self.screen[1] / 2, self.screen[1] / 2), 14 * self.ratio)
        self.add(self.probe)
        
    def clear_shapes(self):
        self.circles = []
        self.cm.clear()
        for c in self.get_children():
            self.remove(c)
        self.batch = BatchNode()
        self.id_batch = BatchNode()
        self.shapes_visible = False
        self.gen_combos()
        self.gen_probe()
        
    def show_shapes(self):
        self.cm.add(self.probe)
        self.shapes_visible = True
        ratio = self.side / 128
        sprites = 0
        resets = 0
        self.circles = []
        for c in self.combos:
            img = self.shapes[c[0]]
            img.anchor_x = 'center'
            img.anchor_y = 'center'
            sprite = Shape(img, chunk=c, rotation=randrange(0, 365), color=self.colors[c[1]], scale=c[2])
            pad = max(sprite.width, sprite.height) * .75
            sprite.set_position(uniform(pad, self.screen[1] - pad), uniform(pad, self.screen[1] - pad))
            while self.cm.objs_colliding(sprite):
                sprite.set_position(uniform(pad, self.screen[1] - pad), uniform(pad, self.screen[1] - pad))
            l = text.Label("%02d" % c[3], font_size=14 * ratio,
                            x=sprite.position[0], y=sprite.position[1],
                            font_name="Monospace", color=(32, 32, 32, 255),
                            anchor_x='center', anchor_y='center', batch=self.id_batch.batch)
            self.circles.append(Circle(sprite.position[0] + (self.screen[0] - self.screen[1]) / 2, sprite.position[1], width=2 * sprite.cshape.r))
            self.cm.add(sprite)
            self.batch.add(sprite)
        self.add(self.batch, z=1)
        self.add(self.id_batch, z=2)
        
    #def draw(self):
    #    super(Task, self).draw()
    #    for c in self.circles:
    #        c.render()
        
    def on_mouse_press(self, x, y, buttons, modifiers):
        print x, y,
        x, y = director.get_virtual_coordinates(x, y)
        print x, y
        for obj in self.cm.objs_touching_point(x - (self.screen[0] - self.screen[1]) / 2, y):
            print obj.chunk

    def on_mouse_motion(self, x, y, dx, dy):
        if self.shapes_visible and not self.responding:
            director.window.set_mouse_position(self.screen[0] / 2, self.screen[1] / 2)
            director.window.set_mouse_visible(True)
            self.responding = True
        
    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            if not self.shapes_visible:
                self.show_shapes()
                self.responding = False
            else:
                self.clear_shapes()
                director.window.set_mouse_visible(False)
        elif symbol == key.D:
            print director.scene_stack, director.scene, director.next_scene
        elif symbol == key.P:
            director.pop()
                 
def main():
    screen = pyglet.window.get_platform().get_default_display().get_default_screen()
    
    pyglet.resource.path.append('resources')
    pyglet.resource.reindex()
    font.add_directory('resources')
    
    settings = {'eyetracker': False,
                'eyetracker_ip': '127.0.0.1',
                'eyetracker_port': '5555',
                'mode': 'Easy',
                'modes': ['Easy', 'Moderate', 'Hard', 'Insane', 'Experiment']}
    
    director.init(width=screen.width, height=screen.height,
                  caption="The Williams' Search Task",
                  visible=False, resizable=True)
    director.window.set_icon(pyglet.resource.image('logo.png'))
    
    director.window.set_size(screen.width / 2, screen.height / 2)
    director.window.set_fullscreen(True, screen)

    director.window.pop_handlers()
    director.window.push_handlers(ExperimentHandler())
    
    director.set_show_FPS(True)
    
    scene = Scene()
    scene.add(MultiplexLayer(
                        MainMenu(settings),
                        OptionsMenu(settings),
                        ParticipantMenu(settings),
                    ), z=0)
    
    scene.add(BackgroundLayer(), z= -1)
    
    cursor = director.window.get_system_mouse_cursor("hand")
    director.window.set_mouse_cursor(cursor)
    director.window.set_visible(True)
    
    director.replace(scene)
    
    reactor.run()

if __name__ == '__main__':
    main()
