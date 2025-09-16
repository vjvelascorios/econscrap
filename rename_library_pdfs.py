#!/usr/bin/env python3
"""
Banxico Library PDF Renamer
Renames PDF files based on the date found in the cover page of the document.
Skips files that have already been renamed to avoid duplicates.
"""

import os
import pdfplumber
import re
from pathlib import Path
from datetime import datetime
import shutil
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_renaming.log'),
        logging.StreamHandler()
    ]
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
                logging.warning(f"PDF {pdf_path} has no pages")
                return None
            
            # Extract text from first page
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            
            if not text:
                logging.warning(f"Could not extract text from {pdf_path}")
                return None
            
            # Look for Spanish month and year pattern
            # Pattern: MONTH YYYY (e.g., "JUNIO 2025", "AGOSTO 2024")
            pattern = r'\b(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+(\d{4})\b'
            match = re.search(pattern, text, re.IGNORECASE)
            
            if match:
                month_name = match.group(1).lower()
                year = match.group(2)
                month_num = MONTHS_ES_TO_NUM.get(month_name)
                
                if month_num:
                    return f"{year}-{month_num}"
                else:
                    logging.warning(f"Unknown month '{month_name}' in {pdf_path}")
                    return None
            else:
                logging.warning(f"No date pattern found in {pdf_path}")
                return None
                
    except Exception as e:
        logging.error(f"Error reading PDF {pdf_path}: {e}")
        return None

def is_already_renamed(filename):
    """Check if file has already been renamed (has readable name)"""
    # If filename starts with YYYY-MM format, it's already renamed
    if re.match(r'^\d{4}-\d{2}', filename):
        return True
    
    # If filename contains readable words (not just GUIDs), it's likely renamed
    # Remove the date prefix and extension to check the core name
    core_name = re.sub(r'^\d{6}_', '', filename)  # Remove YYYYMM_ prefix
    core_name = re.sub(r'\.pdf$', '', core_name, re.IGNORECASE)  # Remove .pdf
    
    # If it's mostly a GUID pattern, it needs renaming
    if re.match(r'^[{]?[0-9A-F-]+[}]?$', core_name, re.IGNORECASE):
        return False
    
    # If it has readable text, it's probably already renamed
    if len(re.findall(r'[a-zA-Z]{3,}', core_name)) > 0:
        return True
        
    return False

def generate_new_filename(original_filename, date_str):
    """Generate new filename based on extracted date"""
    # Format: YYYY-MM_Boletin_Biblioteca_BanxicoYYYY-MM.pdf
    year_month = date_str.replace('-', '')  # Convert 2024-08 to 202408
    new_name = f"{date_str}_Boletin_Biblioteca_Banxico_{year_month}.pdf"
    return new_name

def rename_pdf_files(directory_path, dry_run=False):
    """Rename all PDF files in the directory based on their content"""
    directory = Path(directory_path)
    
    if not directory.exists():
        logging.error(f"Directory {directory_path} does not exist")
        return
    
    pdf_files = list(directory.glob("*.pdf"))
    
    if not pdf_files:
        logging.info(f"No PDF files found in {directory_path}")
        return
    
    logging.info(f"Found {len(pdf_files)} PDF files to process")
    
    renamed_count = 0
    skipped_count = 0
    error_count = 0
    
    for pdf_file in pdf_files:
        original_name = pdf_file.name
        
        # Check if already renamed
        if is_already_renamed(original_name):
            logging.info(f"⏭️  Skipping {original_name} - Already renamed")
            skipped_count += 1
            continue
        
        logging.info(f"🔍 Processing: {original_name}")
        
        # Extract date from PDF
        date_str = extract_date_from_pdf(pdf_file)
        
        if not date_str:
            logging.error(f"❌ Could not extract date from {original_name}")
            error_count += 1
            continue
        
        # Generate new filename
        new_filename = generate_new_filename(original_name, date_str)
        new_path = directory / new_filename
        
        # Check if new filename already exists
        if new_path.exists():
            logging.warning(f"⚠️  Target file {new_filename} already exists, skipping {original_name}")
            skipped_count += 1
            continue
        
        if dry_run:
            logging.info(f"🔮 DRY RUN: Would rename {original_name} → {new_filename}")
        else:
            try:
                # Rename the file
                pdf_file.rename(new_path)
                logging.info(f"✅ Renamed: {original_name} → {new_filename}")
                renamed_count += 1
            except Exception as e:
                logging.error(f"❌ Error renaming {original_name}: {e}")
                error_count += 1
    
    # Summary
    logging.info(f"\n📊 SUMMARY:")
    logging.info(f"   ✅ Renamed: {renamed_count}")
    logging.info(f"   ⏭️  Skipped: {skipped_count}")
    logging.info(f"   ❌ Errors: {error_count}")

def main():
    """Main function"""
    library_updates_dir = "reports and files/banxico_library_updates"
    
    print("📚 Banxico Library PDF Renamer")
    print("=" * 50)
    print(f"Target directory: {library_updates_dir}")
    print()
    
    # Ask user if they want to do a dry run first
    response = input("Do you want to do a dry run first? (y/n): ").lower().strip()
    
    if response == 'y':
        print("\n🔮 DRY RUN MODE - No files will be renamed")
        print("=" * 50)
        rename_pdf_files(library_updates_dir, dry_run=True)
        
        print("\n" + "=" * 50)
        response = input("Proceed with actual renaming? (y/n): ").lower().strip()
    
    if response == 'y' or response != 'n':
        print("\n🔄 RENAMING FILES")
        print("=" * 50)
        rename_pdf_files(library_updates_dir, dry_run=False)
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main()
