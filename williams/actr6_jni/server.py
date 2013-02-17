# -*- coding:    utf-8 -*-
#===============================================================================
# This file is part of ACTR6_JNI.
# Copyright (C) 2012 Ryan Hope <rmh3093@gmail.com>
#
# ACTR6_JNI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ACTR6_JNI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ACTR6_JNI.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory
import json

from clock import MPClock

class ACTR_Protocol(LineReceiver):

    def connectionMade(self):
        for d in self.factory.dispatchers:
            d.trigger(e="connectionMade", model=None, params=None)

    def connectionLost(self, reason):
        self.factory.clock.setTime(0.0)
        self.clearLineBuffer()
        for d in self.factory.dispatchers:
            d.trigger(e="connectionLost", model=None, params=None)

    def lineReceived(self, string):
        model, method, params = json.loads(string)
        if method == 'set-mp-time':
            self.factory.clock.setTime(float(params[0]))
            self.sendCommand(self.factory.model, "time-set")
        else:
            for d in self.factory.dispatchers:
                d.trigger(e=method, model=model, params=params)

    def sendCommand(self, model, method, *params):
        self.sendLine(json.dumps([model, method, params]))

class JNI_Server(Factory):

    ready = False
    running = True
    model = None
    
    clock = MPClock()

    def __init__(self, env):
        self.env = env
        self.dispatchers = []

    def addDispatcher(self, dispatcher):
        self.dispatchers.append(dispatcher)

    def buildProtocol(self, addr):
        self.p = ACTR_Protocol()
        self.p.factory = self
        return self.p

    def update_display(self, chunks, clear=False):
        visual_locations = "(define-chunks %s)" % " ".join([chunk.get_visual_location() for chunk in chunks])
        visual_objects = "(define-chunks %s)" % " ".join([chunk.get_visual_object() for chunk in chunks])
        self.p.sendCommand(self.model, "update-display", visual_locations, visual_objects, clear)
        
    def set_cursor_location(self, loc):
        self.p.sendCommand(self.model, "set-cursor-loc", loc)

    def digit_sound(self, digit):
        self.p.sendCommand(self.model, "new-digit-sound", digit)

    def tone_sound(self, freq, duration):
        self.p.sendCommand(self.model, "new-tone-sound", freq, duration)

    def word_sound(self, word):
        self.p.sendCommand(self.model, "new-word-sound", word)

    def other_sound(self, content, duration, delay, recode):
        self.p.sendCommand(self.model, "new-other-sound", content, duration, delay, recode)

    def trigger_reward(self, reward):
        self.p.sendCommand(self.model, "trigger-reward", reward)

    def set_visual_center_pint(self, (x, y)):
        self.p.sendCommand(self.model, "set-visual-center-point", x, y)

    def ready(self):
        self.p.sendCommand(self.model, "ready")
        
    def reset(self):
        self.p.sendCommand(self.model, "reset")

    def disconnect(self):
        self.p.sendCommand(self.model, "disconnect")
        print "disconnecting bitches"