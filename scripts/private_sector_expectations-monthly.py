# scraping reports from Banxico website (quarterly reports)
# expectativas sector privado
# https://www.banxico.org.mx/publicaciones-y-prensa/encuestas-sobre-las-expectativas-de-los-especialis/encuestas-expectativas-del-se.html

# paquetes
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from pathlib import Path
import re
from datetime import datetime   
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep
import time
from urllib.parse import urljoin
import logging
from tqdm import tqdm
import hashlib
from typing import Optional, Tuple, Dict
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('banxico_downloads.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class ReportInfo:
    pub_date: datetime
    title: str
    url: str
    filename: str

class BanxicoDownloader:
    def __init__(self, base_path: str, max_workers: int = 3, timeout: int = 30):
        self.base_path = Path(base_path)
        self.max_workers = max_workers
        self.timeout = timeout
        self.session = requests.Session()

    def verify_pdf(self, filepath: Path) -> bool:
        """Verify if downloaded file is a valid PDF"""
        try:
            with open(filepath, 'rb') as f:
                header = f.read(4)
                return header.startswith(b'%PDF')
        except Exception as e:
            logging.error(f"Error verifying PDF {filepath}: {e}")
            return False

    def download_report(self, report: ReportInfo) -> Optional[Path]:
        filepath = self.base_path / f"{report.filename}.pdf"
        
        if filepath.exists() and self.verify_pdf(filepath):
            logging.info(f"File already exists and valid: {filepath}")
            return filepath

        try:
            response = self.session.get(report.url, timeout=self.timeout)
            response.raise_for_status()
            
            filepath.write_bytes(response.content)
            
            if not self.verify_pdf(filepath):
                filepath.unlink()
                raise ValueError("Downloaded file is not a valid PDF")
                
            return filepath
            
        except Exception as e:
            logging.error(f"Error downloading {report.url}: {e}")
            if filepath.exists():
                filepath.unlink()
            return None

    def download_all_reports(self, reports: list[ReportInfo]) -> None:
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.download_report, report): report 
                      for report in reports}
            
            with tqdm(total=len(reports), desc="Downloading reports") as pbar:
                for future in as_completed(futures):
                    report = futures[future]
                    try:
                        filepath = future.result()
                        if filepath:
                            logging.info(f"Successfully downloaded: {filepath}")
                    except Exception as e:
                        logging.error(f"Failed to download {report.filename}: {e}")
                    finally:
                        pbar.update(1)

# Define constants
BASE_URL = "https://www.banxico.org.mx"
EXPECTATIONS_URL = "https://www.banxico.org.mx/publicaciones-y-prensa/encuestas-sobre-las-expectativas-de-los-especialis/encuestas-expectativas-del-se.html"
DEFAULT_BASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports and files", "private_sector_expectations")

def extract_date_and_title(row):
    """Extract date and report type from the row"""
    date_cell = row.find('td', class_='bmdateview')
    title_cell = row.find('td', class_='bmtextview')
    
    if date_cell and title_cell:
        date_str = date_cell.text.strip()
        # Convert date from DD/MM/YY to YYYYMM format
        try:
            date = datetime.strptime(date_str, '%d/%m/%y')
            date_formatted = date.strftime('%Y%m')
        except:
            date_formatted = 'unknown_date'
        
        return date_formatted, title_cell
    return None, None

def create_dataframe_from_html(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    data = {'Date': [], 'Title': [], 'Link': [], 'Type': []}
    
    # Find all table rows
    rows = soup.find_all('tr')
    
    for row in rows:
        date, title_cell = extract_date_and_title(row)
        if date and title_cell:
            # Find all links in the title cell
            links = title_cell.find_all('a', href=True)
            for link in links:
                # Extract report type from the link text
                link_text = link.text.strip().lower()
                if 'texto completo' in link_text:
                    report_type = 'completo'
                elif 'resumen' in link_text:
                    report_type = 'resumen'
                elif 'presentación ejecutiva' in link_text:
                    report_type = 'presentacion'
                elif 'infografía' in link_text:
                    report_type = 'infografia'
                else:
                    continue  # Skip non-PDF links
                
                if link['href'].endswith('.pdf'):
                    data['Date'].append(date)
                    data['Title'].append(title_cell.contents[0].strip())
                    data['Link'].append(link['href'])
                    data['Type'].append(report_type)
    
    return pd.DataFrame(data)

def clean_filename(date, title, report_type):
    # Create filename format: YYYYMM_type_clean-title.pdf
    clean_title = re.sub(r'[<>:"/\\|?*]', '', title)
    clean_title = clean_title.strip().replace(' ', '-')
    return f"{date}_{report_type}_{clean_title}.pdf"

def download_pdf(args):
    """Single PDF download function with retries"""
    pdf_url, filepath, retry_count = args
    for attempt in range(retry_count):
        try:
            if not os.path.exists(filepath):
                response = requests.get(pdf_url, stream=True)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    return f"Successfully downloaded: {os.path.basename(filepath)}"
                else:
                    sleep(1)
            else:
                return f"File already exists: {os.path.basename(filepath)}"
        except Exception as e:
            if attempt == retry_count - 1:
                return f"Failed after {retry_count} attempts: {str(e)}"
            sleep(1)
    return "Max retries reached"

def scrape_banxico_reports(url, report_type="quarterly", use_threading=True, max_workers=4):
    """Main function to scrape and download reports with optional threading"""
    try:
        print(f"Starting download from: {url}")
        download_folder = os.path.join(DEFAULT_BASE_PATH, f"banxico_{report_type}_reports")
        Path(download_folder).mkdir(parents=True, exist_ok=True)
        print(f"Download folder: {download_folder}")

        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to get webpage. Status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        data = {'Date': [], 'Title': [], 'Link': [], 'Type': []}
        rows = soup.find_all('tr')
        print(f"Found {len(rows)} rows in the table")

        for row in rows:
            date, title_cell = extract_date_and_title(row)
            if date and title_cell:
                links = title_cell.find_all('a', href=True)
                for link in links:
                    link_text = link.text.strip().lower()
                    if 'texto completo' in link_text:
                        report_type = 'completo'
                    elif 'resumen' in link_text:
                        report_type = 'resumen'
                    elif 'presentación ejecutiva' in link_text:
                        report_type = 'presentacion'
                    elif 'infografía' in link_text:
                        report_type = 'infografia'
                    else:
                        continue
                    
                    if link['href'].endswith('.pdf'):
                        data['Date'].append(date)
                        data['Title'].append(title_cell.contents[0].strip())
                        data['Link'].append(link['href'])
                        data['Type'].append(report_type)

        df = pd.DataFrame(data)
        
        # Create download tasks
        base_url = "https://www.banxico.org.mx"
        download_tasks = []
        
        for _, row in df.iterrows():
            pdf_url = f"{base_url}{row['Link']}" if row['Link'].startswith('/') else row['Link']
            clean_title = re.sub(r'[<>:"/\\|?*]', '', row['Title'])
            clean_title = clean_title.strip().replace(' ', '-')
            filename = f"{row['Date']}_{row['Type']}_{clean_title}.pdf"
            filepath = os.path.join(download_folder, filename)
            download_tasks.append((pdf_url, filepath, 3))

        # Choose download method
        if use_threading:
            print(f"Starting parallel download with {max_workers} workers")
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(download_pdf, task) for task in download_tasks]
                for future in as_completed(futures):
                    print(future.result())
        else:
            print("Starting sequential download")
            for task in download_tasks:
                result = download_pdf(task)
                print(result)
                sleep(0.5)  # Prevent rate limiting

        return df

    except Exception as e:
        print(f"Main function error: {str(e)}")
        return None

def parse_month_from_title(title):
    """Extract the reported month from title"""
    month_map = {
        'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
        'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
        'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
    }
    match = re.search(r':\s*(\w+)\s+(\d{4})', title)
    if match:
        month, year = match.groups()
        month_num = month_map.get(month.lower())
        return month_num, year, month.lower()
    return None, None, None

def format_filename(pub_date, report_month, report_year):
    """Format filename as YYYY.MM.DD-ESESP-monthYY"""
    short_year = report_year[-2:]
    return f"{pub_date.strftime('%Y.%m.%d')}-ESESP-{report_month}{short_year}"

def download_pdf(url, filename, base_path):
    """Download PDF file with retry logic"""
    full_path = os.path.join(base_path, f"{filename}.pdf")
    if os.path.exists(full_path):
        print(f"File already exists: {filename}")
        return
    
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            with open(full_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {filename}")
            time.sleep(1)  # Be nice to the server
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {filename}: {str(e)}")
            if attempt == 2:
                print(f"Failed to download {filename}")
            time.sleep(2)

def main():
    # Create output directory
    output_dir = Path(DEFAULT_BASE_PATH)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting download from: {EXPECTATIONS_URL}")
    print(f"Download folder: {output_dir}")
    
    # Get the webpage content
    response = requests.get(EXPECTATIONS_URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all rows with reports
    rows = soup.find_all('tr')
    print(f"Found {len(rows)} rows in the table")
    
    for row in rows:
        try:
            date_cell = row.find('td', class_='bmdateview')
            title_cell = row.find('td', class_='bmtextview')
            
            if not (date_cell and title_cell):
                continue
                
            date_str = date_cell.find('span').text.strip()
            title = title_cell.get_text(strip=True)
            pdf_link = title_cell.find('a', href=lambda x: x and x.endswith('.pdf'))
            
            if not pdf_link:
                continue
                
            pub_date = datetime.strptime(date_str, '%d/%m/%y')
            month_num, report_year, report_month = parse_month_from_title(title)
            
            if not all([month_num, report_year, report_month]):
                continue
            
            filename = format_filename(pub_date, report_month, report_year)
            pdf_url = urljoin(BASE_URL, pdf_link['href'])
            
            download_pdf(pdf_url, filename, output_dir)
            time.sleep(1)  # Be nice to the server
            
        except Exception as e:
            print(f"Error processing row: {e}")
            continue

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Script failed to execute properly: {e}")

    quarterly_url = "https://www.banxico.org.mx/publicaciones-y-prensa/encuestas-sobre-las-expectativas-de-los-especialis/encuestas-expectativas-del-se.html"
    
    # With threading (default)
    df = scrape_banxico_reports(quarterly_url, report_type="quarterly", use_threading=True, max_workers=10)
    
    # Without threading (uncomment to use)
    # df = scrape_banxico_reports(quarterly_url, report_type="quarterly", use_threading=False)
    
    if df is not None:
        print(f"Successfully processed {len(df)} documents")
    else:
        print("Script failed to execute properly")

import logging
import time
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

@dataclass
class ScrapingConfig:
    use_threading: bool = True
    max_workers: int = min(32, os.cpu_count() * 4)  # Optimal thread count
    timeout: int = 30
    retry_attempts: int = 3

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def scrape_banxico_reports_optimized(
    url: str,
    report_type: str = "quarterly",
    config: Optional[ScrapingConfig] = None
) -> Optional[pd.DataFrame]:
    logger = setup_logging()
    start_time = time.perf_counter()
    
    if config is None:
        config = ScrapingConfig()
    
    try:
        if config.use_threading:
            with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
                df = scrape_banxico_reports(
                    url,
                    report_type=report_type,
                    use_threading=True,
                    max_workers=config.max_workers
                )
        else:
            df = scrape_banxico_reports(
                url,
                report_type=report_type,
                use_threading=False
            )
        
        if df is not None and not df.empty:
            execution_time = time.perf_counter() - start_time
            logger.info(f"Successfully processed {len(df)} documents in {execution_time:.2f} seconds")
            return df
        else:
            logger.error("No data was retrieved")
            return None
            
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        return None

# Usage
quarterly_url = "https://www.banxico.org.mx/publicaciones-y-prensa/encuestas-sobre-las-expectativas-de-los-especialis/encuestas-expectativas-del-se.html"

config = ScrapingConfig(
    use_threading=True,
    max_workers=min(32, os.cpu_count() * 4),
    timeout=30,
    retry_attempts=3
)

df = scrape_banxico_reports_optimized(quarterly_url, report_type="quarterly", config=config)

import os
from pathlib import Path

# Define base paths as constants
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
REPORTS_DIR = BASE_DIR / "reports and files" / "private_sector_expectations"

@dataclass
class PathConfig:
    base_dir: Path = REPORTS_DIR
    
    def __post_init__(self):
        # Ensure only the correct directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def get_file_path(self, filename: str) -> Path:
        return self.base_dir / filename

def setup_directories():
    """Initialize directory structure"""
    try:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        logging.info(f"Directory structure verified at {REPORTS_DIR}")
    except Exception as e:
        logging.error(f"Failed to create directory structure: {e}")
        raise

# Add this at the start of your main execution
path_config = PathConfig()
setup_directories()

# When saving files, use:
def save_file(content, filename):
    file_path = path_config.get_file_path(filename)
    with open(file_path, 'wb') as f:
        f.write(content)
