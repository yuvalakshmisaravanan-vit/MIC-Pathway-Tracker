import streamlit as strl
import os
import random
from openai import OpenAI

# 1. Page Configuration
strl.set_page_config(page_title="MIC Pathway Tracker", page_icon="🎯", layout="wide")

# 2. Hardcoded Certification Dataset
DATASET = {
    "Cloud Infrastructure": [
        {"id": "az-900", "name": "AZ-900: Microsoft Azure Fundamentals", "prereqs": [], "url": "https://microsoft.com"},
        {"id": "az-104", "name": "AZ-104: Microsoft Azure Administrator", "prereqs": ["az-900"], "url": "https://microsoft.com"},
        {"id": "az-305", "name": "AZ-305: Designing Azure Infrastructure", "prereqs": ["az-104"], "url": "https://microsoft.com"}
    ],
    "AI & Data Engineering": [
        {"id": "ai-900", "name": "AI-900: Microsoft Azure AI Fundamentals", "prereqs": [], "url": "https://microsoft.com"},
        {"id": "dp-100", "name": "DP-100: Designing Data Science Solutions", "prereqs": ["ai-900"], "url": "https://microsoft.com"},
        {"id": "ai-102", "name": "AI-102: Designing Azure AI Solutions", "prereqs": ["ai-900"], "url": "https://microsoft.com"}
    ]
}

FALLBACKS = [
    "This certification cements your core concepts and maps cleanly to enterprise cloud architectures.",
    "Progressing to this node unlocks advanced administrative controls and scale implementation techniques.",
    "This module serves as the primary bridge towards specialized deployment pipelines in industry frameworks."
]

# 3. Persistent Local State Initialization
if "completed" not in strl.session_state:
    strl.session_state.completed = set()
if "ai_explanations" not in strl.session_state:
    strl.session_state.ai_explanations = {}

# 4. App UI Layout - Sidebar Configuration First
selected_domain = strl.sidebar.selectbox("Choose a Track/Domain Goal:", list(DATASET.keys()))
user_api_key = strl.sidebar.text_input("Enter OpenAI API Key (Optional)", type="password", key="global_openai_key")

def generate_ai_explanation(cert_name, domain, provided_key):
    api_key = os.environ.get("OPENAI_API_KEY") or provided_key
    if not api_key:
        return f"[Fallback Info] {random.choice(FALLBACKS)}"
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a brief career advisor. Explain in exactly 1-2 encouraging sentences why this specific certification is the next logical step."},
                {"role": "user", "content": f"Certification: {cert_name}, Domain: {domain}."}
            ],
            max_tokens=60
        )
        return response.choices.message.content.strip()
    except Exception:
        return f"[Fallback Info] {random.choice(FALLBACKS)}"
        
strl.title("🎯 Microsoft Certification Roadmap Tracker")
strl.subheader(f"📍 Currently Tracking: {selected_domain}")
strl.markdown("---")

# 5. Core Roadmap Loop with Custom Theme Configurations
for step, cert in enumerate(DATASET[selected_domain], 1):
    c_id = cert["id"]
    c_name = cert["name"]
    c_prereqs = cert["prereqs"]
    
    # [VISUAL UPDATE] Customize colors dynamically across distinct node states
    if c_id in strl.session_state.completed:
        status = "COMPLETED ✅"
        bg_color = "#0B2E1A"        # Deep muted forest green
        border_color = "#10B981"    # Vivid vibrant emerald green
        tag_style = "background-color: #064E3B; color: #34D399;"
    elif all(p_id in strl.session_state.completed for p_id in c_prereqs):
        status = "AVAILABLE 🔓"
        bg_color = "#0A2540"        # Sleek dark midnight navy
        border_color = "#00D4B2"    # High-impact glowing electric cyan/teal
        tag_style = "background-color: #004D40; color: #2EE5B5;"
    else:
        status = "LOCKED 🔒"
        bg_color = "#121824"        # Neutral dark background matte grey
        border_color = "#2D3748"    # Subdued subtle concrete grey
        tag_style = "background-color: #1A202C; color: #718096;"

    with strl.container():
        strl.markdown(
            f"""
            <div style="background-color: {bg_color}; border: 2px solid {border_color}; padding: 22px; border-radius: 12px; margin-bottom: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);">
                <span style="font-family: monospace; font-size: 11px; font-weight: bold; padding: 4px 10px; border-radius: 6px; {tag_style}">Step {step} • {status}</span>
                <h3 style="margin-top: 12px; margin-bottom: 4px; color: #F8FAFC; font-weight: 700; letter-spacing: -0.025em;">{c_name}</h3>
                <p style="font-size: 12px; color: #94A3B8; margin-bottom: 0px; opacity: 0.85;">Prerequisites: {', '.join(c_prereqs) if c_prereqs else 'None'}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        col1, col2 = strl.columns(2)
        
        with col1:
            if status == "AVAILABLE 🔓":
                if strl.button(f"Complete Step ✓", key=f"btn_{c_id}"):
                    strl.session_state.completed.add(c_id)
                    for next_cert in DATASET[selected_domain]:
                        if next_cert["id"] not in strl.session_state.completed:
                            with strl.spinner("Generating automated next-step insight..."):
                                strl.session_state.ai_explanations[next_cert["id"]] = generate_ai_explanation(
                                    next_cert["name"], selected_domain, user_api_key
                                )
                    strl.rerun()
            elif status == "COMPLETED ✅":
                strl.markdown("<span style='color: #34D399; font-weight: 500; font-size: 14px;'>🎉 Step Completed Successfully!</span>", unsafe_allow_html=True)
            else:
                strl.button("Locked 🔒", disabled=True, key=f"dis_{c_id}")
                
        with col2:
            strl.markdown(f"<div style='text-align: right; margin-top: 4px;'><a href='{cert['url']}' target='_blank' rel='noreferrer' style='color: #60A5FA; text-decoration: none; font-size: 13px; font-weight: 500;'>View Official Documentation ↗</a></div>", unsafe_allow_html=True)
            
        if status == "AVAILABLE 🔓":
            explanation = strl.session_state.ai_explanations.get(c_id, "All prerequisites met. Ready to begin your cloud path analysis.")
            strl.info(f"💡 **AI Suggestion**: {explanation}")
            
    strl.markdown("<br>", unsafe_allow_html=True)

if strl.sidebar.button("Clear Progress & Reset"):
    strl.session_state.completed = set()
    strl.session_state.ai_explanations = {}
    strl.rerun()
