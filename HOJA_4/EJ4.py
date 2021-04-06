# sintesis fm con multiples moduladores

import pyaudio, kbhit, os
import numpy as np

p = pyaudio.PyAudio()

RATE = 44100       # sampling rate, Hz, must be integer
CHUNK = 16

# frecuencia dada, frame inical, volumen
def osc(frec,vol,frame):
    return (vol*np.sin(2*np.pi*(np.arange(CHUNK)+frame)*frec/RATE)).astype(np.float32)
    

def timeToFrame(t): return int(t*RATE)

def getNoteJusta(c):
    step = -1
    octava = 0
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
        step = 15/8   
        octava = 2

    return step, octava

def getNoteTemperada(c):
    step = -1
    octava = 0
    if c == 'z':
        step = 0
        octava = 1
    elif c == 'x':
        step = 2
        octava = 1
    elif c == 'c':
        step = 3
        octava = 1
    elif c == 'v':
        step = 5
        octava = 1
    elif c == 'b':
        step = 7
        octava = 1
    elif c == 'n':
        step = 9
        octava = 1
    elif c == 'm':
        step = 11
        octava = 1
    elif c == 'q':
        step = 0
        octava = 2
    elif c == 'w':
        step = 2
        octava = 2
    elif c == 'e':
        step = 3
        octava = 2
    elif c == 'r':
        step = 5
        octava = 2
    elif c == 't':
        step = 7
        octava = 2
    elif c == 'y':
        step = 9
        octava = 2
    elif c == 'u':
        step = 11   
        octava = 2

    if step >= 0:
        step = 2**(step/12)
    return step, octava

def env(lst):
    # convertimos ultimo t de la envolvente en last frame
    last = timeToFrame(lst[len(lst)-1][0])

    # aniadimos 0 al final para evitar el corte con la señal a la que se aplique
    last = last + CHUNK  
     
    # señal con ceros 
    samples = np.zeros(last, dtype=np.float32)
    for i in range(1,len(lst)):
        ''' Interpolación entre cada pareja de puntos (f1,v1) (f2,v2)
        Fórmula clasica ...
        '''        
        f1, f2 = timeToFrame(lst[i-1][0]), timeToFrame(lst[i][0])
        v1, v2 = lst[i-1][1], lst[i][1]
        for j in range(f1,f2):
            # samples  interpolados
            samples[j] = v1 + (j-f1) * (v2-v1)/(f2-f1)
    return samples

# [(fc,vol),(fm1,beta1),(fm2,beta2),...]
def oscFM(frecs,frame):
    # sin(2πfc+βsin(2πfm))  
    chunk = np.arange(CHUNK)+frame
    samples = np.zeros(CHUNK)+frame
    # recorremos en orden inverso
    
    for i in range(len(frecs)-1,-1,-1):
        samples = frecs[i][1] * np.sin(2*np.pi*frecs[i][0]*chunk/RATE + samples)
    return samples

stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=RATE,
                output=True)


kb = kbhit.KBHit()
c = ' '

ROOT_FREC = 440
convC = 3/5
fc = ROOT_FREC
#1 5/4 3/2
frecs = [[fc,0.8],[fc*(5/4),0.6],[fc*(3/2),0.4]]

ptosEnv = [(0,0),(0.02,0.9),(0.1,0.3),(0.6,0.2),(2.3,0)]
last = len(ptosEnv)-1
endFrame = timeToFrame(ptosEnv[last][0])

envSamples = env(ptosEnv) 

frame = 0
step = -1
octava = 1
first = False
usingJusta = 1
c = ' '
while c != 'l':
    #os.system('clear')
    if kb.kbhit():
        step = -1
        os.system('cls')
        c = kb.getch()

        if c == 'k':
            usingJusta = (usingJusta+1)%2

        if usingJusta:
            step, octava = getNoteJusta(c)
            convC = 3/5
        else:
            step, octava = getNoteTemperada(c)
            convC = 1/(2**(8/12))
        if step != -1:
            first = True
            frame = 0
            fc = ROOT_FREC * convC * step * octava
            frecs[0][0] = fc
            if usingJusta:
                frecs[1][0] = fc*(5/4)
                frecs[2][0] = fc*(3/2)
            else:
                frecs[1][0] = fc*2**(3/12)
                frecs[2][0] = fc*2**(7/12)
            print(fc)

    if frame<endFrame and first:
        samples = oscFM(frecs,frame)

        samples = samples * envSamples[frame:frame+CHUNK]

        stream.write(samples.astype(np.float32).tobytes()) 
    
        frame += CHUNK
      

stream.stop_stream()
stream.close()

p.terminate()
