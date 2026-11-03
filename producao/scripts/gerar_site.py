"""Gera index.html e feed.xml a partir de episodios.json (na raiz do repositório)."""
import json, html, os, email.utils, datetime
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BASE = "https://marcopmloa-commits.github.io/forjados-podcast/"
EMAIL = "forjadosclaude@gmail.com"
def carregar(): return json.load(open(os.path.join(RAIZ, "episodios.json"), encoding="utf-8"))
def salvar(eps): json.dump(eps, open(os.path.join(RAIZ, "episodios.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
def mmss(s): s = int(s); return f"{s//60}:{s%60:02d}"
def gerar():
    eps = sorted(carregar(), key=lambda e: e["data"], reverse=True)
    itens = []
    for e in eps:
        dt = datetime.datetime.fromisoformat(e["data"])
        itens.append(f"""<item><title>{html.escape(e['titulo'])}</title><description>{html.escape(e['descricao'])}</description>
<enclosure url="{html.escape(e['url'])}" length="{e['bytes']}" type="audio/mpeg"/><guid isPermaLink="false">{e['id']}</guid>
<pubDate>{email.utils.format_datetime(dt)}</pubDate><itunes:duration>{int(e['dur'])}</itunes:duration><itunes:explicit>false</itunes:explicit></item>""")
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
<channel><title>Forjados</title><link>{BASE}</link><language>pt-br</language>
<atom:link href="{BASE}feed.xml" rel="self" type="application/rss+xml"/>
<description>Operações especiais, histórias reais e a mentalidade de quem decidiu não desistir. Motivação, disciplina e histórias de guerreiros.</description>
<itunes:author>Forjados</itunes:author><itunes:owner><itunes:name>Forjados</itunes:name><itunes:email>{EMAIL}</itunes:email></itunes:owner>
<managingEditor>{EMAIL} (Forjados)</managingEditor><itunes:explicit>false</itunes:explicit>
<itunes:image href="{BASE}capa-v2.jpg"/><image><url>{BASE}capa-v2.jpg</url><title>Forjados</title><link>{BASE}</link></image>
<itunes:category text="Health &amp; Fitness"/><itunes:category text="History"/><itunes:type>episodic</itunes:type>
{''.join(itens)}
</channel></rss>"""
    open(os.path.join(RAIZ, "feed.xml"), "w", encoding="utf-8").write(rss)
    cards = []
    for e in eps:
        tr = "".join(f"<p>{html.escape(p)}</p>" for p in e.get("transcricao", []) if p.strip())
        cards.append(f"""<article class="ep"><h2>{html.escape(e['titulo'])}</h2><div class="meta">{e['data'][:10]} · {mmss(e['dur'])}</div>
<audio controls preload="none" src="{html.escape(e['url'])}"></audio><p>{html.escape(e['descricao'])}</p>
{'<details><summary>TRANSCRIÇÃO</summary><div class="tr">'+tr+'</div></details>' if tr else ''}</article>""")
    page = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Forjados — Podcast</title><meta name="description" content="Operações especiais, histórias reais e mentalidade militar.">
<link rel="alternate" type="application/rss+xml" title="Forjados" href="feed.xml"><meta property="og:image" content="{BASE}capa-v2.jpg">
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Oswald:wght@400;600&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>:root{{--bg:#0b0b0b;--fg:#ece8e0;--mut:#a39d93;--ac:#d4a53a;--card:#151515}}
body{{margin:0;background:var(--bg);color:var(--fg);font-family:Inter,sans-serif;line-height:1.65}}
.w{{max-width:760px;margin:0 auto;padding:40px 16px 80px}} header{{display:flex;gap:28px;align-items:center;flex-wrap:wrap}}
header img{{width:220px;max-width:100%;border-radius:10px}} h1{{font-family:Anton;font-size:64px;letter-spacing:3px;margin:0;line-height:1}}
.tag{{font-family:Oswald;letter-spacing:4px;color:var(--ac);font-size:15px}}
.btns a{{display:inline-block;margin:14px 10px 0 0;padding:8px 14px;border:1px solid #333;border-radius:6px;color:var(--fg);text-decoration:none;font-size:14px}}
.ep{{background:var(--card);border:1px solid #262626;border-radius:12px;padding:24px;margin-top:28px}}
.ep h2{{font-family:Oswald;font-weight:600;font-size:24px;margin:0 0 6px}} .meta{{color:var(--mut);font-size:14px}} audio{{width:100%;margin:14px 0}}
details summary{{cursor:pointer;color:var(--ac);font-family:Oswald;letter-spacing:2px}} .tr p{{margin:0 0 12px}}</style></head><body><div class="w">
<header><img src="capa-v2.jpg" alt="Capa do podcast Forjados"><div><div class="tag">PODCAST</div><h1>FORJADOS</h1>
<p>Operações especiais, histórias reais e a mentalidade de quem decidiu não desistir.</p><div class="btns"><a href="tiktok.html">Vídeos do dia</a><a href="feed.xml">Feed RSS</a></div></div></header>
{''.join(cards)}</div></body></html>"""
    open(os.path.join(RAIZ, "index.html"), "w", encoding="utf-8").write(page)
if __name__ == "__main__": gerar()
