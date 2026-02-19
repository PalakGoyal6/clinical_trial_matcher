"""
Clinical Trial Patient Matching Engine - Streamlit App
UPDATED VERSION: Shows correct validation metrics (66% accuracy) and proper speed measurements
"""

import streamlit as st
import pandas as pd
import json
import ast
from matching import match_patient_to_trials
from extract_keywords import extract_medical_keywords
import os

# Page config
st.set_page_config(
    page_title="Clinical Trial Matcher",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .validation-note {
        background-color: #e8f4f8;
        padding: 0.8rem;
        border-radius: 0.3rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Load data with caching
@st.cache_data
def load_data():
    """Load all required data files"""
    try:
        patients = pd.read_csv("patients.csv")
        trials = pd.read_csv("trials_clean.csv")
        
        if os.path.exists("matches.json"):
            with open("matches.json") as f:
                matches = json.load(f)
        else:
            matches = {}
        
        # Load performance metrics
        if os.path.exists("final_metrics.json"):
            with open("final_metrics.json") as f:
                metrics = json.load(f)
        else:
            metrics = None
        
        # Load validation report (CORRECT accuracy - 66%)
        if os.path.exists("validation_report.json"):
            with open("validation_report.json") as f:
                validation = json.load(f)
        else:
            validation = None
        
        return patients, trials, matches, metrics, validation
    
    except FileNotFoundError as e:
        st.error(f"❌ Data file not found: {e}")
        st.info("Run: python fetch_trials.py → process_trials.py → extract_keywords.py → matching.py → metrics_corrected.py → validation_improved.py")
        st.stop()

def safe_eval_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            return ast.literal_eval(value)
        except:
            return []
    return []

def display_patient_info(patient):
    st.markdown("### 👤 Patient Information")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Patient ID", patient["id"])
    with col2:
        st.metric("Age", f"{patient['age']} years")
    with col3:
        st.metric("Gender", patient["gender"].capitalize())
    
    st.markdown("#### 📋 Medical History")
    conditions = safe_eval_list(patient["conditions"])
    medications = safe_eval_list(patient["medications"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Conditions:**")
        if conditions:
            for condition in conditions[:5]:
                st.markdown(f"- {condition}")
            if len(conditions) > 5:
                st.markdown(f"*... and {len(conditions) - 5} more*")
        else:
            st.markdown("*No conditions recorded*")
    
    with col2:
        st.markdown("**Medications:**")
        if medications:
            for med in medications[:5]:
                st.markdown(f"- {med}")
            if len(medications) > 5:
                st.markdown(f"*... and {len(medications) - 5} more*")
        else:
            st.markdown("*No medications recorded*")

def display_matches(matches, trials_df):
    st.markdown("### 🎯 Matched Clinical Trials")
    
    if not matches:
        st.warning("⚠️ No suitable trials found")
        return
    
    st.success(f"✅ Found {len(matches)} matching trials")
    
    for i, match in enumerate(matches[:10], 1):
        trial = trials_df[trials_df["nct_id"] == match["nct_id"]]
        if trial.empty:
            continue
        trial = trial.iloc[0]
        
        score_color = "🟢" if match["score"] >= 70 else "🟡" if match["score"] >= 50 else "🟠"
        
        with st.expander(f"{score_color} **Match #{i}** - {match['title'][:80]}... (Score: {match['score']}/100)"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**NCT ID:** [{trial['nct_id']}](https://clinicaltrials.gov/study/{trial['nct_id']})")
                st.markdown(f"**Condition:** {trial['condition']}")
                st.markdown(f"**Age:** {trial['age_min']}-{trial['age_max']} years")
                st.markdown(f"**Gender:** {trial['gender']}")
                st.markdown(f"**Status:** {trial['status']}")
            
            with col2:
                st.metric("Match Score", f"{match['score']}/100")
                if match["score"] >= 70:
                    st.success("Excellent")
                elif match["score"] >= 50:
                    st.info("Good")
                else:
                    st.warning("Fair")
            
            st.markdown("**Why This Matches:**")
            for reason in match["reasons"]:
                prefix = "✅" if "✓" in reason else "❌"
                clean_reason = reason.replace("✓", "").replace("✗", "")
                st.markdown(f"{prefix} {clean_reason}")
            
            st.markdown("**Eligibility Criteria:**")
            criteria = trial["eligibility_text"]
            st.text(criteria[:400] + "..." if len(criteria) > 400 else criteria)

def main():
    st.markdown('<p class="main-header">🏥 Clinical Trial Patient Matching Engine</p>', unsafe_allow_html=True)
    st.markdown("*NLP-powered system to match patients to clinical trials*")
    st.markdown("---")
    
    patients_df, trials_df, all_matches, metrics, validation = load_data()
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["🔍 Patient Matching", "📊 System Overview", "➕ Custom Patient"])
    
    # Sidebar metrics
    if metrics:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📈 Performance")
        st.sidebar.metric("Patients", metrics["dataset"]["total_patients"])
        st.sidebar.metric("Trials", metrics["dataset"]["total_trials"])
        st.sidebar.metric("Match Time", f"{metrics['performance']['avg_time_per_patient_seconds']}s")
        st.sidebar.metric("Speedup", f"{int(metrics['performance']['speedup_vs_manual'])}×")
        
        if validation and "strict_heuristic" in validation:
            st.sidebar.metric("Accuracy", f"{validation['strict_heuristic']['accuracy_percent']}%")
            st.sidebar.caption("Strict (score ≥60)")
        else:
            st.sidebar.metric("Accuracy", "Run validation")
        
        st.sidebar.metric("Coverage", f"{metrics['coverage']['coverage_percent']}%")
    
    if page == "🔍 Patient Matching":
        st.header("🔍 Patient Matching")
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Select Patient")
        
        patient_ids = patients_df["id"].tolist()
        selected_id = st.sidebar.selectbox("Patient ID", patient_ids)
        
        patient = patients_df[patients_df["id"] == selected_id].iloc[0]
        display_patient_info(patient)
        
        st.markdown("---")
        matches = all_matches.get(selected_id, [])
        display_matches(matches, trials_df)
    
    elif page == "📊 System Overview":
        st.header("📊 System Overview")
        
        if not metrics:
            st.warning("Run: python metrics_corrected.py")
            return
        
        st.markdown("### 🎯 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Patients", metrics["dataset"]["total_patients"])
        with col2:
            st.metric("Trials", metrics["dataset"]["total_trials"])
        with col3:
            st.metric("Matches", metrics["coverage"].get("total_matches", 0))
        with col4:
            st.metric("Avg/Patient", metrics["coverage"]["avg_matches_per_patient"])
        
        st.markdown("---")
        st.markdown("### ⚡ Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Speed**")
            st.metric("Time/Patient", f"{metrics['performance']['avg_time_per_patient_seconds']}s")
            st.metric("Speedup", f"{int(metrics['performance']['speedup_vs_manual'])}×")
            st.info("Baseline: 30 min manual screening")
        
        with col2:
            st.markdown("**Accuracy**")
            if validation and "strict_heuristic" in validation:
                acc = validation['strict_heuristic']['accuracy_percent']
                st.metric("Validation", f"{acc}%")
                st.caption("Score ≥60, ≥2 keywords, age/gender match")
            else:
                st.warning("Run validation_improved.py")
            
            st.metric("Coverage", f"{metrics['coverage']['coverage_percent']}%")
        
        st.markdown("---")
        st.markdown("### 🔬 Validation Details")
        
        if validation and "strict_heuristic" in validation:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Validation Results**")
                acc = validation['strict_heuristic']['accuracy_percent']
                total = validation['strict_heuristic']['total_evaluated']
                valid = validation['strict_heuristic']['valid_matches']
                
                st.metric("Accuracy", f"{acc}%")
                st.write(f"Valid: {valid}/{total}")
                
                st.markdown("""
                <div class="validation-note">
                <strong>Criteria:</strong><br>
                • Score ≥60<br>
                • ≥2 keywords<br>
                • Age/gender match
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("**Score Distribution**")
                if "score_distribution" in validation:
                    dist = validation['score_distribution']
                    st.metric("Avg Score", f"{dist['avg_score']}/100")
                    st.metric("Avg Top Match", f"{dist['avg_top_score']}/100")
                    st.write(f"Excellent (≥70): {dist['excellent_matches_percent']}%")
    
    elif page == "➕ Custom Patient":
        st.header("➕ Custom Patient")
        
        with st.form("custom_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                age = st.number_input("Age", 18, 100, 45)
                gender = st.selectbox("Gender", ["male", "female"])
            
            with col2:
                conditions = st.text_area("Conditions (comma-separated)", "Type 2 Diabetes, Hypertension")
                medications = st.text_area("Medications (comma-separated)", "Metformin, Lisinopril")
            
            submit = st.form_submit_button("🔍 Find Trials")
        
        if submit:
            cond_list = [c.strip() for c in conditions.split(",") if c.strip()]
            med_list = [m.strip() for m in medications.split(",") if m.strip()]
            keywords = extract_medical_keywords(" ".join(cond_list))
            
            custom_patient = pd.Series({
                "id": "custom",
                "age": age,
                "gender": gender.lower(),
                "conditions": cond_list,
                "medications": med_list,
                "condition_keywords": keywords
            })
            
            st.markdown("---")
            display_patient_info(custom_patient)
            
            st.markdown("---")
            with st.spinner("Finding matches..."):
                matches = match_patient_to_trials(custom_patient, trials_df, top_k=10)
            
            display_matches(matches, trials_df)

if __name__ == "__main__":
    main()
