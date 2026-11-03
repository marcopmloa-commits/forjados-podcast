"""Gera vídeo vertical 1080x1920 a partir de cenas.json (narração Piper + quadros + legendas)."""
import json, subprocess, sys, wave, os, re
cenas_path, modelo, saida = sys.argv[1:4]
base = os.path.dirname(os.path.abspath(cenas_path)); work = os.path.join(base, "_build"); os.makedirs(work, exist_ok=True)
SCR = os.path.dirname(os.path.abspath(__file__))
LEG = [("cento e trinta e cinco quilos","135 kg"),("quarenta e oito quilos","48 kg"),("três meses","3 meses"),
       ("cento e sessenta quilômetros","160 km"),("quatro mil e trinta","4.030"),("dezessete horas","17 horas"),
       ("quarenta por cento","40%"),("dois mil e um","2001"),("três Hell Weeks","3 Hell Weeks")]
HL = ["135 kg","48 kg","3 meses","160 km","4.030","17 horas","40%","2001","3 Hell Weeks","Navy SEAL","Ranger","buraco no coração","Ninguém vem te salvar","Forjados","espelho"]
def legenda(t):
    for a,b in LEG: t = t.replace(a,b)
    t = t.replace(", e ", " e ").replace("espelho,", "espelho")
    for h in HL: t = re.sub(re.escape(h), f'<span class="hl">{h}</span>', t, count=1)
    return t
cenas = json.load(open(cenas_path, encoding="utf-8")); hues=[18,8,0,28,22,12,30,20,16,6,22]
frames, clips = [], []
n = 0
for i, c in enumerate(cenas):
    for j, f in enumerate(c["falas"]):
        wav = os.path.join(work, f"{n:03d}.wav"); png = os.path.join(work, f"{n:03d}.png")
        subprocess.run([sys.executable,"-m","piper","-m",modelo,"-f",wav,"--length-scale","1.0","--sentence-silence","0.25"],
                       input=f.encode(), check=True, stderr=subprocess.DEVNULL)
        with wave.open(wav) as w: dur = w.getnframes()/w.getframerate()
        dur += 0.35 if j < len(c["falas"])-1 else 0.6
        frames.append({"out":png,"kicker":c["kicker"],"big":c["big"],"cap":"" if c.get("outro") else legenda(f),
                       "hue":hues[i%len(hues)],"seed":i+1,"outro":bool(c.get("outro"))})
        clips.append((wav, png, dur, j==0)); n += 1
json.dump(frames, open(os.path.join(work,"frames.json"),"w"))
subprocess.run(["node", os.path.join(SCR,"render_frames.js"), os.path.join(work,"frames.json")], check=True)
# vídeo: cada quadro com zoom lento; áudio: falas + pausas
lst = open(os.path.join(work,"v.txt"),"w"); alst = open(os.path.join(work,"a.txt"),"w")
for k,(wav,png,dur,first) in enumerate(clips):
    mp4 = os.path.join(work,f"{k:03d}.mp4"); fr = int(dur*30)
    subprocess.run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",png,"-vf",
      f"scale=1296:2304,zoompan=z='min(1.0+0.0006*on,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={fr}:s=1080x1920:fps=30,format=yuv420p",
      "-frames:v",str(fr),"-c:v","libx264","-preset","veryfast","-crf","20",mp4],check=True)
    lst.write(f"file '{mp4}'\n")
    pad = os.path.join(work,f"{k:03d}p.wav")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",wav,"-af",f"apad=whole_dur={fr/30}","-ar","22050","-ac","1",pad],check=True)
    alst.write(f"file '{pad}'\n")
lst.close(); alst.close()
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lst.name,"-c","copy",os.path.join(work,"v.mp4")],check=True)
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",alst.name,os.path.join(work,"voz.wav")],check=True)
D = sum(int(c[2]*30)/30 for c in clips)
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",os.path.join(work,"v.mp4"),"-i",os.path.join(work,"voz.wav"),
  "-f","lavfi","-i",f"sine=f=55:d={D+1}","-f","lavfi","-i",f"sine=f=82.4:d={D+1}","-f","lavfi","-i",f"anoisesrc=c=brown:a=0.02:d={D+1}",
  "-filter_complex","[1:a]aresample=44100,highpass=f=70,acompressor=threshold=-18dB:ratio=3[v];"
  "[2:a][3:a][4:a]amix=inputs=3,lowpass=f=300,aresample=44100,tremolo=f=1.1:d=0.5,volume=0.06[bg];"
  f"[v][bg]amix=inputs=2:duration=first:normalize=0,afade=t=out:st={D-1.5}:d=1.5,loudnorm=I=-14:TP=-1.5[a]",
  "-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","160k","-ar","44100","-shortest","-movflags","+faststart",saida],check=True)
print("duração", round(D,1))
