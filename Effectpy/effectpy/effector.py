# -*- coding: utf-8 -*-
"""
effector is an audio library based on matplotlib,soundfile and NumPy. 
"""
import os.path
import numpy as np
import soundfile as sf

__author__ = "Hitoki Yamada"
__status__ = "Prototype"
__version__ = "0.0.1"
__date__ = "2018.1.11"

class effector(object):
    """Process audio signals. \n
    Read wav data, convert it to a numerical value and copy to signal processing buffer.
    Also returns its value.

    Parameters
    ----------
    wavpass : str
    Directory path of the sound file to be processed.
    """
    tmp_data = np.empty(1)
    file_name = ''
    stereo_flag = False

    def __init__(self, wavpass):
        self.load_wav(wavpass)

    def clear_wav_tmp(self):
        """Initialize audio signal temp buffer."""
        self.tmp_data = np.empty(1)

    def convert_csv(self, csv_name=None, data=tmp_data):
        """Debugging functions.\n
           Output value of list as CSV.
        Parameters
        ----------
        csv_name : str
        output csv file name.
        data : list
        If data is not passed, it output the temp buffer as CSV.
        """
        if csv_name is None:
            csv_name = os.path.splitext(self.file_name)[0] + '.csv'
        else:
            csv_name = os.path.splitext(csv_name)
            csv_name = os.path.split(self.file_name)[0] + '/' + csv_name[0] + '.csv'

        np.savetxt(csv_name, data, delimiter=',')

    def _check_use_tmp(self, data):
        if data is None:
            return self.tmp_data
        else:
            print("use argument data.")
            return data

    def load_wav(self, wavpass):
        """Read wav data, convert it to a numerical value and copy to signal processing buffer.
           Also returns its value.

           Parameters
           ----------
           wavpass : str
           Directory path of the sound file to be processed.
        """
        self.clear_wav_tmp()
        self.file_name = '' + wavpass
        self.tmp_data, self.wav_srate = sf.read(wavpass)
        if np.ndim(self.tmp_data) > 1:
            self.stereo_flag = True
            print("[Stereo mode]")
        else:
            self.stereo_flag = False
            print("[Mono mode]")
        print(sf.info(wavpass))
        return self.tmp_data

    def gen_wav(self, output_name=None, data=None):
        """Output the given element in wav format.

           Parameters
           ----------
           output_name : str
           data : list
           If data is not passed, it output the temp buffer as WAV.
           Only one dimension or two dimensional columns are permitted.
        """
        data = self._check_use_tmp(data)

        if output_name is None:
            fname_mod = os.path.splitext(self.file_name)[0] + '_mod.wav'
        else:
            output_name = os.path.splitext(output_name)
            fname_mod = os.path.split(self.file_name)[0] + '/' + output_name[0] + '.wav'
        # check arg index.
        try:
            sf.write(fname_mod, data, self.wav_srate)
        except IndexError:
            print("The data frame is incorrect.")
            return print("Arg data length:", len(data))

        print("generate complete!")

    def bqf(self, coeff_lst, data=None):
        """Processing with IIR of Direct Form 1 based on the given coefficient.

           Parameters
           ----------
           coeff_lst : list
           The list must be in the following format.\n
           = [[a0, a1, a2], [b0, b1, b2]]\n
           However, it is also possible to give multiple coefficient blobs.\n
           <Example> \n
           = ([[a0, a1, a2], [b0, b1, b2]],[[a0, a1, a2], [b0, b1, b2]])
           data : list
           If data is not passed, it output the temp buffer as WAV.
           Only one dimension or two dimensional columns are permitted.
        """
        data = self._check_use_tmp(data)

        multi_flag = True
        # Check number of filter coeff.
        if np.ndim(coeff_lst) <= 2:
            multi_flag = False
        # Perform processing as many times as Filter.
        for coeff in coeff_lst:
            if multi_flag is False:
                coeff = coeff_lst

        # Wav format check
        # Stereo
            if self.stereo_flag is True:
                new_tmp_l = np.asarray([0] * len(data), dtype=np.float64)
                new_tmp_r = np.asarray([0] * len(data), dtype=np.float64)
                for i in range(len(data)):
                    new_tmp_l[i] = coeff[1][0] * data[i][0] + coeff[1][1] * data[i-1][0] + coeff[1][2] \
                                * data[i-2][0] - coeff[0][1] * new_tmp_l[i-1] -  coeff[0][2] * new_tmp_l[i-2]

                    new_tmp_r[i] = coeff[1][0] * data[i][1] + coeff[1][1] * data[i-1][1] + coeff[1][2] \
                                * data[i-2][1] - coeff[0][1] * new_tmp_r[i-1] -  coeff[0][2] * new_tmp_r[i-2]

                data[:, 0] = new_tmp_l
                data[:, 1] = new_tmp_r
                self.tmp_data = data
        # Mono
            else:
                new_tmp = np.asarray([0] * len(data), dtype=np.float64)
                for i in range(len(data)):
                    new_tmp[i] = coeff[1][0] * data[i] + coeff[1][1] * data[i-1] + coeff[1][2] \
                                * data[i-2] - coeff[0][1] * new_tmp[i-1] -  coeff[0][2] * new_tmp[i-2]
                # if multi_flag is True:
                data = new_tmp
                self.tmp_data = data
            if multi_flag is False:
                return data

    def delay(self, attenuation_rate, delay_time, repeat, data=None):
        """Simple Delay processing.

           Parameters
           ----------
           attenuation_rate : int
           Decay rate of Delay
           1 ~ 0.**
           delay_time : int
           repeat : int
           data :list
           If data is not passed, it output the temp buffer as WAV.
           Only one dimension or two dimensional columns are permitted.
        """
        data = self._check_use_tmp(data)

        length = len(data)
        # Stereo
        if self.stereo_flag is True:
            new_tmp_l = np.empty(length)
            new_tmp_r = np.empty(length)
            for n in range(length):
                new_tmp_l[n] = data[n][0]
                new_tmp_r[n] = data[n][1]
                # Add effect
                for i in range(1, repeat + 1):
                    d = int(n - i * delay_time)
                    if d >= 0:
                        new_tmp_l[n] += (attenuation_rate ** i) * data[d][0]
                        new_tmp_r[n] += (attenuation_rate ** i) * data[d][1]
            data[:, 0] = new_tmp_l
            data[:, 1] = new_tmp_r
            self.tmp_data = data
            return data

        # Mono
        else:
            new_tmp = np.empty(length)
            for n in range(length):
                new_tmp[n] = data[n]
                # Add effect
                for i in range(1, repeat + 1):
                    d = int(n - i * delay_time)
                    if d >= 0:
                        new_tmp[n] += (attenuation_rate ** i) * data[d]
            data = new_tmp
            self.tmp_data = data
            return data

    def reverb(self, attenuation_rate, repeat, data=None):
        """Simple Reverb processing.

           Parameters
           ----------
           attenuation_rate : int
           Decay rate of Delay
           1 ~ 0.**
           repeat : int
           data :list
           If data is not passed, it output the temp buffer as WAV.
           Only one dimension or two dimensional columns are permitted.
        """
        data = self._check_use_tmp(data)

        length = len(data)
        #Stereo
        if self.stereo_flag is True:
            for r in range(1000, 3000, 500):
                new_tmp_l = np.empty(length)
                new_tmp_r = np.empty(length)
                for n in range(length):
                    new_tmp_l[n] = data[n][0]
                    new_tmp_r[n] = data[n][1]
                    # 元のデータに残響を加える
                    for i in range(1, repeat + 1):
                        d = int(n - i * r)
                        if d >= 0:
                            new_tmp_l[n] += (attenuation_rate ** i) * data[d][0]
                            new_tmp_r[n] += (attenuation_rate ** i) * data[d][1]
            data[:, 0] = new_tmp_l
            data[:, 1] = new_tmp_r
            self.tmp_data = data
            return data

        #Mono
        else:
            for r in range(1000, 3000, 500):
                new_tmp = np.empty(length)
                for n in range(length):
                    new_tmp[n] = data[n]
                    # 元のデータに残響を加える
                    for i in range(1, repeat + 1):
                        d = int(n - i * r)
                        if d >= 0:
                            new_tmp[n] += (attenuation_rate ** i) * data[d]
            data = new_tmp
            self.tmp_data = data
            return data

    def fir(self, fir_coeff, data=None):
        """Simple FIR processing.

           Parameters
           ----------
           fir_coeff : list
           The list must be in the following format.
           [[a0, a1, a2], [b0, b1, b2]]
           data :list
           If data is not passed, it output the temp buffer as WAV.
           Only one-dimensional arrays are allowed.
        """
        data = self._check_use_tmp(data)
        new_tmp_data = data
        buffer = np.array([])
        for i in range(len(new_tmp_data)):
            s = 0
            for j in range(len(fir_coeff)):
                s += new_tmp_data[i - j] * fir_coeff[j]
            np.append(buffer, s)

        data = buffer
        self.tmp_data = data
        return data

