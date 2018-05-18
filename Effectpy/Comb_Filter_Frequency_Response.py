#-------------------------------------------------------------------------------
# module_Name:Comb Filter Frequency Response
# Author: m_tsutsui
#-------------------------------------------------------------------------------

#Library_Import#############################
from numpy import*

import math, numpy as np
import matplotlib.pyplot as plt
#Library_Import_end##########################


def Hf(g):  #linear_model
    H_o=1/sqrt(g**2-2*g*cos(omega*M*T)+1)
    return  array(H_o)

def Hf_log(g):   #logarithm_model
    H_o_log=1/sqrt(g**2-2*g*cos(omega_log*M*T)+1)
    return  array(H_o_log)



if __name__ == '__main__':

    D_size=600     #Data_size

    M=10  #Memory_number

    f_min=200   #freq_min
    f_max=20000 #freq_max

    f=linspace(f_min,f_max,D_size)  #freq_vector

    omega=2*pi*f     #angular_freq
    fs=48*10**3      #sampling_freq
    T=1/fs           #sampling_interval


    f_log=2*np.logspace(2,4,D_size)     #freq_vector_logmodel
    omega_log=2*pi*f_log        #angular_freq_logmodel

    plt.figure(facecolor='w')

    plt.subplot(121)
    plt.plot(f,20*log10(Hf(0.5)))
    plt.plot(f,20*log10(Hf(0.6)))
    plt.plot(f,20*log10(Hf(0.7)))
    plt.plot(f,20*log10(Hf(0.8)))
    plt.grid()
    plt.xlabel('freq[Hz]',fontsize=15)
    plt.ylabel('Gain[dB]',fontsize=15)
    plt.legend(('g=0.5','g=0.6','g=0.7','g=0.8'))
    plt.title('Comb Filter  Frequency Response')

    plt.subplot(122)
    plt.plot(f,20*log10(Hf_log(0.5)))
    plt.plot(f,20*log10(Hf_log(0.6)))
    plt.plot(f,20*log10(Hf_log(0.7)))
    plt.plot(f,20*log10(Hf_log(0.8)))
    plt.grid()
    plt.xlabel('freq[Hz]',fontsize=15)
    plt.ylabel('Gain[dB]',fontsize=15)
    plt.legend(('g=0.5','g=0.6','g=0.7','g=0.8'))
    plt.title('Comb Filter  Frequency Response (logarithm)')

    plt.show()

