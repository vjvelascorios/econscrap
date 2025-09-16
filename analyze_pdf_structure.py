#!/usr/bin/env python3
"""
PDF Content Analyzer - Analyze the content of Banxico library PDFs to understand their structure
"""

import os
import pdfplumber
import re
from pathlib import Path

def analyze_pdf_sample(pdf_path):
    """Analyze a single PDF to understand its structure"""
    print(f"🔍 Analyzing: {os.path.basename(pdf_path)}")
    print("=" * 60)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Get first page (cover page)
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            
            print("📄 First page text:")
            print("-" * 40)
            print(text[:1000])  # First 1000 characters
            print("-" * 40)
            
            # Look for date patterns
            date_patterns = [
                r'\b\d{1,2}\s+de\s+\w+\s+de\s+\d{4}\b',  # "15 de marzo de 2024"
                r'\b\w+\s+\d{4}\b',  # "marzo 2024"
                r'\b\d{4}\b',  # just year
                r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # DD/MM/YYYY
                r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
            ]
            
            print("\n📅 Found date patterns:")
            for pattern in date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    print(f"  Pattern '{pattern}': {matches}")
            
            print(f"\n📊 Total pages: {len(pdf.pages)}")
            
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")

def main():
    """Analyze a few sample PDFs"""
    pdf_dir = Path("reports and files/banxico_library_updates")
    
    # Get a few sample PDFs
    pdf_files = list(pdf_dir.glob("*.pdf"))[:3]  # First 3 PDFs
    
    if not pdf_files:
        print("❌ No PDF files found in the directory")
        return
    
    print(f"🔍 Analyzing {len(pdf_files)} sample PDFs...")
    print()
    
    for pdf_file in pdf_files:
        analyze_pdf_sample(pdf_file)
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
