#!/usr/bin/env python3

#from time import sleep

import RPi.GPIO as GPIO
import sys
import time
import pygame
import random
import os
import alsaaudio as aa
import wave
import numpy as np
import Patterns



S_NAME=0
S_ENABLED=1
S_GPIO=2
S_STATUS=3
S_TOGGLE=4

P_STATE=0
P_GPIO=1
P_RUN=0
P_STOP=1

V_OPEN=0
V_CLOSE=1

#       [IsRunning,LastPushButtonTime]
STATE = {'ISRUNNING':False,'PUSHBUTTON_LASTTIME':int(round(time.time()*1000))}
print (STATE)
######## Solenoid Definition ################
#    [Name,Enabled {True|False},GPIO]
S0 = ['S0',True,17]
S1 = ['S1',True,27]
S2 = ['S2',True,22]
S3 = ['S3',True,10]
S4 = ['S4',True,9]
S5 = ['S5',True,11]
S6 = ['S6',True,13]

#      [IsRunning {True|False},,GPIO]
Pump = [False,23]

Solenoids = [S0,S1,S2,S3,S4,S5,S6]
NumSolenoids=len(Solenoids)
SD=dict()


#############################################
def PushButton_Callback(channel):


  PushButtonTime=int(round(time.time()*1000))
  #print (STATE,PushButtonTime)

  if not STATE['ISRUNNING'] and PushButtonTime > STATE['PUSHBUTTON_LASTTIME']+5000 :
    print("Starting WaterShow at time: ",PushButtonTime)
    STATE['ISRUNNING']=True
    STATE['PUSHBUTTON_LASTTIME']=PushButtonTime

  if STATE['ISRUNNING'] and PushButtonTime > STATE['PUSHBUTTON_LASTTIME']+5000 :
    print("Stopping WaterShow at time: ",PushButtonTime)
    STATE['ISRUNNING']=False
    STATE['PUSHBUTTON_LASTTIME']=PushButtonTime


#############################################
def InitGPIO ():

  # for GPIO numbering, choose BCM  
  GPIO.setmode(GPIO.BCM)  

  # Button Push to roll on GPIO14 (pin 8 rising edge)
  GPIO.setup(14,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
  # Setup event on for detecting push button
  GPIO.add_event_detect(14,GPIO.RISING,callback=PushButton_Callback) 

  # Setup Pump GPIO
  GPIO.setup(Pump[P_GPIO], GPIO.OUT)

  for i in range(0,NumSolenoids):
    # Add CurrentStatus and DoToggle
    Solenoids[i].extend([V_CLOSE,False]) 

    # If enabled, setup GPIO for output
    if Solenoids[i][S_ENABLED]:
      #print 'Enabling S',i 
      SD[Solenoids[i][S_NAME]]=i
      GPIO.setup(Solenoids[i][S_GPIO], GPIO.OUT)

  print (SD)
#time.sleep(2.0);

#######################################

#############################################
def InitSolenoids ():

  GPIO.output(Solenoids[0][S_GPIO], V_OPEN)
  Solenoids[0][S_STATUS]=V_OPEN

  for i in range(1,NumSolenoids):
    if Solenoids[i][S_ENABLED]:
      GPIO.output(Solenoids[i][S_GPIO], V_CLOSE)
      Solenoids[i][S_STATUS]=V_CLOSE

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

    if Solenoids[5][S_STATUS] == V_OPEN :
      Line5=' -    O->^->^->^->^--*     -'
    else :
      Line5=' -    X--*--*--*--*--*     -'

    if Solenoids[6][S_STATUS] == V_OPEN :
      Line7=' -    *--^<-^<-^<-^<-O     -'
    else :
      Line7=' -    *--*--*--*--*--X     -'

  else :
    for i in range(0,5):
      DS.insert(i,Solenoids[i][0])
    Line5=' -   S5--*--*--*--*---*    -'
    Line7=' -   *---*--*--*--*--S6    -'

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
  print('       ---------------' )
  print('      -               -' )
  print('     -                 -' )
  print('  ',DS[1],'                  ',DS[2])
  print('  -                       -' )
  print(Line5)
  print('-                           -' )
  print(Line7)
  print('  -                       -' )
  print('  ',DS[3],'                  ',DS[4])
  print('     -       ',DS[0],'       -' )
  print('      -               -' )
  print('       ---------------' )
  print('         Time:',CurTime)

    
#######################################

#######################################
'''
def ServoSetAngle(angle):

duty = angle / 18 + 2
GPIO.output(03, True)
pwm.ChangeDutyCycle(duty)
sleep(1)
GPIO.output(03, False)
pwm.ChangeDutyCycle(0)
'''
#######################################


#######################################
#def ServoSetup:
	#pwm=GPIO.PWM(03,50)
	#pwm.start(0)
	#SetAngle(45)
	#pwm.stop()


#######################################
def SolenoidSend(SolenoidsNextState) :

  for i in range (1,NumSolenoids) :
    if Solenoids[i][S_ENABLED] and Solenoids[i][S_NAME] in SolenoidsNextState :
      if Solenoids[i][S_STATE] != SolenoidsNextState[Solenoids[i][S_NAME]] :
        print("Changing state from",Solenoids[i][S_STATE]," to",SolenoidsNextState[Solenoids[i][S_NAME]])
        

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
    print(NextPattern)
    if NextPattern[1] == 'Pulse' :
      Patterns.Pulse(NextPattern[2],NextPattern[3],Solenoids,Timeline)



#######################################
def PumpCtl (RunPump):

  if RunPump and not Pump[P_STATE]:
    GPIO.output(Pump[P_GPIO], P_RUN)
    Pump[P_STATE]=True

  if not RunPump and Pump[P_STATE]:
    GPIO.output(Pump[P_GPIO], P_STOP)
    Pump[P_STATE]=False
     
#######################################
def WaterShowStart():

  # Start pump
  if not Pump[P_STATE]:
    PumpCtl(True)
    time.sleep(2)
    
  # Set up audio
  WavFile = wave.open(WaterShowFile_Audio,'r')
  sample_rate = WavFile.getframerate()
  no_channels = WavFile.getnchannels()
  chunk       = 4096 # Use a multiple of 8
  AudioOutput = aa.PCM(aa.PCM_PLAYBACK, aa.PCM_NORMAL)
  AudioOutput.setchannels(no_channels)
  AudioOutput.setrate(sample_rate)
  AudioOutput.setformat(aa.PCM_FORMAT_S16_LE)
  AudioOutput.setperiodsize(chunk)

  WavData = WavFile.readframes(chunk)
  StartTime = int(round(time.time()*1000))
  step       = 1 #ignore the header line
  CurTime = 0

  while WavData != '' and STATE['ISRUNNING']:
    AudioOutput.write(WavData)
    WavData = WavFile.readframes(chunk)

  AudioOutput.close() 
  WavFile.close()
  InitSolenoids()
 
#######################################
def WaterShowStop ():

  for i in range(0,NumSolenoids):
    # Add CurrentStatus and DoToggle
    Solenoids[i].extend([V_CLOSE,False]) 
  #pygame.mixer.stop()
  #pygame.mixer.quit()
  
#######################################
def HardCleanExit():

  GPIO.cleanup()
  #pygame.mixer.stop()
  #pygame.mixer.quit()
  exit()
  

#######################################
def Usage():
  print("WaterShowPi.py Directory")
  exit()

#######################################

if len(sys.argv) < 2 :
  Usage()

WaterShowDir = []
if (sys.argv[1][len(sys.argv[1])-1] == '/') :
    WaterShowDir = sys.argv[1][0:len(sys.argv[1])-1]
else :
  WaterShowDir = sys.argv[1]
  
WaterShowFile_FFT = WaterShowDir + "/" + WaterShowDir + ".fft"
WaterShowFile_Sequence = WaterShowDir + "/" + WaterShowDir + ".seq"
WaterShowFile_Audio = WaterShowDir + "/" + WaterShowDir + ".wav"

if os.path.exists(WaterShowFile_FFT) :
  print ("FFT file is: ",WaterShowFile_FFT)
else :
  print ("Not a FFT file: ",WaterShowFile_FFT) 
  exit()

if os.path.exists(WaterShowFile_Sequence) :
  print ("Sequence file is: ",WaterShowFile_Sequence)
else :
  print ("Not a valid Sequence File: ",WaterShowFile_Sequence) 
  exit()

if os.path.exists(WaterShowFile_Audio) :
  print ("Audio file is: ",WaterShowFile_Audio)
else :
  print ("Not a valid Audio File: ",WaterShowFile_Audio) 
  exit()

#Solenoids[1][S_STATUS]=V_CLOSE
#Solenoids[2][S_STATUS]=V_OPEN
#Solenoids[3][S_STATUS]=V_OPEN
#Solenoids[4][S_STATUS]=V_OPEN
#PrintLayout(False)

with open(WaterShowFile_Sequence,'r') as SequenceFile:
  SequenceData = SequenceFile.read().splitlines()
del SequenceData[0]

InitGPIO()
InitSolenoids()

# Read Sequence file and process it
Pattern=[]
SequenceProcessor() 
#exit()

#pygame.mixer.init()
#pygame.mixer.music.load(WaterShowFile_Audio)
#pygame.mixer.music.play()


try:
#
#  while CurTime < 210000 :
#
#    CurTime = int(round(time.time()*1000)) - StartTime
#    #print StartTime
#    #print CurTime
#    fun=CurTime % NumSolenoids
#    Solenoids[fun][S_STATUS]=V_OPEN
#    GPIO.output(Solenoids[fun][S_GPIO],V_OPEN)
#    PrintLayout()
#    Solenoids[fun][S_STATUS]=V_CLOSE
#    GPIO.output(Solenoids[fun][S_GPIO],V_CLOSE)
#    time.sleep(.500)

#  WaterShowStart()

  while True:
    if (STATE['ISRUNNING']) :
      WaterShowStart()
    time.sleep(1)

except KeyboardInterrupt:
  HardCleanExit()
