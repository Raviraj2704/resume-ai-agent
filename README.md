# Resume ATS Analyzer

An AI-powered resume analyzer that gives instant ATS (Applicant Tracking System) 
scoring, keyword matching against job descriptions, and actionable improvement 
suggestions — built with FastAPI and Groq's Llama 3.3 70B model.

## Features
- 🎯 Instant ATS score (0-100) with animated circular gauge
- 🔍 Strengths, weaknesses, and missing keyword breakdown
- 📋 AI-generated final verdict and suitable job role suggestions
- 📄 Job description matching — paste a JD and see your match %
- 📊 Resume history — track past analyses over time
- ⚖️ Compare two resumes side-by-side
- 🔐 User authentication with secure password hashing
- 📥 Downloadable PDF reports
- 🔗 Shareable public report links

## Tech Stack
- **Backend:** FastAPI, Python
- **AI:** Groq API (Llama 3.3-70B)
- **Frontend:** HTML, CSS, JavaScript (drag & drop upload, animated gauge)
- **Database:** SQLite
- **Auth:** Passlib (bcrypt) + itsdangerous session tokens

## Setup
1. Clone the repo
2. `pip install -r requirements.txt`
3. Create a `.env` file with:
