"""
Validate lead quality against target industry.

This script checks if scraped leads match the target industry criteria.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)


def validate_leads(leads, target_industry, threshold=80.0):
    """
    Validate leads against target industry.
    
    Args:
        leads (list): List of lead dictionaries
        target_industry (str): Target industry name
        threshold (float): Validation threshold percentage
        
    Returns:
        dict: Validation results with quality score and details
    """
    if not leads:
        return {
            'valid_count': 0,
            'total_count': 0,
            'quality_score': 0.0,
            'passed': False,
            'details': []
        }
    
    valid_count = 0
    details = []
    
    # Industry keywords to check (can be expanded)
    industry_keywords = target_industry.lower().split()
    
    for idx, lead in enumerate(leads):
        # Extract relevant fields for validation (Job Scraper schema)
        # Fields: job_title, company_name, job_description, location
        title = lead.get('job_title', '').lower()
        company_name = lead.get('company_name', '').lower()
        description = lead.get('job_description', '').lower()
        location = lead.get('location', '').lower()
        
        # Combine all text fields for matching
        combined_text = f"{title} {company_name} {description}"
        
        # Check if any industry keyword appears in the combined text
        is_valid = any(keyword in combined_text for keyword in industry_keywords)
        
        if is_valid:
            valid_count += 1
        
        details.append({
            'index': idx,
            'company': lead.get('company_name', 'Unknown'),
            'title': lead.get('job_title', 'Unknown'),
            'valid': is_valid
        })
    
    total_count = len(leads)
    quality_score = (valid_count / total_count) * 100 if total_count > 0 else 0
    passed = quality_score >= threshold
    
    return {
        'valid_count': valid_count,
        'total_count': total_count,
        'quality_score': quality_score,
        'passed': passed,
        'details': details
    }


def print_validation_report(results):
    """Print a formatted validation report."""
    print("\n" + "="*60)
    print("LEAD QUALITY VALIDATION REPORT")
    print("="*60)
    print(f"Total Leads: {results['total_count']}")
    print(f"Valid Leads: {results['valid_count']}")
    print(f"Quality Score: {results['quality_score']:.1f}%")
    print(f"Status: {'✓ PASSED' if results['passed'] else '✗ FAILED'}")
    print("="*60)
    
    if not results['passed']:
        print("\nInvalid Leads:")
        for detail in results['details']:
            if not detail['valid']:
                print(f"  - {detail['company']} (Title: {detail['title']})")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python validate_lead_quality.py <leads_json_file> <target_industry>")
        print("Example: python validate_lead_quality.py .tmp/test_run.json 'Software Development'")
        sys.exit(1)
    
    leads_file = sys.argv[1]
    target_industry = sys.argv[2]
    
    # Load leads from file
    with open(leads_file, 'r') as f:
        leads = json.load(f)
    
    # Validate leads
    results = validate_leads(leads, target_industry)
    
    # Print report
    print_validation_report(results)
    
    # Save results
    output_file = leads_file.replace('.json', '_validation.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Validation results saved to {output_file}")
    
    # Exit with appropriate code
    sys.exit(0 if results['passed'] else 1)
