import pyaudio
from scipy import fftpack
import matplotlib.pyplot as plt
import numpy as np
import struct
import time
from scipy.signal import butter, lfilter

p = pyaudio.PyAudio()
CHUNK = 2048  # bytes in one sample
RATE = 44100  # samples per sec, since 20kHz is max audible frequency
frames = 0  # for counting frames
frame_av = 6  # averages every frame_av values
a = np.zeros(CHUNK)
FPS = []

order = 5
lowcut = 200
highcut = 2000

def butter_bandpass(lowcut, highcut, fs, order):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            output=True,
            frames_per_buffer=CHUNK)

fig = plt.figure()
plt.ion()
ax = fig.add_subplot(121)
axf = fig.add_subplot(122)
x = np.arange(0, 2*CHUNK, 2)
xf = np.linspace(0, RATE, CHUNK)
line1, = ax.plot(x, np.random.rand(CHUNK), '-')
line2, = axf.plot(xf, np.random.rand(CHUNK), '-')

ax.set_title('Audio Signal')
ax.set_ylim(-100, 300)  # comes in a byte
ax.set_xlim(0, 2*CHUNK)
axf.set_title('Fourier Transform')
axf.set_xlim(lowcut, highcut)  # display range
fig.canvas.draw()
fig.show()
start_time = time.time()

while True:
    sig = stream.read(CHUNK)  # gives some weird b/x00 that is 2*CHUNK long
    sig_u = struct.unpack(str(2*CHUNK) + 'B', sig)  # gives 2*Chunk number of bytes
    sig_u_bp = butter_bandpass_filter(sig_u, lowcut, highcut, RATE*2, order)
    sig_plt = np.array(sig_u_bp, dtype='b')[::2] + 128  # takes every other and adds 128
    sig_fft = fftpack.fft(sig_u_bp)
    sig_fft_abs = list(20 * np.log10(np.abs(sig_fft.real[0:CHUNK] / (128 * CHUNK))))
    if frames % frame_av == 0:
        a = list(a / frame_av)
        index = a.index(max(a))
        a = np.zeros(CHUNK)
        print(RATE - ((CHUNK - index) / CHUNK) * RATE + RATE/CHUNK)
    else:
        a = np.array(sig_fft_abs) + a
    line1.set_ydata(sig_plt)
    line2.set_ydata(np.abs(sig_fft.real[0:CHUNK] / (128 * CHUNK)))
    fig.canvas.update()
    fig.canvas.flush_events()
    frames += 1
    FPS.append(frames / (time.time() - start_time))
