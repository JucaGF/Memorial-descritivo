"""Post-processing utilities for DOCX documents."""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional


def clean_toc_field_result(docx_path: Path) -> bool:
    """Clean pre-populated result from TOC field to prevent duplication.
    
    The TOC field has this structure:
    - w:fldChar type="begin"
    - w:instrText with "TOC ..."
    - w:fldChar type="separate"
    - [RESULT: TOC1/TOC2 paragraphs - WE REMOVE THIS]
    - w:fldChar type="end"
    
    Args:
        docx_path: Path to DOCX file
        
    Returns:
        True if cleaned successfully, False otherwise
    """
    if not docx_path.exists():
        return False
    
    try:
        # Read DOCX as zip
        with zipfile.ZipFile(docx_path, 'r') as zf:
            xml_content = zf.read('word/document.xml')
        
        root = ET.fromstring(xml_content)
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        # Find TOC field
        toc_begin = None
        toc_separate = None
        toc_end = None
        
        # Locate the TOC field markers
        for para in root.findall('.//w:p', ns):
            for run in para.findall('.//w:r', ns):
                for fldChar in run.findall('.//w:fldChar', ns):
                    fld_type = fldChar.get('{' + ns['w'] + '}fldCharType')
                    
                    if fld_type == 'begin':
                        # Check if this is a TOC field (next instrText should contain TOC)
                        next_para = para
                        found_toc = False
                        for check_para in root.findall('.//w:p', ns):
                            if check_para == para or found_toc:
                                for instr in check_para.findall('.//w:instrText', ns):
                                    if instr.text and 'TOC' in instr.text:
                                        toc_begin = para
                                        found_toc = True
                                        break
                                if found_toc:
                                    break
                            if found_toc:
                                break
                    
                    elif fld_type == 'separate' and toc_begin is not None and toc_separate is None:
                        toc_separate = para
                    
                    elif fld_type == 'end' and toc_separate is not None and toc_end is None:
                        toc_end = para
                        break
        
        if not (toc_begin and toc_separate and toc_end):
            print("TOC field markers not found completely")
            return False
        
        # Find all paragraphs between separate and end
        paras_to_remove = []
        in_result_section = False
        
        for para in root.findall('.//w:p', ns):
            if para == toc_separate:
                in_result_section = True
                # Clean content after separate in the same paragraph
                for elem in list(para):
                    # Keep only runs that contain w:fldChar with separate
                    has_separate = False
                    for run in para.findall('.//w:r', ns):
                        for fldChar in run.findall('.//w:fldChar', ns):
                            if fldChar.get('{' + ns['w'] + '}fldCharType') == 'separate':
                                has_separate = True
                                break
                    if not has_separate and elem.tag == '{' + ns['w'] + '}r':
                        para.remove(elem)
                continue
            
            if para == toc_end:
                in_result_section = False
                # Clean content before end in the same paragraph
                for elem in list(para):
                    # Keep only runs that contain w:fldChar with end
                    has_end = False
                    if elem.tag == '{' + ns['w'] + '}r':
                        for fldChar in elem.findall('.//w:fldChar', ns):
                            if fldChar.get('{' + ns['w'] + '}fldCharType') == 'end':
                                has_end = True
                                break
                        if not has_end:
                            para.remove(elem)
                break
            
            if in_result_section:
                paras_to_remove.append(para)
        
        # Remove the paragraphs
        for para in paras_to_remove:
            parent = para.getparent()
            if parent is not None:
                parent.remove(para)
        
        # Write back
        new_xml = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        
        # Update the DOCX
        with zipfile.ZipFile(docx_path, 'r') as zf_read:
            with zipfile.ZipFile(str(docx_path) + '.tmp', 'w', zipfile.ZIP_DEFLATED) as zf_write:
                for item in zf_read.infolist():
                    if item.filename == 'word/document.xml':
                        zf_write.writestr(item, new_xml)
                    else:
                        zf_write.writestr(item, zf_read.read(item.filename))
        
        # Replace original
        import os
        os.replace(str(docx_path) + '.tmp', str(docx_path))
        
        print(f"✓ Cleaned TOC field result from {docx_path.name}")
        return True
        
    except Exception as e:
        print(f"✗ Error cleaning TOC: {e}")
        import traceback
        traceback.print_exc()
        return False
