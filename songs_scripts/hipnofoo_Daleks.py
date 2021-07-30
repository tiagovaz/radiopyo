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
READY = True           # Set to True when ready for the radio
TITLE = "Daleks"        # The title of the music
ARTIST = "J T Hutton (hipnofoo)"  # Your artist name
DURATION = 420          # The duration of the music in seconds
##################### These are optional #####################
GENRE = "Electronic"    # Kind of your music, if there is any
DATE = 2016             # Year of creation

if __name__ == "__main__":
    ####################### SERVER CREATION ######################
    if READY:
        s = Server(duplex=0, audio="offline").boot()
        s.recordOptions(dur=DURATION, filename=sys.argv[1], fileformat=7)
    else:
        s = Server(duplex=0).boot()

    ##################### PROCESSING SECTION #####################
    # global volume (should be used to control the overall sound)
    fade = Fader(fadein=0.001, fadeout=10, dur=DURATION).play()


    ############### Daleks! ##################
    # Dedicated to Delia Derbyshire and the others at the BBC Radiophonic Workshop
    import random

    m = Metro(.9, poly=1)  .play()
    pc = Percent(m, percent=40)

    ######### trig burst with ramp ##########
    burst = TrigBurst(pc, time=.05, count=1, expand=1, ampfade=1, poly=1) # variable trig burst
    def changeburst():
        burst.time = random.uniform(.05, .5)
        burst.expand = random.uniform(.5, 2)
        burst.count = random.randint(2, 15)
    tf = TrigFunc(pc, changeburst)

    # freq ramp
    t1 = TrigXnoise(pc, dist=6, x1=1, mul=2, add=-1)   # change ramp amt (+-1)
    ts = TrigRand(pc, min=.01, max=1, port=0) # var ramp speed
    tab = LinTable(list=[(0,1), (8191,-1.)], size=8192)
    t2 = TrigEnv(pc, tab, dur=ts, interp=2, mul=t1, add=1) # ramp freq +-)   # t1 can reverse this line
    bf = TrigRand(burst, min=60, max=1000) # base freq 

    # rand 'sharp'
    t3 = TrigXnoise(pc, dist=6, x1=1, mul=1) # var for osc 'sharp'
    t4 = TrigRand(pc, min=.01, max=.5) # var for env 'dur'

    ######## env and osc ##########
    ev = ExpTable([(0,0),(200,1),(8191,0)], exp=2)
    vol = Randi(min=0, max=.4, freq=1.00, mul=1, add=0)
    env = TrigEnv(burst, ev, dur=t4, interp=2, mul=vol) 
    osc = RCOsc(freq=t2*bf, sharp=t3, mul=env)
    dl = Delay(osc, ts/2., .7) 

    tp = TrigRand(pc, min=0, max=1, port=.1)
    p = Pan(dl+osc, pan=tp, spread=0, mul=fade)      .out()


    #################### START THE PROCESSING ###################
    s.start()
    if not READY:
        s.gui(locals())
