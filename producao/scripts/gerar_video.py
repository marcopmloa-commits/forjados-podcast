"""Vídeo vertical com fotos reais. uso: python3 gerar_video.py video.json saida.mp4"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import tts_corrido, destaca, trilha, VOZ_VIDEO
from imagens import buscar, buscar_video
SCR = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(sys.argv[1], encoding="utf-8")); saida = os.path.abspath(sys.argv[2])
work = saida[:-4] + "_build"; os.makedirs(work, exist_ok=True)
voz = cfg.get("voz", VOZ_VIDEO)
frames, clips, creditos = [], [], []
n = 0
cenas = cfg["cenas"] + [{"outro": True, "falas": [cfg.get("fala_final", "Forjados. Episódios completos no Spotify. Siga para mais.")]}]
for i, c in enumerate(cenas):
    img, cred, clip, inteira = None, "", None, False
    if c.get("video"):
        r = buscar_video(c["video"], os.path.join(work, "vid"))
        if r: clip, cred = r["arquivo"], r["credito"]; creditos.append(cred)
    if c.get("img_url") and not clip:   # foto de arquivo achada via busca (endereço direto da imagem)
        try:
            from imagens import _get
            os.makedirs(os.path.join(work, "img"), exist_ok=True); arq = os.path.join(work, "img", f"url{i:02d}.jpg")
            open(arq, "wb").write(_get(c["img_url"], raw=True)); img = arq
            cred = c.get("credito", "Foto de arquivo"); creditos.append(cred); inteira = c.get("inteira", True)
        except Exception as e: print(f"[img_url] falhou: {e}", file=sys.stderr)
    if c.get("img") and not clip and not img:
        r = buscar(c["img"], os.path.join(work, "img"), 1, c.get("fonte", "auto"))
        if not r and c.get("img_reserva"): r = buscar(c["img_reserva"], os.path.join(work, "img"), 1, "pixabay")
        if r: img, cred = r[0]["arquivo"], r[0]["credito"]; creditos.append(cred)
        inteira = c.get("inteira", "Wikimedia" in cred)
    if c.get("outro") and not img:
        img = cfg.get("_ultima_img")
    bgpng = os.path.join(work, f"bg{i:02d}.png"); frames.append({"out": bgpng, "layer": "bg", "img": img, "inteira": inteira})
    for j, f in enumerate(c["falas"]):
        png = os.path.join(work, f"{n:03d}.png")
        frames.append({"out": png, "layer": "fg", "img": img, "kicker": c.get("kicker", ""), "big": c.get("big", ""),
                       "cap": "" if c.get("outro") else destaca(f), "credito": cred, "outro": bool(c.get("outro"))})
        clips.append({"fala": f, "png": png, "bg": bgpng, "clip": clip, "cena": i}); n += 1
    if img: cfg["_ultima_img"] = img
# narração contínua do roteiro inteiro (história contada, sem "ponto" entre frases)
vozwav = os.path.join(work, "voz.wav")
total, inicios = tts_corrido([c["fala"] for c in clips], vozwav, voz)
fim = total + 0.6
F = [round(t * 30) for t in inicios] + [round(fim * 30)]
for k, c in enumerate(clips):
    c["fr"] = max(F[k + 1] - F[k], 1); c["ini"] = F[k] / 30
for c in clips:   # tempo relativo dentro da cena (zoom/clipe contínuos)
    da_cena = [x for x in clips if x["cena"] == c["cena"]]
    c["t0"] = c["ini"] - da_cena[0]["ini"]; c["tcena"] = sum(x["fr"] for x in da_cena) / 30
json.dump(frames, open(os.path.join(work, "frames.json"), "w"))
subprocess.run(["node", os.path.join(SCR, "render_frames.js"), os.path.join(work, "frames.json"), "frame2.html"], check=True)
lv = open(os.path.join(work, "v.txt"), "w"); D = 0
for k, c in enumerate(clips):
    png, bgpng, clip, fr, t0, tcena = c["png"], c["bg"], c["clip"], c["fr"], c["t0"], c["tcena"]; D += fr / 30
    passo = 0.05 / max(tcena * 30, 1); z0 = 1.0 + passo * t0 * 30   # zoom contínuo na cena, máx. 5%
    mp4 = os.path.join(work, f"{k:03d}.mp4")
    if clip:  # fundo em vídeo: P&B, contraste, cortado em 9:16, continua do ponto da cena
        subprocess.run(["ffmpeg","-y","-loglevel","error","-stream_loop","-1","-ss",f"{t0:.2f}","-i",clip,"-loop","1","-i",png,"-filter_complex",
            "[0:v]fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,hue=s=0,eq=contrast=1.25:brightness=-0.09,setsar=1[b];"
            "[b][1:v]overlay=0:0:format=auto,format=yuv420p","-an",
            "-frames:v",str(fr),"-c:v","libx264","-preset","veryfast","-crf","21",mp4], check=True)
    else:
      subprocess.run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",bgpng,"-loop","1","-i",png,"-filter_complex",
        f"[0:v]scale=2160:3840,zoompan=z='{z0:.5f}+{passo:.7f}*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={fr}:s=1080x1920:fps=30[b];"
        f"[b][1:v]overlay=0:0:format=auto,format=yuv420p",
        "-frames:v",str(fr),"-c:v","libx264","-preset","veryfast","-crf","21",mp4], check=True)
    lv.write(f"file '{mp4}'\n")
lv.close()
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lv.name,"-c","copy",os.path.join(work,"v.mp4")], check=True)
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",vozwav,"-af",f"apad=whole_dur={D}",os.path.join(work,"voz_p.wav")], check=True)
vozwav = os.path.join(work, "voz_p.wav")
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",os.path.join(work,"v.mp4"),"-i",vozwav] + trilha(D+1) + [
  "-filter_complex","[1:a]aresample=44100,highpass=f=70,acompressor=threshold=-18dB:ratio=3[v];"
  "[2:a][3:a][4:a]amix=inputs=3,lowpass=f=300,aresample=44100,tremolo=f=1.1:d=0.5,volume=0.07[bg];"
  f"[v][bg]amix=inputs=2:duration=first:normalize=0,afade=t=out:st={D-1.5:.2f}:d=1.5,loudnorm=I=-14:TP=-1.5[a]",
  "-map","0:v","-map","[a]","-c:v","libx264","-preset","medium","-crf","24","-maxrate","1500k","-bufsize","3M","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-ar","44100","-shortest","-movflags","+faststart",saida], check=True)
json.dump({"duracao": round(D, 1), "creditos": sorted(set(creditos))}, open(saida[:-4] + ".json", "w"), ensure_ascii=False)
print(f"ok {saida} {D:.1f}s")
