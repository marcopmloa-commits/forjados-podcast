// uso: node render.js arquivo.html saida.png largura altura escala
const {chromium}=require('playwright');
(async()=>{const [,,html,out,w,h,sc]=process.argv;const b=await chromium.launch();
const p=await b.newPage({viewport:{width:+w,height:+h},deviceScaleFactor:+(sc||1)});
await p.goto('file://'+require('path').resolve(html));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
await p.screenshot({path:out});await b.close();})();
