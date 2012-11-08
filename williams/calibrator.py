from pyviewx.client import iViewXClient, Dispatcher

from cocos.director import director
from cocos.scene import Scene
from cocos.sprite import Sprite
from cocos.text import Label
from cocos.layer import ColorLayer, Layer
from cocos.actions.interval_actions import MoveTo, RotateBy
from cocos.actions.base_actions import Repeat


from pyglet import font, resource
from pyglet.window import key

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

class HeadPositionLayer(Layer):
    
    d = Dispatcher()
    
    def __init__(self, client):
        super(HeadPositionLayer, self).__init__()
        self.client = client
        
        self.screen = director.get_window_size()
        
        self.font = font.load('Cut Outs for 3D FX', 384)
        arrow1_img = self.font.get_glyphs("I")[0].get_texture(True)
        arrow1_img.anchor_x = 'center'
        arrow1_img.anchor_y = 'center'
        arrow2_img = self.font.get_glyphs("J")[0].get_texture(True)
        arrow2_img.anchor_x = 'center'
        arrow2_img.anchor_y = 'center'
        
        self.arrows = [Sprite(arrow1_img, position=(self.screen[0] / 2, self.screen[1] / 8 * 7), color=(255, 0, 0), opacity=0, scale=.75, rotation=270),
                       Sprite(arrow1_img, position=(self.screen[0] / 2, self.screen[1] / 8 * 7), color=(255, 0, 0), opacity=0, scale=.75, rotation=90),
                       Sprite(arrow1_img, position=(self.screen[0] / 8, self.screen[1] / 2), color=(255, 0, 0), opacity=0, scale=.75, rotation=0),
                       Sprite(arrow1_img, position=(self.screen[0] / 8 * 7, self.screen[1] / 2), color=(255, 0, 0), opacity=0, scale=.75, rotation=180),
                       Sprite(arrow2_img, position=(self.screen[0] / 2, self.screen[1] / 8), color=(255, 0, 0), opacity=0, scale=.75, rotation=90),
                       Sprite(arrow2_img, position=(self.screen[0] / 2, self.screen[1] / 8), color=(255, 0, 0), opacity=0, scale=.75, rotation=270)]
        
        for arrow in self.arrows:
            self.add(arrow)
            
        self.head = (0,0,0)
        
    def on_enter(self):
        super(HeadPositionLayer, self).on_enter()
        self.client.addDispatcher(self.d)
        
    def on_exit(self):
        super(HeadPositionLayer, self).on_exit()
        self.client.removeDispatcher(self.d)
        
    @d.listen('ET_SPL')
    def iViewXEvent(self, inResponse):
        eye_position = map(float, inResponse[10:])
        hx = clamp(round((eye_position[0] + eye_position[1]) / 2 / 99.999, 2), -1.0, 1.0)
        hy = clamp(round((eye_position[2] + eye_position[3]) / 2 / 99.999, 2), -1.0, 1.0)
        hz = clamp(round(((eye_position[4] + eye_position[5]) / 2 - 700) / 150.0, 2), -1.0, 1.0)
        
        self.head = (hx, hy, hz)
        
        if hy >= -.5 and hy <= .5:
            self.arrows[0].opacity = 0
            self.arrows[1].opacity = 0
        elif hy > .5:
            hy = (abs(hy) - .5) / .5
            self.arrows[0].opacity = 0
            self.arrows[1].opacity = 192
            yellow = (1 - hy) * 255
            self.arrows[1].color = (255, yellow, 0)
        elif hy < -.5:
            hy = (abs(hy) - .5) / .5
            self.arrows[0].opacity = 192
            self.arrows[1].opacity = 0
            yellow = (1 - hy) * 255
            self.arrows[0].color = (255, yellow, 0)
            
        if hx >= -.5 and hx <= .5:
            self.arrows[2].opacity = 0
            self.arrows[3].opacity = 0
        elif hx > .5:
            hx = (abs(hx) - .5) / .5
            self.arrows[2].opacity = 0
            self.arrows[3].opacity = 192
            yellow = (1 - hx) * 255
            self.arrows[3].color = (255, yellow, 0)
        elif hx < -.5:
            hx = (abs(hx) - .5) / .5
            self.arrows[2].opacity = 192
            self.arrows[3].opacity = 0
            yellow = (1 - hx) * 255
            self.arrows[2].color = (255, yellow, 0)
        
        if eye_position[4] != 0 and eye_position[5] != 0:
            if hz >= -.5 and hz <= .5:
                self.arrows[4].opacity = 0
                self.arrows[5].opacity = 0
            elif hz > .5:
                hz = (abs(hz) - .5) / .5
                self.arrows[4].opacity = 0
                self.arrows[5].opacity = 192
                yellow = (1 - hz) * 255
                self.arrows[5].color = (255, yellow, 0)
            elif hz < -.5:
                hz = (abs(hz) - .5) / .5
                self.arrows[4].opacity = 192
                self.arrows[5].opacity = 0
                yellow = (1 - hz) * 255
                self.arrows[4].color = (255, yellow, 0)
        
class CalibrationScene(Scene):
    
    d = Dispatcher()
    
    STATE_REFUSED = -1
    STATE_INIT = 0
    STATE_CALIBRATE = 1
    STATE_VALIDATE = 2
    STATE_DONE = 3

    def __init__(self, reactor, host, port, on_success, on_failure):
        super(CalibrationScene, self).__init__()
        self.reactor = reactor
        self.host = host
        self.port = port
        self.on_success = on_success
        self.on_failure = on_failure

        self.window = director.window.get_size()
        self.screen = director.get_window_size()
        self.center_x = self.screen[0] / 2
        self.center_y = self.screen[1] / 2
        self.win_scale = (self.screen[0] / self.window[0], self.screen[1] / self.window[1])

        self.font = font.load('Cut Outs for 3D FX', 32)
        circle_img = self.font.get_glyphs("E")[0].get_texture(True)
        circle_img.anchor_x = 'center'
        circle_img.anchor_y = 'center'
        
        self.circle = Sprite(circle_img, color=(255, 255, 0), scale=1)

        self.spinner = Sprite(resource.image('spinner.png'), position=(self.screen[0] / 2, self.screen[1] / 2), color=(255, 255, 255))
                
        self.client = iViewXClient(self.host, self.port, self.on_connection_refused)
        self.client.addDispatcher(self.d)
        
        self.hpl = HeadPositionLayer(self.client)

        self.init()
        
        director.window.set_mouse_visible(False)
        
    def on_enter(self):
        super(CalibrationScene, self).on_enter()
        director.window.push_handlers(self)
        self.listener = self.reactor.listenUDP(5555, self.client)
        self.start()
        
    def on_connection_refused(self):
        self.state = self.STATE_REFUSED
        self.label = Label("Connection to iViewX server refused!", position=(self.screen[0] / 2, self.screen[1] / 2),
                           align='center', anchor_x='center', anchor_y='center', width=self.screen[0],
                           font_size=32, color=(255, 255, 255, 255), font_name="Monospace", multiline=True)
        self.add(self.label)

    def cleanup(self):
        self.reset()
        self.listener.stopListening()

    def on_exit(self):
        super(CalibrationScene, self).on_exit()
        director.window.remove_handlers(self)

    def init(self):
        for c in self.get_children():
            c.stop()
            self.remove(c)
        self.ts = -1
        self.eye_position = None
        self.calibrationPoints = [None] * 9
        self.calibrationResults = []
        self.circle.opacity = 0
        self.add(ColorLayer(0, 0, 255, 255))
        self.add(self.circle)
        self.add(self.hpl)
        self.state = self.STATE_INIT
        
    def reset(self):
        if self.state > self.STATE_REFUSED:
            self.client.cancelCalibration()
            self.init()
        
    def start(self):
        if self.state > self.STATE_REFUSED:
            self.state = self.STATE_CALIBRATE
            self.client.setDataFormat('%TS %ET %SX %SY %DX %DY %EX %EY %EZ')
            self.client.startDataStreaming()
            self.client.setSizeCalibrationArea(self.window[0], self.window[1])
            self.client.setCalibrationParam(1, 1)
            self.client.setCalibrationParam(2, 0)
            self.client.setCalibrationParam(3, 1)
            self.client.setCalibrationCheckLevel(3)
            self.client.startCalibration(9, 0)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            if self.state == self.STATE_CALIBRATE and not self.circle.actions:
                self.client.acceptCalibrationPoint()
            elif self.state == self.STATE_DONE:
                self.cleanup()
                self.on_success()
        elif symbol == key.R:
            self.reset()
            self.start()
        elif symbol == key.ESCAPE:
            self.cleanup()
            self.on_failure()

    @d.listen('ET_CAL')
    def iViewXEvent(self, inResponse):
        pass

    @d.listen('ET_CSZ')
    def iViewXEvent(self, inResponse):
        pass

    @d.listen('ET_PNT')
    def iViewXEvent(self, inResponse):
        self.calibrationPoints[int(inResponse[0]) - 1] = (int(inResponse[1]), int(inResponse[2]))

    @d.listen('ET_CHG')
    def iViewXEvent(self, inResponse):
        currentPoint = int(inResponse[0]) - 1
        x = self.calibrationPoints[currentPoint][0] * self.win_scale[0]
        y = self.calibrationPoints[currentPoint][1] * self.win_scale[1]
        self.circle.opacity = 255
        if currentPoint == 0:
            self.circle.set_position(x, y)
        else:
            self.circle.do(MoveTo((x, y), .5))

    @d.listen('ET_VLS')
    def iViewXEvent(self, inResponse):
        if self.state == self.STATE_VALIDATE:
            self.calibrationResults.append(' '.join(inResponse))
            if len(self.calibrationResults) == 2:
                self.remove(self.spinner)
                self.remove(self.label)
                text = '\n'.join(self.calibrationResults).decode("cp1252")
                text += "\n\n\nPress 'R' to recalibrate, spres 'Spacebar' to continue..."
                self.label = Label(text, position=(self.screen[0] / 2, self.screen[1] / 2),
                                   align='center', anchor_x='center', anchor_y='center', width=self.screen[0],
                                   font_size=32, color=(255, 255, 255, 255), font_name="Monospace", multiline=True)
                self.add(self.label)
                self.state = self.STATE_DONE

    @d.listen('ET_CSP')
    def iViewXEvent(self, inResponse):
        pass

    @d.listen('ET_FIN')
    def iViewXEvent(self, inResponse):
        self.state = self.STATE_VALIDATE
        self.remove(self.hpl)
        self.remove(self.circle)
        self.add(self.spinner)
        self.spinner.do(Repeat(RotateBy(360, 1)))
        self.label = Label("CALCULATING CALIBRATION ACCURACY", position=(self.screen[0] / 2, self.screen[1] / 4 * 3),
                           font_size=32, color=(255, 255, 255, 255), font_name="Monospace", anchor_x='center', anchor_y='center')
        self.add(self.label)
        self.client.requestCalibrationResults()
        self.client.validateCalibrationAccuracy()
