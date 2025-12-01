"""Script para testar extração completa de um PDF."""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from memorial_maker.extract.unstructured_extract import extract_pdf_unstructured
from memorial_maker.normalize.consolidate import DataConsolidator
import json

# Testa com um PDF
pdf_path = Path("projetos_plantas/MGAMAK_TELECOM_01_SUBSOLO_28-04-2025.pdf")
output_dir = Path("test_output")
output_dir.mkdir(exist_ok=True)

print(f"Extraindo: {pdf_path.name}")
print("=" * 80)

# Extrai
result = extract_pdf_unstructured(pdf_path, output_dir)

print(f"\nTotal de elementos: {result['total_elements']}")
print(f"Textos: {len(result['text'])}")
print(f"Tabelas: {len(result['tables'])}")

print("\n" + "=" * 80)
print("=== DADOS DO CARIMBO EXTRAÍDO ===")
print("=" * 80)

carimbo = result.get("carimbo", {})
for key, value in carimbo.items():
    print(f"{key}: {value}")

print("\n" + "=" * 80)
print("=== CONSOLIDANDO DADOS ===")
print("=" * 80)

# Consolida
consolidator = DataConsolidator()
master = consolidator.consolidate(
    extractions=[result],
    normalized_items=[]
)

print("\nDados da obra consolidados:")
obra = master.get("obra", {})
print(json.dumps(obra, ensure_ascii=False, indent=2))

# Salva
master_path = output_dir / "mestre_test.json"
with open(master_path, "w", encoding="utf-8") as f:
    json.dump(master, f, ensure_ascii=False, indent=2)

print(f"\nSalvo em: {master_path}")
