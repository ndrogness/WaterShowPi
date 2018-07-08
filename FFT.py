#!/usr/bin/env python3

# FFT from (8 band Audio equaliser from wav file)
 
from struct import unpack
import numpy as np
import sys
import time
import os

def calculate_levels(data,chunk,sample_rate,freqs,weighting):

  #matrix=[0,0,0,0,0,0,0,0]
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
