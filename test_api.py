#!/usr/bin/env python3
"""
Simple test script for Memorial Automator API
"""

import requests
import sys
from pathlib import Path


def test_health_check(base_url: str):
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Health check passed: {data['status']}")
        print(f"   Version: {data['version']}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False


def test_generate_memorial(base_url: str, pdf_path: str):
    """Test the memorial generation endpoint"""
    print(f"\n🔍 Testing memorial generation with: {pdf_path}")
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    try:
        url = f"{base_url}/api/v1/generate_memorial"
        
        with open(pdf_path, 'rb') as f:
            files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
            data = {
                'client_id': 'default',
                'include_images': 'false'
            }
            
            print("⏳ Uploading and processing PDF (this may take a while)...")
            response = requests.post(url, files=files, data=data, timeout=300)
            response.raise_for_status()
        
        result = response.json()
        
        print("✅ Memorial generated successfully!")
        print(f"\n📊 Processing Info:")
        print(f"   Pages processed: {result['pages_processed']}")
        print(f"   Processing time: {result['processing_time_seconds']}s")
        
        if result.get('warnings'):
            print(f"   Warnings: {', '.join(result['warnings'])}")
        
        print(f"\n📝 Memorial Preview (first 500 chars):")
        print("-" * 80)
        print(result['memorial_text'][:500] + "...")
        print("-" * 80)
        
        # Save to file
        output_file = "memorial_output.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result['memorial_text'])
        print(f"\n💾 Full memorial saved to: {output_file}")
        
        return True
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out (processing took too long)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"   Error details: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def main():
    base_url = "http://localhost:8000"
    
    print("=" * 80)
    print("🧪 Memorial Automator API Test")
    print("=" * 80)
    print()
    
    # Test health check
    if not test_health_check(base_url):
        print("\n❌ Server is not responding. Make sure it's running:")
        print("   python -m app.main")
        print("   or")
        print("   ./start.sh")
        sys.exit(1)
    
    # Test memorial generation if PDF provided
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        test_generate_memorial(base_url, pdf_path)
    else:
        print("\n⚠️  No PDF file provided for testing")
        print("To test memorial generation, run:")
        print(f"   python {sys.argv[0]} path/to/your/project.pdf")
    
    print("\n" + "=" * 80)
    print("✅ Tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()

