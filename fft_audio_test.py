import pyaudio
from scipy import fftpack
import matplotlib.pyplot as plt
import numpy as np
import time
import transcriber as tb

p = pyaudio.PyAudio()
CHUNK = 2048  # bytes in one sample
RATE = 44100  # samples per sec, since 20kHz is max audible frequency
tol = 120  # db threshold
frames = 0  # for counting frames
freq_range = [200, 6000]

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
ax.set_ylim(-RATE, RATE)
ax.set_xlim(0, 2*CHUNK)
axf.set_title('Fourier Transform')
axf.set_xlim(0, freq_range[1] + 1000)  # display range
axf.set_ylim(-10, 200)
axf.set_ylabel('Frequency Power (dB)')
fig.canvas.draw()
fig.show()

start_note = 0
start_time = time.time()
start_freq = 0

while True:
    sig = stream.read(CHUNK)  # hex
    sig_u = np.fromstring(sig, dtype=np.int16)
    sig_fft = fftpack.fft(sig_u)
    sig_fft[0:round(freq_range[0] * CHUNK / RATE)] = 1
    sig_fft[round((freq_range[1] * CHUNK) / RATE):] = 1
    sig_fft[sig_fft == 0] = 1
    sig_fft_abs = list(10 * np.log10(np.abs(sig_fft.imag**2 + sig_fft.real**2)))
    max = np.max(sig_fft_abs)
    index = sig_fft_abs.index(max) - 1
    freq = (RATE - ((CHUNK - index) / CHUNK) * RATE + RATE/CHUNK)
    note = tb.get_note(freq)
    if max < tol:
        note = 0
    if note != start_note:
        end_time = time.time()
        length = end_time - start_time
        print(start_note, ' at ', str(start_freq), ' for ', str(length), ' seconds.')
        start_note = note
        start_time = time.time()
        start_freq = freq
    line1.set_ydata(sig_u)
    line2.set_ydata(sig_fft_abs)
    fig.canvas.update()
    fig.canvas.flush_events()