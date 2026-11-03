# Forjados — produção diária

Todo dia: **6 episódios de áudio (~3 min)** para o podcast + **6 vídeos verticais (~2 min)** para o TikTok.

## Como rodar um dia

```bash
pip install -q edge-tts piper-tts   # se faltar
python3 producao/scripts/publicar_dia.py producao/diario/AAAA-MM-DD
```

O script gera os MP3/MP4 que faltam em `producao/diario/AAAA-MM-DD/saida/` (essa pasta NÃO vai para o git),
publica os 6 vídeos + `legendas-tiktok.txt` no branch **`tiktok`** (só o dia atual; um commit e um push por vídeo, porque envios grandes falham),
copia os áudios em 64 kbps para `episodios/AAAA-MM-DD-aN.mp3` (servidos pelo GitHub Pages) e atualiza `episodios.json`, `feed.xml`, `index.html` e `tiktok.html` (página fixa dos vídeos do dia: https://marcopmloa-commits.github.io/forjados-podcast/tiktok.html).
Depois: `git add -A` (o .gitignore já exclui `saida/`), commit e push em `main`.
(GitHub Releases não são permitidas nestas sessões.)

**Espaço:** o GitHub Pages aceita ~1 GB → ~10 MB/dia de áudio ≈ 3 meses. Quando `du -sh episodios` passar de 850 MB, avise o dono.

## Formato dos arquivos do dia

`audios/a1.json … a6.json`
```json
{"titulo": "...", "descricao": "1–2 frases", "paragrafos": ["GANCHO de 1–2 frases.", "Isto é o Forjados.", "...", "", "...", "Isso foi o Forjados. Mantenha-se firme."]}
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
- **Mistura por dia: 4 histórias + 2 motivacionais.** O foco do dono são **histórias reais de superação em guerras, batalhas triunfais, resistências impossíveis e operações especiais** — sempre terminando com a lição para a vida de quem ouve. Exemplos de fontes de tema: Termópilas; Desmond Doss em Okinawa; Louis Zamperini; cerco de Bastogne; Dunquerque; FEB em Monte Castelo; Batalha de Riachuelo; Guararapes; resgate de Entebbe; Hiroo Onoda (lado sombrio da obstinação); Marcus Luttrell; Moinho de Rorke's Drift; Masada; Stalingrado (civis e soldados); Nancy Wake; Simo Häyhä e o inverno finlandês; Batalha da Ilha Wake; caverna da Tailândia (resgate 2018). Motivacionais: disciplina, dor, rotina, recaída, foco, medo, solidão, sono, treino, dinheiro, vício em celular…
- **Fatos conferidos via WebSearch** (datas, números, nomes). Na dúvida, generalize ("cerca de", "segundo relatos"). Não glorifique violência nem desumanize inimigos: o herói da história é a **resistência humana**.
- Os 6 vídeos podem ser versões condensadas dos 6 áudios do dia ou temas próprios.

### Mídias com relação e contexto (obrigatório — o dono cobra isso)
- **Histórias reais: imagens de arquivo DO PRÓPRIO FATO** via Wikimedia Commons: `"fonte": "wikimedia"`. Ex.: FEB → fotos da FEB na Itália, o distintivo da **Cobra Fumando**, Monte Castelo, Mascarenhas de Moraes; Desmond Doss → fotos dele e de Okinawa; Termópilas → o local, estátua de Leônidas, pinturas históricas (ex.: "Leonidas at Thermopylae" de David).
- Melhor ainda: ache o arquivo exato com WebSearch/no Commons e use `"img": "File:Nome_exato.jpg"` com `"fonte": "wikimedia"`.
- **Com acesso total à internet (configurado pelo dono):** para histórias brasileiras ou temas em que o Commons/LoC falham, use WebSearch para achar fotos de arquivo em sites oficiais/acervos (Arquivo Nacional, Exército Brasileiro, museus, Wikipédia) e coloque o endereço direto da imagem em `"img_url"` + `"credito": "Foto: <acervo>"`. Prefira material histórico em domínio público (ex.: fotos da FEB de 1944–45). Não use fotos de bancos pagos, de jornais recentes ou com marca d'água.
- Fontes históricas automáticas: `"fonte": "wikimedia"` tenta Commons e depois Biblioteca do Congresso dos EUA (forte em EUA/Europa, fraca em Brasil).
- Sempre coloque `"img_reserva"` (busca genérica na Pixabay, ex.: "vintage soldiers mud") para o caso de o Commons não responder.
- Fotos do Commons aparecem **inteiras** (sem corte), sobre fundo desfocado — automático.
- **Nunca** use foto/clipe que contradiga a história: soldado moderno numa história da 2ª Guerra, uniforme de outro país, época errada, pessoas aleatórias no lugar do personagem. Na dúvida, prefira mapa, local, paisagem ou objeto da época a uma pessoa errada.
- Clipes de vídeo (`"video"`) em histórias só quando combinam com a época/lugar (neve, lama, mar revolto, fogo, explosão distante, montanha). Para gancho de história, uma foto de arquivo forte também vale.
- Ao conferir o vídeo (passo 6 da tarefa diária), troque qualquer cena com imagem fora de contexto.
- Chave do Commons: `WIKIMEDIA_TOKEN` (variável do ambiente) ou `~/.wikimedia_token`. Sem ela o Commons costuma recusar (erro 429) por limite de IP compartilhado.

### Prender a atenção nos primeiros 2 segundos (obrigatório)
- **Nada de introdução.** A 1ª fala do vídeo é o gancho, com no máximo 8 palavras, e entra imediatamente. Tipos de gancho: número chocante ("300 homens contra 100 mil."), cena no meio da ação ("A granada caiu aos pés dele."), pergunta provocativa ("Você aguentaria 3 dias sem dormir?"), contradição ("Ele foi recusado pelo exército. Virou herói.").
- A 1ª cena tem `"video"` (movimento) — ou, em história, a foto de arquivo mais forte do fato — e um `big` curto e forte (1–3 palavras ou um número).
- Revelar a lição só no final; no meio, criar tensão ("mas aí...", "o que ninguém esperava...").
- No áudio do podcast: o 1º parágrafo também é o gancho (1–2 frases), e só depois "Isto é o Forjados." Fechamento: "Isso foi o Forjados. Mantenha-se firme."

### Variar os formatos (rodar ao longo do dia, nunca 2 iguais seguidos)
1. **História narrada** (cronológica, com clímax) — padrão para batalhas.
2. **Começo pelo fim** — abre no clímax e volta: "Como ele chegou aqui?".
3. **3 lições de…** (uma batalha/um personagem) — cenas numeradas no `kicker` ("LIÇÃO 1").
4. **Você sabia?** — fato histórico surpreendente + virada motivacional.
5. **Contagem / números** — cada cena um número grande no `big` (dias, quilômetros, homens, horas).
6. **Chamado direto (motivacional)** — segunda pessoa, ritmo de treino, frases de 3–6 palavras.
7. **Desafio do dia** — termina com uma tarefa concreta para hoje ("Comente FEITO quando terminar").
- Nas legendas dos posts, termine com uma pergunta ou chamada para comentar (engajamento).
- **Não repetir temas**: consulte e atualize `producao/temas_usados.md`.

## Infra

- Voz: Microsoft Edge TTS `pt-BR-AntonioNeural` — áudios rate +4%/pitch −8Hz; vídeos rate +21%/pitch −6Hz, pausas curtas (`scripts/comum.py`). O dono achou a fala lenta dos vídeos entediante: manter ritmo rápido. Reserva offline: Piper.
- Fotos: Pixabay (chave em `PIXABAY_KEY` ou `~/.pixabay_key` — nunca no repositório) → reserva Wikimedia Commons.
- Domínios que o ambiente precisa: speech.platform.bing.com, pixabay.com, cdn.pixabay.com (fotos e vídeos), commons.wikimedia.org, upload.wikimedia.org, fonts.googleapis.com, fonts.gstatic.com.
- Site: https://marcopmloa-commits.github.io/forjados-podcast/ · Feed: …/feed.xml (Spotify já cadastrado).
- Commits com e-mail noreply do GitHub; nunca o e-mail pessoal do dono.
