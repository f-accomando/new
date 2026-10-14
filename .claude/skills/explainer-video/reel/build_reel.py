#!/usr/bin/env python3
"""build_reel.py [--out DIR] [--preview t1,t2,...]: 9:16 animated Reel (canvas animation + Kokoro voice + synth SFX).
Stages: voice -> timeline.json -> sfx/music mix -> frames (Chromium) -> mp4. Needs: playwright, kokoro-onnx, soundfile, numpy, ffmpeg."""
import base64, json, os, re, subprocess, sys, tempfile
import numpy as np, soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
SR, FPS, GAP, LEAD = 24000, 30, 0.22, 0.2
VOICE, SPEED = "af_heart", 1.05

# id, spoken text, caption (word{spoken_chars} overrides timing weight), tail pad (s)
SEGS = [
 ("A1", "Same task. One run read one hundred seven thousand tokens, and locked the session.", "Same task. One run read 107,103{26} tokens, and locked the session.", 0.0),
 ("A2", "The other read four hundred and four.", "The other read 404{21}.", 0.9),
 ("B1", "Here's the trick. The expensive model only thinks.", "Here's the trick. The expensive model only thinks.", 0.0),
 ("B2", "The cheap one does the typing.", "The cheap one does the typing.", 0.5),
 ("C1", "First, a gate. Five questions. Any no, and a planner writes the order.", "First, a gate. Five questions. Any NO, and a planner writes the order.", 0.3),
 ("C2", "Then one grep. Sixteen lines, not ten thousand thirty nine.", "Then one grep. 16{7} lines, not 10,039{22}.", 0.4),
 ("C3", "The planner writes a seventy six token Work Order.", "The planner writes a 76{10} token Work Order.", 0.4),
 ("C4", "A cheap agent runs the audit, and says: done.", "A cheap agent runs the audit, and says: DONE.", 1.2),
 ("D1", "Ninety nine point six percent less input.", "99.6%{26} less input.", 0.3),
 ("D2", "Eighty three point four percent less output.", "83.4%{29} less output.", 0.3),
 ("D3", "Seven times faster.", "7x{5} faster.", 0.8),
 ("E1", "And the estimate? It said ninety to a hundred output tokens.", "And the estimate? It said 90-100{21} output tokens.", 0.3),
 ("E2", "Measured: ninety six.", "Measured: 96{10}.", 2.4),
 ("F1", "One real task, so measure yours.", "One real task, so measure yours.", 0.3),
 ("F2", "Gate it. Grep it. Order it.", "Gate it. Grep it. Order it.", 2.2),
]

def words(cap, s, e):
    toks = []
    for t in cap.split():
        m = re.match(r"^(.*?)(?:\{(\d+)\})?([.,?:!]*)$", t); txt, w, p = m.groups()
        pause = sum({".": 7, "?": 7, "!": 7, ":": 5, ",": 3}.get(c, 0) for c in p)
        toks.append([txt + p, int(w) if w else max(2, len(txt)), pause])
    tot = sum(w + p for _, w, p in toks); cur = s; out = []
    for txt, w, p in toks:
        d = (e - s) * w / tot; out.append({"w": txt, "s": cur, "e": cur + d}); cur += d + (e - s) * p / tot
    for i in range(len(out) - 1): out[i]["e"] = out[i + 1]["s"]
    return out

def voice(tmp):
    from kokoro_onnx import Kokoro
    d = os.environ.get("KOKORO_DIR", os.path.expanduser("~/.cache/kokoro"))
    k = Kokoro(f"{d}/kokoro-v1.0.onnx", f"{d}/voices-v1.0.bin")
    audio = [np.zeros(int(LEAD * SR), dtype=np.float32)]; t = LEAD; tl = {}
    for sid, spoken, cap, tail in SEGS:
        a, sr = k.create(spoken, voice=VOICE, speed=SPEED, lang="en-us"); assert sr == SR
        nz = np.where(np.abs(a) > 0.01)[0]; a = a[nz[0]:nz[-1] + 1] if len(nz) else a
        dur = len(a) / SR; tl[sid] = {"s": t, "e": t + dur, "tail": tail, "words": words(cap, t, t + dur)}
        audio += [a.astype(np.float32), np.zeros(int((GAP + tail) * SR), dtype=np.float32)]; t += dur + GAP + tail
    v = np.concatenate(audio); return v, tl, len(v) / SR

# ---------- synth sound design ----------
def env(n, a=0.005, d=0.1):
    x = np.arange(n) / SR; return np.minimum(1, x / a) * np.exp(-x / d)
def put(buf, t, snd, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(snd))
    if i < len(buf): buf[i:j] += snd[:j - i] * g
rng = np.random.default_rng(7)
def pop(f=650): n = int(.12 * SR); x = np.arange(n) / SR; return np.sin(2 * np.pi * (f * (1 + 4 * x)) * x) * env(n, .003, .04)
def tick(f=2200): n = int(.03 * SR); x = np.arange(n) / SR; return np.sin(2 * np.pi * f * x) * env(n, .001, .008)
def key(): n = int(.02 * SR); return rng.standard_normal(n) * env(n, .0005, .004) * rng.uniform(.4, 1)
def ding(f=880): n = int(1.4 * SR); x = np.arange(n) / SR; return (np.sin(2 * np.pi * f * x) + .5 * np.sin(2 * np.pi * f * 1.5 * x) + .25 * np.sin(2 * np.pi * f * 2 * x)) * env(n, .003, .45)
def boom(): n = int(.9 * SR); x = np.arange(n) / SR; return (np.sin(2 * np.pi * 55 * x * (1 + .4 * np.exp(-x * 8))) * 1.1 + rng.standard_normal(n) * .35 * np.exp(-x * 40)) * env(n, .001, .28)
def shatter(): n = int(.5 * SR); r = rng.standard_normal(n); r = np.diff(r, prepend=0); return r * env(n, .001, .12) * .7
def riser(dur):
    n = int(dur * SR); x = np.arange(n) / SR; p = x / dur
    ph = 2 * np.pi * np.cumsum(120 + 1500 * p ** 2) / SR; nz = rng.standard_normal(n) * .25
    return (np.sin(ph) * .5 + nz * p) * (p ** 1.5)
def whoosh(dur=.5):
    n = int(dur * SR); x = np.arange(n) / SR; p = x / dur; r = rng.standard_normal(n)
    k = 40; r = np.convolve(r, np.ones(k) / k, "same"); return r * np.sin(np.pi * p) * 1.4
def sparkle(): return np.concatenate([np.pad(ding(f) * .3, (0, 0))[:int(.18 * SR)] for f in (1320, 1760, 2200)])

def music(total):
    n = int(total * SR); x = np.arange(n) / SR; m = np.zeros(n)
    chords = [(220, 261.6, 329.6), (174.6, 220, 261.6), (261.6, 329.6, 392), (196, 246.9, 293.7)]
    for i, ch in enumerate(chords * 6):
        s, e = int(i * 4 * SR), int(min(n, (i + 1) * 4 * SR))
        if s >= n: break
        t = x[s:e] - x[s]; w = np.minimum(1, t / .8) * np.minimum(1, (4 - t) / .8)
        for f in ch: m[s:e] += np.sin(2 * np.pi * f * t) * w * .12 + np.sin(2 * np.pi * f * 2.003 * t) * w * .03
    m += np.sin(2 * np.pi * 55 * x) * .08 * (.6 + .4 * np.sin(2 * np.pi * x / 4))
    beat = 60 / 112
    for b in np.arange(0.5, total, beat): put(m, b, np.sin(2 * np.pi * 50 * (np.arange(int(.18 * SR)) / SR)) * env(int(.18 * SR), .002, .06), .5)
    return m

def events(tl):
    A1, A2, B1, B2, C1, C2, C3, C4, D1, D2, D3, E1, E2, F1, F2 = (tl[k] for k in [s[0] for s in SEGS])
    d = lambda S: S["e"] - S["s"]
    EV = {
     "cntS": A1["s"] + .15, "cntE": A1["e"] - .55, "lock": A1["e"] - .55, "pivot": A2["s"] + .02, "pop404": A2["s"] + .5,
     "b1": B1["s"], "think": B1["s"] + 1.1, "card": B1["e"] - .3, "type": B2["s"] + .25,
     "n1": C1["s"] + .05, "chk": [C1["s"] + d(C1) * (.30 + .08 * k) for k in range(5)], "anyno": C1["s"] + d(C1) * .78,
     "n2": C2["s"] + .05, "n2v": C2["s"] + d(C2) * .30, "n2x": C2["s"] + d(C2) * .62,
     "n3": C3["s"] + .05, "n3t": C3["s"] + d(C3) * .35, "n3c": C3["s"] + d(C3) * .70,
     "n4": C4["s"] + .05, "n4v": C4["s"] + d(C4) * .40, "n5": C4["s"] + d(C4) * .85,
     "d1": D1["s"], "d2": D2["s"], "d3": D3["s"],
     "e1": E1["s"] + .1, "e2": E2["s"] + .3, "rows": [E2["s"] + 1.0, E2["s"] + 1.45, E2["s"] + 1.9], "verdict": E2["s"] + 2.3,
     "f": [F2["s"] + d(F2) * f for f in (-.05, .30, .62)], "end": F2["e"] + F2["tail"],
    }
    return EV

def mix(voice_a, tl, EV, total):
    sfx = np.zeros(len(voice_a))
    put(sfx, EV["cntS"], riser(EV["lock"] - EV["cntS"]), .5); put(sfx, EV["lock"], boom(), .9)
    put(sfx, EV["pivot"], shatter(), .8); put(sfx, EV["pop404"], pop(520), .7); put(sfx, EV["pop404"] + .05, ding(1046), .35)
    put(sfx, EV["b1"] - .05, whoosh(.45), .35); put(sfx, EV["card"], whoosh(.5), .4)
    for i in range(14): put(sfx, EV["type"] + i * .085, key(), .5)
    for k, n in enumerate(["n1", "n2", "n3", "n4"]): put(sfx, EV[n], pop(500 + 90 * k), .6)
    for c in EV["chk"]: put(sfx, c, tick(), .7)
    put(sfx, EV["anyno"], pop(300), .5)
    for i in range(10): put(sfx, EV["n3t"] + i * .07, key(), .4)
    put(sfx, EV["n5"], ding(880), .6); put(sfx, EV["n5"] + .02, sparkle(), .5)
    for k in ("d1", "d2", "d3"): put(sfx, EV[k] + .05, whoosh(.5), .35); put(sfx, EV[k] + .8, pop(700), .35)
    put(sfx, EV["e2"], pop(400), .6); put(sfx, EV["e2"] + .1, sparkle(), .5)
    for r in EV["rows"]: put(sfx, r, pop(600), .5)
    put(sfx, EV["verdict"], ding(660), .4)
    for f in EV["f"]: put(sfx, f, boom() * .7, .6)
    mus = music(total)[:len(voice_a)] if len(voice_a) <= int(total * SR) else np.pad(music(total), (0, len(voice_a) - int(total * SR)))
    mus = mus[:len(voice_a)] * (0.55 - 0.3 * (np.convolve(np.abs(voice_a), np.ones(int(.25 * SR)) / int(.25 * SR), "same") > .02))
    vo = voice_a / max(.01, np.abs(voice_a).max()) * .85
    out = vo + sfx * .55 + mus * .55
    fade = np.minimum(1, (len(out) - np.arange(len(out))) / (SR * .8)); out = np.tanh(out * 1.1) * fade
    return out.astype(np.float32)

def render(tl, EV, total, outdir, preview=None):
    from playwright.sync_api import sync_playwright
    html = open(os.path.join(HERE, "reel.html")).read().replace("/*DATA*/", f"const TL={json.dumps(tl)};const EV={json.dumps(EV)};const SEGIDS={json.dumps([s[0] for s in SEGS])};")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or next((c for c in ("/opt/pw-browsers/chromium", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome") if os.path.isfile(c)), None), args=["--no-sandbox"]); pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        pg.set_content(html); pg.wait_for_function("window.ready===true")
        grab = lambda t: base64.b64decode(pg.evaluate(f"(()=>{{draw({t});return document.getElementById('c').toDataURL('image/jpeg',0.93).split(',')[1]}})()"))
        if preview:
            for t in preview: open(f"{outdir}/preview_{t:05.1f}.jpg", "wb").write(grab(t))
            b.close(); return None
        n = int(total * FPS); ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
            "-i", f"{outdir}/_mix.wav", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", "-shortest", f"{outdir}/scaffold_reel.mp4"], stdin=subprocess.PIPE)
        for f in range(n):
            ff.stdin.write(grab(f / FPS))
            if f % 150 == 0: print("frame", f, "/", n, flush=True)
        ff.stdin.close(); ff.wait(); b.close()

def main():
    a = sys.argv[1:]; out = a[a.index("--out") + 1] if "--out" in a else "video"; os.makedirs(out, exist_ok=True)
    cache = f"{out}/_reel_cache.npz"
    vf, tf = f"{out}/_voice.wav", f"{out}/_voice_tl.json"
    if os.path.exists(vf) and os.path.exists(tf) and "--regen" not in a:
        v = sf.read(vf, dtype="float32")[0]; tl = json.load(open(tf)); total = len(v) / SR
    else:
        v, tl, total = voice(out); sf.write(vf, v, SR); json.dump(tl, open(tf, "w"))
    EV = events(tl); total += 0.3
    json.dump({"tl": tl, "ev": EV, "total": total}, open(f"{out}/_reel_timeline.json", "w"), indent=1)
    m = mix(np.pad(v, (0, int(.3 * SR))), tl, EV, total); sf.write(f"{out}/_mix.wav", m, SR)
    pv = [float(x) for x in a[a.index("--preview") + 1].split(",")] if "--preview" in a else None
    render(tl, EV, total, out, pv); print("total", round(total, 1), "s")

if __name__ == "__main__":
    main()
