import streamlit as st
import requests
import os
from dotenv import load_dotenv

# ---- Load environment variables ----
load_dotenv()

# ---- Subject detection ----
def detect_subject(query: str) -> str:
    query_lower = query.lower()
    if any(word in query_lower for word in ["integral", "derivative", "equation", "solve", "∫", "∑"]):
        return "Math"
    elif any(word in query_lower for word in ["experiment", "hypothesis", "reaction", "photosynthesis", "biology", "chemistry"]):
        return "Science"
    elif any(word in query_lower for word in ["timeline", "revolution", "world war", "causes", "history"]):
        return "History"
    elif any(word in query_lower for word in ["theme", "character", "metaphor", "poem", "novel", "literature", "analysis"]):
        return "Literature"
    else:
        return "General"

# ---- Comet (Perplexity) Integration ----
def query_perplexity(prompt, model="sonar", system_message="Provide concise and accurate answers."):
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        st.error("Missing PERPLEXITY_API_KEY. Please set it in your .env file.")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.7,
        "top_p": 0.9
    }
    response = requests.post("https://api.perplexity.ai/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code}")
        st.error(response.text)
        return None

# ---- Streamlit UI ----
st.title("Cross-Subject AI Assistant")
st.write("Powered by Comet. Helps students across Math, Science, History, and Literature.")

query = st.text_area("Enter your question or topic:")

if st.button("Analyze"):
    subject = detect_subject(query)
    st.write(f"Detected Subject: **{subject}**")

    # Call Comet API
    result = query_perplexity(query)

    if result:
        answer_text = result["choices"][0]["message"]["content"]

        # Simple parsing (can refine later)
        summary = answer_text[:200]  # first 200 chars
        deep_dive = answer_text
        visualization = "Visualization placeholder (attach charts later)"
        sources = "Sources placeholder (Comet may include citations in response)"
    else:
        summary = "Error retrieving summary."
        deep_dive = "Error retrieving deep dive."
        visualization = "Error retrieving visualization."
        sources = "Error retrieving sources."

    # Display results in tabs
    tabs = st.tabs(["Summary", "Deep Dive", "Visualization", "Sources"])
    with tabs[0]:
        st.write(summary)
    with tabs[1]:
        st.write(deep_dive)
    with tabs[2]:
        st.write(visualization)
    with tabs[3]:
        st.write(sources)

