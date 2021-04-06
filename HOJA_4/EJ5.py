# karplus strong
# http://www-cs-students.stanford.edu/~blynn/sound/karplusstrong.html

import pyaudio, kbhit, os
import numpy as np

import matplotlib.pyplot as plt

p = pyaudio.PyAudio()

RATE = 44100       # sampling rate, Hz, must be integer
CHUNK = 1024

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


stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=RATE,
                output=True)


kb = kbhit.KBHit()
c = ' '

vol = 0.8
frame = 0

frec = 440


# tabla con seno puro
# waveTable = np.sin(2*np.pi*frec*np.arange(RATE/frec,dtype=np.float32)/RATE) 

# tabla con ruido
size = CHUNK//2  # variar size


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


stream.stop_stream()
stream.close()

p.terminate()
