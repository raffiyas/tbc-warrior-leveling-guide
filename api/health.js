export default function handler(req, res) {
  res.status(200).json({
    ok: true,
    app: 'tbc-warrior-leveling-guide',
    phase: 'v3.1',
    backend: 'vercel-function',
    next: 'blizzard-armory-integration'
  });
}
