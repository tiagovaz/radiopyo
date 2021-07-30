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
import sys, random

################### USER-DEFINED VARIABLES ###################
### READY is used to manage the server behaviour depending ###
### of the context. Set this variable to True when the     ###
### music is ready for the radio. TITLE and ARTIST are the ###
### infos shown by the radio player. DURATION set the      ###
### duration of the audio file generated for the streaming.###
##############################################################
READY = True                # Set to True when ready for the radio
TITLE = "Space Invaders"    # The title of the music
ARTIST = "belangeo"         # Your artist name
DURATION = 260              # The duration of the music in seconds
##################### These are optional #####################
GENRE = "Electronic"    # Kind of your music, if there is any
DATE = 2017             # Year of creation

if __name__ == "__main__":
    ####################### SERVER CREATION ######################
    if READY:
        s = Server(duplex=0, audio="offline").boot()
        s.recordOptions(dur=DURATION, filename=sys.argv[1], fileformat=7)
    else:
        s = Server(duplex=0).boot()


    ##################### PROCESSING SECTION #####################
    # global volume (should be used to control the overall sound)
    masterfade = Fader(fadein=0.0001, fadeout=10, dur=DURATION, mul=1.4).play()


    ### Waveform tables ###
    tCustom = HarmTable([0,0,0,0,.2,0,0,0,.3,0,0,.1,0,0,0,.4,0,0,0,.2,0,0,0,0,.1])
    tPulse = HarmTable([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1])
    tSaw4d = HarmTable([1,.35,.2,.1])
    tSaw6d = HarmTable([1,.35,.2,.1,.07,.04])
    tSaw8d = HarmTable([1,.35,.2,.1,.07,.04,.015,.008])
    tSquare3 = SquareTable(3)
    pad1 = PadSynthTable(basefreq=midiToHz(84), spread=0.85, bw=30, bwscl=1.4, nharms=48, damp=0.7)
    pad2 = PadSynthTable(basefreq=midiToHz(84), spread=1.10, bw=10, bwscl=1.2, nharms=48, damp=0.4)
    pad3 = PadSynthTable(basefreq=midiToHz(84), spread=0.99, bw=50, bwscl=1.7, nharms=48, damp=0.5)

    class Intro:
        def __init__(self, dur=76):
            self.fade = Linseg([(0,1.35), (dur-1,1.35), (dur-0.95, 0)]).play(dur=dur)

            self.high_spread = Sine(.03, 0.75, mul=.005, add=.005).play(dur=dur)
            self.high = OscBank(tSquare3, freq=[2495,2505], spread=self.high_spread,
                                num=12, fjit=True, mul=.004).play(dur=dur)

            self.mid_spread = Linseg([(0, .0015), (dur-14, 0)]).play(dur=dur)
            self.mid = OscBank(tCustom, freq=[32.7032,43.6535], spread=self.mid_spread,
                            num=40, mul=.15).play(dur=dur)

            self.rezdev = Randi(min=0, max=.05, freq=[.25,.33,.41,.47]).play(dur=dur)
            self.rezamp = Fader(fadein=5, fadeout=0.5, dur=dur, mul=self.rezdev).play(dur=dur)
            self.rez = Waveguide(self.mid.mix(1), freq=[24.4997,16.35159,48.9994,58.27046], 
                                dur=10, minfreq=10, mul=self.rezamp).play(dur=dur)

            self.bass = OscBank(tSaw4d, freq=[24.5,24.5], spread=0, num=8,
                                fjit=True, mul=.3).play(dur=dur)

            self.intro_mix = (self.mid + self.rez.mix(2) + self.bass + self.high) * self.fade * masterfade
            self.intro_mix.out(dur=dur)

            self.transi_fade = Expseg([(0,0),(25,.1),(25.1,0)], exp=6).play(delay=dur-26, dur=26)
            self.transi = OscBank(tPulse, freq=[10.5,10.8], spread=self.transi_fade*10, slope=.9, 
                                frndf=self.transi_fade*100, frnda=self.transi_fade*4, num=12, 
                                fjit=True, mul=self.transi_fade).play(delay=dur-26, dur=26)
            self.disto_fade = Expseg([(0,0),(25,.99),(25.1,0)], exp=8).play(delay=dur-26, dur=26)
            self.transi_disto = Disto(self.transi, drive=self.disto_fade, slope=0.8,
                                    mul=0.25).play(delay=dur-26, dur=26)
            self.comp = Compress(self.transi+self.transi_disto, thresh=-12, ratio=3, risetime=0.01,
                                falltime=0.10, mul=masterfade).out(delay=dur-26, dur=26)

    class Waves:
        def __init__(self, delay=90, dur=85):
            self.fade = Fader(fadein=.001, fadeout=25, dur=dur, mul=.075).play(delay=delay, dur=dur+1)
            self.fade.setExp(3)
            self.waves = OscBank(tPulse, freq=[32.7032*2,43.6535*2], spread=.0005, num=40,
                                mul=self.fade).play(delay=delay, dur=dur+1)
            self.lfopan = Sine([0.06, 0.075], mul=.15, add=[.25, .75]).play(delay=delay, dur=dur+1)
            self.outgain = Randi(min=0, max=1, freq=[0.8, .95], mul=1, add=0).play(delay=delay, dur=dur+1)
            self.panner = Pan(self.waves, outs=2, pan=self.lfopan, spread=0,
                            mul=self.outgain).play(delay=delay, dur=dur+1)
            self.verb = WGVerb(self.panner, feedback=0.8, cutoff=5000, bal=0.3,
                            mul=masterfade).out(delay=delay, dur=dur+1)

    class Noisy:
        def __init__(self, delay=90, dur=85):
            self.fade = Fader(fadein=.001, fadeout=25, dur=dur, mul=.006).play(delay=delay, dur=dur+1)
            self.fade.setExp(3)
            self.waves = OscBank(tPulse, freq=[16.3516,16.5211], spread=1.4,
                                num=40, mul=self.fade*masterfade).out(delay=delay, dur=dur+1)

    class BigBass:
        def __init__(self, dur, time):
            if dur < 0.15:
                self.env = Linseg([(0,0),(.03,.3),(.05,.3),(.075,.1),(.1,.05),(dur,0)]).play(dur=dur+0.1)
            else:
                self.env = Linseg([(0,0),(.03,.3),(.05,.3),(.1,.1),(dur-.05,.05),(dur,0)]).play(dur=dur+0.1)
            table = tSaw6d
            if time == 0:
                table = tSaw8d
                freq = midiToHz(24)
                amp = 1.5
            elif (time % 2) == 0:
                freq = midiToHz(random.choice([29,31]))
                amp = .9
            else:
                freq = midiToHz(random.choice([29,31,34]))
                amp = .7
            self.osc = OscBank(table, freq=freq, spread=0, num=[8,8], fjit=True,
                            mul=self.env*amp*masterfade).out(dur=dur+0.1)

    class Ride:
        def __init__(self, dur=.12, amp=0):
            stop = dur + 0.1
            amp = random.uniform(.004,.007) * amp
            self.env = Linseg([(0,0),(.01,amp),(.04,amp),(.05,amp*.3),(dur-.01,amp*.3),(dur,0)]).play(dur=stop)
            self.high = OscBank(tPulse, freq=[32.7032,30.3017], spread=1.13, num=32, 
                                fjit=True, mul=self.env*masterfade).out(dur=stop)
            self.dtime = Linseg([(0,random.uniform(.0005, .001)), (dur,random.uniform(.0075, .01))]).play(dur=stop)
            self.delay = Delay(self.high, delay=self.dtime, feedback=0.4).play(dur=stop)
            self.verb = WGVerb(self.delay, feedback=0.85, cutoff=4500, bal=0.35, mul=masterfade).out(dur=stop)

    class Pad:
        def __init__(self, dur, amp=1):
            freq = s.getSamplingRate() / 262144
            self.amp = TableRead(HannTable(), 1/dur, mul=amp).play()
            t = random.choice([pad1, pad2, pad3])
            speed = random.choice(midiToTranspo([60, 62, 65, 67]))
            self.a = Osc(table=t, freq=freq*speed, phase=[0, 0.5], mul=self.amp)
            self.lfopan = Sine(0.1, [random.random() for i in range(2)])
            self.pan = Pan(self.a, pan=self.lfopan)
            self.rev = STRev(self.pan, inpos=[0.1, 0.9], revtime=2, cutoff=5000, bal=0.30, roomSize=1,
                            firstRefGain=-3, mul=0.03*masterfade).out(dur=dur+5)

    class Conclu:
        def __init__(self, dur=76):
            self.dur = dur
            self.fade = Expseg([(0,0), (10,1.35), (dur-10,1.35), (dur, 0)], exp=2).stop()

            self.high_spread = Sine(.03, 0.75, mul=.005, add=.005).stop()
            self.high = OscBank(tSquare3, freq=[3495,3505], spread=self.high_spread, num=12, 
                                fjit=True, mul=.002).stop()

            self.mid_spread = Linseg([(0,.0015), (dur-14,0)]).stop()
            self.mid = OscBank(tCustom, freq=[32.7032,48.9994, 41.20344, 51.913089],
                            spread=self.mid_spread, num=40, mul=.2).stop()
            self.lfopan = Sine([0.06, 0.075], mul=.15, add=[.25, .75]).stop()
            self.outgain = Randi(min=0, max=1.00, freq=[0.8, .95], mul=1, add=0).stop()
            self.panner = Pan(self.mid.mix(2), outs=2, pan=self.lfopan, spread=0, mul=self.outgain).stop()
            self.verb = WGVerb(self.panner, feedback=0.80, cutoff=5000, bal=0.30).stop()

            self.bass = OscBank(tSaw4d, freq=[16.35155,16.35165], spread=0, num=8, fjit=True, mul=.3).stop()

            self.conclu_mix = (self.verb + self.bass + self.high) * self.fade * masterfade

        def play(self):
            self.fade.play(dur=self.dur)
            self.high_spread.play(dur=self.dur)
            self.high.play(dur=self.dur)
            self.mid_spread.play(dur=self.dur)
            self.mid.play(dur=self.dur)
            self.lfopan.play(dur=self.dur)
            self.outgain.play(dur=self.dur)
            self.panner.play(dur=self.dur)
            self.verb.play(dur=self.dur)
            self.bass.play(dur=self.dur)
            self.conclu_mix.out(dur=self.dur)

    bassnotes = []
    ridenotes = []
    padnotes = []
    interval = .14
    bar = True
    tap = 0
    count = 0
    step = 0
    rideamp = 0.0
    played = 0
    def bassseq():
        global tap, count, step, rideamp, bar, played
        if tap == 0:
            count = 0
            step = random.randrange(12,21,4)
            if bar and played <= 16:
                dur = step
            elif played == 20:
                dur = 256
                bass_pat.stop()
                conclu.play()
            else:
                dur = 32 + step
            bassnotes.append(BigBass(dur=dur*interval, time=tap))
            if rideamp < 1.0:
                rideamp += .1
            if played % 4 == 0 and played < 20:
                if played == 16:
                    padamp = 0.5
                else:
                    padamp = 1.0
                padnotes.append(Pad(dur=256*interval, amp=padamp))
        if bar and played <= 16:
            if count == step:
                if (tap % 4) == 0:
                    count = 0
                    step = random.randrange(2,7,2)
                    bassnotes.append(BigBass(dur=step*interval, time=tap))
                else:
                    count = 0
                    smallest = 4 - (int(played / 4) + 1)
                    if smallest < 1: smallest = 1
                    step = random.randint(smallest, 4)
                    if (step + tap) > 32:
                        step = 32 - tap
                    bassnotes.append(BigBass(dur=step*interval, time=tap))

        if (tap % 4) == 0 and played < 20:
            if played > 15:
                rideamp -= .04
            ridenotes.append(Ride(amp=rideamp))

        count += 1
        tap += 1
        if tap == 32:
            played += 1
            tap = 0
            bar = not bar

    intro = Intro(dur=91)
    startpat = 90
    bass_pat = Pattern(bassseq, interval).play(delay=startpat)
    waves = Waves(delay=startpat)
    noisy = Noisy(delay=startpat)
    conclu = Conclu()


    #################### START THE PROCESSING ###################
    s.start()
    if not READY:
        s.gui(locals())
