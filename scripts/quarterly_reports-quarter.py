# scraping reports from Banxico website (quarterly reports)
## informes trimestrales
# https://www.banxico.org.mx/publicaciones-y-prensa/informes-trimestrales/informes-trimestrales-precios.html

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

# Define base path
DEFAULT_BASE_PATH = r"C:\\Users\\vjvelascorios\\Desktop\\econscrap\\reports and files"
Path(DEFAULT_BASE_PATH).mkdir(parents=True, exist_ok=True)

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

if __name__ == "__main__":
    quarterly_url = "https://www.banxico.org.mx/publicaciones-y-prensa/informes-trimestrales/informes-trimestrales-precios.html"
    
    # With threading (default)
    df = scrape_banxico_reports(quarterly_url, report_type="quarterly", use_threading=True, max_workers=10)
    
    # Without threading (uncomment to use)
    # df = scrape_banxico_reports(quarterly_url, report_type="quarterly", use_threading=False)
    
    if df is not None:
        print(f"Successfully processed {len(df)} documents")
    else:
        print("Script failed to execute properly")
