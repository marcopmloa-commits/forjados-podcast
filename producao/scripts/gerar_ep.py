"""Episódio de áudio. uso: python3 gerar_ep.py ep.json saida.mp3   (ep.json: {titulo, paragrafos:[...]} ; "" = pausa)"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import tts, trilha, VOZ_PADRAO
cfg = json.load(open(sys.argv[1], encoding="utf-8")); saida = os.path.abspath(sys.argv[2])
work = saida[:-4] + "_build"; os.makedirs(work, exist_ok=True)
lst = open(os.path.join(work, "a.txt"), "w"); D = 0
sil = os.path.join(work, "sil.wav")
for k, p in enumerate(cfg["paragrafos"]):
    if not p.strip():
        dur = 1.0
        subprocess.run(["ffmpeg","-y","-loglevel","error","-f","lavfi","-i","anullsrc=r=24000:cl=mono","-t","1.0",os.path.join(work,f"{k:03d}p.wav")],check=True)
    else:
        wav = os.path.join(work, f"{k:03d}.wav"); dur = tts(p, wav, cfg.get("voz", VOZ_PADRAO)) + 0.6
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",wav,"-af",f"apad=whole_dur={dur}","-ar","24000","-ac","1",os.path.join(work,f"{k:03d}p.wav")],check=True)
    lst.write(f"file '{os.path.join(work,f'{k:03d}p.wav')}'\n"); D += dur
lst.close()
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lst.name,os.path.join(work,"voz.wav")],check=True)
T = D + 7
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",os.path.join(work,"voz.wav")] + trilha(T) + [
  "-filter_complex","[0:a]aresample=44100,highpass=f=70,acompressor=threshold=-18dB:ratio=3,adelay=3500,apad=pad_dur=3.5[v];"
  "[1:a][2:a][3:a]amix=inputs=3,lowpass=f=300,volume=0.35,aresample=44100,tremolo=f=1.1:d=0.5[bed];"
  "[bed]volume='if(lt(t,4),1,0.1)':eval=frame,afade=t=in:d=1.5[bg];"
  f"[v][bg]amix=inputs=2:duration=first:normalize=0,afade=t=out:st={T-3:.2f}:d=3,loudnorm=I=-16:TP=-1.5",
  "-ac","1","-ar","44100","-b:a","96k","-id3v2_version","3","-metadata",f"title={cfg['titulo']}","-metadata","artist=Forjados","-metadata","album=Forjados",saida],check=True)
r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",saida],capture_output=True,text=True)
print(f"ok {saida} {float(r.stdout):.1f}s")
