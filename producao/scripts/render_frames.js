// uso: node render_frames.js frames.json  -> cada item {out, ...dados}
const {chromium}=require('playwright');const fs=require('fs'),path=require('path');
(async()=>{const items=JSON.parse(fs.readFileSync(process.argv[2]));const b=await chromium.launch();
const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.resolve(__dirname,'frame.html'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
for(const it of items){await p.evaluate(d=>window.setFrame(d),it);await p.screenshot({path:it.out});}
await b.close();})();
