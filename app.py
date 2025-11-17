import streamlit as st
import pandas as pd
import datetime
import os
from typing import Dict, List, Tuple

# Optional math support (no external APIs)
try:
    import sympy as sp
except ImportError:
    sp = None

# -------------------------------
# Local datasets (static knowledge)
# -------------------------------
HISTORY_NOTES = [
    {"topic": "World War I Causes", "summary": "Militarism, alliances, imperialism, and nationalism set the stage for conflict. The assassination of Archduke Franz Ferdinand in 1914 triggered the war.", "sources": "Encyclopedia entries and standard history texts."},
    {"topic": "French Revolution Overview", "summary": "Economic hardship, Enlightenment ideas, and social inequality led to a revolution starting in 1789, reshaping French society and politics.", "sources": "Primary sources and scholarly summaries."},
]

SCIENCE_NOTES = [
    {"topic": "Photosynthesis", "summary": "Plants convert light energy into chemical energy, producing glucose and oxygen from CO2 and water in chloroplasts.", "sources": "Intro biology references."},
    {"topic": "States of Matter", "summary": "Solid, liquid, gas, and plasma differ by particle arrangement, energy, and intermolecular forces.", "sources": "Chemistry textbooks."},
]

LITERATURE_NOTES = [
    {"topic": "Metaphor", "summary": "A figure of speech that describes an object or action as something else to illuminate meaning.", "sources": "Literary analysis guides."},
    {"topic": "Character Arc", "summary": "The transformation or inner journey of a character over the course of a story.", "sources": "Narrative theory materials."},
]

GENERAL_NOTES = [
    {"topic": "Time Management", "summary": "Prioritize tasks, use time blocking, and review daily to maintain momentum.", "sources": "Productivity research."},
    {"topic": "Study Strategies", "summary": "Spaced repetition, active recall, and interleaving improve long-term retention.", "sources": "Learning science."},
]

# -------------------------------
# Subject detection
# -------------------------------
SUBJECT_KEYWORDS = {
    "Math": ["integral", "derivative", "equation", "solve", "limit", "factor", "matrix", "algebra", "calculus"],
    "Science": ["experiment", "hypothesis", "reaction", "photosynthesis", "biology", "chemistry", "physics", "ecosystem"],
    "History": ["timeline", "revolution", "world war", "causes", "history", "civilization", "era", "empire"],
    "Literature": ["theme", "character", "metaphor", "poem", "novel", "literature", "analysis", "symbolism"]
}

def detect_subject(query: str) -> str:
    q = (query or "").lower()
    for subject, words in SUBJECT_KEYWORDS.items():
        if any(w in q for w in words):
            return subject
    return "General"

# -------------------------------
# Local math utilities (no APIs)
# -------------------------------
def solve_equation(expression: str) -> Tuple[str, str]:
    """
    Solve simple algebraic equations in one variable x.
    Returns (summary, deep_dive). Requires sympy; otherwise explains limitation.
    """
    if sp is None:
        return ("Math solver unavailable",
                "Install sympy to enable solving: `pip install sympy`. The app avoids external APIs and uses local computation.")
    try:
        x = sp.symbols('x')
        # Expect form like "x+2=5" or "2*x+3=7"
        if "=" in expression:
            left, right = expression.split("=")
            eq = sp.Eq(sp.sympify(left), sp.sympify(right))
            sol = sp.solve(eq, x)
            summary = f"Solution: x = {sol}"
            deep = f"Simplified equation: {sp.simplify(eq.lhs - eq.rhs)} = 0\nSymbolic solve steps use sympy's algebraic methods."
            return (summary, deep)
        else:
            # If no equals sign, try to simplify or compute derivative
            expr = sp.sympify(expression)
            summary = f"Simplified: {sp.simplify(expr)}"
            deep = "Provide an equation with '=' to solve for x, e.g., '2*x+3=11'."
            return (summary, deep)
    except Exception as e:
        return ("Could not parse equation",
                f"Ensure a valid algebraic expression (e.g., '2*x+3=11'). Error: {e}")

def derivative(expression: str) -> Tuple[str, str]:
    if sp is None:
        return ("Derivative unavailable",
                "Install sympy to enable derivatives: `pip install sympy`.")
    try:
        x = sp.symbols('x')
        f = sp.sympify(expression)
        df = sp.diff(f, x)
        return (f"Derivative df/dx: {df}", f"Computed using symbolic differentiation on f(x) = {f}.")
    except Exception as e:
        return ("Could not compute derivative", f"Check expression validity. Error: {e}")

# -------------------------------
# Local knowledge search (static data)
# -------------------------------
def search_local_notes(subject: str, query: str) -> Dict[str, str]:
    notes_map = {
        "History": HISTORY_NOTES,
        "Science": SCIENCE_NOTES,
        "Literature": LITERATURE_NOTES,
        "General": GENERAL_NOTES,
        "Math": []  # Math handled by computation
    }
    notes = notes_map.get(subject, GENERAL_NOTES)
    q = (query or "").lower()
    # Simple keyword search over topics and summaries
    for item in notes:
        blob = f"{item['topic']} {item['summary']}".lower()
        if any(word in blob for word in q.split()):
            return item
    # Fallback: first note for subject
    return notes[0] if notes else {"topic": "Math", "summary": "Use the math tools to compute solutions or derivatives.", "sources": "Local computation."}

# -------------------------------
# Local storage (CSV-based history)
# -------------------------------
HISTORY_PATH = "vault_history.csv"

def load_history() -> pd.DataFrame:
    if os.path.exists(HISTORY_PATH):
        try:
            return pd.read_csv(HISTORY_PATH)
        except Exception:
            pass
    return pd.DataFrame(columns=["timestamp", "subject", "query", "summary", "deep_dive", "sources"])

def save_history(entry: Dict[str, str]) -> None:
    df = load_history()
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df.to_csv(HISTORY_PATH, index=False)

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="Knowledge Vault (No-API)", page_icon="📚", layout="wide")
st.title("Knowledge Vault — No‑API Streamlit App")
st.write("This app runs entirely on local logic, static datasets, and optional symbolic math (sympy). No external APIs required.")

# Sidebar: History viewer and settings
with st.sidebar:
    st.header("Vault History")
    df_hist = load_history()
    if not df_hist.empty:
        st.dataframe(df_hist.tail(15), use_container_width=True)
        if st.button("Download full history CSV"):
            st.download_button("Save vault_history.csv", df_hist.to_csv(index=False), "vault_history.csv", "text/csv")
    else:
        st.caption("No history yet. Run an analysis to create entries.")

    st.header("Math tools")
    use_math = st.checkbox("Enable math helpers (sympy recommended)", value=True)

# Main input
query = st.text_area("Enter your question or topic", placeholder="e.g., Solve 2*x+3=11 or Explain photosynthesis")
analyze = st.button("Analyze")

if analyze:
    subject = detect_subject(query)
    st.subheader(f"Detected subject: {subject}")

    # Prepare outputs
    summary = ""
    deep_dive = ""
    visualization_note = ""
    sources = ""

    if subject == "Math" and use_math:
        # Decide whether user wants solution or derivative based on keywords
        q_lower = (query or "").lower()
        if "derivative" in q_lower or "d/dx" in q_lower:
            summary, deep_dive = derivative(query)
            sources = "Local symbolic computation (sympy)."
            visualization_note = "Use the 'Visualization' tab to plot functions (manual input)."
        else:
            summary, deep_dive = solve_equation(query)
            sources = "Local symbolic computation (sympy)."
            visualization_note = "Provide function form for plotting, e.g., 'sin(x)' or 'x**2'."
    else:
        note = search_local_notes(subject, query)
        summary = note["summary"]
        deep_dive = f"Topic: {note['topic']}\n\nExpanded points:\n- Key ideas summarized from local notes.\n- You can refine content by editing data/*.csv.\n- This app avoids external calls for reliability."
        sources = note["sources"]
        visualization_note = "Visualization suggestions: timelines, bar charts, concept maps."

    # Tabs for structured output
    tabs = st.tabs(["Summary", "Deep Dive", "Visualization", "Sources"])
    with tabs[0]:
        st.write(summary)
    with tabs[1]:
        st.write(deep_dive)
    with tabs[2]:
        st.write(visualization_note)
        # Optional quick plot for math (if sympy available)
        if subject == "Math" and sp is not None:
            st.markdown("Plot a function of x")
            func_text = st.text_input("f(x) =", value="x**2")
            plot_btn = st.button("Plot")
            if plot_btn:
                try:
                    x = sp.symbols('x')
                    f = sp.sympify(func_text)
                    # Sample x values and compute y
                    xs = [i/10 for i in range(-50, 51)]
                    ys = [float(f.subs(x, xv)) for xv in xs]
                    chart_df = pd.DataFrame({"x": xs, "f(x)": ys})
                    st.line_chart(chart_df, x="x", y="f(x)")
                except Exception as e:
                    st.error(f"Could not plot. Check function format. Error: {e}")
    with tabs[3]:
        st.write(sources)

    # Save to local CSV
    entry = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "subject": subject,
        "query": query,
        "summary": summary,
        "deep_dive": deep_dive,
        "sources": sources
    }
    save_history(entry)
    st.success("Saved to local Knowledge Vault (vault_history.csv).")

# Footer/help
st.markdown("---")
st.markdown("> Tip: To customize content, replace or extend the local notes in the code or load from CSV files under a data/ folder. For math, install sympy for symbolic solving and derivatives.")
