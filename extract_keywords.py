"""
Day 4: Extract medical keywords using NLP
Run after installing spaCy: python -m spacy download en_core_web_sm
"""

import pandas as pd
import spacy
import ast
from tqdm import tqdm

# Load spaCy model
print("Loading spaCy model...")
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("❌ spaCy model not found. Please run:")
    print("   python -m spacy download en_core_web_sm")
    exit(1)

def extract_medical_keywords(text):
    """
    Extract medical keywords from text using NLP
    
    Args:
        text: Medical text (conditions, eligibility criteria)
    
    Returns:
        List of unique keywords (lowercase)
    """
    if not text or pd.isna(text):
        return []
    
    # Process with spaCy
    doc = nlp(text.lower())
    
    keywords = []
    
    # Extract noun chunks (medical terms are often noun phrases)
    for chunk in doc.noun_chunks:
        # Filter out very short or very long chunks
        chunk_text = chunk.text.strip()
        word_count = len(chunk_text.split())
        
        if 1 <= word_count <= 4:  # Keep 1-4 word phrases
            keywords.append(chunk_text)
    
    # Also extract important single nouns
    for token in doc:
        if token.pos_ == "NOUN" and len(token.text) > 3:
            keywords.append(token.text)
    
    # Remove duplicates and return
    return list(set(keywords))

def process_trials_keywords():
    """Add keywords to trials dataset"""
    
    print("Loading trials...")
    df = pd.read_csv("trials_clean.csv")
    
    print(f"Extracting keywords from {len(df)} trials...")
    
    # Extract keywords from eligibility criteria
    keywords_list = []
    for text in tqdm(df["eligibility_text"], desc="Processing trials"):
        keywords = extract_medical_keywords(text)
        keywords_list.append(keywords)
    
    df["keywords"] = keywords_list
    
    # Save back to CSV
    df.to_csv("trials_clean.csv", index=False)
    
    print(f"✅ Added keywords to trials")
    
    # Statistics
    avg_keywords = sum(len(k) for k in keywords_list) / len(keywords_list)
    print(f"Average keywords per trial: {avg_keywords:.1f}")
    
    return df

def process_patients_keywords():
    """Add keywords to patients dataset"""
    
    print("\nLoading patients...")
    df = pd.read_csv("patients.csv")
    
    print(f"Extracting keywords from {len(df)} patients...")
    
    # Extract keywords from conditions
    keywords_list = []
    for conditions_str in tqdm(df["conditions"], desc="Processing patients"):
        try:
            # Parse list from string
            conditions = ast.literal_eval(conditions_str)
            # Combine all conditions into one text
            combined_text = " ".join(conditions)
            keywords = extract_medical_keywords(combined_text)
            keywords_list.append(keywords)
        except:
            keywords_list.append([])
    
    df["condition_keywords"] = keywords_list
    
    # Save back to CSV
    df.to_csv("patients.csv", index=False)
    
    print(f"✅ Added keywords to patients")
    
    # Statistics
    avg_keywords = sum(len(k) for k in keywords_list) / len(keywords_list)
    print(f"Average keywords per patient: {avg_keywords:.1f}")
    
    return df

if __name__ == "__main__":
    print("="*60)
    print("EXTRACTING MEDICAL KEYWORDS")
    print("="*60)
    
    # Process trials
    trials_df = process_trials_keywords()
    
    # Process patients
    patients_df = process_patients_keywords()
    
    # Sample output
    print("\n" + "="*60)
    print("SAMPLE KEYWORDS:")
    print("="*60)
    
    print("\nTrial keywords:")
    sample_trial = trials_df.iloc[0]
    trial_keywords = ast.literal_eval(sample_trial["keywords"]) if isinstance(sample_trial["keywords"], str) else sample_trial["keywords"]
    print(f"Trial: {sample_trial['title'][:60]}...")
    print(f"Keywords: {', '.join(trial_keywords[:10])}...")
    
    print("\nPatient keywords:")
    sample_patient = patients_df.iloc[0]
    patient_keywords = ast.literal_eval(sample_patient["condition_keywords"]) if isinstance(sample_patient["condition_keywords"], str) else sample_patient["condition_keywords"]
    print(f"Patient: {sample_patient['id']}")
    print(f"Conditions: {sample_patient['conditions']}")
    print(f"Keywords: {', '.join(patient_keywords[:10])}...")
