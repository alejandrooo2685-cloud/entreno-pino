import sys,re
p=sys.argv[1];s=open(p,encoding='utf-8').read()
def R(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:110]); s=s.replace(a,b)
SHP="@shared/library/exercises"
R("const DOCS=['library/tg',","const DOCS=['%s','library/tg',"%SHP)
# store: paths '@shared/...' live in app 'shared'
R("""    const {data,error}=await sb.from('docs').select('path,data').eq('app',CFG.app);
    if(error){this.fail();return}
    const w={};(data||[]).forEach(r=>this.apply(r.path,r.data,w));""",
"""    const {data,error}=await sb.from('docs').select('app,path,data').in('app',[CFG.app,'shared']);
    if(error){this.fail();return}
    const w={};(data||[]).forEach(r=>this.apply(r.app==='shared'?'@shared/'+r.path:r.path,r.data,w));""")
R("""      .on('postgres_changes',{event:'*',schema:'public',table:'docs',filter:'app=eq.'+CFG.app},pl=>{
        const r=pl.new;if(r&&r.path){this.apply(r.path,r.data);onData()}})""",
"""      .on('postgres_changes',{event:'*',schema:'public',table:'docs',filter:'app=eq.'+CFG.app},pl=>{
        const r=pl.new;if(r&&r.path){this.apply(r.path,r.data);onData()}})
      .on('postgres_changes',{event:'*',schema:'public',table:'docs',filter:'app=eq.shared'},pl=>{
        const r=pl.new;if(r&&r.path){this.apply('@shared/'+r.path,r.data);onData()}})""")
R("sb.rpc('set_doc',{p_app:CFG.app,p_path:path,p_data:data})","sb.rpc('set_doc',{...dest(path),p_data:data})")
R("sb.rpc('merge_doc',{p_app:CFG.app,p_path:path,p_patch:patch})","sb.rpc('merge_doc',{...dest(path),p_patch:patch})")
R("const Store={","const dest=path=>path.startsWith('@shared/')?{p_app:'shared',p_path:path.slice(8)}:{p_app:CFG.app,p_path:path};\nconst Store={")
# library: exercises + categories come from the shared doc
R("const updateLib=p=>Store.update('library/main',p);","""const SH_KEYS=['exercises','customGroups','customWorks'];
const SH=()=>state.docs['%s']||null;
const shSrc=()=>SH()||LIB();
const updateLib=p=>{const a={},b={};Object.keys(p).forEach(k=>(SH_KEYS.includes(k)?a:b)[k]=p[k]);
  if(Object.keys(a).length)Store.update('%s',a);if(Object.keys(b).length)Store.update('library/main',b)};"""%(SHP,SHP))
R("const libArr=k=>Array.isArray(LIB()[k])?LIB()[k]:[];","const libArr=k=>{const src=SH_KEYS.includes(k)?shSrc():LIB();return Array.isArray(src[k])?src[k]:[]};")
s=s.replace("(LIB().customGroups||[])","(shSrc().customGroups||[])").replace("(LIB().customWorks||[])","(shSrc().customWorks||[])")
assert "LIB().customGroups" not in s and "LIB().customWorks" not in s
# copy session from another student (coach only)
R("""      :`<div class="empty"><span>Todavía no hay sesiones. Ponle nombre a la primera y pulsa «Crear sesión».</span></div>`}""",
"""      :`<div class="empty"><span>Todavía no hay sesiones. Ponle nombre a la primera y pulsa «Crear sesión».</span></div>`}
    ${state.coach&&otherStudents().length?`<button class="btn block" data-act="sess-import-open" style="border-style:dashed">Copiar una sesión de ${esc(otherStudents().map(x=>x.name).join(' o '))}</button>`:''}""")
R("function sessView(){",r'''const otherStudents=()=>((window.SB_CONFIG||{}).students||[]).filter(x=>x.app!==CFG.app);
async function loadImport(){
  const apps=otherStudents().map(x=>x.app);state.modal={kind:'import',loading:true,data:[]};render();
  const {data}=await sb.from('docs').select('app,data').in('app',apps).eq('path','library/sessions');
  state.modal={kind:'import',loading:false,data:apps.map(a=>({app:a,name:(otherStudents().find(x=>x.app===a)||{}).name||a,list:((data||[]).find(r=>r.app===a)||{data:{}}).data.list||[]}))};render();
}
function importModal(m){
  return `<div class="modal-bg" data-act="modal-bg"><div class="modal" role="dialog" aria-label="Copiar sesión">
    <div class="modal-head"><div class="card-head" style="align-items:center"><h3>Copiar sesión a ${esc(CFG.student)}</h3><button class="btn small" data-act="modal-close">Cerrar</button></div>
    <span class="muted" style="font-size:13px">Se crea una copia en ${esc(CFG.student)}. Si luego la cambias, la del otro alumno no se toca.</span></div>
    <div class="modal-body">${m.loading?'<div class="muted">Cargando sesiones…</div>':m.data.map(g=>`<div class="label">De ${esc(g.name)}</div>
      ${g.list.length?g.list.map(s=>{const n=(s.exercises||[]).length;return `<div class="sessrow"><div class="info"><b>${esc(s.name)}</b><span>${n} ejercicio${n===1?'':'s'}</span></div>
        <div class="acts"><button class="btn small primary" data-act="sess-import" data-app="${esc(g.app)}" data-id="${esc(s.id)}">Copiar</button></div></div>`}).join(''):`<div class="empty"><span>${esc(g.name)} no tiene sesiones.</span></div>`}`).join('')}</div>
  </div></div>`;
}
function sessView(){''')
R("  if(m.kind==='tg'){","  if(m.kind==='import')return importModal(m);\n  if(m.kind==='tg'){")
R("    case'sess-new':","""    case'sess-import-open':loadImport();return;
    case'sess-import':{const g=(state.modal.data||[]).find(x=>x.app===b.dataset.app);const s=g&&g.list.find(x=>x.id===b.dataset.id);if(!s)break;
      const exists=sessions().some(x=>norm(x.name)===norm(s.name));
      saveSessions([...sessions(),{id:uid(),name:exists?s.name+' (de '+g.name+')':s.name,exercises:(s.exercises||[]).map(e=>({...normEx(e),uid:uid()}))}]);
      toast(`Sesión «${s.name}» copiada de ${g.name}`);state.modal=null;break}
    case'sess-new':""")
R("const CHANGELOG=[\n","""const CHANGELOG=[
  {v:'2026-11-24',title:'Novedades',items:[
    'Ejercicios compartidos: la biblioteca de ejercicios del entrenador es la misma para todos los alumnos. Lo que crea para uno, lo puede usar con los demás.',
    'Las sesiones siguen siendo de cada alumno, pero el entrenador puede copiar una sesión de otro alumno desde la pestaña Sesiones.'
  ]},
""")
open(p,'w',encoding='utf-8').write(s)
open(sys.argv[2],'w').write(re.findall(r'<script>\n(/\* ---------- constants.*?)</script>',s,re.S)[0])
