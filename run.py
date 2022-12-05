from typing import Tuple
import numpy as np
import pyaudio
import sys
import time
import torch
from CNN.inference import CNNInference
from Fuzzywuzzy.comparaison import Commands 
from TTS.pytts import VocalFeedback
from queue import Queue
from threading import Thread
import whisper
import librosa


#WHISPER:
model = whisper.load_model("tiny.en")
LANGUAGE = "English"

GOSAIcommands = Commands()
VocalReturn = VocalFeedback()
CHANNEL=1
FORMAT=pyaudio.paFloat32
#duration of wake up word audio 
WUWSECONDS=2
#duration of speech to text audio
STTSECONDS=6

SAMPLE_RATE=44100
SLIDING_WINDOW_SECS=1/6
RUN=True
WUWinf = CNNInference()
device = 'cpu'

Numberofsttwindows = 3
CHUNK = int(SLIDING_WINDOW_SECS*SAMPLE_RATE*WUWSECONDS)  #ici equivalent de 25ms

WUWfeed_samples=SAMPLE_RATE*WUWSECONDS   
STTfeed_samples=SAMPLE_RATE*STTSECONDS

def get_audio_input_stream(callback)->pyaudio.PyAudio:
    stream = pyaudio.PyAudio().open(
        format=FORMAT,
        channels=CHANNEL,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=11,
        stream_callback=callback)
    return stream


data = np.zeros(WUWfeed_samples, dtype=np.float32) 

q = Queue()


def callback(in_data:np.array, frame_count, time_info, flag)->Tuple[np.array,pyaudio.PyAudio]:
    global data, RUN, wuwq

        
    data0 = np.frombuffer(in_data, dtype=np.float32)
    data = np.append(data,data0)  
    
    if len(data) > WUWfeed_samples:
        data = data[-WUWfeed_samples:]
     
        q.put(data)
        print("queue : ",q.qsize())

    return (in_data, pyaudio.paContinue)


def main()->None:
    global RUN
    
    inference=CNNInference()
    
    # Run the demo for a timeout seconds
    timeout = time.time() + 1 #1sec


    # Data buffer for the input wavform
   
    stream = get_audio_input_stream(callback)
    #stream.start_stream()
    try:
        while RUN:
            datarecup = q.get()
           

            new_trigger = inference.get_prediction(torch.tensor(datarecup))
            if new_trigger==1:



                print('not activated')




            if new_trigger== 0:
                print("************** activate **************")
                STTdata = librosa.resample(datarecup, orig_sr = 44100, target_sr=16000)
              

                #process to recuperation of 6 sec audio from the queue 
                for j in range(Numberofsttwindows+1):
                 
                    for i in range(int(1/SLIDING_WINDOW_SECS)):
                      
                        datarecup = q.get()                     
                       
                    datarecup = librosa.resample(datarecup, orig_sr = 44100, target_sr=16000)
                    len(datarecup)
                    STTdata = np.append(STTdata,datarecup)
                

                    if len(STTdata)>=16000*STTSECONDS:
                     
                        STTdata = STTdata[-STTfeed_samples:]
                        result = model.transcribe(STTdata, language=LANGUAGE)
                        STTresult = result["text"]
                        print("transcription : ",STTresult)
                        GOSAIcommands.comparaison(STTresult)
                        print(GOSAIcommands.modeactive)
                        if GOSAIcommands.modeactive != None :
                            VocalReturn.speak(GOSAIcommands.modeactive)
                            GOSAIcommands.modeactive = None

                # for i in range(int(1/SLIDING_WINDOW_SECS)*WUWSECONDS+1):
                #         datarecup = q.get()
                #         print("recup")
                #         if (i%int(1/SLIDING_WINDOW_SECS)==0):                        
                #             STTdata = np.append(STTdata,datarecup)
                #             print("ajout")
                #             print("taille data pour stt : ",len(STTdata))
                #             print(STTdata)
                #      STTdata = STTdata[-STTfeed_samples:]


    except (KeyboardInterrupt, SystemExit):
        stream.stop_stream()
        stream.close()
        RUN = False

    stream.stop_stream()
    stream.close()

main()
