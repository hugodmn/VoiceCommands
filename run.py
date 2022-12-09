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


torch.cuda.empty_cache()

device = 'cpu'
#WHISPER model settings:
model = whisper.load_model("base.en")
LANGUAGE = "English"

#import GOSAI commands
GOSAIcommands = Commands()
#import Vocal feedbacks
VocalReturn = VocalFeedback()
modefeedback = []
#import WUW inference
WUWinf = CNNInference()

#Stream settings
CHANNEL=1
FORMAT=pyaudio.paFloat32
SAMPLE_RATE=44100
RUN=True
STTRun = False
#duration of wake up word audio (sec)
WUWSECONDS=2
#duration of speech to text audio (sec)
STTSECONDS=4


SLIDING_WINDOW=1/6
Numberofsttwindows = 3
CHUNK = int(SLIDING_WINDOW*SAMPLE_RATE*WUWSECONDS)  #equivalent to 20ms

WUWfeed_samples=SAMPLE_RATE*WUWSECONDS   
STTfeed_samples=SAMPLE_RATE*STTSECONDS

silence_threshold = 0.05


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

wuwq = Queue()
sttq = Queue()

fulltranscription = []

def callback(in_data:np.array, frame_count, time_info, flag)->Tuple[np.array,pyaudio.PyAudio]:
    global data, RUN, wuwq, sttq, STTRun 

        
    data0 = np.frombuffer(in_data, dtype=np.float32)
    data = np.append(data,data0)  
    
    if STTRun == True:
        print("STT")
        if len(data) > STTfeed_samples:
            data = data[-STTfeed_samples:]
            print("before queue : ",len(data))
            sttq.put(data)
            print("STTqueue : ",sttq.qsize())
            data = data[-STTfeed_samples//2:]



    else : 
        if len(data) > WUWfeed_samples:
            data = data[-WUWfeed_samples:]
        
            wuwq.put(data)
            print("WUWqueue : ",wuwq.qsize())

    return (in_data, pyaudio.paContinue)


def main()->None:
    global RUN, STTRun
    
    inference=CNNInference()
    
    # Run the demo for a timeout seconds
    timeout = time.time() + 1 #1sec


    # Data buffer for the input wavform
   
    stream = get_audio_input_stream(callback)
  
    try:
        while RUN:
            datarecup = wuwq.get()
            print("dB -> ",np.abs(datarecup).mean())
            if np.abs(datarecup).mean()>silence_threshold:
           
                new_trigger = inference.get_prediction(torch.tensor(datarecup))
                
                if new_trigger==1:

                    print('not activated')




                if new_trigger== 0:
                    print("************** activate **************")
                    STTRun = True
                    
                    nbtranscription = 0
                    
                    starttest = time.time()
                #process to recuperation of 6 sec audio from the queue 
                    # for j in range(Numberofsttwindows+1):
                 
                    #     for i in range(int(1/SLIDING_WINDOW)):
                    while nbtranscription < 2 :
                        if not sttq.empty():
                            
                            STTdatarecup = sttq.get() 
                                              
                        
                            STTdatarecup = librosa.resample(STTdatarecup, orig_sr = 44100, target_sr=16000)
                            
                            

                    
                            if len(STTdatarecup) >= STTSECONDS*16000: 
                                result = model.transcribe(STTdatarecup, language=LANGUAGE)
                                STTresult = result["text"]
                                fulltranscription.append(STTresult)

                                print("transcription : ",STTresult)
                                GOSAIcommands.comparaison(STTresult)
                                print(GOSAIcommands.modeactive)
                                if GOSAIcommands.modeactive != None :
                                    modefeedback.append(GOSAIcommands.modeactive)
                                    
                                    GOSAIcommands.modeactive = None
                                nbtranscription += 1
                                
                    STTRun = False
                    for k in modefeedback:
                        VocalReturn.speak(k)
                    print("time : ",time.time()-starttest)

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
