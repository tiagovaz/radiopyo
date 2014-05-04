#!/usr/bin/python2
# -*- coding: utf-8 -*-

from pyo import *
import random

ARTIST = 'Olivier Bélanger'
TITLE = 'Transparence'
DURATION = 170

s = Server(sr=44100, nchnls=2, buffersize=1024, duplex=0, audio="offline").boot()
s.recordOptions(dur=DURATION, filename='radiopyo.ogg')

fade = Fader(fadein=1, fadeout=20, dur=DURATION-5).play()

accents = [[1,0,.5,.3,.8,0,.5,0,1,0,.5,.3,.8,0,.9,.9],
           [1,0,.5,0,.8,0,.5,0,1,0,.5,0,.8,.4,0,.9],
           [1,.5,.5,.3,.8,.3,0,0,1,0,.5,.3,.8,0,.9,0]]

snd = SndTable(SNDS_PATH+'/transparent.aif')
sndlen = snd.getSize()

samps = []
for i in range(sndlen):
    samps.append(snd.get(i))
for j in range(10):
    sampslen = len(samps)
    hsampslen = sampslen/2
    tmp = []
    for i in range(sampslen+hsampslen):
        if i < hsampslen:
            tmp.append(samps[i])
        elif i < sampslen:
            tmp.append((samps[i] + samps[i-hsampslen])*0.5)
        else:
            tmp.append(samps[i-hsampslen])
    samps = [x for x in tmp]

snd2 = DataTable(size=len(samps), init=samps)

###############################################################
### BEAT ###
met = Metro(.12, 16)
env = LinTable([(0,0), (100,1), (150,1), (500,.25), (1000,.1), (8191,0)])
trig = TrigEnv(met, env, dur=.35, mul=accents[0])
outs = Osc(snd2, [-snd2.getRate()*random.uniform(.1,.2) for i in range(16)], 
               [i/16. for i in range(16)], 4, trig*fade)
outs2 = outs.mix(4)
outs3 = Compress(outs2*1.25, thresh=-12, ratio=3, risetime=.003, falltime=.02).out(-1)

###############################################################
### DISTO ###
dist_tab = HarmTable([1,0,.33,0,.2,0,.143,0,.111])
dist_fade = Fader(.025, .5, 2, mul=.125)
dist_del = Delay(outs3, [.12,.24,.36,.48], .5, 1, .7)
dist_lfo_lfo = Sine([random.uniform(.1,.2) for i in range(4)], 0, [random.uniform(.25,.75) for i in range(4)], 1)
dist_lfo = Osc(dist_tab, dist_lfo_lfo, 0, 2, .1495, .85)
dist = Disto(dist_del, dist_lfo, .5, dist_fade).out()

###############################################################
### VAGUES ###
rui = BrownNoise(1)
fader = Fader(5, 20, mul=.04)
rui_amp = Sine([random.uniform(.25, .5) for i in range(12)], 0, fader, fader)
rui_q = Sine(.05, 0, 25.5, 26)
bands = BandSplit(rui, 12, 200, 6000, rui_q, rui_amp).out()

###############################################################
### BASSE ###
env2 = LinTable([(0,0), (10,1), (30,1), (75,.4), (200,.25), (8191,0)])
trig2 = TrigEnv(met[0], env2, dur=1.9, mul=.25)
basse1 = Biquad(rui, 80, 15, 0, trig2).out(0)
basse2 = Biquad(rui, 90, 15, 0, trig2).out(1)

###############################################################
### HIGH ###
high_fade = Fader(20, 20, mul=.0006)
high_lfo = Sine([random.uniform(.1,.4) for i in range(8)], 0, high_fade, high_fade)
high_lfo2 = Sine([random.uniform(6,10) for i in range(8)], 0, .5, .5)
high_notes = Sine([random.uniform(3000,8000) for i in range(8)], 0, high_lfo*high_lfo2).out()

###############################################################
### CONTROLS ###
inc = .1
def pat():
    global inc
    if inc >= .9:
        inc = .2
        trig.mul = random.choice(accents)
    else:
        inc += .025
    outs.freq = [-snd2.getRate()*random.uniform(.1, inc) for i in range(16)]
    #secondes += 1
       
p = Pattern(pat, .93)

def vague(x=1):
    if x: fader.play()
    else: fader.stop() 
       
def go(x=1):
    global inc
    if x:
        inc = .1
        p.play()
        met.play()
    else:
        p.stop()
        met.stop()    

def high(x=1):
    if x: high_fade.play()
    else: high_fade.stop() 
        
def disto():
    dist_fade.play()

secondes2 = -5
def score():
    global secondes2
    secondes2 += 5
    if secondes2 == 15:
        go()
    elif secondes2 == 45:
        high()
    elif secondes2 > 45 and secondes2 < 120:
        if random.randint(0, 2) == 0:
            disto()
    elif secondes2 == 125:
        vague(0)
    elif secondes2 == 140:
        high(0)
    elif secondes2 == 165:
        go(0)
        pp.stop()


pp = Pattern(score, 5).play()

vague()

s.start()
#s.gui(locals())
