#!/bin/bash
# Script para expor o Roteador Trindade 2.5 via Ngrok
# Protocolo Sombra - Classificador Assíncrono com Failover

set -e

echo "=============================================="
echo "  ROTEADOR TRINDADE 2.5 - TÚNEL NGROK"
echo "=============================================="
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok não encontrado."
    echo "   Instale via: https://ngrok.com/download"
    echo "   Ou: brew install ngrok (macOS)"
    exit 1
fi

# Check if the server is running
if ! curl -s http://localhost:8000/health &> /dev/null; then
    echo "⚠️  Servidor não está rodando na porta 8000."
    echo "   Inicie com: python main.py"
    echo ""
    read -p "   Deseja iniciar o servidor em background? [Y/n] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo "📦 Iniciando servidor..."
        python main.py &
        sleep 3
    fi
fi

echo "🔗 Iniciando túnel Ngrok na porta 8000..."
echo ""

ngrok http 8000 --log-format json --log-level debug &

sleep 5

# Get ngrok API to show the public URL
NGROK_API="http://localhost:4040/api/tunnels"

echo ""
echo "📊 Endpoints disponíveis:"
echo "   Health: http://localhost:8000/health"
echo "   Ingress: http://localhost:8000/ingress"
echo "   Status: http://localhost:8000/status/{task_id}"
echo "   Classify: http://localhost:8000/classify"
echo "   Nodes: http://localhost:8000/nodes"
echo ""

# Try to get the public URL from ngrok API
if command -v jq &> /dev/null; then
    PUBLIC_URL=$(curl -s $NGROK_API 2>/dev/null | jq -r '.tunnels[0].public_url // empty')
    if [ -n "$PUBLIC_URL" ]; then
        echo "🌐 URL pública do túnel:"
        echo "   $PUBLIC_URL"
        echo ""
        echo "   API pública:"
        echo "   ${PUBLIC_URL}/ingress"
        echo "   ${PUBLIC_URL}/health"
    fi
else
    echo "💡 Para ver a URL pública, acesse: http://localhost:4040"
fi

echo ""
echo "✅ Túnel ativo! Pressione Ctrl+C para encerrar."
echo ""
