"""
Run Apify Actor and retrieve results.

This script handles execution of Apify actors and fetches the resulting dataset.
"""

import os
import sys
import json
import time
from apify_client import ApifyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_actor(actor_id, run_input, max_wait_secs=300):
    """
    Run an Apify actor and wait for results.
    
    Args:
        actor_id (str): Apify actor ID
        run_input (dict): Input parameters for the actor
        max_wait_secs (int): Maximum time to wait for completion
        
    Returns:
        list: Dataset items from the actor run
        
    Raises:
        Exception: If actor fails or times out
    """
    api_token = os.getenv('APIFY_API_TOKEN')
    if not api_token:
        raise ValueError("APIFY_API_TOKEN not found in environment variables")
    
    # Initialize the ApifyClient
    client = ApifyClient(api_token)
    
    print(f"Starting actor {actor_id}...")
    print(f"Input: {json.dumps(run_input, indent=2)}")
    
    # Run the actor and wait for it to finish
    run = client.actor(actor_id).call(run_input=run_input, timeout_secs=max_wait_secs)
    
    if not run:
        raise Exception("Actor run failed")
    
    print(f"Actor run completed. Status: {run.get('status')}")
    print(f"Run ID: {run.get('id')}")
    
    # Fetch results from the run's dataset
    dataset_id = run.get('defaultDatasetId')
    if not dataset_id:
        raise Exception("No dataset found in actor run")
    
    print(f"Fetching results from dataset {dataset_id}...")
    items = list(client.dataset(dataset_id).iterate_items())
    
    print(f"Retrieved {len(items)} items")
    
    return items


def save_results(items, output_path):
    """
    Save actor results to a JSON file.
    
    Args:
        items (list): Dataset items
        output_path (str): Path to save the JSON file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) < 3:
        print("Usage: python run_apify_actor.py <actor_id> <input_json_file> [output_file]")
        print("Example: python run_apify_actor.py IoSHqwTR9YGhzccez input.json .tmp/results.json")
        sys.exit(1)
    
    actor_id = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else ".tmp/actor_results.json"
    
    # Load input from file
    with open(input_file, 'r') as f:
        run_input = json.load(f)
    
    # Run actor
    try:
        items = run_actor(actor_id, run_input)
        save_results(items, output_file)
        print(f"\n✓ Successfully scraped {len(items)} leads")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
