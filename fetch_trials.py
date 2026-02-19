"""
Day 1: Fetch clinical trials from ClinicalTrials.gov API
Run this first to get trial data
"""

import requests
import json
import time

def fetch_trials(condition="diabetes", max_studies=2000):
    """
    Fetch trials from ClinicalTrials.gov API v2
    
    Args:
        condition: Disease/condition to search for
        max_studies: Maximum number of trials to fetch
    
    Returns:
        List of trial dictionaries
    """
    print(f"Fetching trials for condition: {condition}")
    
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    all_trials = []
    page_size = 100
    next_page_token = None
    page = 0
    
    while len(all_trials) < max_studies:
        page += 1
        print(f"Fetching page {page}...")
        
        params = {
            "query.cond": condition,
            "pageSize": page_size,
            "format": "json"
        }
        
        # Add page token if we have one from previous response
        if next_page_token:
            params["pageToken"] = next_page_token
        
        try:
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            studies = data.get("studies", [])
            all_trials.extend(studies)
            
            print(f"  Retrieved {len(studies)} trials (total: {len(all_trials)})")
            
            # Get next page token from response
            next_page_token = data.get("nextPageToken")
            
            # Stop if no more pages or no studies returned
            if not next_page_token or len(studies) == 0:
                print("  No more pages available")
                break
                
            # Stop if we have enough
            if len(all_trials) >= max_studies:
                all_trials = all_trials[:max_studies]
                break
                
            # Be nice to the API
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break
    
    # Save raw data
    output_file = "trials_raw.json"
    with open(output_file, "w") as f:
        json.dump(all_trials, f, indent=2)
    
    print(f"\n✅ Successfully fetched {len(all_trials)} trials")
    print(f"📁 Saved to: {output_file}")
    
    return all_trials

if __name__ == "__main__":
    # Fetch trials for diabetes (you can change this)
    trials = fetch_trials(condition="diabetes", max_studies=2000)
    
    # Print sample trial
    if trials:
        print("\n" + "="*60)
        print("SAMPLE TRIAL:")
        print("="*60)
        sample = trials[0]
        protocol = sample.get("protocolSection", {})
        identification = protocol.get("identificationModule", {})
        print(f"Title: {identification.get('briefTitle', 'N/A')}")
        print(f"NCT ID: {identification.get('nctId', 'N/A')}")