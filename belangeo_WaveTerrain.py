#!/usr/bin/env python
# encoding: utf-8
"""
Created by belangeo on 2010-10-06.
"""
from pyo import *
import random, math

TITLE = 'Wave Terrain'
ARTIST = 'Olivier Bélanger'
DURATION = 360

s = Server(sr=44100, nchnls=2, buffersize=512, duplex=0, audio="offline").boot()
s.recordOptions(dur=DURATION, filename='radiopyo.ogg')

SIZE = 128
FREQS = [50.007,49.996,99.995,100.0074,150.005,150.0013,200.004,200.007]
AMPS = [.2,.2,.15,.15,.08,.08,.06,.06]
NUM = len(FREQS)

def getNumRand(mini, maxi, num=NUM):
    return [random.uniform(mini,maxi) for i in range(num)]
    
def terrain(size=256, freq=3, phase=16):
    xfreq = 2 * math.pi * freq
    return [[math.sin(xfreq * (j/float(size)) + math.sin(i/float(phase))) for j in range(size)] for i in range(size)]

m1 = NewMatrix(SIZE, SIZE, terrain(SIZE, 1, 4)).normalize()
m2 = NewMatrix(SIZE, SIZE, terrain(SIZE, 2, 8)).normalize()
m3 = NewMatrix(SIZE, SIZE, terrain(SIZE, 3, 12)).normalize()

mm = NewMatrix(SIZE, SIZE)
inter = Sine(.00278, 0, .5, .5)
morph = MatrixMorph(inter, mm, [m1,m2,m3])

# Bass
fadebass = Fader(fadein=30, fadeout=90, dur=360, mul=.05).play()
x2lfo = Sine(getNumRand(.005,.02, 2), mul=.2, add=.25)
y2lfo = Sine(getNumRand(.005,.02, 2), 0.5, mul=.2, add=.25)
x2 = Sine([24.75,24.81], 0, x2lfo, .5)
y2 = Sine(25, 0, y2lfo, .5)
a2 = MatrixPointer(mm, x2, y2, mul=fadebass)
a2dc = DCBlock(a2)
a2filt = Biquad(a2dc, freq=125).out()

# Mid
fademid = Fader(fadein=10, fadeout=90, dur=360, mul=.4).play()
xlfo = Sine(getNumRand(.005,.02), mul=.2, add=.25)
ylfo = Sine(getNumRand(.005,.02), 0.5, mul=.2, add=.25)
ylin = Linseg([(0,50), (360,100)], mul=getNumRand(.995,1.005)).play()
x = Sine(FREQS, 0, xlfo, .5)
y = Sine(ylin, 0, ylfo, .5)
a = MatrixPointer(mm, x, y, mul=AMPS)
adc = DCBlock(a)
apan = SPan(adc, outs=2, pan=[0,1,.1,.9,.2,.8,.3,.7,.4,.6]).mix(2)
afilt = EQ(apan, freq=1250, type=2)

# high
fadehigh = Fader(fadein=60, fadeout=60, dur=360, mul=.45).play()
l = [[(0,4000),(360,2000)],[(0,6000), (360,4000)],[(0,5000),(360,2500)],[(0,3000),(360,1500)]]
x1lin = Linseg(l[0], mul=getNumRand(.985,1.015)).play()
y1lin = Linseg([(0,10), (360,.1)], mul=getNumRand(.995,1.005)).play()
x1lfo = Sine(getNumRand(.01,.04), mul=.2, add=.25)
y1lfo = Sine(getNumRand(.01,.04), 0.5, mul=.2, add=.25)
x1 = Sine(x1lin, 0, x1lfo, .5)
y1 = Sine(y1lin, 0, y1lfo, .5)
a1ampmod = Sine(getNumRand(.005,.01), getNumRand(0,1), .5, .5)
a1 = MatrixPointer(mm, x1, y1, mul=a1ampmod*.01)
a1dc = DCBlock(a1)
a1pan = SPan(a1dc, outs=2, pan=[0,1,.125,.875,.25,.75,.375,.625]).mix(2)

out = afilt*fademid + a1pan*fadehigh
rev = WGVerb(Biquad(out, freq=6000), feedback=.9, cutoff=5000, bal=.35).out()

s.start()
#s.gui(locals())
