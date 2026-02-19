"""
Day 5-6: Core matching algorithm
Matches patients to clinical trials based on eligibility criteria
"""

import pandas as pd
import ast
from difflib import SequenceMatcher
from tqdm import tqdm
import json

def safe_eval_list(value):
    """Safely evaluate string representation of list"""
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            return ast.literal_eval(value)
        except:
            return []
    return []

def calculate_match_score(patient, trial):
    """
    Calculate match score between patient and trial
    
    Returns:
        score: Integer 0-100
        reasons: List of strings explaining the match
    """
    score = 0
    reasons = []
    
    # 1. AGE MATCH (20 points)
    patient_age = int(patient["age"])
    trial_age_min = int(trial["age_min"])
    trial_age_max = int(trial["age_max"])
    
    if trial_age_min <= patient_age <= trial_age_max:
        score += 20
        reasons.append(f"✓ Age {patient_age} within range ({trial_age_min}-{trial_age_max})")
    else:
        reasons.append(f"✗ Age {patient_age} outside range ({trial_age_min}-{trial_age_max})")
    
    # 2. GENDER MATCH (10 points)
    patient_gender = str(patient["gender"]).upper()
    trial_gender = str(trial["gender"]).upper()
    
    if trial_gender == "ALL" or trial_gender == patient_gender:
        score += 10
        reasons.append(f"✓ Gender matches ({trial_gender})")
    else:
        reasons.append(f"✗ Gender mismatch (requires {trial_gender})")
    
    # 3. CONDITION KEYWORD OVERLAP (50 points max)
    patient_keywords = set(safe_eval_list(patient["condition_keywords"]))
    trial_keywords = set(safe_eval_list(trial["keywords"]))
    
    if patient_keywords and trial_keywords:
        overlap = patient_keywords.intersection(trial_keywords)
        # 10 points per matching keyword, max 50
        keyword_score = min(len(overlap) * 10, 50)
        score += keyword_score
        
        if keyword_score > 0:
            overlap_sample = list(overlap)[:3]  # Show up to 3 examples
            reasons.append(f"✓ {len(overlap)} matching keywords: {', '.join(overlap_sample)}")
    
    # 4. PRIMARY CONDITION SIMILARITY (20 points)
    patient_conditions = safe_eval_list(patient["conditions"])
    trial_condition = str(trial["condition"]).lower()
    
    if patient_conditions and trial_condition:
        # Check primary condition (first in list)
        primary_condition = patient_conditions[0].lower()
        
        # Calculate string similarity
        similarity = SequenceMatcher(None, primary_condition, trial_condition).ratio()
        condition_score = int(similarity * 20)
        score += condition_score
        
        if condition_score > 5:
            reasons.append(f"✓ Primary condition '{primary_condition[:30]}...' similar to trial condition")
    
    return score, reasons

def match_patient_to_trials(patient, trials_df, top_k=10, min_score=20):
    """
    Match a single patient to all trials
    
    Args:
        patient: Patient row (pandas Series)
        trials_df: DataFrame of all trials
        top_k: Number of top matches to return
        min_score: Minimum score threshold
    
    Returns:
        List of match dictionaries
    """
    matches = []
    
    for _, trial in trials_df.iterrows():
        score, reasons = calculate_match_score(patient, trial)
        
        # Only keep matches above threshold
        if score >= min_score:
            matches.append({
                "nct_id": trial["nct_id"],
                "title": trial["title"],
                "condition": trial["condition"],
                "score": score,
                "reasons": reasons
            })
    
    # Sort by score (descending) and return top K
    matches = sorted(matches, key=lambda x: x["score"], reverse=True)
    return matches[:top_k]

def match_all_patients(patients_df, trials_df):
    """
    Match all patients to all trials
    
    Returns:
        Dictionary mapping patient_id -> list of matches
    """
    print(f"Matching {len(patients_df)} patients to {len(trials_df)} trials...")
    
    all_matches = {}
    
    for _, patient in tqdm(patients_df.iterrows(), total=len(patients_df), desc="Matching"):
        patient_id = patient["id"]
        matches = match_patient_to_trials(patient, trials_df)
        all_matches[patient_id] = matches
    
    return all_matches

def save_matches(matches, output_file="matches.json"):
    """Save matches to JSON file"""
    with open(output_file, "w") as f:
        json.dump(matches, f, indent=2)
    print(f"✅ Saved matches to {output_file}")

def load_matches(input_file="matches.json"):
    """Load matches from JSON file"""
    with open(input_file, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    print("="*60)
    print("MATCHING PATIENTS TO TRIALS")
    print("="*60)
    
    # Load data
    print("\nLoading data...")
    patients_df = pd.read_csv("patients.csv")
    trials_df = pd.read_csv("trials_clean.csv")
    
    print(f"Patients: {len(patients_df)}")
    print(f"Trials: {len(trials_df)}")
    
    # Match all patients
    all_matches = match_all_patients(patients_df, trials_df)
    
    # Save results
    save_matches(all_matches)
    
    # Print statistics
    print("\n" + "="*60)
    print("MATCHING STATISTICS:")
    print("="*60)
    
    total_matches = sum(len(matches) for matches in all_matches.values())
    patients_with_matches = sum(1 for matches in all_matches.values() if len(matches) > 0)
    avg_matches = total_matches / len(all_matches) if all_matches else 0
    
    print(f"Total matches: {total_matches}")
    print(f"Patients with ≥1 match: {patients_with_matches}/{len(all_matches)}")
    print(f"Average matches per patient: {avg_matches:.1f}")
    
    # Show sample match
    print("\n" + "="*60)
    print("SAMPLE MATCH:")
    print("="*60)
    
    sample_patient_id = list(all_matches.keys())[0]
    sample_patient = patients_df[patients_df["id"] == sample_patient_id].iloc[0]
    sample_matches = all_matches[sample_patient_id]
    
    print(f"\nPatient: {sample_patient['id']}")
    print(f"Age: {sample_patient['age']}, Gender: {sample_patient['gender']}")
    print(f"Conditions: {sample_patient['conditions']}")
    
    if sample_matches:
        print(f"\nTop Match (Score: {sample_matches[0]['score']}/100):")
        print(f"Trial: {sample_matches[0]['title']}")
        print("Reasons:")
        for reason in sample_matches[0]['reasons']:
            print(f"  {reason}")
    else:
        print("\nNo matches found for this patient")
