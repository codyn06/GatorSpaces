const express = require('express');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;

app.use(express.static(path.join(__dirname)));

app.post('/api/trigger-scrape', (req, res) => {
  const scraper = path.join(__dirname, 'scraper.js');
  const child = spawn(process.execPath, [scraper], { stdio: 'inherit' });
  child.on('exit', (code) => {
    if (code === 0) res.json({ ok: true });
    else res.status(500).json({ ok: false, code });
  });
});

app.listen(PORT, () => console.log(`Static server + API listening on http://localhost:${PORT}`));
