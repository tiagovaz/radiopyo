#!/usr/bin/env python
# encoding: utf-8
"""
4.py

Created by jmdumas
"""
from pyo import *
from random import randrange
from random import uniform
from random import shuffle
import sys

TITLE = '4'
ARTIST = 'jmdumas'
DURATION = 253

s = Server(audio='offline').boot()
s.recordOptions(dur=DURATION, filename=sys.argv[1])


s.setStartOffset(0)
s.amp = 1.3

#MAINLINE
met = Metro(0.125, poly=8)
met2 = Metro(0.127, poly=8)
metjit = Randi(0.495,0.505,freq=0.125)
met3 = Metro(metjit, poly=8)
t1=LinTable([(0,0),(45,0.8948),(1575,0.774),(1710,0),(3848,0),(4096,0.6458),(4388,0),(5693,0),(5783,0.7948),(6189,0),(8192,0)])
t2=LinTable([(0,0),(112,0.9896),(787,0),(4928,0),(5783,0.9792),(7089,0.0781),(8192,0)])
t3=LinTable([(0,0),(14,0.9974),(810,0.1615),(2475,0.0312),(4951,0),(8192,0)])
t4=LinTable([(0,0),(4005,0),(4096,0.9688),(4231,0),(8192,0)])
t5=LinTable([(0,0),(45,0.9792),(270,0.9792),(337,0),(4096,0),(4163,0.7969),(4411,0.7969),(4478,0),(8192,0)])
t6=LinTable([(0,0),(1395,0),(1575,0.9115),(1687,0),(8192,0)])
ntable = NewTable(8192/s.getSamplingRate())
lfomorph = LFO(freq=0.001, type=3, mul=1)
lfo2jit = Randi(-0.00002,0.00002,freq=0.1)
lfo2 = Rossler(pitch=0.00005+lfo2jit, chaos=0.9, mul=0.3)
tablelist = [t1,t2,t3,t4,t5,t6]
morph = TableMorph(lfomorph,ntable,tablelist)
env = TrigEnv(met,ntable)
fader = Fader(60,10, mul=0.4)
fad1 = Fader([10]*10,5, mul=fader*env)
soundgen = SineLoop(freq = [random.randrange(200, 1001, 30) for i in range(10)], feedback=[lfo2,lfo2*1.1], mul=fad1)
sortedfreqlist = sorted(soundgen.freq)
soundgen2fader = Fader(0.1,30)
soundgen2 = Chorus(soundgen, depth=2, feedback=0.2, bal=1, mul=0.5*soundgen2fader)
freqrandsine=Randi(0.5,2,freq=0.5)
biquadsine=Sine(freqrandsine, mul=2500, add=2500)
soundgen2pitch = Biquad(input=soundgen2, type=1, freq=biquadsine)
soundgen2delay = Delay(soundgen2pitch,delay=0.5,feedback=0.1)
soundmix = soundgen.mix(2)
comp=Compress(soundmix)
revdel = WGVerb(comp, feedback=0.4, cutoff=5000, bal=0.3, mul=1)
#FMPULSE
PULSE = {'car': 1, 'ratio': 110, 'index': [(0,20), (0.03,11), (0.5,2), (0.85,0)], 'mul': [(0,0.25),(0.0142,0.016), (0.228,0.016), (0.313,0), (0.8,0)]}
pulseindex = TrigLinseg(met,list=PULSE['index'])
pulsemul = TrigEnv(met2,ntable)
fmmetmul = TrigEnv(met3,ntable)
fmfade = Fader(50,0.1,mul=pulsemul*0.1)
fmpulse = FM(PULSE['car'],PULSE['ratio'],pulseindex,fmfade)
#NOISE
ppmet2 = Metro(0.0125)
ptime2 = TrigChoice(ppmet2, [0.125,0,05,0.20,0.25,0.33,0.5,0.66],port=0.01)
ppmet = Metro(ptime2)
ptime = TrigChoice(ppmet, [0.125,0.06,0.05,0.2,0.166],port=0.01)
pmet = Metro(ptime,poly=4)
ptable = LinTable([(0,0), (50,1), (8191,0)])
penv = TrigEnv(pmet, table=ptable, dur=0.2)
psource = Biquad(Osc(ptable, freq=2, mul=penv*75),freq=2000,type=0)
psource2 = Biquad(Disto(BrownNoise(mul=penv*0.07),drive=1,slope=0.8,mul=0.07),freq=1912,q=4.5)
psource3 = psource+psource2
pfiltermove = TrigChoice(pmet,[4000,4555,5000,5333,6000,6111,7000,8888],port=0.05,init=5000)
pfiltermix = pfiltermove.mix(2)
pmul=Fader(20,0.2)
pmull=Fader(60,0.1)
pmul2 = pmull*0.1*fmmetmul
pfilter = Biquad(psource3, freq=pfiltermix, q=5, type=2, mul=pmul)
basss=Sine(sortedfreqlist[0]/5,mul=pmul2).mix(1).mix(2)
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
#303MEL
met12 = Metro(time=0.125)
met12percent=Percent(met12, 50)
cut = TrigLinseg(met12percent, [(0,350),(0.25,1000),(0.5,350)])
meloscale = [i/100.0 for i in soundgen.freq]
sortedmeloscale = DataTable(size=len(meloscale),init=sorted(meloscale))
meloseq = Metro(0.133, poly=1)
melocount = Counter(meloseq,min=0,max=len(meloscale), dir=2)
melopitch = TableIndex(sortedmeloscale,melocount)
meloenv = CosTable([(0,0),(300,1),(1000,.3),(8191,0)])
melomul = TrigEnv(meloseq, table=meloenv, dur=.5, mul=1).mix(2)
meloport = Port([melopitch*6,melopitch*4,melopitch*2],0.01,0.02,82.41)
melfade = Pow(Fader(30,20),2)
melomulreal = melomul*melfade
melo = Osc303(freq=meloport[0], decay=0.5, shape=1, cutoff=cut*2, reso=3, mult=0.05*melomulreal)
melo2 = Osc303(freq=meloport[1], decay=1, shape=1, cutoff=cut, reso=4, mult=0.06*melomulreal)
melo3 = Osc303(freq=meloport[2], decay=0.3, shape=1, cutoff=cut+1000, reso=3, mult=0.02*melomulreal)
meloreal = melo.filter+melo2.filter+melo3.filter
melo4 = Disto(meloreal,drive=0.7,slope=0.2,mul=0.5)
distofafa = Chorus(melo4,depth=5,feedback=0.15, mul=melfade)
den = Denorm(distofafa)
revfafa = WGVerb(den,feedback=0.3,bal=0.4,mul=0.1)

def play303m():
    melo.play()
    melo2.play()
    melo3.play()

pm = TrigFunc(meloseq,play303m)
#BREAKNOISE
noisetrigger = Trig().stop()
noisetrig = TrigExpseg(noisetrigger, [(0,0),(0.5,0.9),(1,0)], mul=0.5)
startnoise = Noise(mul=noisetrig).mix(2)
startnoisefilt = Biquad(startnoise, freq=5000, type=3, mul=1)
startden=Denorm(startnoisefilt)
startnoiserev = WGVerb(startden, feedback=0.99, cutoff=10000, bal=0.4, mul=1)
#CHORDPULSE
chordtrigger = Metro(0.125, poly=2)
chordtable = CosTable([(0,0.0000),(2000,0.5000),(3465,0.1719),(8192,0.0000)])
chordmulenv = TrigEnv(chordtrigger,table=chordtable, dur=0.2, mul=0.1)
cfrand = Randi([0.125,0.4],[1,0.9],freq=1)
crand = Randh([0.25,0.1,0.5,0.75],[1,2,0.7,1],freq=cfrand[0])
crand2 = Randh([0.25,0.1,0.5,0.75],[1,2,0.7,1.1],freq=cfrand[1])
alist=[]
for caca in sortedfreqlist:
    alist.extend([caca,caca])
chord = CrossFM(carrier=alist, ratio=crand/2, ind1=crand, ind2=crand2)
chordcaca = chord*chordmulenv
chorddist = Disto(chordcaca,drive=0.999,slope=0.2,mul=0.01).mix(2)
chordchor = Chorus(chorddist)
chordfader = Pow(Fader(40,0.1),2)
chordfader2 = Pow(Fader(40,30),2)
chordverb = WGVerb(chordchor, feedback=0.7, cutoff=3000, bal=0.2, mul=1*chordfader)
chordlowpan = Sine(1)
chorddel = SPan(Harmonizer(chordcaca,transpo=-7,mul=chordfader2*0.7),pan=chordlowpan)
#HIGHFREQ BREAKNOISE
voiceenv = TrigExpseg(noisetrigger, [(0,0),(.4,1),(90,0)])
voice = SineLoop([i*10 for i in sortedfreqlist],feedback=0.1, mul=0.001*voiceenv)
#SIRENS
risingfreq = Phasor(0.05, mul=0.45, add=0.55).stop()
risingfader = Fader(20,0.1)
rising = SineLoop([i*risingfreq for i in sortedfreqlist],feedback=0.2, mul=risingfader*0.07)

#TIMELINE
temps = -0.5
def timecontrol():
    global temps
    temps += 0.5
    if temps == 0:
        voice.out()
        startnoiserev.out()
        noisetrigger.play()
    elif temps == 3:
        met3.play()
        ppmet2.play()
        ppmet.play()
        pmet.play()
        pmul.play()
        pmull.play()
        pfilter.out()
        basss.out()
    elif temps == 10:
        chordtrigger.play()
        chordverb.out()
        chordfader.base.play()
        chordfader2.base.play()
        chorddel.out()
    elif temps == 48:
        noisetrig.list=[(0,0),(2,0.7),(3,0)]
        voiceenv.list=[(0,0),(2,0.9),(60,0)]
        noisetrigger.play()
    elif temps == 50:
        voice.stop()
        startnoiserev.stop()
        chordfader.base.stop()
        pmul.stop()
        met12.play()
        meloseq.play()
        revfafa.out()
        pm.play()
        melfade.base.play()
        revdel.out()
        soundgen2fader.play()
        soundgen2delay.out()
        met.play()
        met2.play()
        fader.play()
        fad1[0].play()
    elif temps == 52:
        pfilter.stop()
        chordverb.stop()
    elif temps == 60:
        fmpulse.out()
        fmfade.play()
    elif temps == 70:
        fad1[0].play()
    elif temps == 90:
        fad1[1].play()
    elif temps == 100:
        fad1[2].play()
    elif temps == 110:
        fad1[3].play()
        melfade.base.stop()
        chordfader2.base.stop()
    elif temps == 115:
        fad1[4].play()
    elif temps == 120:
        fad1[5].play()
    elif temps == 125:
        fad1[6].play()
    elif temps == 130:
        fad1[7].play()
    elif temps == 140:
        fad1[8].play()
    elif temps == 150:
        fad1[9].play()
        chordverb.out()
        chordfader.base.play()
    elif temps == 160:
        soundgen2fader.stop()
    elif temps == 210:
        risingfreq.play()
        risingfader.play()
        rising.out()
    elif temps == 219.5:
        noisetrig.list=[(0,0),(0.5,0.9),(1,0)]
        voiceenv.list=[(0,0),(.4,1),(90,0)]
        voice.out()
        startnoiserev.out()
        noisetrigger.play()
    elif temps == 220:
        risingfader.stop()
        risingfreq.stop()
        pfilter.out()
        pmul.play()
        revdel.stop()
        chordfader.base.stop()
    elif temps == 250:
        noisetrig.list=[(0,0),(2,0.7),(3,0)]
        voiceenv.list=[(0,0),(2,0.9),(60,0)]
        noisetrigger.play()
    elif temps == 252:
        pmull.stop()
        pmul.stop()
        fmfade.stop()
        voice.stop()
        startnoiserev.stop()
    else:
        pass
        
mainp = Pattern(timecontrol, 0.5)
mainp.play()

s.start()
