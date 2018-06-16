#!/usr/bin/env python

#from time import sleep

import RPi.GPIO as GPIO, time
import sys
import time
import pygame
import random
import os
import Patterns



S_NAME=0
S_ENABLED=1
S_GPIO=2
S_STATUS=3
S_TOGGLE=4

V_OPEN=0
V_CLOSE=1

######## Solenoid Definition ################
#    [Name,Enabled {True|False},GPIO]
S0 = ['S0',True,23]
S1 = ['S1',True,2]
S2 = ['S2',True,3]
S3 = ['S3',True,4]
S4 = ['S4',True,17]
S5 = ['S5',True,27]
S6 = ['S6',True,22]
S7 = ['S7',True,10]
S8 = ['S8',True,9]

Solenoids = [S0,S1,S2,S3,S4,S5,S6,S7,S8]
SD=dict()
#############################################
def InitSolendois ():

  # for GPIO numbering, choose BCM  
  GPIO.setmode(GPIO.BCM)  

  for i in range(0,9):
    # Add CurrentStatus and DoToggle
    Solenoids[i].extend([V_CLOSE,False]) 

    # If enabled, setup GPIO for output
    if Solenoids[i][S_ENABLED]:
      #print 'Enabling S',i 
      SD[Solenoids[i][S_NAME]]=i
      GPIO.setup(Solenoids[i][S_GPIO], GPIO.OUT)
      GPIO.output(Solenoids[i][S_GPIO], V_CLOSE)

  print SD
#time.sleep(2.0);

#######################################

#######################################
def PrintLayout (ShowStatus=True):

  DS=[]
  Line5=""
  Line7=""

  if ShowStatus:
    for i in range(0,5):
      if Solenoids[i][S_STATUS] == V_OPEN :
        DS.insert(i,'O')
      else :
        DS.insert(i,'X')

    if Solenoids[5][S_STATUS] == V_OPEN and Solenoids[6][S_STATUS] == V_CLOSE :
      Line5=' -    O->^->^->^->^--X     -'
    elif Solenoids[5][S_STATUS] == V_CLOSE and Solenoids[6][S_STATUS] == V_OPEN :
      Line5=' -    X--^<-^<-^<-^<-O     -'
    elif Solenoids[5][S_STATUS] == V_OPEN and Solenoids[6][S_STATUS] == V_OPEN :
      Line5=' -    O->^->^><^<-^<-O     -'
    elif Solenoids[5][S_STATUS] == V_CLOSE and Solenoids[6][S_STATUS] == V_CLOSE :
      Line5=' -    X--*--*--*--*--X     -'

    if Solenoids[7][S_STATUS] == V_OPEN and Solenoids[8][S_STATUS] == V_CLOSE :
      Line7=' -    O->^->^->^->^--X     -'
    elif Solenoids[7][S_STATUS] == V_CLOSE and Solenoids[8][S_STATUS] == V_OPEN :
      Line7=' -    X--^<-^<-^<-^<-O     -'
    elif Solenoids[7][S_STATUS] == V_OPEN and Solenoids[8][S_STATUS] == V_OPEN :
      Line7=' -    O->^->^><^<-^<-O     -'
    elif Solenoids[7][S_STATUS] == V_CLOSE and Solenoids[8][S_STATUS] == V_CLOSE :
      Line7=' -    X--*--*--*--*--X     -'

  else :
    for i in range(0,5):
      DS.insert(i,Solenoids[i][0])
    Line5=' -   S5--*--*--*--*--S6    -'
    Line7=' -   S7--*--*--*--*--S8    -'

    #print '       ---------------' 
    #print '      -               -' 
    #print '     -                 -' 
    #print '   S1                   S2' 
    #print '  -                       -' 
    #print ' -    S5--*--*--*--*--S6   -'
    #print '-                           -' 
    #print ' -    S7--*--*--*--*--S8   -'
    #print '  -                       -' 
    #print '   S3                   S4' 
    #print '     -        S0       -' 
    #print '      -               -' 
    #print '       ---------------' 

  os.system("clear")
  print '       ---------------' 
  print '      -               -' 
  print '     -                 -' 
  print '  ',DS[1],'                  ',DS[2]
  print '  -                       -' 
  print Line5
  print '-                           -' 
  print Line7
  print '  -                       -' 
  print '  ',DS[3],'                  ',DS[4]
  print '     -       ',DS[0],'       -' 
  print '      -               -' 
  print '       ---------------' 
  print '         Time:',CurTime

    
#######################################

#######################################
def ServoSetAngle(angle):

    duty = angle / 18 + 2
	GPIO.output(03, True)
	pwm.ChangeDutyCycle(duty)
	sleep(1)
	GPIO.output(03, False)
	pwm.ChangeDutyCycle(0)

#######################################


#######################################
#def ServoSetup:
	#pwm=GPIO.PWM(03,50)
	#pwm.start(0)
	#SetAngle(45)
	#pwm.stop()


#######################################
def SolenoidSend(SolenoidsNextState) :

  for i in range (0,9) :
    if Solenoids[i][S_ENABLED] and Solenoids[i][S_NAME] in SolenoidsNextState :
      if Solenoids[i][S_STATE] <> SolenoidsNextState[Solenoids[i][S_NAME]] :
        print "Changing state from",Solenoids[i][S_STATE]," to",SolenoidsNextState[Solenoids[i][S_NAME]]
        

#######################################
def SequenceProcessor() :

#AtTime(ms)|Pattern(On,Off,Toggle,Pulse,Sequence,Tilt)|PatternOptions|SolenoidMatrix|Duration(ms)
#2000|Pulse|gap:500|S1=0,S2:1,S3:0,S4:1|17000
#20000|Sequence|gap:500|S1:1,S2:2,S3:3,S4:4|10000
#40000|On|revert:yes|S5,S8|5000
#50000|Off|revert:no|S0,S4|10000
#60000|Tilt|angle:45|S0,S4|10000


  Timeline=[]
  
  for i in range(0,len(SequenceData)):
    NextPattern=SequenceData[i].split("|")
    print NextPattern
    if NextPattern[1] == 'Pulse' :
      Patterns.Pulse(NextPattern[2],NextPattern[3],Solenoids,Timeline)



#######################################
def CleanExit():

  #GPIO.cleanup()
  pygame.mixer.stop()
  pygame.mixer.quit()
  exit()
  

#######################################
def Usage():
  print "watershow sequncefile audiofile"
  exit()

#######################################

if len(sys.argv) < 3 :
  Usage()


#Solenoids[1][S_STATUS]=V_CLOSE
#Solenoids[2][S_STATUS]=V_OPEN
#Solenoids[3][S_STATUS]=V_OPEN
#Solenoids[4][S_STATUS]=V_OPEN
#PrintLayout(False)

with open(sys.argv[1],'r') as SequenceFile:
  SequenceData = SequenceFile.read().splitlines()
del SequenceData[0]

InitSolendois()

# Read Sequence file and process it
Pattern=[]
SequenceProcessor() 
#exit()

pygame.mixer.init()
pygame.mixer.music.load(sys.argv[2])
pygame.mixer.music.play()

StartTime = int(round(time.time()*1000))
step       = 1 #ignore the header line
CurTime = 0

while CurTime < 210000 :

  CurTime = int(round(time.time()*1000)) - StartTime
  #print StartTime
  #print CurTime
  fun=CurTime % 8
  Solenoids[fun][S_STATUS]=V_OPEN
  GPIO.output(Solenoids[fun][S_GPIO],V_OPEN)
  PrintLayout()
  Solenoids[fun][S_STATUS]=V_CLOSE
  GPIO.output(Solenoids[fun][S_GPIO],V_CLOSE)
  time.sleep(.500)

  

CleanExit()

#print Solenoids
#GPIO.setmode(GPIO.BCM)



