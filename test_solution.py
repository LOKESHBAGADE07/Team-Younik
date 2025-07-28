#!/usr/bin/env python3
"""
Test script for the PDF processing solution
"""

import json
import subprocess
import time
from pathlib import Path
import tempfile
import shutil

def create_test_pdf():
    """Create a simple test PDF using reportlab if available"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            c = canvas.Canvas(tmp.name, pagesize=letter)
            c.drawString(100, 750, "Test PDF Document")
            c.drawString(100, 700, "This is a sample PDF for testing the processing solution.")
            c.drawString(100, 650, "Chapter 1: Introduction")
            c.drawString(100, 600, "This chapter covers the basic concepts.")
            c.showPage()
            c.save()
            return tmp.name
    except ImportError:
        print("reportlab not available, skipping test PDF creation")
        return None

def test_docker_build():
    """Test Docker image building"""
    print("Testing Docker build...")
    try:
        result = subprocess.run([
            'docker', 'build', '--platform', 'linux/amd64', 
            '-t', 'pdf-processor-test', '.'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Docker build successful")
            return True
        else:
            print("❌ Docker build failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Docker build error: {e}")
        return False

def test_processing():
    """Test PDF processing with Docker container"""
    print("Testing PDF processing...")
    
    # Create test directories
    input_dir = Path("test_input")
    output_dir = Path("test_output")
    
    try:
        input_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)
        
        # Create or copy test PDF
        test_pdf = create_test_pdf()
        if test_pdf:
            shutil.copy(test_pdf, input_dir / "test_document.pdf")
            Path(test_pdf).unlink()  # Remove temp file
        else:
            print("No test PDF created, please place a PDF in test_input/ directory")
            return False
        
        # Run Docker container
        start_time = time.time()
        result = subprocess.run([
            'docker', 'run', '--rm',
            '-v', f'{input_dir.absolute()}:/app/input:ro',
            '-v', f'{output_dir.absolute()}:/app/output',
            '--network', 'none',
            'pdf-processor-test'
        ], capture_output=True, text=True, timeout=60)
        
        processing_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ Processing completed in {processing_time:.2f}s")
            print("Output:", result.stdout)
            
            # Check for output files
            json_files = list(output_dir.glob("*.json"))
            if json_files:
                print(f"✅ Generated {len(json_files)} JSON file(s)")
                
                # Validate JSON structure
                for json_file in json_files:
                    try:
                        with open(json_file) as f:
                            data = json.load(f)
                        
                        required_keys = ['document_info', 'content_analysis', 'extracted_data']
                        if all(key in data for key in required_keys):
                            print(f"✅ {json_file.name} has valid structure")
                        else:
                            print(f"❌ {json_file.name} missing required keys")
                    except json.JSONDecodeError:
                        print(f"❌ {json_file.name} is not valid JSON")
                
                return True
            else:
                print("❌ No JSON output files generated")
                return False
        else:
            print("❌ Processing failed:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Processing test error: {e}")
        return False
    finally:
        # Cleanup
        if input_dir.exists():
            shutil.rmtree(input_dir)
        if output_dir.exists():
            shutil.rmtree(output_dir)

def main():
    """Run all tests"""
    print("🧪 Testing PDF Processing Solution")
    print("=" * 40)
    
    success = True
    
    # Test Docker build
    if not test_docker_build():
        success = False
    
    print()
    
    # Test processing
    if not test_processing():
        success = False
    
    print()
    print("=" * 40)
    if success:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed")
    
    return success

if __name__ == "__main__":
    main()