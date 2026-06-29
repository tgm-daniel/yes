import json
import os
import random

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import QuizSession

BASE_DIR = os.getcwd()

app = FastAPI(title="MultiQuiz")
Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

with open(os.path.join(BASE_DIR, "profiles.json")) as f:
    PROFILES = json.load(f)


TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")


def _render(name: str, **kwargs) -> str:
    path = os.path.join(TEMPLATES_DIR, name)
    if not os.path.exists(path):
        raise RuntimeError(f"Template not found: {path} (BASE_DIR={BASE_DIR})")
    with open(path, encoding="utf-8") as f:
        html = f.read()
    for k, v in kwargs.items():
        html = html.replace("{{ " + k + " }}", v)
        html = html.replace("{{ " + k + "|safe }}", v)
    return html


def get_profile(profile_id: str) -> dict:
    if profile_id not in PROFILES:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    return PROFILES[profile_id]


def get_profile_questions(profile_id: str) -> list:
    return get_profile(profile_id)["questions"]


def get_result_tier(percentage: float) -> str:
    if percentage >= 80:
        return "high"
    elif percentage >= 50:
        return "mid"
    return "low"


# ---- PÁGINAS ----

@app.get("/", response_class=HTMLResponse)
async def login_page():
    return HTMLResponse(_render("index.html"))


@app.get("/start/{profile_id}")
async def start_redirect(profile_id: str):
    if profile_id not in PROFILES:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    db = next(get_db())
    try:
        questions = get_profile_questions(profile_id)
        session = QuizSession(profile_id=profile_id)
        random.shuffle(questions)
        session.question_order = [q["id"] for q in questions]
        db.add(session)
        db.commit()
        db.refresh(session)
        return RedirectResponse(url=f"/quiz/{session.id}", status_code=302)
    finally:
        db.close()


@app.get("/quiz/{session_id}", response_class=HTMLResponse)
async def quiz_page(session_id: str):
    db = next(get_db())
    try:
        session = db.query(QuizSession).filter(QuizSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        profile = get_profile(session.profile_id)
        return HTMLResponse(_render("quiz.html",
            pistas_json=json.dumps(profile["pistas"]),
            carinho_json=json.dumps(profile["carinhoMessages"]),
            emoji=profile["emoji"],
        ))
    finally:
        db.close()


@app.get("/resultado/{session_id}", response_class=HTMLResponse)
async def result_page(session_id: str):
    return HTMLResponse(_render("result.html"))


# ---- API ----

@app.post("/api/login")
def api_login(body: dict, db: Session = Depends(get_db)):
    name = body.get("name", "").strip().lower()
    password = body.get("password", "")

    profile = PROFILES.get(name)
    if not profile or profile["password"] != password:
        raise HTTPException(status_code=401, detail="Nome ou senha incorretos")

    return {
        "profile_id": name,
        "title": profile["title"],
        "subtitle": profile["subtitle"],
        "emoji": profile["emoji"],
    }


@app.post("/api/start")
def api_start(body: dict = {}, db: Session = Depends(get_db)):
    profile_id = body.get("profile_id", "vanessa")
    get_profile(profile_id)
    questions = get_profile_questions(profile_id)
    session = QuizSession(profile_id=profile_id)
    random.shuffle(questions)
    session.question_order = [q["id"] for q in questions]
    db.add(session)
    db.commit()
    db.refresh(session)
    return {
        "session_id": session.id,
        "total_questions": len(questions),
    }


@app.get("/api/question/{session_id}")
def api_question(session_id: str, db: Session = Depends(get_db)):
    session = db.query(QuizSession).filter(QuizSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    questions = get_profile_questions(session.profile_id)
    total = len(questions)

    if session.finished:
        return {"finished": True, "score": session.score, "total": total}

    order = session.question_order or [q["id"] for q in questions]
    if session.current_question >= len(order):
        session.finished = True
        db.commit()
        return {"finished": True, "score": session.score, "total": total}

    qid = order[session.current_question]
    q = next(q for q in questions if q["id"] == qid)

    return {
        "question_id": q["id"],
        "question": q["question"],
        "options": q["options"],
        "current": session.current_question + 1,
        "total": total,
        "finished": False,
    }


@app.post("/api/answer/{session_id}")
def api_answer(session_id: str, body: dict, db: Session = Depends(get_db)):
    session = db.query(QuizSession).filter(QuizSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    questions = get_profile_questions(session.profile_id)
    total = len(questions)

    if session.finished:
        return {"finished": True, "score": session.score, "total": total}

    selected = body.get("answer")
    order = session.question_order or [q["id"] for q in questions]
    qid = order[session.current_question]
    q = next(q for q in questions if q["id"] == qid)

    correct = selected == q["correct"]
    if correct:
        session.score += 1

    answers = session.answers or []
    answers.append({
        "question_id": q["id"],
        "selected": selected,
        "correct": correct,
    })
    session.answers = answers
    session.current_question += 1

    if session.current_question >= len(order):
        session.finished = True

    db.commit()

    return {
        "correct": correct,
        "correct_answer": q["correct"],
        "fun_fact": q["fun_fact"],
        "score": session.score,
        "current": session.current_question,
        "total": total,
        "finished": session.finished,
        "is_last": session.finished,
    }


@app.get("/api/result/{session_id}")
def api_result(session_id: str, db: Session = Depends(get_db)):
    session = db.query(QuizSession).filter(QuizSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    profile = get_profile(session.profile_id)
    questions = get_profile_questions(session.profile_id)
    total = len(questions)
    score = session.score
    answers = session.answers or []
    percentage = (score / total) * 100

    details = []
    for ans in answers:
        q = next(q for q in questions if q["id"] == ans["question_id"])
        details.append({
            "question": q["question"],
            "selected": q["options"][ans["selected"]],
            "correct": q["options"][q["correct"]],
            "was_correct": ans["correct"],
            "fun_fact": q["fun_fact"],
        })

    tier = get_result_tier(percentage)
    tier_data = profile["resultMessages"][tier]

    return {
        "score": score,
        "total": total,
        "percentage": percentage,
        "message": tier_data["message"],
        "final_question": tier_data["final_question"],
        "emoji": tier_data["emoji"],
        "title": tier_data["title"],
        "details": details,
        "session_id": session_id,
        "instagram": profile["instagram"],
        "yesMessage": profile["yesMessage"],
        "yesFooter": profile["yesFooter"],
        "noMessage": profile["noMessage"],
        "noFooter": profile["noFooter"],
        "profile_emoji": profile["emoji"],
    }
