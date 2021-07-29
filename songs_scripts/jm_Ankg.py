#!/usr/bin/env python
# encoding: utf-8
"""
Ankg.py
Created by jmdumas
"""

#IMPORTS-----------------------------------------------------------------------------------------------------------------------------
from pyo import *
import sys

#CLASSES
#303
class Osc303:
    "basic emulation of a TB-303"
    def __init__(self, freq=20, decay=0.5, shape=1, cutoff=2000, reso=5, mult=1):
        self.shape = shape
        self.cutoff = cutoff
        self.reso = reso
        self.funda = freq
        self.decay = decay
        self.mult = mult
        
        self.wave1 = Phasor(freq=self.funda,phase=0,mul=1)
        self.wave2 = Phasor(freq=self.funda*(-1),phase=0.5,mul=1)
        self.env = Adsr(0.05,self.decay,sustain=0.1,release=0.05,dur=0.2+self.decay)
        self.env2 = self.env*self.mult
        
        if self.shape == 0:
            self.wave3 = Phasor(freq=self.funda,phase=0,mul=self.env2)
        elif self.shape == 1:
            self.wave3 = ((self.wave1+self.wave2)-1)*self.env2
        else:
            pass
        
        self.filter = Biquadx([self.wave3,self.wave3],freq=self.cutoff,q=self.reso,type=0,stages=2)

    def play(self):
        self.env.play()
        self.filter.out()
    
    def stop(self):
        self.filter.stop()

#CONSTANTS---------------------------------------------------------------------------------------------------------------------------
TITLE = 'Ankg'
ARTIST = 'jmdumas'
DURATION = 222

if __name__ == "__main__":
    s = Server(audio='offline').boot()
    s.recordOptions(dur=DURATION, filename=sys.argv[1])


    s.setStartOffset(0)
    s.amp = 0.9

    bassscale = [55.0007, 61.7363, 65.4073, 73.4172, 82.4081, 87.3084, 98.0004, 87.3084, 87.3084, 87.3084, 98.0004, 110.0015]
    bassscale2 = [27.5004, 30.8681, 32.7037, 36.7086, 41.2041, 43.6542, 49.0002, 55.0007, 61.7363, 65.4073, 73.4172, 82.4081, 87.3084, 98.0004, 110.0015]
    meloscale = [55.0007, 61.7363, 65.4073, 73.4172, 82.4081, 98.0004, 82.4081, 82.4081, 82.4081, 98.0004, 110.0015]

    #TIMING & CONTROL--------------------------------------------------------------------------------------------------------------------
    met = Metro(2,poly=2)
    metmet = Metro (0.25,poly=1)
    #----for jitters----#
    jit = TrigChoice(met,[0.125,0.25,0.5,1],0.25,0.25)
    jitjit = TrigChoice(metmet,[1,0.1,0.2,0.3,1,1.2,1.8,1.5],0.15,0.25)
    #----for ampenvs----#
    fmsfade = Fader(15,10)
    fmsfadepow = Pow(fmsfade, 10)
    verbfade = Fader(20,20)
    distofade = Fader(10,10)
    fg = Linseg([(0,1),(20,0)])
    fd = Linseg([(0,1),(20,0)])
    fj = Linseg([(0,1),(20,0)])
    #----for beats----#
    selkick = Beat(time=0.125, taps=16, w1=80, w2=50, w3=10, poly=1)
    selkick2 = Beat(time=0.125, taps=8, w1=55, w2=40, w3=20, poly=1)
    selkick3 = Beat(time=0.125, taps=16, w1=30, w2=50, w3=0, poly=1)
    selkick4 = Beat(time=0.125, taps=4, w1=10, w2=60, w3=10, poly=1)
    #----for filters----#
    filtfreqmov = TrigChoice(met,[250,500,1000,1500,2000,2500,3000,3500,4000,5000],1.5,5000)
    #----for melody----#
    meloenv = CosTable([(0,0),(300,1),(1000,.3),(8191,0)])
    meloseq = Seq(time=0.125, seq=[2,1,1,2,3,3,1,2], poly=1)
    melopitch = TrigChoice(meloseq,meloscale,port=0)
    melomul = TrigEnv(meloseq, table=meloenv, dur=.5, mul=.5).mix(2)
    meloport = Port(melopitch*2,0.001,0.002,82.41)
    meloport2 = Port(melopitch*12,0.02,0.01,82.41)
    meloport3 = Port(melopitch*24,0.01,0.01,82.41)
    #----for bass----#
    table2 = LinTable([(0,0), (50,0.2), (2000,0.1), (8191,0)])
    trenv = TrigEnv(selkick, table=table2, dur=1, mul=0.1)
    #----for 303-----#
    met11 = Metro(0.125)
    met12 = Metro(31)
    count = Counter(met11,1,16,dir=1)
    data = DataTable(size=len(bassscale2), init=bassscale2)
    countf = TableIndex(data, count, mul=1, add=0)
    countfp = Port(countf,0.1,0.1,27.5004)
    cut = TrigLinseg(met12, [(0,350),(15,8000),(30,350)])
    cut2 = Fader(28,0.5)
    abmul = Fader(10)

    #SYNTH DEFS--------------------------------------------------------------------------------------------------------------------------
    HIGH = {'car': 33, 'ratio': 42, 'index': [(0,0), (0.14,5), (0.32,4), (2.9,1), (3,0)], 'mul': [(0,0),(0.01,0.3),(0.12,0),(2.9,0.8), (3,0)]}
    highindex = TrigLinseg(met,list=HIGH['index']).mix()
    highmul = TrigLinseg(met,list=HIGH['mul']).mix()

    KICK = {'car': 3, 'ratio': 12, 'index': [(0,7.5), (0.064,1.9), (0.32,0), (1,0)], 'mul': [(0,0),(0.01,0.4),(0.12,0),(1,0)]}
    kickindex = TrigLinseg(selkick,list=KICK['index'])
    kickmul = TrigLinseg(selkick,list=KICK['mul'])

    KICK2 = {'car': 270, 'ratio': 280, 'index': [(0,21.38), (0.098,20.25), (0.252,12.4), (0.420,0)], 'mul': [(0,0.1), (0.1,0.02), (0.2,0), (0.420,0)]}
    kick2index = TrigLinseg(selkick2,list=KICK2['index'])
    kick2mul = TrigLinseg(selkick2,list=KICK2['mul'])

    KICK3 = {'car': 116, 'ratio': 309, 'index': [(0,20.63), (0.0142,10.5), (0.548,1.9), (0.8,0)], 'mul': [(0,0.25),(0.0142,0.016), (0.228,0.016), (0.313,0), (0.8,0)]}
    kick3index = TrigLinseg(selkick3,list=KICK3['index'])
    kick3mul = TrigLinseg(selkick3,list=KICK3['mul'])

    KICK4 = {'car': 116.54, 'ratio': 709, 'index': [(0,20.63), (0.0142,10.5), (0.548,1.9), (0.8,0)], 'mul': [(0,0.25),(0.0142,0.016), (0.228,0.016), (0.313,0), (0.8,0)]}
    kick4index = TrigLinseg(selkick4,list=KICK4['index'])
    kick4mul = TrigLinseg(selkick4,list=KICK4['mul'])

    #PLAYERS--------------------------------------------------------------------------------------------------------------------------
    #fmhigh
    fmhigh = FM(HIGH['car'],HIGH['ratio']+jitjit,[highindex+jitjit,highindex],[highmul*(0.01*fmsfadepow),highmul*(0.01*fmsfadepow)])
    emptyt = NewTable(5,2)
    table = TableRec(fmhigh,emptyt,0.5)
    granenv = HannTable()
    granpos = Phasor(emptyt.getRate()*.005, 0, emptyt.getSize())
    granposjit = Noise(1)
    grandur = Noise(.005, .2)
    #granulator
    gran = Granulator(table=emptyt, env=granenv, pos=granpos+granposjit, dur=grandur, grains=2, basedur=.3, mul=2)
    dengran = Denorm(gran)
    verb = Freeverb(dengran, size=.95, damp=0.5, mul=verbfade*3)
    #superhighshit
    fucko = Sine([7117.86,6975.12,7312.74,8257.83], mul=0.04).mix(2)
    disto = Disto(fucko,drive=0.8,slope=0.4,mul=distofade*0.08)
    #drum kit
    fmkick = FM(KICK['car'],KICK['ratio'],[kickindex+jit,kickindex],[kickmul*0.3,kickmul*0.3])
    fmkick2 = FM(KICK2['car'],KICK2['ratio'],[kick2index,kick2index+jit],[kick2mul*0.3,kick2mul*0.3])
    fmkick3 = FM(KICK3['car'],KICK3['ratio'],[kick3index+jit,kick3index],[kick3mul*0.3,kick3mul*0.3])
    fmkick4 = FM(KICK4['car'],KICK4['ratio'],[kick4index,kick4index+jit],[kick4mul*0.3,kick4mul*0.3])
    beat = fmkick+fmkick2+fmkick3+fmkick4
    distobeat = Degrade(beat,5,0.4,mul=0.4)
    delaybeat = Disto(distobeat,0.7,0.3,mul=0.4)
    bitdist = Delay(delaybeat,jit,0.56,mul=0.9)
    bitdistfilt = Biquad(bitdist,filtfreqmov, q=10, type=2)
    #basses
    bass = SineLoop([bassscale[0],bassscale[0]*0.5+0.1,bassscale[0]*0.5+0.1,bassscale[0]],0.1,mul=0.2)
    bassdist = Disto(bass,drive=0.9,slope=0.1,mul=kickmul*0.2)
    bass2 = SineLoop([bassscale[5],bassscale[5]*0.5],0.3,mul=trenv)
    #303
    ab = Osc303(freq=countfp, decay=0.1, shape=1, cutoff=cut, reso=6, mult=abmul*0.08)
    rise = Osc303(freq=27.5004,decay=0.15,shape=1,cutoff=1500*cut2,reso=5,mult=0.2*cut2)
    risedist = Disto(rise.filter,drive=0.9,mul=cut2*0.1).out()
    #303melody
    melo = Osc303(freq=meloport, decay=1, shape=1, cutoff=cut*2, reso=3, mult=0.05)
    melo2 = Osc303(freq=meloport2, decay=0.5, shape=1, cutoff=cut, reso=2, mult=0.06)
    melo3 = Osc303(freq=meloport3, decay=0.01, shape=0, cutoff=cut+1000, reso=4, mult=0.04)
    melo4 = Disto(melo.filter+melo2.filter+melo3.filter,mul=0.5)
    distofafa = Delay(melo4,delay=0.33,feedback=0.8)
    den = Denorm(distofafa)
    revfafa = WGVerb(den,feedback=0.5,bal=1,mul=0.1).out()

    #FUNCTIONS-------------------------------------------------------------------------------------------------------------------------
    def play303b():
        ab.play()

    p = TrigFunc(met11,play303b)

    def play303m():
        melo.play()
        melo2.play()
        melo3.play()

    pm = TrigFunc(meloseq,play303m)

    def play303r():
        rise.play()

    pr = TrigFunc(met11,play303r)

    triggg = Trig()
    deltriggg = SDelay(triggg,delay=0.8)

    def drop():
        cut2.stop()

    trigtriggg = TrigFunc(deltriggg,drop)

    #SEQUENCE-----------------------------------------------------------------------------------------------------------------------
    temps = -1
    def timecontrol():
        global temps
        temps += 1
        if temps == 0:
            p.play()
            met.play()
            metmet.play()
            met11.play()
            met12.play()
            abmul.play()
        if temps == 1:
            fmsfade.play()
            fmhigh.out()
        elif temps == 15:
            table.play()
        elif temps == 20:
            verbfade.play()
            verb.out()
        elif temps == 30:
            distofade.play()
            disto.out()
        elif temps == 40:
            cut2.play()
            pr.play()
        elif temps == 57:
            triggg.play()
        elif temps == 58:
            selkick.play()
            selkick2.play()
            selkick3.play()
            selkick4.play()
            selkick.fill()
            selkick2.fill()
            selkick3.fill()
            selkick4.fill()
            fmhigh.stop()
            beat.out()
            verb.stop()
            distobeat.out()
            bass.out()
            disto.stop()
            pr.stop()
        elif temps == 78:
            selkick.new()
            selkick2.new()
            selkick3.new()
            selkick4.new()
            selkick.fill()
            selkick2.fill()
            selkick3.fill()
            selkick4.fill()
            bitdistfilt.out()
            bass.freq = [bassscale[1],bassscale[1]*0.5+0.1,bassscale[1]*0.5+0.1,bassscale[1]]
            bass2.out()
        elif temps == 94:
            selkick.new()
            selkick2.new()
            selkick3.new()
            selkick4.new()
            selkick.fill()
            selkick2.fill()
            selkick3.fill()
            selkick4.fill()
            bass.freq = [bassscale[0],bassscale[0]*0.5+0.1,bassscale[0]*0.5+0.1,bassscale[0]]
            trenv.input = selkick2
        elif temps == 102:
            selkick.new()
            selkick2.new()
            selkick3.new()
            selkick4.new()
            selkick.fill()
            selkick2.fill()
            selkick3.fill()
            selkick4.fill()
            bass.freq = [bassscale[1],bassscale[1]*0.5+0.1,bassscale[1]*0.5+0.1,bassscale[1]]
            trenv.input = selkick4
        elif temps == 114:
            selkick.new()
            selkick2.new()
            selkick3.new()
            selkick4.new()
            selkick.fill()
            selkick2.fill()
            selkick3.fill()
            selkick4.fill()
            bass.freq = [bassscale[0],bassscale[0]*0.5+0.1,bassscale[0]*0.5+0.1,bassscale[0]]
            trenv.input = selkick
        elif temps == 130:
            bassdist.out()
            bass.freq = [bassscale[3],bassscale[3]*0.5+0.1,bassscale[3]*0.5+0.1,bassscale[3]]
            bass.mul = 0.1
            selkick.setPresets([[16, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]])
            selkick2.setPresets([[8, 1, 0, 0, 0, 1, 0, 1, 0]])
            selkick3.setPresets([[16, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]])
            selkick4.setPresets([[4, 0, 0, 0, 0]])
            selkick.recall(0)
            selkick2.recall(0)
            selkick3.recall(0)
            selkick4.recall(0)
            meloseq.play()
            pm.play()
        elif temps == 134:
            selkick.fill()
        elif temps == 140:
            selkick.fill()
        elif temps == 170:
            bass.freq = [bassscale[0],bassscale[0]*0.5+0.1,bassscale[0]*0.5+0.1,bassscale[0]]
            bass.mul = 0.2
        elif temps == 172:
            bass.freq = [bassscale[1],bassscale[1]*0.5+0.1,bassscale[1]*0.5+0.1,bassscale[1]]
        elif temps == 174:
            bass.freq = [bassscale[3],bassscale[3]*0.5+0.1,bassscale[3]*0.5+0.1,bassscale[3]]
            bass.mul = 0.15
        elif temps == 176:
            selkick2.fill()
            selkick3.fill()
            selkick4.fill()
        elif temps == 178:
            bass.freq = [bassscale[0],bassscale[0]*0.5+0.1,bassscale[0]*0.5+0.1,bassscale[0]]
            bass.mul = 0.2
        elif temps == 180:
            bass.freq = [bassscale[1],bassscale[1]*0.5+0.1,bassscale[1]*0.5+0.1,bassscale[1]]
        elif temps == 182:
            bass.freq = [bassscale[3],bassscale[3]*0.5+0.1,bassscale[3]*0.5+0.1,bassscale[3]]
        elif temps == 184:
            bass.freq = [bassscale[11],bassscale[11]*0.5+0.1,bassscale[11]*0.5+0.1,bassscale[11]]
            bass.mul = 0.05
            selkick3.stop()
            selkick4.stop()
            meloseq.stop()
            met11.stop()
            met12.stop()
            distobeat.stop()
            delaybeat.stop()
            bitdist.stop()
            bitdistfilt.stop()
            bass2.stop()
            pm.stop()
            p.stop()
        elif temps == 185:
            melo.stop()
            melo2.stop()
            melo3.stop()
            melo4.stop()
        elif temps == 192:
            verbfade.play()
            verb.out()
            bass.freq = [bassscale[0],bassscale[11]*0.5+0.1,bassscale[11]*0.5+0.1,bassscale[0]]
            fg.play()
            bass.mul = 0.05*fg
            fd.play()
            fmkick.mul = (kickmul*0.4)*fd
            distobeat.play()
            delaybeat.play()
            bitdist.play()
            bitdistfilt.out()
            distofafa.stop()
        elif temps == 196:
            selkick2.fill()
        elif temps == 201:
            fj.play()
            fmkick2.mul = (kick2mul*0.3)*fj
            verbfade.stop()
        elif temps == 221:
            selkick.stop()
            selkick2.stop()
        else:
            pass

    mainp = Pattern(timecontrol, 1)
    mainp.play()

    s.start()
