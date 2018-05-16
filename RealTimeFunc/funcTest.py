#coding:utf-8
import wave
import pyaudio
import struct
import matplotlib
from pylab import *

def wave_info(wf):
	"""Get wave info"""
	print ("channel:", wf.getnchannels())
	print ("sample width:", wf.getsampwidth())
	print ("sample rate:", wf.getframerate())
	print ("frames:", wf.getnframes())
	print ("paramams:", wf.getparams())
	print ("Track(sec) :", float(wf.getnframes()) / wf.getframerate())

def play_wave(data, fs, bit):
	""""""
	import pyaudio
	p = pyaudio.PyAudio()
	stream = p.open(format=pyaudio.paInt16,
			channels=1,
			rate=int(fs),
			output= True)
	chunk = 1024
	sp = 0  # play start pointer
	buffer = data[sp:sp+chunk]
	while buffer != '':
		stream.write(buffer)
		sp = sp + chunk
		buffer = data[sp:sp+chunk]
	stream.close()
	p.terminate()

def save_wave(data, fs, bit, filename):
	""""""
	wf = wave.open(filename, "w")
	wf.setnchannels(1)
	wf.setsampwidth(bit / 8)
	wf.setframerate(fs)
	wf.writeframes(data)
	wf.close()

if __name__ == "__main__":
	wf = wave.open("wav/sample.wav", "r")
	# wave_info(wf)

	fs = wf.getframerate()      # サンプリング周波数
	length = wf.getnframes()    # 総フレーム数
	data = wf.readframes(length)

	data = frombuffer(data, dtype="int16") / 32768.0  # # normalize
	newdata = [0.0] * length
	for n in range(length):
		newdata[n] = data[n] / 4
    # plot wave
		# subplot(211)
		# plot(data)
		# axis([0, 140000, -1.0, 1.0])
		# subplot(212)
		# plot(newdata)
		# axis([0, 140000, -1.0, 1.0])
		# show()
	print("FunctionComplete!")
    # denormalize
	newdata = [int(x * 32767.0) for x in newdata]
	newdata = struct.pack("h" * len(newdata), *newdata)
	play_wave(newdata, fs, 16)
	# save_wave(newdata, fs, 16, "wav/sample_out.wav")