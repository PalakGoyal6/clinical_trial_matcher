"""
Day 3: Process and clean trial data from ClinicalTrials.gov
Extracts structured information from raw trial JSON
"""

import json
import pandas as pd
import re

def extract_age_range(criteria_text):
    """Extract age range from eligibility criteria text"""
    
    # Common patterns for age ranges
    patterns = [
        r'(\d+)\s*(?:to|-|through)\s*(\d+)\s*(?:years|yrs)',
        r'age[s]?\s*(\d+)\s*(?:to|-)\s*(\d+)',
        r'between\s*(\d+)\s*and\s*(\d+)\s*years',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, criteria_text.lower())
        if match:
            return int(match.group(1)), int(match.group(2))
    
    # Check for minimum age only
    min_age_match = re.search(r'(?:minimum|at least)\s*(\d+)\s*years', criteria_text.lower())
    if min_age_match:
        return int(min_age_match.group(1)), 100
    
    # Check for maximum age only  
    max_age_match = re.search(r'(?:maximum|up to)\s*(\d+)\s*years', criteria_text.lower())
    if max_age_match:
        return 18, int(max_age_match.group(1))
    
    # Default
    return 18, 100

def extract_trial_info(trial):
    """Extract structured information from a single trial"""
    
    try:
        protocol = trial.get("protocolSection", {})
        
        # Identification
        identification = protocol.get("identificationModule", {})
        nct_id = identification.get("nctId", "")
        title = identification.get("briefTitle", "")
        
        # Status
        status_module = protocol.get("statusModule", {})
        status = status_module.get("overallStatus", "")
        
        # Conditions
        conditions_module = protocol.get("conditionsModule", {})
        conditions = conditions_module.get("conditions", [])
        condition = conditions[0] if conditions else ""
        
        # Eligibility
        eligibility = protocol.get("eligibilityModule", {})
        criteria_text = eligibility.get("eligibilityCriteria", "")
        gender = eligibility.get("sex", "ALL")
        
        # Extract age range
        age_min, age_max = extract_age_range(criteria_text)
        
        return {
            "nct_id": nct_id,
            "title": title,
            "condition": condition,
            "eligibility_text": criteria_text[:1000],  # Truncate for storage
            "age_min": age_min,
            "age_max": age_max,
            "gender": gender,
            "status": status
        }
    
    except Exception as e:
        print(f"Error processing trial: {e}")
        return None

def process_trials(input_file="trials_raw.json"):
    """Process all trials from raw JSON file"""
    
    print(f"Loading trials from {input_file}...")
    
    with open(input_file, 'r') as f:
        trials_raw = json.load(f)
    
    print(f"Processing {len(trials_raw)} trials...")
    
    trials_data = []
    for i, trial in enumerate(trials_raw):
        trial_info = extract_trial_info(trial)
        if trial_info:
            trials_data.append(trial_info)
        
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1} trials...")
    
    # Convert to DataFrame
    df = pd.DataFrame(trials_data)
    
    # Filter only recruiting trials
    df = df[df["status"].isin(["RECRUITING", "NOT_YET_RECRUITING", "ENROLLING_BY_INVITATION"])]
    
    # Remove trials with missing key fields
    df = df.dropna(subset=["nct_id", "title", "eligibility_text"])
    df = df[df["eligibility_text"].str.len() > 50]  # Must have substantial criteria
    
    # Save to CSV
    output_file = "trials_clean.csv"
    df.to_csv(output_file, index=False)
    
    print(f"\n✅ Processed {len(df)} recruiting trials")
    print(f"📁 Saved to: {output_file}")
    
    # Print statistics
    print("\n" + "="*60)
    print("TRIAL STATISTICS:")
    print("="*60)
    print(f"Age ranges: {df['age_min'].min()}-{df['age_max'].max()} years")
    print(f"Gender distribution: {df['gender'].value_counts().to_dict()}")
    print(f"Status distribution: {df['status'].value_counts().to_dict()}")
    
    # Sample trial
    print("\n" + "="*60)
    print("SAMPLE TRIAL:")
    print("="*60)
    sample = df.iloc[0]
    print(f"NCT ID: {sample['nct_id']}")
    print(f"Title: {sample['title']}")
    print(f"Condition: {sample['condition']}")
    print(f"Age: {sample['age_min']}-{sample['age_max']}")
    print(f"Gender: {sample['gender']}")
    print(f"Eligibility (excerpt): {sample['eligibility_text'][:200]}...")
    
    return df

if __name__ == "__main__":
    trials_df = process_trials()
