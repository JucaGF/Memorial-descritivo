"""Quick test of static template system for electrical memorial."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from memorial_maker.rag.static_templates import StaticTemplateLoader, STATIC_TEMPLATES

def test_static_templates():
    """Test that static templates load correctly."""
    templates_dir = Path("memorial_maker/rag/prompts/eletrico/static_templates")
    
    if not templates_dir.exists():
        print(f"❌ Templates directory not found: {templates_dir}")
        return False
    
    loader = StaticTemplateLoader(templates_dir)
    
    print("Testing static template loader...")
    print(f"Templates directory: {templates_dir}")
    print(f"\\nMapped templates: {len(STATIC_TEMPLATES)}")
    
    success_count = 0
    for section_id, template_name in STATIC_TEMPLATES.items():
        has_template = loader.has_template(template_name)
        content = loader.load_template(template_name)
        
        if has_template and content:
            print(f"✓ {section_id} -> {template_name} ({len(content)} chars)")
            success_count += 1
        else:
            print(f"✗ {section_id} -> {template_name} (NOT FOUND)")
    
    print(f"\\n{success_count}/{len(STATIC_TEMPLATES)} templates loaded successfully")
    
    # Show sample content
    if success_count > 0:
        sample_template = list(STATIC_TEMPLATES.values())[0]
        sample_content = loader.load_template(sample_template)
        print(f"\\nSample content from '{sample_template}':")
        print("=" * 60)
        print(sample_content[:300] + "..." if len(sample_content) > 300 else sample_content)
        print("=" * 60)
    
    return success_count == len(STATIC_TEMPLATES)

if __name__ == "__main__":
    success = test_static_templates()
    sys.exit(0 if success else 1)
