#!/usr/bin/env python3
"""build_video.py SPEC.json [--out DIR]: slides (Pillow) + Kokoro voice + ffmpeg -> mp4, srt, narration txt."""
import json, os, re, subprocess, sys, tempfile, textwrap, urllib.request
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
BG, FG, AC, MU, CARD = (15, 23, 42), (241, 245, 249), (56, 189, 248), (148, 163, 184), (30, 41, 59)
YEL, GRN, RED = (250, 204, 21), (134, 239, 172), (248, 113, 113)
FD = "/usr/share/fonts/truetype/dejavu/"
F = lambda s, b=False: ImageFont.truetype(FD + ("DejaVuSans-Bold.ttf" if b else "DejaVuSans.ttf"), s)
M = lambda s: ImageFont.truetype(FD + "DejaVuSansMono.ttf", s)
REL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"

def models():
    d = os.environ.get("KOKORO_DIR", os.path.expanduser("~/.cache/kokoro")); os.makedirs(d, exist_ok=True)
    for f in ("kokoro-v1.0.onnx", "voices-v1.0.bin"):
        if not os.path.exists(os.path.join(d, f)):
            urllib.request.urlretrieve(REL + f, os.path.join(d, f))
    return os.path.join(d, "kokoro-v1.0.onnx"), os.path.join(d, "voices-v1.0.bin")

def tag(d, part):
    col = {"WHAT": YEL, "HOW": AC, "WHY": GRN}.get(part)
    if col:
        d.rounded_rectangle([1620, 60, 1820, 130], 14, fill=col)
        d.text((1720, 95), part, font=F(40, True), fill=BG, anchor="mm")

def slide(i, n, sl, footer):
    t, kind, c = sl["title"], sl["kind"], sl["content"]
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im); d.rectangle([0, 0, 18, H], fill=AC)
    if kind == "hook":
        d.text((120, 100), c["top"][0], font=F(70, True), fill=FG)
        d.text((120, 190), c["top"][1], font=F(70, True), fill=AC)
        cols = [("left", RED), ("mid", YEL), ("right", GRN)]
        cols = [(k, col) for k, col in cols if k in c]
        bw = 520 if len(cols) == 3 else 760
        gap = (1720 - bw * len(cols)) // max(1, len(cols) - 1) if len(cols) > 1 else 0
        for j, (k, col) in enumerate(cols):
            x = 100 + j * (bw + gap)
            d.rounded_rectangle([x, 380, x + bw, 700], 24, fill=CARD, outline=col, width=5)
            d.text((x + bw // 2, 520), c[k][0], font=F(88 if len(c[k][0]) < 9 else 64, True), fill=col, anchor="mm")
            d.text((x + bw // 2, 630), c[k][1], font=F(34), fill=MU, anchor="mm")
            if j < len(cols) - 1:
                ax = x + bw + gap // 2
                d.polygon([(ax - 25, 510), (ax + 25, 540), (ax - 25, 570)], fill=FG)
        d.text((120, 800), c["bottom"], font=F(44), fill=MU)
    else:
        d.text((100, 70), t, font=F(56, True), fill=FG); d.line([100, 150, 1820, 150], fill=AC, width=4)
        tag(d, t.split()[0])
        if kind == "bullets":
            y = 210
            for l in c:
                if l == "": y += 30; continue
                d.text((100, y), "●", font=F(30), fill=AC); d.text((150, y - 8), l, font=F(44), fill=FG); y += 86
        elif kind == "code":
            d.rounded_rectangle([100, 190, 1820, 1000], 16, fill=CARD)
            for k, l in enumerate(c): d.text((140, 225 + k * 70), l, font=M(36), fill=MU if l.startswith("#") else GRN)
        elif kind == "table":
            cw = [min(520, 1720 // len(c[0]))] * len(c[0]); cw[-1] = 1720 - sum(cw[:-1]); y = 200
            for r, row in enumerate(c):
                d.rectangle([100, y, 1820, y + 88], fill=AC if r == 0 else (CARD if r % 2 else BG)); x = 100
                for j, cell in enumerate(row):
                    d.text((x + 20, y + 24), cell, font=F(32, r == 0 or j == 0), fill=BG if r == 0 else FG); x += cw[j]
                y += 100
        elif kind == "bars":
            rh = min(165, 800 // len(c)); y = 185
            for lab, bt, ot, bv, ov, df in c:
                d.text((100, y), lab, font=F(34, True), fill=FG); d.text((1820, y), df, font=F(34, True), fill=GRN, anchor="ra")
                mx = 1100
                bwid = mx; owid = max(8, int(mx * ov / bv))
                d.rounded_rectangle([100, y + 52, 100 + bwid, y + 88], 6, fill=RED)
                d.text((100 + bwid + 20, y + 52), bt, font=F(30), fill=MU)
                d.rounded_rectangle([100, y + 96, 100 + owid, y + 132], 6, fill=GRN)
                d.text((100 + owid + 20, y + 96), ot, font=F(30, True), fill=GRN)
                y += rh
            d.rectangle([100, 1000, 118, 1010], fill=RED); d.text((130, 992), "baseline", font=F(24), fill=MU)
            d.rectangle([300, 1000, 318, 1010], fill=GRN); d.text((330, 992), "optimised", font=F(24), fill=MU)
        elif kind == "steps":
            rh = min(200, 800 // len(c)); y = 190
            for num, head, det, chip in c:
                d.rounded_rectangle([100, y, 1820, y + rh - 16], 18, fill=CARD)
                d.ellipse([130, y + rh // 2 - 46, 222, y + rh // 2 + 46], fill=AC)
                d.text((176, y + rh // 2 - 8), str(num), font=F(48, True), fill=BG, anchor="mm")
                d.text((260, y + 22), head, font=F(40, True), fill=FG)
                d.text((260, y + 82), det, font=F(30), fill=MU)
                if chip:
                    tw = d.textlength(chip, font=F(32, True))
                    d.rounded_rectangle([1790 - tw - 40, y + 28, 1790, y + 92], 14, fill=BG, outline=GRN, width=3)
                    d.text((1790 - tw - 20, y + 42), chip, font=F(32, True), fill=GRN)
                y += rh
    d.text((100, 1030), footer, font=F(24), fill=MU)
    d.text((1720, 1030), f"{i + 1} / {n}", font=F(24), fill=MU, anchor="ra")
    return im

def ts(x):
    return f"{int(x // 3600):02}:{int(x % 3600 // 60):02}:{int(x % 60):02},{int(x % 1 * 1000):03}"

def main():
    a = sys.argv[1:]
    spec = json.load(open(a[0])); out = a[a.index("--out") + 1] if "--out" in a else "video"
    os.makedirs(out, exist_ok=True); tmp = tempfile.mkdtemp()
    from kokoro_onnx import Kokoro
    k = Kokoro(*models()); S = spec["slides"]; parts, srt, t0 = [], [], 0.0
    for i, sl in enumerate(S):
        slide(i, len(S), sl, spec.get("footer", "")).save(f"{tmp}/s{i}.png")
        au, sr = k.create(sl["narration"], voice=spec.get("voice", "af_heart"), speed=spec.get("speed", 1.05), lang="en-us")
        au = np.concatenate([au, np.zeros(int(sr * 0.8), dtype=au.dtype)]); sf.write(f"{tmp}/a{i}.wav", au, sr)
        dur = len(au) / sr; sents = re.split(r"(?<=[.!?:])\s+", sl["narration"]); tot = sum(map(len, sents)); cur = t0
        for s in sents:
            dd = (dur - 0.8) * len(s) / tot; srt.append((cur, cur + dd, s)); cur += dd
        t0 += dur
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", f"{tmp}/s{i}.png", "-i", f"{tmp}/a{i}.wav",
                        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", "25", "-c:a", "aac", "-b:a", "192k",
                        "-shortest", f"{tmp}/p{i}.mp4"], check=True)
        parts.append(f"{tmp}/p{i}.mp4"); print("slide", i, round(dur, 1), "s", flush=True)
    open(f"{tmp}/l.txt", "w").write("".join(f"file '{p}'\n" for p in parts)); n = spec["name"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{tmp}/l.txt", "-c", "copy", f"{out}/{n}.mp4"], check=True)
    with open(f"{out}/{n}.srt", "w") as f:
        for j, (s, e, x) in enumerate(srt, 1): f.write(f"{j}\n{ts(s)} --> {ts(e)}\n{textwrap.fill(x, 70)}\n\n")
    open(f"{out}/narration_{n}.txt", "w").write("\n\n".join(f"[{s['title']}]\n{s['narration']}" for s in S))
    print("total", round(t0 / 60, 1), "min")

if __name__ == "__main__":
    main()
