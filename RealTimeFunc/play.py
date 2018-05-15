import wave
import pyaudio
import struct
# import matplotlib
from pylab import *

CHUNK = 1024
# 処理が間に合わないようなら
# CHUNK*2
wavfile="wav/sample_Full.wav"

wf = wave.open(wavfile, 'rb')
p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

def limmiter(data):
    """Limit(-1 ~ 1)"""
    for sample in data:
        if (sample < -1):
            sample = -1
        if (sample > 1):
            sample = 1
    return data

data = wf.readframes(CHUNK)
while data[0] != '':
    # Unpack
    data = frombuffer(data, dtype="int16") / 32768.0 # Normalize

    # Separate LR
    if (wf.getnchannels() == 2):
        left = data[::2]
        right = data[1::2]

    # Entry original function#####
    moddata = data

    # Limitter(-1 ~ 1)
    moddata = limmiter(moddata)
    #############################

    # Join LR
    if (wf.getnchannels() == 2):
        moddata[::2] = left
        moddata[1::2] = right

    # Denormalize
    moddata = [int(x * 32767.0) for x in moddata]
    # Packing binary
    moddata = struct.pack("h" * len(moddata), *moddata)

    stream.write(moddata)
    data = wf.readframes(CHUNK)

stream.stop_stream()
stream.close()
p.terminate()