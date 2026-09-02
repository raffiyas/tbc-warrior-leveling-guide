from pathlib import Path

p = Path('index.html')
html = p.read_text(encoding='utf-8')

# Idempotent migration.
if 'id="my-warrior"' in html:
    print('V3.1 already applied')
    raise SystemExit(0)

html = html.replace(
    'Guía interactiva Fury Warrior para TBC Anniversary: talentos, armas, tankeo, rotación, addons y macros.',
    'Warrior Leveling Companion para TBC Anniversary: perfil Xhena, talentos, comparador de ítems, armas, tankeo, addons y macros.'
)

css = r'''
/* V3.1 — My Warrior + embedded comparator */
.profile-grid{display:grid;grid-template-columns:1.15fr .85fr;gap:14px}.profile-card{padding:17px;border:1px solid #39424d;border-radius:12px;background:#11161b}.profile-fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:12px}.profile-fields label{font-size:.78rem;color:var(--m);font-weight:700}.profile-fields input,.profile-fields select{display:block;width:100%;margin-top:4px;background:#0c1015;color:var(--t);border:1px solid var(--b);border-radius:8px;padding:9px}.profile-fields .wide{grid-column:1/-1}.profile-actions{display:flex;gap:9px;flex-wrap:wrap;margin-top:13px}.actionbtn{display:inline-block;border:1px solid #725421;background:#2b2112;color:#ffd98d;border-radius:9px;padding:9px 13px;font-weight:800;cursor:pointer}.actionbtn:hover{text-decoration:none;filter:brightness(1.12)}.profile-stat{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center;padding:10px 0;border-bottom:1px solid #2a323c}.profile-stat:last-child{border-bottom:0}.profile-stat span{color:var(--m)}.profile-stat strong{text-align:right}.sync-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--ok);margin-right:6px;box-shadow:0 0 0 3px #70c48f1f}.compare-shell{border:1px solid #39424d;border-radius:12px;overflow:hidden;background:#0b0d10}.compare-frame{display:block;width:100%;height:1080px;border:0;background:#0b0d10}.compare-top{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:14px}.beta{font-size:.72rem;color:#ffcf73;border:1px solid #66501f;border-radius:999px;padding:2px 7px;background:#2c2412}@media(max-width:850px){.profile-grid,.profile-fields{grid-template-columns:1fr}.profile-fields .wide{grid-column:auto}.compare-frame{height:1380px}}
'''
html = html.replace('</style>', css + '\n</style>', 1)

html = html.replace(
    '<nav class="links"><a href="#talentos">Talentos</a>',
    '<nav class="links"><a href="#my-warrior">My Warrior</a><a href="#talentos">Talentos</a>',
    1
)
html = html.replace(
    '<a href="#addons">Addons</a><a href="#macros">Macros</a>',
    '<a href="#comparador">Comparador</a><a href="#addons">Addons</a><a href="#macros">Macros</a>',
    1
)
html = html.replace(
    '<aside class="card"><strong>Contenido</strong><a href="#resumen">Resumen</a>',
    '<aside class="card"><strong>Contenido</strong><a href="#my-warrior">My Warrior · Xhena</a><a href="#resumen">Resumen</a>',
    1
)
html = html.replace(
    '<a href="#addons">Addons útiles</a>',
    '<a href="#comparador">Comparador de ítems</a><a href="#addons">Addons útiles</a>',
    1
)

profile = r'''
<section id="my-warrior" class="card">
<h2>My Warrior · Xhena</h2>
<p class="muted"><span class="sync-dot"></span>Perfil local V3.1. El nivel se sincroniza con la guía; el arma registrada se toma del comparador cuando exista.</p>
<div class="profile-grid">
  <div class="profile-card">
    <div class="kicker">Perfil</div>
    <div class="profile-fields">
      <label>Personaje<input id="profileName" value="Xhena" autocomplete="off"></label>
      <label>Nivel<input id="profileLevel" type="number" min="1" max="70" value="14"></label>
      <label>Spec<select id="profileSpec"><option selected>Fury</option><option>Arms</option><option>Protection</option></select></label>
      <label>Región<select id="profileRegion"><option value="us" selected>Americas & Oceania</option><option value="eu">Europe</option><option value="kr">Korea</option><option value="tw">Taiwan</option></select></label>
      <label class="wide">Realm<input id="profileRealm" placeholder="Escribe tu realm cuando quieras"></label>
    </div>
    <div class="profile-actions"><a class="actionbtn" href="#comparador">Comparar upgrade</a><button class="actionbtn" id="profileArmory" type="button">Buscar en Armory</button></div>
  </div>
  <div class="profile-card">
    <div class="kicker">Estado actual</div>
    <div class="profile-stat"><span>Raza / clase</span><strong>Human Warrior</strong></div>
    <div class="profile-stat"><span>Arma registrada</span><strong id="profileWeapon">Sincronizando…</strong></div>
    <div class="profile-stat"><span>Próximo hito</span><strong id="profileMilestone">—</strong></div>
    <div class="profile-stat"><span>Dual Wield</span><strong id="profileDualWield">—</strong></div>
  </div>
</div>
<div class="note"><strong>Próxima fase:</strong> Vercel permitirá que “Actualizar personaje” consulte Blizzard desde una función backend sin exponer credenciales en el navegador.</div>
</section>
'''
html = html.replace('<section id="resumen" class="card">', profile + '\n<section id="resumen" class="card">', 1)

comparator = r'''
<section id="comparador" class="card">
<div class="compare-top"><div><div class="kicker">V3 · Gear tools</div><h2 style="margin:.15rem 0">Comparador de ítems</h2></div><a class="actionbtn" href="./compare.html" target="_blank" rel="noopener">Abrir pantalla completa ↗</a></div>
<p class="muted">El comparador que ya construimos ahora vive también dentro de la guía. Sus datos se guardan en el mismo dominio de Vercel, por lo que My Warrior puede reutilizar el nivel y el arma equipada.</p>
<div class="compare-shell"><iframe class="compare-frame" src="./compare.html" title="Comparador de armas de Xhena" loading="lazy"></iframe></div>
</section>
'''
html = html.replace('<section id="addons" class="card">', comparator + '\n<section id="addons" class="card">', 1)

js = r'''

// V3.1 — My Warrior shared profile
(function(){
  const PROFILE_KEY='xhenaProfileV31';
  const $p=id=>document.getElementById(id);
  const clamp=v=>Math.max(1,Math.min(70,parseInt(v,10)||14));
  const read=()=>{try{return JSON.parse(localStorage.getItem(PROFILE_KEY)||'null')||{}}catch(e){return {}}};
  const write=patch=>{const next={...read(),...patch};localStorage.setItem(PROFILE_KEY,JSON.stringify(next));return next};
  const milestones=[[16,'Shield Block'],[20,'Dual Wield'],[24,'Execute'],[30,'Berserker Stance'],[34,'Sweeping Strikes'],[36,'Whirlwind'],[40,'Bloodthirst'],[50,'Rampage'],[62,'Victory Rush'],[64,'Spell Reflection'],[70,'Intervene']];
  function comparatorState(){try{return JSON.parse(localStorage.getItem('xhena-weapon-compare-v3')||'null')||{}}catch(e){return {}}}
  function refresh(level){
    const l=clamp(level);
    const comp=comparatorState();
    if($p('profileWeapon'))$p('profileWeapon').textContent=comp.eqName||'Aún no registrada';
    const next=milestones.find(([n])=>n>l);
    if($p('profileMilestone'))$p('profileMilestone').textContent=next?`${next[1]} · ${next[0]}`:'Nivel máximo';
    if($p('profileDualWield'))$p('profileDualWield').textContent=l>=20?'Desbloqueado':`Faltan ${20-l} niveles`;
  }
  function setLevel(value,fromProfile=false){
    const l=clamp(value); localStorage.setItem('tbcWarriorLevel',String(Math.max(10,l))); write({level:l});
    if($p('profileLevel'))$p('profileLevel').value=l;
    if(typeof slider!=='undefined'&&slider){slider.value=Math.max(10,l);if(fromProfile)slider.dispatchEvent(new Event('input',{bubbles:true}));}
    refresh(l);
  }
  const saved=read(); const comp=comparatorState(); const level=clamp(saved.level||comp.level||localStorage.getItem('tbcWarriorLevel')||14);
  if($p('profileName'))$p('profileName').value=saved.name||'Xhena';
  if($p('profileSpec'))$p('profileSpec').value=saved.spec||'Fury';
  if($p('profileRegion'))$p('profileRegion').value=saved.region||'us';
  if($p('profileRealm'))$p('profileRealm').value=saved.realm||'';
  setLevel(level,false);
  $p('profileLevel')?.addEventListener('change',e=>setLevel(e.target.value,true));
  if(typeof slider!=='undefined'&&slider)slider.addEventListener('input',e=>{const l=clamp(e.target.value);if($p('profileLevel'))$p('profileLevel').value=l;write({level:l});refresh(l)});
  $p('profileName')?.addEventListener('change',e=>write({name:e.target.value.trim()||'Xhena'}));
  $p('profileSpec')?.addEventListener('change',e=>write({spec:e.target.value}));
  $p('profileRegion')?.addEventListener('change',e=>write({region:e.target.value}));
  $p('profileRealm')?.addEventListener('change',e=>write({realm:e.target.value.trim()}));
  $p('profileArmory')?.addEventListener('click',()=>{const name=encodeURIComponent(($p('profileName')?.value||'Xhena').trim());const region=$p('profileRegion')?.value||'us';window.open(`https://worldofwarcraft.blizzard.com/en-us/classic/${region}/armory?q=${name}`,'_blank','noopener')});
  window.addEventListener('storage',()=>refresh(clamp($p('profileLevel')?.value||level)));
  window.addEventListener('focus',()=>refresh(clamp($p('profileLevel')?.value||level)));
})();
'''
html = html.replace('\n</script>\n</body>', js + '\n</script>\n</body>', 1)

p.write_text(html, encoding='utf-8')
print('Applied V3.1 to index.html')
