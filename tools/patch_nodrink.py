import sys,re
p=sys.argv[1];s=open(p,encoding='utf-8').read()
def R(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:110]); s=s.replace(a,b)
R('''    <div class="field"><label class="label" for="${did}">Bebida</label>
      <input class="input" id="${did}" data-f="meal-drink" data-meal="${x.k}" data-sug="drinks" value="${esc(e.drink||'')}" placeholder="Ej: Café con leche, agua" autocomplete="off"><div class="sugs" id="sug-${did}"></div></div>''',
'''    ${e.noDrink?'':`<div class="field"><label class="label" for="${did}">Bebida</label>
      <input class="input" id="${did}" data-f="meal-drink" data-meal="${x.k}" data-sug="drinks" value="${esc(e.drink||'')}" placeholder="Ej: Café con leche, agua" autocomplete="off"><div class="sugs" id="sug-${did}"></div></div>`}
    ${x.k==='desayuno'||x.k==='merienda'?`<label class="lefto" for="nd-${dk}-${x.k}"><input type="checkbox" id="nd-${dk}-${x.k}" data-f="meal-nodrink" data-meal="${x.k}" ${e.noDrink?'checked':''}><span>No he bebido nada</span></label>`:''}''')
R("<dt>Bebida</dt><dd>${esc(e.drink||'—')}</dd>","<dt>Bebida</dt><dd>${e.noDrink?'Nada':esc(e.drink||'—')}</dd>")
R("    case'meal-left':","    case'meal-nodrink':patchWeek({meals:{[fk]:{[el.dataset.meal]:el.checked?{noDrink:true,drink:'',status:'comi'}:{noDrink:false}}}});break;\n    case'meal-left':")
# notification: no drink counts as complete
R("  if((f==='meal-food'||f==='meal-drink')&&v)queueMeal(N,k,mk);","  if(((f==='meal-food'||f==='meal-drink')&&v)||(f==='meal-nodrink'&&el.checked))queueMeal(N,k,mk);")
R("const parts=[e.food?`🍽️ ${e.food}`:'',e.drink?`🥤 ${e.drink}`:''].filter(Boolean).join(' · ');",
  "const parts=[e.food?`🍽️ ${e.food}`:'',e.noDrink?'🥤 sin bebida':(e.drink?`🥤 ${e.drink}`:'')].filter(Boolean).join(' · ');")
R("if(!e.food&&!e.drink)return;","if(!e.food&&!e.drink&&!e.noDrink)return;")
R("q.t=setTimeout(()=>sendMeal(key),(e.food&&e.drink)?1500:60000)","q.t=setTimeout(()=>sendMeal(key),(e.food&&(e.drink||e.noDrink))?1500:60000)")
R("'meal-'+key+'|'+(e.food||'')+'|'+(e.drink||'')","'meal-'+key+'|'+(e.food||'')+'|'+(e.noDrink?'-':(e.drink||''))")
R("const CHANGELOG=[\n","""const CHANGELOG=[
  {v:'2026-11-23c',title:'Novedades',items:[
    'En el desayuno y la merienda puedes marcar «No he bebido nada». El entrenador lo verá como «Bebida: Nada».'
  ]},
""")
open(p,'w',encoding='utf-8').write(s)
open(sys.argv[2],'w').write(re.findall(r'<script>\n(/\* ---------- constants.*?)</script>',s,re.S)[0])
