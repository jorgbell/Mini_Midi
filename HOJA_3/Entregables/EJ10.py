# basic/record0.py Grabacion de un archivo de audio 'q' para terminar
import pyaudio, kbhit
import numpy as np
from scipy.io.wavfile import write


CHUNK = 1024
FORMAT = pyaudio.paFloat32
CHANNELS = 1
SRATE = 44100

def setDelay(data, delayTime):
    delay = np.zeros(int(delayTime * SRATE), dtype=data.dtype)
    return np.append(delay, data)

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, 
                channels=CHANNELS,
                rate=SRATE,                 
                frames_per_buffer=CHUNK, # tamanio buffer == CHUNK !!
                output=True,
                input=True)   # ahora es flujo de entrada

print("* grabando")
print("* pulsa q para termninar")

data = np.array(CHUNK,dtype=np.float32)

DELAY_TIME = 0.3
data = setDelay(data, DELAY_TIME)

numBloque = 0
kb = kbhit.KBHit()
c = ' '
while c != 'q': 
    bloque = stream.read(CHUNK)  # recogida de samples (en bruto)
    bloque = np.frombuffer(bloque,dtype=np.float32) #conversión a np.array
    data = np.append(data,bloque) # acumulado

    bloque = data[ numBloque*CHUNK : numBloque*CHUNK+CHUNK ]    
    stream.write(bloque.astype(data.dtype).tobytes())

    numBloque += 1
    print('.',end='')

    if kb.kbhit(): c = kb.getch()

while len(bloque>0) and c!= 'q': 
    # nuevo bloque
    bloque = data[ numBloque*CHUNK : numBloque*CHUNK+CHUNK ]    

    # pasamos al stream  haciendo conversion de tipo 
    stream.write(bloque.astype(data.dtype).tobytes())

    if kb.kbhit():
        c = kb.getch()

    numBloque += 1
    print('.',end='')

print("* grabacion terminada")
stream.stop_stream(); 
stream.close(); 

# guardamos wav

print('Quieres reproducir [S/n]? ',end='')
while not kb.kbhit(): 
    True

c = kb.getch()
if c!='n':
    stream = p.open(format=FORMAT,
                    channels=len(data.shape),
                    rate=SRATE,
                    frames_per_buffer=CHUNK,
                    output=True)

    stream.write(data.tobytes())    
    stream.stop_stream()
    stream.close()

kb.set_normal_term(); 
p.terminate()

# escritura del wav
write("rec.wav", SRATE, data.astype(np.float32))

