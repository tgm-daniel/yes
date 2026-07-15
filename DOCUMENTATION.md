# Still Learning — Complete Product Documentation

> **Version:** 2.1  
> **Target Audience:** Couples in serious relationships (dating, engaged, married)  
> **Stack:** Python 3.11+ / FastAPI / SQLAlchemy / SQLite (dev) / PostgreSQL (prod) / bcrypt + JWT  
> **Production URL:** `https://still-learning.onrender.com`

---

## Table of Contents

1. [Complete System Architecture](#1-complete-system-architecture)
2. [Navigation Flow](#2-navigation-flow)
3. [User Journey](#3-user-journey)
4. [Text Wireframes](#4-text-wireframes)
5. [Page Structure](#5-page-structure)
6. [Reusable Components](#6-reusable-components)
7. [Design System](#7-design-system)
8. [Visual Guide](#8-visual-guide)
9. [Database Structure](#9-database-structure)
10. [APIs](#10-apis)
11. [AI Structure](#11-ai-structure)
12. [Development Roadmap](#12-development-roadmap)
13. [Launch Roadmap](#13-launch-roadmap)
14. [Growth Strategy](#14-growth-strategy)
15. [Monetization Strategy](#15-monetization-strategy)
16. [Retention Strategy](#16-retention-strategy)
17. [Improvement Checklist](#17-improvement-checklist)
18. [Prioritized Backlog](#18-prioritized-backlog)
19. [Product Evolution Plan](#19-product-evolution-plan)
20. [Risk List](#20-risk-list)
21. [Metrics (KPIs)](#21-metrics-kpis)
22. [A/B Testing Plan](#22-ab-testing-plan)
23. [Accessibility Plan](#23-accessibility-plan)
24. [Security Plan](#24-security-plan)
25. [SEO Plan](#25-seo-plan)
26. [Internationalization Plan](#26-internationalization-plan)

---

## 1. Complete System Architecture

### 1.1 Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                             │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐            │
│  │index.html│  │couple.html   │  │ admin.html        │            │
│  │(login)   │  │(couple app)  │  │ (admin panel)     │            │
│  └──────────┘  └──────────────┘  └───────────────────┘            │
│         │              │               │                           │
│         └──────────────┴───────────────┘                           │
│                            │ HTTP/HTTPS                            │
│                    fetch() / api() wrapper                     │
│                            │                                       │
│                    JWT Bearer Token                                │
└──────────────────────────────────────────────────────┬──────────────┘
                                                       │
┌──────────────────────────────────────────────────────▼──────────────┐
│                    SERVER (FastAPI / Uvicorn)                        │
│                                                                     │
│  ┌──────────────┐  ┌────────────────┐  ┌─────────────────────────┐ │
│  │  Middleware   │  │  require_auth  │  │  check_admin            │ │
│  │  (CORS, etc) │  │  (JWT Bearer)  │  │  (admin credentials)    │ │
│  └──────────────┘  └────────────────┘  └─────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    API ROUTES (53 endpoints)                 │  │
│  │  ┌─────────┐ ┌──────────────┐ ┌──────────────────────────┐  │  │
│  │  │Auth API │ │Couple API    │ │Admin API                 │  │  │
│  │  │  1 route│ │ 28 routes    │ │ 22 routes                │  │  │
│  │  └─────────┘ └──────────────┘ └──────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              DATA LAYER                                      │  │
│  │  ┌─────────────────┐  ┌──────────────────────────────────┐   │  │
│  │  │   SQLAlchemy    │  │  models.py (13 tables)           │   │  │
│  │  │   ORM + Alembic │  │  Profile, LoginCredential,       │   │  │
│  │  └─────────────────┘  │  Couple, DiaryEntry,             │   │  │
│  │                       │  DailyQuestion, Challenge,        │   │  │
│  │  ┌─────────────────┐  │  AgendaEvent, TodoItem,          │   │  │
│  │  │  database.py    │  │  WeeklyReview, QuizAnswer,       │   │  │
│  │  │  engine/session │  │  QuoteRefresh, Photo, LoginEvent │   │  │
│  │  └─────────────────┘  └──────────────────────────────────┘   │  │
│  │                       ┌──────────┐                           │  │
│  │                       │ SQLite / │                           │  │
│  │                       │PostgreSQL│                           │  │
│  │                       └──────────┘                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              STATIC ASSETS (PWA)                             │  │
│  │  ┌───────────┐  ┌──────────┐  ┌──────────┐                 │  │
│  │  │style.css  │  │ sw.js    │  │manifest  │  icons/         │  │
│  │  │           │  │(service  │  │.json     │  (SVG)          │  │
│  │  │           │  │ worker)  │  │          │                 │  │
│  │  └───────────┘  └──────────┘  └──────────┘                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              TRANSLATION LAYER                               │  │
│  │  translations.py (449 lines, ~100 keys, 200 questions       │  │
│  │  + 80 suggestions + 30 quotes + themes, in PT and EN)        │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Detailed Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Runtime | Python 3.11+ | 3.11 |
| Web Framework | FastAPI | 0.104+ |
| ASGI Server | Uvicorn | 0.24+ |
| ORM | SQLAlchemy | 2.0+ |
| DB (dev) | SQLite | 3.x |
| DB (prod) | PostgreSQL | 15+ |
| Authentication | bcrypt + PyJWT | bcrypt 4.1+, PyJWT 2.0+ |
| Templates | HTML + inline JS (server-side string replace) | — |
| Frontend | Vanilla JS + custom CSS | — |
| PWA | Service Worker + Manifest | W3C |
| Deploy | Render (free tier) | — |

### 1.3 Template Architecture (Server-Side Rendering)

The system uses an extremely lightweight template engine (`_render()`) that:
1. Reads the HTML file from the `templates/` directory
2. Replaces `{{ key }}` with dictionary values
3. Returns the HTML as `HTMLResponse`
4. Everything else is rendered via client-side JavaScript (SPA-like)

### 1.4 Template Architecture

```
templates/
├── index.html       → Login (entry point)          ──→ Login Flow
├── couple.html      → Main app (SPA-like)           ──→ Couple Flow
└── admin.html       → Administrative panel           ──→ Admin
```

### 1.5 File Structure

```
project quiz code/
├── .env                   → Environment variables
├── .gitignore
├── requirements.txt       → Python dependencies
├── database.py            → SQLAlchemy engine + SessionLocal
├── models.py              → 13 ORM models
├── main.py                → 53 endpoints + all logic
├── translations.py        → Internationalization (PT/EN) 431 lines
├── profiles.json          → Login data (migrated to DB on first run)
├── quiz.db                → SQLite local (dev)
├── static/
│   ├── style.css          → Main CSS (~600 lines)
│   ├── manifest.json      → PWA manifest
│   ├── sw.js              → Service Worker
│   └── icons/
│       ├── icon-192.svg
│       └── icon-512.svg
└── templates/
    ├── index.html
    ├── couple.html        → ~2250 lines (JS + CSS + HTML)
    └── admin.html         → ~1800 lines (JS + CSS + HTML)
```

---

## 2. Navigation Flow

### 2.1 General Flow

```
                    ┌──────────────┐
                    │   / (index)  │
                    │   Login     │
                    │   Screen    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  /still-    │
                    │  learning   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────────────┐
                    │ 3-Item Bottom Nav   │
                    │ ┌────┬────┬─────┐   │
                    │ │Home│ Us │ ⚙️  │   │
                    │ └────┴────┴─────┘   │
                    └─────────────────────┘
```

### 2.2 Internal Navigation (couple.html — SPA)

```
Home ────────────────────────────────────────────────
  ├── Dashboard (cards: greeting, stats, notifications)
  ├── Daily Question (answer / see response)
  ├── Daily Challenge (start / complete)
  ├── Daily Quote (read / navigate)
  ├── Agenda (view / add events)
  ├── To-Dos (view / add / mark)
  └── Weekly Review (write reflection)

Us ─────────────────────────────────────────────────
  ├── Diary (write / read entries)
  ├── Memories (photos + questions + challenges)
  ├── Couple Quiz (questions about self/partner)
  └── Challenge (shortcut to current challenge)

⚙️ (modal) ───────────────────────────────────────
  ├── Language (PT ↔ EN)
  └── Logout (logout + clear localStorage)
```

### 2.3 Data Flow

```
Login → JWT → localStorage.setItem('auth_token')
   ↓
Each fetch() → Authorization: Bearer <token>
   ↓
require_auth() → decodes JWT → extracts couple_id, login_name
   ↓
Dashboard → GET /api/couple/dashboard
   ↓
Cards → each section calls its specific endpoint
   ↓
Responses → POST /api/couple/... (with JWT in header)
```

---

## 3. User Journey

### 3.1 First Access (Digital Marriage)

```
1. User accesses still-learning.onrender.com
2. Types login name + password
3. System verifies bcrypt (with legacy SHA-256 fallback)
4. Generates JWT (48h validity)
5. Redirects to /still-learning
6. Dashboard is displayed with daily cards
```

### 3.2 Daily Journey

```
Morning:
  └── Opens app → Home
      ├── Sees personalized greeting
      ├── Sees daily stats (diary, challenge, tasks)
      └── Reads daily quote 💕

Afternoon:
  └── Opens app → Home → Daily Question
      ├── Reads question
      ├── Writes answer
      └── Waits for partner to answer

Evening:
  └── Opens app → Us → Diary
      ├── Writes about the day
      └── Chooses mood (emoji)
```

### 3.3 Weekly Journey

```
Monday:
  └── Home → Weekly Review
      ├── New question available
      └── Writes weekly reflection

Throughout the week:
  └── Us → Challenge → types vary:
      ├── Riddle (guess the answer)
      ├── Intimate Question (created by partner)
      ├── Custom Challenge (photo, text, audio)
      ├── Photo Challenge (take a themed photo)
      └── Quote (reflect together)
```

### 3.4 Memories Flow

```
Us → Memories
  ├── Answered daily questions
  ├── Completed challenges
  ├── Photos sent
  ├── Diary entries
  └── Weekly reviews
```

---

## 4. Text Wireframes

### 4.1 Login Screen

```
┌───────────────────────────────────────┐
│  ┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐    │
│    S T I L L   L E A R N I N G        │
│  └─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘    │
│                                       │
│         [✨] [💕] [💑]                │
│                                       │
│    ┌─────────────────────────────┐    │
│    │  your name                  │    │
│    └─────────────────────────────┘    │
│    ┌─────────────────────────────┐    │
│    │  password                   │    │
│    └─────────────────────────────┘    │
│                                       │
│    ┌─────────────────────────────┐    │
│    │      Enter 💕               │    │
│    └─────────────────────────────┘    │
│                                       │
│    [PT]                [EN]           │
│                                       │
│   "Learning from each other,          │
│    one day at a time"                 │
└───────────────────────────────────────┘
```

### 4.2 Dashboard (Home)

```
┌───────────────────────────────────────┐
│ [💕] ✨ Still Learning ✨     [EN]    │
│  Learning from each other...          │
│ ✦ T ✦                               │
├───────────────────────────────────────┤
│ ┌─────────────────────────────────┐   │
│ │ [💕] Hello, T 💕                │   │
│ │      What shall we do today?    │   │
│ └─────────────────────────────────┘   │
│                                       │
│ ┌──────┐ ┌──────┐ ┌──────┐           │
│ │Diary │ │Chall │ │Tasks │           │
│ │  3   │ │  ✓   │ │  1   │           │
│ └──────┘ └──────┘ └──────┘           │
│                                       │
│ ┌─────────────────────────────────┐   │
│ │ 💭  Daily Question        View  │   │
│ │      Answered ✅                │   │
│ └─────────────────────────────────┘   │
│ ┌─────────────────────────────────┐   │
│ │ 📖  Our Diary             ✏️   │   │
│ │      2 entries today            │   │
│ └─────────────────────────────────┘   │
│ ┌─────────────────────────────────┐   │
│ │ 🎯  Today's Challenge    Start  │   │
│ │      Type: riddle               │   │
│ └─────────────────────────────────┘   │
│ ┌─────────────────────────────────┐   │
│ │ 💌  Daily Quote           Read  │   │
│ │      "Love cannot be seen..."   │   │
│ └─────────────────────────────────┘   │
│ ┌─────────────────────────────────┐   │
│ │ 📅  Upcoming Events       View  │   │
│ │      Nothing scheduled          │   │
│ └─────────────────────────────────┘   │
├───────────────────────────────────────┤
│ [🏠 Home]  [💑 Us]    [⚙️]         │
└───────────────────────────────────────┘
```

### 4.3 Us Section

```
┌───────────────────────────────────────┐
│ [💕] ✨ Still Learning ✨     [EN]    │
├───────────────────────────────────────┤
│         💑 Us                         │
│  Our memories and moments             │
│                                       │
│  ┌──────────┐  ┌──────────┐          │
│  │   📖     │  │   ✨     │          │
│  │  Diary   │  │ Memories │          │
│  │Entries.. │  │Photos... │          │
│  └──────────┘  └──────────┘          │
│  ┌──────────┐  ┌──────────┐          │
│  │   ❓     │  │   🎯     │          │
│  │   Quiz   │  │Challenge │          │
│  │Tests...  │  │Current.. │          │
│  └──────────┘  └──────────┘          │
├───────────────────────────────────────┤
│ [🏠 Home]  [💑 Us]    [⚙️]         │
└───────────────────────────────────────┘
```

### 4.4 Settings (⚙️ Modal)

```
┌───────────────────────────────────────┐
│              ╔═══════════╗            │
│              ║    💕     ║            │
│              ╚═══════════╝            │
│         Still Learning                │
│                                       │
│  ┌───────────────────────────────┐    │
│  │         🌐                   │    │
│  │        Language              │    │
│  │    🇧🇷 Português             │    │
│  └───────────────────────────────┘    │
│  ┌───────────────────────────────┐    │
│  │         🚪                   │    │
│  │         Logout               │    │
│  │     Disconnect               │    │
│  └───────────────────────────────┘    │
└───────────────────────────────────────┘
```

### 4.5 Daily Question

```
┌───────────────────────────────────────┐
│ [💕]          ← Back                 │
├───────────────────────────────────────┤
│    💭 Daily Question                  │
│                                       │
│  ┌─────────────────────────────────┐  │
│  │ "What did you learn about me    │  │
│  │  this week that you didn't      │  │
│  │  know?"                         │  │
│  └─────────────────────────────────┘  │
│                                       │
│  ┌─────────────────────────────────┐  │
│  │  Your answer:                   │  │
│  │  ┌─────────────────────────┐    │  │
│  │  │                         │    │  │
│  │  │  Write here...          │    │  │
│  │  │                         │    │  │
│  │  └─────────────────────────┘    │  │
│  │                                 │  │
│  │  [📤 Send 💕]                  │  │
│  └─────────────────────────────────┘  │
│                                       │
│  ┌─────────────────────────────────┐  │
│  │ 💭 Partner's answer:            │  │
│  │ "I learned that you..."        │  │
│  └─────────────────────────────────┘  │
├───────────────────────────────────────┤
│ [🏠 Home]  [💑 Us]    [⚙️]         │
└───────────────────────────────────────┘
```

### 4.6 Diary

```
┌───────────────────────────────────────┐
│ [💕]          ← Back                 │
├───────────────────────────────────────┤
│    📖 Our Diary 💕                    │
│                                       │
│  ┌─────── Today ─────────────────┐    │
│  │ You: [✏️ Write...]            │    │
│  │        How are you feeling?    │    │
│  │        [😊] [😢] [😍] [😴]    │    │
│  │ Partner: Hasn't written yet   │    │
│  └─────────────────────────────────┘  │
│  ┌─────── Previous Days ──────────┐   │
│  │  12/07 - You wrote:            │   │
│  │  "Today was an incredible..."  │   │
│  │  11/07 - Partner wrote:        │   │
│  │  "I love our moments..."       │   │
│  └─────────────────────────────────┘  │
├───────────────────────────────────────┤
│ [🏠 Home]  [💑 Us]    [⚙️]         │
└───────────────────────────────────────┘
```

---

## 5. Page Structure

### 5.1 Structural HTML

Each page follows the same skeleton:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="theme-color" content="#ffb5c2">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <link rel="manifest" href="/static/manifest.json">
  <link rel="apple-touch-icon" href="/static/icons/icon-192.svg">
  <title>Still Learning 💕</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <div class="floating-bg"></div>
  <!-- PAGE-SPECIFIC CONTENT -->
  <script>
    // Page-specific JS + service worker registration
  </script>
</body>
</html>
```

### 5.2 couple.html — Internal Structure

```html
<body>
  <div class="floating-bg"></div>

  <div id="app">
    <div class="app-header">         <!-- Fixed header -->
      <div class="card-heart">💕</div>
      <button class="lang-toggle">EN</button>
      <h1>✨ Still Learning ✨</h1>
      <div class="subtitle">...</div>
    </div>
    <div id="userGreeting"></div>    <!-- User name -->
    <div id="mainContent"></div>     <!-- Dynamic content -->
  </div>

  <div class="nav-bar">              <!-- Fixed 3-item nav -->
    Home | Us | ⚙️
  </div>

  <div class="modal-overlay">        <!-- Settings Modal -->
    Language + Logout
  </div>

  <script>
    // ~1500 lines of JS: api(), showSection(), loadDashboard(),
    // loadDiary(), loadQuestion(), loadChallenge(), loadQuiz(),
    // loadMemories(), loadAgenda(), loadTodos(), loadReview(),
    // toggleLang(), logout(), init()
  </script>
</body>
```

### 5.3 admin.html — Internal Structure

```html
<body>
  <div class="admin-container">
    <div class="admin-sidebar">     <!-- Admin navigation -->
      Stats | Profiles | Couples | Questions | Challenges | ...
    </div>
    <div class="admin-content">     <!-- Dynamic content -->
      <div id="adminMain"></div>
    </div>
  </div>

  <script>
    // ~1800 lines: stats loading, profile CRUD,
    // couple management, data visualization
  </script>
</body>
```

---

## 6. Reusable Components

### 6.1 Frontend (Vanilla JS)

| Component | Location | Description |
|-----------|----------|-------------|
| `api(path, opts)` | couple.html:665 | Fetch wrapper with JWT + headers + automatic JSON |
| `showSection(name)` | couple.html:718 | SPA navigation (swaps content + active nav) |
| `backLink()` | couple.html:718 | Standardized "← Back" button |
| `esc(s)` / `attrEsc(s)` | couple.html:684 | HTML + attribute sanitization (escapes quotes/single quotes) |
| `toggleLang()` | couple.html:679 | PT/EN toggle with cookie + reload |
| `logout(e)` | couple.html:686 | Cleanup + redirect |
| `toggleSettings()` | couple.html:712 | Open/close settings modal |
| `toast(msg)` | couple.html:2207 | Non-intrusive floating toast (3s) |
| `markDirty()` | admin.html | Marks form as unsaved |

### 6.2 Backend (Python)

| Component | File | Description |
|-----------|------|-------------|
| `_render(name, **kwargs)` | main.py:186 | Homemade template engine |
| `require_auth()` | main.py:110 | Authentication Dependency Injection (JWT Bearer only) |
| `check_admin()` | main.py:128 | Admin validation (credentials via env var) |
| `get_couple_info()` | main.py:205 | Returns `(is_primary, partner_name)` by querying the Couple table |
| `_profile_name()` | main.py:219 | Resolves display name for a profile |
| `hash_pw()` / `verify_pw()` | main.py:68 | bcrypt hash/verification + SHA-256 fallback |
| `create_jwt()` / `decode_jwt()` | main.py:82 | JWT generation/validation |
| `get_db()` | database.py:26 | SQLAlchemy session manager |
| `get_quote()` | main.py:708 | Returns daily quote with offset control |
| `lifespan()` | main.py:176 | Startup/shutdown events (lifespan) |

### 6.3 Reusable CSS (style.css)

```css
/* Color system (CSS variables) */
:root {
  --pink: #ffb5c2;
  --pink-dark: #e88a9a;
  --cream: #fff5f5;
  --text: #4a4a4a;
  --text-light: #b0a0a0;
  --bg: #fdf6f0;
  --radius-sm: 10px;
  --radius-cloud: 18px;
  --shadow: 0 4px 20px rgba(255, 181, 194, 0.2);
  --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* Key components */
.card { /* card with white bg, shadow, rounded borders */ }
.card-heart { /* decorative SVG heart at top */ }
.card-text { /* descriptive text inside card */ }
.card-row { /* flexible row in card */ }
.card-action { /* action button in card */ }
.stat-pill { /* stat pill (e.g., Diary: 3) */ }
.notif-card { /* notification card */ }
.loading + .spinner { /* loading state */ }
.empty-state { /* empty state */ }
.btn, .btn-primary, .btn-outline { /* button system */ }
.modal-overlay + .modal-box { /* generic modal */ }
.nav-bar + .nav-item { /* bottom navigation */ }
.more-card { /* menu card */ }
.diary-entry { /* diary entry */ }
.question-card { /* daily question */ }
.challenge-card { /* challenge card */ }
.partner-challenge-card { /* partner challenge */ }
.todo-item { /* to-do item */ }
.floating-bg { /* animated background */ }
```

---

## 7. Design System

### 7.1 Core Tokens

```css
:root {
  /* COLORS */
  --pink: #ffb5c2;           /* Primary — pastel pink */
  --pink-dark: #e88a9a;      /* Primary dark — hover/active */
  --cream: #fff5f5;           /* Surface — card background */
  --text: #4a4a4a;            /* Main text */
  --text-light: #b0a0a0;      /* Secondary text */
  --bg: #fdf6f0;              /* Page background — off-white */
  --white: #ffffff;           /* Cards */

  /* SPACING */
  --radius-sm: 10px;          /* Soft corners */
  --radius-cloud: 18px;       /* "Cloud" style corners */
  --radius-round: 50%;        /* Circular elements */

  /* SHADOW */
  --shadow: 0 4px 20px rgba(255, 181, 194, 0.2);

  /* ANIMATION */
  --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

### 7.2 Typography

```css
/* Titles/Header */
font-family: 'Press Start 2P', monospace;   /* Pixelated — nostalgia */
font-size: 9px (mobile), 7px (nav)

/* Body */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
font-size: 0.9rem (default), 0.82rem (secondary)
```

### 7.3 Icons

Exclusive use of Unicode emoji for icons (no external dependencies):

| Emoji | Meaning |
|-------|---------|
| 🏠 | Home |
| 💑 | Us |
| ⚙️ | Settings |
| 💕 | Love / App |
| 💭 | Daily Question |
| 📖 | Diary |
| ✨ | Memories |
| 🎯 | Challenge |
| ❓ | Quiz |
| 📅 | Agenda |
| 📋 | To-Dos |
| 💌 | Quote |
| 💪 | Physical challenge |
| 🔔 | Notification |

### 7.4 Grid and Layout

```css
/* Base layout — mobile-first, max-width: 520px */
.section { max-width: 440px; margin: 0 auto; padding: 16px; }

/* 2-column grid (Us) */
display: grid; grid-template-columns: 1fr 1fr; gap: 12px;

/* Stacked cards (Dashboard) */
.card + .card { margin-top: 14px; }
```

---

## 8. Visual Guide

### 8.1 Screens (Text Description)

| Screen | Palette | Main Elements | Tone |
|--------|---------|--------------|------|
| Login | Pink + Off-white | Rounded inputs, gradient button, SVG heart | Welcoming, romantic |
| Dashboard (Home) | Pink + White | Cards with shadows, stat pills, action buttons | Informative, inviting |
| Us | Pink + White | 2×2 grid with "more-cards" | Navigational |
| Daily Question | Pink + Off-white | Question card, textarea, send button | Intimate, reflective |
| Diary | Pink + White | "Today" section + day timeline | Personal, nostalgic |
| Challenge | Pink + Off-white | Instructions, input/submission, status | Fun, interactive |
| Memories | Pink + White | Accordion sections (questions, challenges, etc.) | Nostalgic |
| Settings (Modal) | White + Pink | Semi-transparent overlay, action cards | Clean, minimalist |
| Admin | Gray + Dark blue | Sidebar, tables, inputs, action buttons | Technical, utilitarian |

### 8.2 Responsive Behavior

```
Desktop (>768px):
  max-width: 520px; margin: 0 auto;
  Content centered as card

Mobile (<768px):
  Full width with 16px padding
  Fixed bottom nav
  Fixed top header

Small mobile (<375px):
  font-size reduced by 10-15%
  Nav with smaller padding
  Reduced spacing
```

---

## 9. Database Structure

### 9.1 Entity Diagram

```
┌──────────────────┐       ┌──────────────────────┐
│     Profile      │       │   LoginCredential     │
├──────────────────┤       ├──────────────────────┤
│ id (PK)          │◄──────│ id (PK)              │
│ type             │       │ login_name (UNIQUE)   │
│ display_name     │       │ profile_id (FK)       │
│ data (JSON)      │       │ password_hash         │
│ created_at       │       └──────────────────────┘
└──────────────────┘
        │
        │ 1:1 via couple_id
        ▼
┌──────────────────┐       ┌──────────────────────┐
│      Couple      │       │     DiaryEntry        │
├──────────────────┤       ├──────────────────────┤
│ id (PK)          │──┐    │ id (PK)              │
│ user1_id         │  │    │ couple_id (FK) ✦     │
│ user2_id         │  │    │ author_id             │
│ created_at       │  │    │ date                  │
└──────────────────┘  │    │ content (TEXT)        │
                      │    │ mood                  │
                      │    │ created_at            │
                      │    └──────────────────────┘
                      │    ┌──────────────────────────┐
                      │    │     DailyQuestion         │
                      │    ├──────────────────────────┤
                      │    │ id (PK)                  │
                      ├────│ couple_id (FK) ✦         │
                      │    │ date                     │
                      │    │ question_pt              │
                      │    │ question_en              │
                      │    │ answer_a (TEXT)          │
                      │    │ answer_b (TEXT)          │
                      │    │ seen_by_a / seen_by_b    │
                      │    └──────────────────────────┘
                      │    ┌──────────────────────────┐
                      │    │       Challenge           │
                      │    ├──────────────────────────┤
                      ├────│ couple_id (FK) ✦         │
                      │    │ date                     │
                      │    │ type                     │
                      │    │ data (JSON)              │
                      │    │ created_by               │
                      │    │ guess_a / guess_b (TEXT) │
                      │    │ answered_a / answered_b  │
                      │    │ seen_a / seen_b          │
                      │    │ done_a / done_b          │
                      │    └──────────────────────────┘
                      │    ┌──────────────────────────┐
                      │    │       AgendaEvent         │
                      │    ├──────────────────────────┤
                      ├────│ couple_id (FK) ✦         │
                      │    │ title                    │
                      │    │ date (DateTime)          │
                      │    │ description (TEXT)       │
                      │    │ created_by               │
                      │    └──────────────────────────┘
                      │    ┌──────────────────────────┐
                      │    │       TodoItem            │
                      │    ├──────────────────────────┤
                      ├────│ couple_id (FK) ✦         │
                      │    │ title                    │
                      │    │ description (TEXT)       │
                      │    │ done / done_by           │
                      │    │ created_by / created_at  │
                      │    └──────────────────────────┘
                      │    ┌──────────────────────────┐
                      │    │     WeeklyReview          │
                      │    ├──────────────────────────┤
                      ├────│ couple_id (FK) ✦         │
                      │    │ week_start               │
                      │    │ reflection_a (TEXT)      │
                      │    │ reflection_b (TEXT)      │
                      │    │ completed                │
                      │    └──────────────────────────┘
                      │    ┌──────────────────────────┐
                      │    │      QuizAnswer           │
                      │    ├──────────────────────────┤
                      ├────│ couple_id (FK) ✦         │
                      │    │ author_id                │
                      │    │ question_idx             │
                      │    │ category                 │
                      │    │ about_self (TEXT)        │
                      │    │ about_partner (TEXT)     │
                      │    │ created_at               │
                      │    └──────────────────────────┘
                      │    ┌──────────────────────────┐
                      │    │     QuoteRefresh          │
                      │    ├──────────────────────────┤
                      ├────│ couple_id (FK) ✦         │
                      │    │ date                     │
                      │    │ current_offset           │
                      │    │ max_offset               │
                      │    │ unlock_count             │
                      │    │ liked_offset             │
                      │    └──────────────────────────┘
                      │    ┌──────────────────────────┐
                      │    │         Photo             │
                      │    ├──────────────────────────┤
                      ├────│ couple_id (FK) ✦         │
                      │    │ author_id                │
                      │    │ date                     │
                      │    │ data (TEXT - base64)     │
                      │    │ caption                  │
                      │    │ created_at               │
                      │    └──────────────────────────┘
                      │    ┌──────────────────────────┐
                      │    │      LoginEvent           │
                      │    ├──────────────────────────┤
                      │    │ id (PK)                  │
                      │    │ profile_id (FK)          │
                      │    │ timestamp                │
                      │    └──────────────────────────┘
```

### 9.2 Table Summary

| Table | Fields | Primary Key | Foreign Key |
|-------|--------|-------------|-------------|
| profiles | 5 | id (string) | — |
| login_credentials | 3 | id (int) | profile_id |
| login_events | 3 | id (int) | profile_id |
| couples | 4 | id (string) | — |
| diary_entries | 7 | id (int) | couple_id |
| daily_questions | 9 | id (int) | couple_id |
| challenges | 13 | id (int) | couple_id |
| agenda_events | 6 | id (int) | couple_id |
| todo_items | 9 | id (int) | couple_id |
| weekly_reviews | 6 | id (int) | couple_id |
| quiz_answers | 8 | id (int) | couple_id |
| quote_refreshes | 7 | id (int) | couple_id |
| photos | 7 | id (int) | couple_id |

---

## 10. APIs

### 10.1 Authentication

| Method | Route | Request | Response |
|--------|-------|---------|----------|
| POST | `/api/login` | `{name, password}` | `{type, name, couple_id, partner_name, token}` |

### 10.2 Couple App (28 endpoints)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/couple/dashboard` | Full dashboard |
| GET | `/api/couple/question` | Daily question |
| POST | `/api/couple/question/answer` | Answer question |
| POST | `/api/couple/translations` | PT/EN translations |
| GET | `/api/couple/diary` | Diary entries |
| POST | `/api/couple/diary/save` | Save entry |
| GET | `/api/couple/challenge` | Daily challenge |
| POST | `/api/couple/challenge/guess` | Guess (riddle) |
| POST | `/api/couple/challenge/photo` | Photo upload |
| POST | `/api/couple/challenge/create-question` | Create intimate question |
| POST | `/api/couple/challenge/answer-question` | Answer question |
| POST | `/api/couple/challenge/partner/create` | Create custom challenge |
| POST | `/api/couple/challenge/partner/complete` | Complete challenge |
| GET | `/api/couple/challenge/partner` | Custom challenges |
| GET | `/api/couple/challenge/history` | Challenge history |
| GET | `/api/couple/quote` | Daily quote |
| GET | `/api/couple/quiz` | Couple quiz |
| POST | `/api/couple/quiz/save` | Save quiz answer |
| GET | `/api/couple/memories` | Aggregated memories |
| GET | `/api/couple/agenda` | Agenda |
| POST | `/api/couple/agenda/add` | Add event |
| POST | `/api/couple/agenda/delete` | Delete event |
| GET | `/api/couple/todos` | To-Dos |
| POST | `/api/couple/todos/add` | Add task |
| POST | `/api/couple/todos/toggle` | Toggle completion |
| POST | `/api/couple/todos/delete` | Delete task |
| GET | `/api/couple/review` | Weekly review |
| POST | `/api/couple/review/save` | Save review |

### 10.3 Admin API (22 endpoints)

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/admin/couple/stats` | Statistics for all couples |
| POST | `/api/admin/couple/create` | Create new couple |
| POST | `/api/admin/couple/reset` | Reset couple data |
| POST | `/api/admin/couple/delete` | Delete couple + all data |
| POST | `/api/admin/couple/questions` | List daily questions |
| POST | `/api/admin/couple/question/save` | Save daily question |
| POST | `/api/admin/couple/challenges` | List challenges |
| POST | `/api/admin/couple/photos` | List photos |
| POST | `/api/admin/couple/diary` | List diary entries |
| POST | `/api/admin/couple/diary/delete` | Delete entry |
| POST | `/api/admin/couple/agenda` | List agenda |
| POST | `/api/admin/couple/todos` | List to-dos |
| POST | `/api/admin/challenge/delete` | Delete challenge |
| POST | `/api/admin/photo/delete` | Delete photo |
| POST | `/api/admin/photo/data` | Full photo data |
| POST | `/api/admin/agenda/delete` | Delete agenda event |
| POST | `/api/admin/todos/delete` | Delete to-do item |
| POST | `/api/admin/login-history` | Login history |
| POST | `/api/admin/profiles` | List profiles |
| POST | `/api/admin/profiles/save` | Save/edit profile |
| POST | `/api/admin/profiles/delete` | Delete profile |
| GET | `/admin` | Administrative panel (HTML) |

> **Note on the removed quiz system:** The original standalone profile quiz
> was removed in a cleanup. All users now use the couple system.
> The `QuizAnswer` model remains active — it is used by the compatibility
> questionnaire within the couple dashboard (`/api/couple/quiz`).

---

## 11. AI Structure

### 11.1 Current State

The system **does not currently use generative AI or machine learning models**. Everything is based on:

- **Pre-defined content:** 40 daily questions, 41 themes, 18 challenge suggestions, 30 quotes
- **Deterministic rotation:** `daily_offset = (today - COUPLE_START).days % len(translations)` (daily question)
- **Challenge type rotation:** `challenge_types[(today - COUPLE_START).days % 5]`
- **Controlled randomization:** `random.choice()` on themes/suggestions

### 11.2 AI Opportunities

| Feature | AI Type | Priority | Complexity |
|---------|---------|----------|------------|
| Personalized questions based on couple history | LLM (GPT-4 / Claude) | ★★★ | Medium |
| Challenge suggestions based on interests | LLM | ★★☆ | Medium |
| Sentiment analysis of diary entries | NLP (classification) | ★★☆ | Low |
| Automatic weekly diary summary | LLM (summarization) | ★☆☆ | Medium |
| Quote recommendation by mood | Embeddings + Similarity | ★★☆ | Medium |
| Adaptive quiz (questions the partner got wrong) | Conditional logic | ★★★ | Low |
| Communication pattern detection | NLP + Statistics | ★☆☆ | High |

### 11.3 Proposed AI Architecture

```
Frontend → API → main.py → (new) services/ai_service.py
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                    OpenAI API            HuggingFace
                    (GPT-4 Turbo)         (local models)
                         │                     │
                    Rate limiting          Cache (Redis)
                    + Fallback             + Batch
```

---

## 12. Development Roadmap

### 12.1 Version 1.0 — MVP (Current)

- [x] Login with bcrypt + JWT
- [x] Couple dashboard (central card)
- [x] Daily Question (responses revealed after both answer)
- [x] Shared diary
- [x] Challenges (5 types with rotation)
- [x] Event agenda
- [x] Shared To-Do list
- [x] Weekly Review
- [x] Couple Quiz (private + about partner)
- [x] Daily Quote with navigation
- [x] Aggregated memories
- [x] Admin panel (stats, couple CRUD)
- [x] PWA (Service Worker + Manifest)
- [x] PT/EN internationalization
- [x] 3-item bottom nav (Home/Us/⚙️)

### 12.2 Version 2.0 — Connectivity & Engagement

- [ ] Push notifications (Web Push API)
- [ ] Photo sharing with preview
- [ ] AI-generated quiz questions
- [ ] Streak tracking (consecutive days of use)
- [ ] "How many days together" widget + milestones
- [ ] Dark mode
- [ ] Automated tests (pytest + Playwright)
- [ ] CI/CD (GitHub Actions)

### 12.3 Version 3.0 — AI & Personalization

- [ ] Smart suggestions based on history
- [ ] Diary sentiment analysis
- [ ] Automatic weekly summary
- [ ] Adaptive quiz with personalized questions
- [ ] Contextual partner chat
- [ ] Shared playlists (Spotify API)

### 12.4 Version 4.0 — Social & Expansion

- [ ] "Single" mode (self-discovery questions)
- [ ] "Friends" mode (friendship questions)
- [ ] Shared relationship goals
- [ ] Annual digital book (couple year summary)
- [ ] Data export (relationship PDF)
- [ ] Public API for integrations

---

## 13. Launch Roadmap

| Phase | Action | Timeline | Success Metric |
|-------|--------|----------|---------------|
| **Pre-launch** | Test full flow locally | 1 week | Zero critical bugs |
| **Alpha** | 2-3 friend couples use for 2 weeks | 2 weeks | 80% D7 retention |
| **Closed beta** | 10-20 couples, structured feedback | 3 weeks | NPS > 40 |
| **Open beta** | Promote in WhatsApp/Telegram groups | 4 weeks | 100 couples |
| **v1.0 launch** | Instagram post, Product Hunt, groups | — | 500 active users |
| **v2.0** | Push notifications + Streaks | 2 months post-launch | DAU > 20% MAU |
| **v3.0** | AI + Personalization | 4 months post-launch | Avg session > 8min/day |

---

## 14. Growth Strategy

### 14.1 Acquisition Channels

| Channel | Cost | Potential | Priority |
|---------|------|-----------|----------|
| Word of mouth (couples refer couples) | Free | ★★★★★ | High |
| Instagram — daily question posts | Free | ★★★★☆ | High |
| TikTok — couple challenge videos | Free | ★★★★★ | High |
| WhatsApp/Telegram couple groups | Free | ★★★★☆ | Medium |
| Product Hunt | Free | ★★★☆☆ | Medium |
| Google Ads (keywords: "app for couples") | $$ | ★★★☆☆ | Low |
| TikTok Ads | $$ | ★★★★☆ | Low |

### 14.2 Viral Loop

```
Couple A uses → Screenshots a question/dashboard
           → Posts on Instagram/TikTok
           → Couple B sees → Wants to try
           → Couple B invites partner
           → Cycle repeats
```

### 14.3 Strategic Partnerships

- **Couples therapists:** Recommend the app as a daily connection tool
- **Relationship influencers:** Sponsored content
- **Wedding blogs:** Mention in "ideas to strengthen your relationship"

---

## 15. Monetization Strategy

### 15.1 Freemium Model

| Feature | Free | Premium ($1.99/month) |
|---------|------|----------------------|
| Daily Question | ✅ | ✅ |
| Diary | ✅ | ✅ |
| Challenges | 1/day | Unlimited |
| Couple Quiz | ✅ | ✅ + AI |
| Quotes | 1/day | Unlimited |
| Memories | Last 30 | All |
| Photos | 3/day | Unlimited |
| Diary Themes/Mood | 5 emojis | All + custom |
| Sentiment Analysis | — | ✅ |
| Weekly Review | — | ✅ |
| Dark Mode | — | ✅ |
| Data Export | — | ✅ (PDF) |
| Priority Support | — | ✅ |

### 15.2 Plans

| Plan | Price | Audience |
|------|-------|----------|
| Free | $0 | Couples exploring |
| Monthly Premium | $1.99 | Engaged couples |
| Annual Premium | $15.99 (33% off) | Loyal couples |
| Lifetime | $39.99 (launch) | Early adopters |

### 15.3 Payment Methods

- Stripe (international card)
- Mercado Pago / Pix (Brazil)
- Apple Pay / Google Pay

---

## 16. Retention Strategy

### 16.1 Daily Triggers

| Time | Action | Channel |
|------|--------|---------|
| 08:00 | Notification: "Daily Question available!" | Push (future) |
| 12:00 | "Your partner answered the question!" | Push |
| 18:00 | "Time for today's challenge!" | Push |
| 21:00 | "How about writing in your diary?" | Push |

### 16.2 Gamification

| Mechanic | Description |
|----------|-------------|
| Streaks | Consecutive days of use (🔥 fire) |
| Achievements | "7 days of questions answered", "First photo together" |
| Couple Levels | Bronze → Silver → Gold → Diamond (based on activities) |
| Monthly Badges | "February Full of Love", "March of Connection" |

### 16.3 Seasonal Content

- **Valentine's Day:** Special themes, romantic questions
- **Christmas:** Year reflection, goals for next year
- **Anniversary:** Personalized surprise
- **Seasons:** Themed questions

### 16.4 Churn Prevention

- If 3 days without login → email "We miss you! 💕"
- If 7 days without login → notification "We have a special question waiting"
- If 14 days without login → "Want to take a break? Your data is safe"
- Offer "pause" instead of account deletion

---

## 17. Improvement Checklist

### 17.1 Technical Debt (P0 — Critical)

- [x] **Migrate from `on_event("startup")` to lifespan events** ✅
- [ ] **Add automated tests** (pytest for API, Playwright for frontend)
- [ ] **Add rate limiting** (brute-force protection)
- [ ] **Add photo upload validation** (currently: frontend-only check)
- [ ] **Add pagination** to all lists (memories, admin, etc.)

### 17.2 Experience Improvements (P1 — High)

- [ ] **Dark mode** with persistent toggle
- [ ] **Haptic feedback** on mobile interactions
- [ ] **Swipe gestures** (slide to navigate between sections)
- [ ] **Couple profile avatar/photo upload**
- [x] **Admin XSS fixed** (11 locations with missing `esc()`) ✅
- [x] **`esc()` enhanced** (now escapes single quotes) ✅
- [x] **Dirty tracking in admin** (data loss prevention) ✅
- [x] **Parallel batch delete** with progress feedback ✅
- [ ] **Configurable relationship start date**
- [ ] **Day counter** together on dashboard
- [ ] **Streak tracking** (consecutive days)
- [ ] **Real push notifications** (Web Push API)

### 17.3 Quality of Life Improvements (P2 — Medium)

- [ ] **"Surprise me" button** on dashboard (leads to random section)
- [ ] **Offline mode** (last session cache)
- [ ] **Keyboard shortcuts** (1-4 for navigation)
- [ ] **Export history** as PDF
- [ ] **Share achievements** on social media
- [ ] **Ambient music** on login screen

### 17.4 Future Improvements (P3 — Low)

- [ ] **iOS/Android widget** (via PWA or native app)
- [ ] **Spotify integration** for shared playlists
- [ ] **Google Calendar integration** for events
- [ ] **ChatGPT integration** for personalized questions
- [ ] **Native app** (React Native or Flutter)

---

## 18. Prioritized Backlog

### Sprint 1 — Foundation (Now)

| Item | Effort | Impact | Priority |
|------|--------|--------|----------|
| Automated tests (pytest) | 2 days | ★★★★★ | P0 |
| Rate limiting | 4 hours | ★★★★★ | P0 |
| Upload validation | 2 hours | ★★★★☆ | P1 |
| Admin UX (dirty tracking, batch delete) | ✅ | — | Done |
| Migrate lifespan events | ✅ | — | Done |
| XSS security (esc/attrEsc, admin fixes) | ✅ | — | Done |

### Sprint 2 — Retention

| Item | Effort | Impact | Priority |
|------|--------|--------|----------|
| Streak tracking | 1 day | ★★★★★ | P1 |
| Day counter | 3 hours | ★★★★☆ | P1 |
| Configurable start date | 2 hours | ★★★★☆ | P1 |
| Push notifications | 3 days | ★★★★★ | P1 |

### Sprint 3 — Engagement

| Item | Effort | Impact | Priority |
|------|--------|--------|----------|
| Dark mode | 1 day | ★★★★☆ | P1 |
| Pagination | 1 day | ★★★☆☆ | P2 |
| Avatar upload | 2 days | ★★★☆☆ | P2 |
| Offline mode | 3 days | ★★★★☆ | P2 |

### Sprint 4 — Monetization

| Item | Effort | Impact | Priority |
|------|--------|--------|----------|
| Plan system (free/premium) | 5 days | ★★★★★ | P1 |
| Stripe integration | 3 days | ★★★★★ | P1 |
| Mercado Pago integration | 3 days | ★★★★★ | P1 |
| Upgrade triggers | 2 days | ★★★★☆ | P2 |

---

## 19. Product Evolution Plan

### 19.1 Phase 1 — Comfort (Months 1-3)

Focus on **stability and retention**:
- Finalize technical debt
- Implement streaks + day counter
- Improve mobile experience (gestures, haptics)
- Collect alpha/beta user feedback

### 19.2 Phase 2 — Connection (Months 3-6)

Focus on **product depth**:
- Push notifications
- Dark mode
- More challenge types (video, audio, location)
- Quiz with more categories
- Basic sentiment analysis

### 19.3 Phase 3 — Personalization (Months 6-9)

Focus on **AI and individualization**:
- LLM integration for personalized questions
- Automatic weekly summary
- History-based recommendations
- Activity suggestions for couples

### 19.4 Phase 4 — Expansion (Months 9-12)

Focus on **growth and monetization**:
- Premium plan
- "Friends" and "individual" modes
- Public API
- Couple digital book
- Native app (React Native)

---

## 20. Risk List

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| **Data loss** | Low | Catastrophic | Automatic daily backup (PostgreSQL), manual export |
| **Intimate data leak** | Low | Catastrophic | Encryption at rest, mandatory HTTPS, photos in base64 (not public URL) |
| **Login brute-force** | Medium | High | Rate limiting (planned), bcrypt slow by design |
| **Churn after 7 days** | High | High | Better onboarding, notifications, gamification |
| **Insufficient test coverage** | High | High | Add CI/CD with mandatory tests |
| **Free service dependency (Render)** | Medium | Medium | Prepare Dockerfile for easy migration |
| **Low adoption (niche product)** | High | High | Growth strategy + therapist partnerships |
| **Competition (Lovewick, Couply, etc.)** | Medium | Medium | Differentiators: shared diary + varied challenges + affordable price |
| **Long-term maintenance** | Medium | Medium | Modular code, documentation, tests |
| **LLM cost (AI)** | Medium | Medium | Cache, static content fallback, batch processing |

---

## 21. Metrics (KPIs)

### 21.1 Product Metrics

| KPI | Definition | Target (3 months) | Target (6 months) |
|-----|-----------|-------------------|-------------------|
| **MAU** | Monthly active users | 500 | 2,000 |
| **DAU** | Daily active users | 100 | 500 |
| **DAU/MAU** | Engagement ratio | 20% | 25% |
| **D1 Retention** | Returned next day | 60% | 70% |
| **D7 Retention** | Returned after 7 days | 30% | 40% |
| **D30 Retention** | Returned after 30 days | 15% | 25% |
| **Sessions/day** | Average sessions per DAU | 2.5 | 3.0 |
| **Avg time** | Minutes per session | 4 min | 6 min |

### 21.2 Engagement Metrics

| KPI | Definition | Target |
|-----|-----------|--------|
| **Questions answered/couple** | Weekly average | 4/7 |
| **Challenges completed/couple** | Weekly average | 3/5 |
| **Diary entries/couple** | Weekly average | 3 |
| **Avg streak** | Consecutive days of use | 7 days |
| **Invites sent** | Per active user | 0.5 |

### 21.3 Business Metrics

| KPI | Definition | Target (1 year) |
|-----|-----------|-----------------|
| **Conversion rate** | Free → Premium | 5% |
| **LTV** | Lifetime Value | $12 |
| **CAC** | Acquisition Cost | $1 |
| **Monthly revenue** | MRR | $1,000 |
| **NPS** | Net Promoter Score | 50+ |
| **Churn rate** | Cancelations/month | < 5% |

### 21.4 Technical Metrics

| KPI | Target |
|-----|--------|
| **Uptime** | 99.9% |
| **P95 response time** | < 500ms |
| **5xx errors** | < 0.1% |
| **Bundle size** | < 200KB (HTML + CSS + JS inline) |
| **Lighthouse Performance** | > 85 |
| **Lighthouse PWA** | > 90 |

---

## 22. A/B Testing Plan

### 22.1 Test 1 — Onboarding Flow

| Variant | Description | Metric |
|---------|-------------|--------|
| **A (control)** | Direct login → dashboard | D1 Retention |
| **B (test)** | Login → guided tour (3 slides) → dashboard | D1 Retention |

**Hypothesis:** Guided tour increases D1 retention by 15%  
**Duration:** 2 weeks  
**Audience:** 50% of new users each

### 22.2 Test 2 — Notifications

| Variant | Description | Metric |
|---------|-------------|--------|
| **A (control)** | No notifications | DAU |
| **B (test)** | 1 notification/day (question) | DAU |
| **C (test)** | 2 notifications/day (question + challenge) | DAU |

**Hypothesis:** 2 notifications increase DAU by 30%, but may annoy  
**Duration:** 3 weeks  
**Audience:** 33% each

### 22.3 Test 3 — Premium Pricing

| Variant | Description | Metric |
|---------|-------------|--------|
| **A (control)** | $1.99/month, $15.99/year | Conversion rate |
| **B (test)** | $2.99/month, $19.99/year | Conversion rate |
| **C (test)** | $1.99/month, $13.99/year (12% off) | Conversion rate |

**Hypothesis:** Lower price (C) maximizes total revenue  
**Duration:** 1 month  
**Audience:** 33% each (new users only)

### 22.4 Test 4 — Dashboard Layout

| Variant | Description | Metric |
|---------|-------------|--------|
| **A (control)** | Vertical cards (current) | Action clicks |
| **B (test)** | 2×2 grid with larger summaries | Action clicks |

**Hypothesis:** Grid increases action clicks by 20%  
**Duration:** 2 weeks  
**Audience:** 50% each

---

## 23. Accessibility Plan

### 23.1 WCAG 2.1 Compliance (Level AA)

| Criterion | Status | Action Needed |
|-----------|--------|---------------|
| **1.1.1 Alternative Text** | ❌ | Add descriptive `alt` to images and SVGs |
| **1.4.3 Minimum Contrast** | ⚠️ | Check light pink (#ffb5c2) contrast on white |
| **1.4.4 Text Resize** | ✅ | Uses rem/em, supports 200% zoom |
| **2.1.1 Keyboard** | ❌ | Tab + Enter navigation for SPA sections |
| **2.4.1 Skip Navigation** | ❌ | Add "Skip to content" |
| **2.4.4 Link Purpose** | ❌ | Textless buttons (⚙️) need aria-label |
| **2.4.7 Focus Visible** | ❌ | Add focus outline on all interactive elements |
| **3.3.2 Labels** | ❌ | Inputs without explicit labels (login, diary) |
| **4.1.2 Name, Role, Value** | ❌ | ARIA roles for modal, tabs, interactive cards |

### 23.2 Priority Improvements

1. **Add `aria-label`** to ⚙️ settings button, lang toggle, and clickable cards
2. **Add `role="navigation"`** to bottom nav and `aria-current="page"` on active item
3. **Add `role="dialog"`** to settings modal
4. **Add `role="tablist"`** to tabs (if implementing tabs)
5. **Ensure minimum contrast** 4.5:1 for normal text
6. **Support `prefers-reduced-motion`** for animations

### 23.3 Tests

- [ ] Lighthouse Accessibility audit
- [ ] axe DevTools scan
- [ ] Manual test with VoiceOver (macOS) / TalkBack (Android)
- [ ] Screen reader test (NVDA or JAWS)
- [ ] Keyboard-only navigation

---

## 24. Security Plan

### 24.1 Implemented Measures

| Measure | Status | Details |
|---------|--------|---------|
| **bcrypt passwords** | ✅ | Hash with salt + 12 rounds cost |
| **JWT with expiration** | ✅ | 48h validity, signed with HS256 |
| **SHA-256 fallback** | ✅ | Automatic upgrade to bcrypt on login |
| **Fixed admin credentials** | ✅ | `ADMIN_USERS` via env var (no hardcoded fallback) |
| **HTTPS** | ✅ | Render provides automatic TLS |
| **Output sanitization** | ✅ | `esc()` + `attrEsc()` prevent XSS (text and attributes) |
| **CORS** | ✅ | Configured middleware |
| **Connection pool** | ✅ | `pool_size=10, max_overflow=20, pool_pre_ping=True` |
| **Service Worker** | ✅ | Caches only GET requests |
| **Admin XSS** | ✅ | 11 locations fixed with `esc()` |
| **Single quote escaping** | ✅ | `esc()` now escapes `&#39;` |
| **Dirty tracking** | ✅ | `beforeunload` + `markDirty()` in admin |
| **Batch delete** | ✅ | Parallel with progress feedback |
| **SQL Injection** | ✅ | ORM prevents (SQLAlchemy) |
| **XSS** | ✅ | Template engine with controlled insertion |

### 24.2 Pending Measures

| Measure | Priority | Action |
|---------|----------|--------|
| **Rate limiting** | P0 | Add `slowapi` or custom middleware |
| **Content Security Policy** | P1 | Strict CSP header |
| **Upload validation** | P1 | Limit size (5MB), MIME type, sanitize base64 |
| **Helmet.js-like headers** | P1 | Add X-Frame-Options, X-Content-Type-Options, etc. |
| **Dependency auditing** | P2 | Regular `pip-audit`, Dependabot |
| **Security logs** | P2 | Log failed login attempts, admin actions |
| **Encryption at rest** | P2 | Base64 photos in DB are plaintext — consider encryption |

### 24.3 Admin Password Policy

- Minimum 8 characters
- Change default password immediately
- Do not reuse passwords from other services
- 2FA (future)

---

## 25. SEO Plan

### 25.1 On-Page SEO

| Element | Status | Action |
|---------|--------|--------|
| **Title tag** | ⚠️ | `Still Learning 💕` — good, but could be more descriptive |
| **Meta description** | ❌ | Add: "Still Learning: the app for couples to connect every day with questions, challenges and shared diary" |
| **Open Graph** | ❌ | Add og:title, og:description, og:image, og:url |
| **Twitter Cards** | ❌ | Add twitter:card, twitter:title, twitter:description |
| **Structured Data** | ❌ | Schema.org `WebApplication` |
| **Canonical URL** | ❌ | Add link rel="canonical" |
| **Sitemap.xml** | ❌ | Create sitemap.xml |
| **Robots.txt** | ❌ | Create robots.txt |
| **Alt text** | ❌ | Add alt to SVG images |

### 25.2 Target Keywords

| Keyword | Volume (BR) | Competition | Priority |
|---------|-------------|-------------|----------|
| app for couples | ★★★★☆ | Medium | ★★★★★ |
| couple application | ★★★☆☆ | Medium | ★★★★☆ |
| questions for couples | ★★★★☆ | Low | ★★★★★ |
| shared couple diary | ★★☆☆☆ | Low | ★★★★☆ |
| challenges for couples | ★★★☆☆ | Low | ★★★★☆ |
| strengthen relationship | ★★★★☆ | High | ★★★☆☆ |
| couple quiz | ★★★☆☆ | Medium | ★★★☆☆ |

### 25.3 Content Strategy

- Blog with articles about relationship connection
- Instagram posts with daily questions (link in bio)
- Guest posts on wedding/relationship blogs
- Influencer partnerships for reviews

---

## 26. Internationalization Plan

### 26.1 Current Status

- **Portuguese (BR):** ✅ Complete
- **English (US):** ✅ Complete
- **Spanish:** ❌ Pending
- **French:** ❌ Pending
- **Italian:** ❌ Pending

### 26.2 Translation Architecture

**Current (translations.py):**
```python
L = {
    "key": {
        "pt": "text in portuguese",
        "en": "text in english"
    }
}

def t(key, lang="pt"):
    val = L.get(key, {})
    return val.get(lang, val.get("pt", key))
```

**Proposed for new languages:**
```python
L = {
    "key": {
        "pt": "...",
        "en": "...",
        "es": "...",   # new
        "fr": "...",   # new
        "it": "..."    # new
    }
}
```

### 26.3 Localization Roadmap

| Language | Priority | Effort | Timeline |
|----------|----------|--------|----------|
| **Spanish** | ★★★★★ | 2 days | Month 1 |
| **French** | ★★★★☆ | 2 days | Month 2 |
| **Italian** | ★★★☆☆ | 2 days | Month 3 |
| **German** | ★★☆☆☆ | 2 days | Month 6 |

### 26.4 Language Detection

**Current:** `lang` cookie set manually by user  
**Proposed:** Automatic detection via `Accept-Language` header + manual fallback

### 26.5 Language-Sensitive Content

| Content | PT | EN | Other |
|---------|----|----|-------|
| 40 daily questions | ✅ | ✅ | ❌ |
| 41 intimate question themes | ✅ | ✅ | ❌ |
| 18 challenge suggestions | ✅ | ✅ | ❌ |
| 30 quotes with curiosities | ✅ | ✅ | ❌ |
| Interface (100+ keys) | ✅ | ✅ | ❌ |
| Riddles | ✅ | ✅ | ❌ |

---

## Appendix A — Glossary

| Term | Definition |
|------|-----------|
| **Couple** | Entity representing the pair of users |
| **Dashboard** | Main screen (Home) with daily summary |
| **Challenge** | Daily activity: riddle, question, photo, etc. |
| **Diary** | Daily text entry from each partner |
| **JWT** | JSON Web Token for stateless authentication |
| **LoginEvent** | Record of each login for auditing |
| **Memories** | Aggregation of all past interactions |
| **Daily Question** | Daily question answered by both |
| **PWA** | Progressive Web App (installable app) |
| **Quote** | Daily inspirational quote |
| **Review** | Weekly couple reflection |
| **SPA** | Single Page Application (navigation without reload) |

## Appendix B — Environment Variables

```
# .env

# Admin credentials (JSON array of {username, password} pairs)
ADMIN_USERS=[{"username":"ttt","password":"sisrat"},{"username":"T","password":"trs123"},{"username":"Tadmin","password":"trs123"}]

# JWT secret (change in production!)
JWT_SECRET=sl-jwt-secret-change-me-in-production-2024

# Database URL (defaults to SQLite if not set)
# DATABASE_URL=postgresql://user:pass@host/db
```

## Appendix C — Dependencies (requirements.txt)

```
fastapi>=0.104.0
uvicorn>=0.24.0
sqlalchemy>=2.0.0
bcrypt>=4.1.0
pyjwt>=2.0.0
python-dotenv>=1.0.0
```

---

> **Document generated on:** July 12, 2026  
> **Next review:** August 12, 2026  
> **Maintained by:** Tarsis Gonçalves
