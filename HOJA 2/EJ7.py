import pyaudio, kbhit
import numpy as np
import time, sys
p = pyaudio.PyAudio()
#variables "globales"
SRATE = 44100  # sampling rate
TYPE = pyaudio.paFloat32
CHUNK = 1024
FREQ = 880
VOLUMEN = 0.5
# generadores de sonidos
def osc(frec,dur,vol):
    # np.arange(RATE*dur) -> construimos array [0,1,2,...] de longitud RATE*dur
    # argumento del seno: 2pi*n*frec/RATE
    # multipliacado por el volumen  y conversion de tipo    
    return vol*np.sin(2*np.pi*np.arange(int(SRATE*dur))*frec/SRATE)   
last = 0
def oscChunk(vol):
    global last
    dataChunk = vol*np.sin(2*np.pi*(np.arange(CHUNK)+last)*FREQ/SRATE)
    last+=CHUNK
    return dataChunk


#---------------------------------------------------------------------------------

#EJERCICIO ENTREGABLE 7: PARTITURA HAPPY BIRTHDAY
#Constantes para la duración de las notas
NEGRA=0.5
CORCHEA=NEGRA/2
BLANCA=NEGRA*2
#LISTA DE FRECUENCIAS PARA LAS NOTAS
'''
freqTables=[("C", 523.251), 
          ("D", 587.33),
          ("E", 659.255),
          ("F", 698.456),
          ("G", 783.991),
          ("A", 880),
          ("B", 987.767)]
'''
#clase con la tabla de frecuencias because no se usar una lista de python sin hacer un for para buscar un miembro xd
class FreqTable:
    def __init__(self):
        self.C = 523.251
        self.D = 587.251
        self.E = 659.255
        self.F= 698.456
        self.G =783.991
        self.A=880
        self.B=987.767

#Lista de pares para la partitura de Happy Birthday
freqs= FreqTable()
partitura=[(freqs.G, CORCHEA), (freqs.G, CORCHEA), (freqs.A,NEGRA),(freqs.G, NEGRA),
            (freqs.C*2, NEGRA), (freqs.B, BLANCA),
            (freqs.G, CORCHEA), (freqs.G, CORCHEA),(freqs.A,NEGRA),(freqs.G, NEGRA),
            (freqs.D*2,NEGRA),(freqs.C*2, BLANCA),
            (freqs.G, CORCHEA), (freqs.G, CORCHEA), (freqs.G*2,NEGRA),(freqs.E*2, NEGRA),
            (freqs.C*2,NEGRA), (freqs.B, NEGRA), (freqs.A, NEGRA),
            (freqs.F*2, CORCHEA), (freqs.F*2, CORCHEA), (freqs.E*2,NEGRA),(freqs.C*2, NEGRA),
            (freqs.D*2, NEGRA), (freqs.C*2, BLANCA)]
            

#comienzo del stream
stream= p.open(format=TYPE,
        channels=1,
        rate=SRATE, 
        output = True)

c = ' '
kb = kbhit.KBHit()
i=0
notaPrev=0.0
silencio = False
while c!= 'q' and i<len(partitura):
    #reproductor de la partitura
    notaAct= partitura[i][0] #Nota que va a tocar a continuacion
    durAct=partitura[i][1] #Duración de la nota
    '''
    #comprueba si la nota actual es igual a la anterior para meter un pequeño silencio de por medio (porque si no, suena como una sola)
    if notaAct == notaPrev:
        silencio = True
    #A continuación toca la nota correspondiente o en su defecto un pequeño silencio
    if silencio: #si hay que meter un pequeño silencio
        samples=osc(notaAct,0.08,0) #mete un pequeño silencio entre ambas
        silencio = False
        notaPrev = 0.0
    else:
        samples=osc(notaAct, durAct,VOLUMEN) #frecuencia,duracion,volumen
        notaPrev=notaAct
        i=i+1
    '''   
    samples=osc(notaAct, durAct,VOLUMEN) #frecuencia,duracion,volumen
    stream.write(samples.astype(np.float32).tobytes())
    samples=osc(notaAct,0.08,0) #mete un pequeño silencio entre ambas
    stream.write(samples.astype(np.float32).tobytes())
    i=i+1
    if kb.kbhit():
        c = kb.getch()
        if c =='q':
            break
       
    


stream.stop_stream()
stream.close()

p.terminate()
