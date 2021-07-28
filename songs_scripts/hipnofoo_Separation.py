#!/usr/bin/env python
# encoding: utf-8

from pyo import *
import sys

################### USER-DEFINED VARIABLES ###################
### READY is used to manage the server behaviour depending ###
### of the context. Set this variable to True when the     ###
### music is ready for the radio. TITLE and ARTIST are the ###
### infos shown by the radio player. DURATION set the      ###
### duration of the audio file generated for the streaming.###
##############################################################
READY = True          # Set to True when ready for the radio
TITLE = "Separation"    # The title of the music
ARTIST = "JT Hutton (hipnofoo)"  # Your artist name
DURATION = 220          # The duration of the music in seconds
##################### These are optional #####################
GENRE = "Electronic"    # Kind of your music, if there is any
DATE = 2015             # Year of creation

####################### SERVER CREATION ######################
if READY:
    s = Server(duplex=0, audio="offline").boot()
    s.recordOptions(dur=DURATION, filename=sys.argv[1], fileformat=7)
else:
    s = Server(duplex=0).boot()

##################### PROCESSING SECTION #####################
# global volume (should be used to control the overall sound)
fade = Fader(fadein=0.001, fadeout=10, dur=DURATION).play()


########## Separation ###########

ff = Fader(fadein=5, fadeout=10, dur=DURATION, mul=1, add=0)    .play()

########## rhythmic cloud (trigs) using percent 

tpo = .25
m = Metro(time=tpo, poly=3)  .play()
mpc = Percent(m, [100/2.,100/4.,300/4.])  # even divisions
env = TrigLinseg(mpc, [(0,0),(.005,1),(.01,0)], mul=.9, add=0)
aa = Sine([540,720,120], mul=env)
dd = Delay(aa, delay=0.5, feedback=.25, maxdelay=1, mul=1, add=0)

####### pulses through waveguide #########

m2= Metro(time=tpo, poly=2)     .play()
mp2 = Percent(m2, [100/12.,100/8.,100/12.,100/8.]) 
t = LinTable(list=[(0,0),(20,0),(21,1),(50,0),(1000,0)],size=1000)
a2 = TrigEnv(mp2, table=t, dur=.2, interp=1, mul=1)    
fq = [120,135,180,217]
wg = Waveguide(a2, freq=fq, dur=3, minfreq=20, mul=.7)

######### resonant filter ############

nn = Noise(mul=.7)
lfo = LFO(freq=[1/8.,1/12.,1/16.,1/24.], sharp=1, type=2, mul=.5, add=.5) .play(delay=15)
lfp = Port(lfo, 2, 1)
fr = [360,405,720,868]
f = Resonx(nn, freq=fr, q=20, stages=4, mul=lfp*5)

######## out ##########
pan = Pan((dd+wg+f)/3., pan=.5, mul=ff)     .out()
#### end ##############

#################### START THE PROCESSING ###################
s.start()
if not READY:
    s.gui(locals())
