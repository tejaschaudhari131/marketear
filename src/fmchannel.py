"""SIMULATED broadcast-FM channel: audio -> pre-emphasis -> FM modulation -> AWGN at a stated CNR -> channel filter -> discriminator -> de-emphasis.
Ported from /workspace/hacknation/ideation2_scripts/chain_test.py (fm_chain) with per-clip seeding. NOT a real radio recording.
Assumptions (stated, not measured): 50 us emphasis (Africa/Europe), 75 kHz peak deviation (audio scaled to 0.7 of full deviation),
CNR defined in a 200 kHz channel, mono only (no stereo pilot, no RDS), no multipath or fading, so real reception is harder."""
import numpy as np, scipy.signal as sg
FS = 1_024_000; TAU = 50e-6; DEV = 75e3
def fm_chain(a16, cnr_db, seed=0):
    if cnr_db is None: return a16.astype(np.float32)
    rng = np.random.default_rng(seed)
    a = sg.resample_poly(a16, 64, 1)
    a = a / (np.max(np.abs(a))+1e-9) * 0.7
    al = np.exp(-1/(FS*TAU))
    a = sg.lfilter([1.0, -al], [1.0], a)               # pre-emphasis (first-order, corner ~3.2 kHz)
    a = a / (np.max(np.abs(a))+1e-9) * 0.7
    ph = 2*np.pi*DEV*np.cumsum(a)/FS
    iq = np.exp(1j*ph)                                   # unit-power constant-envelope carrier
    Pn = 10**(-cnr_db/10) * (FS/200e3)                   # total noise power so that in-channel (200 kHz) CNR = cnr_db
    iq = iq + (rng.standard_normal(len(iq)) + 1j*rng.standard_normal(len(iq))) * np.sqrt(Pn/2)
    b = sg.firwin(129, 100e3, fs=FS); iq = sg.filtfilt(b, [1], iq)           # 200 kHz channel filter
    d = np.angle(iq[1:]*np.conj(iq[:-1])) * FS/(2*np.pi*DEV)                # discriminator
    b2 = sg.firwin(255, 7.5e3, fs=FS); d = sg.filtfilt(b2, [1], d)           # audio low-pass (band-limit; 16 kHz output => 8 kHz Nyquist)
    d = sg.resample_poly(d, 1, 64)
    a16k = np.exp(-1/(16000*TAU)); d = sg.lfilter([1-a16k], [1, -a16k], d)  # de-emphasis
    d = d / (np.max(np.abs(d))+1e-9) * 0.7
    return d.astype(np.float32)
