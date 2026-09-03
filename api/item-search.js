function cleanInput(value = '') {
  let s = String(value).trim();
  const idMatch = s.match(/\|Hitem:(\d+)/i) || s.match(/(?:item=|\/item\/)(\d+)/i);
  const linkName = s.match(/\|h\[([^\]]+)\]\|h/i);
  if (linkName) s = linkName[1];
  s = s.replace(/\|c[0-9a-f]{8}/ig, '').replace(/\|r/ig, '').replace(/^\[|\]$/g, '').trim();
  // WoW/chat/UI copies may wrap the item name in quotes. Strip only matching outer quotes.
  if ((s.startsWith('\"') && s.endsWith('\"')) || (s.startsWith('“') && s.endsWith('”')) || (s.startsWith("'") && s.endsWith("'"))) s = s.slice(1, -1).trim();
  return { text: s, itemId: idMatch ? Number(idMatch[1]) : null };
}

function decodeEntities(s = '') {
  return s
    .replace(/&nbsp;|&#160;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&quot;/gi, '"')
    .replace(/&#39;|&apos;/gi, "'")
    .replace(/&lt;/gi, '<')
    .replace(/&gt;/gi, '>');
}

function tagText(xml, tag) {
  const cdata = xml.match(new RegExp(`<${tag}[^>]*>\\s*<!\\[CDATA\\[([\\s\\S]*?)\\]\\]>\\s*</${tag}>`, 'i'));
  if (cdata) return cdata[1];
  const plain = xml.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)</${tag}>`, 'i'));
  return plain ? decodeEntities(plain[1].replace(/<[^>]+>/g, '')).trim() : '';
}

function attr(xml, tag, name) {
  const m = xml.match(new RegExp(`<${tag}[^>]*\\s${name}="([^"]+)"[^>]*>`, 'i'));
  return m ? m[1] : '';
}

function parseLooseObject(raw = '') {
  const out = {};
  const normalized = raw.trim();
  if (!normalized) return out;
  try {
    const parsed = JSON.parse(normalized);
    if (parsed && typeof parsed === 'object') return parsed;
  } catch (_) {}
  const re = /(?:^|,)([A-Za-z0-9_]+):(-?\d+(?:\.\d+)?)/g;
  let m;
  while ((m = re.exec(normalized))) out[m[1]] = Number(m[2]);
  return out;
}

function plainTooltip(html = '') {
  return decodeEntities(
    html
      .replace(/<!--([\s\S]*?)-->/g, ' ')
      .replace(/<br\s*\/?>/gi, '\n')
      .replace(/<[^>]+>/g, ' ')
      .replace(/\s+/g, ' ')
  ).trim();
}

function parseXml(xml) {
  const idMatch = xml.match(/<item\s+id="(\d+)"/i);
  if (!idMatch) return null;
  const name = tagText(xml, 'name');
  const subclass = tagText(xml, 'subclass');
  const inventorySlot = tagText(xml, 'inventorySlot');
  const tooltipHtml = tagText(xml, 'htmlTooltip');
  const tooltip = plainTooltip(tooltipHtml);
  const equip = parseLooseObject(tagText(xml, 'jsonEquip'));

  const dmg = tooltip.match(/(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s+Damage/i);
  const speed = tooltip.match(/Speed\s*([0-9.]+)/i);
  const dps = tooltip.match(/\(([0-9.]+)\s+damage per second\)/i);
  const armorMatch = tooltip.match(/(\d+(?:\.\d+)?)\s+Armor/i);
  const stat = label => {
    const m = tooltip.match(new RegExp(`\\+(\\d+)\\s+${label}`, 'i'));
    return m ? Number(m[1]) : 0;
  };
  const lower = `${subclass} ${inventorySlot}`.toLowerCase();
  let family = '';
  if (lower.includes('sword')) family = 'sword';
  else if (lower.includes('mace')) family = 'mace';
  else if (lower.includes('axe')) family = 'axe';

  return {
    id: Number(idMatch[1]),
    name,
    level: Number(tagText(xml, 'level')) || null,
    requiredLevel: Number(equip.reqlevel || 0) || null,
    subclass,
    inventorySlot,
    weaponFamily: family,
    minDamage: dmg ? Number(dmg[1]) : Number(equip.dmgmin1 ?? equip.dmgmin ?? 0) || null,
    maxDamage: dmg ? Number(dmg[2]) : Number(equip.dmgmax1 ?? equip.dmgmax ?? 0) || null,
    speed: speed ? Number(speed[1]) : Number(equip.speed ?? 0) || null,
    dps: dps ? Number(dps[1]) : null,
    strength: Number(equip.str ?? stat('Strength') ?? 0) || 0,
    agility: Number(equip.agi ?? stat('Agility') ?? 0) || 0,
    stamina: Number(equip.sta ?? stat('Stamina') ?? 0) || 0,
    intellect: Number(equip.int ?? stat('Intellect') ?? 0) || 0,
    spirit: Number(equip.spi ?? equip.spr ?? stat('Spirit') ?? 0) || 0,
    armor: Number(equip.armor ?? (armorMatch ? armorMatch[1] : 0) ?? 0) || 0,
    kind: (dmg || speed || dps || /hand|ranged|bow|gun|crossbow|thrown|wand/i.test(inventorySlot)) ? 'weapon' : (armorMatch || Number(equip.armor || 0) > 0 ? 'armor' : 'other'),
    wowheadUrl: `https://www.wowhead.com/tbc/item=${Number(idMatch[1])}`
  };
}

function norm(s = '') {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
}

function extractItemId(value = '') {
  const m = String(value).match(/(?:item=|\/item\/)(\d+)/i);
  return m ? Number(m[1]) : null;
}

async function fetchSuggestionId(term) {
  const q = String(term || '').trim();
  if (!q) return null;
  const headers = {
    'accept': 'application/json,text/plain;q=0.9,*/*;q=0.8',
    'user-agent': 'Mozilla/5.0 (compatible; XhenaWarriorCompanion/1.2)'
  };

  // Current Wowhead rich suggestions include typed results with numeric IDs.
  try {
    const response = await fetch(`https://www.wowhead.com/search/suggestions-template?q=${encodeURIComponent(q)}`, {
      headers, redirect: 'follow'
    });
    if (response.ok) {
      const data = await response.json();
      const results = Array.isArray(data?.results) ? data.results : [];
      const items = results.filter(x => x && (x.typeName === 'Item' || x.type === 3) && Number(x.id));
      let hit = items.find(x => norm(x.name) === norm(q));
      if (!hit) hit = items.find(x => norm(x.name).includes(norm(q)) || norm(q).includes(norm(x.name)));
      if (hit) return Number(hit.id);
    }
  } catch (_) {}

  // Legacy OpenSearch fallback. Some deployments only return names, so this is secondary.
  try {
    const response = await fetch(`https://www.wowhead.com/search/suggestions-open-search?q=${encodeURIComponent(q)}`, {
      headers, redirect: 'follow'
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

async function fetchWowhead(term, isId = false) {
  const key = isId ? String(term) : encodeURIComponent(term);
  const url = `https://www.wowhead.com/tbc/item=${key}&xml`;
  const response = await fetch(url, {
    headers: {
      'accept': 'application/xml,text/xml;q=0.9,*/*;q=0.8',
      'user-agent': 'Mozilla/5.0 (compatible; XhenaWarriorCompanion/1.0)'
    },
    redirect: 'follow'
  });
  if (!response.ok) throw new Error(`Wowhead HTTP ${response.status}`);
  const xml = await response.text();
  return parseXml(xml);
}

export default async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' });
  const raw = req.query?.q;
  if (!raw) return res.status(400).json({ error: 'Falta q' });

  const cleaned = cleanInput(raw);
  if (!cleaned.text && !cleaned.itemId) return res.status(400).json({ error: 'Nombre o link vacío' });

  try {
    let item = null;
    let resolvedFrom = 'name';
    let suffix = null;
    let baseName = cleaned.text;

    if (cleaned.itemId) {
      item = await fetchWowhead(cleaned.itemId, true);
      resolvedFrom = 'id';
    } else {
      const suffixMatch = cleaned.text.match(/^(.*?)(\s+of\s+(?:the\s+)?[^]+)$/i);
      if (suffixMatch) {
        baseName = suffixMatch[1].trim();
        suffix = suffixMatch[2].trim();
      }

      const exact = await fetchWowhead(cleaned.text, false);
      if (exact && (norm(exact.name) === norm(cleaned.text) || norm(cleaned.text).startsWith(norm(exact.name) + ' '))) {
        item = exact;
      }

      if (!item && baseName && norm(baseName) !== norm(cleaned.text)) {
        const base = await fetchWowhead(baseName, false);
        if (base && norm(base.name) === norm(baseName)) {
          item = base;
          resolvedFrom = 'base-name';
        }
      }

      if (!item) {
        const suggestionId = await fetchSuggestionId(baseName || cleaned.text);
        if (suggestionId) {
          item = await fetchWowhead(suggestionId, true);
          resolvedFrom = 'suggestion';
        }
      }

      if (!item && exact) {
        item = exact;
        resolvedFrom = 'fuzzy-name';
      }
    }

    if (!item) return res.status(404).json({ error: 'No se pudo resolver el ítem' });

    const likelyMismatch = cleaned.text &&
      norm(item.name) !== norm(cleaned.text) &&
      norm(cleaned.text).indexOf(norm(item.name)) !== 0 &&
      norm(baseName) !== norm(item.name);

    return res.status(200).json({
      ok: true,
      requestedName: cleaned.text,
      suffix,
      baseName,
      resolvedFrom,
      likelyMismatch,
      suffixNeedsConfirmation: Boolean(suffix && norm(item.name) === norm(baseName)),
      item
    });
  } catch (error) {
    return res.status(502).json({ error: 'No pude consultar Wowhead en este momento', detail: String(error?.message || error) });
  }
}
