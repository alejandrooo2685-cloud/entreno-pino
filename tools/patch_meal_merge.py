import sys,re
p=sys.argv[1];s=open(p,encoding='utf-8').read()
def R(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:110]); s=s.replace(a,b)
R("""  if(f==='meal-food'&&v)notify('admin',`🍽️ ${ST} ha apuntado ${MEAL_N[mk]} del ${dn}: ${v}.`,'mf-'+N+k+mk+v);
  if(f==='meal-drink'&&v)notify('admin',`🥤 ${ST}, bebida en ${MEAL_N[mk]} del ${dn}: ${v}.`,'md-'+N+k+mk+v);""",
"""  if((f==='meal-food'||f==='meal-drink')&&v)queueMeal(N,k,mk);""")
R("function hookChange(f,el){",r'''/* comida y bebida de la misma comida → un solo aviso */
const mealQ={};
function sendMeal(key){
  const q=mealQ[key];if(!q)return;clearTimeout(q.t);delete mealQ[key];
  const w=weekList().find(x=>x.num===q.N);if(!w)return;const e=(dayMeals(w,q.k)[q.mk])||{};
  if(!e.food&&!e.drink)return;
  const parts=[e.food?`🍽️ ${e.food}`:'',e.drink?`🥤 ${e.drink}`:''].filter(Boolean).join(' · ');
  notify('admin',`${CFG.student} ha apuntado ${MEAL_N[q.mk]} del ${dayName(q.k)}: ${parts}`,'meal-'+key+'|'+(e.food||'')+'|'+(e.drink||''));
}
function queueMeal(N,k,mk){
  const key=N+k+mk;const q=mealQ[key]||(mealQ[key]={N,k,mk});clearTimeout(q.t);
  setTimeout(()=>{const w=weekList().find(x=>x.num===N);const e=w?((dayMeals(w,k)[mk])||{}):{};
    q.t=setTimeout(()=>sendMeal(key),(e.food&&e.drink)?1500:60000)},0);
}
document.addEventListener('visibilitychange',()=>{if(document.hidden)Object.keys(mealQ).forEach(sendMeal)});
window.addEventListener('pagehide',()=>Object.keys(mealQ).forEach(sendMeal));
function hookChange(f,el){''')
R("    'Avisos de comidas para el entrenador: le llega un Telegram cuando el alumno apunta una comida o bebida,",
  "    'Avisos de comidas para el entrenador: le llega un Telegram cuando el alumno apunta una comida y su bebida (en un solo aviso),")
open(p,'w',encoding='utf-8').write(s)
open(sys.argv[2],'w').write(re.findall(r'<script>\n(/\* ---------- constants.*?)</script>',s,re.S)[0])
