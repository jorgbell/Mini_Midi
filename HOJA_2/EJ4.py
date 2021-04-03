import pyaudio
import os

from scipy.io import wavfile # para manipulación de wavs
import numpy as np # arrays

# Conversion del tipo de datos NumPy a numero de bytes por muestra
def getWidthData(data):
    if data.dtype.name == 'int16': return 2
    elif data.dtype.name in ['int32','float32']: return 4
    elif data.dtype.name == 'uint8': return 1
    else: raise Exception('Not supported')

SRATE, data = wavfile.read(os.path.dirname(__file__) + '\piano.wav') # Obtenemos SRATE y muestras (en data)

# información de wav (opcional)
print("SRATE: {} Format: {} Channels: {} Len: {}".
    format(SRATE, data.dtype, len(data.shape), data.shape[0]))

p = pyaudio.PyAudio() # arrancamos pyAudio

# Abrimos un stream de PyAudio para enviar ahí los datos
stream = p.open(format=p.get_format_from_width(getWidthData(data)),
    channels=len(data.shape), # num canales (shape de data)
    rate=SRATE, # frecuencia de muestreo
    frames_per_buffer=1024, # num frames por buffer (elegir)
    output=True) # es stream de salida ()

# escribimos en el stream -> suena!
#stream.write(data.astype(data.dtype).tobytes())

# bloque de tamanio CHUNK
CHUNK = 1024
bloque = np.arange(CHUNK,dtype=data.dtype)
# contador de bloques
numBloque = 0
while len(bloque>0):
    # nuevo bloque de tamanio CHUNK
    bloque = data[ numBloque*CHUNK : numBloque*CHUNK+CHUNK ]

    if len(bloque > 0):
        valor1 = np.max(bloque)
        valor2 = abs(np.min(bloque))
        maximo = 32768 / max(valor1, valor2)
        bloque = bloque * maximo

        """
        valMax = np.max(bloque)
        valMin = abs(np.min(bloque))

        maximo = 32768 / max(valMax, valMin)
        #media = (valMax+valMin)//2
        #print(numBloque, ": ", max, min, maximo)

        bloque = bloque * maximo
        #bloque = np.clip(bloque,0,media)
        #bloque = bloque / max
        #bloque = bloque * min
        """

        # pasamos al stream
        stream.write(bloque.astype(data.dtype).tobytes())

    numBloque += 1

# liberamos recursos
stream.stop_stream()
stream.close()
