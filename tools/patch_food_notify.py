import sys,re
p=sys.argv[1];s=open(p,encoding='utf-8').read()
def R(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:110]); s=s.replace(a,b)
# fix comparator bug (v used before definition)
R("if(f==='cmp-a'||f==='cmp-b'){state.cmp[f==='cmp-a'?'a':'b']=v;render();return}",
  "if(f==='cmp-a'||f==='cmp-b'){state.cmp[f==='cmp-a'?'a':'b']=el.value;render();return}")
# food notifications
R("async function tgKey(){",r'''const MEAL_N={desayuno:'el desayuno',almuerzo:'la comida',merienda:'la merienda',cena:'la cena'};
function hookChange(f,el){
  if(state.role!=='alumno')return;const w=curWeek();if(!w)return;const ST=CFG.student;const k=DAYS[state.foodDay].k;const dn=dayName(k);const N=w.num;
  const v=(el.value||'').trim();const mk=el.dataset.meal;
  if(f==='meal-food'&&v)notify('admin',`🍽️ ${ST} ha apuntado ${MEAL_N[mk]} del ${dn}: ${v}.`,'mf-'+N+k+mk+v);
  if(f==='meal-drink'&&v)notify('admin',`🥤 ${ST}, bebida en ${MEAL_N[mk]} del ${dn}: ${v}.`,'md-'+N+k+mk+v);
  if(f==='meal-dessert'&&el.checked)notify('admin',`🍰 ${ST} ha tomado postre en ${MEAL_N[mk]} del ${dn}.`,'ds-'+N+k+mk);
  if(f==='meal-dessert-text'&&v)notify('admin',`🍰 ${ST}, postre en ${MEAL_N[mk]} del ${dn}: ${v}.`,'dt-'+N+k+mk+v);
  if(f==='meal-left'&&el.checked){const e=(dayMeals(w,k)[mk])||{};notify('admin',`♻️ ${ST}: ${MEAL_N[mk]} del ${dn} son sobras${e.food?' ('+e.food+')':''}.`,'lo-'+N+k+mk)}
}
async function tgKey(){''')
R("    if(a==='review-read')","""    if(a==='meal-status'&&b.dataset.v==='no'){const k=DAYS[state.foodDay].k;const e=(dayMeals(w,k)[b.dataset.meal])||{};
      if(e.status!=='no')notify('admin',`🚫 ${ST} no ha tomado ${MEAL_N[b.dataset.meal]} del ${dayName(k)}.`,'mn-'+N+k+b.dataset.meal)}
    if(a==='extra-add'){const t=(document.getElementById('extra-text')?.value||'').trim();const k=DAYS[state.foodDay].k;
      const tm=document.getElementById('extra-time')?.value||'';if(t)notify('admin',`🍺 ${ST} ha apuntado un extra el ${dayName(k)}${tm?' a las '+tm:''}: ${t} (${state.extraCat}).`,'ex-'+N+k+t+tm)}
    if(a==='review-read')""")
R("toast('Foto subida')}","toast('Foto subida');notify('admin',`📷 ${CFG.student} ha subido una foto de ${MEAL_N[p.meal]} del ${dayName(p.day)}.`,'mp-'+p.week+p.day+p.meal)}")
R("const el=ev.target;if(el.id==='xa-h')state.xa.h=+el.value;if(el.id==='xa-m')state.xa.m=+el.value;const f=el.dataset&&el.dataset.f;if(!f)return;",
  "const el=ev.target;if(el.id==='xa-h')state.xa.h=+el.value;if(el.id==='xa-m')state.xa.m=+el.value;const f=el.dataset&&el.dataset.f;if(!f)return;\n  try{hookChange(f,el)}catch(e){}")
R("const CHANGELOG=[\n","""const CHANGELOG=[
  {v:'2026-11-23b',title:'Novedades',items:[
    'Avisos de comidas para el entrenador: le llega un Telegram cuando el alumno apunta una comida o bebida, marca que no ha comido, toma postre, marca sobras, sube una foto de una comida o apunta un extra (cervezas, chuches…).',
    'Arreglado: el comparador de fotos «antes / después» ya deja cambiar las semanas.'
  ]},
""")
open(p,'w',encoding='utf-8').write(s)
open(sys.argv[2],'w').write(re.findall(r'<script>\n(/\* ---------- constants.*?)</script>',s,re.S)[0])
