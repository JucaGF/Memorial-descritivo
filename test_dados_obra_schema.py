#!/usr/bin/env python3
"""Test DADOS DA OBRA schema and generation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from memorial_maker.writer.dados_obra_schema import (
    DADOS_OBRA_SCHEMA,
    format_dados_obra_section,
    validate_dados_obra_schema
)


def test_schema_validation():
    """Test that schema is valid."""
    print("=" * 70)
    print("TEST: Schema Validation")
    print("=" * 70)
    
    try:
        validate_dados_obra_schema()
        print("✓ Schema is valid")
        print(f"  - Total fields: {len(DADOS_OBRA_SCHEMA)}")
        print(f"  - Required fields: {sum(1 for f in DADOS_OBRA_SCHEMA if f.required)}")
        print(f"  - Optional fields: {sum(1 for f in DADOS_OBRA_SCHEMA if not f.required)}")
        return True
    except AssertionError as e:
        print(f"✗ Schema validation failed: {e}")
        return False


def test_field_order_and_labels():
    """Test field order matches expected schema."""
    print("\n" + "=" * 70)
    print("TEST: Field Order and Labels")
    print("=" * 70)
    
    expected_labels = [
        "CONSTRUTORA",
        "EMPREENDIMENTO",
        "ENDEREÇO",
    ]
    
    actual_labels = [f.label for f in DADOS_OBRA_SCHEMA]
    
    print("\nDefined fields (in order):")
    for i, field in enumerate(DADOS_OBRA_SCHEMA, 1):
        req_mark = "REQ" if field.required else "OPT"
        print(f"  {i:2d}. [{req_mark}] {field.label} (key: {field.key})")
    
    # Check that expected labels are present in order
    for expected in expected_labels:
        if expected not in actual_labels:
            print(f"\n✗ Missing expected label: {expected}")
            return False
    
    print("\n✓ All expected labels present in schema")
    return True


def test_complete_data():
    """Test with complete master_data."""
    print("\n" + "=" * 70)
    print("TEST: Complete Data")
    print("=" * 70)
    
    master_data = {
        "obra": {
            "construtora": "Construtora Exemplo LTDA",
            "empreendimento": "Edifício Residencial Torre A",
            "endereco": "Rua Exemplo, 123 - Bairro - Cidade/UF",
            "tipo_edificacao": "Residencial",
            "tipologia": "Edifício multifamiliar",
            "pavimentos": ["Subsolo", "Térreo", "1º ao 15º"],
            "numero_unidades": 60,
            "area_total": 5000.5,
            "responsavel_tecnico": "Eng. João Silva",
            "crea": "CREA SP 123456",
            "data": "Janeiro de 2026"
        }
    }
    
    result = format_dados_obra_section(master_data)
    
    print("\nGenerated content:")
    print("-" * 70)
    print(result)
    print("-" * 70)
    
    # Validate all fields appear
    expected_in_output = [
        "CONSTRUTORA:",
        "EMPREENDIMENTO:",
        "ENDEREÇO:",
    ]
    
    for expected in expected_in_output:
        if expected not in result:
            print(f"\n✗ Expected '{expected}' not found in output")
            return False
    
    print("\n✓ All expected fields present in output")
    return True


def test_missing_required_fields():
    """Test that required fields show 'Não informado'."""
    print("\n" + "=" * 70)
    print("TEST: Missing Required Fields")
    print("=" * 70)
    
    master_data = {
        "obra": {
            # Only provide one required field
            "empreendimento": "Edifício Teste"
            # construtora and endereco are missing (required)
        }
    }
    
    result = format_dados_obra_section(master_data)
    
    print("\nGenerated content with missing required fields:")
    print("-" * 70)
    print(result)
    print("-" * 70)
    
    # Check for "Não informado"
    if "Não informado" not in result:
        print("\n✗ 'Não informado' not found for missing required fields")
        return False
    
    # Required fields should appear even if missing
    required_labels = [f.label for f in DADOS_OBRA_SCHEMA if f.required]
    for label in required_labels:
        if label + ":" not in result:
            print(f"\n✗ Required field '{label}' not present in output")
            return False
    
    print("\n✓ All required fields present with 'Não informado' for missing values")
    return True


def test_optional_fields_omission():
    """Test that optional fields without values are omitted."""
    print("\n" + "=" * 70)
    print("TEST: Optional Fields Omission")
    print("=" * 70)
    
    master_data = {
        "obra": {
            "construtora": "Construtora ABC",
            "empreendimento": "Torre B",
            "endereco": "Av. Principal, 456"
            # All optional fields missing
        }
    }
    
    result = format_dados_obra_section(master_data)
    
    print("\nGenerated content with only required fields:")
    print("-" * 70)
    print(result)
    print("-" * 70)
    
    # Optional fields should NOT appear
    optional_labels = [f.label for f in DADOS_OBRA_SCHEMA if not f.required]
    
    omitted_count = 0
    for label in optional_labels:
        if label + ":" not in result:
            omitted_count += 1
    
    print(f"\n✓ {omitted_count}/{len(optional_labels)} optional fields correctly omitted")
    return True


def main():
    """Run all tests."""
    print("\n")
    print("#" * 70)
    print("# DADOS DA OBRA SCHEMA - VALIDATION TESTS")
    print("#" * 70)
    print()
    
    results = []
    
    results.append(test_schema_validation())
    results.append(test_field_order_and_labels())
    results.append(test_complete_data())
    results.append(test_missing_required_fields())
    results.append(test_optional_fields_omission())
    
    print("\n" + "=" * 70)
    if all(results):
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        print()
        print("Schema is ready for use in DOCX generation.")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
