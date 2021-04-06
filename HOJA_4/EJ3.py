# creacion de una ventana de pygame
import pygame
from pygame.locals import *

# sintesis fm con multiples moduladores

import pyaudio, kbhit, os
import numpy as np

from enum import Enum

p = pyaudio.PyAudio()

RATE = 44100       # sampling rate, Hz, must be integer
CHUNK = 64

class WaveShape(Enum):
    SIN = 0
    SQUARE = 1
    SAW = 2

class OscWaveTable:
    def __init__(self, frec, vol, size, frecs):
        self.frec = frec
        self.vol = vol
        self.size = size
        self.frecs = frecs
        # un ciclo completo de seno en [0,2pi)
        t = np.linspace(0, 1, num=size)
        self.waveTable = np.sin(2 * np.pi * t)
        self.waveTables = []
        for x in range(len(frecs)):
            t = np.linspace(0, 1, num=size*frecs[x][0])
            self.waveTables.append(np.sin(2 * np.pi * t))
        # arranca en 0
        self.fase = 0
        self.fases = np.zeros(len(frecs))
        # paso en la wavetable en funcion de frec y RATE
        self.step = self.size/(RATE/self.frec)
        self.steps = np.zeros(len(frecs))

        for x in range(len(frecs)):
            self.steps[x] = self.size/(RATE/self.frecs[x][0])

    def setFrec(self,frec): 
        self.frec = frec
        self.step = self.size/(RATE/self.frec)

    def setFrecs(self, frecs):
        self.frecs = frecs
        for x in range(len(frecs)):
            self.steps[x] = self.size/(RATE/self.frecs[x][0])
            #t = np.linspace(0, 1, num=self.size*frecs[x][0])
            #self.waveTables[x] = np.sin(2 * np.pi * t)

    def getFrec(self): 
        return self.frec    


    def getChunkFM(self):
        samples = np.zeros(CHUNK,dtype=np.float32)
        chunk = np.zeros(CHUNK, dtype=np.float32)

        for i in range(len(frecs)-1,-1,-1):
            cont = 0
            while cont < CHUNK:
                self.fases[i] = (self.fases[i] + self.steps[i] + chunk[cont]) % self.size

                # con truncamiento, sin redondeo
                # samples[cont] = self.waveTable[int(self.fase)]

                # con redondeo
                #x = round(self.fase) % self.size
                #samples[cont] = self.waveTable[x]
                            
                # con interpolacion lineal 
                #print(samples[cont])                                   
                x0 = int(self.fases[i]) % self.size
                x1 = int(x0 + 1) % self.size
                y0, y1 = self.waveTable[x0], self.waveTable[x1]            
                chunk[cont] = y0 + (self.fases[i]-x0)*(y1-y0)/(x1-x0)

                #if chunk[cont] < 0:
                    #print("oh no")
                cont = cont+1

            samples = self.frecs[i][1] * chunk 

        return self.vol * samples

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
            y0, y1 = self.waveTable[x0], self.waveTable[x1]            
            samples[cont] = y0 + (self.fase-x0)*(y1-y0)/(x1-x0)

            cont = cont+1
            

        return self.vol*samples

def oscSin(frec, chunk, samples):
    return np.sin(2*np.pi*frec*chunk/RATE + samples)
def oscCuad(frec, chunk, samples):
    return 2*np.floor(oscSin(frec, chunk, samples))+1
def oscSierra(frec, chunk, samples):
    return 2*(chunk % (RATE/frec) * frec/RATE + samples)-1

# [(fc,vol),(fm1,beta1),(fm2,beta2),...]
def oscFM(frecs,frame):
    # sin(2πfc+βsin(2πfm))  
    chunk = np.arange(CHUNK)+frame
    samples = np.zeros(CHUNK)+frame
    # recorremos en orden inverso
    
    for i in range(len(frecs)-1,-1,-1):
        #samples = frecs[i][1] * np.sin(2*np.pi*frecs[i][0]*chunk/RATE + samples)
        if frecs[i][2] == WaveShape.SIN:
            samples = frecs[i][1] * oscSin(frecs[i][0], chunk, samples)
        elif frecs[i][2] == WaveShape.SQUARE:
            samples = frecs[i][1] * 0.5 * oscCuad(frecs[i][0], chunk, samples)
        elif frecs[i][2] == WaveShape.SAW:
            samples = frecs[i][1] * 0.5 * oscSierra(frecs[i][0], chunk, samples)

        # los 0.5 son porque si no satura mucho el sonido

    return samples

WIDTH = 960
HEIGHT = 480

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Theremin")

stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=RATE,
                output=True)

#...

fc, fm = 220, 220
frecs = [[fc,0.8,WaveShape.SIN],[fc+fm,0.5,WaveShape.SIN],[fc+2*fm,0.3,WaveShape.SIN],[fc+3*fm,0.2,WaveShape.SIN]]

osc = OscWaveTable(110,1,1024,frecs)

frame = 0
vol = 0

while True:
    # obtencion de la posicion del raton
    for event in pygame.event.get():
        if event.type == pygame.MOUSEMOTION:
            mouseX, mouseY = event.pos

            vol = 1 - (mouseY/HEIGHT)
            fc = (mouseX/WIDTH * 9900) + 100

            osc.setFrec(fc)

            for x in range(len(frecs)):
                frecs[x][0] = fc + (fm * x)
    
            osc.setFrecs(frecs)
            #print("Freq:", fc, "Vol:", vol)
            #print(fc)
            #print(vol)

    # Las 3 opciones para reproducir el audio del theremin
    #samples = oscFM(frecs,frame)
    samples = osc.getChunk()
    #samples = osc.getChunkFM()

    frame += CHUNK

    samples = samples * vol

    stream.write(samples.astype(np.float32).tobytes()) 

pygame.quit()