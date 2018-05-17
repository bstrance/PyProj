import wave
import pyaudio
import struct
import numpy
from pylab import *

def limmiter(data, ch_number:int=0):
    """Limmit(-1 ~ 1)"""
    if (ch_number == 2):
        for sample in data[0]:
            if  (sample < -1):
                sample = -1
            elif(sample > 1):
                sample = 1
        for sample in data[1]:
            if  (sample < -1):
                sample = -1
            elif(sample > 1):
                sample = 1
    elif (ch_number == 1):
        for sample in data:
            if  (sample < -1):
                sample = -1
            elif(sample > 1):
                sample = 1
    else:
        data = -1
        print("The number of channels is not defined.")
    return data

def unpack_chunk(data_chunk, channel_number:int=0):
    """ Return chunk by Stereo or MONO depending on channel number."""
    # Unpack
    # fromiter()より10^6倍アクセスが早い
    try:
        data_chunk = frombuffer(data_chunk, dtype="int16") / 32768.0 # Normalize -1~1
    except AttributeError:
        return -1

    if(channel_number == 2): #STEREO
        _unpack_data = [data_chunk[::2], data_chunk[1::2]]
    elif(channel_number == 1): #MONO
        _unpack_data = data_chunk
    else:
        _unpack_data = -1
        print("The number of channels is not defined.")
    return _unpack_data

def pack_data(data, CHUNK:int, channel_number:int=0):
    """ packing data chunk. """
    # Join Stereo data
    if (channel_number == 2): #STEREO
        try:
            _pack_data = np.empty(CHUNK*2) # 2ch(LR)
            _pack_data[::2] = data[0]
            _pack_data[1::2] = data[1]
        except ValueError:
            return -1
    elif (channel_number == 1): #MONO
        _pack_data = data
    else:
        print("The number of channels is not defined.")
        return -1

    # Denormalize
    _pack_data = [int(x * 32767.0) for x in _pack_data]
    # Packing binary
    _pack_data = struct.pack("h" * len(_pack_data), *_pack_data)
    return _pack_data

def plot_wave(data):
    """Plot wave for matplotlib"""
    import matplotlib
    subplot(211)
    plot(data)
    axis([0, 140000, -1.0, 1.0])
    subplot(212)
    plot(data)
    axis([0, 140000, -1.0, 1.0])
    show()

def real_time_prosess(wavfile:str, CHUNK):
    wf = wave.open(wavfile, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    ch_num = wf.getnchannels()

    data_chunk = wf.readframes(CHUNK)
    while stream.is_active(): #wave moduleのバグでis_activeの同期が取れていない。
        # unpack chunk
        data = unpack_chunk(data_chunk, ch_num)

        # Entry original function#####
        #Gain up(6dB)
        moddata = data * 2

        # Limitter(-1 ~ 1)
        moddata = limmiter(moddata, ch_num)
        #############################

        # unpack chunk
        data_chunk = pack_data(moddata, CHUNK, ch_num)

        if (data_chunk != -1):
            stream.write(data_chunk)
            data_chunk = wf.readframes(CHUNK)
        else:
            stream.stop_stream()
            stream.close()
            p.terminate()

if __name__ == '__main__':

    wavfile="wav/sample_short.wav"
    CHUNK = 1024
    # 処理が間に合わないようなら
    # CHUNK = CHUNK*2
    real_time_prosess(wavfile, CHUNK)