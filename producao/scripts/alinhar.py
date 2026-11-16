"""Alinha a letra oficial (txt da Suno) com as palavras transcritas e aplica cortes.
uso: python3 -I alinhar.py transcricao.json letra.txt "a1:b1,a2:b2" saida.json
Saída: lista [ini, linha, fim] já na linha do tempo do áudio cortado (crossfade de 1s entre trechos)."""
import json, re, sys, difflib, unicodedata
U=["zero","um","dois","três","quatro","cinco","seis","sete","oito","nove","dez","onze","doze","treze","catorze","quinze","dezesseis","dezessete","dezoito","dezenove"]
D=["","","vinte","trinta","quarenta","cinquenta","sessenta","setenta","oitenta","noventa"]
def ext(n):
    n=int(n)
    if n<20: return U[n]
    if n<100: return D[n//10]+("" if n%10==0 else " e "+U[n%10])
    return str(n)
def norm(w): w=unicodedata.normalize("NFD",w.lower()); return re.sub(r"[^a-z0-9]","","".join(c for c in w if unicodedata.category(c)!="Mn"))
def toks(s): s=re.sub(r"\d+",lambda m:" "+ext(m.group())+" ",s); return [norm(w) for w in s.split() if norm(w)]
tr=json.load(open(sys.argv[1])); letra=open(sys.argv[2]).read()
pal=[]
for seg in tr:
    for (a,b,w) in seg["palavras"]:
        for t in toks(w): pal.append((a,b,t))
linhas=[l.strip() for l in letra.splitlines() if l.strip() and not l.strip().startswith("[")]
lt=[(i,t) for i,l in enumerate(linhas) for t in toks(l)]
sm=difflib.SequenceMatcher(None,[t for _,t in lt],[p[2] for p in pal],autojunk=False)
idx={}
for a,b,n in sm.get_matching_blocks():
    for k in range(n): idx.setdefault(lt[a+k][0],[]).append(b+k)
res=[]
for i,l in enumerate(linhas):
    if i in idx: res.append([pal[min(idx[i])][0],l,pal[max(idx[i])][1]])
    else: res.append([None,l,None])
# linhas sem casamento: interpola entre vizinhas
for i,r in enumerate(res):
    if r[0] is None:
        ant=next((res[j][2] for j in range(i-1,-1,-1) if res[j][2] is not None),0.0)
        prox=next((res[j][0] for j in range(i+1,len(res)) if res[j][0] is not None),ant+2)
        r[0]=ant+0.2; r[2]=max(r[0]+0.8,min(prox-0.2,r[0]+2.0)); print("interpolada:",l,file=sys.stderr)
cortes=[tuple(map(float,c.split(":"))) for c in sys.argv[3].split(",")]
out=[]; base=0.0
for k,(a,b) in enumerate(cortes):
    for ini,l,fim in res:
        if ini>=a and ini<b-0.3: out.append([round(base+ini-a,2),l,round(min(fim,b)-a+base,2)])
    base+= (b-a) - 1.0
json.dump(out,open(sys.argv[4],"w"),ensure_ascii=False,indent=0)
for o in out: print(f"{o[0]:6.1f} {o[2]:6.1f} {o[1]}")
