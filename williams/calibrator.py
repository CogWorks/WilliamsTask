from pyviewx.client import iViewXClient, Dispatcher

from cocos.director import director
from cocos.scene import Scene
from cocos.sprite import Sprite
from cocos.text import Label
from cocos.layer import ColorLayer
from cocos.actions.interval_actions import MoveTo, RotateBy
from cocos.actions.base_actions import Repeat


from pyglet import font, resource
from pyglet.window import key

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
        self.win_scale = (self.screen[0]/self.window[0], self.screen[1]/self.window[1])

        self.font = font.load('Cut Outs for 3D FX', 32)
        circle_img = self.font.get_glyphs("E")[0].get_texture(True)
        circle_img.anchor_x = 'center'
        circle_img.anchor_y = 'center'
        self.circle = Sprite(circle_img, color=(255,255,0))

        self.spinner = Sprite(resource.image('spinner.png'), position=(self.screen[0]/2, self.screen[1]/2), color=(255,255,255))
        
        self.client = iViewXClient(self.host, self.port, self.on_connection_refused)
        self.client.addDispatcher(self.d)

        self.init()
        
    def on_enter(self):
        super(CalibrationScene, self).on_enter()
        director.window.push_handlers(self)
        self.listener = self.reactor.listenUDP(5555, self.client)
        self.start()
        
    def on_connection_refused(self):
        self.state = self.STATE_REFUSED
        self.label = Label("Connection to iViewX server refused!", position=(self.screen[0]/2, self.screen[1]/2),
                           align='center', anchor_x='center', anchor_y='center', width=self.screen[0],
                           font_size=32, color=(255,255,255,255), font_name="Monospace", multiline=True)
        self.add(self.label)

    def on_exit(self):
        super(CalibrationScene, self).on_exit()
        director.window.remove_handlers(self)
        self.reset()
        self.listener.stopListening()

    def init(self):
        for c in self.get_children():
            c.stop()
            self.remove(c)
        self.calibrationPoints = [None] * 9
        self.calibrationResults = []
        self.circle.opacity = 0
        self.add(ColorLayer(0,0,255,255))
        self.add(self.circle)
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
                self.on_success()
        elif symbol == key.R:
            self.reset()
            self.start()
        elif symbol == key.ESCAPE:
            self.on_failure()

    @d.listen('ET_SPL')
    def iViewXEvent(self, inResponse):
        pass

    @d.listen('ET_CAL')
    def iViewXEvent(self, inResponse):
        pass

    @d.listen('ET_CSZ')
    def iViewXEvent(self, inResponse):
        pass

    @d.listen('ET_PNT')
    def iViewXEvent(self, inResponse):
        self.calibrationPoints[int(inResponse[0])-1] = (int(inResponse[1]), int(inResponse[2]))

    @d.listen('ET_CHG')
    def iViewXEvent(self, inResponse):
        currentPoint = int(inResponse[0]) - 1
        x = self.calibrationPoints[currentPoint][0] * self.win_scale[0]
        y = self.calibrationPoints[currentPoint][1] * self.win_scale[1]
        self.circle.opacity = 255
        if currentPoint == 0:
            self.circle.set_position(x,y)
        else:
            self.circle.do(MoveTo((x,y), .5))

    @d.listen('ET_VLS')
    def iViewXEvent(self, inResponse):
        if self.state == self.STATE_VALIDATE:
            self.calibrationResults.append(' '.join(inResponse))
            if len(self.calibrationResults) == 2:
                self.remove(self.spinner)
                self.remove(self.label)
                text = '\n'.join(self.calibrationResults).decode("cp1252")
                text += "\n\n\nPress 'R' to recalibrate, spres 'Spacebar' to continue..."
                self.label = Label(text, position=(self.screen[0]/2, self.screen[1]/2),
                                   align='center', anchor_x='center', anchor_y='center', width=self.screen[0],
                                   font_size=32, color=(255,255,255,255), font_name="Monospace", multiline=True)
                self.add(self.label)

    @d.listen('ET_CSP')
    def iViewXEvent(self, inResponse):
        pass

    @d.listen('ET_FIN')
    def iViewXEvent(self, inResponse):
        self.state = self.STATE_VALIDATE
        self.remove(self.circle)
        self.add(self.spinner)
        self.spinner.do(Repeat(RotateBy(360, 1)))
        self.label = Label("CALCULATING CALIBRATION ACCURACY", position=(self.screen[0]/2, self.screen[1]/4*3),
                           font_size=32, color=(255,255,255,255), font_name="Monospace", anchor_x='center', anchor_y='center')
        self.add(self.label)
        self.client.requestCalibrationResults()
        self.client.validateCalibrationAccuracy()