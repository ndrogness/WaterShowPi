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

class Circuit :

  CircuitsRunning = False

  def __init__(self,Name,Members,FreqSet=['eq8','lt8','lt8','lt8'],IntensityMinTrigger=8,MaxConseqCompletions=3, MinCycleTimeDuration=1000):
    self.Name = Name
    self.Members = Members
    self.FreqSet = FreqSet
    self.IntensityMinTrigger = IntensityMinTrigger
    self.NumMembers = len(Members)
    self.CurCircuitMemberIndex=0
    self.NextCircuitMemberIndex=0
    self.IsRunning=False

    self.MaxConseqCircuitCompleted=MaxConseqCompletions
    self.CircuitStartTime=0
    self.CurCircuitCompletedCount=0

    self.MinCycleTimeDuration=MinCycleTimeDuration
    self.CurCycleStartTime=0
    self.CurCycleCount=0

  def PrintMembers(self) :
    print ("Circuit",self.Name,"NumMembers=",self.NumMembers)
    for i in range(0,len(self.Members)):
      print ("Circuit",self.Name,"[",i,"]=",self.Members[i])

    print ("Circuit",self.Name,"CurCircuitMember=",self.Members[self.CurCircuitMemberIndex])
    
  def AddMembers(self,NewMembers) :
    self.Members = self.Members + NewMembers
    self.NumMembers=len(self.Members)

  def GetName(self):
    return self.Name

  def GetFreqSet(self):
    return self.FreqSet

  def GetMinCycleTimeDuration(self):
    return self.MinCycleTimeDuration

  def SetMinCycleTimeDuration(self,MCTD):
    self.MinCycleTimeDuration=MCTD

  def GetIntensityMinTrigger(self):
    return self.IntensityMinTrigger

  def SetIntensityMinTrigger(self,IMT):
    self.IntensityMinTrigger=IMT

  def GetMaxConseqCompletions(self):
    return self.MaxConseqCircuitCompleted

  def SetMaxConseqCompletions(self,MCC):
    self.MaxConseqCircuitCompleted=MCC

  def SetCurInCircuit(self,CurMemberIndex):
    if CurMemberIndex > len(self.Members)-1 :
      return False
    self.CurCircuitMemberIndex=CurMemberIndex
    return True
    
  def SetNextInCircuit(self,NextMemberIndex):
    if NextMemberIndex > len(self.Members)-1 :
      return False
    self.NextCircuitMemberIndex=NextMemberIndex
    return True

  def GetCurCycle(self):
    return self.Members[self.CurCircuitMemberIndex]

  def GetNextCycle(self):
    return self.Members[self.NextCircuitMemberIndex]

  def Running(self):
    return self.IsRunning

  def StopCircuit(self):
    self.IsRunning=False
    self.CircuitsRunning=False
    self.CircuitStartTime=0
    self.CurTriggerTime=0
    self.CurCircuitCompletedCount=0
    self.CurCycleCount=0
    print("Circuit",self.Name,"Stopping...",self.CurCircuitMemberIndex,self.NextCircuitMemberIndex)
    self.CurCircuitMemberIndex=self.NextCircuitMemberIndex

  def StartCircuit(self,ExtTriggerTime):
    print ("Starting",self.Name,"Circuit...")
    self.IsRunning=True
    self.CircuitsRunning=True
    #self.CircuitStartTime=int(round(time.time()*1000))
    self.CircuitStartTime=ExtTriggerTime
    #self.CurTriggerTime=int(round(time.time()*1000))-self.CircuitStartTime
    self.CurTriggerTime=ExtTriggerTime

    self.CurCircuitCompletedCount=0
    self.CurCycleCount=0

    self.NextCircuitMemberIndex=self.CurCircuitMemberIndex+1
    if self.NextCircuitMemberIndex >= self.NumMembers :
      self.NextCircuitMemberIndex=0

  def Trigger(self,ExtTriggerTime):
    if not self.IsRunning:
      self.StartCircuit(ExtTriggerTime)
      #self.CurCycleStartTime=int(round(time.time()*1000))-self.CircuitStartTime
      self.CurCycleStartTime=ExtTriggerTime

    #self.CurTriggerTime=int(round(time.time()*1000))-self.CircuitStartTime
    self.CurTriggerTime=ExtTriggerTime

    #print ("TriggerTime:",self.CurTriggerTime,"CycleStartedAt:",self.CurCycleStartTime)
    if (self.CurTriggerTime-self.CurCycleStartTime) < self.MinCycleTimeDuration:
      self.CurCycleCount+=1
      return self.Members[self.CurCircuitMemberIndex]

    elif self.CurCircuitCompletedCount == self.MaxConseqCircuitCompleted:
      print ("Max circuits completed:",self.MaxConseqCircuitCompleted)
      self.StopCircuit()
      return []

    else:
      return self.GoNextInCircuit(ExtTriggerTime)


  def GoNextInCircuit(self,ExtTriggerTime):
    #self.CurCycleStartTime=int(round(time.time()*1000))-self.CircuitStartTime
    self.CurCycleStartTime=ExtTriggerTime-self.CircuitStartTime

    self.CurCircuitMemberIndex=self.NextCircuitMemberIndex
    self.NextCircuitMemberIndex+=1
    if self.NextCircuitMemberIndex >= self.NumMembers :
      self.NextCircuitMemberIndex=0
      self.CurCircuitCompletedCount+=1

    self.CurCycleCount=1
    return self.Members[self.CurCircuitMemberIndex]
      
