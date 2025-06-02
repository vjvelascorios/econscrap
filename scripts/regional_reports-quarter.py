import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep

# Define base path
DEFAULT_BASE_PATH = r"reports and files"

def get_report_types():
    """Define mappings for regional report types"""
    return {
        'texto completo': 'completo',
        'presentación ejecutiva': 'presentacion',
        'infografía': 'infografia'
    }

def download_pdf(args):
    """Single PDF download function"""
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
                    sleep(1)  # Wait before retry
            else:
                return f"File already exists: {os.path.basename(filepath)}"
        except Exception as e:
            if attempt == retry_count - 1:
                return f"Failed after {retry_count} attempts: {str(e)}"
            sleep(1)
    return "Max retries reached"

def scrape_regional_reports(url="https://www.banxico.org.mx/publicaciones-y-prensa/reportes-sobre-las-economias-regionales/reportes-economias-regionales.html", 
                          use_threading=True, max_workers=4):
    """
    Main function to scrape and download regional reports
    Parameters:
        url: Source URL
        use_threading: Enable/disable parallel downloads
        max_workers: Number of concurrent downloads
    """
    try:
        print(f"Starting download from: {url}")
        download_folder = os.path.join(DEFAULT_BASE_PATH, "banxico_regional_reports")
        Path(download_folder).mkdir(parents=True, exist_ok=True)
        
        base_url = "https://www.banxico.org.mx"
        report_types = get_report_types()
    
        def clean_filename(date, title, report_type):
            clean_title = re.sub(r'[<>:"/\\|?*]', '', title)
            clean_title = clean_title.strip().replace(' ', '-')
            return f"{date}_{report_type}_regional_{clean_title}.pdf"

        def create_dataframe_from_html(url):
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            data = {'Date': [], 'Title': [], 'Link': [], 'Type': []}
            
            rows = soup.find_all('tr')
            
            for row in rows:
                date_cell = row.find('td', class_='bmdateview')
                title_cell = row.find('td', class_='bmtextview')
                
                if date_cell and title_cell:
                    try:
                        date_str = date_cell.text.strip()
                        date = datetime.strptime(date_str, '%d/%m/%y')
                        date_formatted = date.strftime('%Y%m')
                    except:
                        date_formatted = 'unknown_date'
                    
                    links = title_cell.find_all('a', href=True)
                    for link in links:
                        link_text = link.text.strip().lower()
                        
                        report_type = None
                        for key, value in report_types.items():
                            if key in link_text:
                                report_type = value
                                break
                        
                        if report_type and link['href'].endswith('.pdf'):
                            data['Date'].append(date_formatted)
                            data['Title'].append(title_cell.contents[0].strip())
                            data['Link'].append(link['href'])
                            data['Type'].append(report_type)
            
            return pd.DataFrame(data)

        df = create_dataframe_from_html(url)
        
        # Download PDFs
        download_tasks = []
        
        for _, row in df.iterrows():
            pdf_url = f"{base_url}{row['Link']}" if row['Link'].startswith('/') else row['Link']
            clean_title = re.sub(r'[<>:"/\\|?*]', '', row['Title'])
            clean_title = clean_title.strip().replace(' ', '-')
            filename = f"{row['Date']}_{row['Type']}_{clean_title}.pdf"
            filepath = os.path.join(download_folder, filename)
            download_tasks.append((pdf_url, filepath, 3))  # 3 retries per file
        
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
                sleep(0.5)  # Delay between downloads
        
        return df
        
    except Exception as e:
        print(f"Main function error: {str(e)}")
        return None

if __name__ == "__main__":
    # Example usage with threading
    df = scrape_regional_reports(use_threading=True, max_workers=10)
    
    # Example usage without threading
    # df = scrape_regional_reports(use_threading=False)