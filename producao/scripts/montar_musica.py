"""Monta o vídeo vertical da música 'Ninguém vem te salvar. Corre.' com clipes de corrida/treino e letra sincronizada."""
import json, os, re, subprocess, random
S='/tmp/claude-0/-home-user-forjados-podcast/c315f910-9fae-565f-ab58-91701e0ce6cf/scratchpad'
SCR='/home/user/forjados-podcast/producao/scripts'
import sys
CFG=json.load(open(sys.argv[1]))
W=CFG["build"]; os.makedirs(W,exist_ok=True)
MUS=CFG["musica"]; CL=S+'/musica_clips'; meta=json.load(open(CL+'/meta.json'))
DUR=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",MUS],capture_output=True,text=True).stdout)
L=[tuple(x) for x in CFG["legendas"]]
OUTRO=DUR-CFG.get('outro',4.0)
# estados de texto: (t0,t1,texto) ; texto None = sem legenda
est=[]; t=0.0
for i,(a,tx,f) in enumerate(L):
    if a>t+0.05: est.append((t,a,None))
    nxt=L[i+1][0] if i+1<len(L) else OUTRO
    fim=min(nxt, max(f+1.2, a+1.0))
    est.append((a,fim,tx)); t=fim
if t<OUTRO: est.append((t,OUTRO,None))
est.append((OUTRO,DUR,"__OUTRO__"))
# segmentos de vídeo: novo clipe a cada estado; estados longos sem texto são picados em ~1.8s (drops), com texto em ~3.5s
segs=[]
for a,b,tx in est:
    passo=1.8 if tx is None else 3.6
    n=max(1,round((b-a)/passo)) if tx!="__OUTRO__" else 1
    for j in range(n): segs.append([a+(b-a)*j/n, a+(b-a)*(j+1)/n, tx])
# pools de clipes por clima
calmo=["porta_luz","neblina","praia_sol1","praia_sol2","rochas_sol","praia_sol3","trilha_cerca","estrada","parque","trilha_pernas"]
forte=["maratona_pes","maratona_multidao","maratona_aerea","pes_claro","botas_marcha","flexao_praia","flexao_pb","boxer_rosto","boxe_saco","pneu","mar_rochas","ondas","escalada","soldado_areia","soldado_tatico","helicoptero","halter","prancha","trilha_pernas","trilha_cerca"]
random.seed(CFG.get('seed',7)); ult=[]; pos={k:0.0 for k in meta}
def escolhe(t,tx):
    pool = calmo if (t<CFG.get('calmo_ate',8) or t>=CFG.get('calmo_desde',DUR)) else forte
    if tx and re.search(CFG.get("regex_corrida",r"CORRE|corre|quilômetro|QUILÔMETRO|MAIS UM|MAIS RÁPIDO|APERTA"),tx): pool=["maratona_pes","maratona_multidao","pes_claro","trilha_pernas","trilha_cerca","praia_sol2","praia_sol3","parque","maratona_aerea"]
    c=[x for x in pool if x not in ult[-4:]] or pool
    k=random.choice(c); ult.append(k); return k
def png_de(tx,cred):
    d={"layer":"fg","img":None,"kicker":"","big":"","cap":"","credito":cred,"outro":False}
    if tx=="__OUTRO__": d.update(outro=True,cap_outro=CFG.get("outro_texto","Mantenha-se firme."))
    elif tx:
        if tx.isupper() or len(tx.split())<=3: d["big"]=re.sub(r"\*\*","",tx).upper()
        else: d["cap"]=re.sub(r"\*\*(.+?)\*\*",r'<span class="hl">\1</span>',tx)
    return d
frames=[]; F=[]
for i,s in enumerate(segs):
    k=escolhe(s[0],s[2]) if s[2]!="__OUTRO__" else "praia_sol2"
    s.append(k); cred=f"Vídeo: {meta[k]['user']} / Pixabay"
    png=f"{W}/t{i:03d}.png"; d=png_de(s[2],cred); d["out"]=png; frames.append(d)
json.dump(frames,open(W+'/frames.json','w'),ensure_ascii=False)
subprocess.run(["node",SCR+"/render_frames.js",W+'/frames.json',"frame2.html"],check=True,cwd=SCR)
# render dos segmentos com contagem de quadros acumulada (sem deriva)
fps=30; lista=open(W+'/v.txt','w')
for i,(a,b,tx,k) in enumerate(segs):
    fr=round(b*fps)-round(a*fps)
    if fr<=0: continue
    dur=meta[k]["dur"]; off=pos[k]%max(dur-1,1); pos[k]=off+fr/fps+0.5
    out=f"{W}/s{i:03d}.mp4"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-stream_loop","-1","-ss",f"{off:.2f}","-i",f"{CL}/{k}.mp4","-loop","1","-i",f"{W}/t{i:03d}.png","-filter_complex",
      "[0:v]fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,hue=s=0,eq=contrast=1.3:brightness=-0.08,setsar=1[b];[b][1:v]overlay=0:0:format=auto,format=yuv420p",
      "-an","-frames:v",str(fr),"-c:v","libx264","-preset","veryfast","-crf","21",out],check=True)
    lista.write(f"file '{out}'\n")
lista.close()
final=W+'/final.mp4'
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",W+'/v.txt',"-i",MUS,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final],check=True)
creds=sorted({f"Vídeo: {meta[s[3]]['user']} / Pixabay" for s in segs})
json.dump({"duracao":DUR,"creditos":creds,"segmentos":len(segs)},open(W+'/final.json','w'),ensure_ascii=False)
print("ok",final,len(segs),"segmentos")
