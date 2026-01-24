#!/usr/bin/env python3
"""Test section 4.1 conformance with reference memorial."""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


# Prohibited terms (if not in reference model)
PROHIBITED_TERMS = [
    'VLAN',
    'QoS',
    'SIP',
    'VoIP',  # Check if this is actually in reference
    'PABX IP',  # Check if this is actually in reference
]


def test_template_no_prohibited_terms():
    """Test that templates don't contain prohibited terms."""
    print("=" * 70)
    print("TEST: Prohibited Terms in Templates")
    print("=" * 70)
    
    templates_dir = Path(__file__).parent / "memorial_maker" / "rag" / "prompts" / "telecom" / "templates"
    
    templates = [
        "s4_1_voz_residencial.txt",
        "s4_1_voz_corporativo.txt"
    ]
    
    all_ok = True
    
    for template_name in templates:
        template_path = templates_dir / template_name
        
        if not template_path.exists():
            print(f"\n⚠ Template not found: {template_name}")
            continue
        
        with open(template_path, 'r') as f:
            content = f.read()
        
        print(f"\n{template_name}:")
        found_terms = []
        
        for term in PROHIBITED_TERMS:
            if term in content:
                found_terms.append(term)
        
        if found_terms:
            print(f"  ✗ Found prohibited terms: {', '.join(found_terms)}")
            print(f"    → These terms should only appear if they're in the reference model")
            print(f"    → Please verify against reference document")
            all_ok = False
        else:
            print(f"  ✓ No prohibited terms found")
    
    return all_ok


def test_template_structure():
    """Test that templates have proper structure."""
    print("\n" + "=" * 70)
    print("TEST: Template Structure")
    print("=" * 70)
    
    templates_dir = Path(__file__).parent / "memorial_maker" / "rag" / "prompts" / "telecom" / "templates"
    
    templates = {
        "s4_1_voz_residencial.txt": ["CCI-2", "DG", "telefone"],
        "s4_1_voz_corporativo.txt": ["CAT-6", "voice panel", "corporati"]
    }
    
    all_ok = True
    
    for template_name, expected_terms in templates.items():
        template_path = templates_dir / template_name
        
        if not template_path.exists():
            print(f"\n⚠ Template not found: {template_name}")
            continue
        
        with open(template_path, 'r') as f:
            content = f.read()
        
        print(f"\n{template_name}:")
        print(f"  Length: {len(content)} characters")
        
        # Check for expected terms
        missing = []
        for term in expected_terms:
            if term.lower() not in content.lower():
                missing.append(term)
        
        if missing:
            print(f"  ⚠ Missing expected terms: {', '.join(missing)}")
            all_ok = False
        else:
            print(f"  ✓ Contains expected terms: {', '.join(expected_terms)}")
    
    return all_ok


def test_template_used_correctly():
    """Verify that template loading logic exists."""
    print("\n" + "=" * 70)
    print("TEST: Template Loading Logic")
    print("=" * 70)
    
    # Check that generate_sections.py has the template loading logic
    gen_sections_file = Path(__file__).parent / "memorial_maker" / "rag" / "generate_sections.py"
    
    if not gen_sections_file.exists():
        print("✗ generate_sections.py not found")
        return False
    
    with open(gen_sections_file, 'r') as f:
        content = f.read()
    
    checks = [
        ("_get_building_type", "Building type detection method"),
        ("_load_static_template", "Static template loading method"),
        ("s4_1_voz", "Section 4.1 template loading"),
    ]
    
    all_ok = True
    for check_str, description in checks:
        if check_str in content:
            print(f"  ✓ {description} found")
        else:
            print(f"  ✗ {description} NOT found")
            all_ok = False
    
    return all_ok


def main():
    """Run all tests."""
    print("\n")
    print("#" * 70)
    print("# SECTION 4.1 - TEXT CONFORMANCE TESTS")
    print("#" * 70)
    print()
    
    results = []
    
    results.append(test_template_no_prohibited_terms())
    results.append(test_template_structure())
    results.append(test_template_used_correctly())
    
    print("\n" + "=" * 70)
    if all(results):
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        print()
        print("IMPORTANT: Verify that template texts match reference document EXACTLY.")
        print("Update template files with literal text from reference if needed.")
        return 0
    else:
        print("⚠ SOME TESTS FAILED OR NEED REVIEW")
        print("=" * 70)
        print()
        print("Action required:")
        print("1. Check if prohibited terms are actually in reference model")
        print("2. If NOT in reference, remove them from templates")
        print("3. Ensure templates use exact wording from reference")
        return 1


if __name__ == "__main__":
    sys.exit(main())
