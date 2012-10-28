from pyglet.window import key

from cocos.menu import Menu, MenuItem

class GhostMenuItem(MenuItem):
    
    def __init__(self):
        super(GhostMenuItem, self).__init__('', lambda: _)
        self.visible = False

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