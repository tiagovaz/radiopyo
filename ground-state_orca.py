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

Original work by __ground_state__ from 12-2013

"""
from pyo import *
import math, sys  # for `pow`

################### USER-DEFINED VARIABLES ###################
### READY is used to manage the server behaviour depending ###
### of the context. Set this variable to True when the     ###
### music is ready for the radio. TITLE and ARTIST are the ###
### infos shown by the radio player. DURATION set the      ###
### duration of the audio file generated for the streaming.###
##############################################################
READY = True  # Set to True when ready for the radio
TITLE = "Orca"  # The title of the music
ARTIST = "__ground_state__"  # Your artist name
DURATION = 196.535  # The duration of the music in seconds
##################### These are optional #####################
GENRE = "Ambient"  # Kind of your music, if there is any
DATE = 2014  # Year of creation

####################### SERVER CREATION ######################
if READY:
    s = Server(duplex=0, audio="offline").boot()
    s.recordOptions(dur=DURATION, filename=sys.argv[1], fileformat=7)
else:
    s = Server(sr=48000, nchnls=2, buffersize=700, duplex=0, audio='pa').boot()


##################### PROCESSING SECTION #####################
def dbToAmp(db):
    return math.pow(10, 0.05 * db)

# global volume (should be used to control the overall sound)
fade = Fader(fadein=0.001, fadeout=10, dur=DURATION, mul=dbToAmp(-3.0)).play()

class Tempo(object):
    """
    Tempo 1.0
    A simple container for note duration values.
    """

    def __init__(self, bpm):
        self.spb = 60.0 / bpm
        self.quarter = self.spb
        self.eighth = self.quarter / 2.0
        self.six10th = self.eighth / 2.0
        self.thirty2nd = self.six10th / 2.0
        self.sixty4th = self.thirty2nd / 2.0
        self.one28th = self.sixty4th / 2.0
        self.whole = self.quarter * 4.0
        self.minim = self.quarter * 2.0
        self.__float__ = 0.0

    def setTempo(self, bpm):
        # bpm is BPM, example 120 beats per minute.
        self.spb = 60.0 / bpm  # seconds per beat.

class TriTable(PyoTableObject):
    """
    Triangle waveform generator.

    Generates triangle waveforms made up of fixed number of harmonics. Taken
    straight out of the pyo docs.

    :Parent: :py:class:`PyoTableObject`

    :Args:

        order : int, optional
            Number of harmonics triangle waveform is made of. The waveform
            will contain `order` odd harmonics. Defaults to 10.
        size : int, optional
            Table size in samples. Defaults to 8192.

    >>> s = Server().boot()
    >>> s.start()
    >>> t = TriTable(order=15).normalize()
    >>> a = Osc(table=t, freq=[199,200], mul=.2).out()

    """
    def __init__(self, order=10, size=8192):
        PyoTableObject.__init__(self, size)
        self._order = order
        self._tri_table = HarmTable(self._create_list(order), size)
        self._base_objs = self._tri_table.getBaseObjects()
        self.normalize()

    @staticmethod
    def _create_list(order):
        # internal method used to compute the harmonics's weight
        l = []
        ph = 1.0
        for i in range(1, order*2):
            if i % 2 == 0:
                l.append(0)
            else:
                l.append(ph / (i*i))
                ph *= -1
        return l

    def setOrder(self, x):
        """
        Change the `order` attribute and redraw the waveform.

        :Args:

            x : int
                New number of harmonics

        """
        self._order = x
        self._tri_table.replace(self._create_list(x))
        self.normalize()
        self.refreshView()

    @property
    def order(self):
        """int. Number of harmonics triangular waveform is made of."""
        return self._order

    @order.setter
    def order(self, x):
        self.setOrder(x)

class Whale(PyoObject):
    """
    Whale 1.0

    Signal chain:
    lfo -> lfoEnv -> triOsc -> triEnv -> out

    The concept is that of a low-frequency instrument which has a
    delayed-onset vibrato. It is meant to be used at low tempos, to allow
    the vibrato to fade in slowly.

    :Parent: :py:class:`PyoObject`

    :Args:

        freq : PyoObject
            Frequency to generate.
        trig : PyoObject
            A trigger to drive note-ons.
        dur : float
            Time in seconds for the instrument to play once triggered.

    """
    def __init__(self, freq=1000, trig=PyoObject, dur=3.78, mul=1):
        PyoObject.__init__(self, mul)
        self._freq = freq
        self._trig = trig
        self._dur = dur
        self._mul = mul

        freq, trig, dur, mul, lmax = convertArgsToLists(freq, trig, dur, mul)

        # LFO signal chain.
        # This envelope drives the LFO which creates the vibrato effect. Its
        # volume stays very low until just before it ends.
        lfoEnvTable = CosTable([(0, 0.0), (2457, 0.0), (6481, 0.3),
                                (7350, 0.0), (8191, 0.0)])
        # lfoEnvTable.graph()
        self._lfoEnv = TrigEnv(self._trig, lfoEnvTable, dur=self._dur)
        self._lfo = Sine(4.27, mul=self._lfoEnv)

        # Triangle oscillator signal chain.
        triEnvTable = CosTable([(0, 0.0), (1535, 1.0), (2046, 0.95),
                                (6143, 0.95), (8191, 0.0)])
        # triEnvTable.graph()
        self._triEnv = TrigEnv(self._trig, triEnvTable, dur=self._dur)
        # TriTable Table oscillator from the pyo docs.
        triTable = TriTable(order=50, size=24000).normalize()
        self._osc = Osc(triTable, self._freq, interp=4,
                        mul=((self._triEnv + self._lfo) * self._mul))

        self._whale = EQ(self._osc, freq=self._freq * 16, q=1, type=1)

        self._base_objs = self._whale.getBaseObjects()

    def setFreq(self, x):
        """
        Replace the `freq` attribute.

        :Args:

            x : float or PyoObject
                New `freq` attribute.

        """
        self._freq = x

    def setTrig(self, x):
        """
        Replace the `trig` attribute.

        :Args:

            x : PyoObject
                New `trig` attribute.

        """
        self._trig = x
        self._lfoEnv.trig = x
        self._triEnv.trig = x

    def setDur(self, x):
        """
        Replace the `dur` attribute.

        :Args:

            x : PyoObject
                New `dur` attribute.

        """
        self._dur = x
        self._lfoEnv.dur = x
        self._triEnv.dur = x

    @property
    def freq(self):
        """float or PyoObject. Frequency."""
        return self._freq

    @freq.setter
    def freq(self, x):
        self.setFreq(x)

    @property
    def trig(self):
        """PyoObject. Trigger the instrument."""
        return self._trig

    @trig.setter
    def trig(self, x):
        self.setTrig(x)

    @property
    def dur(self):
        """float. Duration in seconds."""
        return self._dur

    @dur.setter
    def dur(self, x):
        self.setDur(x)

    # This doesn't work (causes the LFO to stop working, reason unknown).
    # Hmm...
    # def ctrl(self, map_list=None, title=None, wxnoserver=False):
    #     self._map_list = [SLMapMul(self._mul)]
    #     PyoObject.ctrl(self, map_list, title, wxnoserver)

    def play(self, dur=0, delay=0):
        self._lfoEnv.play(dur, delay)
        self._lfo.play(dur, delay)
        self._triEnv.play(dur, delay)
        self._osc.play(dur, delay)
        return PyoObject.play(self, dur, delay)

    def stop(self):
        self._lfoEnv.stop()
        self._lfo.stop()
        self._triEnv.stop()
        self._osc.stop()
        return PyoObject.stop(self)

    def out(self, chnl=0, inc=1, dur=0, delay=0):
        self._lfoEnv.out(dur, delay)
        self._lfo.out(dur, delay)
        self._triEnv.out(dur, delay)
        self._osc.out(dur, delay)
        return PyoObject.out(self, chnl, inc, dur, delay)

class Aqueous(PyoObject):
    """
    Aqueous 1.0

    This instrument is (loosely) based on a favorite patch from the Analog
    synthesizer device in Ableton Live. Doesn't really sound like the
    original at all, but I like it... Meant for a MIDI range of 30-77.

    Signal chain:
    saw1 -> reson1 -> resonEnv -> ampEnv -> filter -> out
    |________                      ^
            |                      |
    saw2 -> reson2 -> resonEnv --->|

    We have four independent envelopes (reson1Env, reson2Env, amp1Env,
    amp2Env) with slightly different sustain levels/timing. The envelopes are
    the most complex aspect of this instrument. I don't entirely understand
    what goes on here (design by tweak).

    :Parent: :py:class:`PyoObject`

    :Args:

        freq : PyoObject
            Frequency to generate.
        dur : float
            Time in seconds for the instrument to play once triggered.

    """
    def __init__(self, freq=1000, dur=1, mul=1, add=0):
        self._freq = freq
        self._dur = dur
        self._mul = mul
        self._add = add

        # Begin processing.

        # 1st Saw oscillator.
        saw1Table = SawTable(order=50, size=24000).normalize()
        self._saw1 = Osc(saw1Table, self._freq, interp=4, mul=0.6839)
        # Dummy amplitude knobs to split Saw 1 into two paths with independent
        # amplitudes.
        # Out to Reson1.
        saw1Dummy1 = self._saw1 * 1.0
        saw1Dummy1.setMul(0.63)
        # Out to Reson2.
        saw1Dummy2 = self._saw1 * 1.0
        saw1Dummy2.setMul(0.38)

        # 1st Resonant filter.
        # total duration =  note value + 1954ms
        # sustain at 95%
        self._reson1Env = Adsr(1.280, 0.097, 0.95, 0.577, dur=self._dur)
        reson1 = EQ(saw1Dummy1, freq=self._freq, q=100, boost=3.0, type=1,
                    mul=self._reson1Env * 0.7079)
        # Dummy amplitude knob; lets us more easily balance the filter levels.
        reson1Dummy = reson1 * 1.0

        # 2nd Saw oscillator.
        saw2Table = SawTable(order=50, size=24000).normalize()
        self._saw2 = Osc(saw2Table, self._freq / 2, interp=4, mul=0.5433)
        # Dummy amplitude knob to allow mixing with Saw1, going into Reson2.
        saw2Dummy = self._saw2 * 1.0
        saw2Dummy.setMul(0.38)

        # 2nd Resonant filter.
        # total duration =  note value + 1954ms
        # sustain at 53%
        self._reson2Env = Adsr(1.280, 0.097, 0.53, 0.577, dur=self._dur)
        reson2 = EQ(saw1Dummy2 + saw2Dummy, freq=self._freq + 1300, q=100,
                    boost=3.0, type=1, mul=self._reson2Env * 0.7079)
        # Dummy amplitude knob; lets us more easily balance the filter levels.
        reson2Dummy = reson2 * 1.0

        # Amplitude envelopes for the filters.
        # total duration =  note value + 1954ms
        # sustain at %100
        self._amp1Env = Adsr(0.577, 0.097, 1.0, 1.280, dur=self._dur)
        # total duration =  note value + 1862ms
        # sustain at %100
        self._amp2Env = Adsr(0.577, 0.005, 1.0, 1.280, dur=self._dur)

        # Tweak filter levels
        reson1Dummy.setMul(self._amp1Env * 0.3)
        reson2Dummy.setMul(self._amp2Env * 0.4842)

        filtersDummy = reson1Dummy + reson2Dummy

        bpf = ButBP(filtersDummy, freq=325, q=1)

        # Volume knob
        aqueous = Mix(bpf, mul=self._mul)

        self._base_objs = aqueous.getBaseObjects()

    def setFreq(self, x):
        """
        Replace the `freq` attribute.

        :Args:

            x : float or PyoObject
                New `freq` attribute.

        """
        self._freq = x
        self._saw1.freq = x
        self._saw2.freq = x

    @property
    def freq(self):
        """float or PyoObject. Frequency."""
        return self._freq

    @freq.setter
    def freq(self, x):
        self.setFreq(x)

    def __dir__(self):
        return ["freq", "mul", "add"]

    # Works, but not particularly useful. It would be nice to show sliders
    # for some of the muls e.g. the two oscillators...
    # def ctrl(self, map_list=None, title=None, wxnoserver=False):
    #     self._map_list = [SLMap(18.0, 400.0, "log", "reson1 freq",
    #                             self._reson1.freq),
    #                       SLMap(0.00001, 500.0, "log", "reson1 q",
    #                             self._reson1.q),
    #                       SLMapMul(self._reson1.mul),
    #                       SLMap(18.0, 1700.0, "log", "reson2 freq",
    #                             self._reson2.freq),
    #                       SLMap(0.00001, 500.0, "log", "reson2 q",
    #                             self._reson2.q),
    #                       SLMap(18.0, 5000.0, "log", "filter freq",
    #                             self._aqueous.freq),
    #                       SLMapMul(self._mul)]
    #     PyoObject.ctrl(self, map_list, title, wxnoserver)

    def play(self, dur=0, delay=0):
        self._reson1Env.play(dur, delay)
        self._reson2Env.play(dur, delay)
        self._amp1Env.play(dur, delay)
        self._amp2Env.play(dur, delay)
        return PyoObject.play(self, dur, delay)

    def stop(self):
        self._reson1Env.stop()
        self._reson2Env.stop()
        self._amp1Env.stop()
        self._amp2Env.stop()
        return PyoObject.stop(self)

    def out(self, chnl=0, inc=1, dur=0, delay=0):
        self._reson1Env.play(dur, delay)
        self._reson2Env.play(dur, delay)
        self._amp1Env.play(dur, delay)
        self._amp2Env.play(dur, delay)
        return PyoObject.out(self, chnl, inc, dur, delay)

t = Tempo(63.5)  # q=944ms, w=3.776s

metroW = Metro(time=t.whole * 4).play()
metroA = Metro(time=t.whole).play()
noteW = TrigXnoiseMidi(metroW, dist=0, mrange=(30, 41))
noteA = TrigXnoiseMidi(metroA, dist=0, mrange=(42, 83))
snapW = Snap(noteW, choice=[0, 2, 4, 5, 7, 9, 11], scale=1)
snapA = Snap(noteA, choice=[0, 2, 4, 5, 7, 9, 11], scale=1)


w = Whale(snapW, metroW, dur=t.whole, mul=dbToAmp(-9.0))
a = Aqueous(snapA, dur=t.whole * 2, mul=dbToAmp(-12.0))


def noteOn():
    a.play()

playAqueous = Pattern(function=noteOn, time=t.whole * 2).play()

delayW = Delay(w, delay=t.whole, feedback=0.64,
               maxdelay=t.whole, mul=dbToAmp(-6.0))

wetdry = delayW + w + a

volume = wetdry * 1.0

volume.setMul(fade)

rev = STRev(volume, revtime=2, bal=dbToAmp(-7.95), roomSize=1.4).out()

#################### START THE PROCESSING ###################
s.start()
if not READY:
    s.gui(locals())
