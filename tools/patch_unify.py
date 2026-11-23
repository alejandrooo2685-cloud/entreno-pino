import sys,re
p,APP,ST=sys.argv[1],sys.argv[2],sys.argv[3];s=open(p,encoding='utf-8').read()
def R(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:110]); s=s.replace(a,b)
# shared session across student and coach pages
R("storageKey:'entreno-'+CFG.app}","storageKey:'entreno-session'}")
R("role:ls.get('ea_role_%s')||null, auth:'checking',"%APP,"role:null, coach:false, auth:'checking',")
# role from logged-in account
R("    state.auth='in';this.mode='db';render();\n    await this.load();this.sub();",
  """    const em=((data.session.user||{}).email||'').toLowerCase();
    if(em.startsWith('adri@')){state.coach=true;state.role='admin'}
    else if(em===CFG.email){state.coach=false;state.role='alumno'}
    else{await sb.auth.signOut();state.auth='out';state.wrongAcc=true;render();return}
    state.auth='in';this.mode='db';render();
    await this.load();this.sub();""")
# notify includes app; coach telegram uses app 'adri'
R("sb.functions.invoke('notify',{body:{to,text}}).catch(()=>{});","sb.functions.invoke('notify',{body:{to,text,app:CFG.app}}).catch(()=>{});")
R("""async function tgKey(){
  let k=(state.docs['library/tg']||{}).key;
  if(!k){k=randHex().slice(0,20);await Store.set('library/tg',{key:k})}
  return k;
}
async function tgStatus(){
  const {data}=await sb.from('tg_chats').select('role').eq('app',CFG.app);""",
"""const tgApp=()=>state.coach?'adri':CFG.app;
async function tgKey(){
  if(state.coach){
    const {data}=await sb.from('docs').select('data').eq('app','adri').eq('path','library/tg').maybeSingle();
    let k=data&&data.data&&data.data.key;
    if(!k){k=randHex().slice(0,20);await sb.rpc('set_doc',{p_app:'adri',p_path:'library/tg',p_data:{key:k}})}
    return k;
  }
  let k=(state.docs['library/tg']||{}).key;
  if(!k){k=randHex().slice(0,20);await Store.set('library/tg',{key:k})}
  return k;
}
async function tgStatus(){
  const {data}=await sb.from('tg_chats').select('role').in('app',[tgApp()]);""")
R("link:`https://t.me/${CFG.bot}?start=${CFG.app}_${state.role}_${k}`","link:`https://t.me/${CFG.bot}?start=${tgApp()}_${state.role}_${k}`")
R("sb.functions.invoke('notify',{body:{to:state.role,text:'🔔 Prueba: los avisos de la app funcionan.'}})",
  "sb.functions.invoke('notify',{body:{to:state.role,app:CFG.app,text:'🔔 Prueba: los avisos de la app funcionan.'}})")
# role screen: only the student's own card
m=re.search(r'      <button class="role-card" data-act="role" data-role="admin">.*?</button>\n',s);assert m
s=s[:m.start()]+s[m.end():]
R('<p class="lead">Elige quién eres para entrar.</p>','<p class="lead">Pulsa tu tarjeta para entrar.</p>')
# header: coach goes back to the student picker
R("${admin?'Adri':'%s'}</span></button>"%ST,"${admin?'Adri · %s':'%s'}</span></button>"%(ST,ST))
R("    case'role':state.role=b.dataset.role;ls.set('ea_role_%s',state.role);state.tab='entreno';break;"%APP,
  "    case'role':state.role='alumno';state.tab='entreno';break;")
R("    case'switch-role':state.role=null;state.modal=null;state.editSess=null;ls.set('ea_role_%s','');break;"%APP,
  "    case'switch-role':if(state.coach){location.href='../adri/';return}state.role=null;state.modal=null;state.editSess=null;break;")
# login screen: wrong account note + coach link
R("""      <button class="btn primary block" data-act="login" ${state.logging?'disabled':''}>${state.logging?'Entrando…':'Entrar'}</button>
    </div>""","""      <button class="btn primary block" data-act="login" ${state.logging?'disabled':''}>${state.logging?'Entrando…':'Entrar'}</button>
      ${state.wrongAcc?'<span class="muted" style="font-size:13px">Esta no es la cuenta de esta app. Entra con su contraseña.</span>':''}
    </div>
    <a class="btn ghost small" href="../adri/" style="align-self:flex-start;text-decoration:none">¿Eres el entrenador? Entra aquí</a>""")
R("case'logout':sb.auth.signOut().then(()=>{state.auth='out';state.ready=false;render()});return;",
  "case'logout':sb.auth.signOut().then(()=>{state.auth='out';state.ready=false;state.role=null;render()});return;")
R("const CHANGELOG=[\n","""const CHANGELOG=[
  {v:'2026-11-23',title:'Novedades',items:[
    'La app se ha mudado fuera de Claude: ahora se instala como app propia, con su icono, en el móvil y en el PC. Todos los datos, fotos y vídeos se han copiado.',
    'Avisos por Telegram: pulsa la campana 🔔 de arriba y «Conectar Telegram» para recibir avisos en el móvil.',
    'El entrenador tiene ahora su propia app y cuenta: desde ahí elige a qué alumno entrena. El alumno entra directo a su app.'
  ]},
""")
open(p,'w',encoding='utf-8').write(s)
open(sys.argv[4],'w').write(re.findall(r'<script>\n(/\* ---------- constants.*?)</script>',s,re.S)[0])
