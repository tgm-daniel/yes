import json
import os
import random
import uuid
import hashlib
from datetime import datetime, date, timedelta

from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import QuizSession, LoginEvent, Couple, DiaryEntry, DailyQuestion, Challenge, AgendaEvent, TodoItem, WeeklyReview, Photo, QuizAnswer, QuoteRefresh, Profile, LoginCredential
from translations import get_lang, t

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="Still Learning")
Base.metadata.create_all(bind=engine)
# Migration: recreate quote_refreshes with new schema
try:
    from sqlalchemy import inspect, text as sql_text
    insp = inspect(engine)
    cols = [c['name'] for c in insp.get_columns('quote_refreshes')]
    if 'offset' in cols and 'current_offset' not in cols:
        with engine.connect() as conn:
            conn.execute(sql_text("DROP TABLE quote_refreshes"))
            conn.commit()
        Base.metadata.create_all(bind=engine)
except Exception:
    pass

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


@app.on_event("startup")
def startup_load_profiles():
    db = next(get_db())
    try:
        reload_profiles(db)
    finally:
        db.close()


ADMIN_USERS = {"ttt": "sisrat", "T": "trs123", "Tadmin": "trs123"}


def hash_pw(pw: str) -> str:
    return hashlib.sha256((pw + "sl-hmac-2024").encode()).hexdigest()


def migrate_profiles(db: Session):
    """Migrate profiles.json to database if profiles table is empty."""
    if db.query(Profile).count() > 0:
        return

    PROFILES_PATH = os.path.join(BASE_DIR, "profiles.json")
    if not os.path.exists(PROFILES_PATH):
        return

    with open(PROFILES_PATH) as f:
        legacy = json.load(f)

    for login_name, pd in legacy.items():
        pid = str(uuid.uuid4())[:12]
        p_type = pd.get("type", "quiz")
        display = login_name if pd.get("type") == "couple" else ""
        data = {k: v for k, v in pd.items() if k not in ("password", "type")}
        profile = Profile(id=pid, type=p_type, display_name=display, data=data)
        db.add(profile)
        db.flush()

        cred = LoginCredential(
            login_name=login_name.lower(),
            profile_id=pid,
            password_hash=hash_pw(pd["password"])
        )
        db.add(cred)

    db.commit()


def load_profiles_from_db(db: Session):
    profiles = {}
    login_map = {}
    for p in db.query(Profile).all():
        profiles[p.id] = {"type": p.type, "display_name": p.display_name, **p.data}
    for c in db.query(LoginCredential).all():
        login_map[c.login_name] = c.profile_id
    return profiles, login_map


PROFILES: dict = {}
LOGIN_MAP: dict = {}


def reload_profiles(db: Session):
    global PROFILES, LOGIN_MAP
    migrate_profiles(db)
    PROFILES, LOGIN_MAP = load_profiles_from_db(db)

def check_admin(body: dict):
    user = body.get("username", "")
    pw = body.get("password", "")
    if ADMIN_USERS.get(user) != pw:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

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
    profile = PROFILES.get(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    return profile


def get_profile_questions(profile_id: str) -> list:
    return get_profile(profile_id)["questions"]


def get_result_tier(percentage: float) -> str:
    if percentage >= 80:
        return "high"
    elif percentage >= 50:
        return "mid"
    return "low"


def get_partner_id(couple_id: str, my_id: str) -> str:
    partner = next((k for k, v in PROFILES.items() if v.get("type") == "couple" and v.get("couple_id") == couple_id and _profile_name(v).lower() != my_id.lower()), None)
    return partner


def _profile_name(p: dict) -> str:
    return p.get("name", p.get("display_name", ""))


def get_partner_name(couple_id: str, my_name: str) -> str:
    for _, p in PROFILES.items():
        if p.get("type") == "couple" and p.get("couple_id") == couple_id and _profile_name(p).lower() == my_name.lower():
            return p.get("partner_name", "")
    return ""


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
    name_raw = body.get("name", "").strip().lower()
    password = body.get("password", "")

    # Look up by login name in LOGIN_MAP
    profile_id = LOGIN_MAP.get(name_raw)
    if not profile_id:
        raise HTTPException(status_code=401, detail="Nome ou senha incorretos")

    cred = db.query(LoginCredential).filter(LoginCredential.login_name == name_raw).first()
    if not cred or cred.password_hash != hash_pw(password):
        raise HTTPException(status_code=401, detail="Nome ou senha incorretos")

    profile = PROFILES.get(profile_id)
    if not profile:
        raise HTTPException(status_code=401, detail="Nome ou senha incorretos")

    db.add(LoginEvent(profile_id=profile_id))
    db.commit()

    profile_type = profile.get("type", "quiz")

    if profile_type == "quiz":
        incomplete = db.query(QuizSession).filter(
            QuizSession.profile_id == profile_id,
            QuizSession.finished == False,
            QuizSession.current_question > 0
        ).order_by(QuizSession.started_at.desc()).first()

        if incomplete:
            return {"type": "quiz", "incomplete": True, "session_id": incomplete.id}

        completed = db.query(QuizSession).filter(
            QuizSession.profile_id == profile_id,
            QuizSession.finished == True
        ).order_by(QuizSession.started_at.desc()).first()

        if completed:
            return {"type": "quiz", "already_completed": True, "session_id": completed.id, "profile_name": profile.get("display_name", name_raw.capitalize())}

        return {
            "type": "quiz",
            "profile_id": profile_id,
            "title": profile.get("title", ""),
            "subtitle": profile.get("subtitle", ""),
            "emoji": profile.get("emoji", "💕"),
        }
    else:
        display = profile.get("display_name", name_raw)
        return {"type": "couple", "name": display, "couple_id": profile.get("couple_id", ""), "partner_name": profile.get("partner_name", "")}


# ---- COUPLE API ----

@app.get("/api/couple/dashboard")
def api_couple_dashboard(request: Request, db: Session = Depends(get_db)):
    couple_id = request.headers.get("X-Couple-Id", "")
    my_name = request.headers.get("X-User-Name", "")
    if not couple_id or not my_name:
        raise HTTPException(status_code=400, detail="Missing couple/name headers")
    today = date.today()
    partner_name = get_partner_name(couple_id, my_name)
    week_start = today - timedelta(days=today.weekday())

    question = db.query(DailyQuestion).filter(
        DailyQuestion.couple_id == couple_id, DailyQuestion.date == today
    ).first()

    diary_count = db.query(DiaryEntry).filter(
        DiaryEntry.couple_id == couple_id, DiaryEntry.date == today
    ).count()
    diary_my_today = db.query(DiaryEntry).filter(
        DiaryEntry.couple_id == couple_id, DiaryEntry.date == today, DiaryEntry.author_id == my_name
    ).first() is not None
    diary_partner_today = db.query(DiaryEntry).filter(
        DiaryEntry.couple_id == couple_id, DiaryEntry.date == today, DiaryEntry.author_id != my_name
    ).first() is not None

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
    notifications = []
    if question:
        if my_name == couple_id.split("_")[0]:
            has_new_partner_answers = question.answer_b is not None and not question.seen_by_a
            if has_new_partner_answers:
                notifications.append({"type": "daily_answer", "msg_pt": f"{partner_name} respondeu a pergunta do dia!", "msg_en": f"{partner_name} answered the daily question!"})
        else:
            has_new_partner_answers = question.answer_a is not None and not question.seen_by_b
            if has_new_partner_answers:
                notifications.append({"type": "daily_answer", "msg_pt": f"{partner_name} respondeu a pergunta do dia!", "msg_en": f"{partner_name} answered the daily question!"})

    # Check partner challenge notifications
    partner_chals = db.query(Challenge).filter(
        Challenge.couple_id == couple_id, Challenge.date == today, Challenge.type == "partner_challenge"
    ).all()
    for c in partner_chals:
        if c.created_by and c.created_by != my_name:
            other_name = c.created_by
            if c.answered_b if my_name == couple_id.split("_")[0] else c.answered_a:
                notifications.append({"type": "partner_challenge_resp", "id": c.id, "msg_pt": f"{other_name} completou o desafio!", "msg_en": f"{other_name} completed the challenge!"})
                break

    # Check challenge partner_question notification
    chal = db.query(Challenge).filter(
        Challenge.couple_id == couple_id, Challenge.date == today, Challenge.type == "partner_question"
    ).first()
    partner_answered = False
    if chal:
        is_a = my_name == couple_id.split("_")[0]
        partner_answered = chal.answered_b if is_a else chal.answered_a
        partner_seen = chal.seen_b if is_a else chal.seen_a
        if partner_answered and not partner_seen:
            notifications.append({"type": "question_answered", "msg_pt": f"{partner_name} respondeu sua pergunta íntima! 💌", "msg_en": f"{partner_name} answered your intimate question! 💌"})

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
        "diary_my_today": diary_my_today,
        "diary_partner_today": diary_partner_today,
        "challenge": {"exists": challenge is not None, "type": challenge.type if challenge else None, "done": (challenge.done_a if challenge and my_name == (couple_id.split("_")[0] if True else "") else (challenge.done_b if challenge else False)) if challenge else False,
                      "partner_answered": partner_answered} if challenge else {"exists": False, "partner_answered": False},
        "events": [{"id": e.id, "title": e.title, "date": str(e.date)[:16]} for e in events],
        "todos": [{"id": t.id, "title": t.title, "done": t.done} for t in todos],
        "has_new_partner_answers": has_new_partner_answers,
        "review_exists": review is not None,
        "notifications": notifications,
        "partner_challenge_count": len(partner_chals),
        "partner_challenge_limit": 3,
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

    partner_name = get_partner_name(couple_id, my_name)

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

    partner_name = get_partner_name(couple_id, my_name)

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

    partner_name = get_partner_name(couple_id, my_name)

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


# ── CHALLENGES ──────────────────────────────────────────────────

CHALLENGE_TYPES = ["photo", "riddle", "partner_question", "partner_challenge", "quote"]

RIDDLES_PT = ["O que é meu, mas os outros usam mais que eu?", "Quanto mais se tira, maior fica.", "O que pode correr mas nunca anda?", "O que tem chaves mas não abre portas?", "O que é leve como uma pluma, mas ninguém segura por muito tempo?"]
RIDDLES_EN = ["What is mine but others use more than me?", "The more you take, the more you leave behind.", "What can run but never walks?", "What has keys but can't open doors?", "What is light as a feather but nobody can hold for long?"]
ANSWERS_PT = ["Meu nome", "Um buraco", "O vento", "Um piano", "O ar"]
ANSWERS_EN = ["My name", "A hole", "The wind", "A piano", "Your breath"]

def get_riddle(today):
    idx = today.toordinal() % len(RIDDLES_PT)
    return {"riddle_pt": RIDDLES_PT[idx], "riddle_en": RIDDLES_EN[idx],
            "answer_pt": ANSWERS_PT[idx], "answer_en": ANSWERS_EN[idx]}

def get_quote(today, offset=0):
    quotes = t("daily_quotes", "pt")
    if isinstance(quotes, list) and len(quotes):
        idx = (today.toordinal() + offset) % len(quotes)
        q = quotes[idx]
        q_en = t("daily_quotes", "en")
        qe = q_en[idx] if isinstance(q_en, list) and len(q_en) > idx else q
        return {"quote_pt": q["text"], "quote_en": qe.get("text", q.get("text", "")),
                "author": q["author"], "source": q["source"], "original": q.get("original", ""),
                "curiosity_pt": q.get("curiosity", ""), "curiosity_en": qe.get("curiosity_en", qe.get("curiosity", ""))}
    return {"quote_pt": "O amor é paciente, o amor é bondoso.", "quote_en": "Love is patient, love is kind.",
            "author": "Bíblia", "source": "1 Coríntios 13", "original": "Love is patient, love is kind.",
            "curiosity_pt": "1 Coríntios 13 é conhecido como o 'capítulo do amor'. Foi escrito pelo apóstolo Paulo para a igreja de Corinto.",
            "curiosity_en": "1 Corinthians 13 is known as the 'love chapter'. It was written by the apostle Paul to the church in Corinth."}


@app.get("/api/couple/challenge")
def api_get_challenge(request: Request, db: Session = Depends(get_db)):
    couple_id = request.headers.get("X-Couple-Id", "")
    my_name = request.headers.get("X-User-Name", "")
    if not couple_id or not my_name:
        raise HTTPException(status_code=400, detail="Missing headers")
    today = date.today()
    lang = request.cookies.get("lang", "pt")
    partner_name = get_partner_name(couple_id, my_name)
    is_a = my_name == couple_id.split("_")[0]
    is_creator = ((today.day % 2 == 0 and is_a) or (today.day % 2 == 1 and not is_a))

    ctype = CHALLENGE_TYPES[today.toordinal() % len(CHALLENGE_TYPES)]
    challenge = db.query(Challenge).filter(
        Challenge.couple_id == couple_id, Challenge.date == today, Challenge.type == ctype
    ).first()

    if not challenge:
        data = {}
        if ctype == "riddle":
            data = get_riddle(today)
        elif ctype == "partner_question":
            themes = t("themes", lang)
            if isinstance(themes, str): themes = []
            data = {"themes": themes[:6] if len(themes) > 6 else themes, "question": None, "theme": None, "theme_idx": today.toordinal() % max(len(themes), 1)}
        elif ctype == "partner_challenge":
            suggestions = t("challenge_suggestions", lang)
            if isinstance(suggestions, str): suggestions = []
            data = {"suggestions": suggestions[:8] if len(suggestions) > 8 else suggestions, "challenge": None}
        elif ctype == "quote":
            data = get_quote(today)
        elif ctype == "photo":
            pt_prompts = [
                "Sua vista favorita no momento 🌅",
                "Tire uma foto de algo que te lembre de mim 💕",
                "Capture um momento que te fez sorrir hoje 😊",
                "Mostre o que você está vendo agora 👀",
                "Um lugar especial para nós dois 🏠",
                "Algo pequeno que tem um grande significado ✨",
            ]
            en_prompts = [
                "Your favorite view right now 🌅",
                "Take a photo of something that reminds you of me 💕",
                "Capture a moment that made you smile today 😊",
                "Show what you're seeing right now 👀",
                "A special place for the two of us 🏠",
                "Something small with big meaning ✨",
            ]
            idx = today.toordinal() % len(pt_prompts)
            data = {"prompt_pt": pt_prompts[idx], "prompt_en": en_prompts[idx], "photo_url": None}
        challenge = Challenge(couple_id=couple_id, date=today, type=ctype, data=data)
        db.add(challenge)
        db.commit()
        db.refresh(challenge)

    my_done = challenge.done_a if is_a else challenge.done_b
    partner_done = challenge.done_b if is_a else challenge.done_a
    my_answered = challenge.answered_a if is_a else challenge.answered_b
    partner_answered = challenge.answered_b if is_a else challenge.answered_a
    my_guess = challenge.guess_a if is_a else challenge.guess_b
    partner_seen_my_answer = challenge.seen_b if is_a else challenge.seen_a

    # Mark partner's response as seen when fetching (if both answered)
    if ctype == "partner_question" and challenge.created_by and challenge.created_by != my_name:
        if partner_answered and not (challenge.seen_b if is_a else challenge.seen_a):
            if is_a: challenge.seen_b = True
            else: challenge.seen_a = True
            db.commit()

    result = {
        "exists": True,
        "type": ctype,
        "data": challenge.data,
        "my_done": my_done,
        "partner_done": partner_done,
        "partner_name": partner_name,
        "is_creator": is_creator,
        "created_by": challenge.created_by,
        "my_answered": my_answered,
        "partner_answered": partner_answered,
        "my_guess": my_guess,
        "partner_guess": challenge.guess_b if is_a else challenge.guess_a,
        "both_answered": my_answered and partner_answered,
        "_is_a": is_a,
    }
    return result


@app.post("/api/couple/challenge/guess")
def api_challenge_guess(body: dict, db: Session = Depends(get_db)):
    couple_id = body.get("couple_id", "")
    name = body.get("name", "")
    guess = body.get("guess", "")
    if not couple_id or not name or not guess:
        raise HTTPException(status_code=400, detail="Missing fields")
    today = date.today()
    challenge = db.query(Challenge).filter(
        Challenge.couple_id == couple_id, Challenge.date == today, Challenge.type == "riddle"
    ).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="No riddle today")
    is_a = name == couple_id.split("_")[0]
    if is_a:
        challenge.guess_a = guess
    else:
        challenge.guess_b = guess
    data = challenge.data
    pt_answer = (data.get("answer_pt") or "").strip().lower()
    en_answer = (data.get("answer_en") or "").strip().lower()
    correct = guess.strip().lower() in [pt_answer, en_answer]
    if correct:
        if is_a: challenge.done_a = True
        else: challenge.done_b = True
    db.commit()
    return {"ok": True, "correct": correct, "answer_pt": data.get("answer_pt"), "answer_en": data.get("answer_en")}


@app.post("/api/couple/challenge/create-question")
def api_create_question(body: dict, db: Session = Depends(get_db)):
    couple_id = body.get("couple_id", "")
    name = body.get("name", "")
    question = body.get("question", "")
    theme_idx = body.get("theme_idx", None)
    custom_theme = body.get("custom_theme", "")
    if not couple_id or not name or not question:
        raise HTTPException(status_code=400, detail="Missing fields")
    today = date.today()
    challenge = db.query(Challenge).filter(
        Challenge.couple_id == couple_id, Challenge.date == today, Challenge.type == "partner_question"
    ).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="No partner question challenge today")
    challenge.created_by = name
    is_a = name == couple_id.split("_")[0]
    if is_a:
        challenge.answered_a = True
        challenge.done_a = True
    else:
        challenge.answered_b = True
        challenge.done_b = True
    data = challenge.data
    data["question"] = question
    if custom_theme:
        data["custom_theme"] = custom_theme
    elif theme_idx is not None:
        themes = data.get("themes", [])
        if isinstance(themes, list) and theme_idx < len(themes):
            data["chosen_theme"] = themes[theme_idx]
    challenge.data = data
    db.commit()
    return {"ok": True}


@app.post("/api/couple/challenge/answer-question")
def api_answer_question(body: dict, db: Session = Depends(get_db)):
    couple_id = body.get("couple_id", "")
    name = body.get("name", "")
    answer = body.get("answer", "")
    if not couple_id or not name or not answer:
        raise HTTPException(status_code=400, detail="Missing fields")
    today = date.today()
    challenge = db.query(Challenge).filter(
        Challenge.couple_id == couple_id, Challenge.date == today, Challenge.type == "partner_question"
    ).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="No partner question today")
    is_a = name == couple_id.split("_")[0]
    if is_a:
        challenge.answered_a = True
        challenge.done_a = True
        challenge.guess_a = answer  # reuse guess_a as the answer (I know it's confusing, but it stores the response)
    else:
        challenge.answered_b = True
        challenge.done_b = True
        challenge.guess_b = answer
    db.commit()
    both = challenge.answered_a and challenge.answered_b
    return {"ok": True, "both_answered": both}


@app.post("/api/couple/challenge/partner/create")
def api_create_partner_challenge(body: dict, db: Session = Depends(get_db)):
    couple_id = body.get("couple_id", "")
    name = body.get("name", "")
    challenge_text = body.get("challenge", "")
    suggestion_idx = body.get("suggestion_idx", None)
    custom_challenge = body.get("custom_challenge", "")
    if not couple_id or not name:
        raise HTTPException(status_code=400, detail="Missing fields")
    text = challenge_text or custom_challenge
    if not text:
        raise HTTPException(status_code=400, detail="Challenge text required")
    today = date.today()
    count = db.query(Challenge).filter(
        Challenge.couple_id == couple_id, Challenge.date == today,
        Challenge.type == "partner_challenge", Challenge.created_by == name
    ).count()
    if count >= 3:
        raise HTTPException(status_code=400, detail="Daily limit of 3 partner challenges reached")
    chal = Challenge(
        couple_id=couple_id, date=today, type="partner_challenge",
        data={"challenge": text, "suggestion_idx": suggestion_idx},
        created_by=name
    )
    db.add(chal)
    db.commit()
    return {"ok": True, "id": chal.id, "remaining": 2 - count}


@app.post("/api/couple/challenge/partner/complete")
def api_complete_partner_challenge(body: dict, db: Session = Depends(get_db)):
    challenge_id = body.get("id")
    name = body.get("name", "")
    if not challenge_id or not name:
        raise HTTPException(status_code=400, detail="Missing fields")
    chal = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not chal:
        raise HTTPException(status_code=404, detail="Challenge not found")
    couple_id = chal.couple_id
    is_a = name == couple_id.split("_")[0]
    if is_a:
        chal.done_a = True
        chal.answered_a = True
    else:
        chal.done_b = True
        chal.answered_b = True
    db.commit()
    return {"ok": True}


@app.get("/api/couple/challenge/partner")
def api_get_partner_challenges(request: Request, db: Session = Depends(get_db)):
    couple_id = request.headers.get("X-Couple-Id", "")
    my_name = request.headers.get("X-User-Name", "")
    if not couple_id or not my_name:
        raise HTTPException(status_code=400, detail="Missing headers")
    today = date.today()
    challenges = db.query(Challenge).filter(
        Challenge.couple_id == couple_id, Challenge.date == today, Challenge.type == "partner_challenge"
    ).all()
    is_a = my_name == couple_id.split("_")[0]
    return [{
        "id": c.id, "created_by": c.created_by, "challenge": c.data.get("challenge", ""),
        "my_done": c.done_a if is_a else c.done_b,
        "partner_done": c.done_b if is_a else c.done_a,
        "my_answered": c.answered_a if is_a else c.answered_b,
        "partner_answered": c.answered_b if is_a else c.answered_a,
    } for c in challenges]


MAX_QUOTE_UNLOCK = 3

@app.get("/api/couple/quote")
def api_get_quote(request: Request, offset: int = None, unlock: int = 0, like: int = 0, db: Session = Depends(get_db)):
    couple_id = request.headers.get("X-Couple-Id", "")
    if not couple_id:
        raise HTTPException(status_code=400, detail="Missing headers")
    today = date.today()

    state = db.query(QuoteRefresh).filter(
        QuoteRefresh.couple_id == couple_id,
        QuoteRefresh.date == today
    ).first()

    if not state:
        state = QuoteRefresh(couple_id=couple_id, date=today, current_offset=0, max_offset=0, unlock_count=0, liked_offset=None)
        db.add(state)
        db.commit()

    # Handle unlock next
    if unlock:
        if state.unlock_count >= MAX_QUOTE_UNLOCK:
            return {
                "exists": False,
                "exhausted": True,
                "message_pt": "Os quotes de hoje acabaram! Volte amanhã para ver mais. 💫",
                "message_en": "Today's quotes are done! Come back tomorrow for more. 💫",
            }
        state.max_offset += 1
        state.unlock_count += 1
        state.current_offset = state.max_offset
        db.commit()

    # Handle like toggle
    if like:
        if state.liked_offset == state.current_offset:
            state.liked_offset = None
        else:
            state.liked_offset = state.current_offset
        db.commit()

    # Handle explicit offset navigation
    if offset is not None:
        target = max(0, min(offset, state.max_offset))
        state.current_offset = target
        db.commit()

    q = get_quote(today, state.current_offset)
    remaining = max(0, MAX_QUOTE_UNLOCK - state.unlock_count)

    return {
        "exists": True,
        "data": q,
        "current_offset": state.current_offset,
        "max_offset": state.max_offset,
        "unlock_count": state.unlock_count,
        "remaining": remaining,
        "liked_offset": state.liked_offset,
        "has_prev": state.current_offset > 0,
        "has_next": state.current_offset < state.max_offset,
        "can_unlock": state.unlock_count < MAX_QUOTE_UNLOCK,
        "exhausted": False,
    }


@app.get("/api/couple/quiz")
def api_get_quiz(request: Request, db: Session = Depends(get_db)):
    couple_id = request.headers.get("X-Couple-Id", "")
    my_name = request.headers.get("X-User-Name", "")
    if not couple_id or not my_name:
        raise HTTPException(status_code=400, detail="Missing headers")
    partner_name = get_partner_name(couple_id, my_name)
    answers = db.query(QuizAnswer).filter(QuizAnswer.couple_id == couple_id).all()
    my_answers = {a.question_idx: a for a in answers if a.author_id == my_name}
    partner_answers = {a.question_idx: a for a in answers if a.author_id != my_name}
    result = {}
    for a in answers:
        idx = a.question_idx
        if idx not in result:
            result[idx] = {"question_idx": idx, "category": a.category}
        if a.author_id == my_name:
            result[idx]["my_self"] = a.about_self
            result[idx]["my_partner"] = a.about_partner
        else:
            result[idx]["partner_self"] = a.about_self
            result[idx]["partner_partner"] = a.about_partner
    return {
        "answers": list(result.values()),
        "my_answered": any(a.about_self is not None for a in my_answers.values()),
        "partner_answered": any(a.about_self is not None for a in partner_answers.values()),
        "partner_name": partner_name,
    }


@app.post("/api/couple/quiz/save")
def api_save_quiz(body: dict, db: Session = Depends(get_db)):
    couple_id = body.get("couple_id", "")
    author_id = body.get("author_id", "")
    question_idx = body.get("question_idx")
    category = body.get("category", "basic")
    about_self = body.get("about_self")
    about_partner = body.get("about_partner")
    if not couple_id or not author_id or question_idx is None:
        raise HTTPException(status_code=400, detail="Missing fields")
    existing = db.query(QuizAnswer).filter(
        QuizAnswer.couple_id == couple_id,
        QuizAnswer.author_id == author_id,
        QuizAnswer.question_idx == question_idx,
        QuizAnswer.category == category,
    ).first()
    if existing:
        if about_self is not None:
            existing.about_self = about_self
        if about_partner is not None:
            existing.about_partner = about_partner
    else:
        existing = QuizAnswer(
            couple_id=couple_id, author_id=author_id,
            question_idx=question_idx, category=category,
            about_self=about_self, about_partner=about_partner,
        )
        db.add(existing)
    db.commit()
    return {"ok": True}


MAX_PHOTO_SIZE = 300 * 1024  # 300KB max for base64

@app.post("/api/couple/challenge/photo")
def api_upload_photo(body: dict, db: Session = Depends(get_db)):
    couple_id = body.get("couple_id", "")
    name = body.get("name", "")
    photo_data = body.get("photo", "")  # base64
    caption = body.get("caption", "")
    if not couple_id or not name or not photo_data:
        raise HTTPException(status_code=400, detail="Missing fields")
    today = date.today()
    if len(photo_data) > MAX_PHOTO_SIZE:
        raise HTTPException(status_code=400, detail="Photo too large")
    challenge = db.query(Challenge).filter(
        Challenge.couple_id == couple_id, Challenge.date == today, Challenge.type == "photo"
    ).first()
    if challenge:
        is_a = name == couple_id.split("_")[0]
        data = challenge.data
        key = "photo_url_a" if is_a else "photo_url_b"
        data[key] = photo_data
        data["photo_by_" + ("a" if is_a else "b")] = name
        data["caption_" + ("a" if is_a else "b")] = caption
        challenge.data = data
        if is_a:
            challenge.done_a = True
        else:
            challenge.done_b = True
        db.commit()
    # Save to photos table for memories
    photo = Photo(couple_id=couple_id, author_id=name, date=today, data=photo_data, caption=caption)
    db.add(photo)
    db.commit()
    return {"ok": True}


@app.get("/api/couple/memories")
def api_get_memories(request: Request, db: Session = Depends(get_db)):
    couple_id = request.headers.get("X-Couple-Id", "")
    my_name = request.headers.get("X-User-Name", "")
    if not couple_id or not my_name:
        raise HTTPException(status_code=400, detail="Missing headers")
    is_a = my_name == couple_id.split("_")[0]

    # Daily questions answered
    questions = db.query(DailyQuestion).filter(
        DailyQuestion.couple_id == couple_id,
        DailyQuestion.answer_a.isnot(None), DailyQuestion.answer_b.isnot(None)
    ).order_by(DailyQuestion.date.desc()).limit(20).all()

    # Challenge responses (both answered)
    challenges = db.query(Challenge).filter(
        Challenge.couple_id == couple_id,
        Challenge.answered_a == True, Challenge.answered_b == True
    ).order_by(Challenge.date.desc()).limit(20).all()

    # Weekly reviews
    reviews = db.query(WeeklyReview).filter(
        WeeklyReview.couple_id == couple_id,
        WeeklyReview.completed == True
    ).order_by(WeeklyReview.week_start.desc()).limit(10).all()

    # Photos
    photos = db.query(Photo).filter(
        Photo.couple_id == couple_id
    ).order_by(Photo.date.desc()).limit(30).all()

    # Diary entries
    diary = db.query(DiaryEntry).filter(
        DiaryEntry.couple_id == couple_id
    ).order_by(DiaryEntry.date.desc()).limit(30).all()

    return {
        "questions": [{
            "date": str(q.date), "question_pt": q.question_pt, "question_en": q.question_en,
            "my_answer": q.answer_a if is_a else q.answer_b,
            "partner_answer": q.answer_b if is_a else q.answer_a,
        } for q in questions],
        "challenges": [{
            "date": str(c.date), "type": c.type,
            "data": c.data,
            "my_done": c.done_a if is_a else c.done_b,
            "partner_done": c.done_b if is_a else c.done_a,
        } for c in challenges],
        "reviews": [{
            "week_start": str(r.week_start),
            "my_reflection": r.reflection_a if is_a else r.reflection_b,
            "partner_reflection": r.reflection_b if is_a else r.reflection_a,
        } for r in reviews],
        "photos": [{
            "id": p.id, "date": str(p.date), "author_id": p.author_id,
            "data": p.data, "caption": p.caption,
        } for p in photos],
        "diary": [{
            "date": str(d.date), "author_id": d.author_id,
            "content": d.content, "mood": d.mood,
        } for d in diary],
    }


# ---- EXISTING QUIZ API (unchanged) ----

@app.post("/api/start")
def api_start(body: dict = {}, db: Session = Depends(get_db)):
    profile_id = body.get("profile_id", "")
    if not profile_id or profile_id not in PROFILES:
        raise HTTPException(status_code=400, detail="profile_id é obrigatório")
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


# ---- ADMIN ────────────────────────────────────────────────────

@app.post("/api/admin/couple/stats")
def admin_couple_stats(body: dict, db: Session = Depends(get_db)):
    check_admin(body)
    couples = db.query(Couple).all()
    result = []
    for c in couples:
        diary_count = db.query(DiaryEntry).filter(DiaryEntry.couple_id == c.id).count()
        photo_count = db.query(Photo).filter(Photo.couple_id == c.id).count()
        question_count = db.query(DailyQuestion).filter(DailyQuestion.couple_id == c.id).count()
        challenge_count = db.query(Challenge).filter(Challenge.couple_id == c.id).count()
        todo_count = db.query(TodoItem).filter(TodoItem.couple_id == c.id).count()
        event_count = db.query(AgendaEvent).filter(AgendaEvent.couple_id == c.id).count()
        review_count = db.query(WeeklyReview).filter(WeeklyReview.couple_id == c.id).count()
        result.append({
            "couple_id": c.id, "user1": c.user1_id, "user2": c.user2_id,
            "diary": diary_count, "photos": photo_count, "questions": question_count,
            "challenges": challenge_count, "todos": todo_count, "events": event_count,
            "reviews": review_count,
        })
    return {"couples": result}


@app.post("/api/admin/couple/questions")
def admin_couple_questions(body: dict, db: Session = Depends(get_db)):
    check_admin(body)
    couple_id = body.get("couple_id", "")
    q = db.query(DailyQuestion)
    if couple_id:
        q = q.filter(DailyQuestion.couple_id == couple_id)
    questions = q.order_by(DailyQuestion.date.desc()).limit(100).all()
    return {"questions": [{
        "id": q.id, "couple_id": q.couple_id, "date": str(q.date),
        "question_pt": q.question_pt, "question_en": q.question_en,
        "answer_a": q.answer_a, "answer_b": q.answer_b,
    } for q in questions]}


@app.post("/api/admin/couple/question/save")
def admin_couple_question_save(body: dict, db: Session = Depends(get_db)):
    check_admin(body)
    qid = body.get("id")
    couple_id = body.get("couple_id", "")
    date_str = body.get("date", "")
    question_pt = body.get("question_pt", "")
    question_en = body.get("question_en", "")
    if qid:
        q = db.query(DailyQuestion).filter(DailyQuestion.id == qid).first()
        if q:
            q.question_pt = question_pt
            q.question_en = question_en
            if date_str: q.date = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
    elif couple_id and date_str:
        q = DailyQuestion(
            couple_id=couple_id, date=datetime.strptime(date_str[:10], "%Y-%m-%d").date(),
            question_pt=question_pt, question_en=question_en
        )
        db.add(q)
    db.commit()
    return {"ok": True}


@app.post("/api/admin/couple/challenges")
def admin_couple_challenges(body: dict, db: Session = Depends(get_db)):
    check_admin(body)
    couple_id = body.get("couple_id", "")
    q = db.query(Challenge)
    if couple_id:
        q = q.filter(Challenge.couple_id == couple_id)
    challenges = q.order_by(Challenge.date.desc()).limit(100).all()
    return {"challenges": [{
        "id": c.id, "couple_id": c.couple_id, "date": str(c.date),
        "type": c.type, "data": c.data,
        "created_by": c.created_by, "done_a": c.done_a, "done_b": c.done_b,
    } for c in challenges]}


@app.post("/api/admin/couple/photos")
def admin_couple_photos(body: dict, db: Session = Depends(get_db)):
    check_admin(body)
    couple_id = body.get("couple_id", "")
    q = db.query(Photo)
    if couple_id:
        q = q.filter(Photo.couple_id == couple_id)
    photos = q.order_by(Photo.date.desc()).limit(100).all()
    return {"photos": [{
        "id": p.id, "couple_id": p.couple_id, "author_id": p.author_id,
        "date": str(p.date), "caption": p.caption, "data": p.data[:100] + "..." if len(p.data) > 100 else p.data,
    } for p in photos]}


@app.post("/api/admin/couple/diary")
def admin_couple_diary(body: dict, db: Session = Depends(get_db)):
    check_admin(body)
    couple_id = body.get("couple_id", "")
    q = db.query(DiaryEntry)
    if couple_id:
        q = q.filter(DiaryEntry.couple_id == couple_id)
    entries = q.order_by(DiaryEntry.date.desc()).limit(100).all()
    return {"entries": [{
        "id": e.id, "couple_id": e.couple_id, "author_id": e.author_id,
        "date": str(e.date), "content": e.content[:200], "mood": e.mood,
    } for e in entries]}


@app.post("/api/admin/couple/diary/delete")
def admin_couple_diary_delete(body: dict, db: Session = Depends(get_db)):
    check_admin(body)
    entry_id = body.get("id")
    if not entry_id:
        raise HTTPException(status_code=400, detail="id obrigatório")
    db.query(DiaryEntry).filter(DiaryEntry.id == entry_id).delete()
    db.commit()
    return {"ok": True}


@app.post("/api/admin/couple/agenda")
def admin_couple_agenda(body: dict, db: Session = Depends(get_db)):
    check_admin(body)
    couple_id = body.get("couple_id", "")
    q = db.query(AgendaEvent)
    if couple_id:
        q = q.filter(AgendaEvent.couple_id == couple_id)
    events = q.order_by(AgendaEvent.date.desc()).limit(100).all()
    return {"events": [{
        "id": e.id, "couple_id": e.couple_id, "title": e.title,
        "date": str(e.date)[:16], "description": e.description, "created_by": e.created_by,
    } for e in events]}


@app.post("/api/admin/couple/todos")
def admin_couple_todos(body: dict, db: Session = Depends(get_db)):
    check_admin(body)
    couple_id = body.get("couple_id", "")
    q = db.query(TodoItem)
    if couple_id:
        q = q.filter(TodoItem.couple_id == couple_id)
    todos = q.order_by(TodoItem.created_at.desc()).limit(100).all()
    return {"todos": [{
        "id": t.id, "couple_id": t.couple_id, "title": t.title,
        "description": t.description, "done": t.done, "done_by": t.done_by,
        "created_by": t.created_by,
    } for t in todos]}


@app.post("/api/admin/results")
def admin_results(body: dict, db: Session = Depends(get_db)):
    check_admin(body)
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
    check_admin(body)
    events = db.query(LoginEvent).order_by(LoginEvent.timestamp.desc()).limit(500).all()
    return {"events": [{"profile_id": e.profile_id, "timestamp": str(e.timestamp)[:19] if e.timestamp else ""} for e in events]}


@app.post("/api/admin/profiles")
def admin_get_profiles(body: dict, db: Session = Depends(get_db)):
    check_admin(body)
    result = {}
    for p in db.query(Profile).all():
        result[p.id] = {"type": p.type, "display_name": p.display_name, **p.data}
    return {"profiles": result, "template": NEW_PROFILE_TEMPLATE}


@app.post("/api/admin/profiles/save")
def admin_save_profiles(body: dict, db: Session = Depends(get_db)):
    check_admin(body)
    new_profiles = body.get("profiles", {})
    for pid, pd in new_profiles.items():
        existing = db.query(Profile).filter(Profile.id == pid).first()
        if existing:
            existing.data = {k: v for k, v in pd.items() if k not in ("password", "type", "display_name")}
            if "type" in pd: existing.type = pd["type"]
            if "display_name" in pd: existing.display_name = pd["display_name"]
    db.commit()
    reload_profiles(db)
    return {"ok": True}


@app.post("/api/admin/profiles/reset-sessions")
def admin_reset_sessions(body: dict, db: Session = Depends(get_db)):
    check_admin(body)
    profile_id = body.get("profile_id", "")
    if not profile_id:
        raise HTTPException(status_code=400, detail="profile_id é obrigatório")
    deleted = db.query(QuizSession).filter(QuizSession.profile_id == profile_id).delete()
    db.commit()
    return {"ok": True, "deleted": deleted}


@app.post("/api/admin/profiles/delete")
def admin_delete_profile(body: dict, db: Session = Depends(get_db)):
    check_admin(body)
    profile_id = body.get("profile_id", "")
    if not profile_id or profile_id not in PROFILES:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    db.query(LoginCredential).filter(LoginCredential.profile_id == profile_id).delete()
    db.query(QuizSession).filter(QuizSession.profile_id == profile_id).delete()
    db.query(Profile).filter(Profile.id == profile_id).delete()
    db.commit()
    reload_profiles(db)
    return {"ok": True}


@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    return HTMLResponse(_render("admin.html"))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
