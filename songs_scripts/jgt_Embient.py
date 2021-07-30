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
import random

################### USER-DEFINED VARIABLES ###################
### READY is used to manage the server behaviour depending ###
### of the context. Set this variable to True when the     ###
### music is ready for the radio. TITLE and ARTIST are the ###
### infos shown by the radio player. DURATION set the      ###
### duration of the audio file generated for the streaming.###
##############################################################
READY = True         # Set to True when ready for the radio
TITLE = "Embient"    # The title of the music
ARTIST = "JGT"       # Your artist name
DURATION = 105    # The duration of the music in seconds
##################### These are optional #####################
GENRE = "Electronic"   # Kind of your music, if there is any
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
    fade = Fader(fadein=0.001, fadeout=6, dur=DURATION).play()


    #GENERATOR#
    class OscAug:
        def __init__(self, table, phs=.1, ofrq=45, allfeed=.01, dur=0, mul=0.5):
            #Fader pour gerer les clicks.
            self.fade = Fader(fadein=1, fadeout=1, dur=dur, mul=mul)
            #Automation
            self.oaut = Sine(freq=phs, mul=0.5, add=0.5)
            self.allaut = Sine(freq=allfeed, mul=0.25, add=0.75)
            self.daut = Sine(freq=.1, mul=0.005, add=0.010)
            #SigTo - Pour gerer les changements de frequences
            self.freq = SigTo(value=ofrq, time=0.005, init=ofrq)
            #Oscillateur avec table 
            self.osc = Osc(table, freq=self.freq, phase=self.oaut, mul=0.15)
            #AllPass applique a Osc.
            self.alw = AllpassWG(self.osc.mix(2), freq=50, feed=self.allaut, detune=0.21)
            #Compression du signal avant l'envoi.
            self.comp = Compress(self.alw, thresh=-10, ratio=10, mul=self.fade)
            #Delai court/reverb pour rajouter de la couleur.
            self.dela = Delay(self.comp, delay=self.daut, mul=self.fade)
            self.dverb = WGVerb(self.dela, feedback=0.95, cutoff=1800, bal=0.8, mul=mul)
            #Objs.
            self.objs = self.comp + self.dela + self.dverb

        def out(self, chnl=0):
            "Out basique pour objet de type trame"
            self.objs.out(chnl)
            self.fade.play()
            return self

        def stop(self):
            "Methode pour arreter la sortie audio initiale"
            self.fade.stop()
            self.objs.stop()
            return self
            
        def play(self):
            "Play pour objet qui necessite des changements d'amplitudes rapides"
            self.fade.play()
            return self

        def playm(self, x):
            "Choix de note selon 12 <= x <= 127 (MIDI)"
            self.freq.value = midiToHz(x)
            self.fade.play()
            return self

        def setofrq(self, x):
            "Change la frequence de l'oscillateur"
            self.freq.value = x

        def sFade(self, x, y):
            "Ajustement du fadein et fadeout"
            self.fade.fadein = x
            self.fade.fadeout = y
            
        def sig(self):
            "Retourne le signal audio de la classe, pour le post-traitement."
            return self.objs

        def tesot(self):
            "test"
            self.alw.out()
            self.fade.play()
            return self

    class DM:
        def __init__(self, table, ffrq=500, f1=0, f2=1, q=2, of=1000, feedback=0.6, bal=0.3, mul=1):
            self.fadn = Fader(fadein=0.001, fadeout=0.1, dur=0.1001, mul=mul)
            self.osc = Osc(table, freq=of).mix(2)
            self.nos = Noise(mul=self.fadn)
            self.filt1 = Biquad(self.nos*self.osc, freq=ffrq, q=q, type=f1)
            self.filt2 = Biquad(self.filt1, freq=ffrq, q=q, type=f2)
            self.dverb = WGVerb(self.filt1+self.filt2, feedback=feedback, bal=bal)

        def play(self):
            self.fadn.play()
            self.dverb.out()
            return self

        def splay(self):
            self.fadn.play()
            return self

        def stop(self):
            self.fadn.stop()
            self.dverb.stop()

        def sig(self):
            "Retourne le signal audio de la classe, pour le post-traitement."
            return self.dverb

        def sFeedb(self, x):
            "Change la valeur de feedback de la reverb"
            self.dverb.feedback = x
            
        def sMul(self, x):
            "Change la valeur du volume."
            self.fadn.mul = x
            
        def tail(self):
            self.fadn.stop()
            self.osc.stop()


    #DEVELOPPEMENT #

    #Table pour OscAug#
    tab = CurveTable(list=[(0, 0), (250, 0.1), (500, 0.25), (1000, 0.075), (1500, 0.1), (2000, 0.7), (3000, 0.7), 
                                    (4096, 0.3), (5000, 0.1), (6100, 0.15), (7000, 0.1), (8191, 0.0)])
                                    
    tab2 = CurveTable(list=[(0, 0), (250, 0.7), (500, 0.25), (1000, 0.075), (1500, 0.1), (2000, 0.7), (3000, 0.7), 
                                        (4096, 0.3), (5000, 0.1), (6100, 0.15), (7000, 0.1), (8191, 0.0)])

    tab3 = CurveTable(list=[(0, 0), (250, 0.1), (500, 0.15), (1000, 0.2), (1500, 0.3), (2000, 0.4), (3000, 0.5), 
                                        (4096, 0.8), (5000, 0.5), (6100, 0.375), (7000, 0.2), (8191, 0.0)])
    #Table pour Rythme
    tabd = CurveTable(list=[(0,0.7), (1024, 0.3), (2048, 0.3), (4096, 0.8), (6144, 0.05), (8192, 0)])

    ###################
    ##SECTION OBJET AUDIO##
    ###################

    #Graves
    autog1 = Sine(0.1).range(0.1, 0.20)
    autog2 = Sine(0.05).range(0.15, 0.22)
    og = OscAug(tab, phs=.05, ofrq=50, dur=93, mul=autog1)
    og2 = OscAug(tab, phs=.01, ofrq=101, dur=85, mul=autog2)
    og3 = OscAug(tab3, phs=.07, allfeed=.05, ofrq=51, dur=101, mul=0.27).out()

    #Melo
    om = OscAug(tab2, phs=0.28, ofrq=midiToHz(53), allfeed=10, dur=4.5, mul=0.25)
    om2 = OscAug(tab2, phs=0.35, ofrq=midiToHz(56), allfeed=8, dur=4.5, mul=0.25)
    om.sFade(1.2, 2.3); om2.sFade(1.2, 2.3)

    #Rythme principal.
    autdrm = Sine(0.09).range(0, 0.5)
    autof1 =Sine(40).range(20, 1000)
    drm = DM(tabd, ffrq=1000, f1=0, f2=1, of=autof1, mul=autdrm)
    #Rthm B.
    autdrb = Sine(.5).range(250, 400)
    autof2 =Sine(40).range(20, 120)
    drb = DM(tabd, ffrq=autdrb, f1=0, f2=0, of=autof2, mul=0.7)
    drbverb = WGVerb(drb.sig(), feedback=0.8, bal=0.3).out()

    #Rythm cymb.
    autof3 = Sine(30).range(200, 2000)
    dcmb = DM(tabd, ffrq=350, f1=1, f2=3, of=autof3, mul=0.3)
    rcfad = Fader(fadein=0.1, fadeout=0.1, dur=0.1001)
    filtest1 = Tone(dcmb.sig(), freq=4500, mul=rcfad).out()

    ################
    #GESTION DES EVENTS#
    ################

    list = [53, 55, 56, 58, 60, 61, 63, 65, 67, 68, 70, 72, 73, 75]
    count = 0
    cf = 0
    prate = 0
    lastind = 7
    z = 6
    x = 6

    def drum():
        drm.play()

    def dbass():
        drb.play()

    def dcymb():
        dcmb.splay()
        rcfad.play()

    def melo():
        global count, prate, lastnote, lastind, z, x
        prate += 1
        if prate <= 5:
            if count == 0:
                om.out()
                if lastind > 1 and lastind < 12:
                    z = random.randint(-2, 2) + lastind
                    note = list[z]
                    om.playm(note)
                    lastind = z
                elif lastind <= 1:
                    z = random.randint(2, 5) + lastind
                    note = list[z]
                    om.playm(note)
                    lastind = z
                elif lastind >= 12:
                    z = random.randint(-5, -2) + lastind
                    note = list[z]
                    om.playm(note)
                    lastind = z
                count += 1
            elif count == 1:
                om2.out()
                if lastind > 1 and lastind < 12:
                    x = random.randint(-2, 2) + lastind
                    note = list[x]
                    om2.playm(note)
                    lastind = x
                elif lastind <= 1:
                    x = random.randint(2, 5) + lastind
                    note = list[x]
                    om2.playm(note)
                    lastind = x                
                elif lastind >= 12:
                    x = random.randint(-5, -2) + lastind
                    note = list[x]
                    om2.playm(note)
                    lastind = x
                count -= 1
        elif prate > 7 and prate < 10:
            om.stop(); om2.stop()
        elif prate >= 10:
            prate -= 10

    def event_0():
        pass
    def event_1():
        pass
    def event_2():
        og.out()
        btdb.play()
    def event_3():
        patr.play()
    def event_4():
        btcmb.play()
        og2.out()
    def event_5():
        btdb.stop()
    def event_6():
        btdb.play()
    def event_7():
        drm.sFeedb(0.75)
    def event_8():
        btcmb.stop()
        patr.stop()
    def event_9():
        btcmb.play()
        btdb.play()
    def event_10():
        pass
    def event_11():
        drm.sFeedb(0.8)
        patr.play()
    def event_12():
        btdb.stop()
        btcmb.stop()
    def event_13():
        pass
    def event_14():
        drm.sFeedb(0.95)
        patr.stop()
        btcmb.play()
    def event_15():
        btdb.play()
    def event_16():
        pass
    def event_17():
        btcmb.stop()
    def event_18():
        pass
    def event_19():
        btcmb.play()
    def event_20():
        drm.sFeedb(0.65)
        patr.play()
        btcmb.stop()
    def event_21():
        pass
    def event_22():
        btcmb.play()
    def event_23():
        pass
    def event_24():
        patm.stop()
        patr.stop()
        btdb.stop()
        btcmb.stop()
    def event_25():
        pass
    def event_26():
        m.stop()
    def event_27():
        pass
        
    ##############
    #SECTION PATTERN#
    ##############

    #Pattern de la pi�ce
    m = Metro(4).play()
    c = Counter(m, min=0, max=26)
    sc = Score(c)

    #Trig pour melo
    patm = Pattern(function=melo, time=2).play()

    #Trig Drum Principal
    patr = Pattern(function=drum, time=0.125)

    #Trig Drum Bass
    btdb = Beat(time=.125, taps=16, w1=70, w2=50, w3=35)
    patb = TrigFunc(btdb, function=dbass)

    #Trig Drum Cymb.
    btcmb = Beat(time=.125, taps=16, w1=10, w2=20, w3=25)
    patc = TrigFunc(btcmb, function=dcymb)

    #################### START THE PROCESSING ###################
    s.start()
    if not READY:
        s.gui(locals())
