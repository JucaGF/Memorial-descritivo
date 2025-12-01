"""Teste simples da lógica de extração."""

text_after = """ Escala:
PROJETO DE INSTALAÇÕES DE TELECOMUNICAÇÃO
MGA CONSTRUÇÕES E INCORPORAÇÕES LTDA
MAKAI
AVENIDA MAX ZAGEL, S/N, LOTE 05-A QUADRA12, CABEDELO- PB
TecPred
INDICADAS"""

lines = [l.strip() for l in text_after.split('\n') if l.strip()]

print("Linhas originais:")
for i, line in enumerate(lines):
    print(f"  {i}: {line}")

print("\n" + "="*60)

# Lógica do código
if len(lines) >= 1:
    first_line = lines[0]
    print(f"Primeira linha: '{first_line}'")
    
    if 'Escala:' in first_line or 'ESCALA:' in first_line.upper():
        value_lines = lines[1:]
        print("Pulou 'Escala:' - value_lines começa do índice 1")
    else:
        value_lines = lines
        print("Não pulou nada - value_lines é igual a lines")
    
    print(f"\nvalue_lines tem {len(value_lines)} elementos:")
    for i, line in enumerate(value_lines):
        print(f"  value_lines[{i}]: {line}")
    
    print("\n" + "="*60)
    
    if len(value_lines) >= 4:
        print(f"\nvalue_lines[3] = '{value_lines[3]}'")
        
        endereco_candidate = value_lines[3]
        is_address = (
            ',' in endereco_candidate or
            any(word in endereco_candidate.upper() for word in ['AVENIDA', 'RUA', 'AV.', 'R.', 'LOTE', 'QUADRA']) or
            (len(endereco_candidate) > 20 and '-' in endereco_candidate)
        )
        
        print(f"É endereço? {is_address}")
        print(f"Tem vírgula? {',' in endereco_candidate}")
        print(f"Tem AVENIDA? {'AVENIDA' in endereco_candidate.upper()}")
        print(f"Tem LOTE? {'LOTE' in endereco_candidate.upper()}")
