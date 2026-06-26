import random

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import QuizSession
from questions import QUIZ_QUESTIONS

app = FastAPI(title="Nosso Quiz")

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/index.html") as f:
        return HTMLResponse(f.read())


@app.get("/quiz/{session_id}", response_class=HTMLResponse)
async def quiz_page(session_id: str):
    with open("templates/quiz.html") as f:
        html = f.read()
    return HTMLResponse(html)


@app.get("/resultado/{session_id}", response_class=HTMLResponse)
async def result_page(session_id: str):
    with open("templates/result.html") as f:
        html = f.read()
    return HTMLResponse(html)


@app.post("/api/start")
def start_quiz(db: Session = Depends(get_db)):
    session = QuizSession()
    random.shuffle(QUIZ_QUESTIONS)
    session.question_order = [q["id"] for q in QUIZ_QUESTIONS]
    db.add(session)
    db.commit()
    db.refresh(session)
    return {
        "session_id": session.id,
        "total_questions": len(QUIZ_QUESTIONS),
    }


@app.get("/api/question/{session_id}")
def get_question(session_id: str, db: Session = Depends(get_db)):
    session = db.query(QuizSession).filter(QuizSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    if session.finished:
        return {"finished": True, "score": session.score, "total": len(QUIZ_QUESTIONS)}

    question_order = session.question_order or [q["id"] for q in QUIZ_QUESTIONS]
    if session.current_question >= len(question_order):
        session.finished = True
        session.completed_at = None
        db.commit()
        return {"finished": True, "score": session.score, "total": len(QUIZ_QUESTIONS)}

    question_id = question_order[session.current_question]
    question = next(q for q in QUIZ_QUESTIONS if q["id"] == question_id)

    return {
        "question_id": question["id"],
        "question": question["question"],
        "options": question["options"],
        "current": session.current_question + 1,
        "total": len(QUIZ_QUESTIONS),
        "finished": False,
    }


@app.post("/api/answer/{session_id}")
def answer_question(
    session_id: str,
    body: dict,
    db: Session = Depends(get_db),
):
    session = db.query(QuizSession).filter(QuizSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    if session.finished:
        return {"finished": True, "score": session.score, "total": len(QUIZ_QUESTIONS)}

    selected = body.get("answer")
    question_order = session.question_order or [q["id"] for q in QUIZ_QUESTIONS]
    question_id = question_order[session.current_question]
    question = next(q for q in QUIZ_QUESTIONS if q["id"] == question_id)

    correct = selected == question["correct"]
    if correct:
        session.score += 1

    answers = session.answers or []
    answers.append({
        "question_id": question["id"],
        "selected": selected,
        "correct": correct,
    })
    session.answers = answers
    session.current_question += 1

    if session.current_question >= len(question_order):
        session.finished = True
        session.completed_at = None

    db.commit()

    is_last = session.finished

    return {
        "correct": correct,
        "correct_answer": question["correct"],
        "fun_fact": question["fun_fact"],
        "score": session.score,
        "current": session.current_question,
        "total": len(QUIZ_QUESTIONS),
        "finished": is_last,
        "is_last": is_last,
    }


@app.get("/api/result/{session_id}")
def get_result(session_id: str, db: Session = Depends(get_db)):
    session = db.query(QuizSession).filter(QuizSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    total = len(QUIZ_QUESTIONS)
    score = session.score
    answers = session.answers or []
    percentage = (score / total) * 100

    details = []
    for ans in answers:
        q = next(q for q in QUIZ_QUESTIONS if q["id"] == ans["question_id"])
        details.append({
            "question": q["question"],
            "selected": q["options"][ans["selected"]],
            "correct": q["options"][q["correct"]],
            "was_correct": ans["correct"],
            "fun_fact": q["fun_fact"],
        })

    if percentage >= 80:
        message = (
            "Você me conhece mais do que ninguém! 💕 "
            "A gente sempre teve algo especial, e você acabou de provar que "
            "nossa conexão é única. Será que a gente não merece uma segunda chance?"
        )
        final_question = "Você quer voltar comigo? 💍"
    elif percentage >= 50:
        message = (
            "Você lembra de bastante coisa! 😊 "
            "Nossa história foi linda, e mesmo com o tempo, ainda guardamos "
            "memórias especiais. Que tal a gente criar novas?"
        )
        final_question = "Você quer tentar de novo comigo? 🌟"
    else:
        message = (
            "Que vergonha, hein? 😂 Brincadeira! "
            "O importante é que a gente tem histórias pra contar. "
            "E se a gente escrever um novo capítulo juntos?"
        )
        final_question = "Vamos dar um jeito de voltar? 😅"

    return {
        "score": score,
        "total": total,
        "percentage": percentage,
        "message": message,
        "final_question": final_question,
        "details": details,
        "session_id": session_id,
    }
