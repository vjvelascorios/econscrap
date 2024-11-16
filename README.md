# Banxico Reports Scraper

A collection of scripts to automatically download reports from Banco de México (Banxico) website. The scraper handles multiple report types and supports parallel downloads.

## Features

- Downloads multiple types of reports:
  - Quarterly Reports ([`quarterly_reports-quarter.py`](scripts/quarterly_reports-quarter.py))
  - Regional Reports ([`regional_reports-quarter.py`](scripts/regional_reports-quarter.py)) 
  - Library updates ([`library_updates-monthly.py`](scripts/library_updates-monthly.py))
  - Private Sector Expectations ([`private_sector_expectations-monthly.py`](scripts/private_sector_expectations-monthly.py))
- Supports parallel downloads using threading
- Organizes files by date and type
- Handles retry logic for failed downloads
- Creates structured filenames with date prefixes

## Requirements

```
requests
beautifulsoup4
pandas
pathlib
tqdm
```

## Installation

```sh
pip install requests beautifulsoup4 pandas pathlib tqdm
```

## Usage

Each script can be run independently:

```sh
# Download quarterly reports
python "scripts/informes trimestrales.py"

# Download regional reports 
python "scripts/informes regionales.py"

# Download library updates
python "scripts/library_updates.py"
```

### Configuration

- Default save location: `reports and files/`
- Threading enabled by default with 10 workers
- Configurable retry logic for failed downloads

## Output Structure

```
reports and files/
├── banxico_quarterly_reports/
├── banxico_regional_reports/
└── banxico_library_updates/
```

## Error Handling

- Automatic retries for failed downloads
- Skips existing files to avoid duplicates
- Detailed error logging and progress tracking

## Posible errors:

Just in case you get an error, check the filepath where the files are being saved. You can change the path in the scripts.

## TODO

- [] Another posible updates like Monetary Policy Reports, Surveys, Press Reports, Stability Reports, etc.
- [] workflows for automatic downloads and updates.
- [] Anual compilation reports.