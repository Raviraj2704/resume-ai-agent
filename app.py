import os
import shutil

from fastapi import FastAPI, UploadFile, File, Form, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from parser import extract_text_from_pdf
from analyzer import analyze_resume, analyze_resume_with_jd
import db
import auth

app = FastAPI()
db.init_db()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------- Helper: get logged-in user from cookie ----------

def get_current_user(request: Request):
    token = request.cookies.get("session")
    if not token:
        return None
    user_id = auth.read_session_token(token)
    if not user_id:
        return None
    return db.get_user_by_id(user_id)


# ---------- Auth routes ----------

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse(request, "signup.html", {"error": None})


@app.post("/signup")
async def signup(email: str = Form(...), password: str = Form(...)):
    if db.get_user_by_email(email):
        return RedirectResponse("/signup?error=exists", status_code=303)
    db.create_user(email, auth.hash_password(password))
    return RedirectResponse("/login", status_code=303)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"error": None})


@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    user = db.get_user_by_email(email)
    if not user or not auth.verify_password(password, user["password_hash"]):
        return RedirectResponse("/login?error=invalid", status_code=303)

    token = auth.create_session_token(user["id"])
    response = RedirectResponse("/", status_code=303)
    response.set_cookie("session", token, httponly=True, max_age=60 * 60 * 24 * 7)
    return response


@app.get("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("session")
    return response


# ---------- Main pages ----------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(request, "index.html", {"user": user})


@app.post("/upload")
async def upload_resume(request: Request, file: UploadFile = File(...)):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "Not logged in"}, status_code=401)

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    resume_text = extract_text_from_pdf(file_path)
    analysis = analyze_resume(resume_text)

    public_id = db.save_resume(user["id"], file.filename, analysis)

    return JSONResponse({
        "message": "Resume analyzed successfully!",
        "filename": file.filename,
        "public_id": public_id,
        "ats_score": analysis.get("ats_score", 0),
        "strengths": analysis.get("strengths", []),
        "weaknesses": analysis.get("weaknesses", []),
        "missing_keywords": analysis.get("missing_keywords", []),
        "suggestions": analysis.get("suggestions", []),
        "suitable_roles": analysis.get("suitable_roles", []),
        "verdict": analysis.get("verdict", "")
    })


# ---------- History ----------

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    resumes = db.get_history(user["id"])
    return templates.TemplateResponse(request, "history.html", {"user": user, "resumes": resumes})


# ---------- Shareable report link ----------

@app.get("/report/{public_id}", response_class=HTMLResponse)
async def report_page(request: Request, public_id: str):
    resume = db.get_resume_by_public_id(public_id)
    if not resume:
        return HTMLResponse("Report not found", status_code=404)
    import json
    analysis = json.loads(resume["analysis_json"])
    return templates.TemplateResponse(request, "report.html", {
        "filename": resume["filename"],
        "analysis": analysis
    })


# ---------- Compare two resumes ----------

@app.get("/compare", response_class=HTMLResponse)
async def compare_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(request, "compare.html", {"user": user})


@app.post("/compare")
async def compare_resumes(
    request: Request,
    file1: UploadFile = File(...),
    file2: UploadFile = File(...)
):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "Not logged in"}, status_code=401)

    path1 = os.path.join(UPLOAD_FOLDER, file1.filename)
    path2 = os.path.join(UPLOAD_FOLDER, file2.filename)

    with open(path1, "wb") as b1:
        shutil.copyfileobj(file1.file, b1)
    with open(path2, "wb") as b2:
        shutil.copyfileobj(file2.file, b2)

    text1 = extract_text_from_pdf(path1)
    text2 = extract_text_from_pdf(path2)

    analysis1 = analyze_resume(text1)
    analysis2 = analyze_resume(text2)

    return JSONResponse({
        "resume1": {"filename": file1.filename, **analysis1},
        "resume2": {"filename": file2.filename, **analysis2}
    })


# ---------- Job description matcher ----------

@app.post("/match-jd")
async def match_jd(
    request: Request,
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "Not logged in"}, status_code=401)

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    resume_text = extract_text_from_pdf(file_path)
    analysis = analyze_resume_with_jd(resume_text, job_description)

    public_id = db.save_resume(user["id"], file.filename, analysis)

    return JSONResponse({
        "filename": file.filename,
        "public_id": public_id,
        **analysis
    })