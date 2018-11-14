import pyaudio
from scipy import fftpack
import matplotlib.pyplot as plt
import numpy as np
import struct
import time

p = pyaudio.PyAudio()
CHUNK = 2048  # bytes in one sample
RATE = 44100  # samples per sec, since 20kHz is max audible frequency
frames = 0  # for counting frames
frame_av = 6  # averages every frame_av values
a = np.zeros(CHUNK-1)

stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            output=True,
            frames_per_buffer=CHUNK)

fig = plt.figure()
ax = fig.add_subplot(121)
axf = fig.add_subplot(122)
x = np.arange(0, 2*CHUNK, 2)
xf = np.linspace(0, RATE, CHUNK)
line1, = ax.plot(x, np.random.rand(CHUNK), '-')
line2, = axf.plot(xf, np.random.rand(CHUNK), '-')

ax.set_title('Audio Signal')
ax.set_ylim(0, 255)  # comes in a byte
ax.set_xlim(0, 2*CHUNK)
axf.set_title('Fourier Transform')
axf.set_xlim(20, 2000)  # 20kHz again
plt.ion()
plt.show()
start_time = time.time()

while True:
    sig = stream.read(CHUNK)  # gives some weird b/x00 that is 2*CHUNK long
    sig_u = struct.unpack(str(2*CHUNK) + 'B', sig)  # gives 2*Chunk number of bytes
    sig_plt = np.array(sig_u, dtype='b')[::2] + 128  # takes every other and adds 128
    sig_fft = fftpack.fft(sig_u)
    sig_fft_abs = list(np.abs(sig_fft.real[0:CHUNK] / (128 * CHUNK)))[1:]
    if frames % frame_av == 0:
        a = list(a / frame_av)
        index = a.index(max(a))
        a = np.zeros(CHUNK-1)
        print(RATE - ((CHUNK - index) / CHUNK) * RATE + RATE/CHUNK)
    else:
        a = np.array(sig_fft_abs) + a
    line1.set_ydata(sig_plt)
    line2.set_ydata(np.abs(sig_fft.real[0:CHUNK] / (128 * CHUNK)))
    fig.canvas.draw()
    fig.canvas.flush_events()
    frames += 1
    #print('FPS: ', (frames / (time.time() - start_time)))
