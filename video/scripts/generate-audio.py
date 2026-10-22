"""Generate Ledger's original 51-second warm ambient score."""

from pathlib import Path
import wave

import numpy as np

RATE = 48_000
DURATION = 51.0
OUT = Path(__file__).parents[1] / "public" / "ledger" / "audio" / "ledger-score.wav"


def smoothstep(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def oscillator(freq: float | np.ndarray, t: np.ndarray, phase: float = 0.0) -> np.ndarray:
    """A warm, nearly sine-like oscillator with quiet even harmonics."""
    base = np.sin(2 * np.pi * freq * t + phase)
    second = 0.16 * np.sin(2 * np.pi * freq * 2 * t + phase * 0.7)
    fourth = 0.035 * np.sin(2 * np.pi * freq * 4 * t + phase * 1.3)
    return (base + second + fourth) / 1.195


def pad(t: np.ndarray, start: float, end: float, notes: tuple[float, ...], phase: float) -> np.ndarray:
    local = (t - start) / max(end - start, 0.001)
    envelope = smoothstep(local * 2.8) * smoothstep((1 - local) * 2.8)
    signal = np.zeros_like(t)
    for index, note in enumerate(notes):
        drift = 1 + 0.0009 * np.sin(2 * np.pi * (0.031 + index * 0.004) * t + index)
        signal += oscillator(note * drift, t, phase + index * 0.83)
        signal += 0.28 * oscillator(note * 2.005, t, phase + index * 0.41)
    return signal / (len(notes) * 1.28) * envelope


def felt_note(t: np.ndarray, at: float, freq: float, strength: float) -> np.ndarray:
    local = t - at
    active = local >= 0
    attack = 1 - np.exp(-np.clip(local, 0, None) * 34)
    decay = np.exp(-np.clip(local, 0, None) / 2.8)
    body = oscillator(freq, t, at * 0.17) + 0.18 * oscillator(freq * 2.01, t, 0.4)
    return active * attack * decay * body * strength


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    t = np.arange(int(RATE * DURATION), dtype=np.float64) / RATE

    # Slow major-seventh harmony with long overlaps. There is no beat or hard impact.
    harmony = np.zeros_like(t)
    chords = [
        (0.0, 15.0, (73.42, 110.00, 138.59, 164.81)),
        (11.0, 27.0, (65.41, 98.00, 123.47, 146.83)),
        (23.0, 40.0, (82.41, 123.47, 146.83, 185.00)),
        (36.0, 51.0, (73.42, 110.00, 138.59, 164.81)),
    ]
    for index, (start, end, notes) in enumerate(chords):
        harmony += pad(t, start, end, notes, phase=index * 0.47) * 0.115

    # Sparse felt-key tones give the picture motion without sounding instructional.
    keys = np.zeros_like(t)
    note_events = [
        (1.2, 293.66, 0.038), (5.4, 329.63, 0.033), (9.3, 220.00, 0.035),
        (13.8, 246.94, 0.032), (18.6, 293.66, 0.039), (22.4, 369.99, 0.030),
        (27.7, 329.63, 0.034), (31.2, 293.66, 0.036), (35.8, 246.94, 0.032),
        (40.7, 329.63, 0.037), (44.3, 369.99, 0.030), (47.5, 293.66, 0.035),
    ]
    for at, freq, strength in note_events:
        keys += felt_note(t, at, freq, strength)

    # Air is deterministic, heavily smoothed noise. It should be felt before it is heard.
    rng = np.random.default_rng(20261021)
    noise = rng.normal(0, 1, len(t))
    window = 2400
    cumulative = np.cumsum(noise)
    delayed = np.concatenate((np.zeros(window), cumulative[:-window]))
    air = (cumulative - delayed) / window
    air /= max(float(np.max(np.abs(air))), 1e-9)
    air *= 0.0085 * (0.72 + 0.28 * np.sin(2 * np.pi * 0.041 * t + 0.8))

    # Soft harmonic blooms mark major story turns without percussive impacts.
    blooms = np.zeros_like(t)
    for cue, freq in ((8.0, 220.0), (19.0, 246.94), (31.0, 293.66), (44.0, 329.63), (47.5, 293.66)):
        distance = (t - cue) / 1.25
        envelope = np.exp(-(distance**2))
        blooms += envelope * oscillator(freq, t, cue * 0.11) * 0.018
        blooms += envelope * oscillator(freq * 1.5, t, cue * 0.07) * 0.007

    mono = harmony + keys + air + blooms

    # Subtle stereo drift, followed by long opening and closing fades.
    width = 0.009 * np.sin(2 * np.pi * 0.053 * t) * oscillator(440.0, t, 0.3)
    left = mono + width
    right = mono - width + 0.004 * oscillator(554.37, t, 0.8)
    master = smoothstep(t / 2.3) * smoothstep((DURATION - t) / 2.8)
    stereo = np.stack([left * master, right * master], axis=1)
    peak = max(float(np.max(np.abs(stereo))), 1e-9)
    stereo = np.clip(stereo / peak * 0.58, -1, 1)
    pcm = (stereo * 32767).astype("<i2")

    with wave.open(str(OUT), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(pcm.tobytes())
    print(f"wrote {OUT} ({DURATION:.1f}s, {RATE} Hz stereo)")


if __name__ == "__main__":
    main()
