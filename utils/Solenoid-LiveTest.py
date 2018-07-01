#!/usr/bin/env python

#from time import sleep

import RPi.GPIO as GPIO
import time
import random

#For Pi 1
#Solenoids=[2,3,4,17,27,22,10,9]
#For Pi 3
Solenoids=[10,9,11]
DelayBetween=3
S_OFF=1
S_ON=0

# for GPIO numbering, choose BCM  
GPIO.setmode(GPIO.BCM)  
# or, for pin numbering, choose BOARD  
#GPIO.setmode(GPIO.BOARD)  


for i in range(len(Solenoids)):
  GPIO.setup(Solenoids[i], GPIO.OUT)
  GPIO.output(Solenoids[i], S_OFF)
  
GPIO.output(Solenoids[0], S_ON)

try:
  
  while True :

      GPIO.output(Solenoids[0], S_OFF)
      GPIO.output(Solenoids[1], S_ON)
      print "Solenoid",Solenoids[1],"is S_ON"
      time.sleep(DelayBetween)                 # wait

      GPIO.output(Solenoids[0], S_ON)
      GPIO.output(Solenoids[1], S_OFF)
      print "Solenoid",Solenoids[1],"is S_OFF"
      time.sleep(DelayBetween)                 # wait

      GPIO.output(Solenoids[0], S_OFF)
      GPIO.output(Solenoids[2], S_ON)
      print "Solenoid",Solenoids[2],"is S_ON"
      time.sleep(DelayBetween)                 # wait

      GPIO.output(Solenoids[0], S_ON)
      GPIO.output(Solenoids[2], S_OFF)
      print "Solenoid",Solenoids[2],"is S_OFF"
      time.sleep(DelayBetween)                 # wait

      GPIO.output(Solenoids[0], S_OFF)
      GPIO.output(Solenoids[1], S_ON)
      GPIO.output(Solenoids[2], S_ON)
      print "Solenoid",Solenoids[1],"and",Solenoids[2],"are S_ON"
      time.sleep(DelayBetween)                 # wait

      GPIO.output(Solenoids[0], S_ON)
      GPIO.output(Solenoids[1], S_OFF)
      GPIO.output(Solenoids[2], S_OFF)
      print "Solenoid",Solenoids[1],"and",Solenoids[2],"are S_OFF"
      time.sleep(DelayBetween)                 # wait

    

except KeyboardInterrupt:
  GPIO.cleanup()

