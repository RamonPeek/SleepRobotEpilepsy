import aubio
import numpy as num
import pyaudio
import sys
from AppState import AppState
import time
from pydub import AudioSegment
from pydub.playback import play

BUFFER_SIZE             = 20484
CHANNELS                = 1
FORMAT                  = pyaudio.paFloat32
METHOD                  = "default"
SAMPLE_RATE             = 44100
HOP_SIZE                = BUFFER_SIZE//2
PERIOD_SIZE_IN_FRAME    = HOP_SIZE


def main(args):
    # Initiating PyAudio object.
    pA = pyaudio.PyAudio()
    info = pA.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (pA.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", pA.get_device_info_by_host_api_device_index(0, i).get('name'))

    selected_mic = input()

    # Infinite loop!
    # Open the microphone stream.
    mic = None
    state = AppState.DETECTING

    while True:
        if mic is None:
            mic = pA.open(format=FORMAT, channels=CHANNELS,
                          rate=SAMPLE_RATE, input=True,
                          frames_per_buffer=PERIOD_SIZE_IN_FRAME,
                          input_device_index=int(selected_mic)
                          )

        # Initiating Aubio's pitch detection object.
        #pDetection = aubio.pitch(METHOD, BUFFER_SIZE, HOP_SIZE, SAMPLE_RATE)
        # Set unit.
        #pDetection.set_unit("Hz")
        # Frequency under -40 dB will considered
        # as a silence.
        #pDetection.set_silence(-40)

        volume = 0
        #pitch = 0
        if state is AppState.DETECTING:
            # Always listening to the microphone.
            data = mic.read(PERIOD_SIZE_IN_FRAME)
            # Convert into number that Aubio understand.
            samples = num.fromstring(data,
                dtype=aubio.float_type)
            # Finally get the pitch.
            #pitch = pDetection(samples)[0]
            # Compute the energy (volume)
            # of the current frame.
            volume = num.sum(samples**2)/len(samples)
            # Format the volume output so it only
            # displays at most six numbers behind 0.
            volume = "{:6f}".format(volume)

            # Finally print the pitch and the volume.
            #print('pitch:' + str(pitch) + " - " + 'volume: ' + str(volume))
            print('volume: ' + str(volume))

            if float(volume) > 0.0008:
                print('Threshold reached for starting seizure prevention, starting countdown')
                state = AppState.SEIZURE_DETECTED
        elif state is AppState.SEIZURE_DETECTED:
            print('Seizure detected, starting countdown!')
            for count in range(10):
                countIndex = count + 1
                print(countIndex)
                sound = AudioSegment.from_wav(str(countIndex) + '.wav')
                play(sound)
                #0.4 comes from 1S wait minus average of audio playback
                time.sleep(0.4)
            state = AppState.SEIZURE_ACTION_HANDLED
        elif state is AppState.SEIZURE_ACTION_HANDLED:
            print('Seizure handled, waiting 10 seconds before detecting again.');
            time.sleep(10)
            mic = None
            state = AppState.DETECTING

if __name__ == "__main__": main(sys.argv)