"""Generate Ledger's original 48-second ambient score and transition accents."""

from pathlib import Path
import wave

import numpy as np

RATE = 48_000
DURATION = 48.0
OUT = Path(__file__).parents[1] / "public" / "ledger" / "audio" / "ledger-score.wav"


def smoothstep(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def tone(freq: float, t: np.ndarray, phase: float = 0.0) -> np.ndarray:
    return np.sin(2 * np.pi * freq * t + phase)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    t = np.arange(int(RATE * DURATION), dtype=np.float64) / RATE
    audio = np.zeros_like(t)

    # Four restrained harmonic fields. Each phrase crossfades into the next.
    chords = [
        (0.0, 10.0, (55.0, 82.41, 110.0)),
        (8.0, 21.0, (61.74, 92.50, 123.47)),
        (19.0, 38.0, (65.41, 98.0, 130.81)),
        (36.0, 48.0, (55.0, 82.41, 110.0)),
    ]
    for start, end, notes in chords:
        local = (t - start) / max(end - start, 0.001)
        env = smoothstep(local * 5.5) * smoothstep((1 - local) * 5.5)
        bed = sum(tone(freq, t, idx * 0.7) for idx, freq in enumerate(notes)) / len(notes)
        shimmer = 0.18 * tone(notes[-1] * 2, t, 0.4) + 0.07 * tone(notes[-1] * 4, t, 1.1)
        audio += env * (bed + shimmer) * 0.12

    # Quiet rhythmic pulse for forward motion.
    beat_phase = np.mod(t, 1.0)
    pulse = np.exp(-beat_phase * 10.5) * tone(110.0, t)
    audio += pulse * 0.028

    # Transition sweeps and low impacts, aligned to scene boundaries.
    for cue in (3.5, 8.0, 13.5, 19.0, 28.0, 41.0, 44.5):
        local = t - cue
        hit = np.exp(-np.clip(local, 0, None) * 7.5) * (local >= 0) * tone(52.0, t)
        pre = np.clip((local + 0.42) / 0.42, 0, 1) * np.clip((-local) / 0.42, 0, 1)
        sweep = np.sin(2 * np.pi * (180 + 520 * (local + 0.42) ** 2) * t) * pre
        audio += hit * 0.16 + sweep * 0.018

    # Deterministic stereo width and master fades.
    left = audio + 0.012 * tone(0.17, t) * tone(164.81, t)
    right = audio - 0.012 * tone(0.19, t, 0.6) * tone(164.81, t, 0.25)
    master = smoothstep(t / 1.1) * smoothstep((DURATION - t) / 1.6)
    stereo = np.stack([left * master, right * master], axis=1)
    peak = max(float(np.max(np.abs(stereo))), 1e-9)
    stereo = np.clip(stereo / peak * 0.78, -1, 1)
    pcm = (stereo * 32767).astype('<i2')

    with wave.open(str(OUT), 'wb') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(pcm.tobytes())
    print(f"wrote {OUT} ({DURATION:.1f}s, {RATE} Hz stereo)")


if __name__ == '__main__':
    main()
