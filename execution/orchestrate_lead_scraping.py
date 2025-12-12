"""
Main orchestration script for lead scraping workflow.

This script coordinates the entire workflow:
1. Run test scrape (25 leads)
2. Validate quality (>80% match)
3. If valid, run full scrape
4. Export to Google Sheets
"""

import os
import sys
import json
import argparse
from datetime import datetime
from run_apify_actor import run_actor, save_results
from validate_lead_quality import validate_leads, print_validation_report
from export_to_sheets import export_leads_to_sheet


def main():
    parser = argparse.ArgumentParser(description='Scrape leads by industry with quality validation')
    parser.add_argument('--industry', required=True, help='Target industry (e.g., "Software Development")')
    parser.add_argument('--actor-id', default='worldunboxer/rapid-linkedin-scraper', help='Apify actor ID')
    parser.add_argument('--input-file', required=True, help='JSON file with actor input parameters')
    parser.add_argument('--test-size', type=int, default=25, help='Number of leads for test run')
    parser.add_argument('--full-size', type=int, default=1000, help='Number of leads for full scrape')
    parser.add_argument('--quality-threshold', type=float, default=80.0, help='Minimum quality percentage')
    parser.add_argument('--spreadsheet-url', help='URL of existing Google Sheet to export to')
    parser.add_argument('--test-only', action='store_true', help='Run test only, skip full scrape')
    parser.add_argument('--skip-validation', action='store_true', help='Skip quality validation')
    
    args = parser.parse_args()
    
    # Load base input parameters
    with open(args.input_file, 'r') as f:
        base_input = json.load(f)
    
    print("\n" + "="*70)
    print("LEAD SCRAPING WORKFLOW")
    print("="*70)
    print(f"Industry: {args.industry}")
    print(f"Actor ID: {args.actor_id}")
    print(f"Test Size: {args.test_size}")
    print(f"Full Size: {args.full_size}")
    print(f"Quality Threshold: {args.quality_threshold}%")
    print("="*70 + "\n")
    
    # STEP 1: Test Run
    print("STEP 1: Running test scrape...")
    print("-" * 70)
    
    test_input = base_input.copy()
    test_input['limit'] = args.test_size
    # Ensure keyword is present if not in input
    if 'keywords' not in test_input and 'searchKeywords' in test_input:
         test_input['keywords'] = test_input.pop('searchKeywords')
    
    test_results_file = '.tmp/test_run.json'
    
    try:
        test_leads = run_actor(args.actor_id, test_input)
        save_results(test_leads, test_results_file)
    except Exception as e:
        print(f"✗ Test run failed: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    # STEP 2: Quality Validation
    if not args.skip_validation:
        print("\nSTEP 2: Validating lead quality...")
        print("-" * 70)
        
        validation_results = validate_leads(test_leads, args.industry, threshold=args.quality_threshold)
        print_validation_report(validation_results)
        
        # Save validation results
        validation_file = '.tmp/test_run_validation.json'
        with open(validation_file, 'w') as f:
            json.dump(validation_results, f, indent=2)
        
        if not validation_results['passed']:
            print(f"\n✗ Quality check failed ({validation_results['quality_score']:.1f}% < {args.quality_threshold}%)")
            print("\nSuggestions:")
            print("  1. Review the test results and adjust your search filters")
            print("  2. Try more specific industry keywords")
            print("  3. Add location or company size filters")
            print(f"\nTest results saved to: {test_results_file}")
            sys.exit(1)
        
        print(f"\n✓ Quality check passed ({validation_results['quality_score']:.1f}% >= {args.quality_threshold}%)")
    
    # Stop here if test-only mode
    if args.test_only:
        print("\n✓ Test run completed successfully (test-only mode)")
        print(f"Results saved to: {test_results_file}")
        sys.exit(0)
    
    # STEP 3: Full Scrape
    print("\nSTEP 3: Running full scrape...")
    print("-" * 70)
    
    full_input = base_input.copy()
    full_input['limit'] = args.full_size
     # Ensure keyword is present if not in input
    if 'keywords' not in full_input and 'searchKeywords' in full_input:
         full_input['keywords'] = full_input.pop('searchKeywords')
    
    full_results_file = '.tmp/full_scrape.json'
    
    try:
        full_leads = run_actor(args.actor_id, full_input)
        save_results(full_leads, full_results_file)
    except Exception as e:
        print(f"✗ Full scrape failed: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    # STEP 4: Export to Google Sheets
    print("\nSTEP 4: Exporting to Google Sheets...")
    print("-" * 70)
    
    timestamp = datetime.now().strftime("%Y-%m-%d")
    sheet_name = f"{args.industry} Leads - {timestamp}"
    
    try:
        sheet_url = export_leads_to_sheet(full_leads, sheet_name, existing_spreadsheet_url=args.spreadsheet_url)
        
        # Save URL
        url_file = '.tmp/sheet_url.txt'
        with open(url_file, 'w') as f:
            f.write(sheet_url)
        
        print("\n" + "="*70)
        print("WORKFLOW COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"Total Leads Scraped: {len(full_leads)}")
        print(f"Google Sheets URL: {sheet_url}")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"✗ Export to Google Sheets failed: {str(e)}", file=sys.stderr)
        print(f"Leads saved locally to: {full_results_file}")
        sys.exit(1)


if __name__ == "__main__":
    main()
