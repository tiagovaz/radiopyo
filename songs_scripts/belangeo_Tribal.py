#!/usr/bin/env python
# encoding: utf-8
"""
Template for a RadioPyo song (version 1.0).

A RadioPyo song is a musical python script using the python-pyo 
module to create the audio processing chain. You can connect to
the radio here : http://radiopyo.acaia.ca/ 

There is only a few rules:
    1 - It must be a one-page script.
    2 - No soundfile, only synthesis.
    3 - The script must be finite in time, with fade-in and fade-out 
        to avoid clicks between pieces. Use the DURATION variable.

belangeo - 2014

"""
from pyo import *
import sys, random, math

################### USER-DEFINED VARIABLES ###################
### READY is used to manage the server behaviour depending ###
### of the context. Set this variable to True when the     ###
### music is ready for the radio. TITLE and ARTIST are the ###
### infos shown by the radio player. DURATION set the      ###
### duration of the audio file generated for the streaming.###
##############################################################
READY = True            # Set to True when ready for the radio
TITLE = "Tribal"        # The title of the music
ARTIST = "belangeo"     # Your artist name
DURATION = 210          # The duration of the music in seconds
##################### These are optional #####################
GENRE = "Electronic"    # Kind of your music, if there is any
DATE = 2018             # Year of creation

####################### SERVER CREATION ######################
if READY:
    s = Server(duplex=0, audio="offline").boot()
    s.recordOptions(dur=DURATION, filename=sys.argv[1], fileformat=7)
else:
    s = Server(duplex=0).boot()

##################### PROCESSING SECTION #####################
TAPS = 24
GAMME = [2, 3, 5, 7, 8]
TEMPO = .13

class DidjeFormant:
    def __init__(self, input, length, d2, modes, num):
        modes = modes
        num = num
        amp = 1.+(math.sqrt(((modes+1)-num)/modes))

        f1 = (num - 0.5) * 340 / (4 * length)
        f2 = f1 * ((1+(1+((4*(d2-0.2))/(9.869585*0.2*((num-0.5)**2))))**0.5))
        if f2 < 10:
            f2 = 10
        elif f2 > 20000:
            f2 = 20000

        self.jit = Rossler(pitch=0.2, chaos=0.9, mul=0.05, add=1)
        self.filt = Resonx(input, f2, 20*self.jit, 3, mul=amp)

    def sig(self):
        return self.filt

class Didjeridu:
    def __init__(self, input, freq=80, length=1.5, pressure=0.9, formant=500, modes=20):
        if length < 0.1:
            length = 0.1
        self.pressure = Sig(pressure)
        self.formant = Sig(formant)
        d2 = 0.2 + (9.869585 * 0.2 / 16) * (((((8. * freq * length) / 340.) - 1)**2) - 1)

        self.lowpress = Clip(self.pressure, 0, .5, mul=0.1, add=0.95)
        self.pressscl = self.pressure * 0.2 + 0.8
        self.freqrand = Sig(Randi(-0.003, 0.003, 16) + Randi(-0.005, 0.005, 4.65) + Randi(-0.01, 0.01, .421), add=1)
        self.sine = Sine(freq*self.freqrand*self.lowpress, mul=0.5, add=0.5)
        self.pressrand = Sig(Randi(-0.002, 0.002, 15) + Randi(-0.005, 0.005, 2.76) + Randi(-0.008, 0.008, .12), add=1)
        self.press = Clip(self.pressscl*self.pressrand, 0, 1)
        self.excite = Disto(self.sine, self.press, slope=0.01, mul=self.press)
        self.shelf = EQ(self.excite, freq=430, q=2, boost=20*Log10(self.pressrand), type=1)
        self.peak = EQ(self.shelf, self.formant, q=1.5, boost=6)

        # self.peak * live_signal + self.peak * 0.2
        self.formants = [DidjeFormant(self.peak*input+self.peak*0.2, length, d2, modes, i+1) for i in range(modes)]
        self.output = sum([f.sig() for f in self.formants])

    def sig(self):
        return self.output

# Fire
class FireLayer:
    def __init__(self, cfreq=1000):
        self.noise = Noise([1,1])
        # Hissing
        self.hissamp = Pow(Tone(self.noise, freq=1, mul=10), 4, mul=600)
        self.hissing = Atone(self.noise, freq=1000, mul=self.hissamp)
        self.hissout = Clip(self.hissing, -0.9, 0.9)
        # Crackles
        self.cracktable = LinTable(list=[(0, 1.0), (8191, 0.0)])
        self.cracktrig = Cloud(density=2, poly=4).play()
        self.crackdur = TrigRand(self.cracktrig, min=0.001, max=0.04)
        self.crackfreq = TrigRand(self.cracktrig, min=400, max=8000) # min=200
        self.crackamp = Pow(TrigEnv(self.cracktrig, self.cracktable, dur=self.crackdur), 2)
        self.crackband = ButBP(self.noise, freq=self.crackfreq, q=1, mul=self.crackamp)
        self.crackout = ButHP(self.crackband, 500).mix(2)
        # Lapping
        self.lappamp = Randi(min=0.5, max=1., freq=Randi(min=0.3, max=1., freq=1))
        self.lappbp = MoogLP(self.noise, freq=60, res=0.7, mul=50)
        self.lappout = ButHP(self.lappbp, freq=20, mul=self.lappamp)
        # Mixing
        # I reduce lappout volume the give a little more freedom to other bass sounds!
        self.mixed = (self.hissout * 0.1 + self.crackout * 0.4 + self.lappout * 0.1)
        self.output = ButBP(self.mixed, freq=cfreq, q=0.3, mul=0.2).mix(1).mix(2)

    def out(self):
        self.output.out()
        return self

    def sig(self):
        return self.output

class Fire:
    def __init__(self, freqs=[600, 1200, 2600, 6000], cutoff=1000, mul=1):
        self.layers = [FireLayer(f) for f in freqs]
        self.output = Tone(sum([l.sig() for l in self.layers]), freq=cutoff, mul=mul)

    def out(self):
        self.output.out()
        return self

    def sig(self):
        return self.output

# Wind
class RZero:
    def __init__(self, input, coeff, mul=1):
        self.output = Sig(input - coeff * Delay1(input), mul=mul)

    def sig(self):
        return self.output

class WindSpeed:
    def __init__(self, freq=0.1):
        # Wind speed variation
        self.speedvar = Sine(Randi(0.75, 1.25, 0.1, mul=freq), mul=0.25, add=0.25)

        # Wind gust
        self.gust1 = Atone(ButLP(Noise(), freq=0.5), freq=0.1, mul=50)
        self.gust2 = Pow(self.speedvar + 0.5, 2, add=-0.125)
        self.windgust = self.gust1 * self.gust2

        # Wind squall
        self.squall1 = Atone(ButLP(Noise(), freq=3), freq=0.1, mul=20)
        self.squall2 = Pow(Max(self.speedvar, comp=0.4, add=-0.4) * 8, 2)
        self.windsquall = self.squall1 * self.squall2

        # Output
        self.output = Clip(self.speedvar+self.windgust+self.windsquall, 0, 1)

    def sig(self):
        return self.output

class AmbientNoise:
    def __init__(self, windspeed, mul=1):
        self.base = windspeed + 0.2
        self.noise = ButBP(PinkNoise(), 800, 1, mul=self.base)
        self.sweep = RZero(self.noise, Clip(self.base * 0.6, 0, 0.99), 0.2)
        self.output = SPan(self.sweep.sig(), pan=0.5, mul=mul)

    def sig(self):
        return self.output

class Whistling:
    def __init__(self, windspeed, mul=1):
        self.noise = Noise()
        # left
        self.leftspeed = SDelay(windspeed, delay=0.1, maxdelay=0.1)
        self.leftamp = Pow(self.leftspeed+0.12, 2, mul=1.2)
        self.left = ButBP(self.noise, self.leftspeed*400+600, 60, self.leftamp)
        self.leftout = SPan(self.left, pan=0.2)
        # right
        self.rightspeed = SDelay(windspeed, delay=1)
        self.rightamp = Pow(self.rightspeed, 2, mul=2)
        self.right = ButBP(self.noise, self.rightspeed*1000+1000, 60, self.rightamp)
        self.rightout = SPan(self.right, pan=0.8)
        # output
        self.output = Sig(self.leftout + self.rightout, mul=mul)

    def sig(self):
        return self.output

class TreeLeaves:
    def __init__(self, windspeed, mul=1):
        self.noise = PinkNoise()
        # left
        self.leftbase = Tone(SDelay(windspeed, delay=1.2, maxdelay=1.2), freq=0.1)
        self.leftamp = Pow(self.leftbase, 2)
        self.leftfilt = Tone(Atone(self.noise, 200), self.leftamp*3000+300, mul=self.leftamp)
        self.leftout = SPan(self.leftfilt, pan=0.15)
        # right
        self.rightbase = Tone(SDelay(windspeed, delay=2.4, maxdelay=2.4), freq=0.1)
        self.rightamp = Pow(self.rightbase, 2)
        self.rightfilt = Tone(Atone(self.noise, 400), self.rightamp*5000+500, mul=self.rightamp)
        self.rightout = SPan(self.rightfilt, pan=0.85)
        # output
        self.output = Sig(self.leftout + self.rightout, mul=mul)

    def sig(self):
        return self.output

class Howling:
    def __init__(self, windspeed, delay=0.1, freq=400, pan=0.5, mul=1):
        self.noise = Noise()
        self.base = SDelay(windspeed, delay, delay)
        thresh = random.uniform(0.2, 0.3)
        self.clip = Clip(self.base, thresh, thresh+0.25, add=-thresh)
        self.curve = Tone(Cos(((self.clip*2)-0.25)*6.283185307179586), 0.15)
        self.filter = ButBP(self.noise, freq, 40, mul=self.curve)
        self.osc = Sine(self.curve*freq*0.5+30, mul=self.filter*2)
        self.output = SPan(self.osc, pan=pan, mul=mul)

    def sig(self):
        return self.output

class Wind:
    def __init__(self, speedfactor=0.5, mul=1):
        self.windspeed = WindSpeed(speedfactor * 0.2 + 0.001)
        self.ambient = AmbientNoise(self.windspeed.sig(), 0.5)
        self.whistling = Whistling(self.windspeed.sig(), 0.4)
        self.treeleaves = TreeLeaves(self.windspeed.sig(), 0.15)
        self.howling1 = Howling(self.windspeed.sig(), 0.1, 400, 0.1, 0.5)
        self.howling2 = Howling(self.windspeed.sig(), 0.3, 200, 0.5, 0.5)
        self.howling3 = Howling(self.windspeed.sig(), 0.5, 500, 0.9, 0.5)
        self.output = Sig(self.ambient.sig() + self.whistling.sig() + 
                          self.treeleaves.sig() + self.howling1.sig() +
                          self.howling2.sig() + self.howling3.sig(), mul=mul)

    def out(self):
        self.output.out()
        return self

# Instruments.
class Perc:
    def __init__(self, octave=4, w1=80, w2=50, w3=30, mul=1, fill=True):
        self.octave = octave
        self.offset = 0
        self.switch = 1
        self.env = CosTable(list=[(0, 0.0), (64, 1.0), (128,1.0),
                                  (1024, 0.), (5000, 0.), (8191, 0.0)])
        if octave != 3 and fill:
            self.change = TrigFunc(Metro(TEMPO*TAPS*6).play(), self.onRezChange)

        self.beat = Beat(time=TEMPO, taps=TAPS, w1=w1, w2=w2, w3=w3, poly=1).play()
        self.amp = Denorm(TrigEnv(self.beat, self.env, dur=self.beat["dur"],
                                  mul=self.beat["amp"]))
        self.switcher = Sig(self.switch)
        self.first = Port(1-self.switcher, risetime=0.001, falltime=0.001, init=0)
        self.second = Port(self.switcher, risetime=0.001, falltime=0.001, init=0)
        if octave == 3:
            feed = 0.95
            self.freq1 = Sig(midiToHz(octave * 12))
            self.freq2 = Sig(midiToHz(octave * 12))
        else:
            feed = 0.85
            self.freq1 = Sig(midiToHz(random.choice(GAMME) + octave * 12))
            self.freq2 = Sig(midiToHz(random.choice(GAMME) + octave * 12))
        self.osc1 = AllpassWG(self.amp, freq=self.freq1, feed=feed, detune=0.70,
                              minfreq=20, mul=mul*self.first)
        self.osc2 = AllpassWG(self.amp, freq=self.freq2, feed=feed, detune=0.70,
                              minfreq=20, mul=mul*self.second)

        self.out1 = Biquadx(self.osc1, freq=self.freq1*0.9, q=2, type=1, stages=2)
        self.out2 = Biquadx(self.osc2, freq=self.freq2*0.9, q=2, type=1, stages=2)
        self.output = self.out1 + self.out2

        self.c = 0
        if octave != 3 and fill:
            self.tf = TrigFunc(self.beat["end"], self.onEnd)
            self.change = TrigFunc(Metro(TEMPO*TAPS*6).play(), self.onRezChange)

    def out(self):
        self.output.out()
        return self

    def stop(self):
        self.beat.stop()

    def sig(self):
        return self.output

    def onEnd(self):
        self.c += 1
        if (self.c % 6) == 5:
            self.beat.fill()
            self.beat.new()

    def onRezChange(self):
        self.switch = 1 - self.switch
        self.switcher.value = self.switch
        self.later = CallAfter(self.onFreqChange, time=1)

    def onFreqChange(self):
        f = midiToHz(random.choice(GAMME) + (self.octave + self.offset) * 12)
        if random.randint(0, 3) == 0:
            if self.switch == 0:
                self.freq2.value = f
            else:
                self.freq1.value = f

    def setEnvelope(self, newlist):
        self.env.replace(newlist)

    def setFeed(self, which):
        self.osc1.reset()
        self.osc2.reset()
        if which == 0:
            if self.octave == 3:
                feed = 0.95
            else:
                feed = 0.85
            det = 0.7
            self.offset = 1
        else:
            if self.octave == 3:
                feed = 0.83
            else:
                feed = 0.65
            det = 0.2
            self.offset = 0
        self.osc1.feed = feed
        self.osc2.feed = feed
        self.osc1.detune = det
        self.osc2.detune = det

class SmallBell:
    def __init__(self, octave=4, w1=80, w2=50, w3=30, mul=1):
        self.octave = octave
        self.switch = 1
        self.env = CosTable(list=[(0, 0.0), (32, 1.0), (64,0.0), (8191, 0.0)])

        self.change = TrigFunc(Metro(TEMPO*TAPS*6).play(), self.onRezChange)

        self.beat = Beat(time=TEMPO, taps=TAPS, w1=w1, w2=w2, w3=w3, poly=1).play()
        self.amp = TrigEnv(self.beat, self.env, dur=self.beat["dur"],
                           mul=self.beat["amp"])
        self.switcher = Sig(self.switch)
        self.first = Port(1-self.switcher, risetime=0.001, falltime=0.001, init=0)
        self.second = Port(self.switcher, risetime=0.001, falltime=0.001, init=0)
        self.freq1 = Sig(midiToHz(random.choice(GAMME) + octave * 12))
        self.freq2 = Sig(midiToHz(random.choice(GAMME) + octave * 12))

        self.noise = Denorm(Noise(self.amp))
        self.osc1 = Phaser(self.noise, freq=self.freq1, spread=1.1726, q=0.5,
                           feedback=0.9988, num=10, mul=mul*self.first*0.0357)
        self.osc2 = Phaser(self.noise, freq=self.freq2, spread=1.1726, q=0.5,
                           feedback=0.9988, num=10, mul=mul*self.second*0.0357)

        self.output = Biquadx(self.osc1+self.osc2, freq=300, q=0.7, type=1, stages=2)

        self.c = 0
        self.tf = TrigFunc(self.beat["end"], self.onEnd)
        self.change = TrigFunc(Metro(TEMPO*TAPS*6).play(), self.onRezChange)

    def out(self):
        self.output.out()
        return self

    def stop(self):
        self.beat.stop()

    def sig(self):
        return self.output

    def onEnd(self):
        self.c += 1
        if (self.c % 6) == 5:
            self.beat.fill()
            self.beat.new()

    def onRezChange(self):
        self.switch = 1 - self.switch
        self.switcher.value = self.switch
        self.later = CallAfter(self.onFreqChange, time=1)

    def onFreqChange(self):
        f = midiToHz(random.choice(GAMME) + self.octave * 12)
        if random.randint(0, 3) == 0:
            if self.switch == 0:
                self.freq2.value = f
            else:
                self.freq1.value = f

    def setEnvelope(self, newlist):
        self.env.replace(newlist)

def changeResonance(x, amp):
    for v in [v0, v1, v2, v3, v4]:
        v.setFeed(x)
    percamp.value = amp

def stopRhythm():
    for v in [v0, v1, v2, v3, v4]:
        v.stop()
    for b in [b1, b2, b3, b4]:
        b.stop()

### Timing ###
stopcaller = None
bcount = 0
def barCount():
    global bcount, stopcaller
    if bcount == 0:
        fireamp.value = 1.0
        windamp.value = 1.0
    elif bcount == 11:
        percintroamp.value = 1.0
    elif bcount == 12:
        percintroamp.value = 0.0
        percamp.value = 1.5
    elif bcount == 18:
        changeResonance(1, 2.0)
        bellamp.value = 1.0
    elif bcount == 24:
        changeResonance(0, 1.5)
        bellamp.value = 0.0
    elif bcount == 30:
        changeResonance(1, 2.0)
        bellamp.value = 1.0
    elif bcount == 34:
        for v in [v1, v2, v3, v4]:
            v.beat.setWeights(w1=100, w2=100, w3=70)
            v.beat.new()
    elif bcount == 35:
        percamp.time = 3
        percamp.value = 3.5
        for i, v in enumerate([v1, v2, v3, v4]):
            v.beat.setWeights(w1=percweights[i][0],
                              w2=percweights[i][1],
                              w3=percweights[i][2])
            v.beat.new()
    elif bcount == 36:
        bellamp.value = 0.0
        didjeamp.value = 1.0
        percamp.time = 0.0001
        percamp.value = 1.4
        for v in [v0, v1, v2, v3, v4]:
            v.setFeed(0)
            v.offset = 0
    elif bcount == 48:
        changeResonance(1, 2.5)
        bellamp.value = 1.0
    elif bcount == 53:
        for i, v in enumerate([v1, v2, v3, v4]):
            v.beat.setWeights(w1=80, w2=70, w3=70)
            v.beat.new()
    elif bcount == 54:
        changeResonance(0, 2.0)
        percamp.time = 3
        percamp.value = 2.1
        bellamp.value = 0.0
    elif bcount == 58:
        for v in [v1, v2, v3, v4]:
            v.beat.setWeights(w1=100, w2=100, w3=70)
            v.beat.new()
    elif bcount == 60:
        didjeamp.value = 0
        stopcaller = CallAfter(stopRhythm, time=.12)
    elif bcount == 64:
        fireamp.time = 10.0
        windamp.time = 10.0
        fireamp.value = 0.0
        windamp.value = 0.0
    bcount += 1

bar = Metro(time=TEMPO*TAPS).play()
barfunc = TrigFunc(bar, barCount)

### Layers ###
# Wind
windamp = SigTo(0.0, time=10, mul=0.15)
wind = Wind(speedfactor=0.25, mul=windamp).out()

# Fire
fireamp = SigTo(0.0, time=10, mul=1)
fire = Fire(freqs=[600, 1200, 2600, 6000], cutoff=1000, mul=fireamp).out()

# Perc intro
percintroamp = SigTo(0.0, time=0.0001)
percintro = Perc(octave=6, w1=100, w2=100, w3=0, mul=percintroamp, fill=False)
percintropan = Pan(percintro.sig(), pan=0.5, mul=1.)

# Perc jam
percweights = [[100,40, 0], [80, 50, 30], [40, 80, 40], [40, 40, 80]]
percamp = SigTo(0.0, time=0.0001)
v0 = Perc(octave=3, w1=100, w2=0, w3=0, mul=0.12)
v1 = Perc(octave=4, w1=100, w2=40, w3=0, mul=0.3)
v2 = Perc(octave=5, w1=80, w2=50, w3=30, mul=0.4)
v3 = Perc(octave=6, w1=40, w2=80, w3=40, mul=0.6)
v4 = Perc(octave=7, w1=40, w2=40, w3=80, mul=0.8)
percmix = Mix([v0.sig(), v1.sig(), v2.sig(), v3.sig(), v4.sig()], voices=5)
percpan = Pan(percmix, pan=[0.5, 0.3, 0.7, 0.1, 0.9], mul=percamp)
perccomp = Compress(percpan, thresh=-20, ratio=8, risetime=0.005,
                    falltime=0.05, lookahead=4.00, knee=0.5, mul=1.1)

# Small bells
bellamp = SigTo(0.0, time=0.0001, mul=0.075)
b1 = SmallBell(octave=5, w1=100, w2=33, w3=20, mul=0.5)
b2 = SmallBell(octave=6, w1=50, w2=60, w3=20, mul=0.5)
b3 = SmallBell(octave=6, w1=40, w2=80, w3=20, mul=0.5)
b4 = SmallBell(octave=7, w1=80, w2=40, w3=20, mul=0.5)
bellmix = Mix([b1.sig(), b2.sig(), b3.sig(), b4.sig()], voices=4)
bellpan = Pan(bellmix, pan=[0.35, 0.65, 0.1, 0.9], mul=bellamp)

# Didjeridu
didjeamp = SigTo(0.0, time=0.07, mul=0.17)
press = LFO(freq=0.39, sharp=0.1, type=5, mul=0.1, add=0.82)
form = LFO(freq=0.78, sharp=0.85, type=0, mul=750, add=1250)
input = LFO(freq=32.70319, sharp=0.3, type=1, mul=Sine(0.195, mul=0.15, add=0.15))
inputeq = EQ(input, freq=Sine(0.1, mul=200, add=500), q=3, boost=6.00)
didjeridu = Didjeridu(inputeq, freq=65.406389, length=1.8, pressure=press,
                      formant=form, modes=32)
didjeout = ButHP(Sig(didjeridu.sig(), mul=didjeamp), freq=70).mix(2)

denormal = Denorm(percintropan + perccomp + bellpan + didjeout)
rev = STRev(denormal, inpos=[0, 1], revtime=1, cutoff=5000, bal=0.1).out()

#################### START THE PROCESSING ###################
s.start()
if not READY:
    s.gui(locals())
