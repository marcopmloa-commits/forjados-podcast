"""Gera o MP3 de um episódio a partir do roteiro.md usando Piper (offline)."""
import re, subprocess, sys, wave, os, tempfile
roteiro, modelo, saida = sys.argv[1], sys.argv[2], sys.argv[3]
txt = open(roteiro, encoding="utf-8").read().split("### Fontes")[0]
blocos = []
for linha in txt.splitlines():
    l = linha.strip()
    if not l or l.startswith("#") or l.startswith("---") or l.startswith("**Formato") or l.startswith(">"):
        continue
    if re.fullmatch(r"\*\*\[.*\]\*\*", l):
        blocos.append(None)  # pausa longa entre blocos
        continue
    l = re.sub(r"[*_]", "", l)
    blocos.append(l)
tmp = tempfile.mkdtemp()
partes = []
sr = None
for i, b in enumerate(blocos):
    f = os.path.join(tmp, f"{i:03d}.wav")
    if b is None:
        partes.append(("pausa", 1.2)); continue
    subprocess.run([sys.executable, "-m", "piper", "-m", modelo, "-f", f, "--sentence-silence", "0.35", "--length-scale", "1.08"],
                   input=b.encode(), check=True, stderr=subprocess.DEVNULL)
    partes.append(("wav", f)); partes.append(("pausa", 0.5))
with wave.open(next(p for t, p in partes if t == "wav")) as w:
    params = w.getparams()
out = os.path.join(tmp, "voz.wav")
with wave.open(out, "wb") as o:
    o.setparams(params)
    for t, p in partes:
        if t == "pausa":
            o.writeframes(b"\x00\x00" * int(params.framerate * p))
        else:
            with wave.open(p) as w: o.writeframes(w.readframes(w.getnframes()))
print(out)
