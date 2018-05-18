import numpy as np
from wave_loader import *
import matplotlib.pyplot as plt

fs = 48000.0
d = 1.0 / fs
size = 256

wave1 = wave_load("wav/mono/300_2000Hz_mono.wav")
wave2 = wave_load("wav/mono/white_mono.wav")
dt1 = np.fft.fft(wave1[10000:10000 + size])
dt2 = np.fft.fft(wave2[10000:10000 + size])
frq = np.fft.fftfreq(size,d)
print(len(frq))

plt.subplot(2,1,1)
plt.title("FFT - Guitar A4")
plt.plot(frq,abs(dt1))
plt.axis([0,fs/2,0,max(abs(dt1))])
plt.subplot(2,1,2)
plt.title("FFT - recorder_A4")
plt.plot(frq,abs(dt2))
plt.axis([0,fs/2,0,max(abs(dt2))])

plt.show()