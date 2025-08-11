#!/bin/bash

echo "🚀 Iniciando o Dashboard..."
echo "📁 Diretório atual: $(pwd)"
echo "📦 Instalando dependências..."

npm install

echo "🔧 Construindo o projeto..."
npm run build

echo "🌐 Iniciando servidor..."
echo "📍 Acesse: http://localhost:3000/dashboard"
echo "📍 Ou: http://127.0.0.1:3000/dashboard"
echo ""
echo "⏹️  Para parar o servidor, pressione Ctrl+C"
echo ""

npm run dev