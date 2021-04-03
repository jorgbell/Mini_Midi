# basic/record0.py Grabacion de un archivo de audio 'q' para terminar
import pyaudio, kbhit, wave
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()

'''
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

for i in range(p.get_device_count()):
    d = p.get_device_info_by_index(i)
    print(i,": ",d["name"],"\n   ",d["defaultLowOutputLatency"], "  ", d["defaultHighOutputLatency"])

exit(0)
'''


wf = wave.open("record.wav", 'wb')
wf.setnchannels(CHANNELS); 
wf.setsampwidth(p.get_sample_size(FORMAT)); 
wf.setframerate(RATE)


#frames = []
numBloque = 0
def callback(in_data, frame_count, time_info, status):
    #print("entro")
    global numBloque
    #global frames
    #print("Callback bloque ",numBloque)
    #bloque = np.frombuffer(in_data,dtype=np.float32)
    #np.append(in_data, bloque)
    wf.writeframes(in_data)
    #frames += in_data
    #bloque = data[ numBloque*CHUNK : numBloque*CHUNK+CHUNK ]
    numBloque += 1
    return (None, pyaudio.paContinue)


stream = p.open(format=FORMAT, 
                channels=CHANNELS,
                rate=RATE, 
                input=True,   # ahora es flujo de entrada
                frames_per_buffer=CHUNK, # tamanio buffer == CHUNK !!
                stream_callback=callback)

i = stream.start_stream()
print(i)

print("* grabando")
print("* pulsa q para termninar")

#frames = np.arange(0,dtype=np.int16)
#data = np.arange(CHUNK,dtype=np.int16)
kb = kbhit.KBHit()
c = ' '

while c != 'q': 
    #data = stream.read(CHUNK)  # recogida de samples
    #frames = np.concatenate(frames,data)
    if kb.kbhit(): 
        c = kb.getch()
        print(c)

'''
import time
time.sleep(2)
'''


print("* grabacion terminada")
kb.set_normal_term()


stream.stop_stream(); 
stream.close(); 

p.terminate()

# guardamos wav

wf.close()
