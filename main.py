import streamlit as st
import requests
import datetime
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

# ---- Notion API Integration ----
NOTION_API_KEY = os.getenv("NOTION_API_KEY")  # safer than hardcoding
DATABASE_ID = "2aed872b-594c-8085-b6f7-0037b9546e1c"

def save_to_notion(subject, title, summary, deep_dive, sources):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Title": {"title": [{"text": {"content": title}}]},
            "Subject": {"select": {"name": subject}},
            "Summary": {"rich_text": [{"text": {"content": summary}}]},
            "Deep Dive": {"rich_text": [{"text": {"content": deep_dive}}]},
            "Sources": {"url": sources},
            "Created At": {"date": {"start": datetime.datetime.now().isoformat()}}
        }
    }

    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200

# ---- Comet (Perplexity) Integration ----
def query_perplexity(prompt, model="sonar", system_message="Provide concise and accurate answers."):
    api_key = os.getenv("PERPLEXITY_API_KEY")
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
st.write("Powered by Comet + Notion. Helps students across Math, Science, History, and Literature.")

query = st.text_area("Enter your question or topic:")

if st.button("Analyze"):
    subject = detect_subject(query)
    st.write(f"Detected Subject: **{subject}**")

    # Call Comet API
    result = query_perplexity(query)

    if result:
        answer_text = result["choices"][0]["message"]["content"]

        # Simple parsing (you can refine later)
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

    if st.button("Save to Knowledge Vault"):
        success = save_to_notion(subject, query[:50], summary, deep_dive, sources)
        if success:
            st.success("Saved to Notion Knowledge vault!")
        else:
            st.error("Failed to save. Check API key and database ID.")
