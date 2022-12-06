from typing import Tuple
import numpy as np
import pyaudio
import sys
import time
import whisper

from queue import Queue
from threading import Thread
import librosa



model = whisper.load_model("base.en")
LANGUAGE = "English"
CHANNEL=1
FORMAT=pyaudio.paFloat32
SECONDS=4
SAMPLE_RATE=44100
SLIDING_WINDOW_SECS=1/2
RUN=True

device = 'cpu'

CHUNK = int(SLIDING_WINDOW_SECS*SAMPLE_RATE*SECONDS)

feed_samples=SAMPLE_RATE*SECONDS

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



# q = Queue()

# def callback(in_data, frame_count, time_info, flag):
# 	global frames
#     data0 = np.frombuffer(in_data , dtype='int16')
# 	np.append(data, in_data)
# 	if len(frames) > chunks_in_time_window:
# 		while len(frames) != chunks_in_time_window:
# 			frames.pop(0)

# 	if len(frames) == chunks_in_time_window:
# 		bytestring =b''.join(frames)
# 		audio_clip = np.frombuffer(bytestring, dtype=np.int16)
# 		path = os.path.join(output_folder,'voice_{:08d}.wav'.format(cnt))
# 		wf = wave.open(path , 'wb')
# 		wf.setnchannels(channels)
# 		wf.setsampwidth(p.get_sample_size(sample_format))
# 		wf.setframerate(fs)
# 		wf.writeframes(bytestring)
# 		wf.close()
#      return (in_data, pyaudio.paContinue)


data = np.zeros(feed_samples, dtype=np.float32) 
q = Queue()

def callback(in_data:np.array, frame_count, time_info, flag)->Tuple[np.array,pyaudio.PyAudio]:
    global data, RUN, q

    silence_threshold = 0.09

    # if time.time() > timeout:
    #     RUN = False        
    data0 = np.frombuffer(in_data, dtype=np.float32)

    if np.abs(data0).mean() < silence_threshold:
        #sys.stdout.write('-')
        print(np.abs(data0).mean())
        print('-')
        #print(inference.get_prediction(torch.tensor(data0)))
        return (in_data, pyaudio.paContinue)
    else:
        #sys.stdout.write('.')
        print(np.abs(data0).mean())
        print('.')
    data = np.append(data,data0)    
    if len(data) > feed_samples:
        data = data[-feed_samples:]
        # Process data async by sending a queue.



        q.put(data)

        print(q.qsize())
    return (in_data, pyaudio.paContinue)



def main()->None:

    
    
    

    global RUN

    #Queue to communiate between the audio callback and main thread
    

    # Run the demo for a timeout seconds
    timeout = time.time() + 1 #1sec


    # Data buffer for the input wavform
   
    stream = get_audio_input_stream(callback)
    #stream.start_stream()
    try:
        while RUN:
            datarecup = q.get()
            #datarecup = (datarecup * 32767).astype(np.int16)
                     
            datarecup = librosa.resample(datarecup, orig_sr = 41000, target_sr=16000)

            #datarecup = (datarecup*32768.0).astype(np.int16)

            result = model.transcribe(datarecup, language=LANGUAGE)
            print(result["text"])

            # print("------------------------------------------------------")
            # print(datarecup.size())
            # print("------------------------------------------------------")
            # print(torch.unsqueeze(datarecup,dim=0).size())
            # print("------------------------------------------------------")
           
            
    except (KeyboardInterrupt, SystemExit):
        stream.stop_stream()
        stream.close()
        RUN = False

    stream.stop_stream()
    stream.close()

main()