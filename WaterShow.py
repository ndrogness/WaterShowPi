#!/usr/bin/env python3

import RPi.GPIO as GPIO
import sys
import time
import RogyAudio

######## Solenoid Definition ################
#    [Name,Enabled {True|False},GPIO]
S0 = ['S0', True, 17]
S1 = ['S1', True, 27]
S2 = ['S2', True, 22]
S3 = ['S3', True, 10]
S4 = ['S4', True, 9]
S5 = ['S5', True, 11]
S6 = ['S6', True, 13]
Solenoids = [S0, S1, S2, S3, S4, S5, S6]
BassSolenoids = [3, 4]
ChorusSolenoids = [5, 6]

###### Pump Definition ####
#      [IsRunning {True|False},GPIO]
Pump = [False, 23]

########## Control Buttons ###########
# GPIO for Play and Pause (set to 0 if not using)
PLAY_BUTTON_GPIO = 5
PAUSE_BUTTON_GPIO = 6
DEBUG = False

####################### No edit below this ##########################
### Globals...yeh I know
CAN_PLAY = True
SONG_PAUSED = False
NEXT_SONG = False
S_NAME = 0
S_ENABLED = 1
S_GPIO = 2
S_STATUS = 3
S_TOGGLE = 4
PumpColdStartDelay = 5
PumpWarmStartDelay = 4
RunVolume = 100
P_STATE = 0
P_GPIO = 1
P_RUN = 0
P_STOP = 1
V_OPEN = 0
V_CLOSE = 1

#       [IsRunning,LastPushButtonTime]
STATE = {'ISRUNNING': False, 'PUSHBUTTON_LASTTIME': int(round(time.time()*1000))}

# WavChunkIntesity = [0,0,0,0,0,0,0,0]
Freqs = [100, 500, 900, 20000]
Freqweighting = [2, 4, 6, 1]

BASS = {
    'FreqIndex': 0,
    'IntesityMinTrigger': 8,
    'Solenoids': BassSolenoids,
    'MinCycleInterval': 250,
    'MaxConseqCycles': 30,
    'CurTriggerTime': 0,
    'CurCycleCount': 0,
    'CurSolenoid': 0,
    'NextSolenoid': 0,
    'IsRunning': False
    }

CHORUS = {
    'FreqIndex': 2,
    'IntesityMinTrigger': 8,
    'Solenoids': ChorusSolenoids,
    'MinCycleInterval': 2000,
    'MaxConseqCycles': 10,
    'CurTriggerTime': 0,
    'CurCycleCount': 0,
    'CurSolenoid': 0,
    'NextSolenoid': 0,
    'IsRunning': False
    }

NumSolenoids = len(Solenoids)
Solenoid_MinFireTime = .250
SD = dict()


def dprint(msg):
    '''
    Print if Debug is true
    :param msg:
    :return:
    '''
    if DEBUG is True:
        print(msg)


def pause_callback(channel):
    '''
    Call back function when PAUSE button is pressed
    :param channel:
    :return:
    '''
    global CAN_PLAY
    global SONG_PAUSED
    global NEXT_SONG

    dprint('Pause Pressed -> Can Play:{0}, Paused:{1}, Next:{2}'.format(CAN_PLAY, SONG_PAUSED, NEXT_SONG))
    if CAN_PLAY is False:
        CAN_PLAY = False

    elif SONG_PAUSED is True:
        SONG_PAUSED = False
        CAN_PLAY = True

    elif SONG_PAUSED is False:
        SONG_PAUSED = True
    else:
        CAN_PLAY = False
        SONG_PAUSED = False


def play_callback(channel):
    '''
    Call back function when PLAY button is pressed
    :param channel: GPIO channel
    :return:
    '''
    global CAN_PLAY
    global SONG_PAUSED
    global NEXT_SONG

    dprint('Play Pressed -> Can Play:{0}, Paused:{1}, Next:{2}'.format(CAN_PLAY, SONG_PAUSED, NEXT_SONG))
    if CAN_PLAY is False:
        CAN_PLAY = True
    elif NEXT_SONG is False:
        NEXT_SONG = True
    else:
        NEXT_SONG = False

    SONG_PAUSED = False


def init_gpio():

    # for GPIO numbering, choose BCM
    GPIO.setmode(GPIO.BCM)

    if PAUSE_BUTTON_GPIO > 1:
        GPIO.setup(PAUSE_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(PAUSE_BUTTON_GPIO, GPIO.FALLING, callback=pause_callback, bouncetime=300)

    if PLAY_BUTTON_GPIO > 1:
        GPIO.setup(PLAY_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(PLAY_BUTTON_GPIO, GPIO.FALLING, callback=play_callback, bouncetime=300)

    # Setup Pump GPIO
    GPIO.setup(Pump[P_GPIO], GPIO.OUT, initial=P_STOP)

    for i in range(0, NumSolenoids):
        # Add CurrentStatus and DoToggle
        Solenoids[i].extend([V_CLOSE, False])

        # If enabled, setup GPIO for output
        if Solenoids[i][S_ENABLED]:
            SD[Solenoids[i][S_NAME]] = i
            GPIO.setup(Solenoids[i][S_GPIO], GPIO.OUT, initial=V_CLOSE)

    print('Configured Solendoids ->', SD)


def init_solenoids():

    GPIO.output(Solenoids[0][S_GPIO], V_OPEN)
    Solenoids[0][S_STATUS] = V_OPEN

    for i in range(1, NumSolenoids):
        if Solenoids[i][S_ENABLED]:
            GPIO.output(Solenoids[i][S_GPIO], V_CLOSE)
            Solenoids[i][S_STATUS] = V_CLOSE


def solenoid_send(SolenoidX, NewState):

    for i in range(1, NumSolenoids):
        if i == SolenoidX:

            if NewState == V_CLOSE and Solenoids[SolenoidX][S_STATUS] != V_CLOSE:
                print("Changing state:", SolenoidX, ":", Solenoids[SolenoidX][S_STATUS], " -> ", V_CLOSE)
                GPIO.output(Solenoids[SolenoidX][S_GPIO], V_CLOSE)
                Solenoids[SolenoidX][S_STATUS] = V_CLOSE
                if i == 3:
                    GPIO.output(Solenoids[1][S_GPIO], V_CLOSE)
                    Solenoids[1][S_STATUS] = V_CLOSE

                if i == 4:
                    GPIO.output(Solenoids[2][S_GPIO], V_CLOSE)
                    Solenoids[2][S_STATUS] = V_CLOSE
        
            if NewState == V_OPEN and Solenoids[SolenoidX][S_STATUS] != V_OPEN:
                print("Changing state:",SolenoidX,":",Solenoids[SolenoidX][S_STATUS]," -> ",V_OPEN)
                GPIO.output(Solenoids[SolenoidX][S_GPIO], V_OPEN)
                Solenoids[SolenoidX][S_STATUS] = V_OPEN

                if i == 3:
                    GPIO.output(Solenoids[1][S_GPIO], V_OPEN)
                    Solenoids[1][S_STATUS] = V_OPEN
                if i == 4:
                    GPIO.output(Solenoids[2][S_GPIO], V_OPEN)
                    Solenoids[2][S_STATUS] = V_OPEN

        elif NewState == V_OPEN:
            GPIO.output(Solenoids[i][S_GPIO], V_CLOSE)
            Solenoids[i][S_STATUS] = V_CLOSE

    # Figure out if we need to build pressure or not
    BackPressure = True
    for i in range (1,NumSolenoids) :
        if Solenoids[i][S_STATUS] == V_OPEN:
            BackPressure = False

    # Close backpressure valve
    if BackPressure:
        GPIO.output(Solenoids[0][S_GPIO], V_OPEN)
        Solenoids[0][S_STATUS] = V_OPEN
    else:
        GPIO.output(Solenoids[0][S_GPIO], V_CLOSE)
        Solenoids[0][S_STATUS] = V_CLOSE


def PumpCtl (RunPump):

    # Always make sure relief valve is on
    GPIO.output(Solenoids[0][S_GPIO], V_OPEN)
    Solenoids[0][S_STATUS]=V_OPEN

    if RunPump and not Pump[P_STATE]:
        GPIO.output(Pump[P_GPIO], P_RUN)

        if (STATE['ISRUNNING']):
            print ("Starting Pump...Delaying:", PumpWarmStartDelay)
            time.sleep(PumpWarmStartDelay)
        else:
            print("Starting Pump...Delaying:", PumpColdStartDelay)
            time.sleep(PumpColdStartDelay)
            Pump[P_STATE] = True

    if not RunPump and Pump[P_STATE]:
        GPIO.output(Pump[P_GPIO], P_STOP)
        print("Stopping Pump...")
        Pump[P_STATE] = False


def check_signal_trigger(WavChunkIntensity, CurTime):
    '''
    Check the intensity of the Wav signals and fire solenoids if needed
    :param WavChunkIntensity: Signal data from Wave file chunk
    :param CurTime: Current time
    :return:
    '''

    if not CHORUS['IsRunning'] and WavChunkIntensity[BASS['FreqIndex']] >= BASS['IntesityMinTrigger']:

        CurSolenoid = BASS['CurSolenoid']
        NextSolenoid = BASS['NextSolenoid']
        ElapsedTime = CurTime - BASS['CurTriggerTime']

        if ElapsedTime > BASS['MinCycleInterval']:

            if BASS['IsRunning']:
                dprint('{0}: {1} -> Closing: {2}'.format(CurTime, WavChunkIntensity,
                                                         Solenoids[BASS['Solenoids'][CurSolenoid]][S_NAME]))
                solenoid_send(BASS['Solenoids'][CurSolenoid], V_CLOSE)

            if BASS['CurCycleCount'] == BASS['MaxConseqCycles']:
                dprint('{0}: {1} -> Stoping: {2}'.format(CurTime, WavChunkIntensity,
                                                         Solenoids[BASS['Solenoids'][CurSolenoid]][S_NAME]))
                #  print ("Stopng(",CurTime,"): ",Solenoids[BASS['Solenoids'][CurSolenoid]][S_NAME],WavChunkIntensity)
                solenoid_send(BASS['Solenoids'][CurSolenoid], V_CLOSE)
                BASS['IsRunning'] = False
                BASS['CurCycleCount'] = 0

            else:
                dprint('{0}: {1} -> Firing: {2}'.format(CurTime, WavChunkIntensity,
                                                         Solenoids[BASS['Solenoids'][NextSolenoid]][S_NAME]))
                # print("Firing(", CurTime, "): ", Solenoids[BASS['Solenoids'][NextSolenoid]][S_NAME], WavChunkIntensity)
                solenoid_send(BASS['Solenoids'][NextSolenoid], V_OPEN)

                BASS['CurSolenoid'] = NextSolenoid

                NextSolenoid = NextSolenoid+1
                if NextSolenoid > len(BASS['Solenoids'])-1:
                    BASS['NextSolenoid'] = 0
                else:
                    BASS['NextSolenoid'] = NextSolenoid

                BASS['IsRunning'] = True
                BASS['CurTriggerTime'] = CurTime
                BASS['CurCycleCount'] += CurTime
                CHORUS['CurCycleCount'] = 0
 

    if CHORUS['IsRunning'] and WavChunkIntensity[CHORUS['FreqIndex']] < CHORUS['IntesityMinTrigger']:
        CurSolenoid = CHORUS['CurSolenoid']
        NextSolenoid = CHORUS['NextSolenoid']
        ElapsedTime = CurTime - CHORUS['CurTriggerTime']

        if ElapsedTime > CHORUS['MinCycleInterval']:
            dprint('{0}: {1} -> Spindown: {2}'.format(CurTime, WavChunkIntensity,
                                                     Solenoids[CHORUS['Solenoids'][CurSolenoid]][S_NAME]))
            # print ("Spindn(", CurTime, "): ", Solenoids[CHORUS['Solenoids'][CurSolenoid]][S_NAME], WavChunkIntensity)
            solenoid_send(CHORUS['Solenoids'][CurSolenoid], V_CLOSE)
            NextSolenoid = NextSolenoid + 1
            if NextSolenoid > len(CHORUS['Solenoids'])-1:
                CHORUS['NextSolenoid'] = 0
            else:
                CHORUS['NextSolenoid'] = NextSolenoid

        CHORUS['IsRunning'] = False
        CHORUS['CurCycleCount'] = 0

    if WavChunkIntensity[CHORUS['FreqIndex']] >= CHORUS['IntesityMinTrigger']:

        CurSolenoid = CHORUS['CurSolenoid']
        NextSolenoid = CHORUS['NextSolenoid']
        ElapsedTime = CurTime - CHORUS['CurTriggerTime']

        if ElapsedTime > CHORUS['MinCycleInterval']:

            if CHORUS['IsRunning']:
                dprint('{0}: {1} -> Closing: {2}'.format(CurTime, WavChunkIntensity,
                                                          Solenoids[CHORUS['Solenoids'][CurSolenoid]][S_NAME]))
                #print("Closng(", CurTime, "): ", Solenoids[CHORUS['Solenoids'][CurSolenoid]][S_NAME], WavChunkIntensity)
                solenoid_send(CHORUS['Solenoids'][CurSolenoid], V_CLOSE)
      
            if CHORUS['CurCycleCount'] == CHORUS['MaxConseqCycles']:
                dprint('{0}: {1} -> Stoping: {2}'.format(CurTime, WavChunkIntensity,
                                                         Solenoids[CHORUS['Solenoids'][CurSolenoid]][S_NAME]))
                # print("Stopng(", CurTime, "): ", Solenoids[CHORUS['Solenoids'][CurSolenoid]][S_NAME], WavChunkIntensity)
                solenoid_send(CHORUS['Solenoids'][CurSolenoid], V_CLOSE)
                CHORUS['IsRunning'] = False
                CHORUS['CurCycleCount'] = 0

            else:
                dprint('{0}: {1} -> Firing: {2}'.format(CurTime, WavChunkIntensity,
                                                         Solenoids[CHORUS['Solenoids'][NextSolenoid]][S_NAME]))
                # print("Firing(", CurTime, "): ", Solenoids[CHORUS['Solenoids'][NextSolenoid]][S_NAME], WavChunkIntensity)
                solenoid_send(CHORUS['Solenoids'][NextSolenoid], V_OPEN)

                CHORUS['CurSolenoid'] = NextSolenoid

                NextSolenoid = NextSolenoid + 1
                if NextSolenoid > len(CHORUS['Solenoids'])-1:
                    CHORUS['NextSolenoid'] = 0
                else:
                    CHORUS['NextSolenoid'] = NextSolenoid

                CHORUS['IsRunning'] = True
                CHORUS['CurTriggerTime'] = CurTime
                CHORUS['CurCycleCount'] += 1
                BASS['CurCycleCount'] = 0


def watershow_start(songs_playlist):
    '''
    Start the show and run through playlist once
    :param songs_playlist: list of songs
    :return:
    '''

    global CAN_PLAY
    global SONG_PAUSED
    global NEXT_SONG

    # Loop through the playlist and play each song
    for song_index in range(0, len(songs_playlist)):

        # Start pump
        if not Pump[P_STATE]:
            PumpCtl(True)

        StartTime = int(round(time.time()*1000))
        CurrentChunkNum = 1 #ignore the header line
        CurTime = 0

        # init Audio File object
        audio_file = RogyAudio.AudioFile(songs_playlist[song_index])
        print("Playing:", playlist[song_index], "->", audio_file.nframes, audio_file.nchannels,
              audio_file.frame_rate, audio_file.sample_width)

        # Run Audio analysis on it, i.e. FFT
        audio_data = audio_file.read_analyze_chunk(frqs=Freqs, wghts=Freqweighting)
        chunk_counter = 1
        # print(sys.getsizeof(audio_data))

        while sys.getsizeof(audio_data) > 16000 and STATE['ISRUNNING']:

            # WavChunkIntensity=FFT.calculate_levels(WavData,chunk,sample_rate,Freqs,Freqweighting)
            # print(WavChunkIntensity)
            # IntensitySend(WavChunkIntensity,CurTime)
            # AudioOutput.write(WavData)
            # WavData = WavFile.readframes(chunk)

            CurTime = int(round(time.time()*1000)) - StartTime
            check_signal_trigger(audio_file.chunk_levels, CurTime)

            if audio_file.write_chunk(audio_data) is True:
                audio_data = audio_file.read_analyze_chunk(frqs=Freqs, wghts=Freqweighting)
            else:
                raise IOError

            chunk_counter += 1
            while SONG_PAUSED is True:
                time.sleep(1)

            if NEXT_SONG is True:
                break

        audio_file.stop()
        BASS['IsRunning'] = False
        BASS['CurTriggerTime'] = 0
        BASS['CurCycleCount'] = 0
        CHORUS['IsRunning'] = False
        CHORUS['CurTriggerTime'] = 0
        CHORUS['CurCycleCount'] = 0
        #STATE['ISRUNNING']=False

    PumpCtl(False)
    init_solenoids()


def watershow_stop():

    for i in range(0, NumSolenoids):
        # Add CurrentStatus and DoToggle
        Solenoids[i].extend([V_CLOSE, False])


def clean_exit():

    watershow_stop()
    GPIO.cleanup()
    exit()
  

if __name__ == '__main__':
    '''
    Main context
    '''

    try:

        # Init GPIO and SOlenoids
        init_gpio()
        init_solenoids()

        # Build a playlist of songs
        playlist = RogyAudio.build_playlist('/home/pi/WaterShowPi/songs')

        loop_counter = 0
        while True:
            STATE['ISRUNNING'] = True
            watershow_start(playlist)
            time.sleep(2)
            loop_counter += 1

    except KeyboardInterrupt:
        clean_exit()

    except Exception as e:
        print("Exception:", sys.exc_info()[0], "Argument:", str(e))
        clean_exit()

