# Lead Scraping Workflow

Automated workflow to scrape industry-specific leads from LinkedIn using Apify, validate data quality, and export to Google Sheets.

## Features

- **Test Run Validation**: Scrapes 25 leads first to verify quality (>80% match)
- **Quality Control**: Automatically validates leads against target industry
- **Smart Retry**: Prompts for filter adjustment if quality is low
- **Google Sheets Export**: Creates shareable spreadsheet with formatted data
- **Configurable**: Flexible input parameters for different industries

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Credentials

#### Apify API Token

1. Go to [Apify Console](https://console.apify.com/account/integrations)
2. Copy your API token
3. Create `.env` file from template:
   ```bash
   cp .env.example .env
   ```
4. Add your token to `.env`:
   ```
   APIFY_API_TOKEN=your_actual_token_here
   ```

#### Google Sheets Credentials

1. Create a Google Cloud Project
2. Enable Google Sheets API and Google Drive API
3. Create a Service Account
4. Download credentials JSON file
5. Save as `credentials.json` in project root
6. Share your Google Sheets with the service account email

[Detailed Guide](https://docs.gspread.org/en/latest/oauth2.html#for-bots-using-service-account)

### 3. Prepare Actor Input

Create a JSON file with Apify actor input parameters. See `example_input.json`:

```json
{
  "searchKeywords": "software engineer",
  "locations": ["United States"],
  "maxResults": 25
}
```

Adjust parameters based on the Apify actor documentation.

## Usage

### Basic Usage

```bash
python execution/orchestrate_lead_scraping.py \
  --industry "Software Development" \
  --input-file example_input.json
```

### Test Run Only

```bash
python execution/orchestrate_lead_scraping.py \
  --industry "Healthcare" \
  --input-file input.json \
  --test-only
```

### Custom Parameters

```bash
python execution/orchestrate_lead_scraping.py \
  --industry "Fintech" \
  --input-file input.json \
  --test-size 50 \
  --full-size 2000 \
  --quality-threshold 85.0
```

## Workflow Steps

1. **Test Scrape**: Runs Apify actor with limited results (default: 25 leads)
2. **Quality Validation**: Checks if leads match target industry (threshold: 80%)
3. **Full Scrape**: If validation passes, scrapes full dataset
4. **Export**: Creates Google Sheet with formatted data and returns shareable URL

## Output

- **Google Sheets URL**: Shareable link to spreadsheet
- **Local Files** (in `.tmp/`):
  - `test_run.json` - Test scrape results
  - `test_run_validation.json` - Quality validation report
  - `full_scrape.json` - Full scrape results
  - `sheet_url.txt` - Google Sheets URL

## Architecture

This workflow follows the 3-layer architecture defined in `GEMINI.md`:

- **Directive**: `directives/scrape_leads_by_industry.md` - SOP documentation
- **Orchestration**: You (the AI agent) - Decision making and routing
- **Execution**: Python scripts in `execution/` - Deterministic operations

## Troubleshooting

### Apify Errors

- **Invalid Token**: Check `APIFY_API_TOKEN` in `.env`
- **Actor Not Found**: Verify actor ID is correct
- **Rate Limit**: Wait and retry, or upgrade Apify plan

### Google Sheets Errors

- **Authentication Failed**: Check `credentials.json` exists and is valid
- **Permission Denied**: Share spreadsheet with service account email
- **Quota Exceeded**: Reduce batch size or wait for quota reset

### Quality Validation Fails

- Review test results in `.tmp/test_run.json`
- Adjust search keywords in input file
- Add more specific filters (location, company size, etc.)
- Lower quality threshold (not recommended)

## Example

```bash
# 1. Create input file
cat > my_input.json << EOF
{
  "searchKeywords": "machine learning engineer",
  "locations": ["San Francisco", "New York"],
  "maxResults": 25
}
EOF

# 2. Run workflow
python execution/orchestrate_lead_scraping.py \
  --industry "Artificial Intelligence" \
  --input-file my_input.json \
  --full-size 500

# 3. Check output
cat .tmp/sheet_url.txt
```

## License

MIT
