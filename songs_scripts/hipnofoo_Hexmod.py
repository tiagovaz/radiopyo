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
import sys

################### USER-DEFINED VARIABLES ###################
### READY is used to manage the server behaviour depending ###
### of the context. Set this variable to True when the     ###
### music is ready for the radio. TITLE and ARTIST are the ###
### infos shown by the radio player. DURATION set the      ###
### duration of the audio file generated for the streaming.###
##############################################################
READY = True           # Set to True when ready for the radio
TITLE = "Hexmod"    # The title of the music
ARTIST = "J.T.Hutton (hipnofoo)"  # Your artist name
DURATION = 210          # The duration of the music in seconds
##################### These are optional #####################
GENRE = "Electronic"    # Kind of your music, if there is any
DATE = 2015             # Year of creation

if __name__ == "__main__":
    ####################### SERVER CREATION ######################
    if READY:
        s = Server(duplex=0, audio="offline").boot()
        s.recordOptions(dur=DURATION, filename=sys.argv[1], fileformat=7)
    else:
        s = Server(duplex=0).boot()

    ##################### PROCESSING SECTION #####################

    ######### Hexmod ############

    h = Fader(fadein=0.01, fadeout=.1, dur=DURATION, mul=1, add=0)    .play()

    e = Phasor(freq=.3, phase=0, mul=200, add=0)

    x = SineLoop(80+e, feedback=.3, mul=.2) 

    m = Randi(min=0.001, max=.9, freq=1, mul=1, add=0)

    o = Delay(x, delay=m, feedback=.9, mul=1) 

    d = Pan(o, outs=2, pan=m, spread=.3, mul=.5*h, add=0)   .out()

    #################### START THE PROCESSING ###################
    s.start()
    if not READY:
        s.gui(locals())
