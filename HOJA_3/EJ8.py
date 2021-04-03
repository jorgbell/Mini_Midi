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
def oscChunk(vol):
    global last
    dataChunk = vol*np.sin(2*np.pi*(np.arange(CHUNK)+last)*FREQ/SRATE)
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
step = 1
while c!= 'q': 
    if kb.kbhit():
        c = kb.getch()
        if c!= ' ' and c != 'q':
            numBloque = 0
            bloque = data[ numBloque*CHUNK : numBloque*CHUNK+CHUNK ]  
            if c == 'z':
                step = 1
            elif c == 'x':
                step = 1.17
            elif c == 'c':
                step = 1.32
            elif c == 'v':
                step = 1.42
            elif c == 'b':
                step = 1.58
            elif c == 'n':
                step = 1.74
            elif c == 'm':
                step = 1.91
            c = ' '
    
    bloque = signal.resample(bloque, int(len(bloque)/step), axis= 0)

    if len(bloque>0):
        # nuevo bloque
        bloque = data[ numBloque*CHUNK : numBloque*CHUNK+CHUNK ]    

        # pasamos al stream  haciendo conversion de tipo 
        stream.write(bloque.astype(data.dtype).tobytes())

        numBloque += 1
        print('.',end='')

kb.set_normal_term()        
stream.stop_stream()
stream.close()
p.terminate()
