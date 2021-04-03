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

def normalizar(data):
    valor1 = np.max(data)
    valor2 = abs(np.min(data))
    maximo = 32768 / max(valor1, valor2)
    data = data * maximo
    #data = np.clip(data,0,maximo)
    #print(media)
    return data


# abrimos wav y recogemos frecMuestreo y array de datos
SRATE, data = wavfile.read(os.path.dirname(__file__) + '\piano.wav')


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
    if(len(bloque > 0)):
        bloque = normalizar(bloque)
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
