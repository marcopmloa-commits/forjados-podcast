"""Gera e publica o pacote do dia.
uso: python3 publicar_dia.py producao/diario/AAAA-MM-DD
A pasta deve ter audios/a1..a5.json ({titulo, descricao, paragrafos}) e videos/v1..v5.json ({titulo, legenda_post, cenas})."""
import json, os, subprocess, sys, glob, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_site as S
SCR = os.path.dirname(os.path.abspath(__file__)); REPO = "marcopmloa-commits/forjados-podcast"
pasta = os.path.abspath(sys.argv[1]); dia = os.path.basename(pasta); tag = f"dia-{dia}"
out = os.path.join(pasta, "saida"); os.makedirs(out, exist_ok=True)
audios = sorted(glob.glob(os.path.join(pasta, "audios", "*.json"))); videos = sorted(glob.glob(os.path.join(pasta, "videos", "*.json")))
for a in audios:
    mp3 = os.path.join(out, os.path.basename(a)[:-5] + ".mp3")
    if not os.path.exists(mp3): subprocess.run([sys.executable, os.path.join(SCR, "gerar_ep.py"), a, mp3], check=True)
legendas = []
for v in videos:
    mp4 = os.path.join(out, os.path.basename(v)[:-5] + ".mp4")
    if not os.path.exists(mp4): subprocess.run([sys.executable, os.path.join(SCR, "gerar_video.py"), v, mp4], check=True)
    cfg = json.load(open(v, encoding="utf-8")); meta = json.load(open(mp4[:-4] + ".json", encoding="utf-8"))
    legendas.append(f"=== {os.path.basename(mp4)} — {cfg['titulo']} ({meta['duracao']:.0f}s) ===\n{cfg['legenda_post']}\n\nCréditos das fotos: {'; '.join(meta['creditos'])}\n")
open(os.path.join(out, "legendas-tiktok.txt"), "w", encoding="utf-8").write("\n".join(legendas))
# vídeos -> branch "tiktok": só o dia atual; um commit/push por vídeo (envios grandes demais falham no proxy)
RAIZ = S.RAIZ
tk = os.path.join(out, "_tiktok"); subprocess.run(["rm", "-rf", tk]); os.makedirs(os.path.join(tk, dia))
url = subprocess.run(["git", "-C", RAIZ, "remote", "get-url", "origin"], capture_output=True, text=True).stdout.strip()
uid = subprocess.run(["gh", "api", "user", "--jq", ".id"], capture_output=True, text=True).stdout.strip()
autor = ["-c", "user.name=marcopmloa-commits", "-c", f"user.email={uid}+marcopmloa-commits@users.noreply.github.com"]
def git(*a, **k): return subprocess.run(["git", "-C", tk] + list(a), **k)
def enviar(forcar=False):
    for t in range(4):
        if git("push", "-q", *(["-f"] if forcar else []), url, "tiktok").returncode == 0: return
        print(f"[tiktok] push falhou, tentativa {t+1}", file=sys.stderr); subprocess.run(["sleep", str(5 * (t + 1))])
    raise RuntimeError("push do branch tiktok falhou")
git("init", "-q", "-b", "tiktok", check=True)
open(os.path.join(tk, "README.md"), "w").write(f"# Vídeos do TikTok — Forjados\n\nPasta `{dia}`: abra o vídeo e toque em *Download raw file*. Texto dos posts em `legendas-tiktok.txt`.\n")
subprocess.run(["cp", os.path.join(out, "legendas-tiktok.txt"), os.path.join(tk, dia)], check=True)
git("add", "-A", check=True); git(*autor, "commit", "-q", "-m", f"TikTok {dia}: legendas", check=True); enviar(forcar=True)
for f in sorted(glob.glob(os.path.join(out, "*.mp4"))):
    subprocess.run(["cp", f, os.path.join(tk, dia)], check=True)
    git("add", "-A", check=True); git(*autor, "commit", "-q", "-m", f"TikTok {dia}: {os.path.basename(f)}", check=True); enviar()
# áudios -> site (64 kbps)
os.makedirs(os.path.join(RAIZ, "episodios"), exist_ok=True)
for a in audios:
    nome = os.path.basename(a)[:-5]; src = os.path.join(out, nome + ".mp3"); dst = os.path.join(RAIZ, "episodios", f"{dia}-{nome}.mp3")
    if not os.path.exists(dst):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-ac", "1", "-b:a", "64k", "-map_metadata", "0", "-id3v2_version", "3", dst], check=True)
# feed + site
eps = [e for e in S.carregar() if not e["id"].startswith(f"forjados-{dia}-")]
for i, a in enumerate(audios):
    cfg = json.load(open(a, encoding="utf-8")); nome = os.path.basename(a)[:-5] + ".mp3"; mp3 = os.path.join(RAIZ, "episodios", f"{dia}-{nome}")
    dur = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",mp3],capture_output=True,text=True).stdout)
    hora = datetime.datetime.fromisoformat(f"{dia}T08:00:00+00:00") + datetime.timedelta(minutes=i)
    eps.append({"id": f"forjados-{dia}-{nome[:-4]}", "titulo": cfg["titulo"], "descricao": cfg["descricao"],
        "url": S.BASE + f"episodios/{dia}-{nome}", "bytes": os.path.getsize(mp3), "dur": dur,
        "data": hora.isoformat(), "transcricao": [p for p in cfg["paragrafos"] if p.strip()]})
S.salvar(eps); S.gerar()
print(f"publicado. vídeos: https://github.com/{REPO}/tree/tiktok/{dia}")
