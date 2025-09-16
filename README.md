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

## GitHub Actions Automation

This repository includes automated workflows that run on GitHub Actions to download reports automatically:

### Schedule
- **Library Updates**: 3rd of each month at 00:00 Mexico City time (06:00 UTC)
- **Quarterly Reports**: 28th-29th of every 3rd month at 00:00 Mexico City time (06:00 UTC)  
- **Regional Reports**: 11th-15th of every 3rd month at 00:00 Mexico City time (06:00 UTC)

### Manual Execution
You can also trigger the workflow manually from the GitHub Actions tab.

### Troubleshooting

If the GitHub Actions are not working:

1. **Run Local Tests**: 
   ```sh
   python test_workflow.py
   ```

2. **Check Debug Information**:
   ```sh 
   python debug_workflow.py
   ```

3. **Common Issues**:
   - Branch mismatch (ensure workflow uses 'master' not 'main')
   - Schedule condition mismatch with cron expressions
   - Missing dependencies in requirements.txt
   - Incorrect file paths for artifacts

### Recent Fixes

- ✅ Fixed branch name from 'main' to 'master'
- ✅ Fixed schedule condition times to match cron expressions
- ✅ Added debug and test scripts for troubleshooting
- ✅ Reorganized workflow steps for better execution order

## TODO

- [ ] Add Monetary Policy Reports, Surveys, Press Reports, Stability Reports, etc.
- [x] Workflows for automatic downloads and updates
- [ ] Annual compilation reports
- [ ] Error notification system for failed downloads
- [ ] Data validation and quality checks
