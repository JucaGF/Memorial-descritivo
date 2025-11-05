#!/bin/bash
# Script para adicionar logo TecPred

echo "🏢 Adicionar Logo TecPred ao Memorial Maker"
echo "==========================================="
echo ""

# Diretório assets
ASSETS_DIR="$(cd "$(dirname "$0")" && pwd)/assets"
LOGO_PATH="$ASSETS_DIR/logo_tecpred.png"

# Verifica se já existe
if [ -f "$LOGO_PATH" ]; then
    echo "✅ Logo já existe em: $LOGO_PATH"
    ls -lh "$LOGO_PATH"
    
    read -p "Deseja substituir? (s/N): " resposta
    if [[ ! $resposta =~ ^[Ss]$ ]]; then
        echo "❌ Operação cancelada"
        exit 0
    fi
fi

echo ""
echo "Escolha uma opção:"
echo "1) Copiar de arquivo local"
echo "2) Download da internet"
echo "3) Cancelar"
echo ""
read -p "Opção (1-3): " opcao

case $opcao in
    1)
        read -p "Caminho do arquivo: " arquivo
        if [ -f "$arquivo" ]; then
            cp "$arquivo" "$LOGO_PATH"
            echo "✅ Logo copiada com sucesso!"
        else
            echo "❌ Arquivo não encontrado: $arquivo"
            exit 1
        fi
        ;;
    2)
        read -p "URL da logo: " url
        wget "$url" -O "$LOGO_PATH" || curl -o "$LOGO_PATH" "$url"
        if [ $? -eq 0 ]; then
            echo "✅ Logo baixada com sucesso!"
        else
            echo "❌ Erro ao baixar logo"
            exit 1
        fi
        ;;
    3)
        echo "❌ Operação cancelada"
        exit 0
        ;;
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

# Verifica se foi adicionada
if [ -f "$LOGO_PATH" ]; then
    echo ""
    echo "✅ Logo adicionada com sucesso!"
    echo "📍 Localização: $LOGO_PATH"
    echo "📏 Tamanho: $(du -h "$LOGO_PATH" | cut -f1)"
    echo "🔍 Tipo: $(file -b "$LOGO_PATH")"
    echo ""
    echo "🎉 A logo será incluída automaticamente em todos os memoriais!"
else
    echo "❌ Erro: Logo não foi adicionada"
    exit 1
fi

