#!/usr/bin/env python3
"""Generate PDF documentation for Still Learning using reportlab."""

import os

# Try reportlab first (better unicode support), fall back to fpdf2
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem,
        PageBreak, Table, TableStyle, HRFlowable
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.lib.utils import simpleSplit
    from xml.sax.saxutils import escape as xml_escape
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = BASE_DIR


def generate_with_reportlab(language="pt"):
    """Generate PDF using reportlab (better unicode/emoji support).
    language: 'pt' for Portuguese, 'en' for English."""
    is_en = language == "en"
    filename = "Still_Learning_Documentation.pdf" if is_en else "Still_Learning_Documentacao.pdf"
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=26, textColor=HexColor('#e88a9a'),
        spaceAfter=6*mm, alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle', parent=styles['Normal'],
        fontSize=12, textColor=HexColor('#b0a0a0'),
        alignment=TA_CENTER, spaceAfter=4*mm
    )
    h1_style = ParagraphStyle(
        'H1', parent=styles['Heading1'],
        fontSize=16, textColor=HexColor('#e88a9a'),
        spaceBefore=6*mm, spaceAfter=3*mm,
        fontName='Helvetica-Bold'
    )
    h2_style = ParagraphStyle(
        'H2', parent=styles['Heading2'],
        fontSize=11, textColor=HexColor('#4a4a4a'),
        spaceBefore=4*mm, spaceAfter=2*mm,
        fontName='Helvetica-Bold'
    )
    body_style = ParagraphStyle(
        'CustomBody', parent=styles['Normal'],
        fontSize=9, leading=13,
        textColor=HexColor('#4a4a4a'),
        alignment=TA_JUSTIFY,
        spaceAfter=2*mm
    )
    bullet_style = ParagraphStyle(
        'Bullet', parent=body_style,
        leftIndent=8*mm, bulletIndent=3*mm,
        spaceBefore=0.5*mm, spaceAfter=0.5*mm
    )
    code_style = ParagraphStyle(
        'Code', parent=styles['Code'],
        fontSize=7, leading=9,
        leftIndent=5*mm,
        backColor=HexColor('#f5f0f2'),
        spaceAfter=2*mm,
        fontName='Courier'
    )
    
    stories = []
    
    def add_title_page():
        stories.append(Spacer(1, 40*mm))
        stories.append(Paragraph("Still Learning", title_style))
        subtitle = "Complete Product Documentation" if is_en else "Documentacao Completa do Produto"
        stories.append(Paragraph(subtitle, subtitle_style))
        stories.append(Spacer(1, 10*mm))
        version_text = "Version 2.1 &nbsp;|&nbsp; July 2026" if is_en else "Versao 2.1 &nbsp;|&nbsp; Julho 2026"
        stories.append(Paragraph(
            f"{version_text}<br/>"
            "Stack: Python 3.11+ / FastAPI / SQLAlchemy / bcrypt + JWT<br/>"
            "URL: https://still-learning.onrender.com",
            subtitle_style
        ))
        stories.append(PageBreak())
    
    def h1(text):
        stories.append(Paragraph(text, h1_style))
        stories.append(HRFlowable(
            width="100%", thickness=0.5,
            color=HexColor('#ffc8d0'),
            spaceAfter=3*mm
        ))
    
    def h2(text):
        stories.append(Paragraph(text, h2_style))
    
    def p(text):
        stories.append(Paragraph(text, body_style))
    
    def b(text):
        stories.append(Paragraph(f"\u2022 {text}", bullet_style))
    
    def code(text):
        stories.append(Paragraph(
            xml_escape(text).replace('\n', '<br/>'),
            code_style
        ))
    
    # ============== BUILD CONTENT ==============
    
    add_title_page()
    
    if is_en:
        _build_english_content(stories, h1, h2, p, b, code)
    else:
        _build_portuguese_content(stories, h1, h2, p, b, code)
    
    # Build PDF
    doc.build(stories)
    print(f"PDF generated: {output_path}")
    print(f"Total pages: {doc.page}")
    return True


def _build_portuguese_content(stories, h1, h2, p, b, code):
    """Build Portuguese PDF content."""
    # 1. Arquitetura
    h1("1. Arquitetura Completa do Sistema")
    p(
        "Stack: Python 3.11+ / FastAPI / SQLAlchemy / SQLite (dev) / PostgreSQL (prod) / "
        "bcrypt + JWT. O sistema segue arquitetura monolitica com renderizacao server-side "
        "leve e JavaScript no cliente para navegacao SPA-like."
    )
    h2("Camadas")
    b("Cliente: HTML + CSS + Vanilla JS, PWA com Service Worker e Manifest")
    b("Servidor: FastAPI com Uvicorn, 55 endpoints REST")
    b("Dados: SQLAlchemy ORM, 16 tabelas, migracoes automaticas")
    b("Autenticacao: bcrypt para senhas, JWT (HS256, 48h) para sessoes")
    b("Deploy: Render (free tier), PostgreSQL em producao")
    h2("Estrutura de Diretorios")
    code(
        "project quiz code/\n"
        "  main.py           55 endpoints (1893 linhas)\n"
        "  models.py         16 modelos ORM\n"
        "  database.py       Engine + Session SQLAlchemy\n"
        "  translations.py   i18n PT/EN (431 linhas)\n"
        "  static/           CSS, PWA manifest, sw.js, icons SVG\n"
        "  templates/        6 templates HTML\n"
        "  docs/             Documentacao em PDF"
    )
    
    # 2. Fluxo de Navegacao
    stories.append(PageBreak())
    h1("2. Fluxo de Navegacao")
    p(
        "O usuario entra pelo login (/). Se for perfil 'couple', redireciona para "
        "/still-learning com nav inferior de 3 itens: Hoje (dashboard inteligente), "
        "Nos (sub-menus de diario, memorias, quiz, desafio), e Gear (configuracoes/idioma/sair). "
        "Se for perfil 'quiz', inicia sessao de 10 perguntas com fluxo /start &rarr; /quiz &rarr; /resultado."
    )
    h2("Nav Interna (SPA)")
    b("Hoje: Dashboard, Pergunta do Dia, Desafio, Citacao, Agenda, To-Dos, Review Semanal")
    b("Nos: Diario, Memorias, Quiz do Casal, Desafio")
    b("Gear: Idioma (PT/EN), Sair (logout + clear localStorage)")
    h2("Autenticacao")
    p(
        "Login &rarr; JWT armazenado em localStorage &rarr; api() envia "
        "Authorization: Bearer &lt;token&gt; em toda requisicao &rarr; require_auth() "
        "no backend valida JWT (HS256, 48h)."
    )
    
    # 3. Jornada do Usuario
    stories.append(PageBreak())
    h1("3. Jornada do Usuario")
    h2("Primeiro Acesso")
    b("Usuario acessa still-learning.onrender.com e faz login")
    b("Sistema verifica bcrypt (com fallback SHA-256 legado)")
    b("Se 'couple': gera JWT 48h e redireciona para /still-learning com dashboard vazio")
    b("Se 'quiz': inicia nova sessao com 10 perguntas ou retoma sessao incompleta")
    h2("Jornada Diaria")
    b("Manha: Abre Hoje &rarr; ve saudacao, stats, citacao do dia")
    b("Tarde: Abre Pergunta do Dia &rarr; responde e aguarda parceiro")
    b("Noite: Abre Nos &rarr; Diario &rarr; escreve sobre o dia com mood")
    h2("Jornada Semanal")
    b("Review Semanal com reflexao")
    b("Desafios variados: enigma, pergunta intima, foto, citacao, desafio personalizado")
    
    # 4. Wireframes
    stories.append(PageBreak())
    h1("4. Wireframes em Texto")
    p(
        "A interface segue layout mobile-first com max-width de 520px, header fixo com "
        "titulo e botao de idioma, conteudo central em cards com sombra rosa, e nav "
        "inferior fixa com 3 itens. As cores sao rosa pastel (#ffb5c2), off-white "
        "(#fdf6f0) e texto em cinza escuro (#4a4a4a)."
    )
    h2("Telas Principais")
    b("Login: Inputs arredondados, coracao SVG, botao gradiente, toggle PT/EN")
    b("Hoje: Cards de saudacao, stats (pilulas), pergunta, diario, desafio, citacao, agenda")
    b("Nos: Grid 2x2 com cards para Diario, Memorias, Quiz, Desafio")
    b("Settings (Modal): Overlay semi-transparente com opcoes Idioma e Sair")
    b("Pergunta do Dia: Card da pergunta, textarea, botao enviar, resposta do parceiro")
    b("Diario: Secao 'Hoje' com entrada propria + timeline de dias anteriores")
    
    # 5. Estrutura das Paginas
    stories.append(PageBreak())
    h1("5. Estrutura das Paginas")
    h2("Template Base")
    code(
        '<!DOCTYPE html>\n'
        '<html lang="pt-BR">\n'
        '<head>\n'
        '  <meta charset="UTF-8">\n'
        '  <meta name="viewport" content="width=device-width">\n'
        '  <meta name="theme-color" content="#ffb5c2">\n'
        '  <link rel="manifest" href="/static/manifest.json">\n'
        '  <link rel="stylesheet" href="/static/style.css">\n'
        '</head>\n'
        '<body>\n'
        '  <div class="floating-bg"></div>\n'
        '</body>\n'
        '</html>'
    )
    h2("Templates")
    b("index.html: Login (ponto de entrada)")
    b("quiz.html: Quiz interativo (10 perguntas)")
    b("result.html: Resultado do quiz com mensagem personalizada")
    b("retry.html: Retry apos conclusao")
    b("couple.html: App principal SPA-like (~2250 linhas)")
    b("admin.html: Painel administrativo (~1800 linhas)")
    
    # 6. Componentes Reutilizaveis
    stories.append(PageBreak())
    h1("6. Componentes Reutilizaveis")
    h2("Frontend (Vanilla JS)")
    b("api(path, opts): Wrapper fetch com JWT + headers + JSON automatico")
    b("showSection(name): Navegacao SPA (troca conteudo + nav ativa)")
    b("backLink(): Botao 'Voltar' padronizado")
    b("esc(s): Sanitizacao de HTML (textContent + atributos)")
    b("attrEsc(s): Sanitizacao de atributos HTML (escapamento de aspas)")
    b("toggleLang(): Troca PT/EN com cookie + recarrega")
    b("logout(e): Clean do localStorage + redirect para /")
    b("toast(msg): Toast flutuante nao-intrusivo (3s)")
    b("markDirty(): Marca formulario como nao salvo em admin")
    b("initDecorations(): Fundo animado com emojis flutuantes + estrelas")
    h2("Backend (Python)")
    b("_render(name, **kwargs): Template engine caseira (string replace)")
    b("require_auth(): Dependency Injection de autenticacao JWT (Bearer apenas)")
    b("check_admin(): Validacao de credenciais admin (ADMIN_USERS env var)")
    b("get_partner_name(): Resolve nome do parceiro no casal")
    b("hash_pw() / verify_pw(): Hash/verificacao bcrypt + SHA-256 fallback")
    b("create_jwt() / decode_jwt(): Geracao/validacao JWT HS256")
    
    # 7. Sistema de Design
    stories.append(PageBreak())
    h1("7. Sistema de Design")
    h2("Tokens CSS")
    code(
        ":root {\n"
        "  --pink: #ffb5c2;           /* Primaria */\n"
        "  --pink-dark: #e88a9a;      /* Hover/Active */\n"
        "  --cream: #fff5f5;           /* Superficie */\n"
        "  --text: #4a4a4a;            /* Texto principal */\n"
        "  --text-light: #b0a0a0;      /* Texto secundario */\n"
        "  --bg: #fdf6f0;              /* Fundo */\n"
        "  --radius-sm: 10px;\n"
        "  --radius-cloud: 18px;\n"
        "  --shadow: 0 4px 20px rgba(255,181,194,0.2);\n"
        "  --ease-bounce: cubic-bezier(0.34,1.56,0.64,1);\n"
        "}"
    )
    h2("Tipografia")
    b("Titulos: 'Press Start 2P', monospace (9px)")
    b("Corpo: -apple-system, BlinkMacSystemFont, sans-serif (0.9rem)")
    h2("Icones")
    p("Uso exclusivo de emoji Unicode: 🏠 Hoje, 💑 Nos, ⚙️ Config, 💕 Amor, 💭 Pergunta, 📖 Diario, ✨ Memorias, 🎯 Desafio, ❓ Quiz, 📅 Agenda, 📋 To-Dos, 💌 Citacao, 🔔 Notificacao.")
    
    # 8. Guia Visual
    h2("8. Guia Visual")
    p(
        "Paleta rosa pastel com off-white. Layout mobile-first (max-width: 520px). "
        "Cards com sombra suave, cantos arredondados (10-18px). "
        "Header fixo com titulo e botao de idioma. Nav inferior fixa com 3 itens. "
        "Transicoes com cubic-bezier bounce para sensacao organica."
    )
    h2("Responsividade")
    b("Desktop (&gt;768px): Centralizado em 520px")
    b("Mobile (&lt;768px): Largura total com padding 16px")
    b("Mobile pequeno (&lt;375px): Font-size reduzido 10-15%")
    
    # 9. Banco de Dados
    stories.append(PageBreak())
    h1("9. Estrutura do Banco de Dados")
    p("16 tabelas no SQLAlchemy ORM. Banco SQLite em dev, PostgreSQL em prod.")
    h2("Tabelas")
    b("profiles: Perfis de usuario (quiz ou couple)")
    b("login_credentials: Login + password_hash (bcrypt)")
    b("quiz_sessions: Sessoes de quiz com respostas (JSON)")
    b("login_events: Auditoria de login")
    b("couples: Pares de usuarios (user1_id, user2_id)")
    b("diary_entries: Entradas do diario por data")
    b("daily_questions: Perguntas diarias com respostas (answer_a, answer_b)")
    b("challenges: Desafios com 5 tipos rotativos")
    b("agenda_events: Eventos da agenda com data/hora")
    b("todo_items: Itens de tarefas com status done")
    b("weekly_reviews: Revisoes semanais (reflection_a, reflection_b)")
    b("quiz_answers: Respostas do quiz do casal (about_self, about_partner)")
    b("quote_refreshes: Estado de navegacao de citacoes")
    b("photos: Fotos em base64 com caption")
    
    # 10. APIs
    stories.append(PageBreak())
    h1("10. APIs")
    p("Total: 55 endpoints REST documentados. Autenticacao via JWT Bearer exclusivamente.")
    h2("Autenticacao (1 endpoint)")
    b("POST /api/login: Login com name+password, retorna JWT token + dados do usuario")
    h2("Quiz (5 endpoints)")
    b("POST /api/start: Iniciar sessao de quiz")
    b("GET /api/question/{id}: Pergunta atual")
    b("POST /api/answer/{id}: Submeter resposta")
    b("GET /api/result/{id}: Resultado completo com score e mensagem")
    b("POST /api/result/final/{id}: Resposta final (romantica)")
    h2("Couple App (28 endpoints)")
    b("Dashboard, Pergunta do Dia, Diario (CRUD)")
    b("Desafios: enigma, pergunta intima, foto, citacao, desafio personalizado (+ delete)")
    b("Agenda (add + delete), To-Dos (add + toggle + delete), Review Semanal")
    b("Citacoes, Quiz do Casal, Memorias")
    h2("Admin (21 endpoints)")
    b("CRUD de casais, perfis, perguntas, desafios, fotos, diarios, agenda, todos")
    b("Estatisticas, historico de login, resultados de quiz")
    b("Reset/delecao de dados de casal (com batch delete paralelo)")
    
    # 11. IA
    stories.append(PageBreak())
    h1("11. Estrutura de IA")
    p(
        "Estado atual: Sem IA generativa. Todo conteudo e pre-definido: "
        "40 perguntas diarias, 41 temas, 18 sugestoes de desafio, 30 citacoes com curiosidades. "
        "A rotacao e deterministica baseada em dias desde o inicio do casal. "
        "O quiz usa random.shuffle() para ordenar 10 das 40+ perguntas disponiveis."
    )
    h2("Oportunidades Futuras")
    b("Perguntas personalizadas via LLM (GPT-4 / Claude)")
    b("Analise de sentimento das entradas de diario (NLP)")
    b("Resumo semanal automatico via LLM")
    b("Recomendacao de citacoes por mood (embeddings + similaridade)")
    b("Quiz adaptativo com perguntas que o parceiro errou")
    b("Detecao de padroes de comunicacao")
    
    # 12. Roadmap Dev
    h2("12. Roadmap de Desenvolvimento")
    h2("v1.0 - MVP (Atual)")
    b("Login bcrypt + JWT, Dashboard, Pergunta do Dia, Diario")
    b("Desafios (5 tipos: enigma, foto, pergunta intima, desafio personalizado, citacao)")
    b("Agenda, To-Dos, Review Semanal, Quiz do Casal, Citacao, Memorias")
    b("Admin (CRUD de casais/perfis, estatisticas)")
    b("PWA (Service Worker + Manifest), i18n PT/EN")
    b("Nav inferior 3 itens (Hoje/Nos/Gear)")
    h2("v2.0 - Conectividade")
    b("Notificacoes push (Web Push API), Streak tracking")
    b("Modo escuro, Testes automatizados (pytest + Playwright)")
    b("CI/CD (GitHub Actions)")
    h2("v3.0 - IA e Personalizacao")
    b("Sugestoes inteligentes, Analise de sentimento do diario")
    b("Resumo semanal automatico, Quiz adaptativo, Chat contextual")
    h2("v4.0 - Social e Expansao")
    b("Modo solteiro/amigos, Metas de relacionamento compartilhadas")
    b("Livro digital anual, Exportacao PDF, API publica")
    
    # 13. Lancamento
    stories.append(PageBreak())
    h1("13. Roadmap de Lancamento")
    b("Pre-lancamento: Testar fluxo completo local (1 semana)")
    b("Alpha: 2-3 casais amigos usam por 2 semanas (retencao D7 > 80%)")
    b("Beta fechado: 10-20 casais com feedback estruturado (NPS > 40)")
    b("Beta aberto: Divulgacao em grupos WhatsApp/Telegram (100 casais)")
    b("Lancamento v1.0: Instagram, Product Hunt (500 usuarios ativos)")
    b("v2.0: Push + Streaks (2 meses pos-lancamento, DAU > 20% MAU)")
    b("v3.0: IA (4 meses pos-lancamento, tempo medio > 8min/dia)")
    
    # 14. Crescimento
    h1("14. Estrategia de Crescimento")
    h2("Canais de Aquisicao")
    b("Boca a boca (casais indicam casais) - Gratuito, potencial altissimo")
    b("Instagram - posts de perguntas do dia com link na bio")
    b("TikTok - videos de desafios de casal")
    b("Grupos de WhatsApp/Telegram de casais")
    b("Parcerias com terapeutas de casal e influenciadores de relacionamento")
    h2("Ciclo Viral")
    p("Casal A usa &rarr; Tira print de uma pergunta/dashboard &rarr; Posta no Instagram/TikTok &rarr; Casal B ve &rarr; Quer experimentar &rarr; Casal B convida parceiro(a) &rarr; Ciclo se repete.")
    
    # 15. Monetizacao
    stories.append(PageBreak())
    h1("15. Estrategia de Monetizacao")
    h2("Modelo Freemium")
    b("Gratuito: Funcionalidades basicas (1 desafio/dia, 3 fotos/dia, ultimas 30 memorias)")
    b("Premium Mensal (R$9,90): Desafios ilimitados, fotos ilimitadas, todas as memorias, analise de sentimento, modo escuro")
    b("Premium Anual (R$79,90/ano): 33% de desconto")
    b("Vitalicio (R$199,90): Early adopters, lancamento")
    h2("Meios de Pagamento")
    b("Stripe (cartao internacional)")
    b("Mercado Pago / Pix (Brasil)")
    b("Apple Pay / Google Pay")
    
    # 16. Retencao
    h1("16. Estrategia de Retencao")
    h2("Gatilhos Diarios (Push)")
    b("08:00 - 'Pergunta do Dia disponivel!'")
    b("12:00 - 'Seu parceiro respondeu a pergunta!'")
    b("18:00 - 'Hora do desafio de hoje!'")
    b("21:00 - 'Que tal escrever no diario?'")
    h2("Gamificacao")
    b("Streaks: Dias consecutivos de uso (fogo)")
    b("Conquistas: '7 dias de perguntas', 'Primeira foto juntos'")
    b("Niveis de Casal: Bronze &rarr; Prata &rarr; Ouro &rarr; Diamante")
    b("Selos Mensais: 'Fevereiro Cheio de Amor', 'Marco de Conexao'")
    h2("Prevencao de Churn")
    b("3 dias sem login: Email 'Saudades de voces!'")
    b("7 dias: Notificacao com pergunta especial esperando")
    b("14 dias: 'Quer dar uma pausa? Seus dados estao guardados'")
    
    # 17. Checklist
    stories.append(PageBreak())
    h1("17. Checklist de Melhorias")
    h2("P0 - Critico")
    b("[OK] Migrar de on_event() para lifespan events")
    b("[ ] Adicionar testes automatizados (pytest para API, Playwright para frontend)")
    b("[ ] Rate limiting (protecao contra brute-force)")
    b("[ ] Validacao de upload de foto (tamanho, tipo MIME)")
    b("[ ] Paginacao em todas as listas (memorias, admin)")
    h2("P1 - Alta")
    b("[OK] XSS admin corrigido (11 locais)")
    b("[OK] esc() aprimorado (escapamento de single quote)")
    b("[OK] Dirty tracking em admin (beforeunload + markDirty)")
    b("[OK] Batch delete paralelo com feedback de progresso")
    b("[ ] Modo escuro com toggle persistente")
    b("[ ] Streak tracking (dias consecutivos de uso)")
    b("[ ] Notificacoes push reais (Web Push API)")
    b("[ ] Data de inicio do relacionamento configuravel")
    h2("P2 - Media")
    b("[ ] Botao 'surprise me' no dashboard")
    b("[ ] Modo offline (cache da ultima sessao)")
    b("[ ] Atalhos de teclado (1-4 para navegacao)")
    b("[ ] Exportar historico como PDF")
    
    # 18. Backlog
    h1("18. Backlog Priorizado")
    h2("Sprint 1 - Fundacao (Agora)")
    b("[OK] Migrar lifespan events, Admin UX, XSS fixes")
    b("[ ] Testes automatizados (2 dias, P0)")
    b("[ ] Rate limiting (4 horas, P0)")
    b("[ ] Validacao de upload (2 horas, P1)")
    h2("Sprint 2 - Retencao")
    b("[ ] Streak tracking (1 dia, P1)")
    b("[ ] Contador de dias (3 horas, P1)")
    b("[ ] Notificacoes push (3 dias, P1)")
    h2("Sprint 3 - Engajamento")
    b("[ ] Modo escuro (1 dia, P1)")
    b("[ ] Paginacao (1 dia, P2)")
    h2("Sprint 4 - Monetizacao")
    b("[ ] Sistema de planos gratuito/premium (5 dias, P1)")
    b("[ ] Stripe + Mercado Pago (6 dias, P1)")
    
    # 19. Evolucao
    stories.append(PageBreak())
    h1("19. Plano de Evolucao do Produto")
    h2("Fase 1 - Conforto (Meses 1-3)")
    p("Foco em estabilidade e retencao: finalizar pendencias tecnicas, implementar streaks + contador de dias, melhorar experiencia mobile (gestos, haptics), coletar feedback dos usuarios alpha/beta.")
    h2("Fase 2 - Conexao (Meses 3-6)")
    p("Foco em profundidade do produto: notificacoes push, modo escuro, mais tipos de desafio (video, audio, localizacao), quiz com mais categorias, analise de sentimento basica.")
    h2("Fase 3 - Personalizacao (Meses 6-9)")
    p("Foco em IA e individualizacao: integracao com LLM para perguntas personalizadas, resumo semanal automatico, recomendacoes baseadas em historico, sugestoes de atividades.")
    h2("Fase 4 - Expansao (Meses 9-12)")
    p("Foco em crescimento e monetizacao: plano premium, modo amigos e individual, API publica, livro digital do casal, app nativo (React Native).")
    
    # 20. Riscos
    h1("20. Lista de Riscos")
    b("Perda de dados (Baixa/Catastrofico): Backup PostgreSQL + export manual")
    b("Vazamento de dados intimos (Baixa/Catastrofico): HTTPS, criptografia em repouso")
    b("Brute-force de login (Media/Alto): Rate limiting + bcrypt lento por design")
    b("Churn apos 7 dias (Alta/Alto): Onboarding melhorado, notificacoes, gamificacao")
    b("Baixa adocao (Alta/Alto): Growth hacking + parcerias com terapeutas")
    b("Concorrencia (Lovewick, Couply) (Media/Medio): Diferenciais: diario + precos acessiveis")
    b("Custo de LLM (IA) (Media/Medio): Cache, fallback para conteudo estatico, batch")
    
    # 21. KPIs
    stories.append(PageBreak())
    h1("21. Metricas (KPIs)")
    h2("Produto")
    b("MAU: 500 (3 meses) / 2.000 (6 meses)")
    b("DAU: 100 (3 meses) / 500 (6 meses)")
    b("DAU/MAU: 20% (3 meses) / 25% (6 meses)")
    b("Retencao D1: 60% | D7: 30% | D30: 15%")
    b("Tempo medio por sessao: 4 min (3m) / 6 min (6m)")
    h2("Engajamento (por casal/semana)")
    b("Perguntas respondidas: 4 de 7")
    b("Desafios completados: 3 de 5")
    b("Entradas de diario: 3")
    b("Streak medio: 7 dias consecutivos")
    h2("Negocio")
    b("Taxa de conversao gratuito &rarr; premium: 5%")
    b("LTV (Lifetime Value): R$60")
    b("MRR (Receita Mensal Recorrente): R$5.000 (1 ano)")
    b("NPS (Net Promoter Score): 50+")
    b("Churn rate: &lt; 5% ao mes")
    h2("Tecnicas")
    b("Uptime: 99.9%")
    b("Tempo de resposta P95: &lt; 500ms")
    b("Lighthouse Performance: &gt; 85")
    b("Lighthouse PWA: &gt; 90")
    
    # 22. Testes A/B
    stories.append(PageBreak())
    h1("22. Plano de Testes A/B")
    h2("Teste 1: Onboarding Flow")
    b("A (controle): Login direto &rarr; dashboard")
    b("B (teste): Login &rarr; tour guiado (3 slides) &rarr; dashboard")
    b("Hipotese: tour guiado aumenta retencao D1 em 15%")
    h2("Teste 2: Notificacoes")
    b("A: Sem notificacoes | B: 1 notif/dia | C: 2 notifs/dia")
    b("Hipotese: 2 notificacoes aumentam DAU em 30%")
    h2("Teste 3: Precificacao Premium")
    b("A: R$9,90/mes, R$79,90/ano | B: R$14,90/mes | C: R$9,90/mes, R$69,90/ano")
    h2("Teste 4: Dashboard Layout")
    b("A: Cards verticais (atual) | B: Grid 2x2 com resumos maiores")
    
    # 23. Acessibilidade
    h1("23. Plano de Acessibilidade")
    p("Target: WCAG 2.1 Nivel AA.")
    b("Adicionar aria-label no botao Gear, lang toggle, e cards clicaveis")
    b("Adicionar role='navigation' na nav inferior e aria-current='page'")
    b("Adicionar role='dialog' no modal de settings")
    b("Garantir contraste minimo 4.5:1 para texto normal")
    b("Suporte a prefers-reduced-motion para animacoes")
    b("Testes: Lighthouse Accessibility, axe DevTools, VoiceOver, NVDA")
    
    # 24. Seguranca
    stories.append(PageBreak())
    h1("24. Plano de Seguranca")
    h2("Implementado")
    b("Senhas com bcrypt (salt + custo 12 rounds)")
    b("JWT com expiracao de 48h, assinado HS256 (sem fallback headers)")
    b("Fallback SHA-256 com upgrade automatico para bcrypt no login")
    b("Sanitizacao de saida com esc() + attrEsc() (XSS em texto e atributos)")
    b("Escapamento de single quote em esc()")
    b("Admin XSS corrigido (11 locais)")
    b("Dirty tracking (beforeunload + markDirty)")
    b("Batch delete paralelo com feedback de progresso")
    b("ORM SQLAlchemy previne SQL Injection")
    b("HTTPS obrigatorio (Render fornece TLS)")
    b("CORS middleware configurado")
    b("Pool de conexao (pool_size=10, max_overflow=20)")
    b("Service Worker cacheia apenas GET requests")
    b("ADMIN_USERS via env var (sem fallback hardcoded)")
    h2("Pendente")
    b("Rate limiting (slowapi ou middleware custom)")
    b("Content Security Policy (CSP strict)")
    b("Validacao de upload (tamanho max 5MB, tipo MIME)")
    b("Helmet-like headers (X-Frame-Options, X-Content-Type-Options)")
    b("Auditoria de dependencias (pip-audit, Dependabot)")
    
    # 25. SEO
    h1("25. Plano de SEO")
    h2("On-Page")
    b("Meta description: 'Still Learning: o app para casais se conectarem todos os dias'")
    b("Open Graph tags (og:title, og:description, og:image)")
    b("Structured Data (Schema.org WebApplication)")
    b("Sitemap.xml e robots.txt")
    b("Alt text descritivo em todas as imagens SVG")
    h2("Palavras-chave Alvo")
    b("app para casais, aplicativo de casal, perguntas para casais")
    b("diario compartilhado casal, desafios para casais")
    b("fortalecer relacionamento, quiz para casais")
    
    # 26. Internacionalizacao
    stories.append(PageBreak())
    h1("26. Plano de Internacionalizacao")
    h2("Status Atual")
    b("Portugues (BR): Completo")
    b("Ingles (US): Completo")
    b("Espanhol: Pendente | Frances: Pendente | Italiano: Pendente | Alemao: Pendente")
    h2("Arquitetura de Traducao")
    p("Dicionario aninhado: L['chave']['pt'] e L['chave']['en']. Funcao t(key, lang) extrai o valor correto. Interface usa getLang() do cookie 'lang'.")
    h2("Roadmap de Localizacao")
    b("Espanhol: Prioridade maxima, 2 dias de esforco")
    b("Frances: Prioridade alta, 2 dias")
    b("Italiano: Prioridade media, 2 dias")
    b("Alemao: Prioridade baixa, 2 dias")
    h2("Deteccao Automatica")
    p("Atual: Cookie 'lang' definido manualmente pelo usuario. Proposto: Deteccao automatica via Accept-Language header + fallback manual.")


def _build_english_content(stories, h1, h2, p, b, code):
    """Build English PDF content."""
    # 1. Architecture
    h1("1. Complete System Architecture")
    p(
        "Stack: Python 3.11+ / FastAPI / SQLAlchemy / SQLite (dev) / PostgreSQL (prod) / "
        "bcrypt + JWT. The system follows a monolithic architecture with lightweight "
        "server-side rendering and JavaScript on the client for SPA-like navigation."
    )
    h2("Layers")
    b("Client: HTML + CSS + Vanilla JS, PWA with Service Worker and Manifest")
    b("Server: FastAPI with Uvicorn, 55 REST endpoints")
    b("Data: SQLAlchemy ORM, 16 tables, automatic migrations")
    b("Auth: bcrypt for passwords, JWT (HS256, 48h) for sessions")
    b("Deploy: Render (free tier), PostgreSQL in production")
    h2("Directory Structure")
    code(
        "project quiz code/\n"
        "  main.py           55 endpoints (1893 lines)\n"
        "  models.py         16 ORM models\n"
        "  database.py       SQLAlchemy Engine + Session\n"
        "  translations.py   i18n PT/EN (431 lines)\n"
        "  static/           CSS, PWA manifest, sw.js, SVG icons\n"
        "  templates/        6 HTML templates\n"
        "  docs/             PDF documentation"
    )
    
    # 2. Navigation Flow
    stories.append(PageBreak())
    h1("2. Navigation Flow")
    p(
        "User logs in at /. If 'couple' profile, redirects to "
        "/still-learning with 3-item bottom nav: Today (smart dashboard), "
        "Us (sub-menus: diary, memories, quiz, challenge), and Gear (settings/language/logout). "
        "If 'quiz' profile, starts a 10-question session: /start &rarr; /quiz &rarr; /result."
    )
    h2("SPA Internal Nav")
    b("Today: Dashboard, Question of the Day, Challenge, Quote, Agenda, To-Dos, Weekly Review")
    b("Us: Diary, Memories, Couple Quiz, Challenge")
    b("Gear: Language (PT/EN), Logout (clear localStorage)")
    h2("Authentication")
    p(
        "Login &rarr; JWT stored in localStorage &rarr; api() sends "
        "Authorization: Bearer &lt;token&gt; on every request &rarr; require_auth() "
        "validates JWT (HS256, 48h) on the backend."
    )
    
    # 3. User Journey
    stories.append(PageBreak())
    h1("3. User Journey")
    h2("First Access")
    b("User accesses still-learning.onrender.com and logs in")
    b("System verifies bcrypt (with legacy SHA-256 fallback)")
    b("If 'couple': generates 48h JWT and redirects to /still-learning with empty dashboard")
    b("If 'quiz': starts new 10-question session or resumes incomplete session")
    h2("Daily Journey")
    b("Morning: Opens Today &rarr; sees greeting, stats, daily quote")
    b("Afternoon: Opens Question of the Day &rarr; answers and waits for partner")
    b("Evening: Opens Us &rarr; Diary &rarr; writes about the day with mood")
    h2("Weekly Journey")
    b("Weekly Review with reflection")
    b("Varied challenges: riddle, intimate question, photo, quote, custom challenge")
    
    # 4. Wireframes
    stories.append(PageBreak())
    h1("4. Text Wireframes")
    p(
        "The interface follows a mobile-first layout with max-width 520px, fixed header with "
        "title and language button, central content in cards with pink shadow, and fixed "
        "bottom nav with 3 items. Colors: pastel pink (#ffb5c2), off-white "
        "(#fdf6f0) and dark gray text (#4a4a4a)."
    )
    h2("Main Screens")
    b("Login: Rounded inputs, SVG heart, gradient button, PT/EN toggle")
    b("Today: Greeting card, stats (pills), question, diary, challenge, quote, agenda")
    b("Us: 2x2 grid of Diary, Memories, Quiz, Challenge cards")
    b("Settings (Modal): Semi-transparent overlay with Language and Logout options")
    b("Question of the Day: Question card, textarea, send button, partner's answer")
    b("Diary: 'Today' section with own entry + timeline of previous days")
    
    # 5. Page Structure
    stories.append(PageBreak())
    h1("5. Page Structure")
    h2("Base Template")
    code(
        '<!DOCTYPE html>\n'
        '<html lang="pt-BR">\n'
        '<head>\n'
        '  <meta charset="UTF-8">\n'
        '  <meta name="viewport" content="width=device-width">\n'
        '  <meta name="theme-color" content="#ffb5c2">\n'
        '  <link rel="manifest" href="/static/manifest.json">\n'
        '  <link rel="stylesheet" href="/static/style.css">\n'
        '</head>\n'
        '<body>\n'
        '  <div class="floating-bg"></div>\n'
        '</body>\n'
        '</html>'
    )
    h2("Templates")
    b("index.html: Login (entry point)")
    b("quiz.html: Interactive quiz (10 questions)")
    b("result.html: Quiz result with personalized message")
    b("retry.html: Retry after completion")
    b("couple.html: Main SPA-like app (~2250 lines)")
    b("admin.html: Admin panel (~1800 lines)")
    
    # 6. Components
    stories.append(PageBreak())
    h1("6. Reusable Components")
    h2("Frontend (Vanilla JS)")
    b("api(path, opts): Fetch wrapper with JWT + headers + auto JSON")
    b("showSection(name): SPA navigation (swaps content + active nav)")
    b("backLink(): Standardized 'Back' button")
    b("esc(s): HTML sanitization (textContent + attribute escaping)")
    b("attrEsc(s): HTML attribute sanitization (quote escaping)")
    b("toggleLang(): PT/EN switch via cookie + reload")
    b("logout(e): Clear localStorage + redirect to /")
    b("toast(msg): Non-intrusive floating toast (3s)")
    b("markDirty(): Marks admin form as unsaved")
    b("initDecorations(): Animated background with floating emojis and stars")
    h2("Backend (Python)")
    b("_render(name, **kwargs): Custom template engine (string replace)")
    b("require_auth(): JWT auth dependency injection (Bearer only)")
    b("check_admin(): Admin credential validation (ADMIN_USERS env var)")
    b("get_partner_name(): Resolves partner name in a couple")
    b("hash_pw() / verify_pw(): bcrypt hash/verify + SHA-256 fallback")
    b("create_jwt() / decode_jwt(): JWT HS256 generation/validation")
    
    # 7. Design System
    stories.append(PageBreak())
    h1("7. Design System")
    h2("CSS Tokens")
    code(
        ":root {\n"
        "  --pink: #ffb5c2;           /* Primary */\n"
        "  --pink-dark: #e88a9a;      /* Hover/Active */\n"
        "  --cream: #fff5f5;           /* Surface */\n"
        "  --text: #4a4a4a;            /* Main text */\n"
        "  --text-light: #b0a0a0;      /* Secondary text */\n"
        "  --bg: #fdf6f0;              /* Background */\n"
        "  --radius-sm: 10px;\n"
        "  --radius-cloud: 18px;\n"
        "  --shadow: 0 4px 20px rgba(255,181,194,0.2);\n"
        "  --ease-bounce: cubic-bezier(0.34,1.56,0.64,1);\n"
        "}"
    )
    h2("Typography")
    b("Titles: 'Press Start 2P', monospace (9px)")
    b("Body: -apple-system, BlinkMacSystemFont, sans-serif (0.9rem)")
    h2("Icons")
    p("Exclusive use of Unicode emoji: 🏠 Today, 💑 Us, ⚙️ Settings, 💕 Love, 💭 Question, 📖 Diary, ✨ Memories, 🎯 Challenge, ❓ Quiz, 📅 Agenda, 📋 To-Dos, 💌 Quote, 🔔 Notification.")
    
    # 8. Visual Guide
    h2("8. Visual Guide")
    p(
        "Pastel pink palette with off-white. Mobile-first layout (max-width: 520px). "
        "Cards with soft shadow, rounded corners (10-18px). "
        "Fixed header with title and language button. Fixed bottom nav with 3 items. "
        "Transitions with cubic-bezier bounce for organic feel."
    )
    h2("Responsiveness")
    b("Desktop (&gt;768px): Centered at 520px")
    b("Mobile (&lt;768px): Full width with 16px padding")
    b("Small mobile (&lt;375px): Font-size reduced 10-15%")
    
    # 9. Database
    stories.append(PageBreak())
    h1("9. Database Structure")
    p("16 tables in SQLAlchemy ORM. SQLite in dev, PostgreSQL in prod.")
    h2("Tables")
    b("profiles: User profiles (quiz or couple)")
    b("login_credentials: Login + password_hash (bcrypt)")
    b("quiz_sessions: Quiz sessions with JSON answers")
    b("login_events: Login audit trail")
    b("couples: User pairs (user1_id, user2_id)")
    b("diary_entries: Diary entries by date")
    b("daily_questions: Daily questions with answers (answer_a, answer_b)")
    b("challenges: Challenges with 5 rotating types")
    b("agenda_events: Agenda events with date/time")
    b("todo_items: Todo items with done status")
    b("weekly_reviews: Weekly reviews (reflection_a, reflection_b)")
    b("quiz_answers: Couple quiz answers (about_self, about_partner)")
    b("quote_refreshes: Quote navigation state")
    b("photos: Base64 photos with caption")
    
    # 10. APIs
    stories.append(PageBreak())
    h1("10. APIs")
    p("Total: 55 documented REST endpoints. Authentication via JWT Bearer exclusively.")
    h2("Auth (1 endpoint)")
    b("POST /api/login: Login with name+password, returns JWT token + user data")
    h2("Quiz (5 endpoints)")
    b("POST /api/start: Start quiz session")
    b("GET /api/question/{id}: Current question")
    b("POST /api/answer/{id}: Submit answer")
    b("GET /api/result/{id}: Complete result with score and message")
    b("POST /api/result/final/{id}: Final romantic response")
    h2("Couple App (28 endpoints)")
    b("Dashboard, Question of the Day, Diary (CRUD)")
    b("Challenges: riddle, intimate question, photo, quote, custom (+ delete)")
    b("Agenda (add + delete), To-Dos (add + toggle + delete), Weekly Review")
    b("Quotes, Couple Quiz, Memories")
    h2("Admin (21 endpoints)")
    b("CRUD for couples, profiles, questions, challenges, photos, diaries, agenda, todos")
    b("Statistics, login history, quiz results")
    b("Couple data reset/delete (with parallel batch delete)")
    
    # 11. AI
    stories.append(PageBreak())
    h1("11. AI Structure")
    p(
        "Current state: No generative AI. All content is predefined: "
        "40 daily questions, 41 themes, 18 challenge suggestions, 30 quotes with trivia. "
        "Rotation is deterministic based on days since couple creation. "
        "The quiz uses random.shuffle() to order 10 of 40+ available questions."
    )
    h2("Future Opportunities")
    b("Personalized questions via LLM (GPT-4 / Claude)")
    b("Sentiment analysis for diary entries (NLP)")
    b("Automatic weekly summary via LLM")
    b("Quote recommendation by mood (embeddings + similarity)")
    b("Adaptive quiz with questions the partner got wrong")
    b("Communication pattern detection")
    
    # 12. Dev Roadmap
    h2("12. Development Roadmap")
    h2("v1.0 - MVP (Current)")
    b("Login bcrypt + JWT, Dashboard, Question of the Day, Diary")
    b("Challenges (5 types: riddle, photo, intimate question, custom, quote)")
    b("Agenda, To-Dos, Weekly Review, Couple Quiz, Quotes, Memories")
    b("Admin (CRUD couples/profiles, statistics)")
    b("PWA (Service Worker + Manifest), i18n PT/EN")
    b("3-item bottom nav (Today/Us/Gear)")
    h2("v2.0 - Connectivity")
    b("Push notifications (Web Push API), Streak tracking")
    b("Dark mode, Automated tests (pytest + Playwright)")
    b("CI/CD (GitHub Actions)")
    h2("v3.0 - AI & Personalization")
    b("Smart suggestions, Diary sentiment analysis")
    b("Automatic weekly summary, Adaptive quiz, Contextual chat")
    h2("v4.0 - Social & Expansion")
    b("Single/friends mode, Shared relationship goals")
    b("Yearly digital book, PDF export, Public API")
    
    # 13. Launch Roadmap
    stories.append(PageBreak())
    h1("13. Launch Roadmap")
    b("Pre-launch: Test full local flow (1 week)")
    b("Alpha: 2-3 couple friends use for 2 weeks (D7 retention > 80%)")
    b("Closed beta: 10-20 couples with structured feedback (NPS > 40)")
    b("Open beta: WhatsApp/Telegram group promotion (100 couples)")
    b("v1.0 Launch: Instagram, Product Hunt (500 active users)")
    b("v2.0: Push + Streaks (2 months post-launch, DAU > 20% MAU)")
    b("v3.0: AI (4 months post-launch, avg time > 8min/day)")
    
    # 14. Growth
    h1("14. Growth Strategy")
    h2("Acquisition Channels")
    b("Word of mouth (couples refer couples) - Free, very high potential")
    b("Instagram - daily question posts with link in bio")
    b("TikTok - couple challenge videos")
    b("WhatsApp/Telegram couple groups")
    b("Partnerships with couple therapists and relationship influencers")
    h2("Viral Cycle")
    p("Couple A uses &rarr; Takes screenshot of a question/dashboard &rarr; Posts on Instagram/TikTok &rarr; Couple B sees it &rarr; Wants to try &rarr; Couple B invites partner &rarr; Cycle repeats.")
    
    # 15. Monetization
    stories.append(PageBreak())
    h1("15. Monetization Strategy")
    h2("Freemium Model")
    b("Free: Basic features (1 challenge/day, 3 photos/day, last 30 memories)")
    b("Monthly Premium (R$9.90): Unlimited challenges, unlimited photos, all memories, sentiment analysis, dark mode")
    b("Annual Premium (R$79.90/year): 33% discount")
    b("Lifetime (R$199.90): Early adopters, launch price")
    h2("Payment Methods")
    b("Stripe (international cards)")
    b("Mercado Pago / Pix (Brazil)")
    b("Apple Pay / Google Pay")
    
    # 16. Retention
    h1("16. Retention Strategy")
    h2("Daily Triggers (Push)")
    b("08:00 - 'Question of the Day available!'")
    b("12:00 - 'Your partner answered the question!'")
    b("18:00 - 'Time for today's challenge!'")
    b("21:00 - 'How about writing in the diary?'")
    h2("Gamification")
    b("Streaks: Consecutive days of use (fire)")
    b("Achievements: '7 days of questions', 'First photo together'")
    b("Couple Levels: Bronze &rarr; Silver &rarr; Gold &rarr; Diamond")
    b("Monthly Badges: 'February Full of Love', 'March of Connection'")
    h2("Churn Prevention")
    b("3 days without login: Email 'We miss you!'")
    b("7 days: Notification with special question waiting")
    b("14 days: 'Want a break? Your data is safe'")
    
    # 17. Checklist
    stories.append(PageBreak())
    h1("17. Improvements Checklist")
    h2("P0 - Critical")
    b("[OK] Migrate from on_event() to lifespan events")
    b("[ ] Add automated tests (pytest for API, Playwright for frontend)")
    b("[ ] Rate limiting (brute-force protection)")
    b("[ ] Photo upload validation (size, MIME type)")
    b("[ ] Pagination on all lists (memories, admin)")
    h2("P1 - High")
    b("[OK] Admin XSS fixed (11 locations)")
    b("[OK] esc() improved (single quote escaping)")
    b("[OK] Dirty tracking in admin (beforeunload + markDirty)")
    b("[OK] Parallel batch delete with progress feedback")
    b("[ ] Dark mode with persistent toggle")
    b("[ ] Streak tracking (consecutive days)")
    b("[ ] Real push notifications (Web Push API)")
    b("[ ] Configurable relationship start date")
    h2("P2 - Medium")
    b("[ ] 'Surprise me' button on dashboard")
    b("[ ] Offline mode (last session cache)")
    b("[ ] Keyboard shortcuts (1-4 for navigation)")
    b("[ ] Export history as PDF")
    
    # 18. Backlog
    h1("18. Prioritized Backlog")
    h2("Sprint 1 - Foundation (Now)")
    b("[OK] Migrate lifespan events, Admin UX, XSS fixes")
    b("[ ] Automated tests (2 days, P0)")
    b("[ ] Rate limiting (4 hours, P0)")
    b("[ ] Upload validation (2 hours, P1)")
    h2("Sprint 2 - Retention")
    b("[ ] Streak tracking (1 day, P1)")
    b("[ ] Day counter (3 hours, P1)")
    b("[ ] Push notifications (3 days, P1)")
    h2("Sprint 3 - Engagement")
    b("[ ] Dark mode (1 day, P1)")
    b("[ ] Pagination (1 day, P2)")
    h2("Sprint 4 - Monetization")
    b("[ ] Free/premium plan system (5 days, P1)")
    b("[ ] Stripe + Mercado Pago (6 days, P1)")
    
    # 19. Evolution
    stories.append(PageBreak())
    h1("19. Product Evolution Plan")
    h2("Phase 1 - Comfort (Months 1-3)")
    p("Focus on stability and retention: finish technical debt, implement streaks + day counter, improve mobile experience (gestures, haptics), collect alpha/beta user feedback.")
    h2("Phase 2 - Connection (Months 3-6)")
    p("Focus on product depth: push notifications, dark mode, more challenge types (video, audio, location), more quiz categories, basic sentiment analysis.")
    h2("Phase 3 - Personalization (Months 6-9)")
    p("Focus on AI and individualization: LLM integration for personalized questions, automatic weekly summary, history-based recommendations, activity suggestions.")
    h2("Phase 4 - Expansion (Months 9-12)")
    p("Focus on growth and monetization: premium plan, friends and individual mode, public API, couple digital book, native app (React Native).")
    
    # 20. Risks
    h1("20. Risk List")
    b("Data loss (Low/Catastrophic): PostgreSQL backup + manual export")
    b("Intimate data leak (Low/Catastrophic): HTTPS, encryption at rest")
    b("Login brute-force (Medium/High): Rate limiting + slow bcrypt by design")
    b("Churn after 7 days (High/High): Better onboarding, notifications, gamification")
    b("Low adoption (High/High): Growth hacking + therapist partnerships")
    b("Competition (Lovewick, Couply) (Medium/Medium): Differentiators: diary + affordable pricing")
    b("LLM cost (AI) (Medium/Medium): Cache, static content fallback, batch processing")
    
    # 21. KPIs
    stories.append(PageBreak())
    h1("21. Metrics (KPIs)")
    h2("Product")
    b("MAU: 500 (3 months) / 2,000 (6 months)")
    b("DAU: 100 (3 months) / 500 (6 months)")
    b("DAU/MAU: 20% (3 months) / 25% (6 months)")
    b("D1 Retention: 60% | D7: 30% | D30: 15%")
    b("Avg session time: 4 min (3m) / 6 min (6m)")
    h2("Engagement (per couple/week)")
    b("Questions answered: 4 of 7")
    b("Challenges completed: 3 of 5")
    b("Diary entries: 3")
    b("Average streak: 7 consecutive days")
    h2("Business")
    b("Free &rarr; premium conversion rate: 5%")
    b("LTV (Lifetime Value): R$60")
    b("MRR (Monthly Recurring Revenue): R$5,000 (1 year)")
    b("NPS (Net Promoter Score): 50+")
    b("Monthly churn rate: &lt; 5%")
    h2("Technical")
    b("Uptime: 99.9%")
    b("P95 response time: &lt; 500ms")
    b("Lighthouse Performance: &gt; 85")
    b("Lighthouse PWA: &gt; 90")
    
    # 22. A/B Tests
    stories.append(PageBreak())
    h1("22. A/B Testing Plan")
    h2("Test 1: Onboarding Flow")
    b("A (control): Direct login &rarr; dashboard")
    b("B (test): Login &rarr; guided tour (3 slides) &rarr; dashboard")
    b("Hypothesis: guided tour increases D1 retention by 15%")
    h2("Test 2: Notifications")
    b("A: No notifications | B: 1 notif/day | C: 2 notifs/day")
    b("Hypothesis: 2 notifications increase DAU by 30%")
    h2("Test 3: Premium Pricing")
    b("A: R$9.90/mo, R$79.90/yr | B: R$14.90/mo | C: R$9.90/mo, R$69.90/yr")
    h2("Test 4: Dashboard Layout")
    b("A: Vertical cards (current) | B: 2x2 grid with larger summaries")
    
    # 23. Accessibility
    h1("23. Accessibility Plan")
    p("Target: WCAG 2.1 Level AA.")
    b("Add aria-label to Gear button, lang toggle, and clickable cards")
    b("Add role='navigation' to bottom nav and aria-current='page'")
    b("Add role='dialog' to settings modal")
    b("Ensure minimum contrast 4.5:1 for normal text")
    b("Support prefers-reduced-motion for animations")
    b("Tests: Lighthouse Accessibility, axe DevTools, VoiceOver, NVDA")
    
    # 24. Security
    stories.append(PageBreak())
    h1("24. Security Plan")
    h2("Implemented")
    b("bcrypt passwords (salt + 12 round cost)")
    b("JWT with 48h expiration, HS256 signing (no legacy header fallback)")
    b("SHA-256 fallback with automatic bcrypt upgrade on login")
    b("Output sanitization with esc() + attrEsc() (XSS prevention in text and attributes)")
    b("Single quote escaping in esc()")
    b("Admin XSS fixed (11 locations)")
    b("Dirty tracking (beforeunload + markDirty)")
    b("Parallel batch delete with progress feedback")
    b("SQLAlchemy ORM prevents SQL injection")
    b("Mandatory HTTPS (Render provides TLS)")
    b("CORS middleware configured")
    b("Connection pool (pool_size=10, max_overflow=20)")
    b("Service Worker caches only GET requests")
    b("ADMIN_USERS via env var (no hardcoded fallback)")
    h2("Pending")
    b("Rate limiting (slowapi or custom middleware)")
    b("Content Security Policy (strict CSP)")
    b("Upload validation (5MB max, MIME type)")
    b("Helmet-like headers (X-Frame-Options, X-Content-Type-Options)")
    b("Dependency auditing (pip-audit, Dependabot)")
    
    # 25. SEO
    h1("25. SEO Plan")
    h2("On-Page")
    b("Meta description: 'Still Learning: the app for couples to connect every day'")
    b("Open Graph tags (og:title, og:description, og:image)")
    b("Structured Data (Schema.org WebApplication)")
    b("Sitemap.xml and robots.txt")
    b("Descriptive alt text on all SVG images")
    h2("Target Keywords")
    b("app for couples, couple app, questions for couples")
    b("shared couple diary, challenges for couples")
    b("strengthen relationship, couple quiz")
    
    # 26. Internationalization
    stories.append(PageBreak())
    h1("26. Internationalization Plan")
    h2("Current Status")
    b("Portuguese (BR): Complete")
    b("English (US): Complete")
    b("Spanish: Pending | French: Pending | Italian: Pending | German: Pending")
    h2("Translation Architecture")
    p("Nested dictionary: L['key']['pt'] and L['key']['en']. t(key, lang) function extracts the correct value. Interface uses getLang() from cookie 'lang'.")
    h2("Localization Roadmap")
    b("Spanish: Maximum priority, 2 days effort")
    b("French: High priority, 2 days")
    b("Italian: Medium priority, 2 days")
    b("German: Low priority, 2 days")
    h2("Auto-Detection")
    p("Current: 'lang' cookie set manually by user. Proposed: Auto-detection via Accept-Language header + manual fallback.")


def generate_with_fpdf(language="pt"):
    """Fallback: generate PDF using fpdf2."""
    from fpdf import FPDF
    
    is_en = language == "en"
    filename = "Still_Learning_Documentation.pdf" if is_en else "Still_Learning_Documentacao.pdf"
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    title = "Complete Product Documentation" if is_en else "Documentacao do Produto"
    version = "Version 2.1 | July 2026" if is_en else "Versao 2.1 | Julho 2026"
    arch_text = (
        "Stack: Python 3.11+ / FastAPI / SQLAlchemy / SQLite+PostgreSQL / bcrypt+JWT. "
        "Monolithic system with 55 REST endpoints."
        if is_en else
        "Stack: Python 3.11+ / FastAPI / SQLAlchemy / SQLite+PostgreSQL / bcrypt+JWT. "
        "Sistema monolitico com 55 endpoints REST."
    )
    
    pdf = FPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    def safe(text):
        """Remove non-latin1 characters."""
        result = []
        for ch in text:
            try:
                ch.encode("latin-1")
                result.append(ch)
            except UnicodeEncodeError:
                try:
                    import unicodedata
                    base = unicodedata.normalize("NFKD", ch).encode("ascii", "ignore").decode("ascii")
                    if base:
                        result.append(base)
                    else:
                        result.append("?")
                except:
                    result.append("?")
        return "".join(result)
    
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, safe("Still Learning"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, safe(title), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5, safe(version))
    
    pdf.set_font("Helvetica", "B", 14)
    section_title = "1. Architecture" if is_en else "1. Arquitetura"
    pdf.cell(0, 10, safe(section_title), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5, safe(arch_text))
    
    pdf.output(output_path)
    print(f"PDF generated (fpdf fallback): {output_path}")
    print(f"Pages: {pdf.page_no()}")
    return True


if __name__ == "__main__":
    import sys
    lang = "en" if "--en" in sys.argv else "pt"
    if HAS_REPORTLAB:
        print(f"Using reportlab for PDF generation ({'English' if lang == 'en' else 'Portuguese'})...")
        generate_with_reportlab(lang)
    else:
        print("reportlab not available, installing...")
        import subprocess
        subprocess.run(["pip3", "install", "reportlab"], check=True)
        print("Installed reportlab. Running...")
        generate_with_reportlab(lang)
