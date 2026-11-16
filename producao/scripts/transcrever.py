import sys, json
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
import subprocess, numpy as np
raw=subprocess.run(["ffmpeg","-loglevel","error","-i",sys.argv[1],"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True,check=True).stdout
audio=np.frombuffer(raw,dtype=np.float32)
segs, info = m.transcribe(audio, language="pt", word_timestamps=True, vad_filter=False)
out=[]
for s in segs:
    out.append({"ini":round(s.start,2),"fim":round(s.end,2),"texto":s.text.strip(),"palavras":[(round(w.start,2),round(w.end,2),w.word.strip()) for w in s.words]})
    print(f"{s.start:6.1f}-{s.end:6.1f} {s.text.strip()}", flush=True)
json.dump(out,open(sys.argv[2],"w"),ensure_ascii=False,indent=1)
