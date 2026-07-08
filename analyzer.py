from dotenv import load_dotenv
load_dotenv()

import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_resume(resume_text: str) -> dict:
    prompt = f"""
You are an expert ATS (Applicant Tracking System) resume analyzer.

Analyze the resume below and respond with ONLY valid JSON — no markdown,
no code fences, no explanations before or after. Use exactly this structure:

{{
  "ats_score": <integer 0-100>,
  "strengths": ["short strength", "..."],
  "weaknesses": ["short weakness", "..."],
  "missing_keywords": ["keyword", "..."],
  "suggestions": ["short actionable suggestion", "..."],
  "suitable_roles": ["job title", "..."],
  "verdict": "one or two sentence final verdict"
}}

Resume:
\"\"\"{resume_text}\"\"\"
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "", 1).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {
            "ats_score": 0,
            "strengths": [],
            "weaknesses": [],
            "missing_keywords": [],
            "suggestions": [],
            "suitable_roles": [],
            "verdict": "Could not parse AI response. Please try again."
        }

    return data
def analyze_resume_with_jd(resume_text: str, jd_text: str) -> dict:
    prompt = f"""
You are an expert ATS resume analyzer comparing a resume against a specific job description.

Respond with ONLY valid JSON, no markdown, no extra text, using exactly this structure:

{{
  "ats_score": <integer 0-100>,
  "jd_match_percent": <integer 0-100, how well the resume matches THIS job description>,
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "missing_keywords": ["keyword from the JD not found in the resume", "..."],
  "suggestions": ["...", "..."],
  "suitable_roles": ["...", "..."],
  "verdict": "one or two sentence final verdict"
}}

Job Description:
\"\"\"{jd_text}\"\"\"

Resume:
\"\"\"{resume_text}\"\"\"
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").replace("json", "", 1).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "ats_score": 0, "jd_match_percent": 0,
            "strengths": [], "weaknesses": [], "missing_keywords": [],
            "suggestions": [], "suitable_roles": [],
            "verdict": "Could not parse AI response."
        }