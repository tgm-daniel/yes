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

ADMIN_USER = "ttt"
ADMIN_PASS = "sisrat"


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


# ---- ADMIN ----

@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Admin</title>
<link rel="stylesheet" href="/static/style.css">
<style>
.admin-card { background: var(--white); border-radius: var(--radius); box-shadow: var(--shadow); padding: 32px 24px; max-width: 600px; margin: 40px auto; text-align: center; border: 2px solid rgba(255,181,194,0.3); }
.admin-login { display: flex; flex-direction: column; gap: 14px; margin-top: 20px; }
.admin-login input { width: 100%; padding: 14px 18px; font-family: 'Press Start 2P', monospace; font-size: 10px; color: var(--text); background: var(--cream); border: 2px solid rgba(255,181,194,0.3); border-radius: var(--radius-sm); outline: none; box-sizing: border-box; text-align: center; }
.admin-login input:focus { border-color: var(--pink); box-shadow: 0 0 0 3px rgba(255,143,160,0.15); }
.admin-login .btn { margin-top: 4px; }
.admin-error { font-family: 'Press Start 2P', monospace; font-size: 8px; color: var(--pink-dark); min-height: 20px; }
#resultsWrap { display: none; margin-top: 30px; text-align: left; }
.session-card { background: var(--cream); border-radius: var(--radius-sm); padding: 16px 20px; margin-bottom: 16px; border: 2px solid rgba(255,181,194,0.2); }
.session-card h3 { font-family: 'Press Start 2P', monospace; font-size: 9px; color: var(--pink-dark); margin: 0 0 8px; }
.session-card .meta { font-size: 0.85rem; color: var(--text-light); margin-bottom: 8px; }
.session-card table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.session-card td { padding: 6px 4px; border-bottom: 1px solid rgba(255,181,194,0.15); vertical-align: top; }
.session-card td:first-child { font-weight: 700; color: var(--text); width: 40%; }
.session-card td:last-child { color: var(--text-light); }
.correct-row td:last-child { color: #6b9e7a; }
.wrong-row td:last-child { color: var(--pink-dark); }
.no-sessions { text-align: center; color: var(--text-light); font-size: 0.9rem; padding: 40px 0; }
</style>
</head>
<body>
<div class="floating-bg"></div>
<div class="container">
  <div class="admin-card">
    <div class="card-heart">
      <svg viewBox="-10 -10 140 130" width="28" height="28">
        <defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#ffb5c2"/><stop offset="100%" stop-color="#ff8fa0"/></linearGradient>
        <filter id="s" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#ff8fa0" flood-opacity="0.3"/></filter></defs>
        <path d="M60 100 C20 70 0 50 0 30 C0 12 15 0 30 0 C40 0 50 8 60 20 C70 8 80 0 90 0 C105 0 120 12 120 30 C120 50 100 70 60 100Z" fill="url(#g)" filter="url(#s)"/>
      </svg>
    </div>
    <h1 class="title"><span class="title-highlight">Admin</span></h1>
    <div class="title-sub">acesso restrito</div>
    <div class="admin-login">
      <input type="text" id="adminUser" placeholder="usuário" autocomplete="off">
      <input type="password" id="adminPass" placeholder="senha">
      <div class="admin-error" id="adminError"></div>
      <button class="btn btn-primary" id="adminBtn" onclick="adminLogin()">entrar 🔐</button>
    </div>
    <div id="resultsWrap"></div>
  </div>
</div>
<script>
async function adminLogin() {
  const u=document.getElementById('adminUser').value.trim();
  const p=document.getElementById('adminPass').value;
  const err=document.getElementById('adminError');
  const btn=document.getElementById('adminBtn');
  err.textContent=''; btn.innerHTML='<span class=spinner></span>'; btn.disabled=true;
  try {
    const r=await fetch('/api/admin/results',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
    if(!r.ok){const d=await r.json();throw new Error(d.detail||'Erro')}
    const data=await r.json();
    document.querySelector('.admin-login').style.display='none';
    const w=document.getElementById('resultsWrap');
    w.style.display='block';
    if(data.sessions.length===0){w.innerHTML='<div class=no-sessions>Nenhum quiz respondido ainda.</div>';return}
    let h='';
    for(const s of data.sessions){
      const pct=Math.round((s.score/(s.total||1))*100);
      h+='<div class=session-card><h3>'+s.profile_id+'</h3><div class=meta>'+s.score+'/'+s.total+' ('+pct+'%) &mdash; '+s.started_at+'</div><table>';
      for(const a of s.answers){
        const cls=a.was_correct?'correct-row':'wrong-row';
        h+='<tr class='+cls+'><td>'+a.question+'</td><td>'+(a.was_correct?'✅ '+a.fun_fact:'❌ '+a.selected)+'</td></tr>';
      }
      h+='</table></div>';
    }
    w.innerHTML=h;
  } catch(e){err.textContent=e.message;btn.innerHTML='entrar 🔐';btn.disabled=false}
}
</script>
</body>
</html>"""
    return HTMLResponse(html)


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
            q = qmap.get(a["question_id"], {})
            ans_data.append({
                "question": q.get("question", "?"),
                "selected": (q.get("options", []) + ["?"])[a["selected"]] if a["selected"] < len(q.get("options", [])) else "?",
                "was_correct": a["correct"],
                "fun_fact": q.get("fun_fact", ""),
            })
        result.append({
            "session_id": s.id,
            "profile_id": s.profile_id,
            "score": s.score,
            "total": len(questions),
            "started_at": str(s.started_at)[:19] if s.started_at else "",
            "answers": ans_data,
        })

    return {"sessions": result}
