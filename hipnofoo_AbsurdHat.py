#!/usr/bin/env python
# encoding: utf-8

from pyo import *

################### USER-DEFINED VARIABLES ###################
### READY is used to manage the server behaviour depending ###
### of the context. Set this variable to True when the     ###
### music is ready for the radio. TITLE and ARTIST are the ###
### infos shown by the radio player. DURATION set the      ###
### duration of the audio file generated for the streaming.###
##############################################################
READY = True           # Set to True when ready for the radio
TITLE = "The Absurd Hat"    # The title of the music
ARTIST = "JT Hutton (hipnofoo)"  # Your artist name
DURATION = 240          # The duration of the music in seconds
##################### These are optional #####################
GENRE = "Electronic"    # Kind of your music, if there is any
DATE = 2015            # Year of creation

####################### SERVER CREATION ######################
if READY:
    s = Server(duplex=0, audio="offline").boot()
    s.recordOptions(dur=DURATION, filename="radiopyo.ogg", fileformat=7)
else:
    s = Server(duplex=0).boot()


##################### PROCESSING SECTION #####################
# global volume (should be used to control the overall sound)
fade = Fader(fadein=0.001, fadeout=10, dur=DURATION).play()


######### The Absurd Hat ############

# Init ##########
ff = Fader(fadein=5, fadeout=5, dur=DURATION, mul=1, add=0).play()
tpo = 8.0
# delay ##########
vo = Linseg([(0,1), (tpo,0)], loop=True, initToFirstVal=False) .play()
sl = SineLoop(freq=Randh(20,120,tpo), feedback=.3, mul=.5*vo, add=0)     
gl = Port(Randh(min=.01, max=.4, freq=.125), .1, .1)
bh = Port(RandInt(max=2, freq=1/tpo, mul=1), .01, .01)   
dd = Delay(sl, delay=gl, feedback=.97, mul=bh)
co = Compress(dd, thresh=-10, ratio=50, mul=1, add=0)
cd = Clip(co, min=-.8, max=.8, mul=1, add=0) 
   

# pulsar ###########
lf = Port(Randh(min=.1, max=.9, freq =5), .01, .01)
w = SawTable(order=2, size=8192)
e = HannTable()
fr = Xnoise(dist=6, freq=2/tpo, x1=3, mul=30, add=20)
gh = Port(RandInt(max=2, freq=2/tpo, mul=1),.01, .01)                 
a = Pulsar(table=w, env=e, freq=fr, frac=lf, mul=gh)        

# blit pulse #########
cl = Cloud(2, poly=2)   .play()
lfo = Port(TrigRand(cl, min=9, max=100, init=20),.01,.01)
b = Blit(freq=[9.5,7], harms=lfo, mul=Abs(1-gh))     

# mix ###############
mx = Mix((a+b+cd)/3.0, voices=2, mul=ff*2)  .out()
# end ###############

#################### START THE PROCESSING ###################
s.start()
if not READY:
    s.gui(locals())
