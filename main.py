import streamlit as st
import requests
import datetime
import os

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

# ---- Streamlit UI ----
st.title("Cross-Subject AI Assistant")
st.write("Powered by Comet + Notion. Helps students across Math, Science, History, and Literature.")

query = st.text_area("Enter your question or topic:")

if st.button("Analyze"):
    subject = detect_subject(query)
    st.write(f"Detected Subject: **{subject}**")

    # Placeholder outputs (replace with Comet integration later)
    summary = "Quick summary of topic..."
    deep_dive = "Detailed explanation with structured steps..."
    visualization = "Graph/Timeline/Diagram placeholder..."
    sources = "https://example.com"

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
