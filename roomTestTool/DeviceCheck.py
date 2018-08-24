import pyaudio
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
  dev = p.get_device_info_by_index(i)
  name = (dev['name']).decode('cp932', 'replace') if type(dev['name']) is bytes else (dev['name'])
  print((i,name, dev['maxInputChannels']))
print (input("########################################"))