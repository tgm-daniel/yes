import json
import os
import random
import uuid
from datetime import datetime, date, timedelta

from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import QuizSession, LoginEvent, Couple, DiaryEntry, DailyQuestion, Challenge, AgendaEvent, TodoItem, WeeklyReview
from translations import get_lang, t

BASE_DIR = os.getcwd()

app = FastAPI(title="Still Learning")
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


def get_partner_id(couple_id: str, my_id: str) -> str:
    couple = PROFILES.get(couple_id.split("_")[0], {})
    if couple.get("type") == "couple" and couple.get("couple_id") == couple_id:
        if couple.get("partner_name", "").lower() == my_id:
            return next((k for k, v in PROFILES.items() if v.get("type") == "couple" and v.get("couple_id") == couple_id and k != my_id), None)
    partner = next((k for k, v in PROFILES.items() if v.get("type") == "couple" and v.get("couple_id") == couple_id and k != my_id), None)
    return partner


def get_couple_db(couple_id: str, db: Session):
    return db.query(Couple).filter(Couple.id == couple_id).first()


# ---- PÁGINAS ----

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    lang = get_lang(request)
    return HTMLResponse(_render("index.html", lang=lang))


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


@app.get("/still-learning", response_class=HTMLResponse)
async def couple_app(request: Request):
    lang = get_lang(request)
    return HTMLResponse(_render("couple.html", lang=lang))


# ---- API LOGIN ----

@app.post("/api/login")
def api_login(body: dict, request: Request, db: Session = Depends(get_db)):
    name = body.get("name", "").strip().lower()
    password = body.get("password", "")

    profile = PROFILES.get(name)
    if not profile or profile["password"] != password:
        raise HTTPException(status_code=401, detail="Nome ou senha incorretos")

    db.add(LoginEvent(profile_id=name))
    db.commit()

    profile_type = profile.get("type", "quiz")

    if profile_type == "quiz":
        incomplete = db.query(QuizSession).filter(
            QuizSession.profile_id == name,
            QuizSession.finished == False,
            QuizSession.current_question > 0
        ).order_by(QuizSession.started_at.desc()).first()

        if incomplete:
            return {"type": "quiz", "incomplete": True, "session_id": incomplete.id}

        completed = db.query(QuizSession).filter(
            QuizSession.profile_id == name,
            QuizSession.finished == True
        ).order_by(QuizSession.started_at.desc()).first()

        if completed:
            return {"type": "quiz", "already_completed": True, "session_id": completed.id, "profile_name": name.capitalize()}

        return {
            "type": "quiz",
            "profile_id": name,
            "title": profile["title"],
            "subtitle": profile["subtitle"],
            "emoji": profile["emoji"],
        }
    else:
        return {"type": "couple", "name": name, "couple_id": profile["couple_id"], "partner_name": profile.get("partner_name", "")}


# ---- COUPLE API ----

@app.get("/api/couple/dashboard")
def api_couple_dashboard(request: Request, db: Session = Depends(get_db)):
    couple_id = request.headers.get("X-Couple-Id", "")
    my_name = request.headers.get("X-User-Name", "")
    if not couple_id or not my_name:
        raise HTTPException(status_code=400, detail="Missing couple/name headers")
    today = date.today()
    partner_name = next((p.get("partner_name","") for k,p in PROFILES.items() if p.get("type")=="couple" and p.get("couple_id")==couple_id and k==my_name), "")
    week_start = today - timedelta(days=today.weekday())

    question = db.query(DailyQuestion).filter(
        DailyQuestion.couple_id == couple_id, DailyQuestion.date == today
    ).first()

    diary_count = db.query(DiaryEntry).filter(
        DiaryEntry.couple_id == couple_id, DiaryEntry.date == today
    ).count()

    challenge = db.query(Challenge).filter(
        Challenge.couple_id == couple_id, Challenge.date == today
    ).first()

    events = db.query(AgendaEvent).filter(
        AgendaEvent.couple_id == couple_id, AgendaEvent.date >= datetime.utcnow()
    ).order_by(AgendaEvent.date.asc()).limit(3).all()

    todos = db.query(TodoItem).filter(
        TodoItem.couple_id == couple_id, TodoItem.done == False
    ).order_by(TodoItem.created_at.desc()).limit(5).all()

    review = db.query(WeeklyReview).filter(
        WeeklyReview.couple_id == couple_id, WeeklyReview.week_start == week_start
    ).first()

    has_new_partner_answers = False
    if question:
        if my_name == couple_id.split("_")[0]:
            has_new_partner_answers = question.answer_b is not None and not question.seen_by_a
        else:
            has_new_partner_answers = question.answer_a is not None and not question.seen_by_b

    return {
        "couple_id": couple_id,
        "my_name": my_name,
        "partner_name": partner_name,
        "question": {
            "exists": question is not None,
            "id": question.id if question else None,
            "my_answer": question.answer_a if question and (my_name == couple_id.split("_")[0] if True else question.answer_b) else (question.answer_b if question and my_name != (couple_id.split("_")[0] if True else "") else None),
        } if question else {"exists": False},
        "diary_count": diary_count,
        "challenge": {"exists": challenge is not None, "type": challenge.type if challenge else None, "done": (challenge.done_a if challenge and my_name == (couple_id.split("_")[0] if True else "") else (challenge.done_b if challenge else False)) if challenge else False} if challenge else {"exists": False},
        "events": [{"id": e.id, "title": e.title, "date": str(e.date)[:16]} for e in events],
        "todos": [{"id": t.id, "title": t.title, "done": t.done} for t in todos],
        "has_new_partner_answers": has_new_partner_answers,
        "review_exists": review is not None,
    }


@app.post("/api/couple/translations")
def api_translations(request: Request):
    lang = get_lang(request)
    return {"lang": lang, "t": t("daily_questions", lang)}


@app.post("/api/couple/question/answer")
def api_question_answer(body: dict, request: Request, db: Session = Depends(get_db)):
    couple_id = body.get("couple_id", "")
    my_name = body.get("name", "")
    answer = body.get("answer", "")
    if not couple_id or not my_name or not answer:
        raise HTTPException(status_code=400, detail="Missing fields")
    today = date.today()
    question = db.query(DailyQuestion).filter(
        DailyQuestion.couple_id == couple_id, DailyQuestion.date == today
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="No question for today")
    is_a = my_name == couple_id.split("_")[0]
    if is_a:
        question.answer_a = answer
    else:
        question.answer_b = answer
    db.commit()
    return {"ok": True}


@app.get("/api/couple/question")
def api_get_question(request: Request, db: Session = Depends(get_db)):
    couple_id = request.headers.get("X-Couple-Id", "")
    my_name = request.headers.get("X-User-Name", "")
    if not couple_id or not my_name:
        raise HTTPException(status_code=400, detail="Missing headers")
    today = date.today()
    lang = get_lang(request)
    question = db.query(DailyQuestion).filter(
        DailyQuestion.couple_id == couple_id, DailyQuestion.date == today
    ).first()

    if not question:
        questions_pt = t("daily_questions", "pt")
        questions_en = t("daily_questions", "en")
        if isinstance(questions_pt, str):
            questions_pt = []
        if isinstance(questions_en, str):
            questions_en = []
        if not questions_pt or not questions_en:
            return {"exists": False, "message": t("question_no_today", lang)}
        idx = (today.toordinal()) % len(questions_pt)
        q_pt = questions_pt[idx]
        q_en = questions_en[idx]
        question = DailyQuestion(
            couple_id=couple_id, date=today,
            question_pt=q_pt, question_en=q_en
        )
        db.add(question)
        db.commit()
        db.refresh(question)

    partner_name = next((p.get("partner_name","") for k,p in PROFILES.items() if p.get("type")=="couple" and p.get("couple_id")==couple_id and k==my_name), "")

    is_a = my_name == couple_id.split("_")[0]
    my_answer = question.answer_a if is_a else question.answer_b
    partner_answer = question.answer_b if is_a else question.answer_a
    seen = question.seen_by_a if is_a else question.seen_by_b

    if partner_answer is not None and not seen:
        if is_a:
            question.seen_by_a = True
        else:
            question.seen_by_b = True
        db.commit()

    q_lang = "pt" if lang == "pt" else "en"
    question_text = question.question_pt if lang == "pt" else question.question_en

    return {
        "exists": True,
        "id": question.id,
        "question": question_text,
        "my_answer": my_answer,
        "partner_answer": partner_answer,
        "partner_name": partner_name,
        "waiting": my_answer is not None and partner_answer is None,
        "both_answered": my_answer is not None and partner_answer is not None,
    }


@app.post("/api/couple/diary/save")
def api_diary_save(body: dict, db: Session = Depends(get_db)):
    couple_id = body.get("couple_id", "")
    author_id = body.get("author_id", "")
    content = body.get("content", "")
    mood = body.get("mood", "")
    if not couple_id or not author_id:
        raise HTTPException(status_code=400, detail="Missing fields")
    today = date.today()
    entry = db.query(DiaryEntry).filter(
        DiaryEntry.couple_id == couple_id,
        DiaryEntry.author_id == author_id,
        DiaryEntry.date == today
    ).first()
    if entry:
        entry.content = content
        entry.mood = mood
    else:
        entry = DiaryEntry(couple_id=couple_id, author_id=author_id, date=today, content=content, mood=mood)
        db.add(entry)
    db.commit()
    return {"ok": True}


@app.get("/api/couple/diary")
def api_get_diary(request: Request, db: Session = Depends(get_db)):
    couple_id = request.headers.get("X-Couple-Id", "")
    my_name = request.headers.get("X-User-Name", "")
    partner_name = request.headers.get("X-Partner-Name", "")
    if not couple_id or not my_name:
        raise HTTPException(status_code=400, detail="Missing headers")

    today = date.today()
    entries = db.query(DiaryEntry).filter(
        DiaryEntry.couple_id == couple_id
    ).order_by(DiaryEntry.date.desc()).all()

    partner_name = next((p.get("partner_name","") for k,p in PROFILES.items() if p.get("type")=="couple" and p.get("couple_id")==couple_id and k==my_name), "")

    my_today = None
    partner_today = None
    past = []
    for e in entries:
        entry = {"id": e.id, "date": str(e.date), "author_id": e.author_id, "content": e.content, "mood": e.mood}
        if e.date == today:
            if e.author_id == my_name:
                my_today = entry
            else:
                partner_today = entry
        else:
            past.append(entry)

    return {
        "my_today": my_today,
        "partner_today": partner_today,
        "partner_name": partner_name,
        "past": past,
        "my_name": my_name,
    }


@app.post("/api/couple/agenda/add")
def api_agenda_add(body: dict, db: Session = Depends(get_db)):
    couple_id = body.get("couple_id", "")
    title = body.get("title", "")
    date_str = body.get("date", "")
    description = body.get("description", "")
    created_by = body.get("created_by", "")
    if not couple_id or not title or not date_str:
        raise HTTPException(status_code=400, detail="Missing fields")
    try:
        event_date = datetime.fromisoformat(date_str)
    except:
        raise HTTPException(status_code=400, detail="Invalid date format")
    event = AgendaEvent(couple_id=couple_id, title=title, date=event_date, description=description, created_by=created_by)
    db.add(event)
    db.commit()
    db.refresh(event)
    return {"ok": True, "id": event.id}


@app.get("/api/couple/agenda")
def api_get_agenda(request: Request, db: Session = Depends(get_db)):
    couple_id = request.headers.get("X-Couple-Id", "")
    if not couple_id:
        raise HTTPException(status_code=400, detail="Missing couple_id")
    now = datetime.utcnow()
    events = db.query(AgendaEvent).filter(
        AgendaEvent.couple_id == couple_id,
        AgendaEvent.date >= now
    ).order_by(AgendaEvent.date.asc()).all()
    past = db.query(AgendaEvent).filter(
        AgendaEvent.couple_id == couple_id,
        AgendaEvent.date < now
    ).order_by(AgendaEvent.date.desc()).limit(20).all()
    return {
        "upcoming": [{"id": e.id, "title": e.title, "date": str(e.date)[:16], "description": e.description, "created_by": e.created_by} for e in events],
        "past": [{"id": e.id, "title": e.title, "date": str(e.date)[:16], "description": e.description, "created_by": e.created_by} for e in past],
    }


@app.post("/api/couple/todos/add")
def api_todo_add(body: dict, db: Session = Depends(get_db)):
    couple_id = body.get("couple_id", "")
    title = body.get("title", "")
    description = body.get("description", "")
    created_by = body.get("created_by", "")
    if not couple_id or not title:
        raise HTTPException(status_code=400, detail="Missing fields")
    todo = TodoItem(couple_id=couple_id, title=title, description=description, created_by=created_by)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return {"ok": True, "id": todo.id}


@app.post("/api/couple/todos/toggle")
def api_todo_toggle(body: dict, db: Session = Depends(get_db)):
    todo_id = body.get("id")
    my_name = body.get("name", "")
    if not todo_id:
        raise HTTPException(status_code=400, detail="Missing id")
    todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo.done:
        todo.done = False
        todo.done_by = None
    else:
        todo.done = True
        todo.done_by = my_name
    db.commit()
    return {"ok": True, "done": todo.done, "done_by": todo.done_by}


@app.get("/api/couple/todos")
def api_get_todos(request: Request, db: Session = Depends(get_db)):
    couple_id = request.headers.get("X-Couple-Id", "")
    if not couple_id:
        raise HTTPException(status_code=400, detail="Missing couple_id")
    items = db.query(TodoItem).filter(TodoItem.couple_id == couple_id).order_by(TodoItem.created_at.desc()).all()
    return {
        "items": [{"id": t.id, "title": t.title, "description": t.description, "done": t.done, "done_by": t.done_by, "created_by": t.created_by} for t in items]
    }


@app.post("/api/couple/review/save")
def api_review_save(body: dict, db: Session = Depends(get_db)):
    couple_id = body.get("couple_id", "")
    name = body.get("name", "")
    reflection = body.get("reflection", "")
    if not couple_id or not name or not reflection:
        raise HTTPException(status_code=400, detail="Missing fields")
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    review = db.query(WeeklyReview).filter(
        WeeklyReview.couple_id == couple_id,
        WeeklyReview.week_start == week_start
    ).first()
    if not review:
        review = WeeklyReview(couple_id=couple_id, week_start=week_start)
        db.add(review)
    is_a = name == couple_id.split("_")[0]
    if is_a:
        review.reflection_a = reflection
    else:
        review.reflection_b = reflection
    if review.reflection_a and review.reflection_b:
        review.completed = True
    db.commit()
    return {"ok": True}


@app.get("/api/couple/review")
def api_get_review(request: Request, db: Session = Depends(get_db)):
    couple_id = request.headers.get("X-Couple-Id", "")
    my_name = request.headers.get("X-User-Name", "")
    if not couple_id or not my_name:
        raise HTTPException(status_code=400, detail="Missing headers")
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    partner_name = next((p.get("partner_name","") for k,p in PROFILES.items() if p.get("type")=="couple" and p.get("couple_id")==couple_id and k==my_name), "")

    review = db.query(WeeklyReview).filter(
        WeeklyReview.couple_id == couple_id,
        WeeklyReview.week_start == week_start
    ).first()

    is_a = my_name == couple_id.split("_")[0]

    past = db.query(WeeklyReview).filter(
        WeeklyReview.couple_id == couple_id,
        WeeklyReview.week_start < week_start
    ).order_by(WeeklyReview.week_start.desc()).all()

    return {
        "current": {
            "exists": review is not None,
            "my_reflection": review.reflection_a if review and is_a else (review.reflection_b if review else None),
            "partner_reflection": review.reflection_b if review and is_a else (review.reflection_a if review else None),
            "completed": review.completed if review else False,
        } if review else {"exists": False},
        "partner_name": partner_name,
        "past": [{"week_start": str(r.week_start), "completed": r.completed} for r in past],
    }


@app.post("/api/couple/challenge/complete")
def api_challenge_complete(body: dict, db: Session = Depends(get_db)):
    couple_id = body.get("couple_id", "")
    name = body.get("name", "")
    if not couple_id or not name:
        raise HTTPException(status_code=400, detail="Missing fields")
    today = date.today()
    challenge = db.query(Challenge).filter(
        Challenge.couple_id == couple_id, Challenge.date == today
    ).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="No challenge today")
    is_a = name == couple_id.split("_")[0]
    if is_a:
        challenge.done_a = True
    else:
        challenge.done_b = True
    db.commit()
    return {"ok": True, "done_a": challenge.done_a, "done_b": challenge.done_b}


@app.get("/api/couple/challenge")
def api_get_challenge(request: Request, db: Session = Depends(get_db)):
    couple_id = request.headers.get("X-Couple-Id", "")
    my_name = request.headers.get("X-User-Name", "")
    if not couple_id or not my_name:
        raise HTTPException(status_code=400, detail="Missing headers")
    today = date.today()

    partner_name = next((p.get("partner_name","") for k,p in PROFILES.items() if p.get("type")=="couple" and p.get("couple_id")==couple_id and k==my_name), "")

    challenge = db.query(Challenge).filter(
        Challenge.couple_id == couple_id, Challenge.date == today
    ).first()

    if not challenge:
        types = ["wordle", "riddle", "photo"]
        ctype = types[today.toordinal() % len(types)]
        data = {"prompt_pt": "", "prompt_en": "", "word": ""}
        if ctype == "wordle":
            words = ["AMOR", "PAZ", "LUZ", "Vida", "SONHO", "GRATO", "FEITO", "UNIAO", "SABER", "FORTE"]
            data["word"] = words[today.toordinal() % len(words)]
            data["prompt_pt"] = "Descubra a palavra do dia!"
            data["prompt_en"] = "Guess the word of the day!"
        elif ctype == "riddle":
            riddles_pt = ["O que é meu, mas os outros usam mais que eu?", "Quanto mais se tira, maior fica.", "O que pode correr mas nunca anda?"]
            riddles_en = ["What is mine but others use more than me?", "The more you take, the more you leave behind.", "What can run but never walks?"]
            idx = today.toordinal() % len(riddles_pt)
            data["riddle_pt"] = riddles_pt[idx]
            data["riddle_en"] = riddles_en[idx]
            answers_pt = ["Meu nome", "Um buraco", "O vento"]
            data["answer_pt"] = answers_pt[idx]
            answers_en = ["My name", "A hole", "The wind"]
            data["answer_en"] = answers_en[idx]
        else:
            photos_pt = ["Tire uma foto de algo que te lembre de mim", "Tire uma selfie com seu objeto favorito", "Tire uma foto do céu agora"]
            photos_en = ["Take a photo of something that reminds you of me", "Take a selfie with your favorite object", "Take a photo of the sky right now"]
            idx = today.toordinal() % len(photos_pt)
            data["prompt_pt"] = photos_pt[idx]
            data["prompt_en"] = photos_en[idx]

        challenge = Challenge(couple_id=couple_id, date=today, type=ctype, data=data)
        db.add(challenge)
        db.commit()
        db.refresh(challenge)

    is_a = my_name == couple_id.split("_")[0]
    my_done = challenge.done_a if is_a else challenge.done_b
    partner_done = challenge.done_b if is_a else challenge.done_a

    return {
        "exists": True,
        "type": challenge.type,
        "data": challenge.data,
        "my_done": my_done,
        "partner_done": partner_done,
        "partner_name": partner_name,
    }


# ---- EXISTING QUIZ API (unchanged) ----

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
    return {"session_id": session.id, "total_questions": len(questions)}


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
    return {"question_id": q["id"], "question": q["question"], "options": q["options"], "current": session.current_question + 1, "total": total, "finished": False}


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
    answers.append({"question_id": q["id"], "selected": selected, "correct": correct})
    session.answers = answers
    session.current_question += 1
    if session.current_question >= len(order):
        session.finished = True
        session.completed_at = datetime.utcnow()
    db.commit()
    return {"correct": correct, "correct_answer": q["correct"], "fun_fact": q["fun_fact"], "score": session.score, "current": session.current_question, "total": total, "finished": session.finished, "is_last": session.finished}


@app.post("/api/result/final/{session_id}")
def api_result_final(session_id: str, body: dict, db: Session = Depends(get_db)):
    session = db.query(QuizSession).filter(QuizSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    answer = body.get("answer")
    if answer not in ("yes", "no"):
        raise HTTPException(status_code=400, detail="Resposta inválida")
    answers = list(session.answers or [])
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
        details.append({"question": q["question"], "selected": q["options"][ans["selected"]], "correct": q["options"][q["correct"]], "was_correct": ans["correct"], "fun_fact": q["fun_fact"]})
    tier = get_result_tier(percentage)
    tier_data = profile["resultMessages"][tier]
    return {"score": score, "total": total, "percentage": percentage, "message": tier_data["message"], "final_question": tier_data["final_question"], "emoji": tier_data["emoji"], "title": tier_data["title"], "details": details, "session_id": session_id, "instagram": profile["instagram"], "yesMessage": profile["yesMessage"], "yesFooter": profile["yesFooter"], "noMessage": profile["noMessage"], "noFooter": profile["noFooter"], "profile_emoji": profile["emoji"], "final_answer": final_answer, "already_completed": True}


# ---- ADMIN (unchanged) ----

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
            ans_data.append({"question": q.get("question", "?"), "selected": opts[a["selected"]] if a["selected"] < len(opts) else "?", "correct_answer": opts[q["correct"]] if q.get("correct") is not None and q["correct"] < len(opts) else "?", "was_correct": a["correct"], "fun_fact": q.get("fun_fact", "")})
        final_answer = None
        for a in (s.answers or []):
            if a.get("type") == "final_answer":
                final_answer = a.get("value")
                break
        result.append({"session_id": s.id, "profile_id": s.profile_id, "score": s.score, "total": len(s.question_order or questions), "started_at": str(s.started_at)[:19] if s.started_at else "", "completed_at": str(s.completed_at)[:19] if s.completed_at else "", "answers": ans_data, "final_answer": final_answer})
    return {"sessions": result}


@app.post("/api/admin/login-history")
def admin_login_history(body: dict, db: Session = Depends(get_db)):
    if body.get("username") != ADMIN_USER or body.get("password") != ADMIN_PASS:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    events = db.query(LoginEvent).order_by(LoginEvent.timestamp.desc()).limit(500).all()
    return {"events": [{"profile_id": e.profile_id, "timestamp": str(e.timestamp)[:19] if e.timestamp else ""} for e in events]}


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
    html = _render("admin.html", admin_user=ADMIN_USER, admin_pass=ADMIN_PASS)
    return HTMLResponse(html)
