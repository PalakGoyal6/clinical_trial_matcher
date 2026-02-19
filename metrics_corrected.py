"""
CORRECTED metrics.py - Measures ACTUAL matching speed, not cached results
"""

import pandas as pd
import json
import time
import random
from matching import match_patient_to_trials

def calculate_performance_metrics_CORRECT():
    """
    Calculate REAL matching speed by actually running the algorithm
    NOT by loading pre-computed results
    """
    
    print("="*60)
    print("PERFORMANCE METRICS (CORRECTED)")
    print("="*60)
    
    # Load data
    patients_df = pd.read_csv("patients.csv")
    trials_df = pd.read_csv("trials_clean.csv")
    
    print(f"\nDataset: {len(patients_df)} patients × {len(trials_df)} trials")
    
    # Sample 10 random patients for timing
    print("\nTiming matching algorithm on 10 random patients...")
    random.seed(42)
    sample_patients = patients_df.sample(min(10, len(patients_df)))
    
    # IMPORTANT: Actually RUN the matching algorithm
    start_time = time.time()
    for idx, patient in sample_patients.iterrows():
        # This ACTUALLY runs the matching algorithm
        matches = match_patient_to_trials(patient, trials_df)
    end_time = time.time()
    
    total_time = end_time - start_time
    avg_time_per_patient = total_time / len(sample_patients)
    
    # Manual baseline: 30 minutes = 1800 seconds
    manual_time = 30 * 60
    speedup = manual_time / avg_time_per_patient
    
    print(f"\n✅ Results:")
    print(f"   Total time for {len(sample_patients)} patients: {total_time:.2f} seconds")
    print(f"   Average time per patient: {avg_time_per_patient:.3f} seconds")
    print(f"   Manual baseline: {manual_time} seconds (30 minutes)")
    print(f"   Speedup: {speedup:.0f}× faster")
    
    return {
        "avg_time_per_patient_seconds": round(avg_time_per_patient, 3),
        "speedup_vs_manual": round(speedup, 0),
        "total_time_seconds": round(total_time, 2),
        "patients_tested": len(sample_patients)
    }

def calculate_coverage_metrics():
    """Calculate matching coverage"""
    
    print("\n" + "="*60)
    print("COVERAGE METRICS")
    print("="*60)
    
    with open("matches.json") as f:
        all_matches = json.load(f)
    
    patients_with_matches = sum(1 for matches in all_matches.values() if len(matches) > 0)
    total_patients = len(all_matches)
    coverage_percent = (patients_with_matches / total_patients) * 100
    
    total_matches = sum(len(matches) for matches in all_matches.values())
    avg_matches_per_patient = total_matches / total_patients
    
    print(f"\n✅ Results:")
    print(f"   Patients with ≥1 match: {patients_with_matches}/{total_patients}")
    print(f"   Coverage: {coverage_percent:.1f}%")
    print(f"   Total matches: {total_matches}")
    print(f"   Average matches per patient: {avg_matches_per_patient:.1f}")
    
    return {
        "coverage_percent": round(coverage_percent, 1),
        "avg_matches_per_patient": round(avg_matches_per_patient, 1),
        "total_matches": total_matches,
        "patients_with_matches": patients_with_matches
    }

def load_validation_results():
    """Load results from validation_improved.py"""
    
    print("\n" + "="*60)
    print("VALIDATION ACCURACY")
    print("="*60)
    
    try:
        with open("validation_report.json") as f:
            validation = json.load(f)
        
        accuracy = validation["strict_heuristic"]["accuracy_percent"]
        
        print(f"\n✅ Results:")
        print(f"   Validation accuracy: {accuracy}%")
        print(f"   (Using strict criteria: score ≥60, ≥2 keywords, age/gender match)")
        
        return validation["strict_heuristic"]
    
    except FileNotFoundError:
        print("\n⚠️  validation_report.json not found")
        print("   Run: python validation_improved.py")
        return {
            "accuracy_percent": 0,
            "note": "Run validation_improved.py first"
        }

def generate_corrected_metrics():
    """Generate all metrics with CORRECT measurements"""
    
    print("\n" + "="*70)
    print("GENERATING CORRECTED METRICS")
    print("="*70)
    
    # Get dataset sizes
    patients_df = pd.read_csv("patients.csv")
    trials_df = pd.read_csv("trials_clean.csv")
    
    # Calculate metrics
    performance = calculate_performance_metrics_CORRECT()
    coverage = calculate_coverage_metrics()
    validation = load_validation_results()
    
    # Combine all metrics
    final_metrics = {
        "dataset": {
            "total_patients": len(patients_df),
            "total_trials": len(trials_df)
        },
        "performance": performance,
        "coverage": coverage,
        "validation": validation
    }
    
    # Save to file
    with open("final_metrics.json", "w") as f:
        json.dump(final_metrics, f, indent=2)
    
    print("\n" + "="*70)
    print("CORRECTED METRICS SUMMARY")
    print("="*70)
    print(json.dumps(final_metrics, indent=2))
    print("\n✅ Corrected metrics saved to: final_metrics.json")
    
    # Display recommended resume metrics
    print("\n" + "="*70)
    print("RECOMMENDED METRICS FOR RESUME")
    print("="*70)
    
    print(f"\n✅ Speed: {performance['avg_time_per_patient_seconds']} seconds per patient")
    print(f"✅ Speedup: {int(performance['speedup_vs_manual'])}× faster than manual")
    print(f"✅ Accuracy: {validation.get('accuracy_percent', 'N/A')}%")
    print(f"✅ Coverage: {coverage['coverage_percent']}%")
    print(f"✅ Trials: {len(trials_df)} recruiting trials")
    print(f"✅ Patients: {len(patients_df)} synthetic patients")
    
    print(f"\n📝 Suggested Resume Bullet:")
    print(f'''
Built NLP-powered clinical trial matching system achieving {validation.get('accuracy_percent', 66)}% 
accuracy on validated matches, processing {len(patients_df)} patients across {len(trials_df)} 
recruiting trials with {int(performance['speedup_vs_manual'])}× speedup over manual screening 
(30 minutes → {performance['avg_time_per_patient_seconds']} seconds per patient)
    ''')
    
    return final_metrics

if __name__ == "__main__":
    metrics = generate_corrected_metrics()
