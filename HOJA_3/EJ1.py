# 3_generadores/generadores.py
import pyaudio, kbhit
import numpy as np

p = pyaudio.PyAudio()

SRATE = 44100  # sampling rate
TYPE = np.float32

# genera un sinusoide con frecuencia (Hz), duración (segs) y volumen [0,1] dados
def osc(frec,dur,vol):
    # np.arange(RATE*dur) -> construimos array [0,1,2,...] de longitud RATE*dur
    # argumento del seno: 2pi*n*frec/RATE
    # multipliacado por el volumen  y conversion de tipo    
    return vol*np.sin(2*np.pi*np.arange(int(SRATE*dur))*frec/SRATE)
    

def noise(dur,vol):
    # random(n)  -> [x0,x1,...xn-1] muestras aleatorias en [0,1
    # xi*2-1   -> muestra aleatoria en [-1,1]
    return vol*(2.0*np.random.random(int(SRATE*dur))-1.0)
    



# for paFloat32 sample values must be in range [-1.0, 1.0]
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=SRATE,
                output=True)


#samples = noise(1.0,0.4)

c = ' '
kb = kbhit.KBHit()

frec = 880

while c!= 'q':
    samples = osc(frec,0.1,0.5)
    stream.write(samples.astype(TYPE).tobytes())

    if kb.kbhit():
        c = kb.getch()
        print(c)
        if c =='q': break
        elif c=='f': frec-=10 
        elif c=='F': frec+=10
        print("Frec: ",frec)


stream.stop_stream()
stream.close()

p.terminate()
