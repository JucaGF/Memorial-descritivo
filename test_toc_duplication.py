#!/usr/bin/env python3
"""Test to verify TOC field implementation and ensure no duplication."""

import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

def test_toc_field_presence(docx_path):
    """Verify that exactly ONE TOC field exists in the document."""
    print(f"Testing TOC field in: {docx_path}")
    
    with zipfile.ZipFile(docx_path, 'r') as zf:
        xml_content = zf.read('word/document.xml')
        root = ET.fromstring(xml_content)
        
        # Search for TOC instruction text
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        # Find all instrText elements
        instr_texts = root.findall('.//w:instrText', ns)
        toc_count = 0
        
        for instr in instr_texts:
            if instr.text and 'TOC' in instr.text:
                toc_count += 1
                print(f"  Found TOC instruction: {instr.text}")
        
        print(f"  Total TOC fields found: {toc_count}")
        
        if toc_count == 0:
            print("  ✗ ERROR: No TOC field found!")
            return False
        elif toc_count == 1:
            print("  ✓ PASS: Exactly ONE TOC field found")
            return True
        else:
            print(f"  ✗ ERROR: Multiple TOC fields found ({toc_count})!")
            return False


def test_no_sumario_duplication(docx_path):
    """Verify that SUMÁRIO heading and items don't appear duplicated."""
    print(f"\nTesting for duplications in: {docx_path}")
    
    with zipfile.ZipFile(docx_path, 'r') as zf:
        xml_content = zf.read('word/document.xml')
        root = ET.fromstring(xml_content)
        
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        # Extract all text nodes in order
        all_texts = []
        for text in root.findall('.//w:t', ns):
            if text.text and text.text.strip():
                all_texts.append(text.text.strip())
        
        # Check for consecutive duplicates
        duplicates = []
        for i in range(len(all_texts) - 1):
            if all_texts[i] == all_texts[i+1] and len(all_texts[i]) > 10:
                duplicates.append(all_texts[i])
        
        if duplicates:
            print(f"  ✗ ERROR: Found {len(duplicates)} consecutive duplicate texts:")
            for dup in duplicates[:5]:  # Show first 5
                print(f"    - {dup[:50]}...")
            return False
        else:
            print("  ✓ PASS: No consecutive duplicate texts found")
            return True


def test_sumario_heading_style(docx_path):
    """Verify that SUMÁRIO title is NOT using Heading style (to avoid appearing in TOC)."""
    print(f"\nTesting SUMÁRIO heading style in: {docx_path}")
    
    with zipfile.ZipFile(docx_path, 'r') as zf:
        xml_content = zf.read('word/document.xml')
        root = ET.fromstring(xml_content)
        
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        # Find paragraphs containing "SUMÁRIO"
        for para in root.findall('.//w:p', ns):
            texts = [t.text for t in para.findall('.//w:t', ns) if t.text]
            if any('SUMÁRIO' in t for t in texts):
                # Check paragraph style
                pStyle = para.find('.//w:pStyle', ns)
                if pStyle is not None:
                    style_val = pStyle.get('{' + ns['w'] + '}val')
                    if 'Heading' in str(style_val):
                        print(f"  ✗ ERROR: SUMÁRIO is using Heading style ({style_val})")
                        print("    This will cause it to appear in its own TOC!")
                        return False
                
                print("  ✓ PASS: SUMÁRIO is not using Heading style")
                return True
        
        print("  ⚠ WARNING: SUMÁRIO heading not found in document")
        return True


def main():
    """Run all TOC tests."""
    docx_path = Path("/home/joaquim/Projects/Memorial-descritivo/memorial/MEMORIAL_TELECOM_MGAMAK_2026-01-22.docx")
    
    if not docx_path.exists():
        print(f"Document not found: {docx_path}")
        print("Please generate a memorial first.")
        return
    
    print("=" * 70)
    print("TOC DUPLICATION AND FIELD VALIDATION TESTS")
    print("=" * 70)
    print()
    
    results = []
    
    # Test 1: TOC field presence
    results.append(test_toc_field_presence(docx_path))
    
    # Test 2: No duplication
    results.append(test_no_sumario_duplication(docx_path))
    
    # Test 3: SUMÁRIO heading style
    results.append(test_sumario_heading_style(docx_path))
    
    print()
    print("=" * 70)
    if all(results):
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
        sys.exit(1)
    print("=" * 70)


if __name__ == "__main__":
    main()
