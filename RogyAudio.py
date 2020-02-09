#!/usr/bin/env python3

import sys
import os
import random
import alsaaudio as aa
import wave
from struct import unpack
import numpy as np

# Global Defines

# Maximum Signal intensity
MAX_SIGNAL_LEVEL = 8

# Default Frequencies & Weights for FFT analysis
DEFAULT_FREQUENCIES = [80, 150, 310, 450, 800, 2500, 5000, 10000]
DEFAULT_FREQ_WEIGHT = [2,    4,   8,   8,  16,   16,   32,    64]

# High Fidelity Info
SubBass = {'name': 'SubBass',
           'freq_low': 20,
           'freq_high': 60,
           'freq_sweetspot': 60,
           'step_size': 5,
           'weight': 1,
           'num_freqs_to_include': 0,
           'freqs': [60]
           }


Bass = {'name': 'Bass',
        'freq_low': 61,
        'freq_high': 250,
        'freq_sweetspot': 140,
        'step_size': 25,
        'weight': 2,
        'num_freqs_to_include': 1,
        'freqs': [80]
        }

LowMidrange = {'name': 'LowMidrange',
               'freq_low': 251,
               'freq_high': 500,
               'freq_sweetspot': 300,
               'step_size': 30,
               'weight': 4,
               'num_freqs_to_include': 1,
               'freqs': [300]
               }

Midrange = {'name': 'Midrange',
            'freq_low': 501,
            'freq_high': 2000,
            'freq_sweetspot': 1000,
            'step_size': 180,
            'weight': 8,
            'num_freqs_to_include': 2,
            'freqs': [500, 1000]
            #'freqs': [500]
            }

UpperMidrange = {'name': 'UpperMidrange',
                 'freq_low': 2001,
                 'freq_high': 4000,
                 'freq_sweetspot': 2500,
                 'step_size': 250,
                 'weight': 32,
                 'num_freqs_to_include': 2,
                 'freqs': [2500, 3500]
                 #'freqs': [2000]
                 }

Presence = {'name': 'Presence',
            'freq_low': 4001,
            'freq_high': 6000,
            'freq_sweetspot': 5000,
            'step_size': 250,
            'weight': 32,
            'num_freqs_to_include': 1,
            'freqs': [5000]
            }

Brilliance = {'name': 'Brilliance',
              'freq_low': 6001,
              'freq_high': 20000,
              'freq_sweetspot': 12000,
              'step_size': 1500,
              'weight': 64,
              'num_freqs_to_include': 1,
              'freqs': [12000]
              }

HiFi_ascending = [SubBass, Bass, LowMidrange, Midrange, UpperMidrange, Presence, Brilliance]


class AudioFile:
    '''
    AudioFile Helper class
    '''

    def __init__(self, afile, type='WAV', achunk=4096, use_alsa=True):

        if not os.path.exists(afile):
            print("Audio File: ", afile, "not found!")
            return

        self.filename = afile
        self.chunk_size = achunk
        self.use_alsa = use_alsa
        self.chunk_levels = [0, 0, 0, 0, 0, 0, 0, 0]
        self.IsPlaying = False

        # Open the wave file
        self.wave_file = wave.open(afile, 'rb')
        self.nchannels = self.wave_file.getnchannels()
        self.frame_rate = self.wave_file.getframerate()
        self.sample_width = self.wave_file.getsampwidth()
        self.nframes = self.wave_file.getnframes()

        # prepare audio for output

        # Use ALSA setup
        if self.use_alsa is True:
            self.audio_output = aa.PCM(aa.PCM_PLAYBACK, aa.PCM_NORMAL)
            self.audio_output.setchannels(self.nchannels)
            self.audio_output.setrate(self.frame_rate)
            self.audio_output.setformat(aa.PCM_FORMAT_S16_LE)
            self.audio_output.setperiodsize(achunk)
        else:
            # Use Pyaudio vs Alsa(the pyaudio streamer is not good for this, but needed for Bluetooth audio..Ugh)
            import pyaudio
            self.pa = pyaudio.PyAudio()
            # open stream
            self.audio_output = self.pa.open(format=self.pa.get_format_from_width(self.sample_width),
                                             channels=self.nchannels, rate=self.frame_rate, output=True)

    def read_chunk(self):
        _wdata = self.wave_file.readframes(self.chunk_size)
        return _wdata

    def read_analyze_chunk(self, frqs=DEFAULT_FREQUENCIES, wghts=DEFAULT_FREQ_WEIGHT):
        _wdata = self.wave_file.readframes(self.chunk_size)
        self.chunk_levels.clear()
        self.chunk_levels = calculate_levels(_wdata, self.chunk_size, self.frame_rate, frqs, wghts)
        return _wdata

    def write_chunk(self, adata):
        try:
            self.audio_output.write(adata)
        except:
            print("Error playing Audio IO Error in stream write")
            return False
        return True

    def stop(self):

        if self.use_alsa is True:
            self.audio_output.close()
        else:
            self.audio_output.stop_stream()
            self.audio_output.close()
            self.pa.terminate()

        self.wave_file.close()


class Signals:
    '''
    Signals class
    '''

    def __init__(self, stype="hifi", frequencies=DEFAULT_FREQUENCIES, weights=DEFAULT_FREQ_WEIGHT):

        self.weights = []
        self.frequencies = []
        self.fidelities = []

        if stype == "manual" and len(frequencies) > 0:
            self.frequencies = frequencies
            if len(weights) == len(frequencies):
                _need_weights = False
                self.weights = weights
            else:
                _need_weights = True

        else:
            self.frequencies = build_freqs_from_hifi()
            self.weights = build_weights_from_hifi()
            _need_weights = False

        self.num_freqs = len(self.frequencies)
        for i in range(0, self.num_freqs):
            self.fidelities.append(get_hifi_name_from_freq(self.frequencies[i]))
            if _need_weights:
                self.weights.append(get_hifi_name_from_freq(self.frequencies[i]))


def build_playlist(songs_dir, randomize=True, debug=False):
    '''
    Build a playlist from the songs directory
    :param songs_dir: Directory of wavefile songs
    :param randomize: Randomize the list of songs
    :param debug: print debugging
    :return: list of songs to process
    '''

    songs = []

    # Check to make sure we have a songs directory
    if not os.path.exists(songs_dir):
        print('WARNING: No songs directory:', songs_dir)
        return songs

    # Loop through songs dir to generate list of songs
    for dfile in os.listdir(songs_dir):
        pfile = "%s/%s" % (songs_dir, dfile)
        if os.path.isfile(pfile):
            songs.append(pfile)
            if debug is True:
                print('Found valid song to add to playlist:', pfile)

    if randomize is True:
        random.shuffle(songs)

    if debug is True:
        print('Final playlist:', songs)

    return songs


def get_hifi_name_from_freq(frequency):
    '''
    Return the friendly HiFi name based on a frequency
    :param frequency: integer of frequency in Hz
    :return: Text of name
    '''

    # print("Freq:",frequency)
    for i in range(0, len(HiFi_ascending)):

        if frequency >= HiFi_ascending[i]['freq_low'] and frequency <= HiFi_ascending[i]['freq_high']:
            # print(" Found:",HiFi_ascending[i]['name'],HiFi_ascending[i]['freq_low'],HiFi_ascending[i]['freq_high'])
            return HiFi_ascending[i]['name']

    return "UNKNOWN"


def get_hifi_weight_from_freq(frequency):
    '''
    Get the corresponding weight to apply to the signal analysis based on frequency
    :param frequency: integer of frequency in Hz
    :return: integer of weight to apply
    '''

    for i in range(0, len(HiFi_ascending)):

        if frequency >= HiFi_ascending[i]['freq_low'] and frequency <= HiFi_ascending[i]['freq_high']:
            return int(HiFi_ascending[i]['weight'])

    return 0


def build_freqs_from_hifi():
    '''
    Return a list of frequencies based on standard HiFi
    :return: a list of hifi frequencies
    '''

    hifi_frequencies = []
    for i in range(0, len(HiFi_ascending)):

        for j in range(0, HiFi_ascending[i]['num_freqs_to_include']):
            hifi_frequencies.append(HiFi_ascending[i]['freqs'][j])

    return hifi_frequencies


def build_weights_from_hifi():
    '''
    Build the weights for each HiFi frequency
    :return: a list of weights
    '''

    hifi_weights = []
    for i in range(0, len(HiFi_ascending)):

        for j in range(0, HiFi_ascending[i]['num_freqs_to_include']):
            hifi_weights.append(HiFi_ascending[i]['weight'])

    return hifi_weights


def freq_hifi_auto_build_from_file(filename, freqs, weights, ChunkSize=4096, MaxFreqs=8):
    '''
    Experimental - Automatically build the HiFi frequencies from an audio file
    :param filename:
    :param freqs:
    :param weights:
    :param ChunkSize:
    :param MaxFreqs:
    :return:
    '''

    DataFFT = []

    # possible_freqs
    HiFi_freqs = dict()
    HiFi_weights = dict()
    HiFi_counts = dict()

    for i in range(0, len(HiFi_ascending)):
        HiFi_freqs[HiFi_ascending[i]['name']] = build_freq_matrix(HiFi_ascending[i]['freq_low'],
                                                                  HiFi_ascending[i]['step_size'],
                                                                  HiFi_ascending[i]['freq_high'])

        HiFi_weights[HiFi_ascending[i]['name']] = [HiFi_ascending[i]['weight'] for x in range(0, len(HiFi_freqs[HiFi_ascending[i]['name']]))]

        HiFi_counts[HiFi_ascending[i]['name']] = [int(0) for x in range(0,len(HiFi_freqs[HiFi_ascending[i]['name']]))]

        # print(HiFi_freqs[HiFi_ascending[i]['name']])
        # print(HiFi_weights[HiFi_ascending[i]['name']])
  
    wavfile = wave.open(filename, 'r')
    sample_rate = wavfile.getframerate()

    data = wavfile.readframes(ChunkSize)
    print("Calculating FFT on Wavfile...")

    while sys.getsizeof(data) > 16000:

        for HIFI in HiFi_freqs.keys():
            # print ("Processing Hifi:",HIFI,HiFi_freqs[HIFI],HiFi_weights[HIFI])
            DataFFT = calculate_levels(data, ChunkSize, sample_rate, HiFi_freqs[HIFI], HiFi_weights[HIFI])

            for j in range(0, len(DataFFT)):
                # possible_freqs_count[j] += DataFFT[j]
                HiFi_counts[HIFI][j] += DataFFT[j]

        data = wavfile.readframes(ChunkSize)

    wavfile.close()


    final_freq_counter = 0
    for j in range(0, len(HiFi_ascending)):
        name = HiFi_ascending[j]['name']
        num = HiFi_ascending[j]['num_freqs_to_include']
        HiFi_maxes = HiFi_counts[name]
        HiFi_maxes.sort(reverse=True)

        for k in range(0, num):
            candidate_count = HiFi_maxes[k]

            for l in range(0, len(HiFi_counts[name])):
                if HiFi_counts[name][l] == candidate_count:
                    print("Name", name, "Adding Frequency:", HiFi_freqs[name][l], "Count:", HiFi_counts[name][l])
                    freqs.append(HiFi_freqs[name][l])
                    weights.append(HiFi_weights[name][l])
                    final_freq_counter += 1


def freq_auto_build_from_file(filename, freqs, weights, ChunkSize=4096, MaxFreqs=8):
    '''
    Experimental - Attempt to build the key frequencies from an audio file
    :param filename: name of file
    :param freqs:
    :param weights:
    :param ChunkSize:
    :param MaxFreqs:
    :return:
    '''

    possible_freqs = build_freq_matrix(100, 100, 20000)
    print(possible_freqs)

    NumPossibleFreqs = len(possible_freqs)
    possible_freqs_count = [int(0) for i in range(0, NumPossibleFreqs)]

    # Counts=[int(0) for i in range(0,MaxFreqs)]

    possible_weights = [int(1) for i in range(0, NumPossibleFreqs)]
    DataFFT = []
    defaultweighting = [[0,1], [150,2], [625,8], [2500,16], [5000,32], [10000,64]]

    for i in range(0, NumPossibleFreqs):

        for j in range(0, len(defaultweighting)):
            if (defaultweighting[j][0] < possible_freqs[i]):
                possible_weights[i] = defaultweighting[j][1]

        if possible_weights[i] < 2:
            possible_weights[i]=2

    # print ("Freq:",possible_freqs[i],"Weight:",possible_weights[i])
      
    wavfile = wave.open(filename, 'r')
    sample_rate = wavfile.getframerate()

    data = wavfile.readframes(ChunkSize)

    print("Calculating FFT on Wavfile...")
    while sys.getsizeof(data) > 16000:
        # print("Processing FFT on Chunk")
        DataFFT = calculate_levels(data, ChunkSize, sample_rate, possible_freqs, possible_weights)

        for j in range(0, len(DataFFT)):
            possible_freqs_count[j] += DataFFT[j]

        data = wavfile.readframes(ChunkSize)

    wavfile.close()

    FreqCount = dict()
    for k in range(0, len(possible_freqs_count)):
        FreqCount[possible_freqs_count[k]] = k

    print(possible_freqs_count)
    print("Sorting List:")
    freqs_counts = possible_freqs_count
    freqs_counts.sort(reverse=True)
  
    print(freqs_counts)

    Counts = freqs_counts[0:MaxFreqs]
    print(Counts)

    for j in range(0, len(Counts)):
        freqs[j] = possible_freqs[ FreqCount[Counts[j]] ]
        print("Final Frequency:", freqs[j], "with count:", Counts[j])


  # print("Final Freqs:",freqs)


def build_freq_matrix(start_freq=50, step_size=50, end_freq=20000):
    '''
    Build a frequency matrix based on a range of frequencies from start to end
    :param start_freq: int of start freq in Hz
    :param step_size: int step
    :param end_freq: int of end freq in Hz
    :return:
    '''

    if start_freq < 20:
        start_freq = 20

    stop = int(round((end_freq-start_freq)/step_size))
    # print ("Stop:",stop)
    return [start_freq+(step_size*x) for x in range(0, stop)]


def calculate_levels(data, chunk, sample_rate, freqs, weighting):
    '''
    Perform FFT analysis on wave file chunk
    :param data: a list of wave file signal data to be analized
    :param chunk: chunk size
    :param sample_rate: sample rate of wave file
    :param freqs: frequencies of interest
    :param weighting: weighting to apply to the frequencies
    :return: a list of scaled signal levels
    '''

    signal_levels = [int(0) for i in range(0, len(freqs))]

    power = []

    # Convert raw data (ASCII string) to numpy array
    data = unpack("%dh" % (len(data)/2), data)
    data = np.array(data, dtype='h')

    # Apply FFT - real data
    fourier = np.fft.rfft(data)

    # Remove last element in array to make it the same size as chunk
    fourier = np.delete(fourier, len(fourier)-1)

    # Find average 'amplitude' for specific frequency ranges in Hz
    power = np.abs(fourier)
 
    # Loop through freqs
    v1 = int(2*chunk*0/sample_rate)

    for i in range(0, len(freqs)):
        v2 = int(2*chunk*freqs[i]/sample_rate)
        # print (v1,v2)
        try:
            signal_levels[i] = int((np.mean(power[v1:v2:1]) * weighting[i]) / 1000000)

        except:
            signal_levels[i] = 0

        # Clip signal level at max
        if signal_levels[i] > MAX_SIGNAL_LEVEL:
            signal_levels[i] = MAX_SIGNAL_LEVEL

        v1 = v2

    return signal_levels


def print_levels(level_data):
    '''
    Helper function to Print out the signal data (like a spectrum analyzer)
    :param level_data:
    :return:
    '''

    os.system("clear")
    for i in range(1, MAX_SIGNAL_LEVEL+1):
        row = (MAX_SIGNAL_LEVEL + 1) - i

        for j in range(0, len(level_data)):

            if row <= level_data[j]:
                sys.stdout.write(str('*'))

            else:
                sys.stdout.write(str(' '))

        print("")

    for i in range(0, len(level_data)):
        sys.stdout.write(str(i))

    print("")


