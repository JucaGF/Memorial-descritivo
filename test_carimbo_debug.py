"""Script de debug para testar extração de carimbo."""

from pathlib import Path
from unstructured.partition.pdf import partition_pdf
import re

# PDF de teste
pdf_path = Path("projetos_plantas/MGAMAK_TELECOM_01_SUBSOLO_28-04-2025.pdf")

print(f"Extraindo: {pdf_path.name}")
print("=" * 80)

# Extrai elementos
elements = partition_pdf(
    filename=str(pdf_path),
    strategy="fast",  # Usa estratégia rápida para debug
    languages=["por"],
)

print(f"\nTotal de elementos: {len(elements)}")
print("=" * 80)

# Junta todo o texto
full_text = "\n".join([str(e) for e in elements])

print("\n=== TEXTO COMPLETO (últimos 2000 chars) ===")
print(full_text[-2000:])

print("\n" + "=" * 80)
print("=== PROCURANDO PADRÕES DE CARIMBO ===")
print("=" * 80)

# Procura por padrões específicos
patterns = {
    "PROJETO:": r"PROJETO\s*:.*",
    "CONSTRUTOR:": r"CONSTRUTOR\s*:.*",
    "EDIFÍCIO:": r"EDIF[ÍI]CIO\s*:.*",
    "LOCAL:": r"LOCAL\s*:.*",
    "DATA:": r"DATA\s*:.*",
    "Escala:": r"Escala\s*:.*",
    "Labels juntos": r"PROJETO:\s*CONSTRUTOR:\s*EDIF[ÍI]CIO:\s*LOCAL:",
}

for name, pattern in patterns.items():
    matches = re.findall(pattern, full_text, re.IGNORECASE)
    if matches:
        print(f"\n{name}:")
        for match in matches[:3]:  # Mostra primeiras 3 ocorrências
            print(f"  → {match}")

print("\n" + "=" * 80)
print("=== TEXTO AO REDOR DO PADRÃO DE LABELS JUNTOS ===")
print("=" * 80)

# Procura o padrão onde todos os labels estão juntos
pattern_labels = r'PROJETO:\s*CONSTRUTOR:\s*EDIF[ÍI]CIO:\s*LOCAL:'
match = re.search(pattern_labels, full_text, re.IGNORECASE)

if match:
    start_pos = match.start()
    end_pos = match.end()
    
    # Mostra 200 chars antes e 800 depois
    context_before = full_text[max(0, start_pos - 200):start_pos]
    context_after = full_text[end_pos:end_pos + 800]
    
    print("ANTES:")
    print(context_before)
    print("\nPADRÃO ENCONTRADO:")
    print(match.group())
    print("\nDEPOIS:")
    print(context_after)
    
    print("\n" + "=" * 80)
    print("=== LINHAS APÓS O PADRÃO ===")
    print("=" * 80)
    
    lines = [l.strip() for l in context_after.split('\n') if l.strip()]
    for i, line in enumerate(lines[:10]):
        print(f"{i}: {line}")
    
    print("\n" + "=" * 80)
    print("=== ANÁLISE DA LINHA 4 (ENDEREÇO) ===")
    print("=" * 80)
    if len(lines) > 3:
        endereco_line = lines[3]
        print(f"Linha 4: '{endereco_line}'")
        print(f"Tamanho: {len(endereco_line)}")
        print(f"Tem vírgula? {',' in endereco_line}")
        print(f"Tem hífen? {'-' in endereco_line}")
        print(f"Tem AVENIDA? {'AVENIDA' in endereco_line.upper()}")
        print(f"Tem LOTE? {'LOTE' in endereco_line.upper()}")
        print(f"Tem QUADRA? {'QUADRA' in endereco_line.upper()}")
else:
    print("Padrão de labels juntos NÃO ENCONTRADO")
    
    # Tenta procurar cada label individualmente
    print("\n" + "=" * 80)
    print("=== PROCURANDO LABELS INDIVIDUAIS ===")
    print("=" * 80)
    
    for label in ["PROJETO:", "CONSTRUTOR:", "EDIFÍCIO:", "LOCAL:"]:
        pos = full_text.find(label)
        if pos >= 0:
            context = full_text[pos:pos+200]
            print(f"\n{label} encontrado em posição {pos}:")
            print(context[:150])
