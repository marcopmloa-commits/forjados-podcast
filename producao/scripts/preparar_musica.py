"""Corta o áudio, alinha a letra e escreve o cfg para montar_musica.py.
uso: python3 -I preparar_musica.py <pasta m_x com musica.mp3, letra.txt, transcricao.json> <cfg.json> '<json de opções>'
opções: cortes [[a,b],...], calmo_ate, calmo_desde, seed, regex_corrida, outro_texto, pool_calmo/pool_forte/pool_corrida, ajustes {linha:[ini,fim]}"""
import json, subprocess, sys, os
m, cfgp, op = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
AQUI = os.path.dirname(os.path.abspath(__file__))
cortes = op.pop("cortes"); aj = op.pop("ajustes", {})
fil = "".join(f"[0]atrim={a}:{b},asetpts=PTS-STARTPTS[p{i}];" for i, (a, b) in enumerate(cortes)); cur = "p0"
for i in range(1, len(cortes)): fil += f"[{cur}][p{i}]acrossfade=d=1:c1=tri:c2=tri[x{i}];"; cur = f"x{i}"
dur = sum(b - a for a, b in cortes) - (len(cortes) - 1)
fil += f"[{cur}]afade=t=out:st={dur-2:.2f}:d=2[o]"
subprocess.run(["ffmpeg","-loglevel","error","-y","-i",m+"/musica.mp3","-filter_complex",fil,"-map","[o]","-c:a","libmp3lame","-b:a","192k",m+"/corte.mp3"], check=True)
subprocess.run([sys.executable,"-I",AQUI+"/alinhar.py",m+"/transcricao.json",m+"/letra.txt",",".join(f"{a}:{b}" for a,b in cortes),m+"/linhas.json"], check=True, capture_output=True)
L = json.load(open(m + "/linhas.json"))
for r in L:
    if r[1] in aj: r[0], r[2] = aj[r[1]]
L.sort(key=lambda r: r[0]); leg = []
for a, t, f in L:
    w = t.split()
    if len(w) > 3 and not t.isupper(): t = " ".join(w[:-2]) + " **" + " ".join(w[-2:]) + "**"   # destaca o fim da frase
    leg.append([a, t, f])
cfg = dict(build=os.path.join(os.path.dirname(os.path.abspath(cfgp)), "build_" + os.path.basename(m).replace("m_", "")), musica=m + "/corte.mp3",
           legendas=leg, outro=max(1.8, dur - L[-1][2] - 0.4), **op)
json.dump(cfg, open(cfgp, "w"), ensure_ascii=False)
print(os.path.basename(m), round(dur, 1), "última fala", L[-1][2], "outro", round(cfg["outro"], 1))
for a,t,f in leg: print(f"  {a:6.1f} {t}")
