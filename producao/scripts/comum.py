import os, re, subprocess, wave
VOZ_PADRAO = "pt-BR-AntonioNeural:+4%:-8Hz"   # áudios do podcast
VOZ_VIDEO = "pt-BR-AntonioNeural:+21%:-6Hz"   # vídeos: mais rápido, prende atenção
def limpa(t): return re.sub(r"\*\*(.+?)\*\*", r"\1", t)
def destaca(t): return re.sub(r"\*\*(.+?)\*\*", r'<span class="hl">\1</span>', t)
def tts(texto, wav, voz=VOZ_PADRAO):
    nome, rate, pitch = voz.split(":")
    mp3 = wav[:-4] + ".mp3"
    cmd = ["edge-tts", "--voice", nome, f"--rate={rate}", f"--pitch={pitch}", "--text", limpa(texto), "--write-media", mp3]
    if os.environ.get("HTTPS_PROXY"): cmd[1:1] = ["--proxy", os.environ["HTTPS_PROXY"]]
    for tentativa in range(3):
        if subprocess.run(cmd, stderr=subprocess.DEVNULL).returncode == 0 and os.path.getsize(mp3) > 0: break
    else: raise RuntimeError("edge-tts falhou: " + texto[:40])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ar", "24000", "-ac", "1", wav], check=True)
    with wave.open(wav) as w: return w.getnframes() / w.getframerate()
def trilha(dur):
    """entradas lavfi para a trilha grave sintetizada"""
    return ["-f","lavfi","-i",f"sine=f=55:d={dur}","-f","lavfi","-i",f"sine=f=82.4:d={dur}","-f","lavfi","-i",f"anoisesrc=c=brown:a=0.02:d={dur}"]

def tts_corrido(textos, wav, voz):
    """Narra vários trechos NUM fluxo só (entonação contínua, sem pausa artificial entre frases).
    Devolve (duração_total, [início_em_segundos de cada trecho])."""
    import asyncio, edge_tts
    nome, rate, pitch = voz.split(":")
    limpos = [limpa(t).strip() for t in textos]
    texto = " ".join(limpos)
    mp3 = wav[:-4] + ".mp3"; marcas = []
    async def run():
        c = edge_tts.Communicate(texto, nome, rate=rate, pitch=pitch, boundary="WordBoundary",
                                 proxy=os.environ.get("HTTPS_PROXY"))
        with open(mp3, "wb") as f:
            async for ch in c.stream():
                if ch["type"] == "audio": f.write(ch["data"])
                elif ch["type"] == "WordBoundary": marcas.append((ch["offset"] / 1e7, ch["text"]))
    for t in range(3):
        try: marcas.clear(); asyncio.run(run()); break
        except Exception as e:
            if t == 2: raise
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ar", "24000", "-ac", "1", wav], check=True)
    with wave.open(wav) as w: total = w.getnframes() / w.getframerate()
    # início de cada trecho = tempo da 1ª palavra dele; procura a palavra adiante (números podem virar várias marcas)
    norm = lambda s: re.sub(r"[^\w]", "", s.lower())
    inicios, k = [], 0
    for t in limpos:
        palavras = [norm(p) for p in t.split() if norm(p)]
        alvo = palavras[0] if palavras else ""
        achou = next((j for j in range(k, min(k + 12, len(marcas))) if norm(marcas[j][1]) == alvo), None)
        if achou is None: achou = min(k, len(marcas) - 1)
        inicios.append(marcas[achou][0] if marcas else 0.0)
        k = achou + max(len(palavras) - 2, 1)
    inicios[0] = 0.0
    for i in range(1, len(inicios)): inicios[i] = min(max(inicios[i], inicios[i-1] + 0.4), total)
    return total, inicios
