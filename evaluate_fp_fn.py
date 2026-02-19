"""
Comprehensive Evaluation with False Positive/Negative Analysis
Measures precision, recall, F1-score, and confusion matrix
"""

import pandas as pd
import json
import random
from matching import calculate_match_score
import ast

def safe_eval_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            return ast.literal_eval(value)
        except:
            return []
    return []

def is_valid_match(patient, trial, score, strict=True):
    """
    Ground truth validator - determines if a match is truly valid
    
    A match is valid if:
    1. Age is within range
    2. Gender matches (or trial accepts all)
    3. Score is above threshold
    4. (Strict mode) At least 2 keyword matches
    """
    # Age check
    age_valid = trial["age_min"] <= patient["age"] <= trial["age_max"]
    
    # Gender check
    gender_valid = (trial["gender"] == "ALL" or 
                   trial["gender"].upper() == patient["gender"].upper())
    
    # Score check
    score_valid = score >= (60 if strict else 50)
    
    # Keyword check (strict mode only)
    if strict:
        patient_keywords = set(safe_eval_list(patient.get("condition_keywords", [])))
        trial_keywords = set(safe_eval_list(trial.get("keywords", [])))
        keyword_overlap = patient_keywords.intersection(trial_keywords)
        keyword_valid = len(keyword_overlap) >= 2
    else:
        keyword_valid = True
    
    return age_valid and gender_valid and score_valid and keyword_valid

def evaluate_matches_with_fp_fn(threshold=40, num_patients=50, strict_validation=True):
    """
    Evaluate matching system with false positive/negative analysis
    
    Args:
        threshold: Score threshold for considering a match (default: 40)
        num_patients: Number of patients to evaluate (default: 50)
        strict_validation: Use strict validation criteria (default: True)
    """
    
    print("="*70)
    print("FALSE POSITIVE / FALSE NEGATIVE ANALYSIS")
    print("="*70)
    print(f"\nSettings:")
    print(f"  Match threshold: {threshold}")
    print(f"  Validation mode: {'Strict (≥60 score, ≥2 keywords)' if strict_validation else 'Lenient (≥50 score)'}")
    print(f"  Sample size: {num_patients} patients")
    
    # Load data
    patients_df = pd.read_csv("patients.csv")
    trials_df = pd.read_csv("trials_clean.csv")
    with open("matches.json") as f:
        all_matches = json.load(f)
    
    # Sample patients
    random.seed(42)
    sample_patient_ids = random.sample(
        list(all_matches.keys()),
        min(num_patients, len(all_matches))
    )
    
    # Initialize counters
    true_positives = 0   # System said match, actually valid
    false_positives = 0  # System said match, actually invalid
    true_negatives = 0   # System said no match, actually invalid
    false_negatives = 0  # System said no match, actually valid
    
    # Store examples for later analysis
    fp_examples = []
    fn_examples = []
    
    print(f"\n{'='*70}")
    print("Evaluating matches...")
    print(f"{'='*70}\n")
    
    for patient_id in sample_patient_ids:
        patient = patients_df[patients_df["id"] == patient_id].iloc[0]
        matches = all_matches[patient_id]
        
        # Get all trials above threshold (what system recommended)
        recommended_trials = {m["nct_id"]: m["score"] for m in matches if m["score"] >= threshold}
        
        # Sample some trials NOT recommended (for true/false negatives)
        all_trial_ids = set(trials_df["nct_id"].tolist())
        recommended_ids = set(recommended_trials.keys())
        not_recommended_ids = all_trial_ids - recommended_ids
        
        # Sample 10 not-recommended trials
        sample_not_recommended = random.sample(
            list(not_recommended_ids),
            min(10, len(not_recommended_ids))
        )
        
        # Evaluate RECOMMENDED trials (checking for false positives)
        for nct_id, score in recommended_trials.items():
            trial = trials_df[trials_df["nct_id"] == nct_id].iloc[0]
            
            is_valid = is_valid_match(patient, trial, score, strict=strict_validation)
            
            if is_valid:
                true_positives += 1
            else:
                false_positives += 1
                # Store example
                fp_examples.append({
                    "patient_id": patient_id,
                    "patient_age": patient["age"],
                    "patient_gender": patient["gender"],
                    "trial_nct": nct_id,
                    "trial_age_range": f"{trial['age_min']}-{trial['age_max']}",
                    "trial_gender": trial["gender"],
                    "score": score,
                    "reason": get_fp_reason(patient, trial, score, strict_validation)
                })
        
        # Evaluate NOT-RECOMMENDED trials (checking for false negatives)
        for nct_id in sample_not_recommended:
            trial = trials_df[trials_df["nct_id"] == nct_id].iloc[0]
            score, _ = calculate_match_score(patient, trial)
            
            is_valid = is_valid_match(patient, trial, score, strict=strict_validation)
            
            if is_valid:
                # System missed a valid match!
                false_negatives += 1
                fn_examples.append({
                    "patient_id": patient_id,
                    "trial_nct": nct_id,
                    "score": score,
                    "reason": f"Score {score} below threshold {threshold}"
                })
            else:
                true_negatives += 1
    
    # Calculate metrics
    total = true_positives + false_positives + true_negatives + false_negatives
    
    # Precision = TP / (TP + FP) - "Of all recommended matches, how many are valid?"
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    
    # Recall = TP / (TP + FN) - "Of all valid matches, how many did we find?"
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    
    # F1 Score = harmonic mean of precision and recall
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    # Accuracy = (TP + TN) / Total
    accuracy = (true_positives + true_negatives) / total if total > 0 else 0
    
    # False Positive Rate = FP / (FP + TN)
    fpr = false_positives / (false_positives + true_negatives) if (false_positives + true_negatives) > 0 else 0
    
    # False Negative Rate = FN / (FN + TP)
    fnr = false_negatives / (false_negatives + true_positives) if (false_negatives + true_positives) > 0 else 0
    
    # Print results
    print("="*70)
    print("CONFUSION MATRIX")
    print("="*70)
    print(f"""
                    Actually Valid    Actually Invalid
    Predicted Valid      {true_positives:4d}             {false_positives:4d}
    Predicted Invalid    {false_negatives:4d}             {true_negatives:4d}
    """)
    
    print("="*70)
    print("CLASSIFICATION METRICS")
    print("="*70)
    print(f"\n📊 Primary Metrics:")
    print(f"   Precision:  {precision*100:5.1f}%  (Of recommended matches, {precision*100:.1f}% are valid)")
    print(f"   Recall:     {recall*100:5.1f}%  (Found {recall*100:.1f}% of all valid matches)")
    print(f"   F1-Score:   {f1_score*100:5.1f}%  (Balance of precision & recall)")
    print(f"   Accuracy:   {accuracy*100:5.1f}%  (Overall correct predictions)")
    
    print(f"\n❌ Error Rates:")
    print(f"   False Positive Rate: {fpr*100:5.1f}%  ({false_positives} bad recommendations)")
    print(f"   False Negative Rate: {fnr*100:5.1f}%  ({false_negatives} missed opportunities)")
    
    print(f"\n🔢 Raw Counts:")
    print(f"   True Positives:  {true_positives:4d}  ✅ Correct recommendations")
    print(f"   False Positives: {false_positives:4d}  ❌ Bad recommendations")
    print(f"   True Negatives:  {true_negatives:4d}  ✅ Correctly rejected")
    print(f"   False Negatives: {false_negatives:4d}  ❌ Missed opportunities")
    print(f"   Total Evaluated: {total:4d}")
    
    # Show examples
    if fp_examples:
        print(f"\n{'='*70}")
        print(f"FALSE POSITIVE EXAMPLES (showing first 5)")
        print(f"{'='*70}")
        for i, ex in enumerate(fp_examples[:5], 1):
            print(f"\n{i}. Patient: {ex['patient_id']} (Age: {ex['patient_age']}, Gender: {ex['patient_gender']})")
            print(f"   Trial: {ex['trial_nct']} (Age: {ex['trial_age_range']}, Gender: {ex['trial_gender']})")
            print(f"   Score: {ex['score']}/100")
            print(f"   Why invalid: {ex['reason']}")
    
    if fn_examples:
        print(f"\n{'='*70}")
        print(f"FALSE NEGATIVE EXAMPLES (showing first 5)")
        print(f"{'='*70}")
        for i, ex in enumerate(fn_examples[:5], 1):
            print(f"\n{i}. Patient: {ex['patient_id']}")
            print(f"   Trial: {ex['trial_nct']}")
            print(f"   Score: {ex['score']}/100")
            print(f"   Why missed: {ex['reason']}")
    
    # Save results
    results = {
        "settings": {
            "threshold": threshold,
            "strict_validation": strict_validation,
            "sample_size": num_patients
        },
        "confusion_matrix": {
            "true_positives": true_positives,
            "false_positives": false_positives,
            "true_negatives": true_negatives,
            "false_negatives": false_negatives
        },
        "metrics": {
            "precision": round(precision * 100, 2),
            "recall": round(recall * 100, 2),
            "f1_score": round(f1_score * 100, 2),
            "accuracy": round(accuracy * 100, 2),
            "false_positive_rate": round(fpr * 100, 2),
            "false_negative_rate": round(fnr * 100, 2)
        },
        "interpretation": {
            "precision_meaning": f"{precision*100:.1f}% of recommendations are valid",
            "recall_meaning": f"Found {recall*100:.1f}% of all valid matches",
            "fp_meaning": f"{false_positives} bad recommendations out of {true_positives + false_positives}",
            "fn_meaning": f"Missed {false_negatives} valid trials"
        }
    }
    
    with open("fp_fn_analysis.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*70}")
    print("INTERPRETATION & RECOMMENDATIONS")
    print(f"{'='*70}")
    
    if precision < 0.7:
        print(f"\n⚠️  Low Precision ({precision*100:.1f}%)")
        print(f"   Problem: Too many false positives - {fpr*100:.1f}% of recommendations are invalid")
        print(f"   Fix: Increase threshold from {threshold} to {threshold + 10} or add stricter criteria")
    else:
        print(f"\n✅ Good Precision ({precision*100:.1f}%)")
        print(f"   {precision*100:.1f}% of your recommendations are valid")
    
    if recall < 0.7:
        print(f"\n⚠️  Low Recall ({recall*100:.1f}%)")
        print(f"   Problem: Missing {fnr*100:.1f}% of valid matches")
        print(f"   Fix: Lower threshold from {threshold} to {threshold - 10} or relax criteria")
    else:
        print(f"\n✅ Good Recall ({recall*100:.1f}%)")
        print(f"   Finding {recall*100:.1f}% of all valid matches")
    
    print(f"\n💡 Trade-off:")
    print(f"   Higher threshold → Better precision, worse recall (fewer false positives, more false negatives)")
    print(f"   Lower threshold → Worse precision, better recall (more false positives, fewer false negatives)")
    
    print(f"\n📁 Results saved to: fp_fn_analysis.json")
    
    return results

def get_fp_reason(patient, trial, score, strict):
    """Determine why a match is a false positive"""
    reasons = []
    
    if not (trial["age_min"] <= patient["age"] <= trial["age_max"]):
        reasons.append(f"Age mismatch")
    
    if trial["gender"] != "ALL" and trial["gender"].upper() != patient["gender"].upper():
        reasons.append(f"Gender mismatch")
    
    if strict and score < 60:
        reasons.append(f"Score {score} below strict threshold (60)")
    elif not strict and score < 50:
        reasons.append(f"Score {score} below lenient threshold (50)")
    
    if strict:
        patient_keywords = set(safe_eval_list(patient.get("condition_keywords", [])))
        trial_keywords = set(safe_eval_list(trial.get("keywords", [])))
        overlap = patient_keywords.intersection(trial_keywords)
        if len(overlap) < 2:
            reasons.append(f"Only {len(overlap)} keyword match(es)")
    
    return "; ".join(reasons) if reasons else "Unknown"

def compare_thresholds():
    """Compare false positive rates across different thresholds"""
    print("\n" + "="*70)
    print("THRESHOLD COMPARISON - FALSE POSITIVE ANALYSIS")
    print("="*70)
    
    thresholds = [30, 40, 50, 60, 70]
    
    print(f"\n{'Threshold':<12} {'Precision':<12} {'FP Rate':<12} {'FP Count':<12}")
    print("-" * 48)
    
    for threshold in thresholds:
        results = evaluate_matches_with_fp_fn(
            threshold=threshold,
            num_patients=20,  # Smaller sample for speed
            strict_validation=False
        )
        
        precision = results['metrics']['precision']
        fp_rate = results['metrics']['false_positive_rate']
        fp_count = results['confusion_matrix']['false_positives']
        
        print(f"{threshold:<12} {precision:<11.1f}% {fp_rate:<11.1f}% {fp_count:<12}")

if __name__ == "__main__":
    # Run main analysis
    results = evaluate_matches_with_fp_fn(
        threshold=40,
        num_patients=50,
        strict_validation=True
    )
    
    # Compare thresholds
    # Uncomment to run:
    # compare_thresholds()
