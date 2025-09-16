#!/usr/bin/env python3
"""
Automated Banxico Library PDF Renamer
Automatically renames PDF files based on the date found in the cover page.
Safe to run multiple times - skips already renamed files.
"""

import os
import pdfplumber
import re
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Spanish month mapping
MONTHS_ES_TO_NUM = {
    'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
    'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
    'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
}

def extract_date_from_pdf(pdf_path):
    """Extract date from PDF cover page"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) == 0:
                return None
            
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            
            if not text:
                return None
            
            # Look for Spanish month and year pattern
            pattern = r'\b(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+(\d{4})\b'
            match = re.search(pattern, text, re.IGNORECASE)
            
            if match:
                month_name = match.group(1).lower()
                year = match.group(2)
                month_num = MONTHS_ES_TO_NUM.get(month_name)
                
                if month_num:
                    return f"{year}-{month_num}"
                
    except Exception as e:
        logging.error(f"Error reading PDF {pdf_path}: {e}")
    
    return None

def is_already_renamed(filename):
    """Check if file has already been renamed"""
    # If filename starts with YYYY-MM format, it's already renamed
    if re.match(r'^\d{4}-\d{2}', filename):
        return True
    
    # If filename contains only GUID after date prefix, needs renaming
    core_name = re.sub(r'^\d{6}_', '', filename)  # Remove YYYYMM_ prefix
    core_name = re.sub(r'\.pdf$', '', core_name, re.IGNORECASE)  # Remove .pdf
    
    # If it's a GUID pattern, it needs renaming
    if re.match(r'^[{]?[0-9A-F-]+[}]?$', core_name, re.IGNORECASE):
        return False
    
    # If it has readable text, it's probably already renamed
    return len(re.findall(r'[a-zA-Z]{3,}', core_name)) > 0

def generate_new_filename(date_str):
    """Generate new filename based on extracted date"""
    year, month = date_str.split('-')
    month_names = {
        '01': 'Enero', '02': 'Febrero', '03': 'Marzo', '04': 'Abril',
        '05': 'Mayo', '06': 'Junio', '07': 'Julio', '08': 'Agosto',
        '09': 'Septiembre', '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'
    }
    month_name = month_names.get(month, f"Mes{month}")
    return f"{date_str}_Boletin_Biblioteca_Banxico_{month_name}_{year}.pdf"

def rename_banxico_library_pdfs():
    """Main function to rename PDF files"""
    directory = Path("reports and files/banxico_library_updates")
    
    if not directory.exists():
        logging.error(f"Directory {directory} does not exist")
        return False
    
    pdf_files = list(directory.glob("*.pdf"))
    logging.info(f"Found {len(pdf_files)} PDF files to process")
    
    renamed_count = 0
    skipped_count = 0
    error_count = 0
    
    for pdf_file in pdf_files:
        original_name = pdf_file.name
        
        # Skip if already renamed
        if is_already_renamed(original_name):
            logging.info(f"⏭️  Skipping {original_name} - Already renamed")
            skipped_count += 1
            continue
        
        logging.info(f"🔍 Processing: {original_name}")
        
        # Extract date
        date_str = extract_date_from_pdf(pdf_file)
        if not date_str:
            logging.error(f"❌ Could not extract date from {original_name}")
            error_count += 1
            continue
        
        # Generate new filename
        new_filename = generate_new_filename(date_str)
        new_path = directory / new_filename
        
        # Check if target exists
        if new_path.exists():
            logging.warning(f"⚠️  Target {new_filename} already exists, skipping")
            skipped_count += 1
            continue
        
        # Rename file
        try:
            pdf_file.rename(new_path)
            logging.info(f"✅ Renamed: {original_name} → {new_filename}")
            renamed_count += 1
        except Exception as e:
            logging.error(f"❌ Error renaming {original_name}: {e}")
            error_count += 1
    
    # Summary
    logging.info(f"\n📊 SUMMARY - Renamed: {renamed_count}, Skipped: {skipped_count}, Errors: {error_count}")
    return renamed_count > 0

if __name__ == "__main__":
    logging.info("🚀 Starting Banxico Library PDF renaming process")
    success = rename_banxico_library_pdfs()
    if success:
        logging.info("✅ Renaming process completed successfully")
    else:
        logging.info("ℹ️  No files were renamed")
