# -*- coding: utf-8 -*-
"""
IIR filter class created based on AudioCook Book.
http://www.musicdsp.org/files/Audio-EQ-Cookbook.txt
"""
import matplotlib.pyplot as plt
import numpy as np

__author__ = "Hitoki Yamada"
__status__ = "Prototype"
__version__ = "0.0.1"
__date__ = "2018.1.11"

class biQuad(object):
    """IIR filter class created based on AudioCook Book.\n
    Please see below for more information.\n
    http://www.musicdsp.org/files/Audio-EQ-Cookbook.txt.

    Parameters
    ----------
    srate : int
    Sampling rate.
    """
    srate = 48000

    def __init__(self, srate=48000):
        self.set_bq_srate(srate)

    def set_bq_srate(self, srate):
        """Initialize Sampling rate.

        Parameters
        ----------

        srate : int
        Sampling rate.
        """
        self.srate = srate
        #self.freq_range = np.asarray(range(0, int(self.srate/2), 5), dtype=np.float64)　#linear
        self.freq_range = 2*np.logspace(1, 4, int(srate/8), dtype=np.float64)

    @classmethod
    def bq_convert_csv(cls, gain, phase, csv_name=None):
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
            csv_name_gain = gain + '.csv'
            csv_name_phase = phase + '.csv'
        else:
            csv_name_gain = csv_name + '_' + gain + '.csv'
            csv_name_phase = csv_name + '_' +phase + '.csv'

        np.savetxt(csv_name_gain, gain, delimiter=',')
        np.savetxt(csv_name_phase, phase, delimiter=',')

    def bq_lowpass(self, f0, q):
        """Returns the normalized coeff at a0.\n
        H(s) = 1 / (s^2 + s/Q + 1)

        Parameters
        ----------

        f0 : int
        Center frequency.
        q  : int
        Quality factor.

        """
        w0 = self._angular(f0)
        alpha = self._alpha(w0, q, 'q')

        a0 = 1 + alpha
        a1 = -2 * np.cos(w0)
        a2 = 1 - alpha
        b0 = (1 - np.cos(w0))/2
        b1 = 1 - np.cos(w0)
        b2 = b0 # (1 - np.cos(w0))/2
        norm_coeff = [[0, a1/a0, a2/a0], [b0/a0, b1/a0, b2/a0]]
        return norm_coeff

    def bq_highpass(self, f0, q):
        """Returns the normalized coeff at a0.\n
        H(s) = s^2 / (s^2 + s/Q + 1)

        Parameters
        ----------

        f0 : int
        Center frequency.
        q : int
        Quality factor.

        """
        w0 = self._angular(f0)
        alpha = self._alpha(w0, q, 'q')

        a0 = 1 + alpha
        a1 = -2 * np.cos(w0)
        a2 = 1 - alpha
        b0 = (1 + np.cos(w0))/2
        b1 = -(1 + np.cos(w0))
        b2 = b0 # (1 + np.cos(w0))/2
        norm_coeff = [[0, a1/a0, a2/a0], [b0/a0, b1/a0, b2/a0]]
        return norm_coeff

    def bq_bandpass(self, f0, factor, factor_type='q', peakGainType='skirt'):
        """Returns the normalized coeff at a0.\n
        H(s) = s / (s^2 + s/Q + 1) (constant skirt gain, peak gain = Q)\n
        H(s) = (s/Q) / (s^2 + s/Q + 1) (constant 0 dB peak gain)

        Parameters
        ----------

        f0 : int
        factor : int
        factor value.
        factor_type : str
        'q' = factor_type QualityFactor\n
        'bw'= band width
        peakGainType : str
        'skirt' = constant skirt gain, peak gain = Q\n
        '0peak' = constant 0 dB peak gain

        """
        w0 = self._angular(f0)
        alpha = self._alpha(w0, factor, atype=factor_type)

        if peakGainType == 'skirt':
            if factor_type == 'bw':
                return print('Peak gain type \'skirt\' does not allow factor_type =  \'bw.\'')
            q = factor
            a0 = 1 + alpha
            a1 = -2 * np.cos(w0)
            a2 = 1 - alpha
            b0 = q * alpha
            b1 = 0
            b2 = - 1 * q * alpha
        elif peakGainType == '0peak':
            a0 = 1 + alpha
            a1 = -2 * np.cos(w0)
            a2 = 1 - alpha
            b0 = alpha
            b1 = 0
            b2 = -1 * alpha
        else:
            print('peakGainType is incorrect.alpha type is q or 0.')

        norm_coeff = [[0, a1/a0, a2/a0], [b0/a0, b1/a0, b2/a0]]
        return norm_coeff

    def bq_notch(self, f0, factor, factor_type='q'):
        """Returns the normalized coeff at a0.\n
        H(s) = (s^2 + 1) / (s^2 + s/Q + 1)

        Parameters
        ----------

        f0 : int
        factor : int
        factor value.
        factor_type : str
        'q' = factor_type QualityFactor\n
        'bw'= band width

        """
        w0 = self._angular(f0)
        alpha = self._alpha(w0, factor, atype=factor_type)

        a0 = 1 + alpha
        a1 = (-2 * np.cos(w0)) / a0
        a2 = (1 - alpha) / a0
        b0 = 1 / a0
        b1 = (-2 * np.cos(w0)) /a0
        b2 = b0 # b2 = 1
        norm_coeff = [[0, a1/a0, a2/a0], [b0/a0, b1/a0, b2/a0]]
        return norm_coeff

    def bq_allpass(self, f0, q):
        """Returns the normalized coeff at a0.\n
        H(s) = (s^2 - s/Q + 1) / (s^2 + s/Q + 1)

        Parameters
        ----------

        f0 : int
        Center frequency.
        q : int
        Quality factor.

        """
        w0 = self._angular(f0)
        alpha = self._alpha(w0, q, 'q')

        a0 = 1 + alpha
        a1 = -2 * np.cos(w0)
        a2 = 1 - alpha
        b0 = 1 - alpha
        b1 = -2 * np.cos(w0)
        b2 = 1 + alpha
        norm_coeff = [[0, a1/a0, a2/a0], [b0/a0, b1/a0, b2/a0]]
        return norm_coeff

    def bq_peakingeq(self, f0, q, gain):
        """Returns the normalized coeff at a0.\n
        H(s) = (s^2 - s/Q + 1) / (s^2 + s/Q + 1)

        Parameters
        ----------

        f0 : int
        Center frequency.
        q : int
        Quality factor.
        gain : int
        Peak gain.

        """

        w0 = self._angular(f0)
        alpha = self._alpha(w0, q, 'q')
        a = 10**(gain/40)

        a0 = 1 + alpha / a
        a1 = -2 * np.cos(w0)
        a2 = 1 - alpha / a
        b0 = 1 + alpha * a
        b1 = -2 * np.cos(w0)
        b2 = 1 - alpha * a

        norm_coeff = [[0, a1/a0, a2/a0], [b0/a0, b1/a0, b2/a0]]
        return norm_coeff

    def bq_lowshelf(self, f0, factor, gain, factor_type='q'):
        """Returns the normalized coeff at a0.\n
        H(s) = A * (s^2 + (sqrt(A)/Q)*s + A)/(A*s^2 + (sqrt(A)/Q)*s + 1)

        Parameters
        ----------

        f0 : int
        Center frequency.
        factor : int
        factor value.
        gain : int
        Peak gain.
        factor_type : str
        'q'= factor_type QualityFactor.\n
        's'= factor_type slope.

        """
        w0 = self._angular(f0)
        alpha = self._alpha(w0, factor, atype=factor_type)
        a = 10**(gain/40)

        a0 = (a+1) + (a-1) * np.cos(w0) + 2*np.sqrt(a) * alpha
        a1 = -2*((a-1) + (a+1) * np.cos(w0))
        a2 = (a+1)+(a-1) * np.cos(w0) -2*np.sqrt(a) * alpha
        b0 = a*((a+1) - (a-1) * np.cos(w0) + 2*np.sqrt(a) * alpha)
        b1 = 2*a*((a-1) - (a+1) * np.cos(w0))
        b2 = a*((a+1) - (a-1) * np.cos(w0) - 2*np.sqrt(a)*alpha)

        norm_coeff = [[0, a1/a0, a2/a0], [b0/a0, b1/a0, b2/a0]]
        return norm_coeff

    def bq_highshelf(self, f0, factor, gain, factor_type='q'):
        """Returns the normalized coeff at a0.\n
        H(s) = A * (A*s^2 + (sqrt(A)/Q)*s + 1)/(s^2 + (sqrt(A)/Q)*s + A)

        Parameters
        ----------

        f0 : int
        Center frequency.
        factor : int
        factor value.
        gain : int
        Peak gain.
        factor_type : str
        'q'= factor_type QualityFactor.\n
        's'= factor_type slope.

        """
        w0 = self._angular(f0)
        alpha = self._alpha(w0, factor, atype=factor_type)
        a = 10**(gain/40)

        a0 = (a+1) - (a-1) * np.cos(w0) + 2*np.sqrt(a)*alpha
        a1 = 2*((a-1) - (a+1) * np.cos(w0))
        a2 = (a+1) - (a-1) * np.cos(w0) - 2*np.sqrt(a)*alpha
        b0 = a * ((a+1) + (a-1) * np.cos(w0) + 2*np.sqrt(a) * alpha)
        b1 = -2 * a *((a-1) + (a+1) * np.cos(w0))
        b2 = a* ((a+1) + (a-1) * np.cos(w0) - 2*np.sqrt(a) * alpha)

        norm_coeff = [[0, a1/a0, a2/a0], [b0/a0, b1/a0, b2/a0]]
        return norm_coeff

    def _angular(self, freq):
        """2pi f0 / Fs

        Parameters
        ----------

        freq : Target Hz.
        """
        # 角速度算出
        ang = (2*np.pi*freq)/self.srate
        return ang

    @classmethod
    def _alpha(cls, w0, factor, atype='q', gain=None):
        """Calculate alpha.

        Parameters
        ----------

        w0 : int
        The angular frequency
        factor : int
        factor coeff value.
        atype : str
        alpha type.\n
        q = sin(w0)/(2*Q) (with Q)\n
        bw = sin(w0)*sinh(ln(2)/2 * BW * w0/sin(w0)) (with BW)\n
        s = sin(w0)/2 * sqrt( (A + 1/A)*(1/S - 1) + 2 ) (with S)\n
        gain : int
        Setting for peaking and shelving EQ.\n

        """
        if atype == 'q':
            q = factor
            alpha = np.sin(w0)/(2*q)
        elif atype == 'bw':
            bw = factor
            alpha = np.sin(w0) * np.sinh(np.log(2) / 2 * bw * w0/np.sin(w0))
        elif atype == 's':
            s = factor
            a = 10**(gain/40)
            alpha = np.sin(w0) / 2 * np.sqrt((a+1/a) * (1/s-1) + 2)
            pass
        else:
            print('atype is incorrect.alpha type is q or bw or s.')
        return alpha

    def _bq_cal_coeff(self, coeff_lst):
        """The argument must be normalized with "a0".\n
        Multiple arguments can be given at the same time.

        Parameters
        ----------

        coeff_lst : list
        Direct Form1 coefficient.\n
        The argument must be normalized with "a0".\n
        Multiple arguments can be given at the same time.

        """
        accum_real = np.asarray([1] * len(self.freq_range), dtype=np.float64)
        accum_imag = np.asarray([0] * len(self.freq_range), dtype=np.float64)

        multi_flag = True
        for coeff in coeff_lst:
            # Check number of filter coeff.
            if np.ndim(coeff_lst) <= 2:
                multi_flag = False
                coeff = coeff_lst

            i = 0
            for w in self.freq_range:
                ang = self._angular(w)
                a = coeff[1][0]+coeff[1][1]*np.cos(ang)+coeff[1][2]*np.cos(2*ang)
                b = -1*coeff[1][1]*np.sin(ang)-coeff[1][2]*np.sin(2*ang)
                c = 1+coeff[0][1]*np.cos(ang)+coeff[0][2]*np.cos(2*ang)
                d = -1*coeff[0][1]*np.sin(ang)-coeff[0][2]*np.sin(2*ang)

                real = (a*c+b*d)/(c**2+d**2)
                imag = (b*c-a*d)/(c**2+d**2)
                # The cumulative value immediately before.
                realZ1 = accum_real[i]
                imagZ1 = accum_imag[i]

                # Update accumvalue.
                accum_real[i] = real*realZ1-imag*imagZ1
                accum_imag[i] = real*imagZ1+imag*realZ1
                i = i + 1

            if multi_flag is False:
                return accum_real, accum_imag

        return accum_real, accum_imag

    def bq_trans_fresponse(self, coeff_lst):
        """Calculate Gain and Phase of each frequency and return.\n
        The argument must be normalized with "a0".\n
        Multiple arguments can be given at the same time.

        Parameters
        ----------

        coeff_lst : list
        Direct Form1 coefficient.\n
        The argument must be normalized with "a0".\n
        Multiple arguments can be given at the same time.

        """
        # Calculation filter coefficient
        accum_real, accum_imag = self._bq_cal_coeff(coeff_lst)
        #Calculate phase and Gain
        gain = np.asarray([0] * len(self.freq_range), dtype=np.float64)
        phase = np.asarray([0] * len(self.freq_range), dtype=np.float64)
        for i in range(len(self.freq_range)):
        # Calculate gain.
            if accum_real[i] + accum_imag[i] == 0:
                gain[i] = 0
            else:
                gain[i] = 20 * np.log10(np.sqrt(accum_real[i]**2 + accum_imag[i]**2))
        # Calculate Phase
            if accum_imag[i] == 0:
                p = 0
            else:
                p = np.rad2deg(np.arctan(accum_imag[i]/accum_real[i]))
            if accum_real[i] < 0 and accum_imag[i] > 0:
                phase[i] = p + 180
            elif accum_real[i] < 0 and accum_imag[i] < 0:
                phase[i] = p - 180
            else:
                phase[i] = p
        return gain, phase

    def bq_fresponse_plot(self, coeff_lst):
        """Generate Gain and Phase plots from given coefficients.\n
        The argument must be normalized with "a0".\n
        Multiple arguments can be given at the same time.

        Parameters
        ----------

        coeff_lst : list
        Direct Form1 coefficient.\n
        The argument must be normalized with "a0".\n
        Multiple arguments can be given at the same time.

        """
        phaseyticks = [-360, -270, -180, -120, -90, -60, 0, 60, 90, 120, 180, 270, 360]
        freqxtick = [10, 50, 100, 300, 500, 1000, 5000, 10000, 20000]
        freqxticklabel = [10, 50, 100, 300, 500, '1k', '5k', '10k', '20k']

        gain, phase = self.bq_trans_fresponse(coeff_lst)

        #Make Gain plot
        plt.figure(figsize=(8, 7))
        plt.subplot(2, 1, 1)
        plt.title('Gain')
        plt.plot(self.freq_range, gain)
        plt.xscale('log')
        plt.xticks(freqxtick, freqxticklabel)
        plt.xlim([0, 24000])
        plt.ylim([-60, 20])
        plt.grid(which='both', color='c', linestyle=':')

        #Make Phase plot
        plt.subplot(2, 1, 2)
        plt.title('Phase')
        plt.plot(self.freq_range, phase, 'r')
        plt.xscale('log')
        plt.yticks(phaseyticks, phaseyticks)
        plt.xticks(freqxtick, freqxticklabel)
        plt.xlim([0, 24000])
        plt.ylim([-360, 360])
        plt.grid(which='both', color='m', linestyle=':')
        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    plt1 = biQuad(48000)
    lps = plt1.bq_lowpass(600, 0.7892)
    print(lps)
    plt1.bq_fresponse_plot(lps)
