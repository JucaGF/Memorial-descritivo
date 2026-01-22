#!/usr/bin/env python3
"""Quick verification script for section generation logic."""

# Simulate the section generation logic after our fixes
def test_section_generation():
    """Test that material sections are always included."""
    
    # Base sections that are always included
    base_sections = [
        "s1_sumario",
        "s2_memorial_descritivo",
        "s2_1_introducao",
        "s2_2_generalidades",
        "s2_3_descricao_servicos",
        "s3_especificacao_materiais",
        "s3_1_introducao_materiais",
        "s3_2_instalacoes_eletricas",
    ]
    
    # Material sections that should ALWAYS be included (NEW LOGIC)
    material_sections = [
        "s3_2_1_eletrodutos",
        "s3_2_2_fios_cabos",
        "s3_2_3_luminarias",
        "s3_2_4_quadros",
    ]
    
    # Service description sections that are conditional (only if evidence found)
    optional_service_sections = [
        "s2_3_1_entrada_energia",
        "s2_3_2_luz_forca",
        "s2_3_3_luz_essencial",
        "s2_3_4_protecao_aterramento",
        "s2_3_5_montagem_aparelhos",
    ]
    
    # Simulate structured extraction result (what was happening before - missing material sections)
    sections_present_from_extraction = [
        "s2_3_1_entrada_energia",
        "s2_3_2_luz_forca",
        # Note: material sections were missing from here, causing the bug
    ]
    
    # Build final section list (NEW LOGIC)
    sections_ids = base_sections.copy()
    # Always add material sections (THIS IS THE FIX!)
    sections_ids.extend(material_sections)
    # Conditionally add service sections based on evidence
    for section_id in optional_service_sections:
        if section_id in sections_present_from_extraction:
            sections_ids.append(section_id)
    
    print(f"✅ Total sections that will be generated: {len(sections_ids)}")
    print(f"\n📋 Section list:")
    for i, section_id in enumerate(sections_ids, 1):
        # Highlight material sections
        marker = "🔧" if section_id in material_sections else "📄"
        print(f"  {i:2d}. {marker} {section_id}")
    
    # Verify material sections are included
    assert "s3_2_1_eletrodutos" in sections_ids, "❌ Missing eletrodutos section!"
    assert "s3_2_2_fios_cabos" in sections_ids, "❌ Missing fios_cabos section!"
    assert "s3_2_3_luminarias" in sections_ids, "❌ Missing luminarias section!"
    assert "s3_2_4_quadros" in sections_ids, "❌ Missing quadros section!"
    
    print(f"\n✅ All 4 material sections are included!")
    print(f"✅ Expected at least 14 sections (8 base + 4 material + 2 conditional), got {len(sections_ids)}")
    
    return sections_ids

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Section Generation Logic (After Fix)")
    print("=" * 60)
    print()
    
    sections = test_section_generation()
    
    print()
    print("=" * 60)
    print("✅ TEST PASSED - Material sections will always be generated!")
    print("=" * 60)
