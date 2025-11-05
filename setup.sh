#!/bin/bash

# Setup script para Memorial Maker

set -e

echo "🚀 Configurando Memorial Maker..."
echo ""

# Verifica Python
echo "📌 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION encontrado"

# Verifica Tesseract
echo ""
echo "📌 Verificando Tesseract..."
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract não encontrado"
    echo "   Instale com: sudo apt install tesseract-ocr tesseract-ocr-por"
    read -p "Continuar mesmo assim? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    TESSERACT_VERSION=$(tesseract --version | head -n1)
    echo "✅ $TESSERACT_VERSION"
fi

# Cria ambiente virtual
echo ""
echo "📦 Criando ambiente virtual..."
if [ -d "venv" ]; then
    echo "⚠️  venv já existe, pulando..."
else
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
fi

# Ativa ambiente
echo ""
echo "📥 Ativando ambiente virtual..."
source venv/bin/activate

# Atualiza pip
echo ""
echo "⬆️  Atualizando pip..."
pip install --upgrade pip -q

# Instala dependências
echo ""
echo "📚 Instalando dependências..."
pip install -e . -q

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "📝 Próximos passos:"
echo ""
echo "1. Configure suas credenciais:"
echo "   cp env.example .env"
echo "   nano .env  # Adicione sua OPENAI_API_KEY"
echo ""
echo "2. Teste a instalação:"
echo "   source venv/bin/activate"
echo "   memorial-make --help"
echo ""
echo "3. Execute a UI:"
echo "   streamlit run ui/app.py"
echo ""
echo "🎉 Pronto para usar!"






