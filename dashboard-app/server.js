const express = require('express');
const path = require('path');
const app = express();
const PORT = 3000;

// Servir arquivos estáticos
app.use(express.static(path.join(__dirname, '.next')));

// Rota principal
app.get('/', (req, res) => {
  res.redirect('/dashboard');
});

// Rota do dashboard
app.get('/dashboard', (req, res) => {
  res.sendFile(path.join(__dirname, '.next/server/app/dashboard/page.html'));
});

// Rota para assets
app.get('/_next/*', (req, res) => {
  res.sendFile(path.join(__dirname, '.next', req.params[0]));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Dashboard rodando em: http://localhost:${PORT}/dashboard`);
  console.log(`🌐 Ou acesse: http://127.0.0.1:${PORT}/dashboard`);
});