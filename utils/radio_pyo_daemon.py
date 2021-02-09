#!/usr/bin/python

from os import system
from time import sleep

while True:
    system('/home/tvaz/radiopyo/utils/radio_pyo.py update')
    sleep(1)
