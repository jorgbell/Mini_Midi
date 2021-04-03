import pyaudio, kbhit
import numpy as np
import time, sys
p = pyaudio.PyAudio()

#variables "globales"
SRATE = 44100  # sampling rate
TYPE = pyaudio.paFloat32
CHUNK = 1024
FREQ = 880
# generadores de sonidos
def osc(frec,dur,vol):
    # np.arange(RATE*dur) -> construimos array [0,1,2,...] de longitud RATE*dur
    # argumento del seno: 2pi*n*frec/RATE
    # multipliacado por el volumen  y conversion de tipo    
    return vol*np.sin(2*np.pi*np.arange(int(SRATE*dur))*frec/SRATE)   
'''
def noise(dur,vol):
    # random(n)  -> [x0,x1,...xn-1] muestras aleatorias en [0,1
    # xi*2-1   -> muestra aleatoria en [-1,1]
    return vol*(2.0*np.random.random(int(SRATE*dur))-1.0)
'''
def oscCuad(frec, dur, vol):
    return vol*(2*np.floor(np.sin(2*np.pi*np.arange(int(SRATE*dur))*frec/SRATE))+1)
def oscSierra(frec, dur, vol):
    return vol*(2*((np.arange(int(SRATE*dur)) % (SRATE/frec)) * frec/SRATE)-1)
last = 0
def oscChunk(vol):
    global last
    dataChunk = vol*np.sin(2*np.pi*(np.arange(CHUNK)+last)*FREQ/SRATE)
    last+=CHUNK
    return dataChunk



#comienzo del stream
stream= p.open(format=TYPE,
        channels=1,
        rate=SRATE, 
        output = True)

c = ' '
kb = kbhit.KBHit()
while c!= 'q':
    samples = oscChunk(0.5)
    stream.write(samples.astype(np.float32).tobytes())

    if kb.kbhit():
        c = kb.getch()
        if c =='q': break
        elif c=='f': FREQ-=10 
        elif c=='F': FREQ+=10
        print("Frec: ",FREQ)


stream.stop_stream()
stream.close()

p.terminate()
