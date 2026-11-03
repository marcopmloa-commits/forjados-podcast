"""Vídeo vertical com fotos reais. uso: python3 gerar_video.py video.json saida.mp4"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import tts, destaca, trilha, VOZ_VIDEO
from imagens import buscar
SCR = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(sys.argv[1], encoding="utf-8")); saida = os.path.abspath(sys.argv[2])
work = saida[:-4] + "_build"; os.makedirs(work, exist_ok=True)
voz = cfg.get("voz", VOZ_VIDEO)
frames, clips, creditos = [], [], []
n = 0
cenas = cfg["cenas"] + [{"outro": True, "falas": [cfg.get("fala_final", "Forjados. Episódios completos no Spotify. Siga para mais.")]}]
for i, c in enumerate(cenas):
    img, cred = None, ""
    if c.get("img"):
        r = buscar(c["img"], os.path.join(work, "img"), 1, c.get("fonte", "auto"))
        if r: img, cred = r[0]["arquivo"], r[0]["credito"]; creditos.append(cred)
    if c.get("outro") and not img:
        img = cfg.get("_ultima_img")
    bgpng = os.path.join(work, f"bg{i:02d}.png"); frames.append({"out": bgpng, "layer": "bg", "img": img})
    t_cena = 0.0; ini = len(clips)
    for j, f in enumerate(c["falas"]):
        wav = os.path.join(work, f"{n:03d}.wav"); png = os.path.join(work, f"{n:03d}.png")
        dur = tts(f, wav, voz) + (0.12 if j < len(c["falas"]) - 1 else 0.3)
        frames.append({"out": png, "layer": "fg", "img": img, "kicker": c.get("kicker", ""), "big": c.get("big", ""),
                       "cap": "" if c.get("outro") else destaca(f), "credito": cred, "outro": bool(c.get("outro"))})
        clips.append([wav, png, dur, t_cena, bgpng, 0]); t_cena += dur; n += 1
    for cl in clips[ini:]: cl[5] = t_cena
    if img: cfg["_ultima_img"] = img
json.dump(frames, open(os.path.join(work, "frames.json"), "w"))
subprocess.run(["node", os.path.join(SCR, "render_frames.js"), os.path.join(work, "frames.json"), "frame2.html"], check=True)
lv = open(os.path.join(work, "v.txt"), "w"); la = open(os.path.join(work, "a.txt"), "w"); D = 0
for k, (wav, png, dur, t0, bgpng, tcena) in enumerate(clips):
    fr = int(dur * 30); D += fr / 30
    passo = 0.05 / max(tcena * 30, 1); z0 = 1.0 + passo * t0 * 30   # zoom contínuo na cena, máx. 5%
    mp4 = os.path.join(work, f"{k:03d}.mp4")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",bgpng,"-loop","1","-i",png,"-filter_complex",
        f"[0:v]scale=2160:3840,zoompan=z='{z0:.5f}+{passo:.7f}*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={fr}:s=1080x1920:fps=30[b];"
        f"[b][1:v]overlay=0:0:format=auto,format=yuv420p",
        "-frames:v",str(fr),"-c:v","libx264","-preset","veryfast","-crf","21",mp4], check=True)
    pad = os.path.join(work, f"{k:03d}p.wav")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",wav,"-af",f"apad=whole_dur={fr/30}","-ar","24000","-ac","1",pad], check=True)
    lv.write(f"file '{mp4}'\n"); la.write(f"file '{pad}'\n")
lv.close(); la.close()
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lv.name,"-c","copy",os.path.join(work,"v.mp4")], check=True)
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",la.name,os.path.join(work,"voz.wav")], check=True)
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",os.path.join(work,"v.mp4"),"-i",os.path.join(work,"voz.wav")] + trilha(D+1) + [
  "-filter_complex","[1:a]aresample=44100,highpass=f=70,acompressor=threshold=-18dB:ratio=3[v];"
  "[2:a][3:a][4:a]amix=inputs=3,lowpass=f=300,aresample=44100,tremolo=f=1.1:d=0.5,volume=0.07[bg];"
  f"[v][bg]amix=inputs=2:duration=first:normalize=0,afade=t=out:st={D-1.5:.2f}:d=1.5,loudnorm=I=-14:TP=-1.5[a]",
  "-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","160k","-ar","44100","-shortest","-movflags","+faststart",saida], check=True)
json.dump({"duracao": round(D, 1), "creditos": sorted(set(creditos))}, open(saida[:-4] + ".json", "w"), ensure_ascii=False)
print(f"ok {saida} {D:.1f}s")
