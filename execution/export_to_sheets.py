"""
Export lead data to Google Sheets.

This script creates a Google Sheet and populates it with lead data.
"""

import os
import sys
import json
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_sheets_client():
    """
    Initialize and return Google Sheets client.
    
    Returns:
        gspread.Client: Authenticated Google Sheets client
    """
    creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH', './credentials.json')
    
    if not os.path.exists(creds_path):
        raise FileNotFoundError(f"Credentials file not found: {creds_path}")
    
    # Define the scopes
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Authenticate
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    client = gspread.authorize(creds)
    
    return client


def create_spreadsheet(client, title):
    """
    Create a new Google Spreadsheet.
    
    Args:
        client: Google Sheets client
        title (str): Spreadsheet title
        
    Returns:
        gspread.Spreadsheet: Created spreadsheet
    """
    spreadsheet = client.create(title)
    
    # Make it shareable (anyone with link can view)
    spreadsheet.share('', perm_type='anyone', role='reader')
    
    return spreadsheet


def export_leads_to_sheet(leads, sheet_name=None):
    """
    Export leads to a new Google Sheet.
    
    Args:
        leads (list): List of lead dictionaries
        sheet_name (str): Optional custom sheet name
        
    Returns:
        str: URL of the created spreadsheet
    """
    if not leads:
        raise ValueError("No leads to export")
    
    # Initialize client
    client = get_sheets_client()
    
    # Create spreadsheet
    if not sheet_name:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        sheet_name = f"Leads Export - {timestamp}"
    
    print(f"Creating spreadsheet: {sheet_name}")
    spreadsheet = create_spreadsheet(client, sheet_name)
    worksheet = spreadsheet.sheet1
    
    # Prepare headers (extract all unique keys from leads)
    all_keys = set()
    for lead in leads:
        all_keys.update(lead.keys())
    
    headers = sorted(list(all_keys))
    
    # Prepare data rows
    data = [headers]
    for lead in leads:
        row = [lead.get(key, '') for key in headers]
        data.append(row)
    
    # Write data to sheet
    print(f"Writing {len(leads)} leads to spreadsheet...")
    worksheet.update('A1', data)
    
    # Format header row
    worksheet.format('A1:Z1', {
        'textFormat': {'bold': True},
        'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
    })
    
    # Get shareable URL
    url = spreadsheet.url
    print(f"✓ Spreadsheet created successfully!")
    print(f"URL: {url}")
    
    return url


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python export_to_sheets.py <leads_json_file> [sheet_name]")
        print("Example: python export_to_sheets.py .tmp/full_scrape.json 'Software Dev Leads'")
        sys.exit(1)
    
    leads_file = sys.argv[1]
    sheet_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Load leads from file
    with open(leads_file, 'r') as f:
        leads = json.load(f)
    
    try:
        url = export_leads_to_sheet(leads, sheet_name)
        
        # Save URL to file for reference
        url_file = leads_file.replace('.json', '_sheet_url.txt')
        with open(url_file, 'w') as f:
            f.write(url)
        
        print(f"\nSheet URL saved to {url_file}")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
