#!/usr/bin/env python
# encoding: utf-8
"""
Template for a RadioPyo song (version 1.0).
"""
from pyo import *

################### USER-DEFINED VARIABLES ###################
### READY is used to manage the server behaviour depending ###
### of the context. Set this variable to True when the     ###
### music is ready for the radio. TITLE and ARTIST are the ###
### infos shown by the radio player. DURATION set the      ###
### duration of the audio file generated for the streaming.###
##############################################################
READY = True          # Set to True when ready for the radio
TITLE = "Altair"    # The title of the music
ARTIST = "J T Hutton (hipnofoo)"  # Your artist name
DURATION = 360          # The duration of the music in seconds
##################### These are optional #####################
GENRE = "Electronic"    # Kind of your music, if there is any
DATE = 2016             # Year of creation

####################### SERVER CREATION ######################
if READY:
    s = Server(duplex=0, audio="offline").boot()
    s.recordOptions(dur=DURATION, filename="sys.argv[1]", fileformat=7)
else:
    s = Server(duplex=0).boot()

##################### PROCESSING SECTION #####################
# global volume (should be used to control the overall sound)
fade = Fader(fadein=0.01, fadeout=10, dur=DURATION).play()


################## Altair ####################
# An homage to Louis & Bebe Baron 

######## Krell ############
# rumble
rf = Randi(min=[2,3], max=60, freq=2)
lf2 = LFO(freq=rf, sharp=1, type=0, mul=.5, add=0)
sd1 = SmoothDelay(lf2, delay=.03, feedback=.85, crossfade=.1, maxdelay=1, mul=.8)

######## Robby ############
# basic pulse output
m = Cloud(4)    .play()
t = LinTable(list=[(0,0),(0,1),(1,1),(1,0),(1000,0)],size=1000)
ab = TrigEnv(m, table=t, dur=.5, interp=1, mul=1)
ed = TrigRand(m, min=50, max=500)
os = LFO(freq=ed, sharp=0.50, type=3, mul=ab)
sd2 = SmoothDelay(os, delay=.05, feedback=.9, crossfade=.05, maxdelay=1, mul=.2)

####### Morbius ############
# two delays fed back to each other
env = Linseg([(0,0),(.2,1),(.2,0)])  .play(delay=5)
a = LFO(Randh([100,110],400,1), sharp=1, type=5, mul=env)
dt = Randi(min=.001, max=.45, freq=[.21,.43], mul=1)
d = Delay(a, delay=dt, feedback=0, mul=.5)
r = (d[0]+d[1])/2
f = Follower2(r, risetime=.2, falltime=.2, mul=.1)
ret = Log(f)*r
d.input = ret+a  # return output
dc = DCBlock(d, mul=1)
sd3 = Mix(dc, 2, mul =.2)

###########################
# mixers
fl = Follower2(sd3, risetime=.2, falltime=.2, mul=1, add=0)
gt = Gate(sd3, thresh=-60, risetime=3, falltime=3, lookahead=5.00, outputAmp=True, mul=1)
mx1 = Mix(sd2, mul=Abs(1-gt))
ph = Phasor(freq=.02, phase=0, mul=1.4, add=0)
tr = Port(Floor(ph), risetime=.3, falltime=1, init=0, mul=1)
sl = Selector([mx1+sd3,sd1], voice=tr, mul=1)
cm = Compress(sl, thresh=-8, ratio=2, risetime=0.01, falltime=0.10, mul=fade)    .out()


#################### START THE PROCESSING ###################
s.start()
if not READY:
    s.gui(locals())
