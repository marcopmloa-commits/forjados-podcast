# Forjados — produção diária

Todo dia: **6 episódios de áudio (~3 min)** para o podcast + **6 vídeos verticais (~2 min)** para o TikTok.

## Como rodar um dia

```bash
pip install -q edge-tts piper-tts   # se faltar
python3 producao/scripts/publicar_dia.py producao/diario/AAAA-MM-DD
```

O script gera os MP3/MP4 que faltam em `producao/diario/AAAA-MM-DD/saida/` (essa pasta NÃO vai para o git),
publica os 6 vídeos + `legendas-tiktok.txt` no branch **`tiktok`** (pasta do dia; só os últimos 3 dias, push forçado),
copia os áudios em 64 kbps para `episodios/AAAA-MM-DD-aN.mp3` (servidos pelo GitHub Pages) e atualiza `episodios.json`, `feed.xml` e `index.html`.
Depois: `git add -A` (o .gitignore já exclui `saida/`), commit e push em `main`.
(GitHub Releases não são permitidas nestas sessões.)

**Espaço:** o GitHub Pages aceita ~1 GB → ~10 MB/dia de áudio ≈ 3 meses. Quando `du -sh episodios` passar de 850 MB, avise o dono.

## Formato dos arquivos do dia

`audios/a1.json … a6.json`
```json
{"titulo": "...", "descricao": "1–2 frases", "paragrafos": ["Forjados.", "...", "", "...", "Isso foi o Forjados. Mantenha-se firme."]}
```
- **370–400 palavras** no total (= ~3 min com a voz padrão; 438 palavras deram 3min28). `""` = pausa de 1 s.

`videos/v1.json … v6.json`
```json
{"titulo": "...", "legenda_post": "texto do post + hashtags",
 "cenas": [{"img": "busca em INGLÊS para a foto", "kicker": "RÓTULO CURTO", "big": "2–3 PALAVRAS", "falas": ["frase 1", "frase 2", "frase 3"]}]}
```
- **9 cenas × 3 falas, 260–290 palavras** (= ~2 min com a voz rápida dos vídeos, +21%; 240 palavras deram ~1min45). Frases curtas e secas: ritmo é tudo. Uma foto por cena; a cena final (logo + "Episódios completos no Spotify") é automática.
- **Vídeo de fundo:** em ~metade das cenas (4–5 de 9, alternando com foto; sempre a 1ª cena, para prender nos primeiros segundos) adicione `"video": "busca em INGLÊS"` — clipe da Pixabay, P&B, continua rodando durante a cena. Mantenha também o `"img"` na mesma cena: é a reserva se não achar clipe. Buscas de vídeo funcionam melhor com ação: "soldiers running", "boxer punching bag", "man running rain", "military helicopter", "push ups", "waves storm". (Precisa do domínio cdn.pixabay.com liberado.)
- `**palavra**` nas falas = destaque dourado na legenda (e é removido da narração).
- Buscas de imagem: sempre especifique "modern"/"military"/"special forces" quando for soldado ("soldier alone" trouxe um soldado romano). Concretas e visuais ("soldier running beach", "alarm clock dark", "boxer training gym"). Opcional `"fonte": "wikimedia"` para fotos militares reais.

## Linha editorial

- **Máximo de 5 hashtags por post** (`legenda_post`). Sempre incluir `#forjados`; as outras 4, ligadas ao tema do vídeo.

- Tom: cru, direto, segunda pessoa, frases curtas, no estilo dos discursos motivacionais de operações especiais (tipo David Goggins).
- **Texto 100% original.** Não imitar nem se passar por pessoas reais; não transcrever discursos/livros. Citar alguém só com fatos verificáveis e sem aspas longas.
- Mistura por dia: 4 motivacionais (disciplina, dor, rotina, recaída, foco, medo, solidão, sono, treino, dinheiro, vício em celular…) + 2 histórias (forças especiais, missões famosas, seleções militares, atletas de ultraresistência, figuras históricas) — fatos conferidos via busca; na dúvida, generalize.
- Os 6 vídeos podem ser versões condensadas dos 6 áudios do dia ou temas próprios.
- Fechamento padrão do áudio: "Isso foi o Forjados. Mantenha-se firme."
- **Não repetir temas**: consulte e atualize `producao/temas_usados.md`.

## Infra

- Voz: Microsoft Edge TTS `pt-BR-AntonioNeural` — áudios rate +4%/pitch −8Hz; vídeos rate +21%/pitch −6Hz, pausas curtas (`scripts/comum.py`). O dono achou a fala lenta dos vídeos entediante: manter ritmo rápido. Reserva offline: Piper.
- Fotos: Pixabay (chave em `PIXABAY_KEY` ou `~/.pixabay_key` — nunca no repositório) → reserva Wikimedia Commons.
- Domínios que o ambiente precisa: speech.platform.bing.com, pixabay.com, cdn.pixabay.com (fotos e vídeos), commons.wikimedia.org, upload.wikimedia.org, fonts.googleapis.com, fonts.gstatic.com.
- Site: https://marcopmloa-commits.github.io/forjados-podcast/ · Feed: …/feed.xml (Spotify já cadastrado).
- Commits com e-mail noreply do GitHub; nunca o e-mail pessoal do dono.
