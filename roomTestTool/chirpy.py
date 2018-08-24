# -*- coding: utf-8 -*
import os
import sys
import subprocess
import datetime
from time import sleep
import wave
import pyaudio

DLBEXE = 'dlb_hdmi_tool.exe -i '
CHIRPEXE = 'chirp_response.exe -ref datmos_obj_chirp_lh_ref.wav -dut '
# STREAMPASS = 'roomTestTool\\stream\\'
STREAMPASS = '..\\Test_Materials\\Test_Signals\\datmos_obj_chirp_lh\\mat\\'
RESULTPASS = 'roomTestTool\\result\\'
CHIRPNAME = 'datmos_obj_chirp_lh_'
FORMAT = '.mat'

def res_cmd(cmd,communicate=False):
    """"""
    if (communicate is False):
        return subprocess.Popen(cmd, stdout=subprocess.PIPE,shell=True)
    elif (communicate is True):
        return subprocess.Popen(cmd, stdout=subprocess.PIPE,shell=True).communicate()[0]

def select_position_com(position:str='ltm'):
    return DLBEXE + STREAMPASS + CHIRPNAME + position + FORMAT

def rec(wait_time:int=10, rec_time:int=7, device:int=1, file_name = "output"):
    directry = "roomTestTool\\result\\"
    file_name = file_name + ".wav"
    fmt = pyaudio.paInt16
    ch = 1
    sampling_rate = 48000
    chunk = 2**11
    audio = pyaudio.PyAudio()
    device_index = device #device index
    time_stamp = datetime.datetime.now()
    time_stamp = time_stamp.strftime("%Y_%m_%d_%H_%M_%S_")
    stream = audio.open(format=fmt, channels=ch, rate=sampling_rate, input=True,
                        input_device_index = device_index,
                        frames_per_buffer=chunk)
    sleep(wait_time)
    print("[SEC: Start recording]")
    frames = []
    for i in range(0, int(sampling_rate / chunk * rec_time)):
        data = stream.read(chunk)
        frames.append(data)
    print("End recording......")

    # rec
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save file
    wav = wave.open(directry+time_stamp+file_name, 'wb')
    wav.setnchannels(ch)
    wav.setsampwidth(audio.get_sample_size(fmt))
    wav.setframerate(sampling_rate)
    wav.writeframes(b''.join(frames))
    wav.close()
    print("saved:", time_stamp+file_name, "!")
    return time_stamp+file_name

def imp_out(target_file:str="", adjust:int=10):
    return CHIRPEXE + "..\\" + RESULTPASS + target_file + " -win " + str(adjust) + " -out " + "..\\" + RESULTPASS + "imp_" + target_file

def csv_out(target_file:str="", adjust:int=6):
    return CHIRPEXE + "..\\" + RESULTPASS + target_file + " -win " + str(adjust) + " -to " + "..\\" + RESULTPASS + target_file + ".csv"

def helper(arg):
    if arg in ['-h' ,'--h', '--help', '-help']:
        print("*************************************************************")
        print("Auto Chirp test tool.")
        print("chirpy.exe args[1] args[2] args[3] args[4] or help options")
        print("Arguments below:")
        print("args[1] : rec wait time.(Default 10)")
        print("args[2] : csv window time.(Default 6)")
        print("args[3] : Output file name.")
        print("args[4] : Speaker Position. Select ltm/rtm.")
        print("args[5] : (Option)Interface device index.")
        print("*************************************************************")
        return True
    else:
        return False

args = sys.argv
# args =[False, 10, 6, "same", "rtm"] #dummy
if (helper(args[1]) is False):
    POSITION = args[4]
    if POSITION in ["ltm", "rtm"]:
        os.chdir('..\\')
        print("[SEC: Send Stream]")
        print("** Not used NVIDIA CARDS! The following error is okay. **")
        res_cmd(select_position_com(POSITION))
        if (len(args) >= 6):
            device_index = int(args[5])
        else:
            device_index = 1
        cre_file_name = rec(wait_time=int(args[1]), device=device_index, file_name=args[3]+"_"+POSITION)
        os.chdir('chirp_response')
        # print("[SEC: Generate impulse responce]")
        # res_cmd(imp_out(cre_file_name), True)
        print("[SEC: Create CSV file]")
        res_cmd(csv_out(cre_file_name, adjust=int(args[2])), True)
        print("Saved:",cre_file_name + ".csv !" )
        print("[Done!]")
    else:
        print("Incorrect Speaker option.\nEnd.....")