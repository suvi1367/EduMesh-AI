// mock-server.js — run with: node mock-server.js
const http = require('http');

http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', '*');
  res.setHeader('Access-Control-Allow-Methods', '*');
  if (req.method === 'OPTIONS') return res.end();

  let body = '';
  req.on('data', c => body += c);
  req.on('end', () => {
    res.setHeader('Content-Type', 'application/json');
    if (req.url === '/login') {
      res.end(JSON.stringify({ token: 'fake-token-123' }));
    } else {
      res.end(JSON.stringify({ ok: true }));
    }
  });
}).listen(8000, () => console.log('Mock Hub running on http://localhost:8000'));