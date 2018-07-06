#!/usr/bin/env python

#from time import sleep

import RPi.GPIO as GPIO
import time
import random

# for GPIO numbering, choose BCM  
GPIO.setmode(GPIO.BCM)  


#For Pi 3
Solenoids=[17,27,22,10,9,11,13,26,23]
DelayBetween=1
S_OFF=1
S_ON=0

# or, for pin numbering, choose BOARD  
#GPIO.setmode(GPIO.BOARD)  


for i in range(len(Solenoids)):
  GPIO.setup(Solenoids[i], GPIO.OUT)
  GPIO.output(Solenoids[i], S_OFF)
  
try:
  
  while True :

    for i in range(len(Solenoids)):
      GPIO.output(Solenoids[i], S_ON)
      print "Solenoid",Solenoids[i],"is S_ON"
      time.sleep(DelayBetween)                 # wait

      GPIO.output(Solenoids[i], S_OFF)
      print "Solenoid",Solenoids[i],"is S_OFF"
      time.sleep(DelayBetween)                 # wait

    for i in range(len(Solenoids)):
      GPIO.output(Solenoids[i], S_ON)
    
    print "All Solenoids are S_ON"
    time.sleep(DelayBetween)                 # wait

    for i in range(len(Solenoids)):
      GPIO.output(Solenoids[i], S_OFF)

    print "All Solenoids are S_OFF"
    time.sleep(DelayBetween)                 # wait 
    
    for i in range(len(Solenoids)):
      GPIO.output(Solenoids[i], S_ON)
      print "Solenoid",Solenoids[i],"is S_ON"
      time.sleep(DelayBetween)                 # wait

    for i in range(len(Solenoids)):
      GPIO.output(Solenoids[i], S_OFF)

    print "All Solenoids are S_OFF"
    time.sleep(DelayBetween)                 # wait 

except KeyboardInterrupt:
  GPIO.cleanup()

