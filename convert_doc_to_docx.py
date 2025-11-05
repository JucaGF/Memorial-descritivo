#!/usr/bin/env python3
"""Script para converter arquivos .doc (Word 97-2003) para .docx"""

import subprocess
from pathlib import Path
import sys

def convert_doc_to_docx(doc_path: Path) -> bool:
    """Converte .doc para .docx usando LibreOffice."""
    docx_path = doc_path.parent / f"{doc_path.stem}.docx"
    
    if docx_path.exists():
        print(f"⚠️  {docx_path.name} já existe, pulando...")
        return True
    
    print(f"🔄 Convertendo {doc_path.name}...")
    
    try:
        # Usa LibreOffice para converter
        cmd = [
            "libreoffice",
            "--headless",
            "--convert-to", "docx",
            "--outdir", str(doc_path.parent),
            str(doc_path)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and docx_path.exists():
            print(f"✅ Convertido: {docx_path.name}")
            return True
        else:
            print(f"❌ Erro ao converter {doc_path.name}")
            print(f"   Saída: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ LibreOffice não encontrado. Instale com:")
        print("   sudo dnf install libreoffice-core")
        return False
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout ao converter {doc_path.name}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


def main():
    """Converte todos os .doc no diretório memorial/"""
    memorial_dir = Path(__file__).parent / "memorial"
    
    if not memorial_dir.exists():
        print(f"❌ Diretório não encontrado: {memorial_dir}")
        sys.exit(1)
    
    doc_files = list(memorial_dir.glob("*.doc"))
    
    if not doc_files:
        print("✅ Nenhum arquivo .doc encontrado para converter")
        return
    
    print(f"📄 Encontrados {len(doc_files)} arquivo(s) .doc\n")
    
    success = 0
    failed = 0
    
    for doc_file in doc_files:
        if convert_doc_to_docx(doc_file):
            success += 1
        else:
            failed += 1
    
    print(f"\n📊 Resumo:")
    print(f"   ✅ Convertidos: {success}")
    print(f"   ❌ Falhas: {failed}")


if __name__ == "__main__":
    main()



