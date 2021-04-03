# 1_numPy/playNumPy.py   reproductor con Chunks
import pyaudio, kbhit, os

from scipy.io import wavfile # para manejo de wavs
import numpy as np  # arrays    

# Num bytes de la muestra (array de numpy)
def getWidthData(data):
    # miramos formato de samples
    if data.dtype.name == 'int16': return 2
    elif data.dtype.name in ['int32','float32']: return 4
    elif data.dtype.name == 'uint8': return 1
    else: raise Exception('Not supported')

last = 0
FREQ = 100
def oscChunk(vol):
    global last
    dataChunk = vol*np.sin(2*np.pi*(np.arange(CHUNK)+last)*FREQ/SRATE)
    last+=CHUNK
    return dataChunk

# abrimos wav y recogemos frecMuestreo y array de datos
SRATE, data = wavfile.read(os.path.dirname(__file__) + '\Prelude28n4.0.8.1.Completado.wav')


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
while len(bloque>0) and c!= 'q': 
    # nuevo bloque
    bloque = data[ numBloque*CHUNK : numBloque*CHUNK+CHUNK ]    

    samples  = np.fromstring(data, dtype=np.int16)
    # Normalize by int16 max (32767) for convenience, also converts everything to floats
    #normed_samples = samples / float(np.iinfo(np.int16).max)
    # split out the left and right channels to return separately.
    # audio data is stored [left-val1, right-val1, left-val2, right-val2, ...]
    # so just need to partition it out.
    left_samples = samples[0::2]
    right_samples = samples[1::2]

    pan = oscChunk(1)
    """
    left_samples = left_samples * pan
    right_samples = right_samples * -pan
    """

    for x in range(pan.size):
        left_samples[x] = left_samples[x] * pan[x]
        right_samples[x] = right_samples[x] * -pan[x]

    # pasamos al stream  haciendo conversion de tipo 
    stream.write(bloque.astype(data.dtype).tobytes())

    if kb.kbhit():
        c = kb.getch()

    numBloque += 1
    print('.',end='')

kb.set_normal_term()        
stream.stop_stream()
stream.close()
p.terminate()
