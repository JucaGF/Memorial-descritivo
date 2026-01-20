#!/usr/bin/env python3
"""Teste rápido para validar que spawn context funciona sem deadlock."""

import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import time
from pathlib import Path

def mock_extract(file_id: int) -> dict:
    """Simula extração de PDF."""
    print(f"  Worker processando arquivo {file_id}")
    time.sleep(1)  # Simula processamento
    return {"id": file_id, "status": "success"}

def test_spawn_context():
    """Testa ProcessPoolExecutor com spawn context."""
    print("🧪 Testando ProcessPoolExecutor com spawn context...")
    
    # Criar contexto spawn
    mp_context = multiprocessing.get_context('spawn')
    
    files = list(range(4))  # 4 arquivos mock
    results = []
    
    start = time.time()
    
    try:
        with ProcessPoolExecutor(max_workers=2, mp_context=mp_context) as executor:
            # Submit tasks
            futures = {executor.submit(mock_extract, fid): fid for fid in files}
            
            # Collect results
            from concurrent.futures import as_completed
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                print(f"✅ Arquivo {result['id']} completado")
        
        elapsed = time.time() - start
        
        print(f"\n✅ Teste bem-sucedido!")
        print(f"   • {len(results)} tarefas completadas")
        print(f"   • Tempo: {elapsed:.2f}s")
        print(f"   • Paralelismo funcionando: {'Sim' if elapsed < 2.5 else 'Não'}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Teste falhou: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_spawn_context()
    exit(0 if success else 1)
