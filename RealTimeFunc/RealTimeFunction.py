import wave
import pyaudio
import struct
import numpy as np
# from pylab import *
# import numba
from effectpy import biQuad
from stop_watch import stop_watch

__author__ = "Hitoki Yamada"
__status__ = "Prototype"
__version__ = "0.0.1"
__date__ = "2018.1.11"

data_buff = np.array([[0.0, 0.0],[0.0, 0.0]]) # [[One before L,two before L],[[One before R,two before R]
mod_buff = np.array([[0.0, 0.0],[0.0, 0.0]]) # [[One before L,two before L],[[One before R,two before R]

def unpack_chunk(data_chunk:list, CHUNK:int=1024, channel_number:int=0):
    """ Return chunk by Stereo or MONO depending on channel number.
        Parameters
        ----------
        data_chunk : list\n
        CHUNK       : int\n
        Chunk size.Default 1024.\n
        channel_number : int\n
    """
    # Unpack
    # fromiter()より10^6倍アクセスが早い
    try:
        data_chunk = np.frombuffer(data_chunk, dtype="int16") / 32768.0 # Normalize -1~1
    except AttributeError:
        return -1
    if(channel_number == 2): #STEREO
        _unpack_data = np.array([data_chunk[::2], data_chunk[1::2]])
    elif(channel_number == 1): #MONO
        _unpack_data = np.array(data_chunk)
    else:
        _unpack_data = -1
        print("The number of channel is incorrect.")
    return _unpack_data

def pack_data(data, data_size:int, channel_number:int=0):
    """ packing data to binary chunk.
        Parameters
        ----------
        data    : bytes\n
        data_size   :  int\n
        channel_number  : int\n
    """
    # Join Stereo data
    if (channel_number == 2): #STEREO
        try:
            _pack_data = np.empty(data_size*2) # 2ch(LR)
            _pack_data[::2] = data[0]
            _pack_data[1::2] = data[1]
        except ValueError:
            return -1
    elif (channel_number == 1): #MONO
        _pack_data = data
    else:
        print("The number of channel is incorrect.")
        return -1

    # Denormalize
    _pack_data = [int(x * 32767.0) for x in _pack_data]
    # Packing binary
    _pack_data = struct.pack("h" * len(_pack_data), *_pack_data)
    return _pack_data

def gain_make(data, data_size:int, ch_number:int=0, gain:int=0.6):
    for l in range(data_size):
        if(ch_number == 2):
            for n in range(ch_number):
                data[n][l] = data[n][l] * gain
        elif(ch_number == 1):
            data[l] = data[l] * gain
        else:
            data = -1
            print("The number of channel is incorrect.")
    return data

def limmiter(data, data_size:int, ch_number:int=0):
    """ Limmiter(-1 ~ 1) normalizing.
        Parameters
        ----------
        data    : bytes\n
        data_size : int\n
        ch_number : int\n
    """
    for i in range(data_size):
        if (ch_number == 2):
            for j in range(ch_number):
                if (data[j][i] < -1):
                    data[j][i] = -1
                elif(data[j][i] > 1):
                    data[j][i] = 1
        elif (ch_number == 1):
            if (data[i] < -1):
                data[i] = -1
            elif(data[i] > 1):
                data[i] = 1
        else:
            data = -1
            print("The number of channel is incorrect.")
    return data

@stop_watch
def iir_beta(data, data_size:int, coeff, ch_number:int=0):
    _moddata= np.empty_like(data)
    for i in range(data_size):
        if (ch_number == 2):
            for j in range(ch_number):
                _moddata[j][i] = coeff[1][0] * data[j][i] + coeff[1][1] * data_buff[j][0] + coeff[1][2] \
                                * data_buff[j][1] - coeff[0][1] * mod_buff[j][0] - coeff[0][2] * mod_buff[j][1]
                data_buff[j][1] = data_buff[j][0]
                data_buff[j][0] = _moddata[j][i]
                mod_buff[j][1] = mod_buff[j][0]
                mod_buff[j][0] = _moddata[j][i]
        elif (ch_number == 1):
            moddata[i] = coeff[1][0] * data[i] + coeff[1][1] * data_buff[0][0] + coeff[1][2] \
                        * data_buff[0][1] - coeff[0][1] * mod_buff[0][0] - coeff[0][2] * mod_buff[0][1]
            data_buff[0][1] = data_buff[0][0]
            data_buff[0][0] = _moddata[i]
            mod_buff[0][1] = mod_buff[0][0]
            mod_buff[0][0] = _moddata[i]
    return _moddata

def plot_wave(data):
    """ Plot wave for matplotlib"""
    # subplot(211)
    # plot(data)
    # axis([0, 140000, -1.0, 1.0])
    # subplot(212)
    # plot(data)
    # axis([0, 140000, -1.0, 1.0])
    # show()
    pass


def real_time_prosess(wavfile:str, CHUNK:int):
    """ Real time prosess.
        Parameters
        ----------
        wavefile    : str\n
        CHUNK       : int\n
    """

    wf = wave.open(wavfile, 'rb')
    p = pyaudio.PyAudio()
    ch_num = wf.getnchannels()
    f_rate = wf.getframerate()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=ch_num,
                    rate=f_rate,
                    output=True)

    # Real time function
    data_chunk = wf.readframes(CHUNK)
    while len(data_chunk) != 0:
        # Unpack chunk
        data = unpack_chunk(data_chunk, CHUNK, ch_num)

        # Entry original function#####
        moddata = np.empty_like(data)
        # Create Low pass filter coeff
        coeff = biQuad(f_rate).bq_lowpass(600, 0.7892)
        moddata = iir_beta(data, data.shape[1], coeff, ch_num)
        #Gain make up
        # moddata = gain_make(moddata, data_size, ch_num)
        # Limitter(-1 ~ 1)
        # moddata = limmiter(moddata, data_size, ch_num)
        #############################

        # unpack chunk
        data_chunk = pack_data(moddata, data.shape[1], ch_num)

        if (data_chunk != -1):
            stream.write(data_chunk)
            data_chunk = wf.readframes(CHUNK)
        else:
            stream.stop_stream()
            stream.close()
            p.terminate()
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == '__main__':

    wavfile="wav/sample_short_441.wav"
    CHUNK = 1024
    # 処理が間に合わないようなら
    # CHUNK = CHUNK*2
    real_time_prosess(wavfile, CHUNK)