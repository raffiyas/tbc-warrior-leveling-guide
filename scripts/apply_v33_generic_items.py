from pathlib import Path

# --- Backend: robust name lookup + armor/general stats ---
p = Path('api/item-search.js')
s = p.read_text(encoding='utf-8')

s = s.replace(
"  s = s.replace(/\\|c[0-9a-f]{8}/ig, '').replace(/\\|r/ig, '').replace(/^\\[|\\]$/g, '').trim();\n  return { text: s, itemId: idMatch ? Number(idMatch[1]) : null };",
"  s = s.replace(/\\|c[0-9a-f]{8}/ig, '').replace(/\\|r/ig, '').replace(/^\\[|\\]$/g, '').trim();\n  // WoW/chat/UI copies may wrap the item name in quotes. Strip only matching outer quotes.\n  if ((s.startsWith('\\\"') && s.endsWith('\\\"')) || (s.startsWith('“') && s.endsWith('”')) || (s.startsWith(\"'\") && s.endsWith(\"'\"))) s = s.slice(1, -1).trim();\n  return { text: s, itemId: idMatch ? Number(idMatch[1]) : null };"
)

s = s.replace(
"  const dps = tooltip.match(/\\(([0-9.]+)\\s+damage per second\\)/i);\n  const stat = label => {",
"  const dps = tooltip.match(/\\(([0-9.]+)\\s+damage per second\\)/i);\n  const armorMatch = tooltip.match(/(\\d+(?:\\.\\d+)?)\\s+Armor/i);\n  const stat = label => {"
)

s = s.replace(
"    stamina: Number(equip.sta ?? stat('Stamina') ?? 0) || 0,\n    wowheadUrl:",
"    stamina: Number(equip.sta ?? stat('Stamina') ?? 0) || 0,\n    intellect: Number(equip.int ?? stat('Intellect') ?? 0) || 0,\n    spirit: Number(equip.spi ?? equip.spr ?? stat('Spirit') ?? 0) || 0,\n    armor: Number(equip.armor ?? (armorMatch ? armorMatch[1] : 0) ?? 0) || 0,\n    kind: (dmg || speed || dps || /hand|ranged|bow|gun|crossbow|thrown|wand/i.test(inventorySlot)) ? 'weapon' : (armorMatch || Number(equip.armor || 0) > 0 ? 'armor' : 'other'),\n    wowheadUrl:"
)

anchor = "async function fetchWowhead(term, isId = false) {"
if 'async function fetchSuggestionId' not in s:
    helper = r'''function extractItemId(value = '') {
  const m = String(value).match(/(?:item=|\/item\/)(\d+)/i);
  return m ? Number(m[1]) : null;
}

async function fetchSuggestionId(term) {
  const q = String(term || '').trim();
  if (!q) return null;
  try {
    const response = await fetch(`https://www.wowhead.com/search/suggestions-open-search?q=${encodeURIComponent(q)}`, {
      headers: {
        'accept': 'application/json,text/plain;q=0.9,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (compatible; XhenaWarriorCompanion/1.1)'
      },
      redirect: 'follow'
    });
    if (!response.ok) return null;
    const data = await response.json();
    if (!Array.isArray(data)) return null;
    const names = Array.isArray(data[1]) ? data[1] : [];
    const urls = Array.isArray(data[3]) ? data[3] : [];
    let idx = names.findIndex(name => norm(name) === norm(q));
    if (idx < 0) idx = names.findIndex(name => norm(name).includes(norm(q)) || norm(q).includes(norm(name)));
    if (idx < 0) return null;
    return extractItemId(urls[idx] || '');
  } catch (_) {
    return null;
  }
}

'''
    s = s.replace(anchor, helper + anchor)

old = """      if (!item && exact) {\n        item = exact;\n        resolvedFrom = 'fuzzy-name';\n      }\n"""
new = """      if (!item) {\n        const suggestionId = await fetchSuggestionId(baseName || cleaned.text);\n        if (suggestionId) {\n          item = await fetchWowhead(suggestionId, true);\n          resolvedFrom = 'suggestion';\n        }\n      }\n\n      if (!item && exact) {\n        item = exact;\n        resolvedFrom = 'fuzzy-name';\n      }\n"""
s = s.replace(old, new)
p.write_text(s, encoding='utf-8')

# --- Frontend: generic item comparison ---
p = Path('compare.html')
h = p.read_text(encoding='utf-8')

h = h.replace('Comparador de armas — Xhena · TBC Warrior', 'Comparador de ítems — Xhena · TBC Warrior')
h = h.replace('Comparador de armas para Warrior Fury en TBC Anniversary con búsqueda por nombre, Wowhead tooltips y cálculo de DPS/valor.', 'Comparador de ítems para Warrior Fury en TBC Anniversary: armas y armadura con búsqueda por nombre, Wowhead tooltips y comparación transparente.')
h = h.replace('V3.2 · Paste & Search', 'V3.3 · Items + Gear')
h = h.replace('Xhena · Weapon Comparator', 'Xhena · Item Comparator')
h = h.replace('Compara armas por weapon DPS, golpe medio, Strength/AP y costo. El cálculo de “DPS estimado” suma solo el aporte directo de Strength al autoattack: <strong>1 STR = 2 AP</strong> y <strong>14 AP ≈ 1 DPS</strong>. Crit, hit, procs y supervivencia se muestran aparte y no se inventan.', 'Compara <strong>armas y armadura</strong>. Para armas se usa weapon DPS + aporte directo de Strength/AP. Para armor se comparan Armor y stats por separado, sin inventar un “score” único cuando hay trade-offs.')

# Add Other/Armor option to type selectors.
h = h.replace('<option value="axe">Axe</option></select>', '<option value="axe">Axe</option><option value="other">Armor / Other</option></select>')

# Add slot + armor fields after Type for both sides.
h = h.replace(
'<label>Wowhead ID<input id="eqId" type="number" value="3192"></label><label>Tipo<select id="eqType">',
'<label>Wowhead ID<input id="eqId" type="number" value="3192"></label><label>Tipo<select id="eqType">', 1)
eq_marker = '</select></label>\n<label>Daño mín.<input id="eqMin"'
if 'id="eqSlot"' not in h:
    h = h.replace(eq_marker, '</select></label>\n<label>Slot<input id="eqSlot" value="Two-Hand" readonly></label><label>Armor<input id="eqArmor" type="number" value="0"></label>\n<label>Daño mín.<input id="eqMin"', 1)
ca_marker = '</select></label>\n<label>Daño mín.<input id="caMin"'
if 'id="caSlot"' not in h:
    h = h.replace(ca_marker, '</select></label>\n<label>Slot<input id="caSlot" value="Two-Hand" readonly></label><label>Armor<input id="caArmor" type="number" value="0"></label>\n<label>Daño mín.<input id="caMin"', 1)

# Add Intellect + Spirit fields after Stamina on each side.
h = h.replace('<label>Stamina<input id="eqSta" type="number" value="2"></label><label>Precio copper', '<label>Stamina<input id="eqSta" type="number" value="2"></label><label>Spirit<input id="eqSpi" type="number" value="0"></label><label>Intellect<input id="eqInt" type="number" value="0"></label><label>Precio copper')
h = h.replace('<label>Stamina<input id="caSta" type="number" value="0"></label><label>Precio copper', '<label>Stamina<input id="caSta" type="number" value="0"></label><label>Spirit<input id="caSpi" type="number" value="0"></label><label>Intellect<input id="caInt" type="number" value="0"></label><label>Precio copper')

h = h.replace(
"const ids=['level','eqName','eqId','eqType','eqMin','eqMax','eqDps','eqSpeed','eqStr','eqAgi','eqSta','eqPrice','caName','caId','caType','caMin','caMax','caDps','caSpeed','caStr','caAgi','caSta','caPrice'];",
"const ids=['level','eqName','eqId','eqType','eqSlot','eqArmor','eqMin','eqMax','eqDps','eqSpeed','eqStr','eqAgi','eqSta','eqSpi','eqInt','eqPrice','caName','caId','caType','caSlot','caArmor','caMin','caMax','caDps','caSpeed','caStr','caAgi','caSta','caSpi','caInt','caPrice'];"
)

start = h.index('function compare(){')
end = h.index('\nfunction reset(){', start)
new_compare = r'''function saveState(){const save={};ids.forEach(i=>{if($(i))save[i]=$(i).value});localStorage.setItem('xhena-weapon-compare-v3',JSON.stringify(save))}
function signed(v,d=0){const x=Number(v)||0;return `${x>=0?'+':''}${d?fmt(x):x}`}
function compare(){
  const eqSlot=($('eqSlot').value||'').toLowerCase(), caSlot=($('caSlot').value||'').toLowerCase();
  const eqWeapon=n('eqDps')>0 || /hand|ranged/.test(eqSlot), caWeapon=n('caDps')>0 || /hand|ranged/.test(caSlot);
  $('eqWh').href=wh($('eqId').value);$('caWh').href=wh($('caId').value);
  if(eqSlot && caSlot && eqSlot!==caSlot && !eqWeapon && !caWeapon){
    $('result').innerHTML=`<div class="k">Resultado</div><h2 class="flat">Slots distintos</h2><p>Estás comparando <strong>${$('eqName').value}</strong> (${ $('eqSlot').value }) con <strong>${$('caName').value}</strong> (${ $('caSlot').value }). Para una recomendación útil, compara objetos del mismo slot.</p>`;saveState();return;
  }
  if(eqWeapon && caWeapon){
    const eq=n('eqDps')+n('eqStr')*2/14,ca=n('caDps')+n('caStr')*2/14,g=ca-eq,raw=n('caDps')-n('eqDps'),ap=(n('caStr')-n('eqStr'))*2,avg=((n('caMin')+n('caMax'))-(n('eqMin')+n('eqMax')))/2,price=n('caPrice');
    let v='Sidegrade / depende de stats',cl='flat';if(g>=1){v='Upgrade fuerte para leveling';cl='up'}else if(g>.2){v='Upgrade moderado';cl='up'}else if(g<-.2){v='Downgrade de daño';cl='down'}
    const human=['sword','mace'].includes($('caType').value)?'Sí: Human obtiene bonus racial con swords y maces':'No';const value=price<=0?'Excelente: fue drop/gratis':g>0?`${fmt(g/(price/10000))} DPS estimado por gold`:'Mala compra por daño';
    $('result').innerHTML=`<div class="k">Resultado · Weapon</div><h2 class="${cl}">${v}</h2><div class="metrics"><div class="metric"><span>Weapon DPS</span><strong>${signed(raw,1)}</strong></div><div class="metric"><span>DPS estimado + STR</span><strong>${signed(g,1)}</strong></div><div class="metric"><span>Attack Power</span><strong>${signed(ap,1)}</strong></div><div class="metric"><span>Golpe medio</span><strong>${signed(avg,1)}</strong></div></div><p><strong>${$('caName').value}</strong>: ${fmt(ca)} DPS estimado de autoattack vs ${fmt(eq)} de <strong>${$('eqName').value}</strong>. <strong>Valor:</strong> ${value}. <strong>Racial:</strong> ${human}.</p><p class="muted">AGI ${signed(n('caAgi')-n('eqAgi'))} · STA ${signed(n('caSta')-n('eqSta'))} · SPI ${signed(n('caSpi')-n('eqSpi'))} · INT ${signed(n('caInt')-n('eqInt'))}</p>`;
    saveState();return;
  }
  const d={armor:n('caArmor')-n('eqArmor'),str:n('caStr')-n('eqStr'),agi:n('caAgi')-n('eqAgi'),sta:n('caSta')-n('eqSta'),spi:n('caSpi')-n('eqSpi'),int:n('caInt')-n('eqInt')};
  const key=[d.armor,d.str,d.agi,d.sta]; const better=key.every(x=>x>=0)&&key.some(x=>x>0), worse=key.every(x=>x<=0)&&key.some(x=>x<0);
  let title='Trade-off: revisa qué stat prefieres',cl='flat';if(better){title='Upgrade claro en los stats principales';cl='up'}else if(worse){title='Downgrade en los stats principales';cl='down'}
  const ap=d.str*2;
  $('result').innerHTML=`<div class="k">Resultado · Gear</div><h2 class="${cl}">${title}</h2><div class="metrics"><div class="metric"><span>Armor</span><strong>${signed(d.armor)}</strong></div><div class="metric"><span>Strength</span><strong>${signed(d.str)}</strong></div><div class="metric"><span>Agility</span><strong>${signed(d.agi)}</strong></div><div class="metric"><span>Stamina</span><strong>${signed(d.sta)}</strong></div></div><p><strong>${$('caName').value}</strong> frente a <strong>${$('eqName').value}</strong>: ${signed(ap)} AP por Strength · Spirit ${signed(d.spi)} · Intellect ${signed(d.int)}. Para Warrior leveling, STR aporta daño directo; STA supervivencia; AGI aporta crit/armor. No convierto esos trade-offs a un score falso.</p>`;
  saveState();
}'''
h = h[:start] + new_compare + h[end:]

# Extend reset object with generic fields.
h = h.replace("eqType:'sword',eqMin:20", "eqType:'sword',eqSlot:'Two-Hand',eqArmor:0,eqMin:20")
h = h.replace("eqSta:2,eqPrice:0", "eqSta:2,eqSpi:0,eqInt:0,eqPrice:0")
h = h.replace("caType:'mace',caMin:26", "caType:'mace',caSlot:'Two-Hand',caArmor:0,caMin:26")
h = h.replace("caSta:0,caPrice:0", "caSta:0,caSpi:0,caInt:0,caPrice:0")

# Replace the lookup item-filling core.
old_lookup = "const item=data.item;setVal(`${prefix}Id`,item.id);setVal(`${prefix}Min`,item.minDamage);setVal(`${prefix}Max`,item.maxDamage);setVal(`${prefix}Dps`,item.dps);setVal(`${prefix}Speed`,item.speed);setVal(`${prefix}Str`,item.strength||0);setVal(`${prefix}Agi`,item.agility||0);setVal(`${prefix}Sta`,item.stamina||0);if(item.weaponFamily&&['sword','mace','axe'].includes(item.weaponFamily))$(`${prefix}Type`).value=item.weaponFamily;"
new_lookup = "const item=data.item;setVal(`${prefix}Id`,item.id);setVal(`${prefix}Slot`,item.inventorySlot||'');setVal(`${prefix}Armor`,item.armor||0);setVal(`${prefix}Str`,item.strength||0);setVal(`${prefix}Agi`,item.agility||0);setVal(`${prefix}Sta`,item.stamina||0);setVal(`${prefix}Spi`,item.spirit||0);setVal(`${prefix}Int`,item.intellect||0);if(item.kind==='weapon'){setVal(`${prefix}Min`,item.minDamage||0);setVal(`${prefix}Max`,item.maxDamage||0);setVal(`${prefix}Dps`,item.dps||0);setVal(`${prefix}Speed`,item.speed||0);if(item.weaponFamily&&['sword','mace','axe'].includes(item.weaponFamily))$(`${prefix}Type`).value=item.weaponFamily}else{setVal(`${prefix}Min`,0);setVal(`${prefix}Max`,0);setVal(`${prefix}Dps`,0);setVal(`${prefix}Speed`,0);$(`${prefix}Type`).value='other';}"
h = h.replace(old_lookup, new_lookup)

# Better status wording.
h = h.replace("datos completados.", "datos de item completados.")

p.write_text(h, encoding='utf-8')
print('Applied V3.3 generic item search/comparison')
