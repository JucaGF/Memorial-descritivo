#!/usr/bin/env python3
"""Script de teste para diagnóstico de extração"""

from pathlib import Path
import sys

# Adiciona o diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from memorial_maker.extract.unstructured_extract import extract_pdf_unstructured, extract_text_from_elements
from memorial_maker.normalize.canonical_map import ItemExtractor


def test_extraction():
    """Testa extração e normalização"""
    
    print("🧪 TESTE DE EXTRAÇÃO - Memorial Maker\n")
    print("="*60)
    
    # 1. Verifica PDF
    pdf_dir = Path("projetos_plantas")
    pdfs = list(pdf_dir.glob("*.pdf"))
    
    if not pdfs:
        print("❌ Nenhum PDF encontrado em projetos_plantas/")
        return
    
    pdf = pdfs[0]
    print(f"\n📄 Testando PDF: {pdf.name}")
    print(f"📏 Tamanho: {pdf.stat().st_size / 1024:.1f} KB")
    
    # 2. Extrai com Unstructured
    print("\n🔄 Extraindo com Unstructured...")
    out_dir = Path("out/teste_diagnostico")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    result = extract_pdf_unstructured(pdf, out_dir)
    
    print(f"✅ Total elementos: {result['total_elements']}")
    print(f"📝 Textos: {len(result['text'])}")
    print(f"📊 Tabelas: {len(result['tables'])}")
    
    # 3. Extrai texto completo
    full_text = extract_text_from_elements(result)
    print(f"\n📄 Texto extraído: {len(full_text)} caracteres")
    
    # 4. Mostra amostra
    print(f"\n📋 Primeiros 500 caracteres:")
    print("-" * 60)
    print(full_text[:500])
    print("-" * 60)
    
    # 5. Busca palavras-chave
    keywords = ["RJ", "CAT", "PONTO", "CABO", "UTP", "ITEM", "DESCRIÇÃO", "QUANT"]
    print(f"\n🔍 Palavras-chave encontradas:")
    for kw in keywords:
        count = full_text.count(kw)
        status = "✅" if count > 0 else "❌"
        print(f"   {status} {kw}: {count}x")
    
    # 6. Testa normalização
    print(f"\n🔧 Testando normalização...")
    extractor = ItemExtractor()
    items = extractor.extract_from_text(full_text, {"filename": pdf.name})
    
    print(f"✅ Itens extraídos: {len(items)}")
    
    if items:
        print(f"\n📦 Primeiros 5 itens:")
        for i, item in enumerate(items[:5], 1):
            print(f"   {i}. {item.get('item_type', 'N/A')}: {item.get('quantity', '?')} {item.get('unit', '')}")
    else:
        print("⚠️  NENHUM ITEM EXTRAÍDO!")
        print("\n💡 Sugestões:")
        print("   1. Use estratégia 'hi_res' para melhor detecção de tabelas")
        print("   2. Verifique se o PDF tem tabelas de quantitativos")
        print("   3. Considere adicionar parser customizado para seus PDFs")
    
    # 7. Verifica se há tabelas estruturadas
    if result['tables']:
        print(f"\n📊 Primeira tabela:")
        print("-" * 60)
        print(result['tables'][0]['text'][:300])
        print("-" * 60)
    
    print(f"\n{'='*60}")
    print("🎯 RESUMO:")
    print(f"   Extração: {'✅ OK' if result['total_elements'] > 0 else '❌ FALHOU'}")
    print(f"   Texto: {'✅ OK' if len(full_text) > 100 else '❌ VAZIO'}")
    print(f"   Tabelas: {'✅ Detectadas' if result['tables'] else '⚠️  Não detectadas'}")
    print(f"   Normalização: {'✅ OK' if items else '❌ Nenhum item extraído'}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    try:
        test_extraction()
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

