#!/usr/bin/env python
# encoding: utf-8

"""
Scripted by Takmi Ikeda, 2012-01-11

"""

DURATION = 300
TITLE = 'ondes'
ARTIST = 'Takmi Ikeda [i9ed]'

from pyo import *
from random import uniform
import sys

s = Server(audio='offline', duplex=0).boot()
s.recordOptions(dur=DURATION, filename=sys.argv[1])

class BELL:
    def __init__(self):
        self.zz = 0

    def go(self):
        self.rt = random.random()**2*20
        self.tr = Cloud(uniform(self.rt, self.rt*4), 4).play()
        self.du = uniform(.01, 1.0/(self.rt*4))
        self.ev = TrigExpseg(self.tr, [(0,1), (self.du,0)], 4)
        self.ba = uniform(100, 5e3)
        self.fq = TrigRand(self.tr, self.ba, self.ba*1.5)
        self.oc = FM(self.fq, 3.5, self.ev, self.ev/3)
        self.fd = Fader(8, 8)
        self.xx = self.oc * self.fd
        self.yy = Delay(self.xx, .01, uniform(0, .8))
        self.zz = Selector([self.xx, self.yy], random.randint(0, 1))
        self.fd.play()
        self.zz.out()

    def stop(self):
        self.fd.stop()

class MELO:
    def __init__(self):
        self.zz = 0

    def go(self):
        self.tr = Cloud(1).play()
        self.ba = uniform(100, 1e3)
        self.fq = SigTo(TrigRand(self.tr, self.ba, self.ba*4), .5)
        self.am = SigTo(Randh(0, .2, 5), .1)
        self.oc = Sine(self.fq, 0, self.am)
        self.fd = Fader(8, 8)
        self.xx = self.oc * self.fd
        self.yy = Delay(self.xx, [.01, .0101], .97)
        self.zz = Compress(self.yy, -12, 64)
        self.fd.play()
        self.zz.out()

    def stop(self):
        self.fd.stop()

class WIND:
    def __init__(self):
        self.zz = 0

    def go(self):
        self.rt = SigTo(Randh(1, 8, 1), 2)
        self.tm = Sine(self.rt)
        self.nz = BrownNoise(self.tm)
        self.fq = SigTo(Randh(100, 500, 1), 1)
        self.bp = Biquad(self.nz, self.fq, 5, 2, 1.5)
        self.pn = SPan(self.bp, pan=self.tm/2)
        self.fd = Fader(8, 8)
        self.zz = self.pn * self.fd
        self.fd.play()
        self.zz.out()

    def stop(self):
        self.fd.stop()

   
a = [BELL(),BELL(),BELL(),WIND(),BELL(),MELO()]
b = len(a)
w = DURATION/10+1
v = w-4

i = 0
def foo():
    global i
    i += 1
    if i > b-1: a[((i+2)%b)].stop()
    if i < v: a[i%b].go()
    if i == w: s.stop()
    
m = Metro(10).play()
f = TrigFunc(m, foo)

s.start()


