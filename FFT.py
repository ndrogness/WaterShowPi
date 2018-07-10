#!/usr/bin/env python3

# FFT from (8 band Audio equaliser from wav file)
 
from struct import unpack
import numpy as np
import sys
import time
import os
import wave


def AutoBuild(filename,freqs,weights,ChunkSize=4096,MaxFreqs=8):

  possible_freqs=build_freq_matrix(100,100,20000)
  print (possible_freqs)
  NumPossibleFreqs=len(possible_freqs)
  possible_freqs_count=[int(0) for i in range(0,NumPossibleFreqs)]
  #Counts=[int(0) for i in range(0,MaxFreqs)]

  possible_weights=[int(1) for i in range(0,NumPossibleFreqs)]
  DataFFT=[]
  defaultweighting = [ [0,1],[150,2],[625,8],[2500,16],[5000,32],[10000,64] ]
  for i in range(0,NumPossibleFreqs):

    for j in range(0,len(defaultweighting)):
      if (defaultweighting[j][0] < possible_freqs[i]):
        possible_weights[i]=defaultweighting[j][1]

    if possible_weights[i] < 2:
      possible_weights[i]=2

    #print ("Freq:",possible_freqs[i],"Weight:",possible_weights[i])
      
  wavfile = wave.open(filename,'r')
  sample_rate = wavfile.getframerate()

  data = wavfile.readframes(ChunkSize)

  #while data = wavfile.readframes(ChunkSize):
  print ("Calculating FFT on Wavfile...")
  while sys.getsizeof(data) > 16000:
    #print("Processing FFT on Chunk")
    DataFFT=calculate_levels(data,ChunkSize,sample_rate,possible_freqs,possible_weights)
    for j in range(0,len(DataFFT)):
      possible_freqs_count[j]+=DataFFT[j]
    data = wavfile.readframes(ChunkSize)

  wavfile.close()

  FreqCount=dict()
  for k in range(0,len(possible_freqs_count)):
    FreqCount[possible_freqs_count[k]]=k

  print (possible_freqs_count)
  print ("Sorting List:")
  freqs_counts=possible_freqs_count
  freqs_counts.sort(reverse=True)
  
  print (freqs_counts)
  Counts=freqs_counts[0:MaxFreqs]
  print (Counts)

  for j in range(0,len(Counts)):
    freqs[j]=possible_freqs[ FreqCount[Counts[j]] ]
    print("Final Frequency:",freqs[j],"with count:",Counts[j])

  #for j in range(0,len(Counts)):
  #  for k in range(0,len(possible_freqs_count)):
  #    if possible_freqs_count[k] == Counts[j]:
  #      freqs[j]=

  #HiFi [StartFreq,EndFreq,SweetSpot]
  SubBass=[20,60,60]
  Bass=[61,250,250]
  LowMidrange=[251,500,300]
  Midrange=[501,2000,1000]
  UpperMidrange=[2001,4000,2500]
  Presence=[4001,6000,5000]
  Brilliance=[6001,20000,12000]

  #print("Final Freqs:",freqs)

def build_freq_matrix(start_freq=50,step_size=50,end_freq=20000):

  if start_freq < 20:
    start_freq = 20

  stop= int(round(end_freq/step_size))
  #print ("Stop:",stop)
  return [start_freq+(step_size*x) for x in range(0,stop)]

  
def calculate_levels(data,chunk,sample_rate,freqs,weighting):

  matrix=[int(0) for i in range(0,len(freqs))]

  power=[]

  # Convert raw data (ASCII string) to numpy array
  data = unpack("%dh"%(len(data)/2),data)
  data = np.array(data, dtype='h')

  # Apply FFT - real data
  fourier=np.fft.rfft(data)

  # Remove last element in array to make it the same size as chunk
  fourier=np.delete(fourier,len(fourier)-1)

  # Find average 'amplitude' for specific frequency ranges in Hz
  power = np.abs(fourier)	
 
  # Loop through freqs 

  v1=int(2*chunk*0/sample_rate)
  for i in range(0,len(freqs)) :
    v2=int(2*chunk*freqs[i]/sample_rate)
    matrix[i]= int( (np.mean(power[v1:v2:1]) * weighting[i]) / 1000000 )
    if matrix[i] > 8 :
      matrix[i]=8
    v1=v2

#  v1=int(2*chunk*0/sample_rate)
#  v2=int(2*chunk*156/sample_rate)
#  matrix[0]= int( (np.mean(power[v1:v2:1]) * weighting[0]) / 1000000 )
#  if matrix[0] > 8:
#    matrix[0]=8
#
#  v1=v2
#  v2=int(2*chunk*313/sample_rate)
#  matrix[1]= int( (np.mean(power[v1:v2:1]) * weighting[1]) / 1000000 )
#  if matrix[1] > 8:
#    matrix[1]=8

  #print(matrix)

  return matrix

def PrintMatrix (matrix):

  mdisplay = []
  os.system("clear")
  for i in range(1,9) :
    row=9-i
    for j in range (0,len(matrix)):
      if row <= matrix[j] :
        sys.stdout.write(str('*'))
      else :
        sys.stdout.write(str(' '))

    print("")

  for i in range(0,len(matrix)) :
    sys.stdout.write(str(i))

  print("")
