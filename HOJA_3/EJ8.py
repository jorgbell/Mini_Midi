# 1_numPy/playNumPy.py   reproductor con Chunks
import pyaudio, kbhit, os

from scipy.io import wavfile # para manejo de wavs
from scipy import signal
import numpy as np  # arrays    


# Num bytes de la muestra (array de numpy)
def getWidthData(data):
    # miramos formato de samples
    if data.dtype.name == 'int16': return 2
    elif data.dtype.name in ['int32','float32']: return 4
    elif data.dtype.name == 'uint8': return 1
    else: raise Exception('Not supported')

last = 0
def oscChunk(vol, frec):
    global last
    dataChunk = vol*np.sin(2*np.pi*(np.arange(CHUNK)+last)*frec/SRATE)
    last+=CHUNK
    return dataChunk

# abrimos wav y recogemos frecMuestreo y array de datos
SRATE, data = wavfile.read('piano.wav')


# informacion de wav
print("Sample rate ",SRATE)
print("Sample format: ",data.dtype)
print("Num channels: ",len(data.shape))
print("Len: ",data.shape[0])


# arrancamos pyAudio
p = pyaudio.PyAudio()

CHUNK = 1024

stream = p.open(format=p.get_format_from_width(getWidthData(data)),
                channels=len(data.shape),
                rate=SRATE,
                frames_per_buffer=CHUNK,
                output=True)


# En data tenemos el wav completo, ahora procesamos por bloques (chunks)
bloque = np.arange(CHUNK,dtype=data.dtype)
numBloque = 0
kb = kbhit.KBHit()
c= ' '
step = 0
octava = 1
while c!= 'l': 
    if kb.kbhit():
        c = kb.getch()
        if c!= ' ' and c != 'l':
            numBloque = 0
            step = 0
            bloque = data[ numBloque*CHUNK : numBloque*CHUNK+CHUNK ]  
            if c == 'z':
                step = 1
                octava = 1
            elif c == 'x':
                step = 9/8
                octava = 1
            elif c == 'c':
                step = 5/4
                octava = 1
            elif c == 'v':
                step = 4/3
                octava = 1
            elif c == 'b':
                step = 3/2
                octava = 1
            elif c == 'n':
                step = 5/3
                octava = 1
            elif c == 'm':
                step = 15/8
                octava = 1
            elif c == 'q':
                step = 1
                octava = 2
            elif c == 'w':
                step = 9/8
                octava = 2
            elif c == 'e':
                step = 5/4
                octava = 2
            elif c == 'r':
                step = 4/3
                octava = 2
            elif c == 't':
                step = 3/2
                octava = 2
            elif c == 'y':
                step = 5/3
                octava = 2
            elif c == 'u':
                octava = 2
                step = 15/8    
            c = ' '
    

    if len(bloque>0) and step != 0:
        #print(int(len(bloque)/step))
        # nuevo bloque
        bloque = data[ numBloque*CHUNK : numBloque*CHUNK+CHUNK ]    
        
        if len(bloque>0):
            bloque = signal.resample(bloque, int(len(bloque)/(step*octava)), axis= 0)
            # pasamos al stream  haciendo conversion de tipo 
            stream.write(bloque.astype(data.dtype).tobytes())

            numBloque += 1
            print('.',end='')

kb.set_normal_term()        
stream.stop_stream()
stream.close()
p.terminate()
