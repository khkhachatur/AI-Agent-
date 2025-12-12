# Scrape Leads by Industry

## Goal

Scrape industry-specific leads from LinkedIn using Apify, validate data quality through a test run, and export results to Google Sheets.

## Inputs

- **Industry Name**: Target industry for lead scraping (e.g., "Software Development", "Healthcare")
- **Search Filters**: Additional filters like location, company size, job titles
- **Total Lead Count**: Number of leads to scrape in full run (default: 1000)
- **Test Run Size**: Number of leads for quality validation (default: 25)
- **Quality Threshold**: Minimum percentage of valid leads to proceed (default: 80%)

## Tools/Scripts

1. `execution/run_apify_actor.py` - Executes Apify actor and retrieves results
2. `execution/validate_lead_quality.py` - Validates leads against industry criteria
3. `execution/export_to_sheets.py` - Exports data to Google Sheets
4. `execution/orchestrate_lead_scraping.py` - Main orchestration script

## Process

### Step 1: Test Run (25 leads)

1. Call `run_apify_actor.py` with:
   - Actor ID: `IoSHqwTR9YGhzccez`
   - Input parameters: industry filters, limit=25
   - Save results to `.tmp/test_run.json`

2. Call `validate_lead_quality.py` with:
   - Input: `.tmp/test_run.json`
   - Target industry: user-specified industry
   - Output: quality score (percentage of valid leads)

### Step 2: Quality Check

- If quality score >= 80%:
  - Proceed to Step 3 (Full Scrape)
- If quality score < 80%:
  - Log the issue
  - Ask user to adjust filters or confirm retry
  - Return to Step 1 with adjusted parameters

### Step 3: Full Scrape

1. Call `run_apify_actor.py` with:
   - Same parameters as test run
   - Limit: user-specified total count
   - Save results to `.tmp/full_scrape.json`

### Step 4: Export to Google Sheets

1. Call `export_to_sheets.py` with:
   - Input: `.tmp/full_scrape.json`
   - Sheet name: `{Industry} Leads - {Date}`
   - Output: Shareable Google Sheets URL

2. Return URL to user for review

## Outputs

- **Google Sheets URL**: Shareable link to spreadsheet with lead data
- **Quality Report**: Summary of validation results
- **Lead Count**: Total number of leads scraped

## Edge Cases

### Low Quality Results (< 80%)

- **Cause**: Filters too broad, actor returning irrelevant leads
- **Solution**: Prompt user to refine search parameters, retry with adjusted filters
- **Fallback**: Allow user to manually review test results and decide whether to proceed

### API Failures

- **Apify Rate Limits**: Wait and retry with exponential backoff
- **Actor Timeout**: Increase timeout, check actor status
- **Network Errors**: Retry up to 3 times before failing

### Google Sheets Errors

- **Authentication Failed**: Check credentials.json and token.json
- **Quota Exceeded**: Batch writes, implement rate limiting
- **Permission Denied**: Verify service account has proper permissions

### Empty Results

- **Cause**: No leads found matching criteria
- **Solution**: Log warning, suggest broader filters
- **Output**: Empty spreadsheet with headers only

## Timing Expectations

- **Test Run**: 30-60 seconds (25 leads)
- **Quality Validation**: 10-30 seconds (depends on validation method)
- **Full Scrape**: 2-10 minutes (depends on lead count)
- **Export to Sheets**: 10-30 seconds

## API Constraints

- **Apify**: Rate limits vary by plan, typically 100 requests/minute
- **Google Sheets**: 100 requests per 100 seconds per user
- **Actor Costs**: Apify charges based on compute units, monitor usage

## Notes

- All intermediate files stored in `.tmp/` directory
- Credentials stored in `.env` (APIFY_API_TOKEN)
- Google credentials in `credentials.json` (gitignored)
- Results are deliverables (Google Sheets), not local files
