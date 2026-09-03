export default async function handler(req, res) {
  const q = String(req.query?.q || 'Blackrock Boots');
  const headers = { 'user-agent': 'Mozilla/5.0 (compatible; XhenaWarriorCompanion/1.1)', 'accept': 'application/json,text/plain,*/*' };
  const urls = [
    `https://www.wowhead.com/search/suggestions-open-search?q=${encodeURIComponent(q)}`,
    `https://www.wowhead.com/search/suggestions-template?q=${encodeURIComponent(q)}`
  ];
  const out = [];
  for (const url of urls) {
    try {
      const r = await fetch(url, { headers, redirect: 'follow' });
      const text = await r.text();
      out.push({ url, status: r.status, contentType: r.headers.get('content-type'), text: text.slice(0, 12000) });
    } catch (e) {
      out.push({ url, error: String(e?.message || e) });
    }
  }
  res.status(200).json({ q, out });
}
