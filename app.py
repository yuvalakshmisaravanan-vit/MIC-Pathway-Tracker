import streamlit as strl
import os
import random
from openai import OpenAI

# 1. Page Configuration
strl.set_page_config(page_title="MIC Pathway Tracker", page_icon="🎯", layout="wide")

# 2. Hardcoded Certification Dataset (Prerequisite logic built natively)
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

# Fallback recommendations if the AI API fails or Key is absent
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

# Helper function to mock or call real OpenAI
def generate_ai_explanation(cert_name, domain):
    api_key = os.environ.get("OPENAI_API_KEY") or strl.sidebar.text_input("Enter OpenAI API Key (Optional)", type="password")
    
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
        return response.choices[0].message.content.strip()
    except Exception:
        return f"[Fallback Info] {random.choice(FALLBACKS)}"

# 4. App UI Layout
strl.title("🎯 Microsoft Certification Roadmap Tracker")
strl.caption("MIC Development Recruitment Stage 2 Task — Built entirely via Python Logic Structure")

# Domain Selector Tabs
selected_domain = strl.sidebar.selectbox("Choose a Track/Domain Goal:", list(DATASET.keys()))

strl.subheader(f"📍 Currently Tracking: {selected_domain}")
strl.markdown("---")

# 5. Core Roadmap Loop with Logic State Computations
for step, cert in enumerate(DATASET[selected_domain], 1):
    c_id = cert["id"]
    c_name = cert["name"]
    c_prereqs = cert["prereqs"]
    
    # State Determination Logic Matrix
    if c_id in strl.session_state.completed:
        status = "COMPLETED ✅"
        bg_color = "#1e3a1e" 
        border_color = "#22c55e"
    elif all(p_id in strl.session_state.completed for p_id in c_prereqs):
        status = "AVAILABLE 🔓"
        bg_color = "#1e293b"
        border_color = "#3b82f6"
    else:
        status = "LOCKED 🔒"
        bg_color = "#0f172a"
        border_color = "#475569"

    # Dynamic Render Box
    with strl.container():
        strl.markdown(
            f"""
            <div style="background-color: {bg_color}; border: 2px solid {border_color}; padding: 20px; border-radius: 12px; margin-bottom: 15px;">
                <span style="font-family: monospace; font-size: 11px; background-color: rgba(255,255,255,0.1); padding: 3px 8px; border-radius: 4px;">Step {step} • {status}</span>
                <h3 style="margin-top: 8px; margin-bottom: 4px; color: #f8fafc;">{c_name}</h3>
                <p style="font-size: 12px; color: #94a3b8; margin-bottom: 12px;">Prerequisites: {', '.join(c_prereqs) if c_prereqs else 'None'}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Action Buttons Layout row
        col1, col2 = strl.columns([1, 4])
        
        with col1:
            if status == "AVAILABLE 🔓":
                # When clicked, code computes transition instantly
                if strl.button(f"Complete Step ✓", key=f"btn_{c_id}"):
                    strl.session_state.completed.add(c_id)
                    
                    # Proactively request explanation for the subsequent items that unlock
                    for next_cert in DATASET[selected_domain]:
                        if next_cert["id"] not in strl.session_state.completed:
                            with strl.spinner("Generating automated next-step insight..."):
                                strl.session_state.ai_explanations[next_cert["id"]] = generate_ai_explanation(next_cert["name"], selected_domain)
                    strl.rerun()
            elif status == "COMPLETED ✅":
                strl.write("🎉 Done!")
            else:
                strl.button("Locked 🔒", disabled=True, key=f"dis_{c_id}")
                
        with col2:
            strl.markdown(f"[View Official Documentation ↗]({cert['url']})")
            
        # Display AI Recommendation text directly inline inside the active or next available steps
        if status == "AVAILABLE 🔓":
            explanation = strl.session_state.ai_explanations.get(c_id, "All prerequisites met. Ready to begin your cloud path analysis.")
            strl.info(f"💡 **AI Suggestion**: {explanation}")
            
    strl.markdown("<br>", unsafe_allow_html=True)

# 6. Reset Control Matrix
if strl.sidebar.button("Clear Progress & Reset"):
    strl.session_state.completed = set()
    strl.session_state.ai_explanations = {}
    strl.rerun()
