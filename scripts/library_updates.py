import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep
from pathlib import Path

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

def scrape_library_updates(url=None, use_threading=True, max_workers=4):
    """Main function to scrape and download library updates"""
    if url is None:
        url = "https://www.banxico.org.mx/servicios/boletin-mensual-de-la-biblioteca-del-banco-de-mexi/boletin-mensual-biblioteca-pu.html"

    # Define and create base folder
    local_folder = r"C:\\Users\\vjvelascorios\\Desktop\\econscrap\\reports and files\\banxico_library_updates"
    Path(local_folder).mkdir(parents=True, exist_ok=True)
    print(f"Saving files to: {local_folder}")

    try:
        print(f"Fetching content from: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to access URL. Status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        download_tasks = []

        # Find all PDF links
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf'):
                pdf_url = urljoin(url, href)
                filename = os.path.basename(href)
                
                # Add date prefix to filename
                date_str = datetime.now().strftime('%Y%m')
                if not filename.startswith(date_str):
                    filename = f"{date_str}_{filename}"
                
                filepath = os.path.join(local_folder, filename)
                download_tasks.append((pdf_url, filepath, 3))

        print(f"Found {len(download_tasks)} PDFs to download")

        # Choose download method
        if use_threading and download_tasks:
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
                sleep(0.5)

        return len(download_tasks)

    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    # With threading (default)
    result = scrape_library_updates(use_threading=True, max_workers=10)
    
    # Without threading (uncomment to use)
    # result = scrape_library_updates(use_threading=False)
    
    if result is not None:
        print(f"Process completed. Downloaded {result} files")
    else:
        print("Script failed to execute properly")

