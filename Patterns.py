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

#BASS={'FreqIndex':0, 'IntesityMinTrigger':8,'Solenoids':BassSolenoids,'MinCycleInterval':250,'MaxConseqCycles': 30, 'CurTriggerTime':0,'CurCycleCount':0, 'CurSolenoid':0,'NextSolenoid':0, 'IsRunning':False}
 
  def __init__(self,Name,Members):
    self.Name = Name
    self.Members = Members
    self.NumMembers = len(Members)
    self.CurCircuitMemberIndex=0
    self.NextCircuitMemberIndex=0
    self.IsRunning=False

    self.CircuitStartTime=0
    self.CurCircuitCompletedCount=0
    self.MaxConseqCircuitCompleted=3

    self.CurCycleStartTime=0
    self.CurCycleCount=0
    self.MinCycleTimeDuration=5000

  def PrintMembers(self) :
    print ("Circuit",self.Name,"NumMembers=",self.NumMembers)
    for i in range(0,len(self.Members)):
      print ("Circuit",self.Name,"[",i,"]=",self.Members[i])

    print ("Circuit",self.Name,"CurCircuitMember=",self.Members[self.CurCircuitMemberIndex])
    
  def AddMembers(self,NewMembers) :
    self.Members = self.Members + NewMembers
    self.NumMembers=len(self.Members)

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
    self.CircuitStartTime=0
    self.CurTriggerTime=0
    self.CurCircuitCompletedCount=0
    self.CurCycleCount=0

  def StartCircuit(self):
    self.IsRunning=True
    self.CircuitStartTime=int(round(time.time()*1000))
    self.CurTriggerTime=int(round(time.time()*1000))-self.CircuitStartTime

    self.CurCircuitCompletedCount=0
    self.CurCycleCount=0

    self.NextCircuitMemberIndex=self.CurCircuitMemberIndex+1
    if self.NextCircuitMemberIndex >= self.NumMembers :
      self.NextCircuitMemberIndex=0

  def Trigger(self):
    if not self.IsRunning:
      self.StartCircuit()

    self.CurTriggerTime=int(round(time.time()*1000))-self.CircuitStartTime

    print (self.CurTriggerTime)
    if (self.CurTriggerTime-self.CurCycleStartTime) < self.MinCycleTimeDuration:
      self.CurCycleCount+=1
      print ("Current:")
      return self.Members[self.CurCircuitMemberIndex]

    elif self.CurCircuitCompletedCount == self.MaxConseqCircuitCompleted:
      self.StopCircuit()
      return []

    else:
      return self.GoNextInCircuit()


  def GoNextInCircuit(self):
    self.CurCycleStartTime=int(round(time.time()*1000))-self.CircuitStartTime

    self.CurCircuitMemberIndex=self.NextCircuitMemberIndex
    self.NextCircuitMemberIndex+=1
    if self.NextCircuitMemberIndex >= self.NumMembers :
      self.NextCircuitMemberIndex=0
      self.CurCircuitCompletedCount+=1

    self.CurCycleCount=1
    return self.Members[self.CurCircuitMemberIndex]
      
