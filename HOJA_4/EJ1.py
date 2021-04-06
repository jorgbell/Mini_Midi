# sintesis fm con multiples moduladores

import pyaudio, kbhit, os
import numpy as np

p = pyaudio.PyAudio()

RATE = 44100       # sampling rate, Hz, must be integer
CHUNK = 16



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


fc, fm = 220, 220
frecs = [[fc,0.8],[fc+fm,0.5],[fc+2*fm,0.3],[fc+3*fm,0.2]]

frame = 0
frecChanged = False

while True:
    samples = oscFM(frecs,frame)
   
    stream.write(samples.astype(np.float32).tobytes()) 
    
    frame += CHUNK

    if kb.kbhit():
        #os.system('clear')
        os.system('cls')
        c = kb.getch()
        
        if c =='z': break
        elif (c>='a' and c<='x'):
            v = ord(c)-ord('a')
            if v<len(frecs): frecs[v][1] = max(0,frecs[v][1]-0.01)
        elif (c>='A' and c<='X'):
            v = ord(c)-ord('A')
            if v<len(frecs): frecs[v][1] = min(3,frecs[v][1]+0.01) 

        elif c == ',':
            fc += 10
            frecChanged = True
        elif c == ';':
            fc -= 10
            frecChanged = True
        elif c == '.':
            fm += 10
            frecChanged = True
        elif c == ':':
            fm -= 10
            frecChanged = True
        if frecChanged:
            for x in range(len(frecs)):
                frecs[x][0] = fc + (fm * x)
            frecChanged = False

        print("z quit")
        for i in range(len(frecs)): 
            print("["+str(chr(ord('A')+i))+"/"+str(chr(ord('a')+i))+"] ", " Frec " , frecs[i][0],"  beta: ",frecs[i][1])
        print("[,/;] To change base Frec: ", fc)
        print("[./:] To change step Frec: ", fm)
      

stream.stop_stream()
stream.close()

p.terminate()
