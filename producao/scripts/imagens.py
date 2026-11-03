"""Busca e baixa fotos reais (Pixabay; Wikimedia Commons como reserva).
uso: python3 imagens.py "consulta em ingles" pasta_saida [n]  -> imprime JSON [{arquivo, credito}]"""
import json, os, sys, urllib.request, urllib.parse, ssl, random
UA = "ForjadosPodcast/1.0 (https://marcopmloa-commits.github.io/forjados-podcast/)"
def _get(url, raw=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        d = r.read()
    return d if raw else json.loads(d)
def chave():
    k = os.environ.get("PIXABAY_KEY")
    if not k:
        p = os.path.expanduser("~/.pixabay_key")
        if os.path.exists(p): k = open(p).read().strip()
    return k
def pixabay(q, n):
    k = chave()
    if not k: return []
    url = "https://pixabay.com/api/?" + urllib.parse.urlencode({"key": k, "q": q, "image_type": "photo", "per_page": 30, "safesearch": "true", "min_height": 1200})
    hits = _get(url).get("hits", [])
    # prefere retrato/alta resolução, varia a escolha
    ruim = {"skating","skater","dance","dancer","ballet","anatomy","toy","toys","cartoon","illustration","figurine","nutcracker","lego","doll","miniature","game","render","3d","drawing","costume","roman","fantasy","anime","saxophone","music"}
    pal = [w for w in q.lower().split() if len(w) > 2]
    def nota(h):
        tags = h["tags"].lower().replace(",", " ").split()
        if any(b in tags for b in ruim): return -1
        return sum(w in " ".join(tags) for w in pal)
    hits = [h for h in hits if nota(h) >= 0]
    melhor = max((nota(h) for h in hits), default=0)
    top = [h for h in hits if nota(h) == melhor][: max(n * 3, 3)]; random.shuffle(top)
    return [(h["largeImageURL"], f'Foto: {h["user"]} / Pixabay') for h in top[:n]]
def wikimedia(q, n):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"filetype:bitmap {q}", "gsrnamespace": 6, "gsrlimit": 20, "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 1600})
    pages = list(_get(url).get("query", {}).get("pages", {}).values()); random.shuffle(pages)
    out = []
    for p in pages[:n]:
        ii = p["imageinfo"][0]; md = ii.get("extmetadata", {})
        autor = md.get("Artist", {}).get("value", "Wikimedia Commons")
        import re; autor = re.sub("<[^>]+>", "", autor)[:60]
        lic = md.get("LicenseShortName", {}).get("value", "")
        out.append((ii.get("thumburl") or ii["url"], f"Foto: {autor} / Wikimedia Commons ({lic})"))
    return out
def buscar(q, pasta, n=1, fonte="auto"):
    os.makedirs(pasta, exist_ok=True)
    res = []
    for f in ([fonte] if fonte != "auto" else ["pixabay", "wikimedia"]):
        try:
            res = (pixabay if f == "pixabay" else wikimedia)(q, n)
        except Exception as e:
            print(f"[imagens] {f} falhou: {e}", file=sys.stderr); res = []
        if res: break
    saida = []
    for i, (url, cred) in enumerate(res):
        nome = os.path.join(pasta, f"{abs(hash(q)) % 10**8}_{i}.jpg")
        try:
            open(nome, "wb").write(_get(url, raw=True)); saida.append({"arquivo": nome, "credito": cred})
        except Exception as e:
            print(f"[imagens] download falhou: {e}", file=sys.stderr)
    return saida
if __name__ == "__main__":
    print(json.dumps(buscar(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1), ensure_ascii=False, indent=1))

RUIM_V = {"anatomy","skeleton","xray","x-ray","hologram","digital","futuristic","sci-fi","abstract","skating","skater","dance","dancer","toy","cartoon","illustration","animation","3d","render","game","virtual","roman","fantasy","anime","costume","lego","doll"}
def buscar_video(q, pasta, dur_min=4):
    """Clipe vertical/horizontal da Pixabay -> {arquivo, credito} ou None."""
    k = chave()
    if not k: return None
    url = "https://pixabay.com/api/videos/?" + urllib.parse.urlencode({"key": k, "q": q, "per_page": 30, "safesearch": "true"})
    try: hits = _get(url).get("hits", [])
    except Exception as e: print(f"[videos] busca falhou: {e}", file=sys.stderr); return None
    pal = [w for w in q.lower().split() if len(w) > 2]
    def nota(h):
        tags = h["tags"].lower().replace(",", " ").split()
        if any(b in tags for b in RUIM_V) or h.get("duration", 0) < dur_min: return -1
        return sum(w in " ".join(tags) for w in pal)
    hits = [h for h in hits if nota(h) >= 0]
    if not hits: return None
    melhor = max(nota(h) for h in hits); top = [h for h in hits if nota(h) == melhor][:3]; random.shuffle(top)
    os.makedirs(pasta, exist_ok=True)
    for h in top:
        v = h["videos"].get("medium") or h["videos"].get("small")
        if not v or not v.get("url"): continue
        nome = os.path.join(pasta, f"v{h['id']}.mp4")
        try:
            open(nome, "wb").write(_get(v["url"], raw=True))
            return {"arquivo": nome, "credito": f"Vídeo: {h['user']} / Pixabay"}
        except Exception as e: print(f"[videos] download falhou: {e}", file=sys.stderr)
    return None
