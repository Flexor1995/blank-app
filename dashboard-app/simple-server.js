const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;

const server = http.createServer((req, res) => {
  console.log(`📥 Requisição: ${req.method} ${req.url}`);
  
  let filePath = '';
  
  if (req.url === '/' || req.url === '/dashboard') {
    filePath = path.join(__dirname, '.next/server/app/dashboard/page.html');
  } else if (req.url.startsWith('/_next/')) {
    filePath = path.join(__dirname, '.next', req.url);
  } else {
    filePath = path.join(__dirname, '.next/server/app/dashboard/page.html');
  }
  
  fs.readFile(filePath, (err, data) => {
    if (err) {
      console.error(`❌ Erro ao ler arquivo: ${err.message}`);
      res.writeHead(404, { 'Content-Type': 'text/html' });
      res.end('<h1>404 - Página não encontrada</h1>');
      return;
    }
    
    const ext = path.extname(filePath);
    let contentType = 'text/html';
    
    if (ext === '.js') contentType = 'text/javascript';
    else if (ext === '.css') contentType = 'text/css';
    else if (ext === '.json') contentType = 'application/json';
    else if (ext === '.png') contentType = 'image/png';
    else if (ext === '.jpg') contentType = 'image/jpg';
    
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log('🚀 Servidor rodando!');
  console.log(`📍 Acesse: http://localhost:${PORT}/dashboard`);
  console.log(`🌐 Ou: http://127.0.0.1:${PORT}/dashboard`);
  console.log('⏹️  Para parar: Ctrl+C');
});