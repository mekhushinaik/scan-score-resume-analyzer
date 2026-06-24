"""
app.py
-------
Main Streamlit app for the AI Resume Analyzer.
100% FREE — uses local rule-based analysis, no API key required.

Run with: streamlit run app.py
"""

import time
import streamlit as st

from resume_parser import extract_resume_text
from analyzer import analyze_resume


st.set_page_config(
    page_title="ScanScore — AI Resume Analyzer",
    page_icon="🔬",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Fonts + global theme
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

    :root {
        --coral: #FF8A7A;
        --amber: #FFD27A;
        --mint: #7BE0B0;
        --violet-deep: #F6F3FF;
        --violet-mid: #EEE8FF;
        --ink: #1F1B2E;
        --text-soft: #5E5873;
        --border-soft: rgba(31, 27, 46, 0.10);
    }

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #FBF8FF 0%, #F7F3FF 45%, #FFFDF8 100%);
    }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F4EEFF 0%, #FFF8EF 100%);
        border-right: 1px solid var(--border-soft);
    }
    [data-testid="stSidebar"] * { color: var(--ink) !important; }

    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; color: var(--ink) !important; }
    p, span, label, .stMarkdown, div { color: var(--ink); }

    /* ---------- Hero ---------- */
    @keyframes scanSweep {
        0%   { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    @keyframes floatUp {
        from { opacity: 0; transform: translateY(14px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .hero-wrap {
        text-align: center;
        padding: 18px 0 8px 0;
        animation: floatUp 0.6s ease-out;
    }
    .hero-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(255,255,255,0.75);
        border: 1px solid rgba(31,27,46,0.10);
        color: var(--ink);
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 0.78rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 18px;
        box-shadow: 0 4px 18px rgba(31,27,46,0.05);
    }
    .hero-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--mint); box-shadow: 0 0 8px var(--mint); }
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 3.4rem;
        line-height: 1.05;
        margin: 0;
        background: linear-gradient(100deg, var(--ink) 30%, var(--coral) 42%, #F1A93A 50%, var(--ink) 62%);
        background-size: 250% 100%;
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: scanSweep 5s linear infinite;
    }
    .hero-sub {
        font-size: 1.15rem;
        color: var(--text-soft);
        max-width: 620px;
        margin: 18px auto 0 auto;
        line-height: 1.55;
    }
    .hero-pills { display: flex; justify-content: center; gap: 10px; margin-top: 22px; flex-wrap: wrap; }
    .hero-pill {
        font-size: 0.82rem;
        font-weight: 600;
        padding: 7px 14px;
        border-radius: 999px;
        color: #2A2148;
        box-shadow: 0 3px 12px rgba(31,27,46,0.06);
    }
    .pill-coral { background: #FFD3CD; }
    .pill-amber { background: #FFE7B3; }
    .pill-mint  { background: #D8F8E9; }

    /* ---------- Section dividers ---------- */
    .section-divider {
        display: flex;
        align-items: center;
        gap: 14px;
        margin: 38px 0 18px 0;
    }
    .section-divider .line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(255,138,122,0.55), rgba(255,210,122,0.25));
    }
    .section-divider .label {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--ink);
        white-space: nowrap;
    }

    /* ---------- Animations for results ---------- */
    @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes popIn { 0% { transform: scale(0.85); opacity: 0; } 70% { transform: scale(1.03); } 100% { transform: scale(1); opacity: 1; } }
    .fade-in { animation: fadeIn 0.5s ease-out; }
    .pop-in { animation: popIn 0.45s cubic-bezier(0.34, 1.56, 0.64, 1); }

    /* ---------- Score gauge ring ---------- */
    .score-ring-wrap { display: flex; justify-content: center; align-items: center; padding: 6px 0 2px 0; }
    .score-ring {
        position: relative; width: 150px; height: 150px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 8px 24px rgba(31,27,46,0.08);
    }
    .score-ring-inner {
        width: 122px; height: 122px; border-radius: 50%;
        background: #FFFFFF;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        box-shadow: inset 0 0 0 1px rgba(31,27,46,0.06);
    }
    .score-number { font-family: 'Space Grotesk', sans-serif; font-size: 2.1rem; font-weight: 700; line-height: 1; }
    .score-label { font-size: 0.7rem; opacity: 0.7; margin-top: 2px; letter-spacing: 0.04em; text-transform: uppercase; color: var(--ink); }

    /* ---------- Feedback cards ---------- */
    .feedback-card {
        border-radius: 12px; padding: 13px 16px; margin-bottom: 10px;
        border-left: 4px solid transparent;
        background: rgba(255,255,255,0.82);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        color: var(--ink);
        border: 1px solid rgba(31,27,46,0.06);
        box-shadow: 0 6px 20px rgba(31,27,46,0.04);
    }
    .feedback-card:hover { transform: translateX(3px); box-shadow: 0 8px 24px rgba(31,27,46,0.08); }
    .strength-card { border-left-color: #7BE0B0; }
    .weakness-card { border-left-color: #FF8A7A; }
    .improvement-card { border-left-color: #FFD27A; margin-bottom: 8px; }
    .improvement-num {
        display: inline-flex; align-items: center; justify-content: center;
        width: 22px; height: 22px; border-radius: 50%;
        background: #FFD27A; color: #2A2148;
        font-size: 0.75rem; font-weight: 700; margin-right: 8px; flex-shrink: 0;
    }
    .keyword-chip {
        display: inline-block;
        background: rgba(255,210,122,0.25);
        border: 1px solid rgba(241,169,58,0.45);
        color: var(--ink);
        padding: 4px 12px; border-radius: 16px; margin: 3px;
        font-size: 0.85rem; transition: transform 0.15s ease;
    }
    .keyword-chip:hover { transform: scale(1.08); background: rgba(255,210,122,0.38); }

    /* ---------- Streamlit widget restyling ---------- */
    .stButton > button {
        background: linear-gradient(100deg, #FFC1B8, #FFE29A);
        color: #2A2148;
        border: none;
        font-weight: 700;
        font-family: 'Space Grotesk', sans-serif;
        border-radius: 10px;
        padding: 0.6rem 1.6rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        box-shadow: 0 6px 18px rgba(255,138,122,0.18);
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(255,138,122,0.26); }

    [data-testid="stFileUploaderDropzone"] {
        background: rgba(255,255,255,0.72);
        border: 1.5px dashed rgba(241,169,58,0.55);
        border-radius: 14px;
    }

    div[data-testid="stTextArea"] textarea,
    .stTextArea textarea,
    textarea {
        background-color: #FFFFFF !important;
        color: #1F1B2E !important;
        -webkit-text-fill-color: #1F1B2E !important;
        caret-color: #1F1B2E !important;
        border-radius: 12px !important;
        border: 1px solid rgba(31,27,46,0.14) !important;
    }

    div[data-testid="stTextArea"] textarea::placeholder,
    .stTextArea textarea::placeholder,
    textarea::placeholder {
        color: rgba(31,27,46,0.45) !important;
        -webkit-text-fill-color: rgba(31,27,46,0.45) !important;
    }

    [data-testid="stExpander"] {
        background: rgba(255,255,255,0.76);
        border-radius: 12px !important;
        border: 1px solid rgba(31,27,46,0.08) !important;
    }

    [data-testid="stMetricValue"] { color: var(--ink); }

    .stAlert {
        color: #1F1B2E !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def score_color(score: int) -> str:
    """Returns a hex color based on score tier."""
    if score >= 80:
        return "#7BE0B0"   # mint
    elif score >= 60:
        return "#FFD27A"   # amber
    elif score >= 40:
        return "#FFB07A"   # orange-coral
    else:
        return "#FF8A7A"   # coral


def render_score_ring(score: int, label: str = "SCORE"):
    """Renders an animated-feeling circular gauge using conic-gradient CSS."""
    color = score_color(score)
    pct = min(max(score, 0), 100)
    angle = pct * 3.6
    html = f"""
    <div class="score-ring-wrap pop-in">
        <div class="score-ring" style="background: conic-gradient({color} {angle}deg, rgba(31,27,46,0.10) {angle}deg);">
            <div class="score-ring-inner">
                <div class="score-number" style="color:{color};">{pct}</div>
                <div class="score-label">{label}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_cards(items, css_class, icon):
    for item in items:
        st.markdown(
            f'<div class="feedback-card {css_class} fade-in">{icon} {item}</div>',
            unsafe_allow_html=True,
        )


def render_improvements(items):
    for i, item in enumerate(items, 1):
        st.markdown(
            f'<div class="feedback-card improvement-card fade-in">'
            f'<span class="improvement-num">{i}</span>{item}</div>',
            unsafe_allow_html=True,
        )


def render_keyword_chips(keywords):
    chips = "".join(f'<span class="keyword-chip">{kw}</span>' for kw in keywords)
    st.markdown(f'<div class="fade-in">{chips}</div>', unsafe_allow_html=True)


def section_divider(label: str):
    st.markdown(
        f'<div class="section-divider"><div class="line"></div>'
        f'<div class="label">{label}</div><div class="line"></div></div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.title("🔬 ScanScore")
st.sidebar.markdown(
    "This tool is **completely free** — it analyzes your resume locally "
    "using rule-based checks (no API key, no internet calls, no cost).\n\n"
    "**How it works**\n"
    "1. Upload your resume (PDF/DOCX/TXT)\n"
    "2. (Optional) Paste a job description\n"
    "3. Click Analyze\n"
    "4. Get a score + detailed feedback"
)
st.sidebar.markdown("---")
st.sidebar.caption(
    "Note: this uses automated heuristics (keyword matching, structure checks), "
    "not a human or AI judgment call. Use it as a helpful starting point."
)


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-wrap">
        <div class="hero-eyebrow"><span class="hero-dot"></span> FREE &middot; INSTANT &middot; NO SIGN-UP</div>
        <h1 class="hero-title">Scan your resume.<br/>See what recruiters see.</h1>
        <p class="hero-sub">Upload your resume and get an instant score, a breakdown of every section,
        and the exact fixes to make before you hit "apply."</p>
        <div class="hero-pills">
            <span class="hero-pill pill-coral">✓ Action verb check</span>
            <span class="hero-pill pill-amber">✓ ATS formatting scan</span>
            <span class="hero-pill pill-mint">✓ Job match score</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


section_divider("UPLOAD")

col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx", "txt"],
        help="PDF, DOCX, or TXT files only.",
    )

with col2:
    job_description = st.text_area(
        "Job description (optional)",
        height=160,
        placeholder="Paste a job description here to get a job-match score...",
    )

analyze_clicked = st.button("🔬 Analyze Resume", type="primary", use_container_width=False)

if analyze_clicked:
    if not uploaded_file:
        st.error("Please upload a resume file first.")
    else:
        try:
            progress_text = st.empty()
            bar = st.progress(0)

            progress_text.markdown("📖 Extracting text from your resume...")
            bar.progress(25)
            resume_text = extract_resume_text(uploaded_file)
            time.sleep(0.3)

            progress_text.markdown("🔎 Scanning sections and structure...")
            bar.progress(55)
            time.sleep(0.3)

            progress_text.markdown("🧮 Calculating your score...")
            bar.progress(80)
            result = analyze_resume(resume_text, job_description)
            time.sleep(0.3)

            bar.progress(100)
            progress_text.markdown("✅ Done!")
            time.sleep(0.25)

            bar.empty()
            progress_text.empty()

            st.session_state["last_result"] = result
            st.session_state["last_resume_text"] = resume_text
            st.session_state["just_analyzed"] = True

        except ValueError as ve:
            st.error(f"⚠️ {ve}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")


# ---------------------------------------------------------------------------
# Display results
# ---------------------------------------------------------------------------
if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    score = result.get("overall_score", 0)

    if st.session_state.get("just_analyzed") and score >= 80:
        st.balloons()
    st.session_state["just_analyzed"] = False

    section_divider("YOUR RESULTS")

    score_col, summary_col = st.columns([1, 3])
    with score_col:
        render_score_ring(score, "OVERALL")
    with summary_col:
        st.markdown(f'<div class="fade-in" style="padding-top: 30px;">{result.get("summary", "")}</div>', unsafe_allow_html=True)

    if result.get("job_match_score") is not None:
        st.markdown("####")
        jm_col, jm_text_col = st.columns([1, 3])
        with jm_col:
            render_score_ring(result["job_match_score"], "JOB MATCH")
        with jm_text_col:
            st.markdown(f'<div class="fade-in" style="padding-top: 30px;">{result.get("job_match_notes", "")}</div>', unsafe_allow_html=True)

    section_divider("STRENGTHS & WEAKNESSES")

    strengths_col, weaknesses_col = st.columns(2)
    with strengths_col:
        st.subheader("✅ Strengths")
        render_cards(result.get("strengths", []), "strength-card", "✅")

    with weaknesses_col:
        st.subheader("⚠️ Weaknesses")
        render_cards(result.get("weaknesses", []), "weakness-card", "⚠️")

    section_divider("SECTION-BY-SECTION")

    section_feedback = result.get("section_feedback", {})
    section_labels = {
        "contact_info": "Contact Info",
        "summary_objective": "Summary / Objective",
        "work_experience": "Work Experience",
        "skills": "Skills",
        "education": "Education",
        "formatting": "Formatting & ATS-Friendliness",
    }
    for key, label in section_labels.items():
        if key in section_feedback and section_feedback[key]:
            with st.expander(label):
                st.write(section_feedback[key])

    section_divider("NEXT STEPS")

    st.subheader("🛠️ Actionable Improvements")
    render_improvements(result.get("actionable_improvements", []))

    if result.get("keyword_suggestions"):
        st.markdown("####")
        st.subheader("🔑 Suggested Keywords to Add")
        render_keyword_chips(result["keyword_suggestions"])

    section_divider("RAW TEXT")
    with st.expander("View extracted resume text (for debugging)"):
        st.text(st.session_state.get("last_resume_text", ""))