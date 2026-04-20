"""
compound_sim metric used to compute the compound_ks column in pairs/pairs.csv.

Formula: 0.4·chroma + 0.3·duration + 0.1·register + 0.1·density

Input: Moonbeam compound-token .npy arrays, shape (N, 5+).
Token columns: [time, duration, octave, pitch_class, ...]
All timing values are in ticks at 480 TPQ, normalised to 120 BPM.

Extracted from scripts/eval/eval_r10_generated.py (Run 10 authoritative eval).
"""

from __future__ import annotations
import argparse
import numpy as np
from pathlib import Path


def chroma_vector(tokens: np.ndarray) -> np.ndarray:
    if len(tokens) == 0:
        return np.zeros(12)
    chroma = np.zeros(12)
    for row in tokens:
        pitch_class = int(row[3]) % 12
        chroma[pitch_class] += 1
    s = chroma.sum()
    return chroma / s if s > 0 else chroma


def chroma_sim_ks(a: np.ndarray, b: np.ndarray) -> float:
    """Transposition-invariant chroma cosine similarity (best key shift over 12 semitones)."""
    ca, cb = chroma_vector(a), chroma_vector(b)
    na, nb = np.linalg.norm(ca), np.linalg.norm(cb)
    if na == 0 or nb == 0:
        return 0.0
    return float(max(
        np.dot(np.roll(ca, k), cb) / (na * nb)
        for k in range(12)
    ))


def duration_dist(tokens: np.ndarray) -> np.ndarray:
    if len(tokens) == 0:
        return np.zeros(8)
    bins = np.array([0, 60, 120, 240, 480, 960, 1920, 3840, np.inf])
    durs = tokens[:, 1].astype(float)
    hist, _ = np.histogram(durs, bins=bins)
    s = hist.sum()
    return hist / s if s > 0 else hist.astype(float)


def duration_sim(a: np.ndarray, b: np.ndarray) -> float:
    da, db = duration_dist(a), duration_dist(b)
    return float(1.0 - 0.5 * np.sum(np.abs(da - db)))


def register_sim(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) == 0 or len(b) == 0:
        return 0.0
    ma = float(np.mean(a[:, 2] * 12 + a[:, 3]))
    mb = float(np.mean(b[:, 2] * 12 + b[:, 3]))
    return float(max(0.0, 1.0 - abs(ma - mb) / 88.0))


def density_sim(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) == 0 and len(b) == 0:
        return 1.0
    if len(a) == 0 or len(b) == 0:
        return 0.0
    da = len(a) / max(1, int(a[-1, 0] - a[0, 0]) + 1)
    db = len(b) / max(1, int(b[-1, 0] - b[0, 0]) + 1)
    return float(max(0.0, 1.0 - abs(da - db) / max(da, db, 1e-9)))


def compound_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Compute compound_sim between two compound-token arrays."""
    return (0.4 * chroma_sim_ks(a, b) +
            0.3 * duration_sim(a, b) +
            0.1 * register_sim(a, b) +
            0.1 * density_sim(a, b))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute compound_sim between two .npy section files.")
    parser.add_argument("file_a", type=Path, help="First section .npy file")
    parser.add_argument("file_b", type=Path, help="Second section .npy file")
    args = parser.parse_args()

    a = np.load(args.file_a)
    b = np.load(args.file_b)
    score = compound_sim(a, b)
    chroma = chroma_sim_ks(a, b)
    dur    = duration_sim(a, b)
    reg    = register_sim(a, b)
    den    = density_sim(a, b)
    print(f"compound_sim : {score:.4f}")
    print(f"  chroma     : {chroma:.4f}  (×0.4 = {0.4*chroma:.4f})")
    print(f"  duration   : {dur:.4f}  (×0.3 = {0.3*dur:.4f})")
    print(f"  register   : {reg:.4f}  (×0.1 = {0.1*reg:.4f})")
    print(f"  density    : {den:.4f}  (×0.1 = {0.1*den:.4f})")