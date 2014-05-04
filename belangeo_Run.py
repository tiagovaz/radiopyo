#!/usr/bin/env python
# encoding: utf-8
"""
Created by belangeo on 2011-04-13.
"""

from pyo import *
import random, time
from random import uniform as rnd

class RunFm:
    def __init__(self, TM, TAPS, changeFreqSelect, fmTranspo, countCloseDisto, finalFadeout, IndSwitch, num=4):
        self.env = ExpTable([(0,0),(50,1),(8191,0)], exp=12)
        self.ampSwitch = DataTable(size=4, init=[1,.65,1,1])
        self.amp = 0.15
        self.changeFreqSelect = changeFreqSelect
        self.fmTranspo = fmTranspo
        self.countCloseDisto = countCloseDisto
        self.fmFadeForStringSolo = TableIndex(self.ampSwitch, self.countCloseDisto)
        self.finalFadeout = finalFadeout
        self.IndSwitch = Sig(IndSwitch, add=2)
        
        self.mCar = Beat(time=TM, taps=TAPS, w1=[90,80,40,50], w2=[30,40,90,40], w3=[40,30,30,20], poly=1).play()
        self.mRat = Beat(time=TM, taps=TAPS, w1=[50,80,40,70], w2=[30,40,50,80], w3=[30,40,70,50], poly=1).play()
        self.mInd = Beat(time=TM, taps=TAPS, w1=[30,30,80,70], w2=[30,50,80,30], w3=[40,40,80,30], poly=1).play()

        self.carAdd = TrigChoice(self.changeFreqSelect, choice=[midiToHz(x) for x in [31,36,43,48,55,60]], mul=[rnd(.99,1.01) for i in range(4)])
        self.mulCarMul = TrigChoice(self.changeFreqSelect, choice=[midiToHz(x) for x in [19,24,36,43,48,55]], mul=[rnd(.99,1.01) for i in range(4)])
        self.trigFmTranspo = SampHold(self.fmTranspo, self.changeFreqSelect, 1.0, mul=self.fmFadeForStringSolo)
        
        self.mulCar = Sig(self.mCar['amp'], mul=self.mulCarMul*self.trigFmTranspo)
        self.mulRat = Sig(self.mRat['amp'], mul=self.fmFadeForStringSolo*2)
        self.mulInd = Sig(self.mInd['amp'], mul=self.fmFadeForStringSolo*15)

        self.car = TrigEnv(self.mCar, table=self.env, dur=self.mCar['dur'], mul=self.mulCar, add=self.carAdd*self.trigFmTranspo)
        self.rat = TrigEnv(self.mRat, table=self.env, dur=self.mRat['dur'], mul=self.mulRat, add=[.996,.7485,1.502,.506])
        self.ind = TrigEnv(self.mInd, table=self.env, dur=self.mInd['dur'], mul=self.mulInd, add=self.IndSwitch)

        self.lfoCar = Sine(Sine(.05, 0, midiToHz(60), midiToHz(67)), mul=25, add=self.car)
        self.lfoRat = Sine(Sine(.05, 0.5, midiToHz(60), midiToHz(72)), mul=.25, add=self.rat)
        self.lfoInd = Sine(midiToHz(72), mul=1, add=self.ind)

        self.fmList = [FM(carrier=self.lfoCar*rnd(.99,1.01), 
                          ratio=self.lfoRat*rnd(.99,1.01), 
                          index=self.lfoInd*rnd(.99,1.01), 
                          mul=self.amp) for i in range(num)]

        self.outMix = Mix(self.fmList, voices=4)
        self.antiAlias = Biquad(self.outMix, freq=15000)
        self.outPan = SPan(self.antiAlias, pan=[0,.33,.67,1])
        self.outDc = DCBlock(self.outPan, mul=1.6)
        self.outEQ = EQ(self.outDc, freq=90, boost=-9.0, mul=self.finalFadeout).out()
    
    def change(self):
        self.mCar.fill()
        self.mCar.new()
        self.mRat.fill()
        self.mRat.new()
        self.mInd.fill()
        self.mInd.new()
    
    def getBarEnd(self):
        return self.mCar['end'][0]
    
    def getOutput(self):
        return self.outEQ

class RunKick:
    def __init__(self, TM, TAPS, BASS_SEQ, changeFreqSelect, ampSwitch, bassSwitch, distoSwitch):
        self.env = CosTable([(0,0),(100,1),(400,.3),(3000,.3),(8191,0)])
        self.notes = DataTable(TAPS*2, init=[midiToHz(x+12) for x in [24,26,27,29, 27,29,27,26, 24,22,20,22, 19,20,22,26,
                                                                    24,22,26,24, 26,29,27,26, 27,29,27,24, 26,27,26,22]])
        self.notes2 = DataTable(TAPS*2, init=[midiToHz(x+7) for x in [24,22,24,22, 24,26,27,29, 27,29,27,26, 24,22,26,27,
                                                                    24,22,26,24, 27,26,29,27, 29,27,26,24, 22,24,27,26]])
        self.notes3 = DataTable(TAPS*2, init=[midiToHz(x+12) for x in [24,26,27,26, 24,22,24,20, 24,22,20,22, 24,27,22,26,
                                                                    24,22,26,27, 26,24,22,20, 24,22,26,24, 22,27,26,22]])
        self.BASS_SEQ = BASS_SEQ
        self.changeFreqSelect = changeFreqSelect
        self.ampSwitch = ampSwitch
        self.bassSwitch = bassSwitch
        self.distoSwitch = distoSwitch

        self.mSub = Seq(time=TM, seq=[TAPS]).play()
        self.mBass = Seq(time=TM, seq=self.BASS_SEQ[0]).play()
        self.mWalk = Beat(time=TM, taps=TAPS*2, w1=100, w2=70, w3=70).play()

        self.trig = Interp(self.mBass, self.mWalk, self.bassSwitch)

        self.distoMul = Counter(self.distoSwitch, max=2)
        self.bPit1 = TableIndex(self.notes, self.distoMul*self.mWalk["tap"])
        self.bPit2 = TableIndex(self.notes2, self.distoMul*self.mWalk["tap"])
        self.bPit3 = TableIndex(self.notes3, self.distoMul*self.mWalk["tap"])
        self.firstTap = Select(self.mWalk['tap'])
        self.countWalk = Counter(self.firstTap, max=2)
        self.fourBar = Select(self.countWalk)
        self.newNotes = TrigRandInt(self.fourBar, max=3)
        self.bassPitch2 = Selector([self.bPit1, self.bPit2, self.bPit3], voice=self.newNotes)

        self.bassPitch1 = TrigXnoiseMidi(self.changeFreqSelect, scale=1, mrange=(30,36))
        self.bassPitch = Interp(self.bassPitch1, self.bassPitch2, self.bassSwitch)

        self.relamp = Sqrt(self.mWalk["amp"], mul=1.7)
        self.dur = Interp(Sig(.25), self.mWalk["dur"], self.bassSwitch)
        self.amp = Interp(Sig(1), self.relamp, self.bassSwitch)

        self.sub = TrigEnv(self.mSub, table=self.env, dur=.25, mul=self.ampSwitch*.75)
        self.bass = TrigEnv(self.trig, table=self.env, dur=self.dur, mul=self.ampSwitch*self.amp)
        self.outSub = SineLoop(self.bassPitch, feedback=.12, mul=self.sub).mix(2).out()
        self.outBass = SineLoop(self.bassPitch, feedback=.12, mul=self.bass)
        self.eq = EQ(self.outBass, freq=150, boost=3).mix(2).out()

    def change(self):
        self.mBass.seq = random.choice(self.BASS_SEQ)
        self.mWalk.new()

    def stop(self):
        self.mSub.stop()
        self.mBass.stop()
        self.mWalk.stop()
        self.trig.stop()
        self.bPit1.stop()
        self.bPit2.stop()
        self.bPit3.stop()
        self.firstTap.stop()
        self.countWalk.stop()
        self.fourBar.stop()
        self.newNotes.stop()        
        self.bassPitch1.stop()
        self.bassPitch2.stop()
        self.bassPitch.stop()
        self.dur.stop()
        self.amp.stop()
        self.relamp.stop()
        self.sub.stop()
        self.bass.stop()
        self.outSub.stop()
        self.outBass.stop()
        self.eq.stop()

class RunStrings:
    def __init__(self, TM, TAPS, SCALES, invAmpSwitch, finalFadeout, num=5):
        self.SCALES = SCALES
        self.invAmpSwitch = invAmpSwitch
        self.finalFadeout = finalFadeout
        self.count, self.scl = 1, 1

        self.mHarm = Beat(time=TM*8, taps=TAPS, w1=[100,20,0,30,20,40], w2=[10,20,100,20,40,25], w3=[0,20,10,40,10,0]).play()
        self.env = Port(self.mHarm['amp'], .75, .75, mul=2.3).stop()
        self.harmMid = TrigXnoiseMidi(self.mHarm, dist=11, x1=1, x2=.4, scale=0, mrange=[(36,45),(45,60),(55,69),(64,75),(68,85),(72,88)]).stop()
        self.harmMidPort = Port(self.harmMid, [.35,.4,.45,.5,.55,.7], [.35,.4,.45,.5,.55,.7]).stop()
        self.harmFreqRnd = Randi(.995, 1.005, freq=[rnd(.3,1.2) for i in range(6*num)]).stop()
        self.harmFreq = Snap(self.harmMidPort, choice=self.SCALES[0], scale=1, mul=self.harmFreqRnd).stop()
        self.harmFeedRnd = Randi(min=.1, max=.15, freq=[rnd(.1,.7) for i in range(6*num)]).stop()
        self.harmOsc = SineLoop(freq=self.harmFreq, feedback=self.harmFeedRnd, mul=self.env*[.055,.05,.047,.047,.035,.027]).stop()
        self.harmPan = SPan(self.harmOsc.mix(6), pan=[.7,.45,.2,0,1,.5]).stop()
        self.harmDc = DCBlock(self.harmPan, mul=self.invAmpSwitch*self.finalFadeout).stop()

        self.harmChange = TrigFunc(self.mHarm['end'][0], self.changeHarm).stop()
        self.thresh = Thresh(self.finalFadeout, threshold=0.1666, dir=1).stop()
        self.finalFreeze = TrigFunc(self.thresh, self.stopBeat).stop()

    def getOut(self):
        return self.harmDc

    def play(self):
        self.env.play()
        self.harmMid.play()
        self.harmMidPort.play()
        self.harmFreqRnd.play()
        self.harmFreq.play()
        self.harmFeedRnd.play()
        self.harmOsc.play()
        self.harmPan.play()
        self.harmDc.play()
        self.harmChange.play()
        self.thresh.play()
        self.finalFreeze.play()

    def stopBeat(self):
        self.mHarm.time = 100

    def changeHarm(self):
        if (self.count % 4) == 0:
            self.harmFreq.choice = self.SCALES[self.scl % len(self.SCALES)]
            self.scl += 1
        if (self.count % 2) == 0:
            self.mHarm.new()
        self.count += 1

class RunStringsDuet:
    def __init__(self, TM, TAPS, SCALES, num=5):
        self.SCALES = SCALES
        self.count, self.scl = 1, 1

        self.globalEnv = Linseg([(0,0), (10,1.5), (90, 1.5), (116, 0)]).stop()
        self.mHarm = Beat(time=TM*8, taps=TAPS, w1=[35,50,50], w2=[10,25,25], w3=[0,0,0]).play()
        self.env = Port(self.mHarm['amp'], 1, 1, init=[.5,.5,.5], mul=1.5).stop()
        self.harmMid = TrigXnoiseMidi(self.mHarm, dist=11, x1=1, x2=.25, scale=0, mrange=[(60,77),(68,85),(72,88)])
        self.harmMidPort = Port(self.harmMid, .5, .5, init=[72,79,84]).stop()
        self.harmFreqRnd = Randi(.995, 1.005, freq=[rnd(.3,1.2) for i in range(3*num)]).stop()
        self.harmFreq = Snap(self.harmMidPort, choice=self.SCALES[0], scale=1, mul=self.harmFreqRnd).stop()
        self.harmFeedRnd = Randi(min=.1, max=.15, freq=[rnd(.1,.7) for i in range(3*num)]).stop()
        self.harmOsc = SineLoop(freq=self.harmFreq, feedback=self.harmFeedRnd, mul=self.env*[.043,.032,.027]).stop()
        self.harmPan = SPan(self.harmOsc.mix(3), pan=[.5,.1,.9]).stop()
        self.harmDc = DCBlock(self.harmPan, mul=self.globalEnv).stop()

        self.harmChange = TrigFunc(self.mHarm['end'][0], self.changeHarm).stop()

    def getOut(self):
        return self.harmDc

    def play(self):
        self.globalEnv.play(dur=116)
        self.env.play(dur=116)
        self.harmMid.play(dur=116)
        self.harmMidPort.play(dur=116)
        self.harmFreqRnd.play(dur=116)
        self.harmFreq.play(dur=116)
        self.harmFeedRnd.play(dur=116)
        self.harmOsc.play(dur=116)
        self.harmPan.play(dur=116)
        self.harmDc.play(dur=116)
        self.harmChange.play(dur=116)

    def changeHarm(self):
        if (self.count % 4) == 0:
            self.harmFreq.choice = self.SCALES[self.scl % len(self.SCALES)]
            self.scl += 1
        if (self.count % 2) == 0:
            self.mHarm.new()
        self.count += 1

class RunWind:
    def __init__(self, input, ampSwitch, countCloseDisto, num=8):
        self.input = input
        self.ampSwitch = ampSwitch
        self.countCloseDisto = countCloseDisto
        self.amplitudes = DataTable(size=4, init=[1,.35,1,1])
        self.rand = Randi(min=1000, max=2000, freq=[rnd(.02, .05) for i in range(2)])
        self.freq = Randi(min=[.99]*num, max=1.01, mul=self.rand)
        self.varAmp = TableIndex(self.amplitudes, self.countCloseDisto)
        self.varAmpPort = Port(self.varAmp, 10, 10, mul=.3)
        self.amp = Randi(min=0.5, max=1.3, freq=[rnd(.15, .2) for i in range(2)], mul=self.varAmpPort)
        self.wind = Waveguide(self.input, freq=self.freq, dur=60, minfreq=800, mul=self.amp*self.ampSwitch)
        self.mix = self.wind.mix(2)

    def getOutput(self):
        return self.mix
        
    def stop(self):
        self.rand.stop()
        self.freq.stop()
        self.amp.stop()
        self.varAmp.stop()
        self.varAmpPort.stop()
        self.wind.stop()
        self.mix.stop()

class RunSiren:
    def __init__(self, input, sirenSwitch):
        self.input = input
        self.sirenSwitch = sirenSwitch

        self.amp = Fader(fadein=6, fadeout=8, dur=40, mul=.5)
        self.freq = Randi(min=300, max=1000, freq=[rnd(.02, .05) for i in range(2)])
        self.siren = Waveguide(self.input, freq=self.freq, dur=60, minfreq=250, mul=self.amp*self.sirenSwitch)

    def getOutput(self):
        return self.siren

    def play(self):
        self.amp.play()

    def stop(self):
        self.amp.stop()
        self.freq.stop()
        self.siren.stop()    

class RunPunch:
    def __init__(self, input, start, num=2):
        self.input = input
        self.start = start
        self.off = False

        self.amp = TrigLinseg(self.start, list=[(0,0),(.002,4),(.25,.5),(4.6,1.5),(10,.75),(16.2,0)])
        self.freq = Randi(min=500, max=2500, freq=[rnd(.05, .08) for i in range(num)])
        self.punch = Waveguide(self.input, freq=self.freq, dur=60, minfreq=500, mul=self.amp)
        self.trigStop = TrigFunc(self.amp['trig'], self.stop)

    def getOutput(self):
        return self.punch

    def openOffSwitch(self):
        self.off = True

    def stop(self):
        if self.off:
            self.amp.stop()
            self.freq.stop()
            self.punch.stop()

class RunDisto:
    def __init__(self, input, start):
        self.input = input
        self.start = start
        self.off = False
        self.distoFade = TrigLinseg(self.start, [(0,0),(7.3,1),(10.8,1),(10.805,0)], mul=.2)
        self.distoHighFade = TrigLinseg(self.start, [(0,0),(6,.5),(9.9,6),(10.8,6),(10.805,0)])
        self.denorm = Denorm(self.input)
        self.disto = Disto(self.denorm, drive=.99, slope=.9, mul=self.distoFade)
        self.dc = DCBlock(self.disto)
        self.outDistoLp = Biquad(self.dc, freq=3000).out()
        self.outDistoHigh = Biquad(self.dc, freq=3500, q=2.5, type=2, mul=self.distoHighFade).out()

        self.trigOn = TrigFunc(self.start, self.on)
        self.trigStop = TrigFunc(self.distoFade['trig'], self.stop)

    def openOffSwitch(self):
        self.off = True

    def on(self):
        self.denorm.play()
        self.disto.play()
        self.dc.play()
        self.outDistoLp.out()
        self.outDistoHigh.out()

    def stop(self):
        self.denorm.stop()
        self.disto.stop()
        self.dc.stop()
        self.outDistoLp.stop()
        self.outDistoHigh.stop()
        if self.off:
            self.distoFade.stop()
            self.distoHighFade.stop()

class RunHighSines:
    def __init__(self, sirenSwitch, num=20):
        self.num = num
        self.sirenSwitch = sirenSwitch

        self.fades = Fader(fadein=5, fadeout=30, dur=[35]*num, mul=self.sirenSwitch*.01)
        self.trems = Sine(freq=[rnd(8,16) for i in range(num)], mul=.5, add=.5)
        self.sines = Sine(freq=[rnd(8000, 12000) for i in range(num)], mul=self.fades*self.trems).out()

    def play(self):
        self.sines.freq = [rnd(8000, 12000) for i in range(self.num)]
        self.fades.play(dur=21, delay=[rnd(0, 10) for i in range(self.num)])

    def stop(self):
        self.fades.stop()
        self.trems.stop()
        self.sines.stop()

class RunBell:
    def __init__(self, TM, TAPS, start, invAmpSwitch, finalFadeout, num=8):
        self.w1 = [90,80,50,60]
        self.w2 = [60,70,90,80]
        self.w3 = [60,60,80,90]
        self.slowDown = False
        self.start = start
        self.invAmpSwitch = invAmpSwitch
        self.ampSwitch = 1. - self.invAmpSwitch
        self.finalFadeout = finalFadeout
        self.relativeAmp = Sig(self.ampSwitch, mul=.95, add=.05)
        self.feedback = Sig(self.invAmpSwitch, mul=.198, add=.8)
        self.env = ExpTable([(0,0),(60,1),(300,.25),(8191,0)])
        self.mBell = Beat(time=TM, taps=TAPS, w1=self.w1, w2=self.w2, w3=self.w3, poly=1).play()
        self.amp = TrigEnv(self.mBell, self.env, self.mBell['dur'], mul=self.mBell['amp']).stop()
        self.globalAmp = TrigLinseg(self.start, [(0,0),(.001,1),(1,1)], mul=self.relativeAmp*.25)
        self.noise = Noise(self.amp).stop()
        self.vibrato = Sine(freq=[4.5,4.87,5.34,5.67], mul=[rnd(10,30) for i in range(4)], 
                            add=[midiToHz(101)*random.uniform(.995,1.005) for i in range(4)]).stop()
        self.bell = Phaser(self.noise, freq=self.vibrato, spread=[random.uniform(1.4,1.6) for i in range(4)], 
                           q=0.5, feedback=self.feedback, num=num, mul=self.globalAmp).stop()
        self.bellHp = Biquad(self.bell, freq=1000, q=.5, type=1, mul=self.finalFadeout).stop()

    def activate(self):
        self.amp.play()
        self.noise.play()
        self.vibrato.play()
        self.bell.play()
        self.bellHp.out()

    def change(self):
        self.mBell.fill()
        if self.slowDown:
            for i in range(4):
                if self.w1[i] > 30:
                    self.w1[i] -= 10
                if self.w2[i] > 20:
                    self.w2[i] -= 10
                if self.w3[i] > 10:
                    self.w3[i] -= 10
            self.mBell.setWeights(self.w1, self.w2, self.w3)   
        self.mBell.new()

    def openSlowDownSwitch(self):
        self.slowDown = True

class RunNoise:
    def __init__(self):
        self.fade = Fader(fadein=40, mul=.1).play()
        self.noise = Noise(self.fade)
        self.noiseLp = Biquad(self.noise, freq=2000)
        self.noiseHp = Biquad(self.noiseLp, freq=200, type=1)

    def getOutput(self):
        return self.noiseHp    

RES = 'off'
ATTR = {'off': {'sr': 44100, 'bufsize': 512, 'audio': 'offline', 'fm': 4, 'sines': 4, 'wind': 4, 'punch': 4, 'strings': 8, 'bell': 4}}

TITLE = 'Run [radio edit]'
ARTIST = 'Olivier Bélanger'
DURATION = 725

s = Server(sr=ATTR[RES]['sr'], nchnls=2, buffersize=ATTR[RES]['bufsize'], duplex=0, audio=ATTR[RES]['audio']).boot()
s.recordOptions(dur=DURATION, filename='radiopyo.ogg')

s.amp = .25

#s.setStartOffset(300)


### Constants ###
TM = .1125
TAPS = 16
BASS_SEQ = [[3,3,6,4], [6,6,4], [3,3,2,8]]
SCALES = [[0,2,3,7,10],[0,3,5,8,10],[0,2,7,8,10]]

### Timing ###
minutes = -1
def sectionControl():
    global minutes
    minutes += 1
    # if (minutes % 2) == 0:
    #     print 'Elapsed time: ', minutes/2, 'minutes'
    if minutes == 1:
        rSiren.play()
    elif minutes == 2:
        rSines.play()    
    elif minutes == 4:
        rSiren.play()
    elif minutes == 5:
        rSines.play()   
    elif minutes == 6:
        rStringsDuet.play()  
    elif minutes == 8:
        rBell.activate()        
    elif minutes == 10:
        rSiren.play()
    elif minutes == 11:
        rDisto.openOffSwitch()
        rPunch.openOffSwitch()
        rSines.play()    
    elif minutes == 12:
        sirenSwitch.value = 0        
    elif minutes == 13:
        rSiren.play()
    elif minutes == 14:
        rSines.play()    
        rStrings.play()
        ampSwitch.value = 0
        invAmpSwitch.value = 1
        rBell.openSlowDownSwitch()
    elif minutes == 17:
        rKick.stop()
        rWind.stop()
        rSines.stop()
        rSiren.stop()
    elif minutes == 20:
        finalFadeout.value = 0
        fmFinalFadeout.value = 0

mainTime = Metro(time=30).play()
mainFunc = TrigFunc(mainTime, sectionControl)

barTime = Metro(TM*TAPS).play()
barCount = Counter(barTime, max=1000)
eightBarCount = Counter(barTime, max=8)
changeFreqSelect = Select(eightBarCount)
startDisto = Select(barCount, value=[50, 90, 154, 210]).mix(1)
closeDisto = SDelay(startDisto, delay=10.799, maxdelay=11)

countCloseDisto = Counter(closeDisto)
startBell = Select(countCloseDisto, 2)
bassSwitch = Counter(startBell+Trig().play(), min=0, max=2)

ampSwitch = SigTo(value=1, time=60, init=1)
invAmpSwitch = SigTo(value=0, time=70, init=0)
fmTranspo = Sig(ampSwitch, mul=.75, add=.25)
sirenSwitch = SigTo(value=1, time=120, init=1)
finalFadeout = SigTo(value=1, time=120, init=1)
fmFinalFadeout = SigTo(value=1, time=90, init=1)

### Processes ###
rFm = RunFm(TM, TAPS, changeFreqSelect, fmTranspo, countCloseDisto, fmFinalFadeout, bassSwitch, ATTR[RES]['fm'])
rKick = RunKick(TM, TAPS, BASS_SEQ, changeFreqSelect, ampSwitch, bassSwitch, startDisto+closeDisto)
rDisto = RunDisto(rFm.getOutput(), startDisto)
rSines = RunHighSines(sirenSwitch, ATTR[RES]['sines'])
rBell = RunBell(TM, TAPS, startBell, invAmpSwitch, finalFadeout, ATTR[RES]['bell'])
rNoise = RunNoise()
rWind = RunWind(rNoise.getOutput(), ampSwitch, countCloseDisto, ATTR[RES]['wind'])
rSiren = RunSiren(rNoise.getOutput(), sirenSwitch)
rPunch = RunPunch(rNoise.getOutput(), closeDisto, ATTR[RES]['punch'])
rStrings = RunStrings(TM, TAPS, SCALES, invAmpSwitch, finalFadeout, ATTR[RES]['strings'])
rStringsDuet = RunStringsDuet(TM, TAPS, SCALES, ATTR[RES]['strings'])
rStringsTotal =  rStrings.getOut() + rStringsDuet.getOut() + rWind.getOutput() + rSiren.getOutput() + rPunch.getOutput()
rOutRev = WGVerb(Denorm(rStringsTotal), feedback=.95, cutoff=5000, bal=.5, mul=1).out()

### Events callback ###
x1, thresh1 = 0, 4
def callback():
    global x1, thresh1
    x1 += 1
    if (x1 % thresh1) == 0:
        rKick.change()
        rFm.change()
        rBell.change()
        x1 = 0
        thresh1 = random.randint(1, 4) * 4

tt = TrigFunc(rFm.getBarEnd(), callback)

s.start()
#s.gui(locals())
