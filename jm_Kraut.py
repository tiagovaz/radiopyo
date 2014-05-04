#!/usr/bin/env python
# encoding: utf-8
"""
Kraut.py

Created by jmdumas
"""

from pyo64 import *
from random import shuffle

TITLE = 'Kraut'
ARTIST = 'jmdumas'
DURATION = 180

s = Server(audio='offline').boot()
s.recordOptions(dur=DURATION, filename='radiopyo.ogg')

s.setStartOffset(0)
s.amp = 0.8

#KRAUTBEAT

krautbeat = Seq(time=0.3,seq=[2,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,3,2,2,2,2,2,1,1,1,6],poly=1)
krauttable = LinTable([(0,0.0000),(6,0.8325),(236,0.0000),(1417,0.0000),(8192,0.0000)])
krautenv = TrigEnv(krautbeat, table=krauttable, dur=1.5, mul=0.7).mix(1)
krautgen = PinkNoise()
krautfiltfreq = LFO(freq=1,type=6, mul=0.3, add=3500.7)
krautfilt = Biquad(krautgen, freq=krautfiltfreq, q=5, type=0, mul=krautenv)
krautfiltpan = SPan(krautfilt, pan=0.3)
krautdelmul = LFO(freq=2,type=6, mul=1)
krautdel = Delay(krautfilt,delay=0.751,feedback=0.5, mul=krautdelmul)
krautdelpan = SPan(krautdel, pan=0.7)
krautrevinput = krautdelpan+krautfiltpan
krautrev = WGVerb(krautrevinput, feedback=0.9, bal=0.03)

#BASS
selbass = Beat(time=0.15, taps=5, w1=90, w2=54, w3=37, poly=4)
beat1 = [5, 1, 1, 1, 1, 0]
beat2 = [5, 1, 0, 1, 1, 1]
beat3 = [5, 1, 0, 1, 1, 0]
beat4 = [5, 1, 1, 0, 1, 0]
selbass.setPresets([beat1,beat2,beat3,beat4])
selbass.recall(0)
selbassm = selbass.mix(1)
bass_scale = [38, 38, 41, 41, 45, 45, 48, 48, 52, 52, 55, 55]
random.shuffle(bass_scale)
shuffledbassscale = DataTable(size=len(bass_scale),init=[midiToHz(i) for i in bass_scale])
basscount = Counter(selbassm,min=0,max=len(bass_scale))
basspitch = TableIndex(shuffledbassscale, basscount)
bassmul = TrigLinseg(selbass,list=[(0,0.0000),(0.01,0.3),(0.5,0)],mul=selbass['amp']).mix(1)
bass = SineLoop([basspitch, basspitch/2], feedback=0.1, mul=bassmul*0.4).mix(1).mix(2)

#STRINGS
selstrings = Metro(2.5,poly=2)
selstrings2 = Percent(selstrings, percent=35)
STRINGS = {'car': 199, 'ratio': 0.5, 'index': [(0,0), (1.042,10.30854), (3.565,20.43354), (5,24)], 'mul': [(0,0), (2.568,0.859375), (3.577,0.28125), (5,0)]}
stringsindex = TrigLinseg(selstrings,list=STRINGS['index'])
stringsmul = TrigLinseg(selstrings,list=STRINGS['mul'])
fmbass = FM(basspitch,STRINGS['ratio'],stringsindex,stringsmul*0.2).mix(2)
fmbasschorus = Chorus(fmbass, mul=1.2)
fmbassdisto = Disto(fmbass, drive=0.9, mul=0.01).mix(2)
fmstringscount = TrigRandInt(selstrings2,max=len(bass_scale))
fmstringspitch = TableIndex(shuffledbassscale, fmstringscount)
fmstrings = FM(fmstringspitch*4,STRINGS['ratio'],stringsindex,stringsmul*0.1).mix(2)
fmstringschorus = Chorus(fmstrings, mul=1)
fmstringsdelay = Delay(fmstrings, delay=0.3, feedback=0.6)
#stringslow
jit = LFO(freq=0.005,type=1,sharp=0,add=0.01).play()
fmstringslow = FM(fmstringspitch,STRINGS['ratio']+jit,stringsindex,stringsmul*0.1).mix(2)
fmstringslow2 = FM(fmstringspitch*20,STRINGS['ratio']+jit,stringsindex,stringsmul*0.05).mix(2)
stringsfader = Pow(Fader(30,20),3)
fmstringschoruslow = Chorus(fmstringslow, feedback=0.25, mul=stringsfader)
fmstringschoruslow2 = Chorus(fmstringslow2, feedback=0.5, mul=stringsfader)
fmstringsdelaylow = Delay(fmstringslow, delay=0.35, feedback=0.6, mul=stringsfader)
fmstringsdelaylow2 = Delay(fmstringslow2, delay=0.4, feedback=0.8, mul=stringsfader)
fmstringslowverb = WGVerb(fmstringschoruslow+fmstringsdelaylow+fmstringschoruslow2+fmstringsdelaylow2,feedback=0.7,cutoff=6000,bal=1,mul=0.3)
sineenv = LFO(freq=2.5,type=1,sharp=0.9,add=0.01).play()
sinelow = SineLoop(fmstringspitch, feedback=jit*0.55, mul=stringsmul*sineenv*0.2).mix(1).mix(2)

temps = -1
def timecontrol():
    global temps
    temps += 1
    if temps == 0:
        fmstringschoruslow.out()
        fmstringschoruslow2.out()
        fmstringsdelaylow.out()
        fmstringsdelaylow2.out()
        fmstringslowverb.out()
        sinelow.out()
        selstrings.play()
        fmstringschorus.out()
        fmstringsdelay.out()
        krautbeat.play()
        krautrev.out()
        selbass.play()
        bass.out()
        fmbasschorus.out()
        fmbassdisto.out()
    elif temps == 20:
        stringsfader.base.play()
    elif temps == 60:
        selbass.recall(1)
    elif temps == 120:
        selbass.recall(2)
    elif temps == 169:
        selstrings.stop()
        selbass.recall(3)
    elif temps == 179:
        krautbeat.stop()
        selbass.stop()
    else:
        pass
        
mainp = Pattern(timecontrol, 1)
mainp.play()

s.start()
