import pyaudio
import wave
import sys
import kbhit
from scipy.io import wavfile
import numpy as np

'''
if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)
'''
#fs, data = wavfile.read(sys.argv[1])
fs, data = wavfile.read('bakamitai.wav')

if data.dtype.name == 'int16':
    fmt = 2
elif data.dtype.name == 'int32':
    fmt = 4
elif data.dtype.name == 'float32':
    fmt = 4
elif data.dtype.name == 'uint8':    
    fmt = 1
else:
    raise Exception('Not supported')


p = pyaudio.PyAudio()
CHUNK = 1024
stream = p.open(format=p.get_format_from_width(fmt),
                channels=len(data.shape),
                rate=fs,
                frames_per_buffer=CHUNK,
                output=True)


data2 = np.arange(CHUNK,dtype=data.dtype)
kb = kbhit.KBHit()

frame = 0
c= ' '   

import math 


print("[F] frecuencia de corte +100")
print("[f] frecuencia de corte -100")
print("[b] filtro BP")
print("[B] desactivar filtro BP")

freq = 1000
prev = 0
filter = "bp"

while c!= 'q': # and not(quit):
    data0 = np.copy(data[frame*CHUNK:frame*CHUNK+CHUNK])
    data2 = np.copy(data[frame*CHUNK:frame*CHUNK+CHUNK])
        
    alpha = math.exp(-2*math.pi*freq / fs)    

    # filtro paso bajo
    if (filter=='bp'):
        data2[0] = alpha * prev + (1-alpha) * data2[0]
        for i in range(1,CHUNK):         
            data2[i] = alpha * data2[i-1] + (1-alpha) * data2[i]            
    # filtro paso alto (diferencia entre señal original y paso bajo)
        data2[0] = data[0] - alpha * prev + (1-alpha) * data2[0]
        for i in range(1,CHUNK):
            data2[i] = data2[i] - (alpha * data2[i-1] + (1-alpha) * data2[i])

    prev = data2[CHUNK-1]

    stream.write(data2.astype((data.dtype)).tobytes())    
    if kb.kbhit():
        c = kb.getch()
        print(c)
        if c =='q': break
        elif c=='F': freq += 100
        elif c=='f': freq -= 100
        elif c=='b': filter = 'bp'
        elif c=='B': filter = ' '
        freq = min(fs/2,max(0,freq))
        print("Filtro: ", filter,"   Cut off frec: ",freq)


    frame += 1

kb.set_normal_term()
        
stream.stop_stream()
stream.close()

p.terminate()
