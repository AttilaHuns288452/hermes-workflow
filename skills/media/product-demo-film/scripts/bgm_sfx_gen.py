#!/usr/bin/env python3
"""Cinematic BGM + UI SFX generator (numpy + wave, no network, no API keys).
Edit the CONFIG block per film: duration, music sections, montage impact times.
Bake impact times from the FINAL timeline.json — regenerate after any beat retiming.
Output: assets/bgm.wav + assets/sfx_{click,toggle,whoosh,chime,notify,sweep,impact}.wav"""
import numpy as np, wave, os

# ------------------------- CONFIG -------------------------
SR = 44100
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
DUR = 150.0            # total film length (s)
BPM = 110
GAIN = 0.25            # BGM bake level; SFX/VO stay hot above this
# (start, end, pad_amp, bell_amp, bass_amp, drums) — anchor to beat boundaries
SECTIONS = [
    (0,   18,  .16, .10, 0,   False),  # intro: pads only
    (18,  46,  .20, .11, .10, True),   # build
    (46,  111, .24, .13, .13, True),   # main
    (111, 142, .26, .15, .14, True),   # peak
    (142, 150, .18, .10, .05, False),  # resolve
]
RISER_AT, IMPACT_AT = 107.0, 111.0
MONTAGE_CUTS = [127.95, 130.35, 132.75, 135.15, 137.55]  # from timeline.json
RESOLVE_AT = 142.5
# -----------------------------------------------------------

def note(n):
    names = {'C':-9,'C#':-8,'D':-7,'D#':-6,'E':-5,'F':-4,'F#':-3,'G':-2,'G#':-1,'A':0,'A#':1,'B':2}
    return 440.0 * 2 ** ((names[n[:-1]] + (int(n[-1]) - 4) * 12) / 12)

def env(n, a, r, sus=1.0):
    e = np.full(n, sus)
    na = min(int(a*SR), n); nr = min(int(r*SR), max(0, n - na))
    if na: e[:na] *= np.linspace(0, 1, na)
    if nr: e[n-nr:] *= np.linspace(1, 0, nr)
    return e

def write(path, L, R, gain=1.0):
    m = max(np.abs(L).max(), np.abs(R).max())
    L, R = L/m*0.72*gain, R/m*0.72*gain
    with wave.open(path, 'w') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        it = np.empty(len(L)*2, np.int16)
        it[0::2] = (L*32767).astype(np.int16); it[1::2] = (R*32767).astype(np.int16)
        w.writeframes(it.tobytes())

N = int(SR*DUR); mixL = np.zeros(N); mixR = np.zeros(N)
B = 60/BPM; BAR = 4*B

def put(sig, t, pan=0.0):
    i = int(t*SR); j = min(i+len(sig), N)
    if j <= i: return
    seg = sig[:j-i]
    mixL[i:j] += seg*np.cos((pan+1)*np.pi/4); mixR[i:j] += seg*np.sin((pan+1)*np.pi/4)

def pad(f, dur, amp):
    n = int(dur*SR)
    w = sum(np.sin(2*np.pi*f*k)*v for k, v in [(1,1),(2,.35),(3,.12)])
    return amp * w * env(n, 1.2, 1.5)

def bell(f, dur, amp):
    n = int(dur*SR); t = np.arange(n)/SR
    w = np.sin(2*np.pi*f*t) + .4*np.sin(2*np.pi*f*2.001*t) + .15*np.sin(2*np.pi*f*3.003*t)
    return amp * w * np.exp(-t*3.2)

def bass(f, dur, amp):
    n = int(dur*SR); t = np.arange(n)/SR
    return amp * (np.sin(2*np.pi*f*t) + .3*np.sin(2*np.pi*f*2*t)) * env(n, .01, .1)

def kick(amp):
    n = int(.22*SR); t = np.arange(n)/SR
    return amp*np.sin(2*np.pi*(140*np.exp(-t*22)+42)*t)*np.exp(-t*7)

def hat(amp, open_=False):
    n = int((.09 if open_ else .035)*SR)
    return amp*np.random.default_rng(7).uniform(-1,1,n)*np.exp(-np.arange(n)/SR*(22 if open_ else 60))

def clap(amp):
    n = int(.12*SR)
    return amp*np.random.default_rng(3).uniform(-1,1,n)*np.exp(-np.arange(n)/SR*28)

# C minor: Cm - Ab - Eb - Bb
PROG = [('C3',['C4','D#4','G4']), ('G#2',['C4','D#4','G4']),
        ('D#3',['D#4','G4','A#4']), ('A#2',['D#4','F4','A#4'])]
rng = np.random.default_rng(11)
for s, e, pa, ba, bba, drums in SECTIONS:
    t = s
    while t < e:
        root, chord = PROG[int(t/BAR) % 4]
        for cf in chord:
            put(pad(note(cf), min(BAR*1.1, e-t), pa), t, pan=0.12*(cf != chord[0]))
        if bba: put(bass(note(root), BAR*.95, bba), t)
        for k in range(4):
            if rng.random() < .4:
                put(bell(note(chord[int(rng.random()*len(chord))])*2, 1.4, ba),
                    t + k*B + rng.random()*.2, pan=rng.uniform(-.3,.3))
        if drums:
            for k in range(4):
                put(kick(.5), t+k*B)
                if k in (1,3): put(clap(.30), t+k*B)
                put(hat(.10), t+k*B+B/2)
                if k == 3: put(hat(.10, True), t+k*B+B*.9)
        t += BAR

n = int(4*SR); tt = np.arange(n)/SR
put(.22*rng.uniform(-1,1,n)*np.linspace(0,1,n)*np.sin(2*np.pi*tt*tt*150), RISER_AT)
put(.55*np.sin(2*np.pi*55*np.arange(int(1.2*SR))/SR)*np.exp(-np.arange(int(1.2*SR))/SR*3), IMPACT_AT)
for tm in MONTAGE_CUTS:
    put(.30*np.sin(2*np.pi*55*np.arange(int(.5*SR))/SR)*np.exp(-np.arange(int(.5*SR))/SR*5), tm)
for cf in ['C4','G4','C5']:
    put(bell(note(cf), 3.5, .14), RESOLVE_AT)
fadi, fado = int(1.2*SR), int(3.5*SR)
mixL[:fadi] *= np.linspace(0,1,fadi); mixR[:fadi] *= np.linspace(0,1,fadi)
mixL[-fado:] *= np.linspace(1,0,fado); mixR[-fado:] *= np.linspace(1,0,fado)
os.makedirs(OUT, exist_ok=True)
write(os.path.join(OUT, 'bgm.wav'), mixL, mixR, gain=GAIN)
print(f'bgm.wav {DUR}s')

# ---- SFX set ----
def sfx(name, sig):
    m = np.abs(sig).max()
    write(os.path.join(OUT, f'sfx_{name}.wav'), sig/m, sig/m)

n = int(.05*SR); t = np.arange(n)/SR
sfx('click', .8*np.sin(2*np.pi*1900*t)*np.exp(-t*90))
tog = np.zeros(int(.14*SR))
d1 = .7*np.sin(2*np.pi*1500*np.arange(int(.04*SR))/SR)*np.exp(-np.arange(int(.04*SR))/SR*70)
tog[:len(d1)] = d1
i2 = int(.07*SR)
d2 = .7*np.sin(2*np.pi*2100*np.arange(int(.04*SR))/SR)*np.exp(-np.arange(int(.04*SR))/SR*70)
tog[i2:i2+len(d2)] += d2
sfx('toggle', tog)
n = int(.45*SR)
w = np.random.default_rng(5).uniform(-1,1,n)*np.hanning(n)
sfx('whoosh', w*np.sin(2*np.pi*np.linspace(400,900,n)/SR*np.arange(n))*.9)
sig = np.zeros(int(1.3*SR))
for k, f in enumerate([note('C6'), note('E6'), note('G6')]):
    nn = int(.7*SR); t = np.arange(nn)/SR
    b = .5*np.sin(2*np.pi*f*t)*np.exp(-t*4)
    sig[int(k*.09*SR):int(k*.09*SR)+nn] += b
sfx('chime', sig)
sig = np.zeros(int(.8*SR))
for k, f in enumerate([note('G5'), note('C6')]):
    nn = int(.28*SR); t = np.arange(nn)/SR
    b = .6*np.sin(2*np.pi*f*t)*np.exp(-t*9)
    sig[int(k*.18*SR):int(k*.18*SR)+nn] += b
sfx('notify', sig)
n = int(.5*SR); t = np.arange(n)/SR
sfx('sweep', .5*np.sin(2*np.pi*(300+900*t/.5)*t)*np.hanning(n))
n = int(1.0*SR); t = np.arange(n)/SR
sfx('impact', .9*np.sin(2*np.pi*(90*np.exp(-t*10)+45)*t)*np.exp(-t*4))
print('sfx done')
