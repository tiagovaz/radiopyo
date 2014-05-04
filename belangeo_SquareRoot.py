#!/usr/bin/python2
# encoding: utf-8

from pyo import *
import random

ARTIST = 'Olivier Bélanger'
TITLE = 'SquareRoot'
DURATION = 150

s = Server(audio='offline').boot()
s.recordOptions(dur=DURATION, filename='radiopyo.ogg')

fade = Fader(fadein=2, fadeout=10, dur=DURATION, mul=.35).play()

table = SquareTable(40)

q = Sine(.05, 0, 5, 8)
line = Linseg([(0,1),(20,1),(40,2),(60,2),(90,3),(120,3),(150,1)]).play()
line2 = Linseg([(0,1),(90,3),(180,1)]).play()
freq = Randh(min=line*2, max=line*9, freq=[.1,.18,.19,.16,.12,.15,.17,.2])
freq2 = Randh(min=line2*1, max=line*2, freq=[random.uniform(.1,.2) for i in range(8)])
amps = Osc(table, freq, mul=[.2,.18,.16,.14,.1,.06,.04,.03], add=[.2,.18,.16,.14,.1,.06,.04,.03])
dels = Osc(table, freq2, mul=.001, add=[random.uniform(.002, .01) for i in range(8)])
bands = BandSplit(Noise(fade), 8, 50, 7000, q, amps)
distomuls = RandInt(max=2, freq=[.03,.09,.1,.05,.08,.04,.06,.07])
disto = Disto(bands, [.85,.9,.75,.85,.7,.8,.6,.7], .8, Port(distomuls))
distomix = disto.mix(2)
delays = Delay(disto, delay=dels, feedback=.5, maxdelay=.02)
delaysmix = delays.mix(2)
rev = WGVerb(distomix+delaysmix, feedback=.8, bal=.15, mul=.7).out()

sinemuls = RandInt(max=2, freq=[.03,.09,.1,.05,.08,.04,.06,.07], mul=.025)
sine = Sine(sorted([random.uniform(6000,12000) for i in range(8)]), mul=fade*sinemuls*amps).out()

bassamp = LFO(freq=.25, type=3, mul=.5, add=.5)
bass = LFO(freq=[30,40], sharp=0, type=3, mul=fade*bassamp*[.8,.55]).out()

s.start()
#s.gui(locals())
