import wave
import pyaudio
import struct
import numpy as np
from effectpy import biQuad
from func_time import func_time

__author__ = "Hitoki Yamada"
__status__ = "Prototype"
__version__ = "0.0.1"
__date__ = "2018.1.11"

data_buff = np.array([[0.0, 0.0], [0.0, 0.0]], dtype = 'float64') # [[One before L,two before L],[[One before R,two before R]
mod_buff = np.array([[0.0, 0.0], [0.0, 0.0]], dtype = 'float64') # [[One before L,two before L],[[One before R,two before R]


def init():
    """Buffer initialization"""
    data_buff, mod_buff = np.array([[0.0, 0.0], [0.0, 0.0]]), np.array([[0.0, 0.0], [0.0, 0.0]], dtype = 'float64')


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
    try:
        # fromiter()より10^6倍アクセスが早い
        data_chunk = np.frombuffer(data_chunk, dtype="int16") / 32768.0 # Normalize -1~1
    except AttributeError:
        return -1
    if(channel_number == 2): #STEREO
        _unpack_data = np.array([data_chunk[::2], data_chunk[1::2]])
        _data_size = _unpack_data.shape[1]
    elif(channel_number == 1): #MONO
        _unpack_data = np.array(data_chunk)
        _data_size = _unpack_data.size
    else:
        _unpack_data = -1
        print("The number of channel is incorrect.")
    return _unpack_data, _data_size


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
            _pack_data[::2], _pack_data[1::2] = data[0], data[1]
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


def limmiter(data):
    """ Limmiter(-1 ~ 1) normalizing.
        Parameters
        ----------
        _data    : bytes\n
    """
    LIMMIT = 1.0
    data[data<-LIMMIT] = -LIMMIT
    data[data>LIMMIT] = LIMMIT
    return data


def exciter(data):
    """ Limmiter(-1 ~ 1) normalizing.
        Parameters
        ----------
        _data    : bytes\n
    """
    data = np.where(data<-0.08, data*0.7, data)
    data = np.where(data>0.08, data*0.7, data)
    return data


def iir_vec(data, coeff, ch_number:int=0):
    if (ch_number == 2):
        coef_comb_l_vec= np.vectorize(coef_comb_l)
        coef_comb_r_vec= np.vectorize(coef_comb_r)
        data[0] = coef_comb_l_vec(data[0], coeff[1][0], coeff[1][1], coeff[1][2], coeff[0][1], coeff[1][2])
        data[1] = coef_comb_r_vec(data[1], coeff[1][0], coeff[1][1], coeff[1][2], coeff[0][1], coeff[1][2])
    elif (ch_number == 1):
        coef_comb_vec = np.vectorize(coef_comb_l)
        data = coef_comb_vec(data, coeff)
    return data


def coef_comb_l(sample, coeff1, coeff2, coeff3, coeff4, coeff5):
    _comb = coeff1 * sample + coeff2 * data_buff[0][0] + coeff3 * data_buff[0][1] - coeff4 * mod_buff[0][0] - coeff5 * mod_buff[0][1]
    data_buff[0][1],mod_buff[0][1] = data_buff[0][0], mod_buff[0][0]
    data_buff[0][0],mod_buff[0][0] = sample, _comb
    return _comb


def coef_comb_r(sample, coeff1, coeff2, coeff3, coeff4, coeff5):
    _comb = coeff1 * sample + coeff2 * data_buff[1][0] + coeff3 * data_buff[1][1] - coeff4 * mod_buff[1][0] - coeff5 * mod_buff[1][1]
    data_buff[1][1], mod_buff[1][1] = data_buff[1][0], mod_buff[1][0]
    data_buff[1][0], mod_buff[1][0] = sample, _comb
    return _comb


def delay(_data):
    pass

def iir(data, data_size:int, coeff, ch_number:int=0):
    _moddata= np.empty_like(data)
    if (ch_number == 2):
        _mod_buff_l_1, _data_buff_l_1, _mod_buff_l_2, _data_buff_l_2 = mod_buff[0][0], data_buff[0][0], mod_buff[0][1], data_buff[0][1]
        _mod_buff_r_1, _data_buff_r_1, _mod_buff_r_2, _data_buff_r_2 = mod_buff[1][0], data_buff[1][0], mod_buff[1][1], data_buff[1][1]
        for i in range(data_size):
            _moddata[0][i] = coeff[1][0] * data[0][i] + coeff[1][1] * _data_buff_l_1 + coeff[1][2] * _data_buff_l_2 - coeff[0][1] * _mod_buff_l_1 - coeff[0][2] * _mod_buff_l_2
            _moddata[1][i] = coeff[1][0] * data[1][i] + coeff[1][1] * _data_buff_r_1 + coeff[1][2] * _data_buff_r_2 - coeff[0][1] * _mod_buff_r_1 - coeff[0][2] * _mod_buff_r_2
            _data_buff_l_2, _data_buff_r_2, _data_buff_l_1, _data_buff_r_1  = _data_buff_l_1, _data_buff_r_1, data[0][i], data[1][i]
            _mod_buff_l_2, _mod_buff_r_2, _mod_buff_l_1, _mod_buff_r_1 = _mod_buff_l_1, _mod_buff_r_1, _moddata[0][i], _moddata[1][i]
        mod_buff[0][0], data_buff[0][0], mod_buff[0][1], data_buff[0][0] = _mod_buff_l_1, _data_buff_l_1, _mod_buff_l_2, _data_buff_l_2
        mod_buff[1][0], data_buff[1][0], mod_buff[1][1], data_buff[1][1] = _mod_buff_r_1, _data_buff_r_1, _mod_buff_r_2, _data_buff_r_2
    elif (ch_number == 1):
        for i in range(data_size):
            _moddata[i] = coeff[1][0] * data[i] + coeff[1][1] * data_buff[0][0] + coeff[1][2] \
                        * data_buff[0][1] - coeff[0][1] * mod_buff[0][0] - coeff[0][2] * mod_buff[0][1]
            data_buff[0][1], data_buff[0][0], mod_buff[0][1], mod_buff[0][0] = data_buff[0][0], _moddata[i], mod_buff[0][0], _moddata[i]
    return _moddata


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
        data, data_size = unpack_chunk(data_chunk, CHUNK, ch_num)

        ### Entry original function#####
        moddata = np.empty_like(data, dtype='float64')
        moddata = data
        ###iir #
        # moddata = iir(data, data_size, biQuad(f_rate).bq_lowpass(600, 0.7892), ch_num)
        # moddata = iir_vec(data, biQuad(f_rate).bq_lowpass(600, 0.7892), ch_num)
        ###Gain make up(-6dB) #
        # moddata = moddata*0.5
        ###Limitter(-1 ~ 1) #
        # moddata = exciter(data)
        moddata = limmiter(moddata)
        ################################
        ###unpack chunk #
        data_chunk = pack_data(moddata, data_size, ch_num)
        stream.write(data_chunk)
        data_chunk = wf.readframes(CHUNK)
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == '__main__':

    wavfile="wav/sample.wav"
    CHUNK = 1024
    # 処理が間に合わないようなら
    # CHUNK = CHUNK*2
    real_time_prosess(wavfile, CHUNK)