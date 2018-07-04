#!/usr/bin/env python

# 8 band Audio equaliser from wav file
 
import alsaaudio as aa
from struct import unpack
import numpy as np
import wave
import sys
import time
import os

def Set_Column(row, col):
	bus.write_byte_data(ADDR, BANKA, col)
	bus.write_byte_data(ADDR, BANKB, row)
			
# Initialise matrix
matrix    = [0,0,0,0,0,0,0,0]
power     = []
#weighting = [2,2,2,2,2,2,2,2] # Change these according to taste
weighting = [2,2,8,8,16,32,64,64] # Change these according to taste

# Set up audio
wavfile = wave.open(sys.argv[1],'r')
sample_rate = wavfile.getframerate()
no_channels = wavfile.getnchannels()
chunk       = 4096 # Use a multiple of 8
output = aa.PCM(aa.PCM_PLAYBACK, aa.PCM_NORMAL)
output.setchannels(no_channels)
output.setrate(sample_rate)
output.setformat(aa.PCM_FORMAT_S16_LE)
output.setperiodsize(chunk)

# Return power array index corresponding to a particular frequency
def piff(val,chunk,sample_rate):
	return int(2*chunk*val/sample_rate)
	
def calculate_levels(data, chunk,sample_rate):
	global matrix
	# Convert raw data (ASCII string) to numpy array
	data = unpack("%dh"%(len(data)/2),data)
	data = np.array(data, dtype='h')
	# Apply FFT - real data
	fourier=np.fft.rfft(data)
	# Remove last element in array to make it the same size as chunk
	fourier=np.delete(fourier,len(fourier)-1)
	# Find average 'amplitude' for specific frequency ranges in Hz
	power = np.abs(fourier)	
	c2=2*chunk

	#matrix[0]= int(np.mean(power[piff(0,chunk,sample_rate)    :piff(156,chunk,sample_rate):1]))
	#matrix[1]= int(np.mean(power[piff(156,chunk,sample_rate)  :piff(313,chunk,sample_rate):1]))
	#matrix[2]= int(np.mean(power[piff(313,chunk,sample_rate)  :piff(625,chunk,sample_rate):1]))
	#matrix[3]= int(np.mean(power[piff(625,chunk,sample_rate)  :piff(1250,chunk,sample_rate):1]))
	#matrix[4]= int(np.mean(power[piff(1250,chunk,sample_rate) :piff(2500,chunk,sample_rate):1]))
	#matrix[5]= int(np.mean(power[piff(2500,chunk,sample_rate) :piff(5000,chunk,sample_rate):1]))
	#matrix[6]= int(np.mean(power[piff(5000,chunk,sample_rate) :piff(10000,chunk,sample_rate):1]))
	#matrix[7]= int(np.mean(power[piff(10000,chunk,sample_rate):piff(20000,chunk,sample_rate):1]))

	matrix[0]= int(np.mean(power[int(c2*0/sample_rate     :int(c2*156/sample_rate):1]))
	matrix[1]= int(np.mean(power[int(c2*156/sample_rate)  :int(c2*313/sample_rate):1]))
	matrix[2]= int(np.mean(power[int(c2*313/sample_rate)  :int(c2*625/sample_rate):1]))
	matrix[3]= int(np.mean(power[int(c2*625/sample_rate)  :int(c2*1250/sample_rate):1]))
	matrix[4]= int(np.mean(power[int(c2*1250/sample_rate) :int(c2*2500/sample_rate):1]))
	matrix[5]= int(np.mean(power[int(c2*2500/sample_rate) :int(c2*5000/sample_rate):1]))
	matrix[6]= int(np.mean(power[int(c2*5000/sample_rate) :int(c2*10000/sample_rate):1]))
	matrix[7]= int(np.mean(power[int(c2*10000/sample_rate):int(c2*20000/sample_rate):1]))

	# Tidy up column values for the LED matrix
	matrix=np.divide(np.multiply(matrix,weighting),1000000)
	# Set floor at 0 and ceiling at 8 for LED matrix
	matrix=matrix.clip(0,8) 
	return matrix

def PrintMatrix (matrix):

  mdisplay = []
  os.system("clear")
  for i in range(1,9) :
    dec=9-i
    for j in range (0,8):
      if dec <= matrix[j] :
	sys.stdout.write(str('*'))
      else :
	sys.stdout.write(str(' '))
    print ""        
  
  print "01234567"


# Process audio file	
print "Processing....."
data = wavfile.readframes(chunk)

StartTime = int(round(time.time()*1000))
step       = 1 #ignore the header line
CurTime = 0

while data!='':
  	CurTime = int(round(time.time()*1000)) - StartTime
	output.write(data)	
	matrix=calculate_levels(data, chunk,sample_rate)
	#print matrix[0],matrix[1]

	#if (step%2) == 0:
	#  PrintMatrix(matrix)
	print step,CurTime,matrix
	
	#for i in range (0,8):
		#Set_Column((1<<matrix[i])-1,0xFF^(1<<i))	
	#	print matrix[i]
	data = wavfile.readframes(chunk)
	step=step+1
