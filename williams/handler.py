import time

from pyglet.gl import *
from pyglet.window import key

from cocos.director import director

from PIL import Image

class DefaultHandler(object):
    def __init__(self):
        super(DefaultHandler, self).__init__()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.F and (modifiers & key.MOD_ACCEL):
            director.window.set_fullscreen(not director.window.fullscreen)
            return True

        elif symbol == key.X and (modifiers & key.MOD_ACCEL):
            director.show_FPS = not director.show_FPS
            return True

        elif symbol == key.S and (modifiers & key.MOD_ACCEL):
            window = director.get_window_size()
            buffer = (GLubyte * (3 * window[0] * window[1]))(0)
            glReadPixels(0, 0, window[0], window[1], GL_RGB, GL_UNSIGNED_BYTE, buffer)
            image = Image.fromstring(mode="RGB", size=(window[0], window[1]), data=buffer)     
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            image.save('screenshot-%d.png' % (int(time.time())))
            return True
