#!/usr/bin/python

"""
SunRadio.py
Created by jmdumas
"""
#IMPORTS
from pyo import *
#CONSTANTS

TITLE = 'SunRadio'
ARTIST = 'jmdumas'
DURATION = 273

s = Server(audio='offline').boot()
s.recordOptions(dur=DURATION, filename='radiopyo.ogg')

emit = 2
#SYNTHS DEFS
BASS = {'car': 13.75, 'ratio': 1, 'index': [(0,0), (0.01,7.5), (0.061,5.25), (1.2,8.25), (2.2,8.6), (2.8, 5.25), (2.99, 5.6), (4,0) ], 'mul': [(0,0), (0.01,0.06), (2.9,0.1), (4,0)]}
#DRUMS DEFS
HH = {'car': 270, 'ratio': 280, 'index': [(0,21.38), (0.098,20.25), (0.252,12.4), (0.420,0)], 'mul': [(0,0.1), (0.1,0.02), (0.2,0), (0.420,0)]}
SNARE = {'car': 116.54, 'ratio': 709, 'index': [(0,20.63), (0.0142,10.5), (0.548,1.9), (0.8,0)], 'mul': [(0,0.25),(0.0142,0.016), (0.228,0.016), (0.313,0), (0.8,0)]}
SNARE2 = {'car': 96, 'ratio': 0.4, 'index': [(0,20.63), (0.0142,10.5), (0.548,1.9), (0.8,0)], 'mul': [(0,0.25),(0.0142,0.016), (0.228,0.016), (0.313,0), (0.8,0)]}
SNARE3 = {'car': 116, 'ratio': 309, 'index': [(0,20.63), (0.0142,10.5), (0.548,1.9), (0.8,0)], 'mul': [(0,0.25),(0.0142,0.016), (0.228,0.016), (0.313,0), (0.8,0)]}
KICK = {'car': 3, 'ratio': 12, 'index': [(0,7.5), (0.064,1.9), (0.32,0), (1,0)], 'mul': [(0,0),(0.01,0.4),(0.12,0),(1,0)]}
TOM = {'car': 0, 'ratio': 0, 'index': [(0,0), (0,0)], 'mul': [(0,0),(0,0)]}
#SEQUENCE
met = Metro(emit).play()
selbass = Metro(emit*2, poly=2).play()
selbass2 = Metro(emit*0.25, poly=1).play()
selhh2 = Metro(emit*0.167, poly=1).play()
count = Counter(met, min=1, max=18)
count2 = Counter(met, min=1, max=17)
selkick = Select(count, [1,5,9,13,14,15,17]).mix()
selsnare = Select(count2, [2,4,6,8,9]).mix()
selsnare2 = Select(count, [3,4,6,8,9,10,14,16]).mix()
selhh = Select(count, [1,2,3,4,5,6,7,8,9,11,13,15]).mix()
sellead = Metro(emit*0.25, poly=1).play()
prog = TrigChoice(sellead,[261.6, 293.7, 311.1, 349.2, 392, 415.3, 466.2, 523.2, 1, 1, 1, 1, 1, 1],0.25, 261.6).mix()
prog1 = TrigChoice(selbass,[32.703, 36.708],.01, 32.703).mix()
prog2 = TrigChoice(selbass2,[32.703, 36.708],.01, 32.703).mix()
#KICK
kickindex = TrigLinseg(selkick,list=KICK['index'])
kickmul = TrigLinseg(selkick,list=KICK['mul'])
#SNARE
snareindex = TrigLinseg(selsnare,list=SNARE['index'])
snaremul = TrigLinseg(selsnare,list=SNARE['mul'])
#SNARE2
snare2index = TrigLinseg(selsnare2,list=SNARE2['index'])
snare2mul = TrigLinseg(selsnare2,list=SNARE2['mul'])
#HH
hhindex = TrigLinseg(selhh,list=HH['index'])
hhmul = TrigLinseg(selhh,list=HH['mul'])
#HH2
hh2index = TrigLinseg(selhh2,list=HH['index'])
hh2mul = TrigLinseg(selhh2,list=HH['mul'])
#BASS
bassindex = TrigLinseg(selbass,list=BASS['index']).mix()
bassmul = TrigLinseg(selbass,list=BASS['mul']).mix()
#BASS2
bass2index = TrigLinseg(selbass2,list=BASS['index']).mix()
bass2mul = TrigLinseg(selbass2,list=BASS['mul']).mix()
#CONTROLS
jit = TrigChoice(met,[0.125,0.167,0.25,0.2,0.333,0.0625,0.5,1],0.1,0.25).mix()
filtfade = Expseg([(0,10000),(36,1)], exp=10)
filtfade1 = Expseg([(0,1),(36,10000)], exp=10)
bassfade = Fader(10,10)
filterfader = Fader(0.2,5)
#PLAYERS
fmkick = FM(KICK['car'],KICK['ratio'],[kickindex,kickindex+count*0.1],[kickmul*0.6,kickmul*0.6])
revkick = WGVerb(fmkick,feedback=0.7,cutoff=7000)
kicktable = CosTable([(0,0.0000),(405,0.5000),(3465,0.1719),(8192,0.0000)])
tt = TrigEnv(selkick,table=kicktable, dur=1)
sinekick = Sine([32.703,32], mul=tt)
fmsnare = FM(SNARE3['car'],SNARE3['ratio'],[snareindex+count,snareindex],[snaremul,snaremul])
delsnare = Delay(fmsnare,jit,0.6,mul=0.8)
degdel = Degrade([delsnare,delsnare],5,0.5)
tom = FM(SNARE2['car'],SNARE2['ratio'],[snare2index,snare2index+count],[snare2mul*0.9,snare2mul*0.9])
fmhh = FM(HH['car'],HH['ratio'],[hhindex,hhindex+jit],[hhmul,hhmul])
fmhh2 = FM(HH['car']*jit,HH['ratio']+jit*2,[hh2index+jit,hh2index+jit*0.25],[hh2mul*0.01,hh2mul*0.01])
fmbass = FM(prog1*0.5,BASS['ratio'],[bassindex+jit,bassindex],[bassmul*bassfade,bassmul*bassfade])
fmbass2 = FM(prog2*0.5,BASS['ratio'],[bass2index+jit,bass2index],[bass2mul,bass2mul])
revbass2 = AllpassWG(fmbass2,freq=261.6,detune=0.2,mul=0.3)
acid = Sine([prog*10,prog*10.1], mul=0.1)
sindel = Delay(acid,jit,0.8,mul=0.1)
mainfilter = Biquad(revbass2,freq=filtfade+filtfade1, type=1, mul=0.7*filterfader)
#FUNCTIONS
temps = -1
def timecontrol():
    global temps
    temps += 1
    if temps == 0:
        fmhh2.out()
        filtfade.play()
        filterfader.play()
        mainfilter.out()
    elif temps == 36:
        fmsnare.out()
        delsnare.out()
        degdel.out()
        tom.out()
        fmhh.out()
        fmkick.out()
        revkick.out()
        sinekick.out()
    elif temps == 57:
        bassfade.play()
        fmbass.out()
    elif temps == 89:
        sindel.out()
    elif temps == 240:
        filtfade1.play()
        sindel.stop()
        bassfade.stop()
        fmkick.stop()
        revkick.stop()
        sinekick.stop()
        fmhh.stop()
    elif temps == 272:
        mainfilter.stop()
        fmbass.stop()
        fmsnare.stop()
        delsnare.stop()
        degdel.stop()
        tom.stop()
        fmhh2.stop()
    else:
        pass
        
#PATTERNS
mainp = Pattern(timecontrol, 1)
mainp.play()
s.start()
