'''
    wavetable real con clase python
    para conseguir la continuidad en los chunks generados y no tener pops
    llevamos un atributo "fase" que recorre la tabla de ondas y se actualiza 
    en cada sample producido.
    La siguiente vez se solicita un chunk, la fase está en el punto correcto
    Si varia la frencia de un chunk al siguiente, se varia el "paso" (step) entre 
    muestas de la wavetable, pero la fase está donde quedo -> enlazan dos senos de
    distinta frecuencia
'''


import pyaudio, kbhit, os
import numpy as np

import matplotlib.pyplot as plt
from scipy.io import wavfile # para manejo de wavs

p = pyaudio.PyAudio()

RATE = 44100       # sampling rate, Hz, must be integer
CHUNK = 64

# Num bytes de la muestra (array de numpy)
def getWidthData(data):
    # miramos formato de samples
    if data.dtype.name == 'int16': return 2
    elif data.dtype.name in ['int32','float32']: return 4
    elif data.dtype.name == 'uint8': return 1
    else: raise Exception('Not supported')

def getNoteJusta(c):
    step = -1
    if c == 'z':
        step = 0
    elif c == 'x':
        step = 1
    elif c == 'c':
        step = 2
    elif c == 'v':
        step = 3
    elif c == 'b':
        step = 4
    elif c == 'n':
        step = 5
    elif c == 'm':
        step = 6
    elif c == 'q':
        step = 7
    elif c == 'w':
        step = 8
    elif c == 'e':
        step = 9
    elif c == 'r':
        step = 10
    elif c == 't':
        step = 11
    elif c == 'y':
        step = 12
    elif c == 'u':
        step = 13 

    return step


class Sample:
    def __init__(self, vol, name, noteOn, noteOff):
        self.vol = vol
        # un ciclo completo de seno en [0,2pi)

        #t = np.linspace(0, 1, num=size)
        #self.waveTable = np.sin(2 * np.pi * t)
        self.SRATE, self.data = wavfile.read(name)

        self.size = int((noteOff - noteOn) * self.SRATE)
        self.waveTable = self.data[int(noteOn * self.SRATE) : int(noteOff * self.SRATE)]
        # arranca en 0
        self.fase = 0
        # paso en la wavetable en funcion de frec y RATE
        self.step = 3/2
        #self.step = self.size/(self.SRATE/self.frec)

        self.stream = p.open(format=p.get_format_from_width(getWidthData(self.data)),
                channels=len(self.data.shape),
                rate=self.SRATE,
                output=True)

    def setStep(self,step): 
        self.step = step

    def getStep(self): 
        return self.step   

    def getRate(self):
        return self.SRATE

    def playChunk(self):
        samples = np.zeros(CHUNK,dtype=self.data.dtype)
        cont = 0
        #print("RATE ",RATE, "   frec ",self.frec)
        
        while cont < CHUNK:
            self.fase = (self.fase + self.step) % self.size

            # con truncamiento, sin redondeo
            # samples[cont] = self.waveTable[int(self.fase)]

            # con redondeo
            #x = round(self.fase) % self.size
            #samples[cont] = self.waveTable[x]
                        
            # con interpolacion lineal                                    
            x0 = int(self.fase) % self.size
            x1 = (x0 + 1) % self.size
            y0, y1 = self.waveTable[int(x0)], self.waveTable[int(x1)]            
            samples[cont] = y0 + (self.fase-x0)*(y1-y0)/(x1-x0)


            cont = cont+1
        
        samples = samples * self.vol
        self.stream.write(samples.tobytes())
        return samples

    def closeSampler(self):
        self.stream.stop_stream()
        self.stream.close()


osc = Sample(1,os.path.dirname(__file__) + '\\' + "piano.wav", 0.25, 0.5)


kb = kbhit.KBHit()
c = ' '

timePerNote = 0.5
steps = [1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8]

bloqueActual = 0
totalBloques = int(timePerNote*(osc.getRate()/CHUNK))

first = False

while c != 'l':

    if kb.kbhit():
        #os.system('clear')
        os.system('cls')
        c = kb.getch()
        print(c)     

        step = getNoteJusta(c)

        if step != -1:
            first = True
            stepAt = step%len(steps) + ((step // len(steps)) * len(steps))
            print(stepAt)
            osc.setStep(steps[step%len(steps)] + (step // len(steps)) )
            print("noteon")
            bloqueActual = 0

    if first == True:
        if bloqueActual < totalBloques:
            osc.playChunk()
            bloqueActual = bloqueActual + 1
        
        else:
            first = False
            print("noteoff")
            """
            if c =='q': break
            elif c=='F': osc.setFrec(osc.getFrec()+1)
            elif c=='f': osc.setFrec(osc.getFrec()-1)

            print("Frec ",osc.getFrec())
            print("[F/f] subir/bajar frec")
            print("q quit")
            """

osc.closeSampler()
p.terminate()
