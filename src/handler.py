import time

from pyglet.gl import *
from pyglet.window import key

from cocos.director import director

from PIL import Image

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
            pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot-%d.png' % (int(time.time())))
            return True
