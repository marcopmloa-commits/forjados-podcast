"""Gera tiktok.html (página fixa com os vídeos do dia: baixar + copiar legenda)."""
import json, os, glob, html, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_site as S
def gerar(pasta_dia):
    dia = os.path.basename(os.path.abspath(pasta_dia)); itens = []
    for v in sorted(glob.glob(os.path.join(pasta_dia, "videos", "*.json"))):
        nome = os.path.basename(v)[:-5]; cfg = json.load(open(v, encoding="utf-8"))
        meta_p = os.path.join(pasta_dia, "saida", nome + ".json")
        meta = json.load(open(meta_p, encoding="utf-8")) if os.path.exists(meta_p) else {"duracao": 0, "creditos": []}
        leg = cfg["legenda_post"]
        url = f"https://raw.githubusercontent.com/marcopmloa-commits/forjados-podcast/tiktok/{dia}/{nome}.mp4"
        itens.append(f"""<article><div class="n">{nome[1:]}</div><div class="c"><h2>{html.escape(cfg['titulo'])}</h2>
<div class="meta">{int(meta['duracao'])//60}:{int(meta['duracao'])%60:02d}</div>
<a class="btn dl" href="{url}" download="forjados-{dia}-{nome}.mp4">⬇ Baixar vídeo</a>
<pre id="l{nome}">{html.escape(leg)}</pre><button class="btn cp" onclick="cp('l{nome}',this)">📋 Copiar legenda</button>
<div class="cred">{html.escape('; '.join(meta['creditos']))}</div></div></article>""")
    d = f"{dia[8:10]}/{dia[5:7]}/{dia[:4]}"
    page = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Forjados — Vídeos do dia</title><link rel="apple-touch-icon" href="capa-v2.jpg"><link rel="icon" href="capa-v2.jpg">
<meta name="robots" content="noindex">
<style>:root{{--ac:#d4a53a}} body{{margin:0;background:#0b0b0b;color:#ece8e0;font-family:system-ui,sans-serif}}
.w{{max-width:680px;margin:0 auto;padding:20px 16px 60px}} header{{display:flex;gap:14px;align-items:center}} header img{{width:64px;border-radius:8px}}
h1{{font-size:22px;margin:0}} .sub{{color:#a39d93;font-size:14px}}
article{{display:flex;gap:14px;background:#151515;border:1px solid #262626;border-radius:12px;padding:16px;margin-top:16px}}
.n{{font-size:28px;font-weight:800;color:var(--ac);min-width:28px}} .c{{flex:1;min-width:0}} h2{{font-size:18px;margin:0 0 4px}} .meta{{color:#a39d93;font-size:13px;margin-bottom:10px}}
.btn{{display:block;width:100%;box-sizing:border-box;text-align:center;padding:12px;border-radius:8px;font-size:16px;font-weight:600;border:0;margin:8px 0;cursor:pointer;text-decoration:none}}
.dl{{background:var(--ac);color:#111}} .cp{{background:#2a2a2a;color:#ece8e0}}
pre{{white-space:pre-wrap;background:#0f0f0f;border-radius:8px;padding:10px;font-size:14px;font-family:inherit;margin:8px 0 0}}
.cred{{font-size:11px;color:#6f6a63;margin-top:6px}}</style></head><body><div class="w">
<header><img src="capa-v2.jpg" alt=""><div><h1>Vídeos do dia</h1><div class="sub">Forjados · {d} · {len(itens)} vídeos</div></div></header>
{''.join(itens)}
<p class="sub" style="margin-top:24px">Se o download abrir o vídeo em vez de baixar: toque e segure no vídeo → Baixar/Salvar.</p></div>
<script>function cp(id,b){{const t=document.getElementById(id).innerText;navigator.clipboard.writeText(t).then(()=>{{b.textContent='✔ Copiada';setTimeout(()=>b.textContent='📋 Copiar legenda',1500)}})}}</script>
</body></html>"""
    open(os.path.join(S.RAIZ, "tiktok.html"), "w", encoding="utf-8").write(page)
if __name__ == "__main__": gerar(sys.argv[1])
