from pathlib import Path
p=Path('api/item-search.js')
s=p.read_text(encoding='utf-8')
start=s.index('async function fetchSuggestionId(term) {')
end=s.index('\n\nasync function fetchWowhead(', start)
new=r'''async function fetchSuggestionId(term) {
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
}'''
s=s[:start]+new+s[end:]
p.write_text(s,encoding='utf-8')
print('Updated Wowhead suggestion resolver')
