#  well-tempered tuning
#  credit https://www.johndcook.com/blog/2016/02/10/musical-pitch-notation/
import numpy as np

A4 = 440
C0 = A4 * np.power(2, -4.75)
notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def get_note(freq):
    if freq == 0:
        return 0
    else:
        pitch = round(12 * np.float64(np.log2(freq / C0)).item())
        note = pitch % 12
        octave = pitch // 12
        if not octave:
            return notes[note] + str(0)
        else:
            return notes[note] + str(octave)
def get_num(freq):
    if freq == 0:
        return 0
    else:
        pitch = round(12 * np.float64(np.log2(freq / C0)).item())
        note = pitch % 12
        return note + 1
