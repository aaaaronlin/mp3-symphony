import pyaudio
from scipy import fftpack
import numpy as np
import time
import transcriber as tb
import MQTTsend

CHUNK = 2048  # splitting the sample
RATE = 44100  # samples per sec, since 20kHz is max audible frequency
tol = 120  # db threshold for a note
frames = 0  # for counting frames
freq_range = [200, 5000]  # range of frequencies to analyze
sig_arr = []
sig_time = []
MQTT_str = "0,0"

p = pyaudio.PyAudio()
stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            output=True,
            frames_per_buffer=CHUNK)

print("'START' to start recording, Ctrl+C to stop.")

if input() == 'START':
    print('Now recording audio...')
    while True:
        start_time = time.time()
        try:
            s = list(np.fromstring(stream.read(CHUNK), dtype=np.int16))  # decode hex
            t = time.time() - start_time
            sig_arr.append(s)
            sig_time.append(t)
        except KeyboardInterrupt:
            break
else:
    print('No recording.')
    exit()

print("'YES' to perform FFT and note analysis")

if input() == 'YES':
    start_note = 0
    start_freq = 0
    index = 0
    length = 0
    for i in range(0, len(sig_arr)):
        sig_fft = fftpack.fft(sig_arr[i])
        sig_fft[0:int(np.ceil(freq_range[0] * CHUNK / RATE))] = 1  # cutoff
        sig_fft[int(np.floor((freq_range[1] * CHUNK) / RATE)):] = 1
        sig_fft[sig_fft == 0] = 1  # for np logic
        sig_fft_abs = list(10 * np.log10(np.abs(sig_fft.imag ** 2 + sig_fft.real ** 2)))  # calc db
        sig_max = np.max(sig_fft_abs)
        index = sig_fft_abs.index(sig_max) - 1
        freq = (RATE - ((CHUNK - index) / CHUNK) * RATE + RATE / CHUNK)
        note = tb.get_note(freq)
        if sig_max < tol:
            note = 0
            freq = 0
        if note != start_note:
            for j in range(index, i-1):
                length += sig_time[j]
            print(start_note, ' at ', str(start_freq), ' Hz for ', str(length), ' seconds.')
            MQTT_str += "/" + str(tb.get_num(start_freq)) + "," + str(np.round(length, 3))
            start_note = note
            start_freq = freq
            index = i
            length = 0
    print('Total Recording Length: ', sum(sig_time), ' seconds')
    print('Data string: ', MQTT_str)
else:
    print('Did not compute.')
    exit()

print("'PLAY' to send to chime.")

if input() == 'PLAY':
    MQTTsend.send_MCU(MQTT_str)
else:
    print('Not playing.')