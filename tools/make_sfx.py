"""Make the three button sound effects as short WAV files.

Each sound is built from sine waves (pure tones) with a quick fade-out,
so it is original and free to use.

Run:  python tools/make_sfx.py
"""
import os
import wave
import numpy as np

RATE = 44100
OUT = "art/audio"


def tone(freq_start, freq_end, seconds, volume=0.6, vibrato=0.0):
    """A tone that slides from one pitch to another and fades out."""
    t = np.linspace(0, seconds, int(RATE * seconds), endpoint=False)
    freq = np.linspace(freq_start, freq_end, len(t))
    if vibrato:
        freq = freq * (1 + 0.08 * np.sin(2 * np.pi * vibrato * t))
    phase = 2 * np.pi * np.cumsum(freq) / RATE              # smooth pitch change
    fade = np.exp(-t * 6 / seconds)                          # quick decay
    attack = np.minimum(1, t / 0.005)                        # no click at the start
    return volume * np.sin(phase) * fade * attack


def silence(seconds):
    return np.zeros(int(RATE * seconds))


def save(name, samples):
    samples = np.clip(samples, -1, 1)
    data = (samples * 32767).astype(np.int16)
    with wave.open(f"{OUT}/{name}.wav", "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(data.tobytes())
    print(f"{name}.wav  {len(data) / RATE:.2f}s")


os.makedirs(OUT, exist_ok=True)

# food: two chomps, the second a little lower
save("food", np.concatenate([tone(420, 260, 0.09), silence(0.05), tone(380, 220, 0.11)]))

# love: three rising notes (C6, E6, G6) overlapping like a chime
notes = [tone(f, f, 0.35, 0.4) for f in (1047, 1319, 1568)]
love = np.zeros(int(RATE * 0.55))
for k, n in enumerate(notes):
    start = int(RATE * 0.08 * k)
    love[start:start + len(n)] += n
save("love", love)

# play: a springy boing, sliding up with a wobble
save("play", tone(180, 620, 0.35, 0.6, vibrato=18))
