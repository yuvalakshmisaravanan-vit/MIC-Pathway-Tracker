# Microsoft Certification Pathway Tracker

An interactive web application designed to track free Microsoft learning paths and certifications. This project fulfills all technical requirements for the **Option A (Frontend Only)** recruitment task.

---

## ✨ Features

* **Code-Driven Logic:** Prerequisite checking is calculated entirely using native Python structures (`all()`). The AI only handles descriptions, never the roadmap sequence.
* **Dynamic Visual States:** 
  * `Completed ✅` (Green) – Tasks successfully finished.
  * `Available 🔓` (Blue) – Next steps ready to explore.
  * `Locked 🔒` (Slate) – Steps requiring unfulfilled prerequisites.
* **API Resilience:** Built-in `try/except` exception handler that injects meaningful fallback explanations automatically if the network drops or API keys are omitted.

---

## 🔍 Core Logic Highlight

Node states are determined dynamically on each rerun using clean boolean checking:

```python
if c_id in strl.session_state.completed:
    status = "COMPLETED ✅"
elif all(p_id in strl.session_state.completed for p_id in c_prereqs):
    status = "AVAILABLE 🔓"
else:
    status = "LOCKED 🔒"
```

---

## 🛠️ How to Run Locally

1. **Install dependencies:**
   ```bash
   pip install streamlit openai
   ```

2. **Launch the application:**
   ```bash
   streamlit run app.py
   ```
   The interactive dashboard will automatically open at `http://localhost:8501`.
