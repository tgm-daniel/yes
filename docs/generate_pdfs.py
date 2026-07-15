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


def generate_with_reportlab():
    """Generate PDF using reportlab (better unicode/emoji support)."""
    output_path = os.path.join(OUTPUT_DIR, "Still_Learning_Documentacao.pdf")
    
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
        stories.append(Paragraph("Documentacao Completa do Produto", subtitle_style))
        stories.append(Spacer(1, 10*mm))
        stories.append(Paragraph(
            "Versao 2.0 &nbsp;|&nbsp; Julho 2026<br/>"
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
    
    # 1. Arquitetura
    h1("1. Arquitetura Completa do Sistema")
    p(
        "Stack: Python 3.11+ / FastAPI / SQLAlchemy / SQLite (dev) / PostgreSQL (prod) / "
        "bcrypt + JWT. O sistema segue arquitetura monolitica com renderizacao server-side "
        "leve e JavaScript no cliente para navegacao SPA-like."
    )
    h2("Camadas")
    b("Cliente: HTML + CSS + Vanilla JS, PWA com Service Worker e Manifest")
    b("Servidor: FastAPI com Uvicorn, 60 endpoints REST")
    b("Dados: SQLAlchemy ORM, 16 tabelas, migracoes automaticas")
    b("Autenticacao: bcrypt para senhas, JWT (HS256, 48h) para sessoes")
    b("Deploy: Render (free tier), PostgreSQL em producao")
    h2("Estrutura de Diretorios")
    code(
        "project quiz code/\n"
        "  main.py           60 endpoints (1868 linhas)\n"
        "  models.py         16 modelos ORM\n"
        "  database.py       Engine + Session SQLAlchemy\n"
        "  translations.py   i18n PT/EN (449 linhas)\n"
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
        "no backend valida JWT com fallback para headers X-Couple-Id / X-User-Name "
        "(backward compatibility)."
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
    b("esc(s): Sanitizacao de HTML (textContent)")
    b("toggleLang(): Troca PT/EN com cookie + recarrega")
    b("logout(e): Clean do localStorage + redirect para /")
    b("toast(msg): Toast flutuante nao-intrusivo (3s)")
    b("initDecorations(): Fundo animado com emojis flutuantes + estrelas")
    h2("Backend (Python)")
    b("_render(name, **kwargs): Template engine caseira (string replace)")
    b("require_auth(): Dependency Injection de autenticacao JWT")
    b("check_admin(): Validacao de credenciais admin")
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
    p("Total: 60 endpoints REST documentados. Autenticacao via JWT (Bearer) com fallback para headers X-Couple-Id / X-User-Name.")
    h2("Autenticacao (1 endpoint)")
    b("POST /api/login: Login com name+password, retorna JWT token + dados do usuario")
    h2("Quiz (5 endpoints)")
    b("POST /api/start: Iniciar sessao de quiz")
    b("GET /api/question/{id}: Pergunta atual")
    b("POST /api/answer/{id}: Submeter resposta")
    b("GET /api/result/{id}: Resultado completo com score e mensagem")
    b("POST /api/result/final/{id}: Resposta final (romantica)")
    h2("Couple App (26 endpoints)")
    b("Dashboard, Pergunta do Dia, Diario (CRUD)")
    b("Desafios: enigma, pergunta intima, foto, citacao, desafio personalizado")
    b("Agenda, To-Dos, Review Semanal, Citacoes, Quiz do Casal, Memorias")
    h2("Admin (21 endpoints)")
    b("CRUD de casais, perfis, perguntas, desafios, fotos, diarios, agenda, todos")
    b("Estatisticas, historico de login, resultados de quiz")
    b("Reset/delecao de dados de casal")
    
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
    b("Migrar de on_event() para lifespan events (deprecation warning)")
    b("Adicionar testes automatizados (pytest para API, Playwright para frontend)")
    b("Rate limiting (protecao contra brute-force)")
    b("Validacao de upload de foto (tamanho, tipo MIME)")
    b("Paginação em todas as listas (memorias, admin)")
    h2("P1 - Alta")
    b("Modo escuro com toggle persistente")
    b("Streak tracking (dias consecutivos de uso)")
    b("Notificacoes push reais (Web Push API)")
    b("Data de inicio do relacionamento configuravel")
    b("Contador de dias juntos no dashboard")
    b("Feedback tatil (haptics) em interacoes mobile")
    h2("P2 - Media")
    b("Botao 'surprise me' no dashboard")
    b("Modo offline (cache da ultima sessao)")
    b("Atalhos de teclado (1-4 para navegacao)")
    b("Exportar historico como PDF")
    b("Compartilhar conquistas em redes sociais")
    
    # 18. Backlog
    h1("18. Backlog Priorizado")
    h2("Sprint 1 - Fundacao (Agora)")
    b("Testes automatizados (2 dias, P0)")
    b("Rate limiting (4 horas, P0)")
    b("Validacao de upload (2 horas, P1)")
    h2("Sprint 2 - Retencao")
    b("Streak tracking (1 dia, P1)")
    b("Contador de dias (3 horas, P1)")
    b("Notificacoes push (3 dias, P1)")
    h2("Sprint 3 - Engajamento")
    b("Modo escuro (1 dia, P1)")
    b("Paginação (1 dia, P2)")
    h2("Sprint 4 - Monetizacao")
    b("Sistema de planos gratuito/premium (5 dias, P1)")
    b("Stripe + Mercado Pago (6 dias, P1)")
    
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
    b("JWT com expiracao de 48h, assinado HS256")
    b("Fallback SHA-256 com upgrade automatico para bcrypt no login")
    b("Sanitizacao de saida com textContent (previne XSS)")
    b("ORM SQLAlchemy previne SQL Injection")
    b("HTTPS obrigatorio (Render fornece TLS)")
    h2("Pendente")
    b("Rate limiting (slowapi ou middleware custom)")
    b("CSRF Protection (tokens CSRF em mutacoes)")
    b("Content Security Policy (CSP strict)")
    b("Validacao de upload (tamanho max 300KB, tipo MIME)")
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
    
    # Build PDF
    doc.build(stories)
    print(f"PDF generated: {output_path}")
    print(f"Total pages: {doc.page}")
    return True


def generate_with_fpdf():
    """Fallback: generate PDF using fpdf2."""
    from fpdf import FPDF
    
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
    pdf.cell(0, 8, safe("Documentacao do Produto"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5, safe("Versao 2.0 | Julho 2026"))
    
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, safe("1. Arquitetura"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5, safe("Stack: Python 3.11+ / FastAPI / SQLAlchemy / SQLite+PostgreSQL / bcrypt+JWT. Sistema monolitico com 60 endpoints REST."))
    
    output_path = os.path.join(OUTPUT_DIR, "Still_Learning_Documentacao.pdf")
    pdf.output(output_path)
    print(f"PDF generated (fpdf fallback): {output_path}")
    print(f"Pages: {pdf.page_no()}")
    return True


if __name__ == "__main__":
    if HAS_REPORTLAB:
        print("Using reportlab for PDF generation...")
        generate_with_reportlab()
    else:
        print("reportlab not available, installing...")
        import subprocess
        subprocess.run(["pip3", "install", "reportlab"], check=True)
        print("Installed reportlab. Running...")
        generate_with_reportlab()
