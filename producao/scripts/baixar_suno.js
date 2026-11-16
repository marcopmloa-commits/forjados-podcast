// uso: node baixar_suno.js <link suno> <pasta_saida>  -> baixa o zip (áudio+letra+capa) pelo usesuno.com
const { chromium } = require('playwright');
(async () => {
  const [link, out] = process.argv.slice(2);
  const b = await chromium.launch(); const ctx = await b.newContext({ acceptDownloads: true }); const p = await ctx.newPage();
  await p.goto('https://usesuno.com/pt-br/tools/downloader/', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await p.fill('#dl-input', link); await p.click('#dl-submit');
  await p.waitForSelector('#dl-btn-all', { state: 'visible', timeout: 90000 });
  const dl = p.waitForEvent('download', { timeout: 180000 });
  await p.click('#dl-btn-all');
  await p.click('[data-audio-format-choice="mp3"]', { timeout: 15000 });
  const cont = p.getByRole('button', { name: /Continuar download/i });   // aviso de patrocinador antes do download
  try { await cont.waitFor({ state: 'visible', timeout: 20000 }); await cont.click(); } catch (e) {}
  const d = await dl; let nome = d.suggestedFilename(); if (!/\.zip$/i.test(nome)) nome = 'musica_' + Date.now() + '.zip';   // nomes com acento chegam como "download"
  const f = out + '/' + nome; await d.saveAs(f); console.log(f);
  await b.close();
})().catch(e => { console.error('ERRO', e.message); process.exit(1); });
