#!/usr/bin/env python3
"""
Script de verificação da instalação do Memorial Automator
"""

import sys

def check_imports():
    """Verifica se todas as dependências essenciais podem ser importadas"""
    
    print("🔍 Verificando instalação do Memorial Automator...\n")
    
    dependencies = {
        'fastapi': 'FastAPI (Framework Web)',
        'uvicorn': 'Uvicorn (Servidor ASGI)',
        'pydantic': 'Pydantic (Validação de dados)',
        'pydantic_settings': 'Pydantic Settings',
        'openai': 'OpenAI (Cliente API)',
        'fitz': 'PyMuPDF (Processamento de PDF)',
        'PIL': 'Pillow (Processamento de imagens)',
        'dotenv': 'Python-dotenv (Variáveis de ambiente)'
    }
    
    failed = []
    success = []
    
    for module, description in dependencies.items():
        try:
            __import__(module)
            success.append((module, description))
            print(f"✅ {description}")
        except ImportError as e:
            failed.append((module, description, str(e)))
            print(f"❌ {description} - ERRO: {e}")
    
    print(f"\n{'='*60}")
    print(f"Resultado: {len(success)}/{len(dependencies)} dependências instaladas")
    print(f"{'='*60}\n")
    
    if failed:
        print("❌ Dependências faltando:")
        for module, desc, error in failed:
            print(f"   - {desc} ({module})")
        print("\nPara instalar as dependências faltando:")
        print("   pip install -r requirements.txt")
        return False
    else:
        print("✅ Todas as dependências essenciais estão instaladas!")
        return True


def check_structure():
    """Verifica se a estrutura de diretórios está correta"""
    
    print("\n🔍 Verificando estrutura do projeto...\n")
    
    from pathlib import Path
    
    required_files = [
        'app/main.py',
        'app/core/config.py',
        'app/services/pdf_extractor.py',
        'app/services/document_parser.py',
        'app/services/agent_service.py',
        'app/models/schemas.py',
        'context_files/abnt_rules.txt',
        'context_files/client_template.txt',
        '.env',
        'requirements.txt'
    ]
    
    missing = []
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NÃO ENCONTRADO")
            missing.append(file_path)
    
    if missing:
        print(f"\n❌ Arquivos faltando: {len(missing)}")
        return False
    else:
        print("\n✅ Estrutura do projeto está completa!")
        return True


def check_config():
    """Verifica se o arquivo .env está configurado"""
    
    print("\n🔍 Verificando configuração...\n")
    
    from pathlib import Path
    
    env_file = Path('.env')
    
    if not env_file.exists():
        print("⚠️  Arquivo .env não encontrado!")
        print("   Crie o arquivo .env com sua chave OpenAI:")
        print("   echo 'OPENAI_API_KEY=sua_chave_aqui' > .env")
        return False
    
    # Ler .env e verificar OPENAI_API_KEY
    env_content = env_file.read_text()
    
    if 'OPENAI_API_KEY' not in env_content:
        print("⚠️  OPENAI_API_KEY não encontrada no .env")
        return False
    
    if 'your_openai_api_key_here' in env_content:
        print("⚠️  OPENAI_API_KEY ainda está com valor placeholder")
        print("   Edite o arquivo .env e adicione sua chave real da OpenAI")
        return False
    
    print("✅ Arquivo .env configurado")
    return True


def main():
    """Executa todas as verificações"""
    
    print("=" * 60)
    print("  Memorial Automator - Verificação de Instalação")
    print("=" * 60)
    
    checks = [
        check_imports(),
        check_structure(),
        check_config()
    ]
    
    print("\n" + "=" * 60)
    
    if all(checks):
        print("🎉 TUDO PRONTO! O sistema está configurado corretamente!")
        print("\nPróximos passos:")
        print("1. Edite os arquivos de contexto em context_files/")
        print("2. Inicie o servidor: ./start.sh")
        print("3. Acesse: http://localhost:8000/docs")
        print("=" * 60)
        return 0
    else:
        print("⚠️  Algumas verificações falharam.")
        print("Corrija os problemas acima antes de usar o sistema.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

