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
RunVolume=100

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
#Freqs=[100,900,4000,20000]
#Freqweighting=[2,4,6,1]
Freqs=[]
Freqweighting=[]

######## Solenoid Definition ################
#    [Name,Enabled {True|False},GPIO]
S0 = ['S0',True,17]
S1 = ['S1',True,27]
S2 = ['S2',True,22]
S3 = ['S3',True,10]
S4 = ['S4',True,9]
S5 = ['S5',True,11]
S6 = ['S6',True,13]


#Name,
#Members,
#FreqIndex=0,
#IntensityMinTrigger=8,
#MaxConseqCompletions=3,
#MinCycleTimeDuration=1000
#Bass=Patterns.Circuit("Bass",[[1,3],[2,4]],FreqSet=['eq8','lt8','lt8','lt8'],IntensityMinTrigger=8,MinCycleTimeDuration=85,MaxConseqCompletions=50)
#Chorus=Patterns.Circuit("Chorus",[[5]],FreqSet=['lt8','eq8','lt8','lt8'],IntensityMinTrigger=8,MinCycleTimeDuration=2000,MaxConseqCompletions=10)
#Chorus2=Patterns.Circuit("Chorus2",[[6]],FreqSet=['lt8','lt8','eq8','lt8'],IntensityMinTrigger=8,MinCycleTimeDuration=2000,MaxConseqCompletions=3)

# In order of Trigger Priority ascending
#WaterShowPatterns=[Chorus2,Chorus,Bass]
WaterShowPatterns=[]

#      [IsRunning {True|False},GPIO]
Pump = [False,23]

Solenoids = [S0,S1,S2,S3,S4,S5,S6]
NumSolenoids=len(Solenoids)


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
def SolenoidSend(SolenoidSet,NewState) :

  print("SolenoidSet:",SolenoidSet,NewState)

  InSolenoidSet=dict()
  for i in range(0,len(SolenoidSet)):
    if SolenoidSet[i] == 0:
      return False    

    if Solenoids[SolenoidSet[i]][S_STATUS] != V_OPEN and NewState == V_OPEN:
        #print("Changing state:",SolenoidSet[i],":",Solenoids[SolenoidSet[i]][S_STATUS]," -> ",V_OPEN)
        GPIO.output(Solenoids[SolenoidSet[i]][S_GPIO], V_OPEN)
        Solenoids[SolenoidSet[i]][S_STATUS]=V_OPEN
        InSolenoidSet[SolenoidSet[i]]=True

    elif NewState == V_CLOSE:
      GPIO.output(Solenoids[SolenoidSet[i]][S_GPIO], V_CLOSE)
      Solenoids[SolenoidSet[i]][S_STATUS]=V_CLOSE

  BackPressure=True        

  for i in range(1,len(Solenoids)):

    if not i in InSolenoidSet.keys():
      #print ("S",i,"Not in set",SolenoidSet)
      GPIO.output(Solenoids[i][S_GPIO], V_CLOSE)
      Solenoids[i][S_STATUS]=V_CLOSE

    elif NewState == V_OPEN:
      BackPressure=False


  #for i in range (1,NumSolenoids) :
  #  if Solenoids[i][S_STATUS] == V_OPEN:
  #    BackPressure=False

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
def CreatePatternFromCFG (PatternOptions):

  PatternOptionsVals=PatternOptions.split("|")

  for i in range(0,len(PatternOptionsVals)):
    PatternOption=PatternOptionsVals[i].split(":")

    #Name:Bass
    if PatternOption[0] == 'Name':
      CName=PatternOption[1]

    #SolSet:1&3,2&4
    if PatternOption[0] == 'SolSet':
      CSolenoidSet=[]
      SolOuterSet=PatternOption[1].split(",")
      print("SolOuterSet:",SolOuterSet)
      for j in range(0,len(SolOuterSet)):
        SolInnerSet=SolOuterSet[j].split("&")
        SolInnerSet=list(map(int,SolInnerSet))
        print("SolInnerSet:",SolInnerSet)
        CSolenoidSet.append(SolInnerSet)

    #FreqSet:eq8,lt8,lt8,lt8
    if PatternOption[0] == 'FreqSet':
      CFreqSet=PatternOption[1].split(",")

  #print ("CSolSet:",CSolenoidSet)
  C=Patterns.Circuit(Name=CName,Members=CSolenoidSet,FreqSet=CFreqSet)

  for i in range(0,len(PatternOptionsVals)):
    PatternOption=PatternOptionsVals[i].split(":")

    if PatternOption[0] == 'IntensityMinTrigger':
      C.SetIntensityMinTrigger(int(PatternOption[1]))

    if PatternOption[0] == 'MinCycleTimeDuration':
      C.SetMinCycleTimeDuration(int(PatternOption[1]))

    if PatternOption[0] == 'MaxConseqCompletions':
      C.SetMaxConseqCompletions(int(PatternOption[1]))

  WaterShowPatterns.append(C)

#######################################
def CFGParser ():

  for i in range(0,len(CFGData)):
    CFGLine=CFGData[i].split("=")
    #print("ConfigLine is:",CFGLine)

    # Populate Freqs=[]
    if CFGLine[0] == 'Frequencies' :
      print("Frequencies are:",CFGLine[1])
      CFGValues=CFGLine[1].split(",")

      for i in range(0,len(CFGValues)):
        Freqs.append(int(CFGValues[i]))

    #Populate Freqweighting=[]
    if CFGLine[0] == 'FrequenciesWeighting' :
      CFGValues=CFGLine[1].split(",")

      for i in range(0,len(CFGValues)):
        Freqweighting.append(int(CFGValues[i]))

    #Populate WaterShowPatternNames=[]
    #if CFGLine[0] == 'Patterns' :
    #  CFGValues=CFGLine[1].split(",")

    #  for i in range(0,len(CFGValues)):
    #    WaterShowPatternNames[CFGValues[i]]={}

    #Pattern Def
    if CFGLine[0] == 'PatternDef' :
      CreatePatternFromCFG(CFGLine[1])
      CFGValues=CFGLine[1].split("|")


  if len(Freqs) < 1 or len(Freqweighting) < 1 :
    print("Missing Frequencies or Weighting in .cfg file...bailing out!")
    exit()

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
def IntensityTrigger (WavChunkIntensity,CurTime):

  #Bass=Patterns.Circuit('Bass',[[1,3],[2,4]],FreqIndex=0,IntensityMinTrigger=8)
  #Chorus=Patterns.Circuit('Chorus',[5,6],FreqIndex=1,IntensityMinTrigger=7,MinCycleTimeDuration=2000)

  #print ("Intensity:",WavChunkIntensity)

  CircuitFound=False

  for i in range(0,len(WaterShowPatterns)):

    FreqSet=WaterShowPatterns[i].GetFreqSet()
    #FreqSet=['eq8','lt8','lt8','lt8']

    FreqSetMatch=True
    for j in range(0,len(FreqSet)):
      FreqOperand=FreqSet[j][0:2]
      FreqIntensity=int(FreqSet[j][2:])

      if FreqOperand == 'eq' and WavChunkIntensity[j] != FreqIntensity :
          FreqSetMatch=False 
      elif FreqOperand == 'lt' and WavChunkIntensity[j] >= FreqIntensity :
          FreqSetMatch=False 
      elif FreqOperand == 'le' and WavChunkIntensity[j] > FreqIntensity :
          FreqSetMatch=False 
      elif FreqOperand == 'gt' and WavChunkIntensity[j] <= FreqIntensity :
          FreqSetMatch=False 
      elif FreqOperand == 'ge' and WavChunkIntensity[j] < FreqIntensity :
          FreqSetMatch=False 

    if WaterShowPatterns[i].IsRunning and CurTime-WaterShowPatterns[i].CurCycleStartTime < WaterShowPatterns[i].MinCycleTimeDuration :
  
        #print (WaterShowPatterns[i].Name,"Holding SameCycle:",WavChunkIntensity)
        WaterShowPatterns[i].Trigger(CurTime)
        CircuitFound=True

    else: 
    
      if CircuitFound:
        if WaterShowPatterns[i].IsRunning:
          print (WaterShowPatterns[i].Name,"Stopping.(Circuit Collision)..:",WavChunkIntensity)
          WaterShowPatterns[i].StopCircuit()

      else:
        # Circuit Not Found Yet

        # This Pattern Should fire or hold sense we matched
        if FreqSetMatch:

          if WaterShowPatterns[i].IsRunning:
            #print (WaterShowPatterns[i].Name,"Holding NextCyle...:",WavChunkIntensity)
            WaterShowPatterns[i].Trigger(CurTime)
            CircuitFound=True

          else:
            print (WaterShowPatterns[i].Name,"Triggering:",WavChunkIntensity)
            SolenoidSend(WaterShowPatterns[i].Trigger(CurTime),V_OPEN)
            CircuitFound=True


        # This Pattern Should NOT fire sense we didn't match
        if not FreqSetMatch:

          if WaterShowPatterns[i].IsRunning:
            print (WaterShowPatterns[i].Name,"Stopping (No match)...:",WavChunkIntensity)
            WaterShowPatterns[i].StopCircuit()



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
    #print("WavChunk:",WavChunkIntensity)
    IntensityTrigger(WavChunkIntensity,CurTime)
    AudioOutput.write(WavData)
    WavData = WavFile.readframes(chunk)

  WavChunkIntensity[:]
  STATE['ISRUNNING']=False
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
WaterShowFile_CFG = WaterShowDir + "/" + WaterShowDir + ".cfg"
WaterShowFile_Audio = WaterShowDir + "/" + WaterShowDir + ".wav"

if os.path.exists(WaterShowFile_FFT) :
  print ("FFT file is: ",WaterShowFile_FFT)
else :
  print ("Not a FFT file: ",WaterShowFile_FFT) 
  #exit()

if os.path.exists(WaterShowFile_CFG) :
  print ("Config file is: ",WaterShowFile_CFG)
  with open(WaterShowFile_CFG,'r') as CFGFile:
    CFGData = CFGFile.read().splitlines()
  #del SequenceData[0]
  CFGParser()

else :
  print ("Not a valid cfg File: ",WaterShowFile_CFG) 
  CFGData = []
  exit()

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

except KeyboardInterrupt:
  HardCleanExit()
except Exception as e:
  print ("Exception:",sys.exc_info()[0],"Argument:",str(e))
  HardCleanExit()
