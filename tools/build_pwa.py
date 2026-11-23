#!/usr/bin/env python3
"""Convierte la app de Claude (artifact) en la versión web instalable con Supabase.

Uso: python3 build_pwa.py <index_claude.html> <carpeta_salida> <app> <Alumno> <img_alumno>
Ej.:  python3 build_pwa.py entreno-alex/index.html dist/alex alex Alex tiburon.jpg
Cada vez que cambie la app de Claude, se vuelve a ejecutar y se sube la carpeta resultante.
"""
import sys, re, os, json

src, out, APP, ST, STIMG = sys.argv[1:6]
s = open(src, encoding="utf-8").read()


def R(a, b, cnt=1):
    global s
    n = s.count(a)
    assert n == cnt, (n, a[:120])
    s = s.replace(a, b)


# ---------- 1. almacenamiento: Claude → Supabase ----------
i = s.index("/* ---------- store (shared db, local fallback) ---------- */")
j = s.index("\n};\n", i) + 4
STORE = r'''/* ---------- store: Supabase (datos, fotos y cambios en directo) ---------- */
const CFG=Object.assign({},window.SB_CONFIG||{},window.APP_CFG||{});
const sb=(window.supabase&&CFG.url&&CFG.key)?window.supabase.createClient(CFG.url,CFG.key,{auth:{persistSession:true,autoRefreshToken:true,storageKey:'entreno-'+CFG.app}}):null;
const randHex=()=>[...crypto.getRandomValues(new Uint8Array(16))].map(b=>b.toString(16).padStart(2,'0')).join('');
const URLS={};const signQ=new Set();let signT=null;
const BLANK='data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
function mediaUrl(id){
  if(!id)return'';const u=URLS[id];
  if(u&&u.exp>Date.now())return u.url;
  if(!signQ.has(id)){signQ.add(id);clearTimeout(signT);signT=setTimeout(signNow,40)}
  return BLANK;
}
async function signNow(){
  const ids=[...signQ];signQ.clear();if(!ids.length||!sb)return;
  const {data,error}=await sb.storage.from('media').createSignedUrls(ids.map(i=>CFG.app+'/'+i),3600);
  if(error)return;let n=0;
  (data||[]).forEach((d,k)=>{if(d&&d.signedUrl){URLS[ids[k]]={url:d.signedUrl,exp:Date.now()+3300e3};n++}else URLS[ids[k]]={url:'',exp:Date.now()+600e3}});
  if(n)render();
}
const AssetShim={
  async upload(data,opts){
    const id=randHex();const type=(opts&&opts.type)||data.type||'application/octet-stream';
    const {error}=await sb.storage.from('media').upload(CFG.app+'/'+id,data,{contentType:type,upsert:false});
    if(error)throw {code:/exceed|too large|payload|413/i.test(error.message||'')?'too_large':'upload_failed',message:error.message};
    return {id};
  },
  async delete(id){try{await sb.storage.from('media').remove([CFG.app+'/'+id])}catch(e){}}
};
const Store={
  mode:'loading', q:{}, wasDown:false, subbed:false,
  async init(){
    state.assets=AssetShim;
    if(!sb){state.auth='config';render();return}
    const {data}=await sb.auth.getSession();
    if(!data||!data.session){state.auth='out';render();return}
    state.auth='in';this.mode='db';render();
    await this.load();this.sub();
  },
  apply(path,d,w){
    if(path.startsWith('weeks/'))(w||state.weeks)[path.slice(6)]=d;
    else{state.docs[path]=d;state.exists[path]=true;state.loaded[path]=true}
  },
  async load(){
    const {data,error}=await sb.from('docs').select('path,data').eq('app',CFG.app);
    if(error){this.fail();return}
    const w={};(data||[]).forEach(r=>this.apply(r.path,r.data,w));
    DOCS.forEach(p=>{state.loaded[p]=true;if(!(p in state.docs)){state.docs[p]=null;state.exists[p]=false}});
    state.weeks=w;state.ready=true;onData();
  },
  sub(){
    if(this.subbed)return;this.subbed=true;
    sb.channel('docs-'+CFG.app)
      .on('postgres_changes',{event:'*',schema:'public',table:'docs',filter:'app=eq.'+CFG.app},pl=>{
        const r=pl.new;if(r&&r.path){this.apply(r.path,r.data);onData()}})
      .subscribe(st=>{
        if(st==='SUBSCRIBED'&&this.wasDown){this.wasDown=false;this.load()}
        if(st==='CHANNEL_ERROR'||st==='TIMED_OUT'||st==='CLOSED')this.wasDown=true;
      });
    document.addEventListener('visibilitychange',()=>{if(!document.hidden&&state.auth==='in')this.load()});
  },
  fail(){toast('No se pudo conectar con los datos. Revisa tu conexión y recarga.')},
  enqueue(key,fn){const p=(this.q[key]||Promise.resolve()).then(fn).catch(e=>{
      if(e&&/JWT|auth|permission|Sin permiso/i.test(e.message||''))toast('Tu sesión ha caducado. Vuelve a entrar.');
      else toast('No se pudo guardar. Revisa tu conexión e inténtalo de nuevo.');});this.q[key]=p;return p},
  set(path,data){
    state.exists[path]=true;this.apply(path,clone(data));onData();
    return this.enqueue(path,async()=>{const {error}=await sb.rpc('set_doc',{p_app:CFG.app,p_path:path,p_data:data});if(error)throw error});
  },
  update(path,patch){
    const cur=path.startsWith('weeks/')?state.weeks[path.slice(6)]:state.docs[path];
    this.apply(path,deepMerge(clone(cur)||{},clone(patch)));onData();
    return this.enqueue(path,async()=>{const {error}=await sb.rpc('merge_doc',{p_app:CFG.app,p_path:path,p_patch:patch});if(error)throw error});
  }
};

/* ---------- avisos por Telegram ---------- */
const lastNote={};
function notify(to,text,key){
  if(!sb||state.auth!=='in'||!state.role||to===state.role)return;
  key=key||text;if(lastNote[key]&&Date.now()-lastNote[key]<10*60e3)return;lastNote[key]=Date.now();
  sb.functions.invoke('notify',{body:{to,text}}).catch(()=>{});
}
function hookClick(a,b){
  const w=curWeek();if(!w)return;const ST=CFG.student;
  const gk=DAYS[state.gymDay].k;const dn=k=>dayName(k);const N=w.num;
  if(state.role==='admin'){
    if(a==='day-type'&&b.dataset.type==='gym')notify('alumno',`🏋️ Adri te ha preparado entreno para el ${dn(gk)} (Semana ${N}).`,'plan-'+N+gk);
    if(a==='day-type'&&b.dataset.type==='sport')notify('alumno',`⚽ El ${dn(gk)} cuenta como deporte (Semana ${N}).`,'plan-'+N+gk);
    if(a==='day-type'&&b.dataset.type==='rest')notify('alumno',`😴 El ${dn(gk)} no hay gym (Semana ${N}).`,'plan-'+N+gk);
    if(a==='sess-load'){const s=sessions().find(x=>x.id===b.dataset.id);notify('alumno',`🏋️ Adri te ha puesto la sesión «${s?s.name:''}» el ${dn(gk)} (Semana ${N}).`,'plan-'+N+gk)}
    if(a==='weigh-toggle'&&!isWeigh(w,b.dataset.day))notify('alumno',`⚖️ El ${dn(b.dataset.day)} toca pesarse.`,'wg-'+N+b.dataset.day);
    if(a==='photo-toggle'&&!isPhotoDay(w,b.dataset.day))notify('alumno',`📸 El ${dn(b.dataset.day)} toca foto de físico (frente y lado).`,'ph-'+N+b.dataset.day);
    if(a==='close-week'&&state.confirm==='close')notify('alumno',`📋 Adri ha cerrado la Semana ${N}. Entra a leer su valoración.`,'close-'+N);
    if(a==='an-save')notify('alumno','📈 Adri ha analizado tu último pesaje.','an-'+b.dataset.id);
    if(a==='ban-save')notify('alumno','📸 Adri ha comentado tus fotos de físico.','ban-'+b.dataset.id);
  }else{
    if(a==='prog-status'){const g=dayProg(w,gk);if(g.status!==b.dataset.v){
      if(b.dataset.v==='hecho')notify('admin',`✅ ${ST} ha completado el entreno del ${dn(gk)}.`,'st-'+N+gk);
      else notify('admin',`❌ ${ST} no ha podido ir el ${dn(gk)}.`,'st-'+N+gk)}}
    if(a==='weigh-save'){const kg=num(document.getElementById('wi-'+b.dataset.day)?.value);if(kg)notify('admin',`⚖️ ${ST} se ha pesado: ${fmtKg(kg)}.`,'w-'+N+b.dataset.day)}
    if(a==='xa-add'){const k=state.xa.kind==='Otro'?(document.getElementById('xa-other')?.value||'otra actividad'):state.xa.kind;notify('admin',`➕ ${ST} ha apuntado actividad extra el ${dn(gk)}: ${k}.`)}
    if(a==='review-read')notify('admin',`👀 ${ST} ha leído tu valoración de la Semana ${N}.`,'read-'+N);
  }
}
async function tgKey(){
  let k=(state.docs['library/tg']||{}).key;
  if(!k){k=randHex().slice(0,20);await Store.set('library/tg',{key:k})}
  return k;
}
async function tgStatus(){
  const {data}=await sb.from('tg_chats').select('role').eq('app',CFG.app);
  state.tgRoles=[...new Set((data||[]).map(r=>r.role))];render();
}
'''
s = s[:i] + STORE + s[j:]

R("const DOCS=['library/main',", "const DOCS=['library/tg','library/main',")
R("const avSrc=r=>{const id=(state.docs&&state.docs['library/profile']||{})[r];return id?'/_blob/'+id:DEF_AV[r]};",
  "const avSrc=r=>{const id=(state.docs&&state.docs['library/profile']||{})[r];return id?mediaUrl(id):DEF_AV[r]};")
R("const blob=id=>'/_blob/'+id;", "const blob=id=>mediaUrl(id);")
s = s.replace("'ea_role'", "'ea_role_" + APP + "'")
R("role:ls.get('ea_role_" + APP + "')||null,", "role:ls.get('ea_role_" + APP + "')||null, auth:'checking', tgRoles:null,")

# ---------- 2. pantalla de acceso ----------
R("  if(!state.role){app.innerHTML=roleScreen();",
  """  if(state.auth!=='in'){app.innerHTML=loginScreen();document.getElementById('modal').innerHTML='';return}
  if(!state.role){app.innerHTML=roleScreen();""")
R("function roleScreen(){", r'''function loginScreen(){
  if(state.auth==='checking')return '<div class="loading"><img src="img/pino.png" alt="">Cargando…</div>';
  if(state.auth==='config')return '<div class="wrap loading">Falta configurar la conexión (config.js).</div>';
  return `<div class="role-bg"><div class="wrap role-screen">
    <div class="crest-row"><img src="img/pino.png" alt="Escudo del Pino F.S."><div><div class="stars">★★★</div><div class="club">Pino F.S.</div><div class="label">Preparación física</div></div></div>
    <h1 class="splash-title">Entreno<br>${esc(CFG.student)} <span>&amp;</span> Adri</h1>
    <img class="lema" src="img/himno-lema.jpg" alt="Jugamos con el alma">
    <div class="card"><div class="label">Acceso</div>
      <span class="muted">Escribe la contraseña de la app. Solo hay que hacerlo una vez en cada dispositivo.</span>
      <div class="field"><label class="label" for="lg-pass">Contraseña</label><input class="input" id="lg-pass" type="password" autocomplete="current-password" placeholder="Contraseña"></div>
      <button class="btn primary block" data-act="login" ${state.logging?'disabled':''}>${state.logging?'Entrando…':'Entrar'}</button>
    </div>
  </div></div>`;
}
function roleScreen(){''')
R("    <p class=\"lead\">Elige quién eres para entrar.</p>",
  "    <p class=\"lead\">Elige quién eres para entrar.</p>")
# logout link at the end of role screen
m = re.search(r"(function roleScreen\(\)\{.*?)(\n  </div></div>`;\n\})", s, re.S)
assert m
s = s[:m.end(1)] + "\n    <button class=\"btn ghost small\" data-act=\"logout\" style=\"align-self:flex-start\">Cerrar sesión en este dispositivo</button>" + s[m.end(1):]

# ---------- 3. campana de avisos ----------
R("IC.cam}</button>`:''}</div>",
  "IC.cam}</button>`:''}<button class=\"iconbtn avbtn\" data-act=\"tg-open\" title=\"Avisos por Telegram\" aria-label=\"Avisos por Telegram\">${IC.bell}</button></div>")
R("const IC={", "const IC={\n  bell:'<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M6 9a6 6 0 1 1 12 0c0 6 2.5 7.5 2.5 7.5h-17S6 15 6 9\"/><path d=\"M10 20a2 2 0 0 0 4 0\"/></svg>',")
R("function modalHTML(){\n  const m=state.modal;", r'''function modalHTML(){
  const m=state.modal;
  if(m.kind==='tg'){const me=state.role;const on=state.tgRoles&&state.tgRoles.includes(me);
    return `<div class="modal-bg" data-act="modal-bg" style="align-items:center"><div class="modal" role="dialog" aria-label="Avisos por Telegram" style="border-radius:20px">
      <div class="modal-body" style="gap:14px;padding-top:20px">
        <div class="wc-h"><span class="ptick-lg">${IC.bell}</span><div><div class="label">${me==='admin'?'Entrenador':'Alumno'}</div><h2 style="font-size:28px">Avisos por Telegram</h2></div></div>
        <p class="muted" style="margin:0">${me==='admin'?`Te llegará un mensaje cuando ${esc(CFG.student)} marque un entreno como hecho o no hecho, se pese, suba fotos, apunte actividad extra o lea tu valoración.`:'Te llegará un mensaje cuando Adri te prepare un entreno, marque un día de pesaje o de fotos, cierre la semana o analice tu peso o tus fotos.'}</p>
        <div class="statusline ${on?'badge-ok':''}">${state.tgRoles==null?'Comprobando…':on?'✓ Telegram conectado en este perfil':'Todavía no está conectado'}</div>
        ${m.link?`<a class="btn primary block" href="${esc(m.link)}" target="_blank" rel="noopener">Abrir Telegram y pulsar «Iniciar»</a>
          <span class="muted" style="font-size:13px">Cuando el bot te diga «Conectado», vuelve aquí y pulsa «Comprobar».</span>`
          :`<button class="btn primary block" data-act="tg-link">${on?'Conectar otro dispositivo':'Conectar Telegram'}</button>`}
        <div class="row"><button class="btn" data-act="tg-check" style="flex:1">Comprobar</button>${on?`<button class="btn" data-act="tg-test" style="flex:1">Enviar prueba</button>`:''}</div>
        <button class="btn ghost" data-act="modal-close">Cerrar</button>
      </div></div></div>`;}''')

# ---------- 4. acciones nuevas + enganches de avisos ----------
R("document.addEventListener('click',ev=>{\n  const b=ev.target.closest('[data-act]');if(!b)return;\n  const a=b.dataset.act;const w=curWeek();",
  "document.addEventListener('click',ev=>{\n  const b=ev.target.closest('[data-act]');if(!b)return;\n  const a=b.dataset.act;const w=curWeek();\n  try{hookClick(a,b)}catch(e){}")
R("    case'role':", r'''    case'login':{const pw=document.getElementById('lg-pass')?.value||'';if(!pw){toast('Escribe la contraseña.');return}
      state.logging=true;render();
      sb.auth.signInWithPassword({email:CFG.email,password:pw}).then(({error})=>{state.logging=false;
        if(error){toast('Contraseña incorrecta.');render();return}Store.init()});return}
    case'logout':sb.auth.signOut().then(()=>{state.auth='out';state.ready=false;render()});return;
    case'tg-open':state.modal={kind:'tg'};state.tgRoles=null;tgStatus();break;
    case'tg-link':tgKey().then(k=>{state.modal={kind:'tg',link:`https://t.me/${CFG.bot}?start=${CFG.app}_${state.role}_${k}`};render()});return;
    case'tg-check':state.tgRoles=null;tgStatus();break;
    case'tg-test':sb.functions.invoke('notify',{body:{to:state.role,text:'🔔 Prueba: los avisos de la app funcionan.'}}).then(()=>toast('Prueba enviada. Mira tu Telegram.')).catch(()=>toast('No se pudo enviar la prueba.'));return;
    case'role':''')
R("await saveBody({entries:list});if(old&&old!==r.id)A.delete(old).catch(()=>{});toast('Foto subida')}",
  "await saveBody({entries:list});if(old&&old!==r.id)A.delete(old).catch(()=>{});toast('Foto subida');notify('admin',`📸 ${CFG.student} ha subido una foto de físico.`,'body-'+p.weekNum+p.day)}")
R("        toast(mx==null?", "        notify('admin',`🏆 ${CFG.student}: ${mx==null?'primer máximo':'nuevo máximo'} en ${ex.name}: ${fmtKg(kg)}.`);\n        toast(mx==null?")
R("    else if(f==='ask-kg')click('[data-act=\"ask-save\"]');",
  "    else if(f==='ask-kg')click('[data-act=\"ask-save\"]');\n    else if(ev.target.id==='lg-pass')click('[data-act=\"login\"]');")

# ---------- 5. documento completo con cabecera de app instalable ----------
title = re.search(r"<title>(.*?)</title>", s).group(1)
s = re.sub(r"<title>.*?</title>\n", "", s, count=1)
s = s.replace('<script>\n/* ---------- constants', '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.118.0/dist/umd/supabase.min.js"></script>\n<script src="../config.js"></script>\n<script>\nwindow.APP_CFG=' + json.dumps({"app": APP, "student": ST, "email": APP + "@entreno.app"}) + ';\n</script>\n<script>\n/* ---------- constants', 1)
assert 'supabase.min.js' in s
head = f'''<!doctype html>
<html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="img/icon-192.png">
<link rel="apple-touch-icon" href="img/icon-180.png">
<meta name="theme-color" content="#0C0B09">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Entreno">
<style>:root{{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0;font:14px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
</head><body>
'''
s = head + s + "\n</body></html>\n"

os.makedirs(out, exist_ok=True)
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(s)
manifest = {
    "name": title.replace("&amp;", "&"), "short_name": "Entreno", "start_url": "./", "scope": "./",
    "display": "standalone", "background_color": "#0C0B09", "theme_color": "#0C0B09", "lang": "es",
    "icons": [{"src": "img/icon-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "img/icon-512.png", "sizes": "512x512", "type": "image/png"},
              {"src": "img/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}
open(os.path.join(out, "manifest.webmanifest"), "w").write(json.dumps(manifest, ensure_ascii=False, indent=1))
print("ok", out, len(s))
