"""Busca e baixa fotos reais (Pixabay; Wikimedia Commons como reserva).
uso: python3 imagens.py "consulta em ingles" pasta_saida [n]  -> imprime JSON [{arquivo, credito}]"""
import json, os, sys, urllib.request, urllib.parse, ssl, random
UA = "ForjadosPodcast/1.0 (https://marcopmloa-commits.github.io/forjados-podcast/; forjadosclaude@gmail.com)"
def _token_wiki():
    t = os.environ.get("WIKIMEDIA_TOKEN")
    if not t:
        p = os.path.expanduser("~/.wikimedia_token")
        if os.path.exists(p): t = open(p).read().strip()
    return t
def _get(url, raw=False):
    import time, urllib.error
    h = {"User-Agent": UA}
    if "wikimedia.org" in url and _token_wiki(): h["Authorization"] = "Bearer " + _token_wiki()
    for t in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=40) as r:
                d = r.read()
            return d if raw else json.loads(d)
        except urllib.error.HTTPError as e:
            if e.code != 429 or t == 3: raise
            time.sleep(5 * (t + 1))
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
    """q = busca livre ou nome exato de arquivo do Commons ("File:Nome.jpg")."""
    import re
    api = "https://commons.wikimedia.org/w/api.php?"
    base = {"action": "query", "format": "json", "prop": "imageinfo", "iiprop": "url|extmetadata|size|mime", "iiurlwidth": 1600}
    if q.startswith("File:"):
        params = dict(base, titles=q)
    else:
        params = dict(base, generator="search", gsrsearch=f"filetype:bitmap {q}", gsrnamespace=6, gsrlimit=25)
    pages = list(_get(api + urllib.parse.urlencode(params)).get("query", {}).get("pages", {}).values())
    pages = [p for p in pages if p.get("imageinfo") and p["imageinfo"][0].get("mime") in ("image/jpeg", "image/png", "image/tiff")]
    pages.sort(key=lambda p: (p.get("index", 0), -p["imageinfo"][0].get("height", 0)))
    top = pages[: max(n * 2, 3)] if not q.startswith("File:") else pages; random.shuffle(top)
    out = []
    for p in top[:n]:
        ii = p["imageinfo"][0]; md = ii.get("extmetadata", {})
        autor = re.sub("<[^>]+>", "", md.get("Artist", {}).get("value", "Wikimedia Commons"))[:60].strip()
        lic = md.get("LicenseShortName", {}).get("value", "")
        out.append((ii.get("thumburl") or ii["url"], f"Foto: {autor} / Wikimedia Commons ({lic})"))
    return out
def loc(q, n):
    """Biblioteca do Congresso dos EUA (fotos históricas, muitas em domínio público)."""
    url = "https://www.loc.gov/photos/?" + urllib.parse.urlencode({"q": q, "fo": "json", "c": 40})
    res = _get(url).get("results", [])
    out = []
    for r in res:
        urls = [u for u in (r.get("image_url") or []) if "tile.loc.gov" in u and not u.endswith(".svg")]
        if not urls: continue
        if r.get("online_format") and "image" not in " ".join(r["online_format"]): continue
        u = urls[-1].split("#")[0]
        texto = (r.get("title", "") + " " + " ".join(r.get("subject", []) or [])).lower()
        nota = sum(w in texto for w in [w for w in q.lower().split() if len(w) > 3])
        out.append((nota, u, f"Foto: {r.get('title','')[:50]} / Library of Congress"))
    if not out: return []
    melhor = max(o[0] for o in out)
    minimo = max(1, (len([w for w in q.split() if len(w) > 3]) + 1) // 2)   # pelo menos metade das palavras
    if melhor < minimo: return []
    top = [(u, c) for nt, u, c in out if nt == melhor][: max(n * 2, 3)]; random.shuffle(top)
    return top[:n]
def buscar(q, pasta, n=1, fonte="auto"):
    os.makedirs(pasta, exist_ok=True)
    ordem = {"auto": ["pixabay", "wikimedia"], "wikimedia": ["wikimedia", "loc"], "historico": ["wikimedia", "loc"], "loc": ["loc"], "pixabay": ["pixabay"]}[fonte]
    # nome de arquivo do Commons ("File:Nome_exato.jpg") vira busca em texto para a LoC
    q_loc = os.path.splitext(q.replace("File:", ""))[0].replace("_", " ") if q.startswith("File:") else q
    for f in ordem:
        try:
            res = {"pixabay": pixabay, "wikimedia": wikimedia, "loc": loc}[f](q_loc if f == "loc" else q, n)
        except Exception as e:
            print(f"[imagens] {f} falhou: {e}", file=sys.stderr); res = []
        saida = []
        for i, (url, cred) in enumerate(res):
            nome = os.path.join(pasta, f"{abs(hash(q)) % 10**8}_{f}_{i}.jpg")
            try:
                open(nome, "wb").write(_get(url, raw=True)); saida.append({"arquivo": nome, "credito": cred})
            except Exception as e:
                print(f"[imagens] download {f} falhou: {e}", file=sys.stderr)
        if saida: return saida   # só desiste da fonte se nada foi baixado (ex.: Commons com 429 sem token)
    return []
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
