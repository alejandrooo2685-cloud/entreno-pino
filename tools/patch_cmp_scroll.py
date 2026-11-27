import sys
def rep(s,a,b,n=1):
    assert s.count(a)==n,(a[:60],s.count(a));return s.replace(a,b)
for f in sys.argv[1:]:
    s=open(f).read()
    old_start=s.index("  const cmp=withV.length>1?`<div class=\"seg\"")
    old_end=s.index("    </div>`:'';\n",old_start)+len("    </div>`:'';\n")
    new='''  const last=withV[withV.length-1],olds=withV.slice(0,-1);
  const ci=Math.min(Math.max(0,c.i|0),Math.max(0,olds.length-1));
  const cmp=withV.length>1?`<div class="seg" style="max-width:260px">${SLOTS.map(([sk,sn])=>`<button data-act="cmp-view" data-v="${sk}" aria-pressed="${v===sk}">${sn}</button>`).join('')}</div>
    <div class="cmp">
      <div class="cmpcol"><div class="cmp-sc" id="cmp-sc" data-n="${olds.length}">${olds.map(e=>`<button class="bimg" data-act="lightbox" data-id="${esc(e[v])}" data-lbl="${esc(bLabel(e))}"><img src="${blob(esc(e[v]))}" alt="${esc(bLabel(e))}" loading="lazy"></button>`).join('')}</div>
        <div class="cmp-nav"><button class="cmp-ar" data-act="cmp-step" data-d="-1" aria-label="Semana anterior" ${ci<=0?'disabled':''}>‹</button><span class="label" id="cmp-lbl">${esc(bLabel(olds[ci]))}</span><button class="cmp-ar" data-act="cmp-step" data-d="1" aria-label="Semana siguiente" ${ci>=olds.length-1?'disabled':''}>›</button></div>
        <span class="cmp-pos muted" id="cmp-pos">${olds.length>1?`${ci+1} de ${olds.length} · desliza para cambiar`:''}</span></div>
      <div class="cmpcol"><button class="bimg last" data-act="lightbox" data-id="${esc(last[v])}"><img src="${blob(esc(last[v]))}" alt="Última foto"></button>
        <div class="cmp-nav"><span class="label">Última · ${esc(bLabel(last))}</span></div></div>
    </div>`:'';
'''
    s=s[:old_start]+new+s[old_end:]
    s=rep(s,"cmp:{a:null,b:null,view:'front'}","cmp:{i:0,view:'front'}")
    s=rep(s,"    case'cmp-view':state.cmp.view=b.dataset.v;break;",
      "    case'cmp-view':state.cmp.view=b.dataset.v;state.cmp.i=0;break;\n    case'cmp-step':{const sc=document.getElementById('cmp-sc');if(sc)sc.scrollBy({left:(+b.dataset.d)*sc.clientWidth,behavior:'smooth'});return}")
    s=rep(s,"  app.innerHTML=shell();\n","  app.innerHTML=shell();\n  setupCmp();\n")
    s=rep(s,"function bodyCard(){",'''function setupCmp(){
  const sc=document.getElementById('cmp-sc');if(!sc)return;
  const n=+sc.dataset.n||0;const slides=[...sc.children];
  const upd=i=>{i=Math.min(Math.max(0,i),n-1);state.cmp.i=i;const l=document.getElementById('cmp-lbl');if(l&&slides[i])l.textContent=slides[i].dataset.lbl;
    const p=document.getElementById('cmp-pos');if(p&&n>1)p.textContent=`${i+1} de ${n} · desliza para cambiar`;
    document.querySelectorAll('.cmp-ar').forEach(x=>{x.disabled=(+x.dataset.d<0)?i<=0:i>=n-1})};
  const go=()=>{sc.scrollLeft=(state.cmp.i|0)*sc.clientWidth};go();requestAnimationFrame(go);
  let t=null;sc.addEventListener('scroll',()=>{clearTimeout(t);t=setTimeout(()=>upd(Math.round(sc.scrollLeft/Math.max(1,sc.clientWidth))),60)},{passive:true});
}
function bodyCard(){''')
    s=rep(s,"  if(f==='cmp-a'||f==='cmp-b'){state.cmp[f==='cmp-a'?'a':'b']=el.value;render();return}","")
    s=rep(s,".cmpcol .label{text-align:center}\n",""".cmpcol .label{text-align:center}
.cmp-sc{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;border-radius:12px;scrollbar-width:none;-webkit-overflow-scrolling:touch;overscroll-behavior-x:contain}
.cmp-sc::-webkit-scrollbar{display:none}
.cmp-sc>.bimg{flex:0 0 100%;scroll-snap-align:center;scroll-snap-stop:always}
.bimg.last{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent)}
.cmp-nav{display:flex;align-items:center;justify-content:center;gap:6px;min-height:34px}
.cmp-nav .label{flex:1;min-width:0;font-size:11px;line-height:1.25}
.cmp-ar{width:34px;height:34px;flex:none;border-radius:50%;border:1px solid var(--line);background:var(--surface-2);color:var(--ink);font-size:22px;line-height:1;padding:0;display:grid;place-items:center;cursor:pointer}
.cmp-ar:disabled{opacity:.3;cursor:default}
.cmp-pos{text-align:center;font-size:11px}
""")
    open(f,'w').write(s)
    print('ok',f)
