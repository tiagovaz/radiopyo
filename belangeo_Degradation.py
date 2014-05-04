#!/usr/bin/python

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

################### USER-DEFINED VARIABLES ###################
### READY is used to manage the server behaviour depending ###
### of the context. Set this variable to True when the     ###
### music is ready for the radio. TITLE and ARTIST are the ###
### infos shown by the radio player. DURATION set the      ###
### duration of the audio file generated for the streaming.###
##############################################################
READY = True           # Set to True when ready for the radio
TITLE = "Degradation"    # The title of the music
ARTIST = "belangeo"  # Your artist name
DURATION = 120          # The duration of the music in seconds

####################### SERVER CREATION ######################
if READY:
    s = Server(duplex=0, audio="offline").boot()
    s.recordOptions(dur=DURATION, filename="radiopyo.ogg", fileformat=7)
else:
    s = Server(duplex=0).boot()


##################### PROCESSING SECTION #####################
# global volume (should be used to control the overall sound)
fade = Fader(fadein=0.001, fadeout=10, dur=DURATION).play()

env = CosTable([(0,0),(40,1),(500,.2),(8191,0)])
env2 = CosTable([(0,0),(20,1),(500,1),(2000,.3),(8191,0)])

met = Metro(.1,8).play()

car = TrigChoice(met.mix(), [50]*12+[75,99]*2+[151], init=50, mul=RandInt(3,.3125,2,4))
ind = SampHold(Clip(Sine(.02, 0, 3, 2), min=0, max=4), met, 1)
amp = TrigEnv(met, env, .25, mul=[1,.5,.5,.5,.7,.5,.5,.5])
fm = FM(car, [.25,.33,.5,.75], ind, amp)
srscl = SampHold(Sine(.05, 0, .06, .1), met.mix(), 1)
deg = Degrade(fm, 32, srscl)
filt = Biquad(deg.mix(2), freq=5000)

low = Biquad(filt, freq=200, mul=.3)
b1 = Biquad(filt, freq=200, q=5, type=2)
b2 = Biquad(filt, freq=500, q=5, type=2)
b3 = Biquad(filt, freq=1000, q=5, type=2)
b4 = Biquad(filt, freq=1700, q=8, type=2)
b5 = Biquad(filt, freq=2500, q=8, type=2)

delb1 = SDelay(b1, delay=.8, maxdelay=1)
delb3 = SDelay(b3, delay=1.6, maxdelay=2, mul=.5)
delb4 = SDelay(b4, delay=3.2, maxdelay=4, mul=.75)
delb5 = SDelay(b5, delay=6.4, maxdelay=7, mul=.75)

total = low+delb1+b2+delb3+delb4+delb5

rev = WGVerb(total, feedback=.75, bal=.15, mul=fade*1.3).out()

rumvol = TrigEnv(met[0]+met[4], env2, .39, mul=.4)
rumble = Rossler(pitch=[.09,.09003], chaos=.25, mul=fade*rumvol).out()
bass = Sine(freq=[40,40], mul=fade*rumvol*.25).out()

#################### START THE PROCESSING ###################
s.start()
if not READY:
    s.gui(locals())
