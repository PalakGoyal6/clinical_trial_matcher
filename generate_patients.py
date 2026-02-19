"""
Day 2: Generate synthetic patient data
Alternative to Synthea - generates simple synthetic patients directly in Python
"""

import pandas as pd
import numpy as np
import random
import json

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Medical conditions (focused on diabetes-related for matching)
CONDITIONS = [
    "Type 2 Diabetes Mellitus",
    "Type 1 Diabetes Mellitus",
    "Prediabetes",
    "Diabetic Neuropathy",
    "Diabetic Retinopathy",
    "Hypertension",
    "Hyperlipidemia",
    "Obesity",
    "Coronary Artery Disease",
    "Chronic Kidney Disease",
    "Metabolic Syndrome",
    "Hypothyroidism",
    "Depression",
    "Asthma",
    "Osteoarthritis"
]

# Common diabetes medications
MEDICATIONS = [
    "Metformin",
    "Insulin Glargine",
    "Insulin Lispro",
    "Glipizide",
    "Sitagliptin",
    "Empagliflozin",
    "Lisinopril",
    "Atorvastatin",
    "Aspirin",
    "Losartan",
    "Amlodipine",
    "Levothyroxine"
]

def generate_patient(patient_id):
    """Generate a single synthetic patient"""
    
    # Basic demographics
    age = np.random.randint(25, 85)
    gender = random.choice(["male", "female"])
    
    # Generate conditions (1-5 per patient)
    num_conditions = np.random.randint(1, 6)
    # Most patients should have diabetes
    if random.random() < 0.8:  # 80% have diabetes
        patient_conditions = [random.choice([
            "Type 2 Diabetes Mellitus",
            "Type 1 Diabetes Mellitus",
            "Prediabetes"
        ])]
        # Add additional conditions
        other_conditions = random.sample(
            [c for c in CONDITIONS if c not in patient_conditions],
            num_conditions - 1
        )
        patient_conditions.extend(other_conditions)
    else:
        patient_conditions = random.sample(CONDITIONS, num_conditions)
    
    # Generate medications (2-6 per patient)
    num_meds = np.random.randint(2, 7)
    patient_meds = random.sample(MEDICATIONS, num_meds)
    
    return {
        "id": f"patient_{patient_id:04d}",
        "age": age,
        "gender": gender,
        "conditions": patient_conditions,
        "medications": patient_meds
    }

def generate_patients(num_patients=200):
    """Generate multiple synthetic patients"""
    
    print(f"Generating {num_patients} synthetic patients...")
    
    patients = []
    for i in range(num_patients):
        patient = generate_patient(i + 1)
        patients.append(patient)
        
        if (i + 1) % 50 == 0:
            print(f"  Generated {i + 1} patients...")
    
    # Convert to DataFrame
    df = pd.DataFrame(patients)
    
    # Save to CSV
    output_file = "patients.csv"
    df.to_csv(output_file, index=False)
    
    print(f"\n✅ Generated {len(df)} patients")
    print(f"📁 Saved to: {output_file}")
    
    # Print statistics
    print("\n" + "="*60)
    print("PATIENT STATISTICS:")
    print("="*60)
    print(f"Age range: {df['age'].min()} - {df['age'].max()} years")
    print(f"Gender distribution: {df['gender'].value_counts().to_dict()}")
    print(f"Average conditions per patient: {df['conditions'].apply(len).mean():.1f}")
    print(f"Average medications per patient: {df['medications'].apply(len).mean():.1f}")
    
    # Sample patient
    print("\n" + "="*60)
    print("SAMPLE PATIENT:")
    print("="*60)
    sample = df.iloc[0]
    print(f"ID: {sample['id']}")
    print(f"Age: {sample['age']}, Gender: {sample['gender']}")
    print(f"Conditions: {', '.join(sample['conditions'][:3])}...")
    print(f"Medications: {', '.join(sample['medications'][:3])}...")
    
    return df

if __name__ == "__main__":
    patients_df = generate_patients(200)
