# Still Learning — Documentação Completa do Produto

> **Versão:** 2.1  
> **Público-alvo:** Casais em relacionamentos sérios (namoro, noivado, casamento)  
> **Stack:** Python 3.11+ / FastAPI / SQLAlchemy / SQLite (dev) / PostgreSQL (prod) / bcrypt + JWT  
> **URL de produção:** `https://still-learning.onrender.com`

---

## Índice

1. [Arquitetura Completa do Sistema](#1-arquitetura-completa-do-sistema)
2. [Fluxo de Navegação](#2-fluxo-de-navegação)
3. [Jornada do Usuário](#3-jornada-do-usuário)
4. [Wireframes em Texto](#4-wireframes-em-texto)
5. [Estrutura das Páginas](#5-estrutura-das-páginas)
6. [Componentes Reutilizáveis](#6-componentes-reutilizáveis)
7. [Sistema de Design](#7-sistema-de-design)
8. [Guia Visual](#8-guia-visual)
9. [Estrutura do Banco de Dados](#9-estrutura-do-banco-de-dados)
10. [APIs](#10-apis)
11. [Estrutura de IA](#11-estrutura-de-ia)
12. [Roadmap de Desenvolvimento](#12-roadmap-de-desenvolvimento)
13. [Roadmap de Lançamento](#13-roadmap-de-lançamento)
14. [Estratégia de Crescimento](#14-estratégia-de-crescimento)
15. [Estratégia de Monetização](#15-estratégia-de-monetização)
16. [Estratégia de Retenção](#16-estratégia-de-retenção)
17. [Checklist de Melhorias](#17-checklist-de-melhorias)
18. [Backlog Priorizado](#18-backlog-priorizado)
19. [Plano de Evolução do Produto](#19-plano-de-evolução-do-produto)
20. [Lista de Riscos](#20-lista-de-riscos)
21. [Métricas (KPIs)](#21-métricas-kpis)
22. [Plano de Testes A/B](#22-plano-de-testes-ab)
23. [Plano de Acessibilidade](#23-plano-de-acessibilidade)
24. [Plano de Segurança](#24-plano-de-segurança)
25. [Plano de SEO](#25-plano-de-seo)
26. [Plano de Internacionalização](#26-plano-de-internacionalização)

---

## 1. Arquitetura Completa do Sistema

### 1.1 Visão Geral

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENTE (Browser)                           │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐            │
│  │index.html│  │couple.html   │  │ admin.html        │            │
│  │(login)   │  │(app casal)   │  │ (painel admin)    │            │
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
│                    SERVIDOR (FastAPI / Uvicorn)                     │
│                                                                     │
│  ┌──────────────┐  ┌────────────────┐  ┌─────────────────────────┐ │
│  │  Middleware   │  │  require_auth  │  │  check_admin            │ │
│  │  (CORS, etc) │  │  (JWT Bearer)  │  │  (admin credentials)    │ │
│  └──────────────┘  └────────────────┘  └─────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    ROTAS DA API (53 endpoints)               │  │
│  │  ┌─────────┐ ┌──────────────┐ ┌──────────────────────────┐  │  │
│  │  │Auth API │ │Couple API    │ │Admin API                 │  │  │
│  │  │  1 rota │ │ 28 rotas     │ │ 22 rotas                 │  │  │
│  │  └─────────┘ └──────────────┘ └──────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              CAMADA DE DADOS                                 │  │
│  │  ┌─────────────────┐  ┌──────────────────────────────────┐   │  │
│  │  │   SQLAlchemy    │  │  models.py (13 tabelas)          │   │  │
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
│  │              ESTATICOS (PWA)                                │  │
│  │  ┌───────────┐  ┌──────────┐  ┌──────────┐                 │  │
│  │  │style.css  │  │ sw.js    │  │manifest  │  icons/         │  │
│  │  │           │  │(service  │  │.json     │  (SVG)          │  │
│  │  │           │  │ worker)  │  │          │                 │  │
│  │  └───────────┘  └──────────┘  └──────────┘                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              CAMADA DE TRADUÇÃO                              │  │
│  │  translations.py (449 linhas, ~100 chaves, 200 perguntas    │  │
│  │  + 80 sugestões + 30 citações + temas, em PT e EN)          │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Stack Detalhada

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| Runtime | Python 3.11+ | 3.11 |
| Framework Web | FastAPI | 0.104+ |
| Servidor ASGI | Uvicorn | 0.24+ |
| ORM | SQLAlchemy | 2.0+ |
| Banco (dev) | SQLite | 3.x |
| Banco (prod) | PostgreSQL | 15+ |
| Autenticação | bcrypt + PyJWT | bcrypt 4.1+, PyJWT 2.0+ |
| Templates | HTML + JS inline (server-side string replace) | — |
| Frontend | Vanilla JS + CSS custom | — |
| PWA | Service Worker + Manifest | W3C |
| Deploy | Render (free tier) | — |

### 1.3 Arquitetura de Templates (Server-Side Rendering)

O sistema usa um motor de template extremamente leve (`_render()`) que:
1. Lê o arquivo HTML do diretório `templates/`
2. Substitui `{{ chave }}` por valores do dicionário
3. Retorna o HTML como `HTMLResponse`
4. Todo o resto é renderizado via JavaScript no cliente (SPA-like)

### 1.4 Arquitetura dos Templates

```
templates/
├── index.html       → Login (ponto de entrada)       ──→ Fluxo Login
├── couple.html      → App principal (SPA-like)       ──→ Fluxo Casal
└── admin.html       → Painel administrativo           ──→ Admin
```

### 1.5 Estrutura de Arquivos

```
project quiz code/
├── .env                   → Variáveis de ambiente
├── .gitignore
├── requirements.txt       → Dependências Python
├── database.py            → Engine SQLAlchemy + SessionLocal
├── models.py              → 13 modelos ORM
├── main.py                → 53 endpoints + toda a lógica
├── translations.py        → Internacionalização (PT/EN) 431 linhas
├── profiles.json          → Dados de login (migrados p/ DB na 1ª execução)
├── quiz.db                → SQLite local (dev)
├── static/
│   ├── style.css          → CSS principal (~600 linhas)
│   ├── manifest.json      → PWA manifest
│   ├── sw.js              → Service Worker
│   └── icons/
│       ├── icon-192.svg
│       └── icon-512.svg
└── templates/
    ├── index.html
    ├── couple.html        → ~2250 linhas (JS + CSS + HTML)
    └── admin.html         → ~1800 linhas (JS + CSS + HTML)
```

---

## 2. Fluxo de Navegação

### 2.1 Fluxo Geral

```
                    ┌──────────────┐
                    │   / (index)  │
                    │   Tela de   │
                    │   Login     │
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
                    │ │Hoje│ Nós│ ⚙️  │   │
                    │ └────┴────┴─────┘   │
                    └─────────────────────┘
```

### 2.2 Navegação Interna (couple.html — SPA)

```
Hoje ──────────────────────────────────────────────
  ├── Dashboard (cards: saudação, stats, notifs)
  ├── Pergunta do Dia (responder / ver resposta)
  ├── Desafio do Dia (iniciar / completar)
  ├── Citação do Dia (ler / navegar)
  ├── Agenda (ver / adicionar eventos)
  ├── To-Dos (ver / adicionar / marcar)
  └── Revisão Semanal (escrever reflexão)

Nós ───────────────────────────────────────────────
  ├── Diário (escrever / ler entradas)
  ├── Memórias (fotos + perguntas + desafios)
  ├── Quiz do Casal (perguntas sobre si/parceiro)
  └── Desafio (atalho para o desafio atual)

⚙️ (modal) ───────────────────────────────────────
  ├── Idioma (PT ↔ EN)
  └── Sair (logout + clear localStorage)
```

### 2.3 Fluxo de Dados

```
Login → JWT → localStorage.setItem('auth_token')
   ↓
Cada fetch() → Authorization: Bearer <token>
   ↓
require_auth() → decodifica JWT → extrai couple_id, login_name
   ↓
Dashboard → GET /api/couple/dashboard
   ↓
Cards → cada seção chama seu endpoint específico
   ↓
Respostas → POST /api/couple/... (com JWT no header)
```

---

## 3. Jornada do Usuário

### 3.1 Primeiro Acesso (Casamento Digital)

```
1. Usuário acessa still-learning.onrender.com
2. Digita nome de login + senha
3. Sistema verifica bcrypt (com fallback SHA-256 legado)
4. Gera JWT (48h de validade)
5. Redireciona para /still-learning
6. Dashboard é exibido com cards do dia
```

### 3.2 Jornada Diária

```
Manhã:
  └── Abre o app → Hoje
      ├── Vê saudação personalizada
      ├── Vê stats do dia (diário, desafio, tarefas)
      └── Lê citação do dia 💌

Tarde:
  └── Abre o app → Hoje → Pergunta do Dia
      ├── Lê pergunta
      ├── Escreve resposta
      └── Aguarda parceiro responder

Noite:
  └── Abre o app → Nós → Diário
      ├── Escreve sobre o dia
      └── Escolhe mood (emoji)
```

### 3.3 Jornada Semanal

```
Segunda:
  └── Hoje → Revisão Semanal
      ├── Nova pergunta/disponível
      └── Escreve reflexão da semana

Distribuído na semana:
  └── Nós → Desafio → tipos variam:
      ├── Enigma (adivinhar resposta)
      ├── Pergunta Íntima (criada pelo parceiro)
      ├── Desafio Personalizado (foto, texto, áudio)
      ├── Desafio de Foto (tirar foto do tema)
      └── Citação (refletir juntos)
```

### 3.4 Fluxo de Memórias

```
Nós → Memórias
  ├── Perguntas do Dia respondidas
  ├── Desafios completados
  ├── Fotos enviadas
  ├── Entradas de diário
  └── Revisões semanais
```

---

## 4. Wireframes em Texto

### 4.1 Tela de Login

```
┌───────────────────────────────────────┐
│  ┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐    │
│    S T I L L   L E A R N I N G        │
│  └─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘    │
│                                       │
│         [✨] [💕] [💑]                │
│                                       │
│    ┌─────────────────────────────┐    │
│    │  seu nome                   │    │
│    └─────────────────────────────┘    │
│    ┌─────────────────────────────┐    │
│    │  senha                      │    │
│    └─────────────────────────────┘    │
│                                       │
│    ┌─────────────────────────────┐    │
│    │      Entrar 💕              │    │
│    └─────────────────────────────┘    │
│                                       │
│    [PT]                [EN]           │
│                                       │
│   "Aprendendo um ao outro,            │
│    um dia de cada vez"                │
└───────────────────────────────────────┘
```

### 4.2 Dashboard (Hoje)

```
┌───────────────────────────────────────┐
│ [💕] ✨ Still Learning ✨     [EN]    │
│  Aprendendo um ao outro...            │
│ ✦ T ✦                               │
├───────────────────────────────────────┤
│ ┌─────────────────────────────────┐   │
│ │ [💕] Olá, T 💕                  │   │
│ │      O que vamos fazer hoje?    │   │
│ └─────────────────────────────────┘   │
│                                       │
│ ┌──────┐ ┌──────┐ ┌──────┐           │
│ │ Diário│ │Desaf │ │Taref │           │
│ │   3   │ │  ✓   │ │  1   │           │
│ └──────┘ └──────┘ └──────┘           │
│                                       │
│ ┌─────────────────────────────────┐   │
│ │ 💭  Pergunta do Dia       Ver   │   │
│ │      Respondida ✅              │   │
│ └─────────────────────────────────┘   │
│ ┌─────────────────────────────────┐   │
│ │ 📖  Nosso Diário           ✏️   │   │
│ │      2 registros hoje           │   │
│ └─────────────────────────────────┘   │
│ ┌─────────────────────────────────┐   │
│ │ 🎯  Desafio de Hoje      Iniciar│   │
│ │      Tipo: enigma               │   │
│ └─────────────────────────────────┘   │
│ ┌─────────────────────────────────┐   │
│ │ 💌  Citação do Dia         Ler  │   │
│ │      "O amor não se vê..."      │   │
│ └─────────────────────────────────┘   │
│ ┌─────────────────────────────────┐   │
│ │ 📅  Próximos Eventos      Ver   │   │
│ │      Nada agendado              │   │
│ └─────────────────────────────────┘   │
├───────────────────────────────────────┤
│ [🏠 Hoje]  [💑 Nós]    [⚙️]       │
└───────────────────────────────────────┘
```

### 4.3 Seção Nós

```
┌───────────────────────────────────────┐
│ [💕] ✨ Still Learning ✨     [EN]    │
├───────────────────────────────────────┤
│         💑 Nós                        │
│  Nossas memórias e momentos           │
│                                       │
│  ┌──────────┐  ┌──────────┐          │
│  │   📖     │  │   ✨     │          │
│  │  Diário  │  │ Memórias │          │
│  │Entradas..│  │Fotos...  │          │
│  └──────────┘  └──────────┘          │
│  ┌──────────┐  ┌──────────┐          │
│  │   ❓     │  │   🎯     │          │
│  │   Quiz   │  │ Desafio  │          │
│  │Teste...  │  │Atual...  │          │
│  └──────────┘  └──────────┘          │
├───────────────────────────────────────┤
│ [🏠 Hoje]  [💑 Nós]    [⚙️]       │
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
│  │        Idioma                 │    │
│  │    🇧🇷 Português             │    │
│  └───────────────────────────────┘    │
│  ┌───────────────────────────────┐    │
│  │         🚪                   │    │
│  │         Sair                  │    │
│  │     Desconectar               │    │
│  └───────────────────────────────┘    │
└───────────────────────────────────────┘
```

### 4.5 Pergunta do Dia

```
┌───────────────────────────────────────┐
│ [💕]          ← Voltar               │
├───────────────────────────────────────┤
│    💭 Pergunta do Dia                 │
│                                       │
│  ┌─────────────────────────────────┐  │
│  │ "O que você aprendeu sobre mim  │  │
│  │  essa semana que não sabia?"    │  │
│  └─────────────────────────────────┘  │
│                                       │
│  ┌─────────────────────────────────┐  │
│  │  Sua resposta:                  │  │
│  │  ┌─────────────────────────┐    │  │
│  │  │                         │    │  │
│  │  │  Escreva aqui...        │    │  │
│  │  │                         │    │  │
│  │  └─────────────────────────┘    │  │
│  │                                 │  │
│  │  [📤 Enviar 💕]                │  │
│  └─────────────────────────────────┘  │
│                                       │
│  ┌─────────────────────────────────┐  │
│  │ 💭 Resposta do(a) parceiro(a):  │  │
│  │ "Aprendi que você..."          │  │
│  └─────────────────────────────────┘  │
├───────────────────────────────────────┤
│ [🏠 Hoje]  [💑 Nós]    [⚙️]       │
└───────────────────────────────────────┘
```

### 4.6 Diário

```
┌───────────────────────────────────────┐
│ [💕]          ← Voltar               │
├───────────────────────────────────────┤
│    📖 Nosso Diário 💕                 │
│                                       │
│  ┌─────── Hoje ───────────────────┐   │
│  │ Você: [✏️ Escrever...]         │   │
│  │        Como está se sentindo?   │   │
│  │        [😊] [😢] [😍] [😴]    │   │
│  │ Parceiro: Ainda não escreveu   │   │
│  └─────────────────────────────────┘   │
│  ┌─────── Dias Anteriores ─────────┐   │
│  │  12/07 - Você escreveu:         │   │
│  │  "Hoje foi um dia incrível..."  │   │
│  │  11/07 - Parceiro escreveu:     │   │
│  │  "Amo nossos momentos..."       │   │
│  └─────────────────────────────────┘   │
├───────────────────────────────────────┤
│ [🏠 Hoje]  [💑 Nós]    [⚙️]       │
└───────────────────────────────────────┘
```

---

## 5. Estrutura das Páginas

### 5.1 HTML Estrutural

Cada página segue o mesmo esqueleto:

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
  <!-- CONTEÚDO ESPECÍFICO DA PÁGINA -->
  <script>
    // JS específico + service worker registration
  </script>
</body>
</html>
```

### 5.2 couple.html — Estrutura Interna

```html
<body>
  <div class="floating-bg"></div>

  <div id="app">
    <div class="app-header">         <!-- Header fixo -->
      <div class="card-heart">💕</div>
      <button class="lang-toggle">EN</button>
      <h1>✨ Still Learning ✨</h1>
      <div class="subtitle">...</div>
    </div>
    <div id="userGreeting"></div>    <!-- Nome do usuário -->
    <div id="mainContent"></div>     <!-- Conteúdo dinâmico -->
  </div>

  <div class="nav-bar">              <!-- 3-item nav fixa -->
    Hoje | Nós | ⚙️
  </div>

  <div class="modal-overlay">        <!-- Modal Settings -->
    Idioma + Sair
  </div>

  <script>
    // ~1500 linhas de JS: api(), showSection(), loadDashboard(),
    // loadDiary(), loadQuestion(), loadChallenge(), loadQuiz(),
    // loadMemories(), loadAgenda(), loadTodos(), loadReview(),
    // toggleLang(), logout(), init()
  </script>
</body>
```

### 5.3 admin.html — Estrutura Interna

```html
<body>
  <div class="admin-container">
    <div class="admin-sidebar">     <!-- Navegação admin -->
      Stats | Profiles | Couples | Questions | Challenges | ...
    </div>
    <div class="admin-content">     <!-- Conteúdo dinâmico -->
      <div id="adminMain"></div>
    </div>
  </div>

  <script>
    // ~1800 linhas: carregamento de stats, CRUD de perfis,
    // gerenciamento de casais, visualização de dados
  </script>
</body>
```

---

## 6. Componentes Reutilizáveis

### 6.1 Frontend (Vanilla JS)

| Componente | Local | Descrição |
|-----------|-------|-----------|
| `api(path, opts)` | couple.html:665 | Wrapper fetch com JWT + headers + JSON automático |
| `showSection(name)` | couple.html:718 | Navegação SPA (troca conteúdo + nav ativa) |
| `backLink()` | couple.html:718 | Botão "← Voltar" padronizado |
| `esc(s)` / `attrEsc(s)` | couple.html:684 | Sanitização HTML + atributos (escapa aspas/single quotes) |
| `toggleLang()` | couple.html:679 | Troca PT/EN com cookie + recarrega |
| `logout(e)` | couple.html:686 | Clean + redirect |
| `toggleSettings()` | couple.html:712 | Abre/fecha modal de configurações |
| `toast(msg)` | couple.html:2207 | Toast flutuante não-intrusivo (3s) |
| `markDirty()` | admin.html | Marca formulário como não salvo |

### 6.2 Backend (Python)

| Componente | Arquivo | Descrição |
|-----------|---------|-----------|
| `_render(name, **kwargs)` | main.py:186 | Template engine caseira |
| `require_auth()` | main.py:110 | Dependency Injection de autenticação (JWT Bearer apenas) |
| `check_admin()` | main.py:128 | Validação de admin (credenciais via env var) |
| `get_couple_info()` | main.py:205 | Retorna `(is_primary, partner_name)` buscando a tabela Couple |
| `_profile_name()` | main.py:219 | Resolve nome de exibição do perfil |
| `hash_pw()` / `verify_pw()` | main.py:68 | Hash/verificação bcrypt + SHA-256 fallback |
| `create_jwt()` / `decode_jwt()` | main.py:82 | Geração/validação JWT |
| `get_db()` | database.py:26 | Gerenciador de sessão SQLAlchemy |
| `get_quote()` | main.py:708 | Retorna citação do dia com controle de offset |
| `lifespan()` | main.py:176 | Startup/shutdown events (lifespan) |

### 6.3 CSS Reutilizável (style.css)

```css
/* Sistema de cores (variáveis CSS) */
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

/* Componentes chave */
.card { /* cartão com fundo branco, sombra, bordas arredondadas */ }
.card-heart { /* coração SVG decorativo no topo */ }
.card-text { /* texto descritivo dentro do card */ }
.card-row { /* linha flexível no card */ }
.card-action { /* botão de ação no card */ }
.stat-pill { /* pílula de estatística (ex: Diário: 3) */ }
.notif-card { /* cartão de notificação */ }
.loading + .spinner { /* estado de carregamento */ }
.empty-state { /* estado vazio */ }
.btn, .btn-primary, .btn-outline { /* sistema de botões */ }
.modal-overlay + .modal-box { /* modal genérico */ }
.nav-bar + .nav-item { /* navegação inferior */ }
.more-card { /* cartão de menu */ }
.diary-entry { /* entrada de diário */ }
.question-card { /* pergunta do dia */ }
.challenge-card { /* cartão de desafio */ }
.partner-challenge-card { /* desafio do parceiro */ }
.todo-item { /* item de to-do */ }
.floating-bg { /* fundo animado */ }
```

---

## 7. Sistema de Design

### 7.1 Core Tokens

```css
:root {
  /* CORES */
  --pink: #ffb5c2;           /* Primária — rosa pastel */
  --pink-dark: #e88a9a;      /* Primária escura — hover/active */
  --cream: #fff5f5;           /* Superfície — fundo de cards */
  --text: #4a4a4a;            /* Texto principal */
  --text-light: #b0a0a0;      /* Texto secundário */
  --bg: #fdf6f0;              /* Fundo da página — off-white */
  --white: #ffffff;           /* Cards */

  /* ESPAÇAMENTO */
  --radius-sm: 10px;          /* Cantos suaves */
  --radius-cloud: 18px;       /* Cantos estilo "nuvem" */
  --radius-round: 50%;        /* Elementos circulares */

  /* SOMBRA */
  --shadow: 0 4px 20px rgba(255, 181, 194, 0.2);

  /* ANIMAÇÃO */
  --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

### 7.2 Tipografia

```css
/* Títulos/Header */
font-family: 'Press Start 2P', monospace;   /* Pixelada — nostalgia */
font-size: 9px (mobile), 7px (nav)

/* Corpo */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
font-size: 0.9rem (padrão), 0.82rem (secundário)
```

### 7.3 Ícones

Uso exclusivo de emoji Unicode para ícones (sem dependências externas):

| Emoji | Significado |
|-------|-------------|
| 🏠 | Hoje / Home |
| 💑 | Nós / Us |
| ⚙️ | Configurações |
| 💕 | Amor / App |
| 💭 | Pergunta do Dia |
| 📖 | Diário |
| ✨ | Memórias |
| 🎯 | Desafio |
| ❓ | Quiz |
| 📅 | Agenda |
| 📋 | To-Dos |
| 💌 | Citação |
| 💪 | Desafio físico |
| 🔔 | Notificação |

### 7.4 Grid e Layout

```css
/* Layout base — mobile-first, max-width: 520px */
.section { max-width: 440px; margin: 0 auto; padding: 16px; }

/* Grid de 2 colunas (Nós) */
display: grid; grid-template-columns: 1fr 1fr; gap: 12px;

/* Cards empilhados (Dashboard) */
.card + .card { margin-top: 14px; }
```

---

## 8. Guia Visual

### 8.1 Telas (Descrição Textual)

| Tela | Paleta | Elementos Principais | Tom |
|------|--------|---------------------|-----|
| Login | Rosa + Off-white | Inputs arredondados, botão gradiente, coração SVG | Acolhedor, romântico |
| Dashboard (Hoje) | Rosa + Branco | Cards com sombra, stats em pílulas, botões de ação | Informativo, convidativo |
| Nós | Rosa + Branco | Grid 2×2 com "more-cards" | Navegacional |
| Pergunta do Dia | Rosa + Off-white | Card da pergunta, textarea, botão enviar | Íntimo, reflexivo |
| Diário | Rosa + Branco | Seção "hoje" + timeline de dias | Pessoal, nostálgico |
| Desafio | Rosa + Off-white | Instruções, input/submissão, status | Divertido, interativo |
| Memórias | Rosa + Branco | Acordeão de seções (perguntas, desafios, etc.) | Nostálgico |
| Settings (Modal) | Branco + Rosa | Overlay semi-transparente, cards de ação | Limpo, minimalista |
| Admin | Cinza + Azul escuro | Sidebar, tabelas, inputs, botões de ação | Técnico, utilitário |

### 8.2 Comportamento Responsivo

```
Desktop (>768px):
  max-width: 520px; margin: 0 auto;
  Conteúdo centralizado como card

Mobile (<768px):
  Largura total com padding 16px
  Nav fixa inferior
  Header fixo superior

Mobile pequeno (<375px):
  font-size reduzido em 10-15%
  Nav com padding menor
  Spacing reduzido
```

---

## 9. Estrutura do Banco de Dados

### 9.1 Diagrama de Entidades

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

### 9.2 Resumo das Tabelas

| Tabela | Qtd Campos | Chave Primária | Chave Estrangeira |
|--------|-----------|----------------|-------------------|
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

### 10.1 Autenticação

| Método | Rota | Request | Response |
|--------|------|---------|----------|
| POST | `/api/login` | `{name, password}` | `{type, name, couple_id, partner_name, token}` |

### 10.2 Couple App (28 endpoints)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/couple/dashboard` | Dashboard completo |
| GET | `/api/couple/question` | Pergunta do dia |
| POST | `/api/couple/question/answer` | Responder pergunta |
| POST | `/api/couple/translations` | Traduções PT/EN |
| GET | `/api/couple/diary` | Entradas do diário |
| POST | `/api/couple/diary/save` | Salvar entrada |
| GET | `/api/couple/challenge` | Desafio do dia |
| POST | `/api/couple/challenge/guess` | Palpite (enigma) |
| POST | `/api/couple/challenge/photo` | Upload de foto |
| POST | `/api/couple/challenge/create-question` | Criar pergunta íntima |
| POST | `/api/couple/challenge/answer-question` | Responder pergunta |
| POST | `/api/couple/challenge/partner/create` | Criar desafio personalizado |
| POST | `/api/couple/challenge/partner/complete` | Completar desafio |
| GET | `/api/couple/challenge/partner` | Desafios personalizados |
| GET | `/api/couple/challenge/history` | Histórico de desafios |
| GET | `/api/couple/quote` | Citação do dia |
| GET | `/api/couple/quiz` | Quiz do casal |
| POST | `/api/couple/quiz/save` | Salvar resposta do quiz |
| GET | `/api/couple/memories` | Memórias agregadas |
| GET | `/api/couple/agenda` | Agenda |
| POST | `/api/couple/agenda/add` | Adicionar evento |
| POST | `/api/couple/agenda/delete` | Deletar evento |
| GET | `/api/couple/todos` | To-Dos |
| POST | `/api/couple/todos/add` | Adicionar tarefa |
| POST | `/api/couple/todos/toggle` | Alternar conclusão |
| POST | `/api/couple/todos/delete` | Deletar tarefa |
| GET | `/api/couple/review` | Review semanal |
| POST | `/api/couple/review/save` | Salvar review |

### 10.3 Admin API (22 endpoints)

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/admin/couple/stats` | Estatísticas de todos os casais |
| POST | `/api/admin/couple/create` | Criar novo casal |
| POST | `/api/admin/couple/reset` | Resetar dados de um casal |
| POST | `/api/admin/couple/delete` | Deletar casal + todos os dados |
| POST | `/api/admin/couple/questions` | Listar perguntas do dia |
| POST | `/api/admin/couple/question/save` | Salvar pergunta do dia |
| POST | `/api/admin/couple/challenges` | Listar desafios |
| POST | `/api/admin/couple/photos` | Listar fotos |
| POST | `/api/admin/couple/diary` | Listar diários |
| POST | `/api/admin/couple/diary/delete` | Deletar entrada |
| POST | `/api/admin/couple/agenda` | Listar agenda |
| POST | `/api/admin/couple/todos` | Listar to-dos |
| POST | `/api/admin/challenge/delete` | Deletar desafio |
| POST | `/api/admin/photo/delete` | Deletar foto |
| POST | `/api/admin/photo/data` | Dados completos da foto |
| POST | `/api/admin/agenda/delete` | Deletar evento da agenda |
| POST | `/api/admin/todos/delete` | Deletar item de to-do |
| POST | `/api/admin/login-history` | Histórico de login |
| POST | `/api/admin/profiles` | Listar perfis |
| POST | `/api/admin/profiles/save` | Salvar/editar perfil |
| POST | `/api/admin/profiles/delete` | Deletar perfil |
| GET | `/admin` | Painel administrativo (HTML) |

> **Nota sobre o sistema de quiz removido:** O quiz standalone original (Questionário de Perfil)
> foi removido em uma limpeza. Todos os usuários agora utilizam o sistema de casal.
> O modelo `QuizAnswer` continua ativo — ele é usado pelo questionário de compatibilidade
> dentro do dashboard do casal (`/api/couple/quiz`).

---

## 11. Estrutura de IA

### 11.1 Estado Atual

O sistema **não utiliza IA generativa ou modelos de machine learning** atualmente. Tudo é baseado em:

- **Conteúdo pré-definido:** 40 perguntas diárias, 41 temas, 18 sugestões de desafio, 30 citações
- **Rotação determinística:** `daily_offset = (today - COUPLE_START).days % len(translations)` (pergunta do dia)
- **Rotação de tipos de desafio:** `challenge_types[(today - COUPLE_START).days % 5]`
- **Randomização controlada:** `random.choice()` nos temas/sugestões

### 11.2 Oportunidades de IA

| Funcionalidade | Tipo de IA | Prioridade | Complexidade |
|---------------|-----------|------------|--------------|
| Perguntas personalizadas baseadas no histórico do casal | LLM (GPT-4 / Claude) | ★★★ | Média |
| Sugestões de desafio baseadas em interesses | LLM | ★★☆ | Média |
| Análise de sentimento das entradas de diário | NLP (classificação) | ★★☆ | Baixa |
| Resumo semanal automático do diário | LLM (sumarização) | ★☆☆ | Média |
| Recomendação de citações por mood | Embeddings + Similaridade | ★★☆ | Média |
| Quiz adaptativo (perguntas que o parceiro errou) | Lógica condicional | ★★★ | Baixa |
| Detecção de padrões de comunicação | NLP + Estatística | ★☆☆ | Alta |

### 11.3 Arquitetura Proposta para IA

```
Frontend → API → main.py → (novo) services/ai_service.py
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                    OpenAI API            HuggingFace
                    (GPT-4 Turbo)         (modelos locais)
                         │                     │
                    Rate limiting          Cache (Redis)
                    + Fallback             + Batch
```

---

## 12. Roadmap de Desenvolvimento

### 12.1 Versão 1.0 — MVP (Atual)

- [x] Login com bcrypt + JWT
- [x] Dashboard do casal (card central)
- [x] Pergunta do Dia (com respostas reveladas após ambos)
- [x] Diário compartilhado
- [x] Desafios (5 tipos com rotação)
- [x] Agenda de eventos
- [x] To-Do list compartilhada
- [x] Revisão Semanal
- [x] Quiz do Casal (privado + sobre parceiro)
- [x] Citação do Dia com navegação
- [x] Memórias agregadas
- [x] Painel Admin (stats, CRUD de casais)
- [x] PWA (Service Worker + Manifest)
- [x] Internacionalização PT/EN
- [x] Nav inferior de 3 itens (Hoje/Nós/⚙️)

### 12.2 Versão 2.0 — Conectividade & Engajamento

- [ ] Notificações push (Web Push API)
- [ ] Compartilhamento de fotos com preview
- [ ] Quiz com perguntas geradas por IA
- [ ] Streak tracking (dias consecutivos de uso)
- [ ] Widget de "quantos dias" juntos + marcos
- [ ] Modo escuro
- [ ] Testes automatizados (pytest + Playwright)
- [ ] CI/CD (GitHub Actions)

### 12.3 Versão 3.0 — IA & Personalização

- [ ] Sugestões inteligentes baseadas em histórico
- [ ] Análise de sentimento do diário
- [ ] Resumo semanal automático
- [ ] Quiz adaptativo com perguntas personalizadas
- [ ] Chat contextual entre parceiros
- [ ] Playlists compartilhadas (Spotify API)

### 12.4 Versão 4.0 — Social & Expansão

- [ ] Modo "solteiro" (perguntas para autoconhecimento)
- [ ] Modo "amigos" (perguntas para amizades)
- [ ] Metas de relacionamento compartilhadas
- [ ] Livro digital anual (resumo do ano do casal)
- [ ] Exportação de dados (PDF do relacionamento)
- [ ] API pública para integrações

---

## 13. Roadmap de Lançamento

| Fase | Ação | Prazo | Métrica de Sucesso |
|------|------|-------|-------------------|
| **Pré-lançamento** | Testar fluxo completo local | 1 semana | Zero bugs críticos |
| **Alpha** | 2-3 casais amigos usam por 2 semanas | 2 semanas | 80% retenção D7 |
| **Beta fechado** | 10-20 casais, feedback estruturado | 3 semanas | NPS > 40 |
| **Beta aberto** | Divulgação em grupos de WhatsApp/Telegram | 4 semanas | 100 casais |
| **Lançamento v1.0** | Post Instagram, Product Hunt, grupos | — | 500 usuários ativos |
| **v2.0** | Push notifications + Streaks | 2 meses pós-lançamento | DAU > 20% MAU |
| **v3.0** | IA + Personalização | 4 meses pós-lançamento | Tempo médio > 8min/dia |

---

## 14. Estratégia de Crescimento

### 14.1 Canais de Aquisição

| Canal | Custo | Potencial | Prioridade |
|-------|-------|-----------|------------|
| Boca a boca (casais indicam casais) | Grátis | ★★★★★ | Alta |
| Instagram — posts de perguntas do dia | Grátis | ★★★★☆ | Alta |
| TikTok — vídeos de desafios de casal | Grátis | ★★★★★ | Alta |
| Grupos de WhatsApp/Telegram de casais | Grátis | ★★★★☆ | Média |
| Product Hunt | Grátis | ★★★☆☆ | Média |
| Google Ads (palavras: "app para casais") | $$ | ★★★☆☆ | Baixa |
| TikTok Ads | $$ | ★★★★☆ | Baixa |

### 14.2 Ciclo Viral

```
Casal A usa → Tira print de uma pergunta/dashboard
           → Posta no Instagram/TikTok
           → Casal B vê → Quer experimentar
           → Casal B convida parceiro(a)
           → Ciclo se repete
```

### 14.3 Parcerias Estratégicas

- **Terapeutas de casal:** Indicarem o app como ferramenta de conexão diária
- **Influenciadores de relacionamento:** Conteúdo patrocinado
- **Blogs de casamento:** Menção em "ideias para fortalecer o relacionamento"

---

## 15. Estratégia de Monetização

### 15.1 Modelo Freemium

| Funcionalidade | Gratuito | Premium (R$ 9,90/mês) |
|---------------|----------|----------------------|
| Pergunta do Dia | ✅ | ✅ |
| Diário | ✅ | ✅ |
| Desafios | 1/dia | Ilimitados |
| Quiz do Casal | ✅ | ✅ + IA |
| Citações | 1/dia | Ilimitadas |
| Memórias | Últimas 30 | Todas |
| Fotos | 3/dia | Ilimitadas |
| Temas/Mood do Diário | 5 emojis | Todos + personalizado |
| Análise de Sentimento | — | ✅ |
| Resumo Semanal | — | ✅ |
| Modo Escuro | — | ✅ |
| Exportar Dados | — | ✅ (PDF) |
| Suporte Prioritário | — | ✅ |

### 15.2 Planos

| Plano | Preço | Público |
|-------|-------|---------|
| Gratuito | R$ 0 | Casais explorando |
| Premium Mensal | R$ 9,90 | Casais engajados |
| Premium Anual | R$ 79,90 (33% off) | Casais fiéis |
| Vitalício | R$ 199,90 (lançamento) | Early adopters |

### 15.3 Meios de Pagamento

- Stripe (cartão internacional)
- Mercado Pago / Pix (Brasil)
- Apple Pay / Google Pay

---

## 16. Estratégia de Retenção

### 16.1 Gatilhos Diários

| Horário | Ação | Canal |
|---------|------|-------|
| 08:00 | Notificação: "Pergunta do Dia disponível!" | Push (futuro) |
| 12:00 | "Seu parceiro respondeu a pergunta!" | Push |
| 18:00 | "Hora do desafio de hoje!" | Push |
| 21:00 | "Que tal escrever no diário?" | Push |

### 16.2 Gamificação

| Mecânica | Descrição |
|----------|-----------|
| Streaks | Dias consecutivos de uso (🔥 fogo) |
| Conquistas | "7 dias de perguntas respondidas", "Primeira foto juntos" |
| Níveis de Casal | Bronze → Prata → Ouro → Diamante (baseado em atividades) |
| Selos Mensais | "Fevereiro Cheio de Amor", "Março de Conexão" |

### 16.3 Conteúdo Sazonal

- **Dia dos Namorados:** Temas especiais, perguntas românticas
- **Natal:** Reflexão sobre o ano, metas para o próximo
- **Aniversário de casal:** Surpresa personalizada
- **Estações do ano:** Perguntas temáticas

### 16.4 Prevenção de Churn

- Se 3 dias sem login → email "Saudades de vocês! 💕"
- Se 7 dias sem login → notificação "Temos uma pergunta especial esperando"
- Se 14 dias sem login → "Quer dar uma pausa? Seus dados estão guardados"
- Oferecer "pausa" em vez de deletar conta

---

## 17. Checklist de Melhorias

### 17.1 Pendências Técnicas (P0 — Crítico)

- [x] **Migrar de `on_event("startup")` para lifespan events** ✅
- [ ] **Adicionar testes automatizados** (pytest para API, Playwright para frontend)
- [ ] **Adicionar rate limiting** (proteção contra brute-force)
- [ ] **Adicionar validação de upload de foto** (atual: só verifica no frontend)
- [ ] **Adicionar paginação** em todas as listas (memórias, admin, etc.)

### 17.2 Melhorias de Experiência (P1 — Alta)

- [ ] **Modo escuro** com toggle persistente
- [ ] **Feedback tátil (haptics)** em interações mobile
- [ ] **Swipe gestures** (deslizar para navegar entre seções)
- [ ] **Upload de avatar/foto do perfil** do casal
- [x] **Admin XSS corrigido** (11 locais com `esc()` faltando) ✅
- [x] **`esc()` aprimorado** (agora escapa single quote) ✅
- [x] **Dirty tracking em admin** (prevenção de perda de dados) ✅
- [x] **Batch delete paralelo** com feedback de progresso ✅
- [ ] **Data de início do relacionamento** configurável
- [ ] **Contador de dias** juntos no dashboard
- [ ] **Streak tracking** (dias consecutivos)
- [ ] **Notificações push** reais (Web Push API)

### 17.3 Melhorias de Qualidade de Vida (P2 — Média)

- [ ] **Botão "surprise me"** no dashboard (leva a uma seção aleatória)
- [ ] **Modo offline** (cache de última sessão)
- [ ] **Atalhos de teclado** (1-4 para navegação)
- [ ] **Exportar histórico** como PDF
- [ ] **Compartilhar conquistas** em redes sociais
- [ ] **Música ambiente** na tela de login

### 17.4 Melhorias Futuras (P3 — Baixa)

- [ ] **Widget de iOS/Android** (via PWA ou app nativo)
- [ ] **Integração com Spotify** para playlists compartilhadas
- [ ] **Integração com Google Calendar** para eventos
- [ ] **Integração com ChatGPT** para perguntas personalizadas
- [ ] **App nativo** (React Native ou Flutter)

---

## 18. Backlog Priorizado

### Sprint 1 — Fundação (Agora)

| Item | Esforço | Impacto | Prioridade |
|------|---------|---------|------------|
| Testes automatizados (pytest) | 2 dias | ★★★★★ | P0 |
| Rate limiting | 4 horas | ★★★★★ | P0 |
| Validação de upload | 2 horas | ★★★★☆ | P1 |
| Admin UX (dirty tracking, batch delete) | ✅ | — | Concluído |
| Migrar lifespan events | ✅ | — | Concluído |
| Segurança XSS (esc/attrEsc, admin fixes) | ✅ | — | Concluído |

### Sprint 2 — Retenção

| Item | Esforço | Impacto | Prioridade |
|------|---------|---------|------------|
| Streak tracking | 1 dia | ★★★★★ | P1 |
| Contador de dias | 3 horas | ★★★★☆ | P1 |
| Data de início configurável | 2 horas | ★★★★☆ | P1 |
| Notificações push | 3 dias | ★★★★★ | P1 |

### Sprint 3 — Engajamento

| Item | Esforço | Impacto | Prioridade |
|------|---------|---------|------------|
| Modo escuro | 1 dia | ★★★★☆ | P1 |
| Paginação | 1 dia | ★★★☆☆ | P2 |
| Upload de avatar | 2 dias | ★★★☆☆ | P2 |
| Modo offline | 3 dias | ★★★★☆ | P2 |

### Sprint 4 — Monetização

| Item | Esforço | Impacto | Prioridade |
|------|---------|---------|------------|
| Sistema de planos (gratuito/premium) | 5 dias | ★★★★★ | P1 |
| Stripe integration | 3 dias | ★★★★★ | P1 |
| Mercado Pago integration | 3 dias | ★★★★★ | P1 |
| Gatilhos de upgrade | 2 dias | ★★★★☆ | P2 |

---

## 19. Plano de Evolução do Produto

### 19.1 Fase 1 — Conforto (Meses 1-3)

Foco em **estabilidade e retenção**:
- Finalizar pendências técnicas
- Implementar streaks + contador de dias
- Melhorar experiência mobile (gestos, haptics)
- Coletar feedback dos usuários alpha/beta

### 19.2 Fase 2 — Conexão (Meses 3-6)

Foco em **profundidade do produto**:
- Notificações push
- Modo escuro
- Mais tipos de desafio (vídeo, áudio, localização)
- Quiz com mais categorias
- Análise de sentimento básica

### 19.3 Fase 3 — Personalização (Meses 6-9)

Foco em **IA e individualização**:
- Integração com LLM para perguntas personalizadas
- Resumo semanal automático
- Recomendações baseadas em histórico
- Sugestões de atividades para o casal

### 19.4 Fase 4 — Expansão (Meses 9-12)

Foco em **crescimento e monetização**:
- Plano premium
- Modo "amigos" e "individual"
- API pública
- Livro digital do casal
- App nativo (React Native)

---

## 20. Lista de Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| **Perda de dados** | Baixa | Catastrófico | Backup automático diário (PostgreSQL), export manual |
| **Vazamento de dados íntimos** | Baixa | Catastrófico | Criptografia em repouso, HTTPS obrigatório, fotos em base64 (não URL pública) |
| **Brute-force de login** | Média | Alto | Rate limiting (já planejado), bcrypt lento por design |
| **Churn após 7 dias** | Alta | Alto | Onboarding melhor, notificações, gamificação |
| **Cobertura de testes insuficiente** | Alta | Alto | Adicionar CI/CD com testes obrigatórios |
| **Dependência de serviços gratuitos (Render)** | Média | Médio | Preparar Dockerfile para migração fácil |
| **Baixa adoção (produto nichado)** | Alta | Alto | Estratégia de growth + parcerias com terapeutas |
| **Concorrência (Lovewick, Couply, etc.)** | Média | Médio | Diferenciais: diário compartilhado + desafios variados + preço acessível |
| **Manutenção de longo prazo** | Média | Médio | Código modular, documentação, testes |
| **Custo de LLM (IA)** | Média | Médio | Cache, fallback para conteúdo estático, batch processing |

---

## 21. Métricas (KPIs)

### 21.1 Métricas de Produto

| KPI | Definição | Alvo (3 meses) | Alvo (6 meses) |
|-----|-----------|----------------|----------------|
| **MAU** | Usuários ativos no mês | 500 | 2.000 |
| **DAU** | Usuários ativos no dia | 100 | 500 |
| **DAU/MAU** | Razão de engajamento | 20% | 25% |
| **Retenção D1** | Voltaram no dia seguinte | 60% | 70% |
| **Retenção D7** | Voltaram após 7 dias | 30% | 40% |
| **Retenção D30** | Voltaram após 30 dias | 15% | 25% |
| **Sessões/dia** | Média de sessões por DAU | 2.5 | 3.0 |
| **Tempo médio** | Minutos por sessão | 4 min | 6 min |

### 21.2 Métricas de Engajamento

| KPI | Definição | Alvo |
|-----|-----------|------|
| **Perguntas respondidas/casal** | Média semanal | 4/7 |
| **Desafios completados/casal** | Média semanal | 3/5 |
| **Entradas de diário/casal** | Média semanal | 3 |
| **Streak médio** | Dias consecutivos de uso | 7 dias |
| **Convites enviados** | Por usuário ativo | 0.5 |

### 21.3 Métricas de Negócio

| KPI | Definição | Alvo (1 ano) |
|-----|-----------|--------------|
| **Taxa de conversão** | Grátis → Premium | 5% |
| **LTV** | Lifetime Value | R$ 60 |
| **CAC** | Custo de Aquisição | R$ 5 |
| **Receita mensal** | MRR | R$ 5.000 |
| **NPS** | Net Promoter Score | 50+ |
| **Churn rate** | Cancelamentos/mês | < 5% |

### 21.4 Métricas Técnicas

| KPI | Alvo |
|-----|------|
| **Uptime** | 99.9% |
| **Tempo de resposta P95** | < 500ms |
| **Erros 5xx** | < 0.1% |
| **Tamanho do bundle** | < 200KB (HTML + CSS + JS inline) |
| **Lighthouse Performance** | > 85 |
| **Lighthouse PWA** | > 90 |

---

## 22. Plano de Testes A/B

### 22.1 Teste 1 — Onboarding Flow

| Variante | Descrição | Métrica |
|----------|-----------|---------|
| **A (controle)** | Login direto → dashboard | Retenção D1 |
| **B (teste)** | Login → tour guiado (3 slides) → dashboard | Retenção D1 |

**Hipótese:** Tour guiado aumenta retenção D1 em 15%  
**Duração:** 2 semanas  
**Público:** 50% dos novos usuários cada

### 22.2 Teste 2 — Notificações

| Variante | Descrição | Métrica |
|----------|-----------|---------|
| **A (controle)** | Sem notificações | DAU |
| **B (teste)** | 1 notificação/dia (pergunta) | DAU |
| **C (teste)** | 2 notificações/dia (pergunta + desafio) | DAU |

**Hipótese:** 2 notificações aumentam DAU em 30%, mas podem irritar  
**Duração:** 3 semanas  
**Público:** 33% cada

### 22.3 Teste 3 — Preços Premium

| Variante | Descrição | Métrica |
|----------|-----------|---------|
| **A (controle)** | R$ 9,90/mês, R$ 79,90/ano | Taxa de conversão |
| **B (teste)** | R$ 14,90/mês, R$ 99,90/ano | Taxa de conversão |
| **C (teste)** | R$ 9,90/mês, R$ 69,90/ano (12% off) | Taxa de conversão |

**Hipótese:** Preço mais baixo (C) maximiza receita total  
**Duração:** 1 mês  
**Público:** 33% cada (novos usuários apenas)

### 22.4 Teste 4 — Dashboard Layout

| Variante | Descrição | Métrica |
|----------|-----------|---------|
| **A (controle)** | Cards verticais (atual) | Cliques em ações |
| **B (teste)** | Grid 2×2 com resumos maiores | Cliques em ações |

**Hipótese:** Grid aumenta cliques em ações em 20%  
**Duração:** 2 semanas  
**Público:** 50% cada

---

## 23. Plano de Acessibilidade

### 23.1 WCAG 2.1 Compliance (Nível AA)

| Critério | Estado | Ação Necessária |
|----------|--------|-----------------|
| **1.1.1 Texto Alternativo** | ❌ | Adicionar `alt` descritivo a imagens e SVGs |
| **1.4.3 Contraste Mínimo** | ⚠️ | Verificar contraste do rosa claro (#ffb5c2) sobre branco |
| **1.4.4 Redimensionar Texto** | ✅ | Usa rem/em, suporta zoom 200% |
| **2.1.1 Teclado** | ❌ | Navegação por Tab + Enter nas seções SPA |
| **2.4.1 Pular Navegação** | ❌ | Adicionar "Skip to content" |
| **2.4.4 Propósito do Link** | ❌ | Botões sem texto (⚙️) precisam de aria-label |
| **2.4.7 Foco Visível** | ❌ | Adicionar outline focus em todos os elementos interativos |
| **3.3.2 Rótulos** | ❌ | Inputs sem label explícito (login, diário) |
| **4.1.2 Nome, Função, Valor** | ❌ | ARIA roles para modal, tabs, cards interativos |

### 23.2 Melhorias Prioritárias

1. **Adicionar `aria-label`** no botão ⚙️ settings, lang toggle, e cards clicáveis
2. **Adicionar `role="navigation"`** na nav inferior e `aria-current="page"` no item ativo
3. **Adicionar `role="dialog"`** no modal de settings
4. **Adicionar `role="tablist"`** nos tabs (se implementar tabs)
5. **Garantir contraste mínimo** 4.5:1 para texto normal
6. **Suporte a `prefers-reduced-motion`** para animações

### 23.3 Testes

- [ ] Lighthouse Accessibility audit
- [ ] axe DevTools scan
- [ ] Teste manual com VoiceOver (macOS) / TalkBack (Android)
- [ ] Teste com leitor de tela (NVDA ou JAWS)
- [ ] Navegação apenas por teclado

---

## 24. Plano de Segurança

### 24.1 Medidas Implementadas

| Medida | Status | Detalhes |
|--------|--------|----------|
| **Senhas com bcrypt** | ✅ | Hash com salt + custo 12 rounds |
| **JWT com expiração** | ✅ | 48h de validade, assinado com HS256 |
| **Fallback SHA-256** | ✅ | Upgrade automático para bcrypt no login |
| **Admin com credenciais fixas** | ✅ | `ADMIN_USERS` via env var (sem fallback hardcoded) |
| **HTTPS** | ✅ | Render fornece TLS automático |
| **Sanitização de saída** | ✅ | `esc()` + `attrEsc()` previnem XSS (texto e atributos) |
| **CORS** | ✅ | Middleware configurado |
| **Pool de conexão** | ✅ | `pool_size=10, max_overflow=20, pool_pre_ping=True` |
| **Service Worker** | ✅ | Cache apenas requisições GET |
| **Admin XSS** | ✅ | 11 locais corrigidos com `esc()` |
| **Single quote escaping** | ✅ | `esc()` agora escapa `&#39;` |
| **Dirty tracking** | ✅ | `beforeunload` + `markDirty()` em admin |
| **Batch delete** | ✅ | Paralelo com feedback de progresso |
| **SQL Injection** | ✅ | ORM previne (SQLAlchemy) |
| **XSS** | ✅ | Template engine com inserção controlada |

### 24.2 Medidas Pendentes

| Medida | Prioridade | Ação |
|--------|-----------|------|
| **Rate limiting** | P0 | Adicionar `slowapi` ou middleware custom |
| **Content Security Policy** | P1 | Header CSP strict |
| **Validação de upload** | P1 | Limitar tamanho (5MB), tipo MIME, sanitizar base64 |
| **Helmet.js-like headers** | P1 | Adicionar X-Frame-Options, X-Content-Type-Options, etc. |
| **Auditoria de dependências** | P2 | `pip-audit` regular, Dependabot |
| **Logs de segurança** | P2 | Logar tentativas de login falhas, ações admin |
| **Criptografia em repouso** | P2 | Foto base64 no DB é texto plano — considerar criptografia |

### 24.3 Política de Senhas Admin

- Mínimo 8 caracteres
- Alterar senha padrão imediatamente
- Não reutilizar senhas de outros serviços
- 2FA (futuro)

---

## 25. Plano de SEO

### 25.1 SEO On-Page

| Elemento | Estado | Ação |
|----------|--------|------|
| **Title tag** | ⚠️ | `Still Learning 💕` — bom, mas poderia ser mais descritivo |
| **Meta description** | ❌ | Adicionar: "Still Learning: o app para casais se conectarem todos os dias com perguntas, desafios e diário compartilhado" |
| **Open Graph** | ❌ | Adicionar og:title, og:description, og:image, og:url |
| **Twitter Cards** | ❌ | Adicionar twitter:card, twitter:title, twitter:description |
| **Structured Data** | ❌ | Schema.org `WebApplication` |
| **Canonical URL** | ❌ | Adicionar link rel="canonical" |
| **Sitemap.xml** | ❌ | Criar sitemap.xml |
| **Robots.txt** | ❌ | Criar robots.txt |
| **Alt text** | ❌ | Adicionar alt nas imagens SVG |

### 25.2 Palavras-chave Alvo

| Palavra-chave | Volume (BR) | Concorrência | Prioridade |
|---------------|-------------|--------------|------------|
| app para casais | ★★★★☆ | Média | ★★★★★ |
| aplicativo de casal | ★★★☆☆ | Média | ★★★★☆ |
| perguntas para casais | ★★★★☆ | Baixa | ★★★★★ |
| diário compartilhado casal | ★★☆☆☆ | Baixa | ★★★★☆ |
| desafios para casais | ★★★☆☆ | Baixa | ★★★★☆ |
| fortalecer relacionamento | ★★★★☆ | Alta | ★★★☆☆ |
| quiz para casais | ★★★☆☆ | Média | ★★★☆☆ |

### 25.3 Estratégia de Conteúdo

- Blog com artigos sobre conexão em relacionamentos
- Posts de Instagram com perguntas do dia (link na bio)
- Guest posts em blogs de casamento/relacionamento
- Parceria com influenciadores para review

---

## 26. Plano de Internacionalização

### 26.1 Status Atual

- **Português (BR):** ✅ Completo
- **Inglês (US):** ✅ Completo
- **Espanhol:** ❌ Pendente
- **Francês:** ❌ Pendente
- **Italiano:** ❌ Pendente

### 26.2 Arquitetura de Tradução

**Atual (translations.py):**
```python
L = {
    "key": {
        "pt": "texto em português",
        "en": "text in english"
    }
}

def t(key, lang="pt"):
    val = L.get(key, {})
    return val.get(lang, val.get("pt", key))
```

**Proposta para novos idiomas:**
```python
L = {
    "key": {
        "pt": "...",
        "en": "...",
        "es": "...",   # novo
        "fr": "...",   # novo
        "it": "..."    # novo
    }
}
```

### 26.3 Roadmap de Localização

| Idioma | Prioridade | Esforço | Prazo |
|--------|-----------|---------|-------|
| **Espanhol** | ★★★★★ | 2 dias | Mês 1 |
| **Francês** | ★★★★☆ | 2 dias | Mês 2 |
| **Italiano** | ★★★☆☆ | 2 dias | Mês 3 |
| **Alemão** | ★★☆☆☆ | 2 dias | Mês 6 |

### 26.4 Detecção de Idioma

**Atual:** Cookie `lang` definido manualmente pelo usuário  
**Proposto:** Detecção automática via `Accept-Language` header + fallback manual

### 26.5 Conteúdo Sensível ao Idioma

| Conteúdo | PT | EN | Outros |
|----------|----|----|--------|
| 40 perguntas diárias | ✅ | ✅ | ❌ |
| 41 temas de perguntas íntimas | ✅ | ✅ | ❌ |
| 18 sugestões de desafios | ✅ | ✅ | ❌ |
| 30 citações com curiosidades | ✅ | ✅ | ❌ |
| Interface (100+ chaves) | ✅ | ✅ | ❌ |
| Enigmas | ✅ | ✅ | ❌ |

---

## Apêndice A — Glossário

| Termo | Definição |
|-------|-----------|
| **Couple** | Entidade que representa o par de usuários |
| **Dashboard** | Tela principal (Hoje) com resumo do dia |
| **Desafio** | Atividade diária: enigma, pergunta, foto, etc. |
| **Diário** | Entrada de texto diária de cada parceiro |
| **JWT** | JSON Web Token para autenticação stateless |
| **LoginEvent** | Registro de cada login para auditoria |
| **Memórias** | Agregação de todas as interações passadas |
| **Pergunta do Dia** | Pergunta diária respondida por ambos |
| **PWA** | Progressive Web App (app instalável) |
| **Quote** | Citação inspiradora diária |
| **Review** | Reflexão semanal do casal |
| **SPA** | Single Page Application (navegação sem reload) |

## Apêndice B — Variáveis de Ambiente

```
# .env

# Admin credentials (JSON array of {username, password} pairs)
ADMIN_USERS=[{"username":"ttt","password":"sisrat"},{"username":"T","password":"trs123"},{"username":"Tadmin","password":"trs123"}]

# JWT secret (change in production!)
JWT_SECRET=sl-jwt-secret-change-me-in-production-2024

# Database URL (defaults to SQLite if not set)
# DATABASE_URL=postgresql://user:pass@host/db
```

## Apêndice C — Dependências (requirements.txt)

```
fastapi>=0.104.0
uvicorn>=0.24.0
sqlalchemy>=2.0.0
bcrypt>=4.1.0
pyjwt>=2.0.0
python-dotenv>=1.0.0
```

---

> **Documento gerado em:** 12 de julho de 2026  
> **Próxima revisão:** 12 de agosto de 2026  
> **Manutenção:** Tarsis Gonçalves
