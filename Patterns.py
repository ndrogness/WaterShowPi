#!/usr/bin/env python


import sys
import time
import random


###########################################################
def Pulse(PulseOptionsString,SolenoidMatrix,Solenoids,TimeSequence) :

#AtTime(ms)|Pattern(On,Off,Toggle,Pulse,Sequence,Tilt)|PatternOptions|SolenoidMatrix|Duration(ms)
#2000|Pulse|gap:500|S1=0,S2:1,S3:0,S4:1|17000
#20000|Sequence|gap:500|S1:1,S2:2,S3:3,S4:4|10000
#40000|On|revert:yes|S5,S8|5000
#50000|Off|revert:no|S0,S4|10000
#60000|Tilt|angle:45|S0,S4|10000

  PulseGap=500 
  PulseOptions=PulseOptionsString.split(",")

  for i in range(0,len(PulseOptions)):
    PulseOption=PulseOptions[i].split(":")

    if PulseOption[0] == 'gap' :
      PulseGap=PulseOption[1]

  print("Pulse received with string:",SolenoidMatrix)
  print(Solenoids)
######################################################
