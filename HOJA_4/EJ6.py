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


class Sample:
    def __init__(self, frec, vol, name, noteOn, noteOff):
        self.frec = frec
        self.vol = vol
        # un ciclo completo de seno en [0,2pi)

        #t = np.linspace(0, 1, num=size)
        #self.waveTable = np.sin(2 * np.pi * t)
        self.SRATE, self.data = wavfile.read(name)
        self.size = (noteOff - noteOn) * self.SRATE
        self.waveTable = self.data[int(noteOn * self.SRATE) : int(noteOff * self.SRATE)]
        # arranca en 0
        self.fase = 0
        # paso en la wavetable en funcion de frec y RATE
        self.step = self.size/(self.SRATE/self.frec)

    def setFrec(self,frec): 
        self.frec = frec
        self.step = self.size/(self.SRATE/self.frec)

    def getFrec(self): 
        return self.frec    


    def getChunk(self):
        samples = np.zeros(CHUNK,dtype=np.float32)
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
        

        return self.vol*samples


stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=RATE,
                output=True)


kb = kbhit.KBHit()
c = ' '

osc = Sample(440,1,"audio.wav", 0.5, 1.0)


while True:
    samples = osc.getChunk()
    
    stream.write(samples.tobytes())

    if kb.kbhit():
        os.system('clear')
        os.system('cls')
        c = kb.getch()
        print(c)        
        if c =='q': break
        elif c=='F': osc.setFrec(osc.getFrec()+1)
        elif c=='f': osc.setFrec(osc.getFrec()-1)

        print("Frec ",osc.getFrec())
        print("[F/f] subir/bajar frec")
        print("q quit")
        


stream.stop_stream()
stream.close()

p.terminate()
