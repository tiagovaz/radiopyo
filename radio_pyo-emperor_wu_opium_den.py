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
TITLE = "Emporer Wu's Opium Den"    # The title of the music
ARTIST = "Filtercreed"  # Your artist name
DURATION = 377          # The duration of the music in seconds
##################### These are optional #####################
GENRE = "Electronic/Psybient" # Kind of your music, if there is any
DATE = 2017                   # Year of creation

####################### SERVER CREATION ######################
if READY:
    s = Server(duplex=0, audio="offline").boot()
    s.recordOptions(dur=DURATION, filename=sys.argv[1], fileformat=7)
else:
    s = Server(duplex=0).boot()

##################### PROCESSING SECTION #####################
# global volume (should be used to control the overall sound)
fade = Fader(fadein=0.01, fadeout=10, dur=DURATION).play()

######################
## major variables: ##
######################

BASE_PITCH = 200
EDO = 5
mynotes = range(EDO+1)
myocts = [.25, .5, 1, 2]
mydetunes = [x/3.5 for x in [1, 1, 2, 3, 5, 8]]

mybelldurs = [.2, .33, .5, 1, 1, 2, 3, 5, 8]
myblitdurs = [8, 13, 21, 34, 55, 89]

myamps = [1/13., 1/8., 2/13., 1/5., 1/3., 1/2.]

myFMmods = [1.0031, 1.5002, 2.0201, 2.2501, 3.0013, 5.011, 8.003]

mypans = [0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85]

###########################
## end of variable setup ##
###########################

#####################
#####################
## FM bells stuff ###
#####################
#####################

# main trigger event, a statistical 'cloud' of time-event triggers.
# density is determined by an average events-per-second in the 
# 'density' parameter.
bell_cloud = Cloud(density=1.4, poly=16).play(delay=5)

# choose a duration randomly:
bell_dur_ch = TrigChoice(bell_cloud, mybelldurs)
# choose a random amp:
bell_amp_ch = TrigChoice(bell_cloud, myamps)

# envelope, whose length is influenced by the duration choice:
bell_tab = ExpTable([(0,0), (32, .5), (8191,0)], exp=3.4)
bell_env = TrigEnv(bell_cloud, table=bell_tab, dur=bell_dur_ch,
                   mul=.25*bell_amp_ch)

############################
# iteration through notes: #
############################
bell_note = TrigChoice(bell_cloud, mynotes)
bell_oct_ch = TrigChoice(bell_cloud, myocts)
bell_det_ch = TrigChoice(bell_cloud, mydetunes)
# pitch is a combination of strands cycling through 'mynotes', and a 
# random octave register choice:
bell_pitch = Pow(base=2, exponent=bell_note/EDO, mul=BASE_PITCH * bell_oct_ch)

# the color of the sound (bright/clangorous, etc.) is determined by the choice 
# of FM modulation ratio:
bell_rat_ch = TrigChoice(bell_cloud, myFMmods)
bell_pan_ch = TrigChoice(bell_cloud, mypans)

# our sound source is an FM object. Notice that its volume AND 
# modulation index are both influenced by the 'env' object
bell1 = FM(carrier=bell_pitch, ratio=bell_rat_ch, index=bell_env+0.5,
           mul=bell_env)
bell2 = FM(carrier=bell_pitch+bell_det_ch, ratio=bell_rat_ch, 
           index=bell_env+0.5, mul=bell_env)
bell_pan1 = Pan(bell1, pan=bell_pan_ch)
bell_pan2 = Pan(bell2, pan=1-bell_pan_ch)
bell_mix = Mix(bell_pan1+bell_pan2, voices=2)

################
################
## BLIT stuff ##
################
################

# main trigger event, a statistical 'cloud' of time-event triggers.
# density is determined by an average events-per-second in the 
# 'density' parameter.
blit_cloud = Cloud(density=0.7, poly=24).play()

# choose a duration randomly:
blit_dur_ch = TrigChoice(blit_cloud, myblitdurs)
# choose a random amp:
blit_amp_ch = TrigChoice(blit_cloud, myamps)

# envelope, whose length is influenced by the duration choice:
blit_tab = ExpTable([(0,0), (2731, .5), (5461, .5), (8191,0)], exp=3.4)
blit_env = TrigEnv(blit_cloud, table=blit_tab, dur=blit_dur_ch,
                  mul=.25*blit_amp_ch)

############################
# iteration through notes: #
############################
blit_note = TrigChoice(blit_cloud, mynotes)
blit_oct_ch = TrigChoice(blit_cloud, myocts)
blit_det_ch = TrigChoice(blit_cloud, mydetunes)
# pitch is a combination of strands cycling through 'mynotes', 
# and a random octave register choice:
blit_pitch = Pow(base=2, exponent=blit_note/EDO, mul=BASE_PITCH * blit_oct_ch)

# the color of the sound (bright/clangorous, etc.) is determined by the 
# choice of FM modulation ratio:
blit_rat_ch = TrigChoice(blit_cloud, myFMmods)
blit_pan_ch = TrigChoice(blit_cloud, mypans)

# our sound source is an FM object. Notice that its volume AND modulation 
# index are both influenced by the 'env' object
blit_rat_ch_var = blit_rat_ch * 3.0
blit1 = Blit(freq=blit_pitch, harms=blit_rat_ch_var, mul=blit_env)
blit2 = Blit(freq=blit_pitch+blit_det_ch, harms=blit_rat_ch_var, mul=blit_env)
blit_pan1 = Pan(blit1, pan=blit_pan_ch)
blit_pan2 = Pan(blit2, pan=1-blit_pan_ch)
blit_mix = Mix(blit_pan1+blit_pan2, voices=2)

############
## OUTPUT ##
############

verb = Freeverb(bell_mix+blit_mix, 0.9, damp=0.2, bal=0.8, mul=fade).out()

## parameter changes near the end:
def callback():
    bell_cloud.density = 0.7 
    blit_cloud.density = 0.45

call = CallAfter(callback, 300)

#################### START THE PROCESSING ###################
s.start()
if not READY:
    s.gui(locals())
