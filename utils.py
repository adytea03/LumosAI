from io import BytesIO
from collections import Counter, OrderedDict
import re

from docx import Document
from pypdf import PdfReader


SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "c", "c++", "sql", "mysql", "postgresql",
    "mongodb", "html", "css", "react", "node", "node.js", "flask", "django", "fastapi",
    "api", "rest api", "git", "github", "docker", "kubernetes", "aws", "azure", "gcp",
    "linux", "testing", "debugging", "machine learning", "deep learning", "data analysis",
    "pandas", "numpy", "statistics", "excel", "power bi", "tableau", "communication",
    "teamwork", "problem solving", "leadership", "project management", "nlp", "cloud",
    "ui", "ux", "figma", "spring", "hibernate", "jdbc", "data structures", "algorithms"
]

ROLE_KEYWORDS = {
    "Software Engineer": ["software engineer", "developer", "programmer", "backend", "frontend", "full stack"],
    "Data Scientist": ["data scientist", "machine learning", "deep learning", "nlp", "data science"],
    "Data Analyst": ["data analyst", "analytics", "business intelligence", "dashboard", "excel", "power bi"],
    "Web Developer": ["web developer", "frontend", "html", "css", "javascript", "react"],
    "Mobile App Developer": ["android", "ios", "mobile app", "flutter", "kotlin", "swift"],
    "DevOps Engineer": ["devops", "docker", "kubernetes", "ci/cd", "aws", "linux", "cloud"],
    "Product Manager": ["product manager", "roadmap", "stakeholder", "product strategy", "user research"],
    "UI/UX Designer": ["ui ux", "ux designer", "ui designer", "figma", "wireframe", "prototype"],
    "Business Analyst": ["business analyst", "requirements", "stakeholder", "process analysis"],
    "HR Executive": ["human resources", "hr", "recruiter", "talent acquisition"]
}

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "about", "your", "you",
    "our", "their", "they", "them", "are", "was", "were", "will", "would", "shall",
    "could", "should", "have", "has", "had", "can", "may", "might", "been", "being",
    "job", "role", "responsibilities", "required", "requirements", "skills", "experience",
    "using", "based", "company", "resume", "description", "candidate", "candidates",
    "project", "projects", "work", "working", "team", "teams", "develop", "development",
    "design", "implement", "implementation", "manage", "management", "support", "solutions"
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def extract_text_from_upload(upload):
    if not upload or not getattr(upload, "filename", ""):
        return ""

    filename = upload.filename.lower()
    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""

    try:
        upload.stream.seek(0)
        file_bytes = upload.read()

        if ext == "txt":
            return normalize_text(file_bytes.decode("utf-8", errors="ignore"))

        if ext == "docx":
            doc = Document(BytesIO(file_bytes))
            text = "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())
            return normalize_text(text)

        if ext == "pdf":
            reader = PdfReader(BytesIO(file_bytes))
            pages = []
            for page in reader.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    pages.append(page_text)
            return normalize_text("\n".join(pages))

    except Exception:
        return ""

    return ""


def dedupe_preserve_order(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def extract_keywords(text: str):
    lower_text = (text or "").lower()
    found = []

    for keyword in SKILL_KEYWORDS:
        pattern = r"(?<!\w)" + re.escape(keyword.lower()) + r"(?!\w)"
        if re.search(pattern, lower_text):
            found.append(keyword)

    return dedupe_preserve_order(found)


def top_frequent_terms(text: str, limit: int = 8):
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9\+\#\.]+", (text or "").lower())
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 2]

    if not tokens:
        return []

    counts = Counter(tokens)
    return [word for word, _ in counts.most_common(limit)]


def infer_role(text: str) -> str:
    lower_text = (text or "").lower()

    for role, keywords in ROLE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in lower_text:
                return role

    return "the role"


def build_question_pools(role, jd_keywords, resume_keywords, company_keywords):
    common = [k for k in jd_keywords if k in resume_keywords]
    gaps = [k for k in jd_keywords if k not in resume_keywords]

    technical = []
    hr = []
    behavioral = []
    manager = []

    if common:
        for keyword in common[:5]:
            technical.append(f"Tell me about a project where you used {keyword}.")
            technical.append(f"How have you applied {keyword} in a real-world situation?")
    else:
        technical.append(f"What makes you a strong fit for {role}?")
        technical.append(f"How would you prepare for the core responsibilities of {role}?")

    if gaps:
        for keyword in gaps[:5]:
            technical.append(f"The job description highlights {keyword}. How would you close that gap?")
            technical.append(f"What is your current level of comfort with {keyword}?")

    extra_terms = top_frequent_terms(" ".join(jd_keywords), 5)
    for term in extra_terms:
        technical.append(f"Can you explain {term} in simple words with an example?")

    hr.extend([
        f"Tell me about yourself and why you are interested in {role}.",
        "What are your biggest strengths for this position?",
        "What is one weakness you are actively working on?",
        "Why should we hire you for this role?"
    ])

    if company_keywords:
        hr.append("Why do you want to work for this company?")
        hr.append(f"What interests you about the company’s focus on {company_keywords[0]}?")
    else:
        hr.append("Why are you interested in this company?")

    behavioral.extend([
        "Tell me about a time you solved a difficult problem under pressure.",
        "Describe a situation where you had to learn something quickly.",
        "How do you handle conflict within a team?",
        "Tell me about a mistake you made and what you learned from it.",
        "How do you stay organized when you have multiple deadlines?"
    ])

    manager.extend([
        "How do you prioritize tasks when everything feels urgent?",
        "How do you keep your manager updated on progress and blockers?",
        "How do you react to feedback that you do not fully agree with?",
        "What would you do if project priorities changed suddenly?",
        "How would you work independently without constant supervision?"
    ])

    if company_keywords:
        manager.append(f"How would you align your work with a company that focuses on {company_keywords[0]}?")

    return OrderedDict([
        ("Technical", dedupe_preserve_order(technical)),
        ("HR", dedupe_preserve_order(hr)),
        ("Behavioral", dedupe_preserve_order(behavioral)),
        ("Manager", dedupe_preserve_order(manager))
    ]), common, gaps


def pick_balanced_questions(pools, total_count):
    categories = list(pools.keys())
    if not categories or total_count <= 0:
        return OrderedDict()

    base = total_count // len(categories)
    rem = total_count % len(categories)

    quotas = {}
    for i, cat in enumerate(categories):
        quotas[cat] = base + (1 if i < rem else 0)

    selected = OrderedDict()

    for cat in categories:
        questions = pools[cat]
        take = min(quotas[cat], len(questions))
        selected[cat] = questions[:take]

    current_total = sum(len(v) for v in selected.values())
    if current_total < total_count:
        remaining = total_count - current_total
        for cat in categories:
            if remaining == 0:
                break
            already = set(selected[cat])
            for q in pools[cat]:
                if q not in already:
                    selected[cat].append(q)
                    already.add(q)
                    remaining -= 1
                    if remaining == 0:
                        break

    for cat in list(selected.keys()):
        if not selected[cat]:
            del selected[cat]

    return selected


def generate_interview_pack(jd_text, resume_text, company_text, question_count=9):
    try:
        question_count = int(question_count)
    except (TypeError, ValueError):
        question_count = 9

    if question_count < 1:
        question_count = 1

    jd_keywords = extract_keywords(jd_text)
    resume_keywords = extract_keywords(resume_text)
    company_keywords = extract_keywords(company_text) if company_text and company_text.strip() else []

    if not jd_keywords:
        jd_keywords = top_frequent_terms(jd_text, 8)

    if not resume_keywords:
        resume_keywords = top_frequent_terms(resume_text, 8)

    role = infer_role(f"{jd_text} {company_text}")

    pools, common, gaps = build_question_pools(
        role=role,
        jd_keywords=jd_keywords,
        resume_keywords=resume_keywords,
        company_keywords=company_keywords
    )

    questions_by_category = pick_balanced_questions(pools, question_count)

    overlap = len(common)
    jd_total = max(len(jd_keywords), 1)
    resume_total = max(len(resume_keywords), 1)

    relevance_score = round(
        min(
            98,
            max(
                35,
                (overlap / jd_total) * 60 + (overlap / resume_total) * 25 + (5 if company_keywords else 0) + 10
            )
        )
    )

    return {
        "role": role,
        "score": relevance_score,
        "jd_keywords": jd_keywords[:10],
        "resume_keywords": resume_keywords[:10],
        "company_keywords": company_keywords[:8],
        "common_keywords": common[:10],
        "gap_keywords": gaps[:10],
        "questions_by_category": questions_by_category
    }