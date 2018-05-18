from effectpy import biQuad, effector
import numpy as np

class modDelay(effector):
    def delay(self, attenuation_rate, delay_time, repeat, coeff_lst, data=None,):
        data = super()._check_use_tmp(data)
        length = len(data)
        # Stereo
        if self.stereo_flag is True:
            new_tmp_l = np.empty(length)
            new_tmp_r = np.empty(length)
            delay_tmp_l = np.empty(length) # DelayのBufferを追加
            delay_tmp_r = np.empty(length)
            for n in range(length):
                new_tmp_l[n] = data[n][0]
                new_tmp_r[n] = data[n][1]
                # Add effect
                for i in range(1, repeat + 1):
                    d = int(n - i * delay_time)
                    if d >= 0:
                        delay_tmp_l += (attenuation_rate ** i) * data[d][0] # Delay成分のみを蓄積
                        delay_tmp_r += (attenuation_rate ** i) * data[d][1]
            # biquad highpassをかける
            delay_tmp_l = super().bqf(coeff_lst, delay_tmp_l)
            delay_tmp_r = super().bqf(coeff_lst, delay_tmp_r)
            # Delay成分を足し込む
            for m in range(length):
                new_tmp_l[m] = data[m] + delay_tmp_l[m]
                new_tmp_r[m] = data[m] + delay_tmp_r[m]

            data[:, 0] = new_tmp_l
            data[:, 1] = new_tmp_r
            self.tmp_data = data
            return data

        # Mono
        else:
            new_tmp = np.empty(length)
            delay_tmp = np.empty(length) # DelayのBufferを追加
            for n in range(length):
                new_tmp[n] = data[n]
                # Add effect
                for i in range(1, repeat + 1):
                    d = int(n - i * delay_time)
                    if d >= 0:
                        delay_tmp[n] += (attenuation_rate ** i) * data[d] # Delay成分のみを蓄積

            # biquad highpassをかける
            delay_tmp = super().bqf(coeff_lst, delay_tmp)
            # Delay成分を足し込む
            for m in range(length):
                new_tmp[m] = data[m] + delay_tmp[m]

            data = new_tmp
            self.tmp_data = data
            return data


if __name__ == '__main__':
    wavfile = 'wav/mono/muisc3_48k_mono.wav'
    attenuation_rate = 0.6
    delay_time = 20000
    repeat = 6
    plt1 = biQuad(srate=48000)
    hpf = plt1.bq_highpass(1200,0.789)
    sig1 = modDelay(wavfile)
    sig1.load_wav
    sig1.delay(attenuation_rate, delay_time, repeat, hpf)
    sig1.gen_wav()