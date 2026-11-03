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
