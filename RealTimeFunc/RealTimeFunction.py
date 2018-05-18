import wave
import pyaudio
import struct
import numpy
from pylab import *

def real_time_prosess(wavfile:str, CHUNK):
    wf = wave.open(wavfile, 'rb')
    p = pyaudio.PyAudio()
    ch_num = wf.getnchannels()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # Real time function
    data_chunk = wf.readframes(CHUNK)
    while stream.is_active(): #wave moduleのバグでis_activeの同期が取れていない。
        # unpack chunk
        data = unpack_chunk(data_chunk, CHUNK, ch_num)

        # Entry original function#####
        moddata = data
        for l in range(CHUNK):
            #Gain up(-6dB)
            moddata[0][l] = moddata[0][l] * 0.5
            moddata[1][l] = moddata[1][l] * 0.5

        # Limitter(-1 ~ 1)
        moddata = limmiter(moddata, CHUNK, ch_num)
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

def unpack_chunk(data_chunk, CHUNK:int, channel_number:int=0):
    """ Return chunk by Stereo or MONO depending on channel number."""
    # Unpack
    # fromiter()より10^6倍アクセスが早い
    try:
        data_chunk = frombuffer(data_chunk, dtype="int16") / 32768.0 # Normalize -1~1
    except AttributeError:
        return -1
    if(channel_number == 2): #STEREO
        _unpack_data = np.empty((2, CHUNK))
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

def limmiter(data,CHUNK ,ch_number:int=0):
    """Limmit(-1 ~ 1)"""
    if (ch_number == 2):
        for i in range(CHUNK):
            if  (data[0][i] < -1):
                data[0][i] = -1
            elif(data[0][i] > 1):
                data[0][i] = 1
        for j in range(CHUNK):
            if  (data[1][j] < -1):
                data[1][j] = -1
            elif(data[1][j] > 1):
                data[1][j] = 1
    elif (ch_number == 1):
        for k in range(CHUNK):
            if  (data[k] < -1):
                data[k] = -1
            elif(data[k] > 1):
                data[k] = 1
    else:
        data = -1
        print("The number of channels is not defined.")
    return data

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

if __name__ == '__main__':

    wavfile="wav/sample_short_441.wav"
    CHUNK = 1024
    # 処理が間に合わないようなら
    # CHUNK = CHUNK*2
    real_time_prosess(wavfile, CHUNK)