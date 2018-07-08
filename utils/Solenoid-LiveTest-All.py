#!/usr/bin/env python3

#from time import sleep

import RPi.GPIO as GPIO
import time
import random

# for GPIO numbering, choose BCM  
GPIO.setmode(GPIO.BCM)  

#For Pi 3
#Solenoids=[10,9,11,5,6,13,19,26]
Solenoids=[17,27,22,10,9,11,13]
PumpGPIO=23

DelayBetween=.250
S_OFF=1
S_ON=0


NumSolenoids=len(Solenoids)
print ("Num Solendoids:",NumSolenoids)

GPIO.setup(PumpGPIO, GPIO.OUT)

for i in range(len(Solenoids)):
  GPIO.setup(Solenoids[i], GPIO.OUT)
  GPIO.output(Solenoids[i], S_OFF)
  
GPIO.output(Solenoids[0], S_ON)
GPIO.output(PumpGPIO, S_ON)

try:
  
  while True :

      GPIO.output(Solenoids[0], S_ON)

      for i in range(1,NumSolenoids):
        GPIO.output(Solenoids[0], S_OFF)
        GPIO.output(Solenoids[i], S_ON)
        print ("Solenoid",Solenoids[i],"is S_ON")

        time.sleep(DelayBetween)                 # wait

        GPIO.output(Solenoids[0], S_ON)
        GPIO.output(Solenoids[i], S_OFF)
        print ("Solenoid",Solenoids[i],"is S_OFF")
        time.sleep(DelayBetween)                 # wait

      time.sleep(DelayBetween)                 # wait
      
      for i in range(1,NumSolenoids):
        GPIO.output(Solenoids[0], S_OFF)
        GPIO.output(Solenoids[i], S_ON)
        print ("Solenoid",Solenoids[i],"is S_ON")
        time.sleep(DelayBetween)                 # wait

      time.sleep(DelayBetween)                 # wait

      for i in range(1,NumSolenoids):
        if i == (NumSolenoids-1):
          GPIO.output(Solenoids[0], S_ON)
        GPIO.output(Solenoids[i], S_OFF)
        print ("Solenoid",Solenoids[i],"is S_OFF")
        time.sleep(DelayBetween)                 # wait

      GPIO.output(Solenoids[0], S_ON)

except KeyboardInterrupt:
  GPIO.cleanup()

