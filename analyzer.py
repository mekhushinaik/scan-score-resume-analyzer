"""
analyzer.py
------------
100% FREE, LOCAL resume analyzer. No API key, no internet calls, no cost.

Uses rule-based checks + keyword matching to score resumes and generate
feedback. Returns the same dict schema the app.py UI expects, so the UI
code never needed to change.
"""

import re
from collections import Counter

# ---------------------------------------------------------------------------
# Reference data used for checks
# ---------------------------------------------------------------------------

SECTION_KEYWORDS = {
    "summary_objective": ["summary", "objective", "profile", "about me"],
    "work_experience": ["experience", "employment", "work history", "career"],
    "skills": ["skills", "technical skills", "competencies", "proficiencies"],
    "education": ["education", "academic", "qualification", "degree"],
    "projects": ["projects", "portfolio"],
    "certifications": ["certification", "certificate", "license"],
}

ACTION_VERBS = [
    "achieved", "improved", "led", "managed", "built", "created", "designed",
    "developed", "increased", "decreased", "reduced", "launched", "implemented",
    "delivered", "drove", "spearheaded", "optimized", "streamlined", "negotiated",
    "coordinated", "executed", "established", "automated", "analyzed", "resolved",
    "mentored", "trained", "presented", "researched", "engineered", "architected",
]

WEAK_PHRASES = [
    "responsible for", "duties included", "worked on", "helped with",
    "tasked with", "in charge of", "involved in",
]

COMMON_TECH_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "sql", "react",
    "node.js", "node", "angular", "vue", "aws", "azure", "gcp", "docker",
    "kubernetes", "git", "html", "css", "django", "flask", "spring",
    "machine learning", "data analysis", "excel", "tableau", "power bi",
    "linux", "rest api", "graphql", "mongodb", "postgresql", "mysql",
    "agile", "scrum", "ci/cd", "tensorflow", "pytorch", "pandas", "numpy",
]

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s.-]?)?(\(?\d{2,4}\)?[\s.-]?){2,4}\d{3,4}")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w-]+", re.IGNORECASE)
DATE_RANGE_RE = re.compile(
    r"(19|20)\d{2}\s*[-–to]+\s*((19|20)\d{2}|present|current)", re.IGNORECASE
)
BULLET_RE = re.compile(r"^[\s]*[•\-\*▪●○]\s+", re.MULTILINE)
NUMBER_RE = re.compile(r"\b\d+%?\b")

STOPWORDS = set(
    "a an the and or for of to in on with at by from is are was were be been "
    "this that these those as it its into over under more most very you your "
    "we our looking required required. strong skills experience years team "
    "ability able work working environment role position responsibilities "
    "including across various other strong communication required will".split()
)


# ---------------------------------------------------------------------------
# Helper checks
# ---------------------------------------------------------------------------

def _find_section(text_lower: str, keywords: list[str]) -> bool:
    return any(kw in text_lower for kw in keywords)


def _count_occurrences(text_lower: str, terms: list[str]) -> dict:
    counts = {}
    for term in terms:
        n = text_lower.count(term)
        if n > 0:
            counts[term] = n
    return counts


def _detect_skills(text_lower: str, skills: list[str]) -> list[str]:
    """
    Detect skills using word-boundary matching so 'java' doesn't match inside
    'javascript', etc. Skills containing special characters (c++, c#, node.js)
    fall back to substring matching since \\b doesn't work cleanly around symbols.
    """
    found = []
    for skill in skills:
        if re.search(r"[+#.]", skill):
            if skill in text_lower:
                found.append(skill)
        else:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text_lower):
                found.append(skill)
    return found


def _extract_keywords(text_lower: str) -> set:
    words = re.findall(r"[a-zA-Z][a-zA-Z+#-]*[a-zA-Z0-9]|[a-zA-Z]", text_lower)
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def analyze_resume(resume_text: str, job_description: str = "", api_key: str = None) -> dict:
    """
    Analyzes resume_text using local rule-based heuristics.
    `api_key` is accepted but ignored (kept for compatibility with app.py).
    Returns a dict matching the same schema the UI expects.
    """
    text = resume_text
    text_lower = text.lower()
    word_count = len(text.split())

    strengths = []
    weaknesses = []
    actionable_improvements = []
    score = 100  # start at 100, deduct for issues found

    # ---- Contact info ----
    has_email = bool(EMAIL_RE.search(text))
    has_phone = bool(PHONE_RE.search(text))
    has_linkedin = bool(LINKEDIN_RE.search(text))

    contact_notes = []
    if has_email:
        contact_notes.append("Email found.")
    else:
        contact_notes.append("No email address detected.")
        weaknesses.append("No email address found — recruiters need a way to contact you.")
        actionable_improvements.append("Add a professional email address near the top of your resume.")
        score -= 10

    if has_phone:
        contact_notes.append("Phone number found.")
    else:
        contact_notes.append("No phone number detected.")
        score -= 3

    if has_linkedin:
        contact_notes.append("LinkedIn profile found.")
    else:
        contact_notes.append("No LinkedIn URL detected.")
        actionable_improvements.append("Add a link to your LinkedIn profile.")
        score -= 2

    contact_feedback = " ".join(contact_notes)
    if has_email and has_phone:
        strengths.append("Contact information is present and easy to find.")

    # ---- Section detection ----
    section_feedback = {"contact_info": contact_feedback}
    found_sections = {}

    for key, keywords in SECTION_KEYWORDS.items():
        found = _find_section(text_lower, keywords)
        found_sections[key] = found

    if found_sections.get("summary_objective"):
        section_feedback["summary_objective"] = "A summary/objective section was found. Make sure it's tailored to the specific role you're applying for."
    else:
        section_feedback["summary_objective"] = "No summary or objective section detected. Consider adding a 2-3 line professional summary at the top."
        actionable_improvements.append("Add a brief professional summary (2-3 sentences) at the top highlighting your strongest qualifications.")
        score -= 5

    if found_sections.get("work_experience"):
        strengths.append("Work experience section is present.")
        section_feedback["work_experience"] = "Work experience section detected."
    else:
        weaknesses.append("No clearly labeled work experience section found.")
        section_feedback["work_experience"] = "Could not clearly detect a work experience section. Make sure it's clearly labeled (e.g. 'Work Experience' or 'Professional Experience')."
        score -= 15

    if found_sections.get("skills"):
        strengths.append("Skills section is present.")
        section_feedback["skills"] = "Skills section detected."
    else:
        weaknesses.append("No clearly labeled skills section found.")
        section_feedback["skills"] = "No dedicated skills section detected. A clear skills list helps both recruiters and ATS systems quickly see your qualifications."
        actionable_improvements.append("Add a dedicated 'Skills' section listing your key technical and soft skills.")
        score -= 8

    if found_sections.get("education"):
        section_feedback["education"] = "Education section detected."
    else:
        section_feedback["education"] = "No education section detected. If you have relevant education, make sure it's clearly labeled."
        score -= 5

    # ---- Action verbs vs weak phrases ----
    action_verb_hits = _count_occurrences(text_lower, ACTION_VERBS)
    weak_phrase_hits = _count_occurrences(text_lower, WEAK_PHRASES)

    total_action_verbs = sum(action_verb_hits.values())
    total_weak_phrases = sum(weak_phrase_hits.values())

    if total_action_verbs >= 5:
        strengths.append(f"Good use of strong action verbs (found {total_action_verbs} instances, e.g. {', '.join(list(action_verb_hits.keys())[:5])}).")
    else:
        weaknesses.append("Limited use of strong action verbs to describe accomplishments.")
        actionable_improvements.append(
            "Start bullet points with strong action verbs like 'led', 'built', 'improved', 'launched' instead of passive phrasing."
        )
        score -= 8

    if total_weak_phrases > 0:
        weaknesses.append(f"Found {total_weak_phrases} instance(s) of weak/passive phrasing (e.g. '{list(weak_phrase_hits.keys())[0]}').")
        actionable_improvements.append(
            "Replace passive phrases like 'responsible for' or 'worked on' with direct action verbs that show ownership and impact."
        )
        score -= 5

    # ---- Quantified achievements ----
    numbers_found = NUMBER_RE.findall(text)
    if len(numbers_found) >= 3:
        strengths.append(f"Resume includes quantified results (found {len(numbers_found)} numbers/metrics) — this is great for showing measurable impact.")
    else:
        weaknesses.append("Few or no quantified achievements (numbers, percentages, metrics) found.")
        actionable_improvements.append(
            "Quantify your achievements where possible, e.g. 'increased sales by 20%' or 'managed a team of 5'."
        )
        score -= 10

    # ---- Bullet points / formatting ----
    bullet_count = len(BULLET_RE.findall(text))
    if bullet_count >= 3:
        strengths.append("Resume uses bullet points, which improves readability and ATS parsing.")
    else:
        weaknesses.append("Few or no bullet points detected — content may be in dense paragraphs.")
        actionable_improvements.append("Format your experience and skills as bullet points rather than paragraphs for better readability.")
        score -= 5

    # ---- Date ranges (employment history clarity) ----
    has_date_ranges = bool(DATE_RANGE_RE.search(text))
    if has_date_ranges:
        strengths.append("Clear date ranges found for work history/education.")
    else:
        weaknesses.append("No clear date ranges (e.g. '2020 - 2023') detected for work or education entries.")
        score -= 5

    # ---- Length check ----
    if word_count < 150:
        weaknesses.append(f"Resume seems very short ({word_count} words) — may be missing detail.")
        actionable_improvements.append("Expand on your experience with more detail — aim for at least 300-600 words for a 1-page resume.")
        score -= 10
    elif word_count > 1200:
        weaknesses.append(f"Resume is quite long ({word_count} words) — consider trimming to keep it concise.")
        actionable_improvements.append("Trim less relevant content — most resumes should fit on 1-2 pages.")
        score -= 5
    else:
        strengths.append(f"Resume length ({word_count} words) is in a reasonable range.")

    formatting_notes = []
    formatting_notes.append(f"Word count: {word_count}.")
    formatting_notes.append(f"Bullet points detected: {bullet_count}.")
    formatting_notes.append("Date ranges " + ("found." if has_date_ranges else "not clearly found."))
    section_feedback["formatting"] = " ".join(formatting_notes)

    # ---- Tech skill detection ----
    detected_skills = _detect_skills(text_lower, COMMON_TECH_SKILLS)
    keyword_suggestions = []

    # ---- Job description match (optional) ----
    job_match_score = None
    job_match_notes = None

    if job_description and job_description.strip():
        jd_lower = job_description.lower()
        jd_keywords = _extract_keywords(jd_lower)
        resume_keywords = _extract_keywords(text_lower)

        overlap = jd_keywords & resume_keywords
        missing = jd_keywords - resume_keywords

        # Focus missing-keyword suggestions on meaningful, longer terms
        meaningful_missing = sorted(
            [w for w in missing if len(w) > 3],
            key=lambda w: jd_lower.count(w),
            reverse=True,
        )[:12]

        if jd_keywords:
            match_ratio = len(overlap) / len(jd_keywords)
        else:
            match_ratio = 0

        job_match_score = round(min(max(match_ratio * 100, 0), 100))
        job_match_notes = (
            f"Your resume shares {len(overlap)} of {len(jd_keywords)} significant keyword(s) "
            f"found in the job description (~{job_match_score}% overlap). "
        )
        if meaningful_missing:
            job_match_notes += "Consider addressing these terms from the job description if they genuinely apply to your background: " + ", ".join(meaningful_missing[:8]) + "."
            keyword_suggestions = meaningful_missing[:10]
        else:
            job_match_notes += "Good coverage of the job description's key terms."
    else:
        # No JD provided — suggest generic in-demand skills not already present
        keyword_suggestions = [s for s in COMMON_TECH_SKILLS if s not in detected_skills][:8]

    if detected_skills:
        strengths.append(f"Detected {len(detected_skills)} recognizable technical skill(s): {', '.join(detected_skills[:8])}.")

    # ---- Clamp score ----
    score = max(0, min(100, score))

    # ---- Build summary ----
    if score >= 85:
        tier = "strong"
    elif score >= 65:
        tier = "solid but improvable"
    elif score >= 45:
        tier = "needs meaningful work"
    else:
        tier = "needs significant revision"

    summary = (
        f"This resume scored {score}/100, which is {tier}. "
        f"It has {len(strengths)} notable strength(s) and {len(weaknesses)} area(s) to improve. "
        f"This analysis is based on automated structural and keyword checks, not human judgment — "
        f"use it as a starting point, not a final verdict."
    )

    # Ensure lists aren't empty (UI expects iterables)
    if not strengths:
        strengths = ["No major strengths detected by the automated checks — consider a full rewrite using the suggestions below."]
    if not weaknesses:
        weaknesses = ["No major issues detected by the automated checks. Nice work."]
    if not actionable_improvements:
        actionable_improvements = ["Keep refining bullet points with metrics and strong action verbs."]

    return {
        "overall_score": score,
        "summary": summary,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "section_feedback": section_feedback,
        "keyword_suggestions": keyword_suggestions,
        "actionable_improvements": actionable_improvements,
        "job_match_score": job_match_score,
        "job_match_notes": job_match_notes,
    }
