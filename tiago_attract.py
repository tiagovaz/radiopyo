#!/usr/bin/env python
# encoding: utf-8

"""
'attract' is a music composition which plays with a Rossler attractor.

Copyright 2014 Tiago Bortoletto Vaz <tiago at acaia \. ca>

This code is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from pyo import *
import random
import sys

TITLE = 'attract v1.0'
ARTIST = 'Tiago Bortoletto Vaz'
DURATION = 216

s = Server(audio='offline').boot()
#s = Server(audio='jack').boot()

s.recordOptions(dur=DURATION, filename=sys.argv[1])

class DarkRoss():
    def __init__(self, fadein=.3, p2=None, chaos1=.4038, chaos2=.0769, feedback=.2, mul=1):
        self.r1 = Rossler(pitch=[.000001*random.uniform(0.99, 1.01) for i in range(4)], chaos=chaos1, stereo=True, mul=.9, add=.2).stop()
        self.r1.ctrl()
        self.r2 = Rossler(pitch=[.1*random.uniform(0.99, 1.01) for i in range(4)], chaos=chaos2, mul=self.r1 * .5).stop() # give p2 to pitch
        self.r2.ctrl()
        self.amp = Fader(fadein=fadein, fadeout=15).stop()
        self.rev = STRev(self.r2, roomSize=2, revtime=.8)
        self.rev.ctrl()
        self.feedback = feedback
        self.outsig= Delay(self.rev, delay=[.5,.1], feedback=self.feedback, mul=self.amp * mul).stop()

    def play(self):
        self.r1.play()
        self.r2.play()
        self.amp.play()
        self.outsig.out()

    def tail(self):
        self.amp.stop()

    def stop(self):
        self.r1.stop()
        self.r2.stop()
        self.outsig.stop()

class HighFreq():
    def __init__(self, freq=[11200, 11202], dur=.4, mul=.5):
        self.amp = Fader(fadein=.01, fadeout=.01, dur=dur, mul=mul)
        self.sine = SineLoop(freq=freq, mul=self.amp * .05).out()
        self.rev = Freeverb(self.sine, size=.84, damp=.87, bal=.9, mul=self.amp * .2).out()

    def setDur(self, dur):
        self.amp.dur = dur
        return self

    def play(self):
        self.amp.play()
        return self

    def stop(self):
        self.amp.stop()
        return self

    def getOut(self):
        return self.amp


class SmoothNoise():
    def __init__(self, dur=1.3, mul=.5):
        self.amp = Fader(fadein=.1, fadeout=.01, dur=dur, mul=mul)
        self.noise = PinkNoise(self.amp * .01).mix(2).out()

    def setDur(self, dur):
        self.amp.dur = dur
        return self

    def play(self):
        self.amp.play()
        return self

    def stop(self):
        self.amp.stop()
        return self

    def getOut(self):
        return self.amp

    def setInput(self, x, fadetime=.001):
        self.input.setInput(x, fadetime)

class MyPattern:
    """
    Instruments is a dict instrument:beats (pyoObj:[list of int])
    """
    def __init__(self, instruments={}, time=.25, beats=32):
        self.current_beat = 1
        self.time = time
        self.instruments = instruments
        self.beats = beats
        self.p = Pattern(self.pat, time).stop()

    def pat(self):
        for k, v in self.instruments.iteritems():
            if self.current_beat in v:
                k.play()
            if self.current_beat == self.beats:
                self.current_beat = 0
        self.current_beat += 1

    def play(self):
        self.p.play()

    def stop(self):
        self.p.stop()

snoise = SmoothNoise(mul=.15)
high = HighFreq(mul=.05)

mypat = MyPattern({high:[3, 30], snoise:[15, 31]}, time=.25, beats=64)

dark = DarkRoss(fadein=10)

time = -1

p0 = [.1,
      Randh(.1, .2, freq=Randh(.01, .1)),
      Randh(.3, .4, freq=Randh(.01, .1)),
      Randh(.01, .03, freq=1)
     ]

p1 = [.01966,
      Randh(.0955, .15, freq=Randh(.01, .1)),
      Randh(.01, .1, freq=Randh(.01, .1)),
      Randh(.3955, .6, freq=.01)
     ]

p2 = [.01966,
      Randh(.0955, .15, freq=Randh(.01, .99)),
      Randh(.01, .99, freq=Randh(.01, .99)),
      Randh(.3955, .6, freq=.01)
     ]

p3 = [Choice([.1, .5], freq=3),
      Randh(.0955, .15, freq=Randh(.8, .9)),
      Randh(.5, .99, freq=Randh(.1, .2)),
      Randh(.1955, .6, freq=.9 )
     ]

p4 = [Choice([.2, .3], freq=10),
      Randh(.0955, .15, freq=Randh(8, 9)),
      Randh(.5, .99, freq=Randh(1, 2)),
      Randh(.1955, .6, freq=9 )
     ]

def score():
    global time
    time += 1

    if time == 1:
        dark.r2.pitch = p0
        dark.play()

    if time == 30:
        dark.outsig.set("feedback", .9, port=20)
        dark.r2.pitch = p1

    if time == 50:
        dark.outsig.set("feedback", .0, port=20)
        mypat.play()
        dark.r2.pitch = p2

    if time == 100:
        dark.outsig.set("feedback", .2, port=10)
        dark.r2.pitch = p3
        dark.r2.chaos = Randi(0, .3, freq=.1)

    if time == 140:
        dark.outsig.set("feedback", .5, port=10)
        dark.r1.chaos = Randi(0, .7, freq=10)
        dark.r2.chaos = Randi(0, .3, freq=20)

    if time == 170:
        dark.r2.pitch = p4
        dark.r2.chaos = Randi(0, .5, freq=30)
        dark.r1.mul = .5 # needs to be float before using set() bellow
        dark.r1.set("mul", 0, 10)

    if time == 200:
        dark.tail()

    if time == 215:
        mypat.stop()

mainTime = Metro(time=1).play()
mainFunc = TrigFunc(mainTime, score)

s.start()
#s.gui(locals())
