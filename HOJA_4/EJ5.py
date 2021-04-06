# karplus strong
# http://www-cs-students.stanford.edu/~blynn/sound/karplusstrong.html

import pyaudio, kbhit, os
import numpy as np

import matplotlib.pyplot as plt

p = pyaudio.PyAudio()

RATE = 44100       # sampling rate, Hz, must be integer
CHUNK = 1024

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

'''

Explanation
The Karplus-Strong algorithm is an example of digital waveguide synthesis. An instrument is physically modeled and simulated. In this case, the random samples crudely represents the initial pluck: each part of the string is in a random position moving at a random velocity.

The delay and feedback cause the waveform to repeat itself, oscillating as a string would. If we just had y[n]=y[n−N], we would have a waveform that repeats with frequency  RATE/N
'''

def karplus_strong(wavetable,nSamples):
    """Synthesizes a new waveform from an existing wavetable, modifies last sample by averaging."""
    samples = []
    current_sample = 0
    previous_value = 0
    while len(samples) < nSamples:
        wavetable[current_sample] = 0.5 * (wavetable[current_sample] + previous_value)
        samples.append(wavetable[current_sample])
        previous_value = samples[-1]
        current_sample += 1
        current_sample = current_sample % wavetable.size
    return np.array(samples)



def synthWaveTable(wavetable, frame):
    samples = np.zeros(CHUNK, dtype=np.float32)
    t = frame % len(wavetable)
    for i in range(CHUNK):
        samples[i] = wavetable[t]
        t = (t+1) % len(wavetable)
    return samples

# tabla con ruido
size = CHUNK//2  # variar size

NUM_STREAMS = 14
samples = []
streams = np.empty([NUM_STREAMS],dtype=pyaudio.Stream)
steps = [1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8]
inUse = np.zeros(NUM_STREAMS)
frames = np.zeros(NUM_STREAMS, dtype=np.int)

for x in range(NUM_STREAMS):
    stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=RATE,
                output=True)
    streams[x] = stream

    waveTable = (2 * np.random.randint(0, 2, int(size / (steps[x % len(steps)] * ((x // 7)+1) )) ) - 1).astype(np.float32)
    samples.append(karplus_strong(waveTable, 1*RATE))

kb = kbhit.KBHit()
c = ' '

vol = 0.8
frame = 0

frec = 440

# tabla con seno puro
# waveTable = np.sin(2*np.pi*frec*np.arange(RATE/frec,dtype=np.float32)/RATE) 


step = -1
octava = -1
first = False

print("Press l to exit")
print("Active streams: []")

while c != 'l':
    #os.system('clear')
    os.system('cls')
    if kb.kbhit():
        step = -1
        c = kb.getch()

        step = getNoteJusta(c)

        if step != -1:
            first = True
            inUse[step] = 1
            frames[step] = 0

    active = [i for i in range(len(inUse)) if inUse[i] != 0]

    print("Press l to exit")
    print("Active streams:",active)

    for x in range(len(inUse)):
        if inUse[x] == 1:
            if frames[x] < len(samples[x]):
                lastVal = frames[x] + int(CHUNK)
                if lastVal > len(samples[x]):
                    lastVal = len(samples[x])
                sample = samples[x][frames[x] : lastVal]
                streams[x].write(sample.astype(np.float32).tobytes()) 
            
                frames[x] += CHUNK
            else: 
                inUse[x] = 0

"""
# varias notas
waveTable = (2 * np.random.randint(0, 2, size) - 1).astype(np.float32)
stream.write(karplus_strong(waveTable,1*RATE).tobytes())

waveTable = (2 * np.random.randint(0, 2, size//2) - 1).astype(np.float32)
stream.write(karplus_strong(waveTable, 1*RATE).tobytes()) 

waveTable = (2 * np.random.randint(0, 2, size//4) - 1).astype(np.float32)
stream.write(karplus_strong(waveTable, 1*RATE).tobytes()) 



# escala diatónica
escala = [(2 * np.random.randint(0, 2, int(size/2**(k/12))) - 1).astype(np.float32) for k in range(24)]

for i in [0,2,4,5,7,9,11,12]:
    stream.write(karplus_strong(escala[i], 0.3*RATE).tobytes()) 

"""
for i in range(len(streams)):
    streams[i].stop_stream()
    streams[i].close()

p.terminate()
