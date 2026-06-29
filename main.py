import json
import os
import random
import sys
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import QuizSession, LoginEvent

BASE_DIR = os.getcwd()

app = FastAPI(title="Quiz pra ti")
Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

PROFILES_PATH = os.path.join(BASE_DIR, "profiles.json")

def load_profiles():
    with open(PROFILES_PATH) as f:
        return json.load(f)

PROFILES = load_profiles()

ADMIN_USER = "ttt"
ADMIN_PASS = "sisrat"

GENERIC_QUESTIONS = [
    {"id": 1, "question": "Qual seria seu destino dos sonhos pra viajar?", "options": ["Paris — romance e charme", "Tóquio — tecnologia e cultura", "Nova York — cidade que nunca dorme", "Uma praia paradisíaca — sol e mar"], "correct": 3, "fun_fact": "Praia paradisíaca! Bora sonhar juntos 🏖️"},
    {"id": 2, "question": "O que mais te atrai em alguém?", "options": ["Humor que faz qualquer dia ficar leve", "Inteligência que prende a atenção", "Gentileza com todo mundo", "Confiança sem arrogância"], "correct": 0, "fun_fact": "Humor é o caminho mais curto pro coração 😄"},
    {"id": 3, "question": "Qual seu estilo musical favorito?", "options": ["Pop — pra cantar no chuveiro", "MPB — pra alma e dias cinzas", "Eletrônica — dançar até o chão", "Sertanejo — modão e coração na mão"], "correct": 1, "fun_fact": "MPB! Já temos playlist pra fazer juntos 🎵"},
    {"id": 4, "question": "O que você mais valoriza numa amizade?", "options": ["Lealdade — tamo junto até o fim", "Bom humor — rir até chorar", "Sinceridade — mesmo que doa", "Aventura — vamos fazer loucura juntos"], "correct": 2, "fun_fact": "Sinceridade é a base de tudo 💕"},
    {"id": 5, "question": "Fim de semana ideal pra você?", "options": ["Explorar um lugar novo", "Maratona de série com delivery", "Rolê com os amigos até altas horas", "Sofá, cobertor e um livro"], "correct": 0, "fun_fact": "Aventura e descoberta! A vida é curta 🌟"},
    {"id": 6, "question": "O que te faz sentir especial de verdade?", "options": ["Um elogio sincero do nada", "Uma surpresa inesperada", "Uma conversa profunda de madrugada", "Um gesto simples cheio de significado"], "correct": 3, "fun_fact": "São as pequenas coisas que constroem grandes sentimentos ✨"},
    {"id": 7, "question": "Qual seria seu date ideal?", "options": ["Jantar romântico à luz de velas", "Café gostoso com conversa boa", "Um piquenique no parque", "Algo espontâneo e sem roteiro"], "correct": 1, "fun_fact": "Café e conversa — melhor forma de começo ☕"},
    {"id": 8, "question": "O que te conquista de verdade?", "options": ["Presentes (sem julgamentos)", "Atenção genuína — lembrar dos detalhes", "Uma aventura radical", "Simplicidade — pequenas coisas"], "correct": 1, "fun_fact": "Atenção genuína — nada mais bonito 💝"},
    {"id": 9, "question": "Qual seu jeito de recarregar as energias?", "options": ["Uma soneca estratégica", "Um tempo sozinha com seus pensamentos", "Sair rodeada de gente", "Exercício — endorfina é tudo"], "correct": 0, "fun_fact": "Dormir é sempre uma boa ideia 😂"},
    {"id": 10, "question": "Se você fosse um emoji, qual seria?", "options": ["😎 — descolada e confiante", "🤗 — abraço e afeto", "🔥 — intensa e apaixonada", "🌙 — calma, misteriosa e sonhadora"], "correct": 0, "fun_fact": "😎 Descolada! Já tô imaginando nosso rolê 🚀"}
]

NEW_PROFILE_TEMPLATE = {
    "password": "senha123",
    "title": "",
    "subtitle": "vamos nos conhecer melhor :)",
    "emoji": "💕",
    "instagram": "@",
    "welcomeMessage": "Oiiii! Que bom que você está aqui! Vamos nos conhecer melhor? 💕",
    "yesMessage": "mal posso esperar pra te conhecer melhor. vai ser incrível!",
    "yesFooter": "💕 ansioso pelo nosso encontro",
    "noMessage": "tudo bem! a vida é sobre encontros e desencontros.",
    "noFooter": "se um dia mudar de ideia, é só chamar. 😊",
    "resultMessages": {
        "high": {"message": "Nossa compatibilidade é incrível! ✨ Parece que já nos entendemos. Que tal a gente descobrir se é verdade?", "final_question": "Você aceita sair comigo? 💕", "emoji": "🥰", "title": "Compatibilidade máxima! ✨"},
        "mid": {"message": "Já temos uma boa conexão! 😊 Ainda temos o que descobrir, e essa é a melhor parte.", "final_question": "Que tal a gente se conhecer melhor? 🌟", "emoji": "😊", "title": "Quase lá! 🌟"},
        "low": {"message": "Ainda temos o que descobrir um sobre o outro! 😂 E essa é a parte mais divertida.", "final_question": "Me dá uma chance de te conhecer? 😅", "emoji": "😂", "title": "Ainda temos o que descobrir 😂"}
    },
    "questions": GENERIC_QUESTIONS,
    "pistas": [
        ["primeiro encontro marcado", "um café bem quentinho", "e aquele frio na barriga ☕💕"],
        ["conversa boa e sincera", "risada solta e gostosa", "o melhor jeito de começar algo ✨"],
        ["um passeio no parque", "o vento no rosto", "e a descoberta de um novo sorriso 🌳💕"],
        ["noite estrelada", "planos pro futuro", "e a certeza de que tô no lugar certo 🌟💕"]
    ],
    "carinhoMessages": [
        "tudo bem, a gente mal se conhece! ainda dá tempo de descobrir 💕",
        "palpite errado, mas a intenção foi boa 😊",
        "imagina se a gente já soubesse tudo um do outro? não teria graça! ✨",
        "relaxa, o importante é a gente se conhecer de verdade 💗",
        "errar faz parte — e a melhor parte é aprender juntos 🍀"
    ]
}


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
        random.shuffle(questions)
        questions = questions[:10]
        session = QuizSession(profile_id=profile_id)
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
        welcome = profile.get("welcomeMessage", "")
        return HTMLResponse(_render("quiz.html",
            pistas_json=json.dumps(profile["pistas"]),
            carinho_json=json.dumps(profile["carinhoMessages"]),
            emoji=profile["emoji"],
            profile_id=session.profile_id,
            welcome_message=json.dumps(welcome),
        ))
    finally:
        db.close()


@app.get("/resultado/{session_id}", response_class=HTMLResponse)
async def result_page(session_id: str):
    return HTMLResponse(_render("result.html"))

@app.get("/retry/{session_id}", response_class=HTMLResponse)
async def retry_page(session_id: str):
    db = next(get_db())
    try:
        session = db.query(QuizSession).filter(QuizSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        profile = get_profile(session.profile_id)
        name = session.profile_id.capitalize()
        return HTMLResponse(_render("retry.html",
            profile_name=json.dumps(name),
            session_id=session.id,
            emoji=profile["emoji"],
        ))
    finally:
        db.close()


# ---- API ----

@app.post("/api/login")
def api_login(body: dict, request: Request, db: Session = Depends(get_db)):
    name = body.get("name", "").strip().lower()
    password = body.get("password", "")

    profile = PROFILES.get(name)
    if not profile or profile["password"] != password:
        raise HTTPException(status_code=401, detail="Nome ou senha incorretos")

    db.add(LoginEvent(profile_id=name))
    db.commit()

    # Check for incomplete session (user left mid-quiz)
    incomplete = db.query(QuizSession).filter(
        QuizSession.profile_id == name,
        QuizSession.finished == False,
        QuizSession.current_question > 0
    ).order_by(QuizSession.started_at.desc()).first()

    if incomplete:
        return {"incomplete": True, "session_id": incomplete.id}

    # Check for completed session
    completed = db.query(QuizSession).filter(
        QuizSession.profile_id == name,
        QuizSession.finished == True
    ).order_by(QuizSession.started_at.desc()).first()

    if completed:
        return {"already_completed": True, "session_id": completed.id, "profile_name": name.capitalize()}

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
    random.shuffle(questions)
    questions = questions[:10]
    session = QuizSession(profile_id=profile_id)
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
    order = session.question_order or [q["id"] for q in questions[:10]]
    total = len(order)

    if session.finished:
        return {"finished": True, "score": session.score, "total": total}

    if session.current_question >= len(order):
        session.finished = True
        session.completed_at = datetime.utcnow()
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
    order = session.question_order or [q["id"] for q in questions[:10]]
    total = len(order)

    if session.finished:
        return {"finished": True, "score": session.score, "total": total}

    selected = body.get("answer")
    qid = order[session.current_question]
    q = next(q for q in questions if q["id"] == qid)

    correct = selected == q["correct"]
    if correct:
        session.score += 1

    answers = list(session.answers or [])
    answers.append({
        "question_id": q["id"],
        "selected": selected,
        "correct": correct,
    })
    session.answers = answers
    session.current_question += 1

    if session.current_question >= len(order):
        session.finished = True
        session.completed_at = datetime.utcnow()

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


@app.post("/api/result/final/{session_id}")
def api_result_final(session_id: str, body: dict, db: Session = Depends(get_db)):
    session = db.query(QuizSession).filter(QuizSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    answer = body.get("answer")
    if answer not in ("yes", "no"):
        raise HTTPException(status_code=400, detail="Resposta inválida")
    answers = list(session.answers or [])
    # Remove previous final_answer if any, then append new one
    answers = [a for a in answers if a.get("type") != "final_answer"]
    answers.append({"type": "final_answer", "value": answer})
    session.answers = answers
    db.commit()
    return {"ok": True}


@app.get("/api/result/{session_id}")
def api_result(session_id: str, db: Session = Depends(get_db)):
    session = db.query(QuizSession).filter(QuizSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    profile = get_profile(session.profile_id)
    questions = get_profile_questions(session.profile_id)
    order = session.question_order or [q["id"] for q in questions[:10]]
    total = len(order)
    score = session.score
    answers = session.answers or []
    percentage = (score / total) * 100

    details = []
    final_answer = None
    for ans in answers:
        if ans.get("type") == "final_answer":
            final_answer = ans.get("value")
            continue
        q = next((q for q in questions if q["id"] == ans["question_id"]), None)
        if not q:
            continue
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
        "final_answer": final_answer,
        "already_completed": True,
    }




@app.post("/api/admin/results")
def admin_results(body: dict, db: Session = Depends(get_db)):
    if body.get("username") != ADMIN_USER or body.get("password") != ADMIN_PASS:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    sessions = db.query(QuizSession).order_by(QuizSession.started_at.desc()).all()
    result = []
    for s in sessions:
        profile = PROFILES.get(s.profile_id, {})
        questions = profile.get("questions", [])
        qmap = {q["id"]: q for q in questions}
        answers = s.answers or []
        ans_data = []
        for a in answers:
            if a.get("type") == "final_answer":
                continue
            q = qmap.get(a["question_id"], {})
            opts = q.get("options", [])
            ans_data.append({
                "question": q.get("question", "?"),
                "selected": opts[a["selected"]] if a["selected"] < len(opts) else "?",
                "correct_answer": opts[q["correct"]] if q.get("correct") is not None and q["correct"] < len(opts) else "?",
                "was_correct": a["correct"],
                "fun_fact": q.get("fun_fact", ""),
            })
        final_answer = None
        for a in (s.answers or []):
            if a.get("type") == "final_answer":
                final_answer = a.get("value")
                break
        result.append({
            "session_id": s.id,
            "profile_id": s.profile_id,
            "score": s.score,
            "total": len(s.question_order or questions),
            "started_at": str(s.started_at)[:19] if s.started_at else "",
            "completed_at": str(s.completed_at)[:19] if s.completed_at else "",
            "answers": ans_data,
            "final_answer": final_answer,
        })

    return {"sessions": result}


@app.post("/api/admin/login-history")
def admin_login_history(body: dict, db: Session = Depends(get_db)):
    if body.get("username") != ADMIN_USER or body.get("password") != ADMIN_PASS:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    events = db.query(LoginEvent).order_by(LoginEvent.timestamp.desc()).limit(500).all()
    return {
        "events": [
            {
                "profile_id": e.profile_id,
                "timestamp": str(e.timestamp)[:19] if e.timestamp else "",
            }
            for e in events
        ]
    }


@app.post("/api/admin/profiles")
def admin_get_profiles(body: dict):
    if body.get("username") != ADMIN_USER or body.get("password") != ADMIN_PASS:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return {"profiles": load_profiles(), "template": NEW_PROFILE_TEMPLATE}


@app.post("/api/admin/profiles/save")
def admin_save_profiles(body: dict):
    if body.get("username") != ADMIN_USER or body.get("password") != ADMIN_PASS:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    new_profiles = body.get("profiles", {})
    current = load_profiles()
    current.update(new_profiles)
    with open(PROFILES_PATH, "w") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)
    global PROFILES
    PROFILES = load_profiles()
    return {"ok": True}


@app.post("/api/admin/profiles/reset-sessions")
def admin_reset_sessions(body: dict, db: Session = Depends(get_db)):
    if body.get("username") != ADMIN_USER or body.get("password") != ADMIN_PASS:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    profile_id = body.get("profile_id", "")
    if not profile_id:
        raise HTTPException(status_code=400, detail="profile_id é obrigatório")

    deleted = db.query(QuizSession).filter(QuizSession.profile_id == profile_id).delete()
    db.commit()
    return {"ok": True, "deleted": deleted}


@app.post("/api/admin/profiles/delete")
def admin_delete_profile(body: dict, db: Session = Depends(get_db)):
    global PROFILES
    if body.get("username") != ADMIN_USER or body.get("password") != ADMIN_PASS:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    profile_id = body.get("profile_id", "")
    if not profile_id or profile_id not in PROFILES:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")

    current = load_profiles()
    del current[profile_id]
    with open(PROFILES_PATH, "w") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)
    PROFILES = load_profiles()

    db.query(QuizSession).filter(QuizSession.profile_id == profile_id).delete()
    db.commit()
    return {"ok": True}


@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    html = _render("admin.html",
        admin_user=ADMIN_USER,
        admin_pass=ADMIN_PASS)
    return HTMLResponse(html)
