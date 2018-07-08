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
import FFT
import Patterns



S_NAME=0
S_ENABLED=1
S_GPIO=2
S_STATUS=3
S_TOGGLE=4

PumpColdStartDelay=5
PumpWarmStartDelay=4
#RunVolume=100
RunVolume=75

P_STATE=0
P_GPIO=1
P_RUN=0
P_STOP=1

V_OPEN=0
V_CLOSE=1

#       [IsRunning,LastPushButtonTime]
STATE = {'ISRUNNING':False,'PUSHBUTTON_LASTTIME':int(round(time.time()*1000))}
#print (STATE)

WavChunkIntesity = [0,0,0,0,0,0,0,0]
Freqs=[100,500,900,20000]
Freqweighting=[2,4,6,1]

######## Solenoid Definition ################
#    [Name,Enabled {True|False},GPIO]
S0 = ['S0',True,17]
S1 = ['S1',True,27]
S2 = ['S2',True,22]
S3 = ['S3',True,10]
S4 = ['S4',True,9]
S5 = ['S5',True,11]
S6 = ['S6',True,13]

BassSolenoids=[3,4]
ChorusSolenoids=[5,6]

BASS={'FreqIndex':0, 'IntesityMinTrigger':8,'Solenoids':BassSolenoids,'MinCycleInterval':250,'MaxConseqCycles': 30, 'CurTriggerTime':0,'CurCycleCount':0, 'CurSolenoid':0,'NextSolenoid':0, 'IsRunning':False}

CHORUS={'FreqIndex':2, 'IntesityMinTrigger':8,'Solenoids':ChorusSolenoids,'MinCycleInterval':2000,'MaxConseqCycles': 10, 'CurTriggerTime':0,'CurCycleCount':0, 'CurSolenoid':0,'NextSolenoid':0,'IsRunning':False}

#      [IsRunning {True|False},GPIO]
Pump = [False,23]

Solenoids = [S0,S1,S2,S3,S4,S5,S6]
NumSolenoids=len(Solenoids)

Solenoid_MinFireTime=.250

SD=dict()


#############################################
def PushButton_Callback(channel):

  return

#############################################
def OrigPushButton_Callback(channel):


  PushButtonTime=int(round(time.time()*1000))
  print (STATE,PushButtonTime)

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
  GPIO.setup(Pump[P_GPIO], GPIO.OUT, initial=P_STOP)

  for i in range(0,NumSolenoids):
    # Add CurrentStatus and DoToggle
    Solenoids[i].extend([V_CLOSE,False]) 

    # If enabled, setup GPIO for output
    if Solenoids[i][S_ENABLED]:
      #print 'Enabling S',i 
      SD[Solenoids[i][S_NAME]]=i
      GPIO.setup(Solenoids[i][S_GPIO], GPIO.OUT, initial=V_CLOSE)

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
def SolenoidSend(SolenoidX,NewState) :

  #SolendoidsOpen[1,2,3]
  #SolendoidsClose[4,5,6]
  #print("SolenoidX:",SolenoidX,NewState)

  for i in range(1,NumSolenoids):
    if i == SolenoidX:
      if NewState == V_CLOSE and Solenoids[SolenoidX][S_STATUS] != V_CLOSE:
        print("Changing state:",SolenoidX,":",Solenoids[SolenoidX][S_STATUS]," -> ",V_CLOSE)
        GPIO.output(Solenoids[SolenoidX][S_GPIO], V_CLOSE)
        Solenoids[SolenoidX][S_STATUS]=V_CLOSE
        if i == 3:
          GPIO.output(Solenoids[1][S_GPIO], V_CLOSE)
          Solenoids[1][S_STATUS]=V_CLOSE

        if i == 4:
          GPIO.output(Solenoids[2][S_GPIO], V_CLOSE)
          Solenoids[2][S_STATUS]=V_CLOSE
        
      if NewState == V_OPEN and Solenoids[SolenoidX][S_STATUS] != V_OPEN:
        #print("Changing state:",SolenoidX,":",Solenoids[SolenoidX][S_STATUS]," -> ",V_OPEN)
        GPIO.output(Solenoids[SolenoidX][S_GPIO], V_OPEN)
        Solenoids[SolenoidX][S_STATUS]=V_OPEN
        #time.sleep(.250)
        #GPIO.output(Solenoids[SolenoidX][S_GPIO], V_CLOSE)
        #Solenoids[SolenoidX][S_STATUS]=V_CLOSE

        if i == 3:
          GPIO.output(Solenoids[1][S_GPIO], V_OPEN)
          Solenoids[1][S_STATUS]=V_OPEN
        if i == 4:
          GPIO.output(Solenoids[2][S_GPIO], V_OPEN)
          Solenoids[2][S_STATUS]=V_OPEN

    elif NewState == V_OPEN:
      GPIO.output(Solenoids[i][S_GPIO], V_CLOSE)
      Solenoids[i][S_STATUS]=V_CLOSE

  BackPressure=True        
  #GPIO.output(Solenoids[0][S_GPIO], V_OPEN)
  #Solenoids[0][S_STATUS]=V_OPEN

  for i in range (1,NumSolenoids) :
    if Solenoids[i][S_STATUS] == V_OPEN:
      BackPressure=False

  # Close backpressure valve
  if BackPressure:
    GPIO.output(Solenoids[0][S_GPIO], V_OPEN)
    Solenoids[0][S_STATUS]=V_OPEN
  else:
    GPIO.output(Solenoids[0][S_GPIO], V_CLOSE)
    Solenoids[0][S_STATUS]=V_CLOSE


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

  # Always make sure relief valve is on
  GPIO.output(Solenoids[0][S_GPIO], V_OPEN)
  Solenoids[0][S_STATUS]=V_OPEN

  if RunPump and not Pump[P_STATE]:
    GPIO.output(Pump[P_GPIO], P_RUN)

    if (STATE['ISRUNNING']):
      print ("Starting Pump...Delaying:",PumpWarmStartDelay)
      time.sleep(PumpWarmStartDelay)
    else:
      print ("Starting Pump...Delaying:",PumpColdStartDelay)
      time.sleep(PumpColdStartDelay)

    Pump[P_STATE]=True

  if not RunPump and Pump[P_STATE]:
    GPIO.output(Pump[P_GPIO], P_STOP)
    print ("Stopping Pump...")
    Pump[P_STATE]=False
     
#######################################
def IntensitySend(WavChunkIntensity,CurTime):


#BASS={'FreqIndex':0, 'IntesityMinTrigger':8,'Solenoids':BassSolenoids,'MinCycleInterval':1000,'MaxConseqCycles': 30, 'CurTriggerTime':0,'CurCycleCount':0, 'CurSolenoid':0,'NextSolenoid':0, 'IsRunning':False}

#  if BASS['IsRunning'] and WavChunkIntensity[BASS['FreqIndex']] < BASS['IntesityMinTrigger']:
#    CurSolenoid=BASS['CurSolenoid']
#    NextSolenoid=BASS['NextSolenoid']
#    ElapsedTime=CurTime-BASS['CurTriggerTime']
#    if ElapsedTime > BASS['MinCycleInterval']:
#      print ("Spindn(",CurTime,"): ",Solenoids[BASS['Solenoids'][CurSolenoid]][S_NAME],WavChunkIntensity)
#      SolenoidSend(BASS['Solenoids'][CurSolenoid],V_CLOSE)
#      NextSolenoid=NextSolenoid+1
#      if NextSolenoid > len(BASS['Solenoids'])-1 :
#        BASS['NextSolenoid']=0
#      else :
#        BASS['NextSolenoid']=NextSolenoid
#
#      BASS['IsRunning']=False
#      BASS['CurCycleCount'] = 0

  if not CHORUS['IsRunning'] and WavChunkIntensity[BASS['FreqIndex']] >= BASS['IntesityMinTrigger']:

    CurSolenoid=BASS['CurSolenoid']
    NextSolenoid=BASS['NextSolenoid']
    ElapsedTime=CurTime-BASS['CurTriggerTime']

    if ElapsedTime > BASS['MinCycleInterval']:

      if BASS['IsRunning']:
      #  print ("Closng(",CurTime,"): ",Solenoids[BASS['Solenoids'][CurSolenoid]][S_NAME],WavChunkIntensity)
        SolenoidSend(BASS['Solenoids'][CurSolenoid],V_CLOSE)


      
      if BASS['CurCycleCount'] == BASS['MaxConseqCycles']:
      #  print ("Stopng(",CurTime,"): ",Solenoids[BASS['Solenoids'][CurSolenoid]][S_NAME],WavChunkIntensity)
        SolenoidSend(BASS['Solenoids'][CurSolenoid],V_CLOSE)
        BASS['IsRunning']=False
        BASS['CurCycleCount'] = 0

      else:
        print ("Firing(",CurTime,"): ",Solenoids[BASS['Solenoids'][NextSolenoid]][S_NAME],WavChunkIntensity)
        SolenoidSend(BASS['Solenoids'][NextSolenoid],V_OPEN)

        BASS['CurSolenoid']=NextSolenoid

        NextSolenoid=NextSolenoid+1
        if NextSolenoid > len(BASS['Solenoids'])-1 :
          BASS['NextSolenoid']=0
        else :
          BASS['NextSolenoid']=NextSolenoid

        BASS['IsRunning']=True
        BASS['CurTriggerTime']=CurTime
        BASS['CurCycleCount']+=CurTime
        CHORUS['CurCycleCount']=0
 

  if CHORUS['IsRunning'] and WavChunkIntensity[CHORUS['FreqIndex']] < CHORUS['IntesityMinTrigger']:
    CurSolenoid=CHORUS['CurSolenoid']
    NextSolenoid=CHORUS['NextSolenoid']
    ElapsedTime=CurTime-CHORUS['CurTriggerTime']
    if ElapsedTime > CHORUS['MinCycleInterval']:
      print ("Spindn(",CurTime,"): ",Solenoids[CHORUS['Solenoids'][CurSolenoid]][S_NAME],WavChunkIntensity)
      SolenoidSend(CHORUS['Solenoids'][CurSolenoid],V_CLOSE)
      NextSolenoid=NextSolenoid+1
      if NextSolenoid > len(CHORUS['Solenoids'])-1 :
        CHORUS['NextSolenoid']=0
      else :
        CHORUS['NextSolenoid']=NextSolenoid

      CHORUS['IsRunning']=False
      CHORUS['CurCycleCount'] = 0

  if WavChunkIntensity[CHORUS['FreqIndex']] >= CHORUS['IntesityMinTrigger']:

    CurSolenoid=CHORUS['CurSolenoid']
    NextSolenoid=CHORUS['NextSolenoid']
    ElapsedTime=CurTime-CHORUS['CurTriggerTime']

    if ElapsedTime > CHORUS['MinCycleInterval']:

      if CHORUS['IsRunning']:
        print ("Closng(",CurTime,"): ",Solenoids[CHORUS['Solenoids'][CurSolenoid]][S_NAME],WavChunkIntensity)
        SolenoidSend(CHORUS['Solenoids'][CurSolenoid],V_CLOSE)
      
      if CHORUS['CurCycleCount'] == CHORUS['MaxConseqCycles']:
        print ("Stopng(",CurTime,"): ",Solenoids[CHORUS['Solenoids'][CurSolenoid]][S_NAME],WavChunkIntensity)
        SolenoidSend(CHORUS['Solenoids'][CurSolenoid],V_CLOSE)
        CHORUS['IsRunning']=False
        CHORUS['CurCycleCount'] = 0

      else:
        print ("Firing(",CurTime,"): ",Solenoids[CHORUS['Solenoids'][NextSolenoid]][S_NAME],WavChunkIntensity)
        SolenoidSend(CHORUS['Solenoids'][NextSolenoid],V_OPEN)

        CHORUS['CurSolenoid']=NextSolenoid

        NextSolenoid=NextSolenoid+1
        if NextSolenoid > len(CHORUS['Solenoids'])-1 :
          CHORUS['NextSolenoid']=0
        else :
          CHORUS['NextSolenoid']=NextSolenoid

        CHORUS['IsRunning']=True
        CHORUS['CurTriggerTime']=CurTime
        CHORUS['CurCycleCount']+=1
        BASS['CurCycleCount']=0

        
        


#######################################
def WaterShowStart():

  # Start pump
  if not Pump[P_STATE]:
    PumpCtl(True)
    
  # Set up audio
  AudioMixer = aa.Mixer()
  vol = AudioMixer.getvolume()
  AudioVolume = int(vol[0])
  AudioMixer.setvolume(RunVolume)

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
  CurrentChunkNum = 1 #ignore the header line
  CurTime = 0
  
  while sys.getsizeof(WavData) > 16000 and STATE['ISRUNNING']:
    WavChunkIntensity=FFT.calculate_levels(WavData,chunk,sample_rate,Freqs,Freqweighting)
    CurTime = int(round(time.time()*1000)) - StartTime
    print(WavChunkIntensity)
    IntensitySend(WavChunkIntensity,CurTime)
    AudioOutput.write(WavData)
    WavData = WavFile.readframes(chunk)

  WavChunkIntensity[:]
  BASS['IsRunning']=False
  BASS['CurTriggerTime']=0
  BASS['CurCycleCount']=0
  CHORUS['IsRunning']=False
  CHORUS['CurTriggerTime']=0
  CHORUS['CurCycleCount']=0
  #STATE['ISRUNNING']=False
  AudioOutput.close() 
  AudioMixer.setvolume(AudioVolume)
  WavFile.close()
  PumpCtl(False)
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
  #exit()

if os.path.exists(WaterShowFile_Sequence) :
  print ("Sequence file is: ",WaterShowFile_Sequence)
  with open(WaterShowFile_Sequence,'r') as SequenceFile:
    SequenceData = SequenceFile.read().splitlines()
  del SequenceData[0]

else :
  print ("Not a valid Sequence File: ",WaterShowFile_Sequence) 
  SequenceData = []
  #exit()

if os.path.exists(WaterShowFile_Audio) :
  print ("Audio file is: ",WaterShowFile_Audio)
else :
  print ("Not a valid Audio File: ",WaterShowFile_Audio) 
  exit()



InitGPIO()
InitSolenoids()

# Read Sequence file and process it
Pattern=[]
#SequenceProcessor() 
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
    #if (STATE['ISRUNNING']) :
      STATE['ISRUNNING']=True
      WaterShowStart()
      time.sleep(10)

      print("In main loop")
      time.sleep(5)

except :
  HardCleanExit()
