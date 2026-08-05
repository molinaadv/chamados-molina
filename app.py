
from streamlit_autorefresh import st_autorefresh
import streamlit as st
import pandas as pd
from supabase import create_client, Client
import plotly.express as px
from datetime import datetime, timezone, timedelta
import bcrypt
import requests

# =========================
# CONFIGURAÇÃO
# =========================

st.set_page_config(
    page_title="V360 LegalOne Molina",
    layout="wide",
    page_icon="⚖️",
    initial_sidebar_state="expanded"
)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

GOOGLE_CHAT_WEBHOOK = st.secrets.get("GOOGLE_CHAT_WEBHOOK", "")
BOT_NOTIFY_URL = st.secrets.get("BOT_NOTIFY_URL", "")
BOT_API_SECRET = st.secrets.get("BOT_API_SECRET", "")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Unidades disponíveis no sistema de Chamados LegalOne.
# "LegalOne" é mantida como opção por compatibilidade com cadastros antigos.
UNIDADES_MOLINA = [
    "LegalOne",
    "Atrium",
    "Autazes",
    "Barreirinha",
    "Boa Vista",
    "Boa Vista do Ramos",
    "Caapiranga",
    "Cachoeirinha",
    "Canutama",
    "Careiro",
    "Cidade Nova",
    "Compensa",
    "Cuiabá",
    "Humaitá",
    "Iranduba",
    "Itacoatiara",
    "Itapiranga",
    "Lábrea",
    "Manacapuru",
    "Manaquiri",
    "Maués",
    "Novo Airão",
    "Online",
    "Parintins",
    "Porto Velho - Unid 1",
    "Porto Velho - Unid 2",
    "Presidente Figueiredo",
    "Rio Preto da Eva",
    "São José",
    "Urucurituba"
]


# =========================
# CSS V2
# =========================

st.markdown("""
<style>
:root {
    --azul:#061B3A;
    --azul2:#0B3F8A;
    --navy:#071A33;
    --bg:#F3F6FB;
    --card:#ffffff;
    --muted:#64748b;
    --text:#0f172a;
    --border:#e5e7eb;
    --green:#16a34a;
    --red:#dc2626;
    --orange:#f97316;
    --purple:#7c3aed;
    --blue:#2563eb;
}

html, body, .stApp {
    background:var(--bg) !important;
    color:var(--text) !important;
}

.block-container {
    padding-top: 2.4rem !important;
    padding-bottom: 2rem;
    max-width: 100%;
}

[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#04162F 0%,#062B5F 58%,#04162F 100%) !important;
    border-right:0 !important;
    box-shadow: 8px 0 26px rgba(2, 8, 23, .18);
}

[data-testid="stSidebar"] * {
    color:white !important;
}

.sidebar-logo {
    font-size:30px;
    font-weight:900;
    letter-spacing:.5px;
    margin:18px 0 20px 0;
    display:flex;
    align-items:center;
    gap:10px;
}

.sidebar-user {
    background:rgba(255,255,255,.12);
    padding:16px;
    border-radius:18px;
    margin:10px 0 18px 0;
}

.sidebar-user-name {
    font-weight:900;
    font-size:17px;
}

.sidebar-user-role {
    font-size:13px;
    opacity:.8;
}

.main-title {
    font-size:36px;
    font-weight:950;
    color:#0f172a;
    margin-bottom:0;
}

.main-subtitle {
    font-size:15px;
    color:#64748b;
    margin-bottom:20px;
}

.hero {
    background:linear-gradient(135deg,#071a33,#073763);
    border-radius:28px;
    padding:28px 32px;
    color:white;
    box-shadow:0 12px 35px rgba(7,26,51,.22);
    margin-bottom:22px;
}

.hero-title {
    font-size:40px;
    font-weight:950;
}

.hero-subtitle {
    font-size:17px;
    opacity:.9;
    margin-top:6px;
}

.kpi-card {
    background:white;
    border:1px solid #e5e7eb;
    border-radius:22px;
    padding:22px;
    box-shadow:0 12px 28px rgba(15,23,42,.08);
    min-height:135px;
    transition: all .2s ease;
}

.kpi-icon {
    width:46px;
    height:46px;
    border-radius:15px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:24px;
    margin-bottom:12px;
}

.kpi-label {
    color:#64748b;
    font-size:14px;
    font-weight:800;
}

.kpi-number {
    font-size:42px;
    font-weight:950;
    color:#0f172a;
    line-height:1;
}

.kpi-foot {
    font-size:13px;
    font-weight:800;
    margin-top:8px;
}

.chart-card {
    background:white;
    border:1px solid #e5e7eb;
    border-radius:22px;
    padding:18px;
    box-shadow:0 12px 28px rgba(15,23,42,.07);
    margin-bottom:18px;
}

.section-title {
    font-size:22px;
    font-weight:950;
    margin-bottom:12px;
    color:#0f172a;
}

.ticket-list {
    background:white;
    border:1px solid #e5e7eb;
    border-radius:22px;
    padding:14px;
    box-shadow:0 8px 22px rgba(15,23,42,.07);
}

.ticket-item {
    border:1px solid #e5e7eb;
    border-radius:18px;
    padding:14px;
    margin-bottom:12px;
    background:#ffffff;
}

.ticket-title {
    font-size:19px;
    font-weight:950;
    color:#0f172a;
}

.badge {
    padding:5px 10px;
    border-radius:999px;
    font-size:12px;
    font-weight:900;
    color:white;
    float:right;
}

.badge-baixa {background:#16a34a;}
.badge-media {background:#7c3aed;}
.badge-alta {background:#f97316;}
.badge-urgente {background:#dc2626;}

.status-chip {
    padding:6px 12px;
    border-radius:999px;
    font-size:13px;
    font-weight:900;
    background:#dcfce7;
    color:#166534;
}

.detail-card {
    background:white;
    border:1px solid #e5e7eb;
    border-radius:24px;
    padding:24px;
    box-shadow:0 8px 22px rgba(15,23,42,.07);
}

.desc-box {
    background:#f8fafc;
    border:1px solid #e5e7eb;
    border-radius:16px;
    padding:16px;
    color:#334155;
    margin:14px 0;
}

.timeline-item {
    border-left:4px solid #2563eb;
    padding-left:14px;
    margin:14px 0;
    color:#334155;
}

.login-wrap {
    min-height:88vh;
    display:flex;
    align-items:center;
    justify-content:center;
    background:linear-gradient(135deg,#071a33,#073763);
    border-radius:28px;
}

.login-card {
    width:390px;
    background:white;
    padding:28px;
    border-radius:24px;
    box-shadow:0 18px 45px rgba(0,0,0,.25);
}

.login-logo {
    font-size:38px;
    font-weight:950;
    color:#073763;
    text-align:center;
    margin-bottom:18px;
}

.tv-bg {
    background:#061224;
    padding:18px;
    border-radius:20px;
}

.tv-header {
    background:linear-gradient(90deg,#071a33,#0b5394);
    color:white;
    padding:22px;
    border-radius:20px;
    margin-bottom:18px;
    display:flex;
    justify-content:space-between;
    align-items:center;
}

.tv-title {
    font-size:32px;
    font-weight:950;
}

.tv-live {
    color:#ef4444;
    font-weight:900;
}

.tv-card {
    background:#0b1f3a;
    border:1px solid rgba(255,255,255,.08);
    border-radius:18px;
    padding:22px;
    color:white;
    text-align:center;
}

.tv-number {
    font-size:54px;
    font-weight:950;
}

.tv-label {
    font-size:17px;
    font-weight:900;
    opacity:.9;
}

.tv-table {
    background:#0b1f3a;
    border-radius:18px;
    padding:16px;
    color:white;
    margin-top:18px;
}

.stButton > button {
    border-radius:14px !important;
    font-weight:900 !important;
    border:1px solid #d1d5db !important;
}

div[data-testid="stMetric"] {
    background:white;
    padding:16px;
    border-radius:18px;
    border:1px solid #e5e7eb;
}

.online-box {
    background:white;
    border:1px solid #e5e7eb;
    border-radius:16px;
    padding:12px 16px;
    color:#0f172a;
    box-shadow:0 8px 20px rgba(15,23,42,.06);
}
.online-dot {
    display:inline-block;
    width:10px;
    height:10px;
    background:#16a34a;
    border-radius:50%;
    margin-right:7px;
}
.premium-kpi {
    background:#fff;
    border:1px solid #e5e7eb;
    border-radius:22px;
    padding:22px;
    box-shadow:0 10px 28px rgba(15,23,42,.08);
    min-height:138px;
}
.premium-icon {
    width:44px;
    height:44px;
    border-radius:16px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:23px;
    margin-bottom:10px;
}
.kpi-blue {background:#dbeafe;}
.kpi-orange {background:#ffedd5;}
.kpi-purple {background:#ede9fe;}
.kpi-green {background:#dcfce7;}
.kpi-red {background:#fee2e2;}
.premium-label {
    font-size:13px;
    font-weight:900;
    color:#475569;
}
.premium-number {
    font-size:38px;
    font-weight:950;
    color:#020617;
    line-height:1.05;
}
.premium-foot {
    font-size:13px;
    font-weight:900;
    color:#2563eb;
    margin-top:8px;
}
.premium-chart {
    min-height:auto;
    padding-bottom:10px;
}
.dark-tv-box {
    background:linear-gradient(180deg,#071A33,#0B274D);
    border-radius:22px;
    padding:18px;
    box-shadow:0 16px 35px rgba(2,8,23,.18);
    color:white !important;
}
.dark-tv-box * {
    color:white !important;
}
.dark-tv-title {
    font-size:20px;
    font-weight:950;
}
.live-badge {
    background:#dc2626;
    color:white;
    border-radius:999px;
    padding:5px 10px;
    font-size:12px;
    margin-left:10px;
}
.dark-tv-time {
    text-align:right;
    font-size:18px;
    font-weight:900;
}
.tv-tab {
    background:rgba(255,255,255,.08);
    border-radius:12px;
    text-align:center;
    padding:10px;
    font-weight:900;
    font-size:13px;
    margin-bottom:12px;
}
.tv-tab.active {
    background:#2563eb;
}
.right-panel {
    background:white;
    border:1px solid #e5e7eb;
    border-radius:26px;
    padding:22px;
    box-shadow:0 12px 30px rgba(15,23,42,.08);
    position:sticky;
    top:20px;
}
.right-title {
    font-size:30px;
    font-weight:950;
    color:#0f172a;
}
.right-subtitle {
    color:#64748b;
    font-size:14px;
    margin-bottom:18px;
}
.selected-ticket {
    border:1px solid #dbeafe;
    border-radius:20px;
    padding:18px;
    background:#f8fbff;
    margin-bottom:16px;
}
.selected-header {
    display:flex;
    justify-content:space-between;
    align-items:center;
}
.selected-protocol {
    font-size:26px;
    font-weight:950;
    color:#0f172a;
}
.selected-meta {
    margin-top:12px;
    color:#475569;
    font-weight:800;
    font-size:13px;
}
.selected-desc {
    background:#eef6ff;
    border-radius:14px;
    padding:14px;
    margin-top:14px;
    color:#0f172a;
    font-size:14px;
}
[data-testid="stSidebar"] .stRadio label {
    background:rgba(255,255,255,.08);
    border-radius:12px;
    padding:8px 10px;
    margin-bottom:5px;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background:rgba(37,99,235,.45);
}


.card-title-only {
    background:white;
    border:1px solid #e5e7eb;
    border-bottom:0;
    border-radius:22px 22px 0 0;
    padding:20px 22px 8px 22px;
    margin-bottom:0;
    box-shadow:0 12px 28px rgba(15,23,42,.07);
}
[data-testid="stPlotlyChart"] {
    background:white;
    border:1px solid #e5e7eb;
    border-top:0;
    border-radius:0 0 22px 22px;
    padding:8px 12px 14px 12px;
    box-shadow:0 12px 28px rgba(15,23,42,.07);
    margin-bottom:18px;
}


/* V4.2 fixes */
[data-testid="stSidebar"] .stButton > button {
    background:rgba(255,255,255,.12) !important;
    color:white !important;
    border:1px solid rgba(255,255,255,.45) !important;
}
[data-testid="stSidebar"] .stButton > button * {
    color:white !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background:rgba(37,99,235,.55) !important;
    color:white !important;
}
[data-testid="stSidebar"] {
    min-width: 285px !important;
}
.main-title {
    padding-top: 8px;
}
.right-panel {
    top:72px !important;
}
[data-testid="stHeader"] {
    background:rgba(255,255,255,.92) !important;
}


.dark-tv-box .stButton > button {
    background:rgba(255,255,255,.10) !important;
    color:white !important;
    border:1px solid rgba(255,255,255,.18) !important;
    border-radius:12px !important;
    font-weight:950 !important;
    padding:10px 8px !important;
}
.dark-tv-box .stButton > button:hover {
    background:#2563eb !important;
    color:white !important;
    border-color:#2563eb !important;
}
.dark-tv-box .stButton > button * {
    color:white !important;
}
.filtro-ativo {
    background:rgba(37,99,235,.22);
    border:1px solid rgba(255,255,255,.12);
    border-radius:12px;
    padding:10px 14px;
    margin:10px 0 12px 0;
    font-weight:900;
    color:white !important;
}

</style>
""", unsafe_allow_html=True)

# Visual do menu em formato de botões + componentes do menu Insights
st.markdown("""
<style>
/* Menu lateral em formato de botões */
[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 2px !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label {
    width: 100% !important;
    background: rgba(255,255,255,.08) !important;
    border: 1px solid rgba(255,255,255,.04) !important;
    border-radius: 12px !important;
    padding: 11px 13px !important;
    margin: 3px 0 !important;
    transition: all .18s ease !important;
    cursor: pointer !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background: rgba(37,99,235,.42) !important;
    transform: translateX(2px);
}

[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: #2563eb !important;
    border-color: rgba(255,255,255,.20) !important;
    box-shadow: 0 8px 18px rgba(2,8,23,.22) !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label p {
    font-size: 14px !important;
    font-weight: 850 !important;
    margin: 0 !important;
    color: white !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] > label {
    font-size: 12px !important;
    font-weight: 800 !important;
    text-transform: uppercase;
    letter-spacing: .5px;
    opacity: .75;
    margin: 4px 4px 8px 4px !important;
}

/* Insights */
.insight-summary {
    background: linear-gradient(135deg,#071a33,#0b3f8a);
    border-radius: 24px;
    padding: 24px 26px;
    color: white !important;
    box-shadow: 0 18px 40px rgba(7,26,51,.22);
    margin: 16px 0 20px 0;
}
.insight-summary * { color: white !important; }
.insight-summary-title {
    font-size: 24px;
    font-weight: 950;
    margin-bottom: 10px;
}
.insight-summary-text {
    color: #e8f0ff !important;
    line-height: 1.65;
    font-size: 15px;
}
.insight-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 20px;
    padding: 18px;
    box-shadow: 0 12px 28px rgba(15,23,42,.08);
    min-height: 152px;
}
.insight-card-icon {
    width: 44px;
    height: 44px;
    border-radius: 14px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:22px;
    margin-bottom:10px;
}
.insight-card-label {
    color:#64748b;
    font-size:13px;
    font-weight:850;
}
.insight-card-main {
    color:#0f172a;
    font-size:24px;
    font-weight:950;
    margin-top:6px;
}
.insight-card-foot {
    color:#64748b;
    font-size:12px;
    line-height:1.45;
    margin-top:8px;
}
.insight-panel {
    background:white;
    border:1px solid #e5e7eb;
    border-radius:22px;
    padding:20px;
    box-shadow:0 12px 28px rgba(15,23,42,.07);
    margin-bottom:18px;
}
.insight-panel-title {
    color:#0f172a;
    font-size:21px;
    font-weight:950;
    margin-bottom:4px;
}
.insight-panel-subtitle {
    color:#64748b;
    font-size:13px;
    margin-bottom:15px;
}
.insight-attention {
    border:1px solid #fed7aa;
    background:linear-gradient(180deg,#fff7ed,#ffffff);
    border-radius:18px;
    padding:18px;
}
.insight-attention-title {
    color:#9a3412;
    font-size:13px;
    font-weight:900;
}
.insight-attention-main {
    color:#c2410c;
    font-size:37px;
    font-weight:950;
    margin:7px 0;
}
.insight-recommendation {
    display:flex;
    gap:12px;
    align-items:flex-start;
    border:1px solid #e5e7eb;
    background:#fbfcfe;
    border-radius:15px;
    padding:14px;
    margin-bottom:10px;
}
.insight-recommendation-number {
    width:34px;
    height:34px;
    flex:0 0 34px;
    border-radius:11px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#dbeafe;
    color:#1d4ed8;
    font-weight:950;
}
.insight-recommendation-text {
    color:#334155;
    font-size:13px;
    line-height:1.45;
}
.insight-recommendation-text b {
    color:#0f172a;
    display:block;
    margin-bottom:3px;
}
</style>
""", unsafe_allow_html=True)


# =========================
# FUNÇÕES BASE
# =========================

def opcoes_unidade(unidade_atual=None):
    """Retorna as unidades válidas sem perder valores antigos já cadastrados."""
    opcoes = list(UNIDADES_MOLINA)

    if unidade_atual is not None and not pd.isna(unidade_atual):
        unidade_atual = str(unidade_atual).strip()
        if unidade_atual and unidade_atual not in opcoes:
            opcoes.append(unidade_atual)

    return opcoes


def indice_unidade(opcoes, unidade_atual=None):
    unidade_atual = str(unidade_atual or "LegalOne").strip() or "LegalOne"
    return opcoes.index(unidade_atual) if unidade_atual in opcoes else 0


def gerar_hash_senha(senha):
    return bcrypt.hashpw(
        senha.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verificar_senha(senha_digitada, senha_salva):
    if senha_salva and str(senha_salva).startswith("$2b$"):
        return bcrypt.checkpw(
            senha_digitada.encode("utf-8"),
            senha_salva.encode("utf-8")
        )
    return senha_digitada == senha_salva


def fazer_login(email, senha):
    response = supabase.table("usuarios_legalone") \
        .select("*") \
        .eq("email", email) \
        .execute()

    if response.data:
        usuario = response.data[0]
        senha_salva = usuario.get("senha", "")

        if verificar_senha(senha, senha_salva):
            return usuario

    return None


def enviar_google_chat(mensagem):
    """
    Envia uma mensagem simples para o espaço do Google Chat configurado
    em GOOGLE_CHAT_WEBHOOK nos Secrets do Streamlit.
    """
    if not GOOGLE_CHAT_WEBHOOK:
        return False, "GOOGLE_CHAT_WEBHOOK não configurado."

    try:
        resposta = requests.post(
            GOOGLE_CHAT_WEBHOOK,
            json={"text": mensagem},
            timeout=10
        )

        if resposta.status_code in [200, 201]:
            return True, "Mensagem enviada ao Google Chat."

        return False, f"{resposta.status_code} - {resposta.text}"

    except Exception as e:
        return False, str(e)


def notificar_conclusao_bot(chamado, responsavel, observacao):
    """
    Aciona o bot do Google Chat para notificar o solicitante no chat direto.
    Importante: o endpoint /notificar-conclusao do bot precisa usar email_solicitante
    para localizar a conversa privada do usuário.
    """
    if not BOT_NOTIFY_URL:
        return False, "BOT_NOTIFY_URL não configurado no Streamlit Secrets."

    if not BOT_API_SECRET:
        return False, "BOT_API_SECRET não configurado no Streamlit Secrets."

    try:
        payload = {
            "protocolo": chamado.get("protocolo", ""),
            "status": "Finalizado",
            "concluido_por": responsavel,
            "responsavel": responsavel,
            "observacao": observacao or "",
            "solicitante": chamado.get("solicitante", ""),
            "email_solicitante": chamado.get("email_solicitante", ""),
            "unidade": chamado.get("unidade", ""),
            "categoria": chamado.get("categoria", ""),
            "descricao": chamado.get("descricao", ""),
            "destino": "solicitante"
        }

        resp = requests.post(
            BOT_NOTIFY_URL,
            headers={
                "Content-Type": "application/json",
                "X-API-KEY": BOT_API_SECRET
            },
            json=payload,
            timeout=30
        )

        if resp.status_code in [200, 201]:
            return True, resp.text

        return False, f"{resp.status_code} - {resp.text}"

    except Exception as e:
        return False, str(e)


def carregar_chamados():
    response = supabase.table("chamados_legalone") \
        .select("*") \
        .eq("setor", "LegalOne") \
        .order("criado_em", desc=True) \
        .execute()

    return pd.DataFrame(response.data or [])


def aplicar_permissao_chamados(df, usuario):
    perfil = usuario.get("perfil")
    email = usuario.get("email")
    setor = usuario.get("setor")

    if df.empty:
        return df

    if perfil in ["Administrador", "Diretoria", "TV"]:
        return df

    if perfil == "Gestor":
        return df[df["setor"] == setor]

    if perfil == "Colaborador":
        return df[df["email_solicitante"] == email]

    return df.iloc[0:0]


def calcular_sla(row):
    prioridade = row.get("prioridade", "Média")
    status = row.get("status", "Aberto")
    criado_em = row.get("criado_em")

    if status in ["Finalizado", "Cancelado"]:
        return "Concluído"

    if pd.isna(criado_em):
        return "Sem data"

    prazos = {
        "Urgente": 1,
        "Alta": 4,
        "Média": 24,
        "Baixa": 72
    }

    horas_prazo = prazos.get(prioridade, 24)
    prazo_final = criado_em + timedelta(hours=horas_prazo)
    agora = datetime.now(timezone.utc)

    if prazo_final < agora:
        return "Atrasado"

    return "No prazo"


def criar_protocolo(chamado_id):
    return f"LO-{chamado_id:05d}"


def prioridade_badge(prioridade):
    p = str(prioridade or "").lower()
    if "urgente" in p:
        return "badge-urgente"
    if "alta" in p:
        return "badge-alta"
    if "média" in p or "media" in p:
        return "badge-media"
    return "badge-baixa"


def formatar_data(valor):
    if pd.isna(valor) or not valor:
        return ""
    try:
        return pd.to_datetime(valor).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(valor)[:16]


# =========================
# LOGIN V2
# =========================

if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = {}

if not st.session_state.logado:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {display:none;}
    .block-container {
        padding-top: 4rem !important;
        max-width: 980px !important;
    }
    .login-page-header {
        background:linear-gradient(135deg,#04162F,#073763);
        border-radius:28px;
        padding:38px 32px;
        color:white;
        text-align:center;
        margin-bottom:28px;
        box-shadow:0 18px 45px rgba(2,8,23,.22);
    }
    .login-page-logo {
        font-size:42px;
        font-weight:950;
        color:white;
    }
    .login-page-subtitle {
        color:#dbeafe;
        margin-top:8px;
        font-size:16px;
    }
    .login-box {
        background:white;
        border:1px solid #e5e7eb;
        border-radius:24px;
        padding:28px;
        box-shadow:0 16px 38px rgba(15,23,42,.10);
    }
    
/* V4.2 fixes */
[data-testid="stSidebar"] .stButton > button {
    background:rgba(255,255,255,.12) !important;
    color:white !important;
    border:1px solid rgba(255,255,255,.45) !important;
}
[data-testid="stSidebar"] .stButton > button * {
    color:white !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background:rgba(37,99,235,.55) !important;
    color:white !important;
}
[data-testid="stSidebar"] {
    min-width: 285px !important;
}
.main-title {
    padding-top: 8px;
}
.right-panel {
    top:72px !important;
}
[data-testid="stHeader"] {
    background:rgba(255,255,255,.92) !important;
}


.dark-tv-box .stButton > button {
    background:rgba(255,255,255,.10) !important;
    color:white !important;
    border:1px solid rgba(255,255,255,.18) !important;
    border-radius:12px !important;
    font-weight:950 !important;
    padding:10px 8px !important;
}
.dark-tv-box .stButton > button:hover {
    background:#2563eb !important;
    color:white !important;
    border-color:#2563eb !important;
}
.dark-tv-box .stButton > button * {
    color:white !important;
}
.filtro-ativo {
    background:rgba(37,99,235,.22);
    border:1px solid rgba(255,255,255,.12);
    border-radius:12px;
    padding:10px 14px;
    margin:10px 0 12px 0;
    font-weight:900;
    color:white !important;
}

</style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-page-header">
        <div class="login-page-logo">⚖️ LEGALONE</div>
        <div class="login-page-subtitle">Chamados Operacionais LegalOne • V360</div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 1.15, 1])

    with col_b:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("### Bem-vindo de volta!")
        st.caption("Faça login para continuar no sistema de chamados.")

        with st.form("login_form"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            entrar = st.form_submit_button("Entrar no Sistema", use_container_width=True)

            if entrar:
                usuario_login = fazer_login(email, senha)

                if usuario_login:
                    st.session_state.logado = True
                    st.session_state.usuario = usuario_login
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

usuario = st.session_state.usuario


# =========================
# SIDEBAR V2
# =========================

with st.sidebar:
    st.markdown('<div class="sidebar-logo">⚖️ LEGALONE</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="sidebar-user">
            <div class="sidebar-user-name">Olá, {usuario.get('nome','')}</div>
            <div class="sidebar-user-role">{usuario.get('perfil','')}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

perfil_usuario = usuario["perfil"]

MENU_LABELS = {
    "Painel Geral": "🔴 Painel Geral",
    "Insights": "💡 Insights",
    "TV Operacional": "⚪ TV Operacional",
    "Atualizar Chamado": "⚪ Atualizar Chamado",
    "Abrir Chamado": "⚪ Abrir Chamado",
    "Relatórios": "⚪ Relatórios",
    "Gerenciar Usuários": "⚪ Gerenciar Usuários"
}

if perfil_usuario == "TV":
    opcoes_menu = ["TV Operacional"]
elif perfil_usuario == "Administrador":
    opcoes_menu = [
        "Painel Geral",
        "Insights",
        "TV Operacional",
        "Atualizar Chamado",
        "Abrir Chamado",
        "Relatórios",
        "Gerenciar Usuários"
    ]
elif perfil_usuario == "Gestor":
    opcoes_menu = [
        "Painel Geral",
        "Insights",
        "Atualizar Chamado",
        "Abrir Chamado",
        "Relatórios"
    ]
elif perfil_usuario == "Colaborador":
    opcoes_menu = [
        "Abrir Chamado",
        "Painel Geral"
    ]
else:
    opcoes_menu = ["Abrir Chamado", "Painel Geral"]

query_params = st.query_params
modo_tv = query_params.get("tv", "0") == "1"

if modo_tv and perfil_usuario in ["Administrador", "Diretoria", "TV"]:
    menu = "TV Operacional"
else:
    with st.sidebar:
        menu = st.radio(
            "Menu",
            opcoes_menu,
            format_func=lambda opcao: MENU_LABELS.get(opcao, opcao)
        )
        st.divider()
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.logado = False
            st.session_state.usuario = {}
            st.rerun()

if modo_tv:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {display:none;}
    .block-container {padding: 0.5rem 0.5rem 1rem 0.5rem;}
    
.online-box {
    background:white;
    border:1px solid #e5e7eb;
    border-radius:16px;
    padding:12px 16px;
    color:#0f172a;
    box-shadow:0 8px 20px rgba(15,23,42,.06);
}
.online-dot {
    display:inline-block;
    width:10px;
    height:10px;
    background:#16a34a;
    border-radius:50%;
    margin-right:7px;
}
.premium-kpi {
    background:#fff;
    border:1px solid #e5e7eb;
    border-radius:22px;
    padding:22px;
    box-shadow:0 10px 28px rgba(15,23,42,.08);
    min-height:138px;
}
.premium-icon {
    width:44px;
    height:44px;
    border-radius:16px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:23px;
    margin-bottom:10px;
}
.kpi-blue {background:#dbeafe;}
.kpi-orange {background:#ffedd5;}
.kpi-purple {background:#ede9fe;}
.kpi-green {background:#dcfce7;}
.kpi-red {background:#fee2e2;}
.premium-label {
    font-size:13px;
    font-weight:900;
    color:#475569;
}
.premium-number {
    font-size:38px;
    font-weight:950;
    color:#020617;
    line-height:1.05;
}
.premium-foot {
    font-size:13px;
    font-weight:900;
    color:#2563eb;
    margin-top:8px;
}
.premium-chart {
    min-height:auto;
    padding-bottom:10px;
}
.dark-tv-box {
    background:linear-gradient(180deg,#071A33,#0B274D);
    border-radius:22px;
    padding:18px;
    box-shadow:0 16px 35px rgba(2,8,23,.18);
    color:white !important;
}
.dark-tv-box * {
    color:white !important;
}
.dark-tv-title {
    font-size:20px;
    font-weight:950;
}
.live-badge {
    background:#dc2626;
    color:white;
    border-radius:999px;
    padding:5px 10px;
    font-size:12px;
    margin-left:10px;
}
.dark-tv-time {
    text-align:right;
    font-size:18px;
    font-weight:900;
}
.tv-tab {
    background:rgba(255,255,255,.08);
    border-radius:12px;
    text-align:center;
    padding:10px;
    font-weight:900;
    font-size:13px;
    margin-bottom:12px;
}
.tv-tab.active {
    background:#2563eb;
}
.right-panel {
    background:white;
    border:1px solid #e5e7eb;
    border-radius:26px;
    padding:22px;
    box-shadow:0 12px 30px rgba(15,23,42,.08);
    position:sticky;
    top:20px;
}
.right-title {
    font-size:30px;
    font-weight:950;
    color:#0f172a;
}
.right-subtitle {
    color:#64748b;
    font-size:14px;
    margin-bottom:18px;
}
.selected-ticket {
    border:1px solid #dbeafe;
    border-radius:20px;
    padding:18px;
    background:#f8fbff;
    margin-bottom:16px;
}
.selected-header {
    display:flex;
    justify-content:space-between;
    align-items:center;
}
.selected-protocol {
    font-size:26px;
    font-weight:950;
    color:#0f172a;
}
.selected-meta {
    margin-top:12px;
    color:#475569;
    font-weight:800;
    font-size:13px;
}
.selected-desc {
    background:#eef6ff;
    border-radius:14px;
    padding:14px;
    margin-top:14px;
    color:#0f172a;
    font-size:14px;
}
[data-testid="stSidebar"] .stRadio label {
    background:rgba(255,255,255,.08);
    border-radius:12px;
    padding:8px 10px;
    margin-bottom:5px;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background:rgba(37,99,235,.45);
}


.card-title-only {
    background:white;
    border:1px solid #e5e7eb;
    border-bottom:0;
    border-radius:22px 22px 0 0;
    padding:20px 22px 8px 22px;
    margin-bottom:0;
    box-shadow:0 12px 28px rgba(15,23,42,.07);
}
[data-testid="stPlotlyChart"] {
    background:white;
    border:1px solid #e5e7eb;
    border-top:0;
    border-radius:0 0 22px 22px;
    padding:8px 12px 14px 12px;
    box-shadow:0 12px 28px rgba(15,23,42,.07);
    margin-bottom:18px;
}


/* V4.2 fixes */
[data-testid="stSidebar"] .stButton > button {
    background:rgba(255,255,255,.12) !important;
    color:white !important;
    border:1px solid rgba(255,255,255,.45) !important;
}
[data-testid="stSidebar"] .stButton > button * {
    color:white !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background:rgba(37,99,235,.55) !important;
    color:white !important;
}
[data-testid="stSidebar"] {
    min-width: 285px !important;
}
.main-title {
    padding-top: 8px;
}
.right-panel {
    top:72px !important;
}
[data-testid="stHeader"] {
    background:rgba(255,255,255,.92) !important;
}


.dark-tv-box .stButton > button {
    background:rgba(255,255,255,.10) !important;
    color:white !important;
    border:1px solid rgba(255,255,255,.18) !important;
    border-radius:12px !important;
    font-weight:950 !important;
    padding:10px 8px !important;
}
.dark-tv-box .stButton > button:hover {
    background:#2563eb !important;
    color:white !important;
    border-color:#2563eb !important;
}
.dark-tv-box .stButton > button * {
    color:white !important;
}
.filtro-ativo {
    background:rgba(37,99,235,.22);
    border:1px solid rgba(255,255,255,.12);
    border-radius:12px;
    padding:10px 14px;
    margin:10px 0 12px 0;
    font-weight:900;
    color:white !important;
}

</style>
    """, unsafe_allow_html=True)


# =========================
# ABRIR CHAMADO
# =========================

if menu == "Abrir Chamado":
    st.markdown('<div class="main-title">➕ Abrir Chamado LegalOne</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Registre uma nova solicitação operacional do LegalOne.</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="detail-card">', unsafe_allow_html=True)

        with st.form("form_chamado"):
            col1, col2 = st.columns(2)

            with col1:
                solicitante = st.text_input(
                    "Nome do solicitante",
                    value=usuario["nome"]
                )

                email_solicitante = st.text_input(
                    "E-mail",
                    value=usuario["email"]
                )

                unidade_atual = usuario.get("unidade") or "LegalOne"
                unidades_abertura = opcoes_unidade(unidade_atual)
                unidade = st.selectbox(
                    "Unidade",
                    unidades_abertura,
                    index=indice_unidade(unidades_abertura, unidade_atual)
                )

            with col2:
                setor = st.selectbox(
                    "Setor responsável",
                    ["LegalOne"],
                    disabled=True
                )

                categoria = st.selectbox(
                    "Categoria",
                    [
                        "Prazo",
                        "Processo",
                        "Andamento",
                        "Tarefa",
                        "Documento",
                        "GED",
                        "Acesso",
                        "Relatório",
                        "Mesa de Trabalho",
                        "Sincronização",
                        "Cadastro",
                        "Contrato",
                        "Lentidão",
                        "Erro Geral"
                    ]
                )

                prioridade = st.selectbox(
                    "Prioridade",
                    ["Baixa", "Média", "Alta", "Urgente"]
                )

            descricao = st.text_area("Descrição do chamado", height=160)

            enviar = st.form_submit_button("✅ Abrir chamado", use_container_width=True)

            if enviar:
                if not descricao:
                    st.error("Descreva o chamado.")
                else:
                    dados = {
                        "solicitante": solicitante,
                        "email_solicitante": email_solicitante,
                        "unidade": unidade,
                        "setor": "LegalOne",
                        "categoria": categoria,
                        "prioridade": prioridade,
                        "descricao": descricao,
                        "status": "Aberto",
                        "criado_em": datetime.now(timezone.utc).isoformat()
                    }

                    result = supabase.table("chamados_legalone").insert(dados).execute()
                    chamado_id = result.data[0]["id"]
                    protocolo = criar_protocolo(chamado_id)

                    supabase.table("chamados_legalone") \
                        .update({"protocolo": protocolo}) \
                        .eq("id", chamado_id) \
                        .execute()

                    st.success(f"Chamado LegalOne criado com sucesso! {protocolo}")

                    ok_chat, detalhe_chat = enviar_google_chat(
                        f"🚨 *Novo chamado LegalOne aberto*\n\n"
                        f"Protocolo: {protocolo}\n"
                        f"Solicitante: {solicitante}\n"
                        f"Unidade: {unidade}\n"
                        f"Setor: LegalOne\n"
                        f"Categoria: {categoria}\n"
                        f"Prioridade: {prioridade}\n"
                        f"Descrição: {descricao}"
                    )

                    if not ok_chat:
                        st.warning("Chamado criado, mas não foi possível avisar no Google Chat.")
                        st.code(detalhe_chat)

        st.markdown('</div>', unsafe_allow_html=True)


# =========================
# PAINEL GERAL V4
# =========================

elif menu == "Painel Geral":
    df = carregar_chamados()
    df = aplicar_permissao_chamados(df, usuario)

    if df.empty:
        st.markdown('<div class="main-title">Painel Geral LegalOne</div>', unsafe_allow_html=True)
        st.info("Nenhum chamado encontrado.")

    else:
        df["criado_em"] = pd.to_datetime(df["criado_em"], errors="coerce", utc=True)
        df["sla"] = df.apply(calcular_sla, axis=1)

        total = len(df)
        abertos = len(df[df["status"] == "Aberto"])
        andamento = len(df[df["status"] == "Em andamento"])
        finalizados = len(df[df["status"] == "Finalizado"])
        urgentes = len(df[df["prioridade"] == "Urgente"])
        atrasados = len(df[df["sla"] == "Atrasado"])

        agora_mes = datetime.now(timezone.utc)
        if "finalizado_em" in df.columns:
            df["finalizado_em"] = pd.to_datetime(df["finalizado_em"], errors="coerce", utc=True)
            finalizados_mes = len(
                df[
                    (df["status"] == "Finalizado") &
                    (df["finalizado_em"].dt.month == agora_mes.month) &
                    (df["finalizado_em"].dt.year == agora_mes.year)
                ]
            )
        else:
            finalizados_mes = finalizados

        topo1, topo2, topo3 = st.columns([1.8, 1, 1])

        with topo1:
            st.markdown('<div class="main-title">Painel Geral LegalOne</div>', unsafe_allow_html=True)
            st.markdown('<div class="main-subtitle">Visão geral dos chamados operacionais LegalOne.</div>', unsafe_allow_html=True)

        with topo2:
            st.markdown(
                f"""
                <div class="online-box">
                    <span class="online-dot"></span>
                    <b>Última atualização:</b><br>
                    {datetime.now().strftime('%d/%m/%Y %H:%M')}
                </div>
                """,
                unsafe_allow_html=True
            )

        with topo3:
            if st.button("🔄 Atualizar dados", use_container_width=True, key="painel_atualizar_dados"):
                st.rerun()

        k1, k2, k3, k4, k5 = st.columns(5)

        kpis = [
            (k1, "🟠", "Abertos", abertos, "- hoje", "kpi-orange"),
            (k2, "🔍", "Em Andamento", andamento, "+ hoje", "kpi-purple"),
            (k3, "⏱️", "Atrasados (SLA)", atrasados, "+ SLA", "kpi-red"),
            (k4, "✅", "Finalizados do mês", finalizados_mes, "+ mês", "kpi-green"),
            (k5, "📋", "Total de Chamados", total, "+ geral", "kpi-blue"),
        ]

        for col, icon, label, num, foot, classe in kpis:
            with col:
                st.markdown(
                    f"""
                    <div class="premium-kpi">
                        <div class="premium-icon {classe}">{icon}</div>
                        <div class="premium-label">{label}</div>
                        <div class="premium-number">{num}</div>
                        <div class="premium-foot">{foot}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.write("")
        st.markdown('<div class="section-title">🛠️ Atualizar Chamado</div>', unsafe_allow_html=True)
        st.caption("A função mais utilizada agora fica em destaque, logo abaixo dos indicadores.")

        df_abertos = df[~df["status"].isin(["Finalizado", "Cancelado"])].copy()
        busca = st.text_input(
            "Buscar chamado",
            placeholder="Protocolo, unidade, descrição...",
            key="painel_busca_chamado"
        )

        if busca and not df_abertos.empty:
            termo = busca.lower().strip()
            df_abertos = df_abertos[
                df_abertos.astype(str).apply(
                    lambda linha: termo in " ".join(linha.values).lower(),
                    axis=1
                )
            ]

        if df_abertos.empty:
            st.info("Nenhum chamado aberto encontrado para atualização.")
        else:
            df_abertos["opcao"] = (
                df_abertos["protocolo"].fillna(df_abertos["id"].astype(str))
                + " - "
                + df_abertos["descricao"].fillna("").str[:70]
            )

            chamado_opcao = st.selectbox(
                "Selecione um chamado aberto",
                df_abertos["opcao"].tolist(),
                key="painel_chamado_selecionado"
            )

            chamado = df_abertos[df_abertos["opcao"] == chamado_opcao].iloc[0]
            chamado_id = int(chamado["id"])

            detalhe_col, edicao_col = st.columns([1.15, 1.35], gap="large")

            with detalhe_col:
                st.markdown(
                    f"""
                    <div class="selected-ticket">
                        <div class="selected-header">
                            <span class="selected-protocol">{chamado.get('protocolo','')}</span>
                            <span class="badge {prioridade_badge(chamado.get('prioridade',''))}">{chamado.get('prioridade','')}</span>
                        </div>
                        <div class="selected-meta">
                            📍 {chamado.get('unidade','')} &nbsp; • &nbsp;
                            🏢 {chamado.get('setor','')} &nbsp; • &nbsp;
                            👤 {chamado.get('solicitante','')}
                        </div>
                        <div class="selected-desc">
                            <b>Descrição do problema</b><br>
                            {chamado.get('descricao','')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                with st.expander("📜 Histórico do chamado", expanded=False):
                    try:
                        hist = supabase.table("historico_chamados_legalone") \
                            .select("*") \
                            .eq("chamado_id", chamado_id) \
                            .order("criado_em", desc=True) \
                            .limit(6) \
                            .execute()

                        if not hist.data:
                            st.caption("Nenhum histórico registrado.")

                        for h in hist.data or []:
                            st.markdown(
                                f"""
                                <div class="timeline-item">
                                    <b>{formatar_data(h.get('criado_em',''))}</b><br>
                                    {h.get('usuario','')} - Status: {h.get('status','')}<br>
                                    <small>{h.get('observacao','')}</small>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    except Exception:
                        st.caption("Histórico indisponível.")

            with edicao_col:
                status_opcoes = ["Aberto", "Em andamento", "Aguardando", "Finalizado", "Cancelado"]
                status_atual = chamado.get("status") or "Aberto"
                status_index = status_opcoes.index(status_atual) if status_atual in status_opcoes else 0

                responsaveis_opcoes = ["Paulo Balbi", "Icaro Bruce", "Alexandre Brito"]
                responsavel_atual = chamado.get("responsavel")

                if pd.isna(responsavel_atual) or not str(responsavel_atual).strip() or str(responsavel_atual).lower() == "nan":
                    responsavel_atual = usuario["nome"]

                if str(responsavel_atual) not in responsaveis_opcoes:
                    responsaveis_opcoes.append(str(responsavel_atual))

                f1, f2 = st.columns(2)

                with f1:
                    novo_status = st.selectbox(
                        "Atualizar Status",
                        status_opcoes,
                        index=status_index,
                        key=f"painel_status_{chamado_id}"
                    )

                with f2:
                    responsavel = st.selectbox(
                        "Responsável",
                        responsaveis_opcoes,
                        index=responsaveis_opcoes.index(str(responsavel_atual)),
                        key=f"painel_responsavel_{chamado_id}"
                    )

                observacao_atual = chamado.get("observacoes")
                if pd.isna(observacao_atual) or str(observacao_atual).lower() == "nan":
                    observacao_atual = ""

                observacoes = st.text_area(
                    "Observações",
                    value=observacao_atual,
                    height=150,
                    key=f"painel_observacoes_{chamado_id}"
                )

                col_a, col_b = st.columns([1, 1.35])

                with col_a:
                    salvar = st.button(
                        "💾 Salvar",
                        use_container_width=True,
                        key=f"painel_salvar_{chamado_id}"
                    )

                with col_b:
                    responder = st.button(
                        "💬 Responder Solicitante",
                        use_container_width=True,
                        key=f"painel_responder_{chamado_id}"
                    )

                if salvar or responder:
                    dados_update = {
                        "status": novo_status,
                        "responsavel": responsavel,
                        "observacoes": observacoes,
                        "atualizado_em": datetime.now(timezone.utc).isoformat()
                    }

                    if novo_status == "Finalizado":
                        dados_update["finalizado_em"] = datetime.now(timezone.utc).isoformat()

                    supabase.table("chamados_legalone") \
                        .update(dados_update) \
                        .eq("id", chamado_id) \
                        .execute()

                    supabase.table("historico_chamados_legalone").insert({
                        "chamado_id": chamado_id,
                        "protocolo": chamado.get("protocolo", ""),
                        "status": novo_status,
                        "usuario": responsavel or usuario["nome"],
                        "observacao": observacoes
                    }).execute()

                    st.success("Chamado LegalOne atualizado.")

                    if novo_status == "Finalizado":
                        ok, detalhe = notificar_conclusao_bot(
                            chamado,
                            responsavel or usuario["nome"],
                            observacoes
                        )

                        if ok:
                            st.success("Solicitante notificado no Google Chat.")
                        else:
                            st.warning("Não foi possível notificar o solicitante.")
                            st.code(detalhe)

                    ok_chat, detalhe_chat = enviar_google_chat(
                        f"✅ *Chamado atualizado*\n\n"
                        f"Protocolo: {chamado.get('protocolo', '')}\n"
                        f"Novo status: {novo_status}\n"
                        f"Responsável: {responsavel}\n"
                        f"Observação: {observacoes}"
                    )

                    if not ok_chat:
                        st.warning("Chamado atualizado, mas não foi possível avisar no Google Chat.")
                        st.code(detalhe_chat)

        st.divider()
        st.markdown('<div class="section-title">📊 Gráficos e indicadores</div>', unsafe_allow_html=True)

        g1, g2, g3 = st.columns([1.05, 1.05, .95], gap="medium")

        with g1:
            st.markdown('<div class="section-title card-title-only">Chamados por Status</div>', unsafe_allow_html=True)
            fig_status = px.pie(df, names="status", hole=0.58)
            fig_status.update_layout(
                height=310,
                margin=dict(t=5, b=5, l=5, r=5),
                legend=dict(orientation="v", y=.5)
            )
            st.plotly_chart(fig_status, use_container_width=True)

        with g2:
            st.markdown('<div class="section-title card-title-only">Chamados por Prioridade</div>', unsafe_allow_html=True)
            prioridade_df = (
                df.groupby("prioridade")
                .size()
                .reset_index(name="quantidade")
                .sort_values("quantidade", ascending=False)
            )
            fig_prioridade = px.bar(
                prioridade_df,
                x="prioridade",
                y="quantidade",
                text="quantidade"
            )
            fig_prioridade.update_layout(
                height=310,
                margin=dict(t=5, b=5, l=5, r=5),
                showlegend=False
            )
            fig_prioridade.update_traces(textposition="outside")
            st.plotly_chart(fig_prioridade, use_container_width=True)

        with g3:
            st.markdown('<div class="section-title card-title-only">Chamados por Categoria</div>', unsafe_allow_html=True)
            agrupado_df = (
                df.groupby("categoria")
                .size()
                .reset_index(name="quantidade")
                .sort_values("quantidade", ascending=True)
                .tail(8)
            )
            fig_agrupado = px.bar(
                agrupado_df,
                x="quantidade",
                y="categoria",
                orientation="h",
                text="quantidade"
            )
            fig_agrupado.update_layout(
                height=310,
                margin=dict(t=5, b=5, l=5, r=5),
                showlegend=False
            )
            st.plotly_chart(fig_agrupado, use_container_width=True)

        st.markdown('<div class="dark-tv-box">', unsafe_allow_html=True)
        tv_top1, tv_top2 = st.columns([2, 1])

        with tv_top1:
            st.markdown('<div class="dark-tv-title">📺 TV OPERACIONAL - LEGALONE AO VIVO <span class="live-badge">AO VIVO</span></div>', unsafe_allow_html=True)

        with tv_top2:
            st.markdown(
                f'<div class="dark-tv-time">{datetime.now().strftime("%d/%m/%Y %H:%M")}</div>',
                unsafe_allow_html=True
            )

        if "filtro_tv_painel" not in st.session_state:
            st.session_state.filtro_tv_painel = "Todos"

        tabs1, tabs2, tabs3, tabs4, tabs5 = st.columns(5)

        with tabs1:
            if st.button(f"Todos  {total}", use_container_width=True, key="btn_tv_todos"):
                st.session_state.filtro_tv_painel = "Todos"

        with tabs2:
            if st.button(f"Abertos  {abertos}", use_container_width=True, key="btn_tv_abertos"):
                st.session_state.filtro_tv_painel = "Abertos"

        with tabs3:
            if st.button(f"Em andamento  {andamento}", use_container_width=True, key="btn_tv_andamento"):
                st.session_state.filtro_tv_painel = "Em andamento"

        with tabs4:
            if st.button(f"Atrasados  {atrasados}", use_container_width=True, key="btn_tv_atrasados"):
                st.session_state.filtro_tv_painel = "Atrasados"

        with tabs5:
            if st.button(f"Urgentes  {urgentes}", use_container_width=True, key="btn_tv_urgentes"):
                st.session_state.filtro_tv_painel = "Urgentes"

        filtro_tv = st.session_state.filtro_tv_painel

        if filtro_tv == "Abertos":
            df_tv_painel = df[df["status"] == "Aberto"].copy()
        elif filtro_tv == "Em andamento":
            df_tv_painel = df[df["status"] == "Em andamento"].copy()
        elif filtro_tv == "Atrasados":
            df_tv_painel = df[df["sla"] == "Atrasado"].copy()
        elif filtro_tv == "Urgentes":
            df_tv_painel = df[df["prioridade"] == "Urgente"].copy()
        else:
            df_tv_painel = df.copy()

        st.markdown(
            f'<div class="filtro-ativo">Filtro ativo: <b>{filtro_tv}</b> • {len(df_tv_painel)} chamado(s)</div>',
            unsafe_allow_html=True
        )

        colunas_recentes = [
            "protocolo",
            "unidade",
            "setor",
            "descricao",
            "prioridade",
            "status",
            "sla",
            "responsavel",
            "criado_em"
        ]
        colunas_recentes = [c for c in colunas_recentes if c in df_tv_painel.columns]
        recentes = df_tv_painel[colunas_recentes].head(12).copy()

        if "criado_em" in recentes.columns:
            recentes["criado_em"] = recentes["criado_em"].apply(formatar_data)

        st.dataframe(recentes, use_container_width=True, hide_index=True)
        st.caption("Atualização automática a cada 30 segundos")
        st.markdown('</div>', unsafe_allow_html=True)


# =========================
# INSIGHTS LEGALONE
# =========================

elif menu == "Insights":
    df = carregar_chamados()
    df = aplicar_permissao_chamados(df, usuario)

    topo_titulo, topo_periodo, topo_unidade = st.columns([1.8, .75, .9])

    with topo_titulo:
        st.markdown('<div class="main-title">💡 Insights LegalOne</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="main-subtitle">Leitura inteligente dos chamados para orientar decisões e prioridades.</div>',
            unsafe_allow_html=True
        )

    with topo_periodo:
        periodo_dias = st.selectbox(
            "Período",
            [7, 15, 30, 60, 90],
            index=2,
            format_func=lambda valor: f"Últimos {valor} dias",
            key="insights_periodo"
        )

    if df.empty:
        with topo_unidade:
            st.selectbox("Unidade", ["Todas as unidades"], disabled=True)
        st.info("Nenhum chamado encontrado para gerar insights.")

    else:
        # Garante as colunas necessárias mesmo em bases mais antigas.
        colunas_padrao = {
            "unidade": "Não informada",
            "categoria": "Geral",
            "responsavel": "Não atribuído",
            "prioridade": "Média",
            "status": "Aberto",
            "descricao": ""
        }

        for coluna, valor_padrao in colunas_padrao.items():
            if coluna not in df.columns:
                df[coluna] = valor_padrao
            df[coluna] = df[coluna].fillna(valor_padrao).astype(str)

        df["criado_em"] = pd.to_datetime(df.get("criado_em"), errors="coerce", utc=True)

        unidades_disponiveis = sorted(
            [u for u in df["unidade"].dropna().unique().tolist() if str(u).strip()]
        )

        with topo_unidade:
            unidade_selecionada = st.selectbox(
                "Unidade",
                ["Todas as unidades"] + unidades_disponiveis,
                key="insights_unidade"
            )

        agora = datetime.now(timezone.utc)
        inicio_periodo = agora - timedelta(days=periodo_dias)
        inicio_periodo_anterior = inicio_periodo - timedelta(days=periodo_dias)

        df_periodo = df[df["criado_em"] >= inicio_periodo].copy()
        df_anterior = df[
            (df["criado_em"] >= inicio_periodo_anterior) &
            (df["criado_em"] < inicio_periodo)
        ].copy()

        if unidade_selecionada != "Todas as unidades":
            df_periodo = df_periodo[df_periodo["unidade"] == unidade_selecionada].copy()
            df_anterior = df_anterior[df_anterior["unidade"] == unidade_selecionada].copy()

        if df_periodo.empty:
            st.warning("Não há chamados no período e filtro selecionados.")

        else:
            df_periodo["sla"] = df_periodo.apply(calcular_sla, axis=1)

            status_encerrados = ["Finalizado", "Cancelado"]
            df_ativos = df_periodo[~df_periodo["status"].isin(status_encerrados)].copy()
            df_finalizados = df_periodo[df_periodo["status"] == "Finalizado"].copy()

            prazos_horas = {
                "Urgente": 1,
                "Alta": 4,
                "Média": 24,
                "Media": 24,
                "Baixa": 72
            }

            if not df_ativos.empty:
                df_ativos["horas_prazo"] = df_ativos["prioridade"].map(prazos_horas).fillna(24)
                df_ativos["prazo_final"] = (
                    df_ativos["criado_em"] +
                    pd.to_timedelta(df_ativos["horas_prazo"], unit="h")
                )
                df_ativos["horas_restantes"] = (
                    df_ativos["prazo_final"] - pd.Timestamp(agora)
                ).dt.total_seconds() / 3600
            else:
                df_ativos["horas_restantes"] = pd.Series(dtype=float)

            df_atrasados = df_ativos[df_ativos["horas_restantes"] < 0].copy()
            df_proximos = df_ativos[
                (df_ativos["horas_restantes"] >= 0) &
                (df_ativos["horas_restantes"] <= 24)
            ].sort_values("horas_restantes").copy()

            total_periodo = len(df_periodo)
            ativos = len(df_ativos)
            atrasados = len(df_atrasados)
            proximos = len(df_proximos)
            dentro_sla = round(((ativos - atrasados) / ativos) * 100) if ativos else 100

            contagem_categoria = (
                df_periodo.groupby("categoria")
                .size()
                .sort_values(ascending=False)
            )
            categoria_top = contagem_categoria.index[0] if not contagem_categoria.empty else "Sem categoria"
            qtd_categoria_top = int(contagem_categoria.iloc[0]) if not contagem_categoria.empty else 0

            # Taxa simples de reincidência por concentração em categorias.
            repeticoes = int(sum(max(int(qtd) - 1, 0) for qtd in contagem_categoria.tolist()))
            taxa_reincidencia = round((repeticoes / total_periodo) * 100) if total_periodo else 0

            # Ranking de unidades por volume + atraso + urgência.
            base_unidades = df_periodo.copy()
            base_unidades["atrasado_num"] = (base_unidades["sla"] == "Atrasado").astype(int)
            base_unidades["urgente_num"] = (base_unidades["prioridade"] == "Urgente").astype(int)
            base_unidades["ativo_num"] = (~base_unidades["status"].isin(status_encerrados)).astype(int)

            ranking_unidades = (
                base_unidades.groupby("unidade")
                .agg(
                    chamados=("unidade", "size"),
                    ativos=("ativo_num", "sum"),
                    atrasados=("atrasado_num", "sum"),
                    urgentes=("urgente_num", "sum")
                )
                .reset_index()
            )
            ranking_unidades["pontuacao"] = (
                ranking_unidades["chamados"] +
                ranking_unidades["atrasados"] * 3 +
                ranking_unidades["urgentes"] * 2
            )
            ranking_unidades = ranking_unidades.sort_values(
                ["pontuacao", "atrasados", "chamados"],
                ascending=False
            )

            unidade_atencao = (
                ranking_unidades.iloc[0]["unidade"]
                if not ranking_unidades.empty
                else "Sem unidade"
            )

            dados_unidade_atencao = (
                ranking_unidades.iloc[0]
                if not ranking_unidades.empty
                else None
            )

            # Crescimento da unidade de atenção comparado ao período anterior.
            atual_unidade = len(df_periodo[df_periodo["unidade"] == unidade_atencao])
            anterior_unidade = len(df_anterior[df_anterior["unidade"] == unidade_atencao])

            if anterior_unidade > 0:
                crescimento_unidade = round(
                    ((atual_unidade - anterior_unidade) / anterior_unidade) * 100
                )
            elif atual_unidade > 0:
                crescimento_unidade = 100
            else:
                crescimento_unidade = 0

            fila_responsavel = (
                df_ativos.groupby("responsavel")
                .size()
                .sort_values(ascending=False)
            )
            responsavel_maior_fila = (
                fila_responsavel.index[0]
                if not fila_responsavel.empty
                else "Sem responsável"
            )
            qtd_maior_fila = (
                int(fila_responsavel.iloc[0])
                if not fila_responsavel.empty
                else 0
            )

            resumo = (
                f"A categoria <b>{categoria_top}</b> concentra a maior quantidade de chamados "
                f"no período, com <b>{qtd_categoria_top}</b> ocorrência(s). "
                f"A unidade <b>{unidade_atencao}</b> aparece como principal ponto de atenção. "
                f"Existem <b>{atrasados} chamado(s) atrasado(s)</b> e "
                f"<b>{proximos} próximo(s) do vencimento do SLA</b>. "
                f"A prioridade recomendada é atuar primeiro nos chamados atrasados, "
                f"nos protocolos próximos do prazo e nas ocorrências recorrentes de {categoria_top}."
            )

            st.markdown(
                f"""
                <div class="insight-summary">
                    <div class="insight-summary-title">💡 Resumo inteligente do período</div>
                    <div class="insight-summary-text">{resumo}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            k1, k2, k3, k4 = st.columns(4)

            with k1:
                atrasados_unidade = (
                    int(dados_unidade_atencao["atrasados"])
                    if dados_unidade_atencao is not None
                    else 0
                )
                chamados_unidade = (
                    int(dados_unidade_atencao["chamados"])
                    if dados_unidade_atencao is not None
                    else 0
                )
                st.markdown(
                    f"""
                    <div class="insight-card">
                        <div class="insight-card-icon kpi-red">⚠️</div>
                        <div class="insight-card-label">Unidade que exige atenção</div>
                        <div class="insight-card-main">{unidade_atencao}</div>
                        <div class="insight-card-foot">
                            {chamados_unidade} chamado(s) • {atrasados_unidade} atrasado(s) •
                            variação de {crescimento_unidade:+d}% contra o período anterior
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with k2:
                st.markdown(
                    f"""
                    <div class="insight-card">
                        <div class="insight-card-icon kpi-orange">🔁</div>
                        <div class="insight-card-label">Problema mais recorrente</div>
                        <div class="insight-card-main">{categoria_top}</div>
                        <div class="insight-card-foot">
                            {qtd_categoria_top} ocorrência(s) • reincidência estimada em {taxa_reincidencia}%
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with k3:
                st.markdown(
                    f"""
                    <div class="insight-card">
                        <div class="insight-card-icon kpi-purple">⏳</div>
                        <div class="insight-card-label">Próximos de atrasar</div>
                        <div class="insight-card-main">{proximos} chamado(s)</div>
                        <div class="insight-card-foot">
                            {len(df_proximos[df_proximos["horas_restantes"] <= 2]) if not df_proximos.empty else 0}
                            vence(m) em até 2 horas
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with k4:
                st.markdown(
                    f"""
                    <div class="insight-card">
                        <div class="insight-card-icon kpi-blue">👥</div>
                        <div class="insight-card-label">Responsável com maior fila</div>
                        <div class="insight-card-main">{responsavel_maior_fila}</div>
                        <div class="insight-card-foot">
                            {qtd_maior_fila} chamado(s) ativo(s) • {dentro_sla}% da fila ainda dentro do SLA
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.write("")

            esquerda, direita = st.columns(2, gap="large")

            with esquerda:
                st.markdown('<div class="insight-panel">', unsafe_allow_html=True)
                st.markdown(
                    '<div class="insight-panel-title">Unidades que precisam de atenção</div>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    '<div class="insight-panel-subtitle">Ranking baseado em volume, atraso e urgência.</div>',
                    unsafe_allow_html=True
                )

                ranking_exibir = ranking_unidades.head(8).copy()
                ranking_exibir.insert(0, "posição", range(1, len(ranking_exibir) + 1))
                ranking_exibir = ranking_exibir.rename(columns={
                    "posição": "Posição",
                    "unidade": "Unidade",
                    "chamados": "Chamados",
                    "ativos": "Ativos",
                    "atrasados": "Atrasados",
                    "urgentes": "Urgentes",
                    "pontuacao": "Índice de atenção"
                })
                st.dataframe(
                    ranking_exibir[
                        ["Posição", "Unidade", "Chamados", "Ativos", "Atrasados", "Urgentes", "Índice de atenção"]
                    ],
                    use_container_width=True,
                    hide_index=True
                )
                st.markdown('</div>', unsafe_allow_html=True)

            with direita:
                st.markdown('<div class="insight-panel">', unsafe_allow_html=True)
                st.markdown(
                    '<div class="insight-panel-title">Problemas recorrentes</div>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    '<div class="insight-panel-subtitle">Categorias com maior concentração de chamados no período.</div>',
                    unsafe_allow_html=True
                )

                recorrentes = (
                    df_periodo.groupby("categoria")
                    .agg(
                        ocorrencias=("categoria", "size"),
                        unidades_afetadas=("unidade", "nunique"),
                        atrasados=("sla", lambda serie: int((serie == "Atrasado").sum()))
                    )
                    .reset_index()
                    .sort_values(["ocorrencias", "atrasados"], ascending=False)
                    .head(8)
                    .rename(columns={
                        "categoria": "Categoria",
                        "ocorrencias": "Ocorrências",
                        "unidades_afetadas": "Unidades afetadas",
                        "atrasados": "Atrasados"
                    })
                )
                st.dataframe(
                    recorrentes,
                    use_container_width=True,
                    hide_index=True
                )
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="insight-panel">', unsafe_allow_html=True)
            st.markdown(
                '<div class="insight-panel-title">Risco de SLA</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<div class="insight-panel-subtitle">Chamados que ainda não atrasaram, mas exigem atenção nas próximas 24 horas.</div>',
                unsafe_allow_html=True
            )

            if df_proximos.empty:
                st.success("Nenhum chamado corre risco de vencer nas próximas 24 horas.")
            else:
                sla_exibir = df_proximos.copy()
                sla_exibir["Tempo restante"] = sla_exibir["horas_restantes"].apply(
                    lambda horas: (
                        f"{int(horas)}h {int((horas - int(horas)) * 60):02d}min"
                        if horas >= 1
                        else f"{max(0, int(horas * 60))} min"
                    )
                )
                colunas_sla = [
                    "protocolo",
                    "unidade",
                    "categoria",
                    "responsavel",
                    "prioridade",
                    "Tempo restante"
                ]
                colunas_sla = [c for c in colunas_sla if c in sla_exibir.columns]
                sla_exibir = sla_exibir[colunas_sla].head(12).rename(columns={
                    "protocolo": "Protocolo",
                    "unidade": "Unidade",
                    "categoria": "Categoria",
                    "responsavel": "Responsável",
                    "prioridade": "Prioridade"
                })
                st.dataframe(
                    sla_exibir,
                    use_container_width=True,
                    hide_index=True
                )
            st.markdown('</div>', unsafe_allow_html=True)

            produtividade_col, recomendacoes_col = st.columns([1.1, .9], gap="large")

            with produtividade_col:
                st.markdown('<div class="insight-panel">', unsafe_allow_html=True)
                st.markdown(
                    '<div class="insight-panel-title">Produtividade e carga da equipe</div>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    '<div class="insight-panel-subtitle">Chamados ativos e finalizados por responsável.</div>',
                    unsafe_allow_html=True
                )

                fila_df = (
                    df_ativos.groupby("responsavel")
                    .size()
                    .reset_index(name="Fila atual")
                    if not df_ativos.empty
                    else pd.DataFrame(columns=["responsavel", "Fila atual"])
                )

                concluidos_df = (
                    df_finalizados.groupby("responsavel")
                    .size()
                    .reset_index(name="Finalizados")
                    if not df_finalizados.empty
                    else pd.DataFrame(columns=["responsavel", "Finalizados"])
                )

                produtividade = pd.merge(
                    fila_df,
                    concluidos_df,
                    on="responsavel",
                    how="outer"
                ).fillna(0)

                if produtividade.empty:
                    st.info("Ainda não há dados suficientes de responsáveis.")
                else:
                    produtividade["Fila atual"] = produtividade["Fila atual"].astype(int)
                    produtividade["Finalizados"] = produtividade["Finalizados"].astype(int)
                    produtividade = produtividade.rename(columns={"responsavel": "Responsável"})
                    produtividade = produtividade.sort_values(
                        ["Fila atual", "Finalizados"],
                        ascending=[False, False]
                    )
                    st.dataframe(
                        produtividade,
                        use_container_width=True,
                        hide_index=True
                    )
                st.markdown('</div>', unsafe_allow_html=True)

            with recomendacoes_col:
                st.markdown('<div class="insight-panel">', unsafe_allow_html=True)
                st.markdown(
                    '<div class="insight-panel-title">Recomendações automáticas</div>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    '<div class="insight-panel-subtitle">Ações sugeridas pelas regras de análise.</div>',
                    unsafe_allow_html=True
                )

                recomendacoes = []

                if atrasados > 0:
                    recomendacoes.append(
                        (
                            "Priorizar chamados atrasados",
                            f"Existem {atrasados} chamado(s) fora do SLA no filtro atual."
                        )
                    )

                if proximos > 0:
                    recomendacoes.append(
                        (
                            "Atuar nos protocolos próximos do vencimento",
                            f"{proximos} chamado(s) vence(m) nas próximas 24 horas."
                        )
                    )

                if unidade_atencao != "Sem unidade":
                    recomendacoes.append(
                        (
                            f"Concentrar atenção na unidade {unidade_atencao}",
                            f"Ela obteve o maior índice de atenção no período analisado."
                        )
                    )

                if categoria_top != "Sem categoria":
                    recomendacoes.append(
                        (
                            f"Investigar recorrências de {categoria_top}",
                            f"A categoria soma {qtd_categoria_top} ocorrência(s) no período."
                        )
                    )

                if qtd_maior_fila >= 5:
                    recomendacoes.append(
                        (
                            f"Revisar a carga de {responsavel_maior_fila}",
                            f"O responsável possui {qtd_maior_fila} chamado(s) ativo(s)."
                        )
                    )

                if not recomendacoes:
                    recomendacoes.append(
                        (
                            "Manter o acompanhamento",
                            "Não foram identificados alertas críticos no filtro atual."
                        )
                    )

                for indice, (titulo, detalhe) in enumerate(recomendacoes[:5], start=1):
                    st.markdown(
                        f"""
                        <div class="insight-recommendation">
                            <div class="insight-recommendation-number">{indice}</div>
                            <div class="insight-recommendation-text">
                                <b>{titulo}</b>
                                {detalhe}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown(
                    f"""
                    <div class="insight-attention">
                        <div class="insight-attention-title">PRIORIDADE DO PERÍODO</div>
                        <div class="insight-attention-main">{unidade_atencao}</div>
                        <div style="color:#7c2d12;font-size:13px;line-height:1.5;">
                            Tratar atrasos, chamados próximos do SLA e ocorrências de {categoria_top}.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown('</div>', unsafe_allow_html=True)


# =========================
# ATUALIZAR CHAMADO V4
# =========================

elif menu == "Atualizar Chamado":
    st.markdown('<div class="main-title">Atualizar Chamado</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Gerencie e atualize os chamados do sistema.</div>', unsafe_allow_html=True)

    busca = st.text_input("🔎 Buscar chamado, protocolo, unidade ou descrição", placeholder="Ex.: LO-00182, Cuiabá, prazo...")

    df = carregar_chamados()
    df = aplicar_permissao_chamados(df, usuario)
    df = df[~df["status"].isin(["Finalizado", "Cancelado"])]

    if busca and not df.empty:
        termo = busca.lower().strip()
        df = df[
            df.astype(str).apply(
                lambda linha: termo in " ".join(linha.values).lower(),
                axis=1
            )
        ]

    if df.empty:
        st.info("Nenhum chamado encontrado.")
    else:
        df["criado_em"] = pd.to_datetime(df["criado_em"], errors="coerce", utc=True)
        df["sla"] = df.apply(calcular_sla, axis=1)

        col_list, col_detail = st.columns([1, 1.65])

        with col_list:
            st.markdown('<div class="ticket-list">', unsafe_allow_html=True)
            st.markdown(f'<div class="section-title">Chamados Abertos <span class="status-chip">{len(df)}</span></div>', unsafe_allow_html=True)

            df["opcao"] = (
                df["protocolo"].fillna(df["id"].astype(str))
                + " - "
                + df["descricao"].fillna("").str[:45]
            )

            opcao = st.radio(
                "Selecione o chamado",
                df["opcao"].tolist(),
                label_visibility="collapsed"
            )

            st.markdown('</div>', unsafe_allow_html=True)

        chamado = df[df["opcao"] == opcao].iloc[0]

        with col_detail:
            st.markdown('<div class="detail-card">', unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="ticket-title">
                    {chamado.get('protocolo','')}
                    <span class="badge {prioridade_badge(chamado.get('prioridade',''))}">
                        {chamado.get('prioridade','')}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.caption(
                f"📍 {chamado.get('unidade','')}  •  "
                f"🏢 {chamado.get('setor','')}  •  "
                f"👤 {chamado.get('solicitante','')}  •  "
                f"🕒 {formatar_data(chamado.get('criado_em',''))}"
            )

            st.markdown('<div class="section-title">Descrição do Problema</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="desc-box">{chamado.get("descricao","")}</div>',
                unsafe_allow_html=True
            )

            c1, c2, c3 = st.columns(3)
            c1.metric("Prioridade", chamado.get("prioridade",""))
            c2.metric("Categoria", chamado.get("categoria",""))
            c3.metric("SLA", chamado.get("sla",""))

            novo_status = st.selectbox(
                "Atualizar Status",
                [
                    "Aberto",
                    "Em andamento",
                    "Aguardando",
                    "Finalizado",
                    "Cancelado"
                ]
            )

            observacoes = st.text_area(
                "Observações",
                value=chamado.get("observacoes") or "",
                height=120
            )

            responsavel = st.text_input(
                "Responsável",
                value=chamado.get("responsavel") or usuario["nome"]
            )

            b1, b2, b3 = st.columns([1,1,1.4])

            with b1:
                cancelar = st.button("Cancelar", use_container_width=True)

            with b2:
                salvar = st.button("Salvar Alterações", use_container_width=True)

            with b3:
                responder = st.button("Responder ao Solicitante", use_container_width=True)

            if salvar or responder:
                dados_update = {
                    "status": novo_status,
                    "responsavel": responsavel,
                    "observacoes": observacoes,
                    "atualizado_em": datetime.now(timezone.utc).isoformat()
                }

                if novo_status == "Finalizado":
                    dados_update["finalizado_em"] = datetime.now(timezone.utc).isoformat()

                supabase.table("chamados_legalone") \
                    .update(dados_update) \
                    .eq("id", int(chamado["id"])) \
                    .execute()

                supabase.table("historico_chamados_legalone") \
                    .insert({
                        "chamado_id": int(chamado["id"]),
                        "protocolo": chamado["protocolo"],
                        "status": novo_status,
                        "usuario": responsavel or usuario["nome"],
                        "observacao": observacoes
                    }) \
                    .execute()

                st.success("Chamado LegalOne atualizado.")

                if novo_status == "Finalizado":
                    ok, detalhe = notificar_conclusao_bot(
                        chamado,
                        responsavel or usuario["nome"],
                        observacoes
                    )

                    if ok:
                        st.success("O bot foi acionado para notificar o solicitante no Google Chat.")
                    else:
                        st.warning("Chamado finalizado, mas o bot não conseguiu notificar o solicitante.")
                        st.code(detalhe)

                ok_chat, detalhe_chat = enviar_google_chat(
                    f"✅ *Chamado atualizado*\n\n"
                    f"Protocolo: {chamado.get('protocolo', '')}\n"
                    f"Novo status: {novo_status}\n"
                    f"Responsável: {responsavel}\n"
                    f"Observação: {observacoes}"
                )

                if ok_chat:
                    st.success("Aviso enviado ao Google Chat.")
                else:
                    st.warning("Chamado atualizado, mas não foi possível avisar no Google Chat.")
                    st.code(detalhe_chat)

            st.markdown('<div class="section-title">Histórico do Chamado</div>', unsafe_allow_html=True)

            try:
                hist = supabase.table("historico_chamados_legalone") \
                    .select("*") \
                    .eq("chamado_id", int(chamado["id"])) \
                    .order("criado_em", desc=True) \
                    .limit(5) \
                    .execute()

                for h in hist.data or []:
                    st.markdown(
                        f"""
                        <div class="timeline-item">
                            <b>{formatar_data(h.get('criado_em',''))}</b><br>
                            {h.get('usuario','')} - Status: {h.get('status','')}<br>
                            <small>{h.get('observacao','')}</small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            except Exception:
                st.caption("Histórico indisponível.")

            st.markdown('<div class="section-title">Ações rápidas</div>', unsafe_allow_html=True)
            qa1, qa2, qa3 = st.columns(3)
            with qa1:
                st.button("📊 Relatórios", use_container_width=True)
            with qa2:
                st.button("📺 Dashboard TV 55”", use_container_width=True)
            with qa3:
                st.button("⚙️ Configurações", use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)


# =========================
# TV OPERACIONAL V3
# =========================

elif menu == "TV Operacional":
    st_autorefresh(interval=30000, key="tv_refresh_v2")

    df = carregar_chamados()
    df = aplicar_permissao_chamados(df, usuario)

    st.markdown('<div class="tv-bg">', unsafe_allow_html=True)

    agora_tela = datetime.now().strftime("%d/%m/%Y %H:%M")

    st.markdown(
        f"""
        <div class="tv-header">
            <div>
                <div class="tv-live">● AO VIVO</div>
                <div class="tv-title">TV OPERACIONAL - V360 LEGALONE</div>
            </div>
            <div style="font-size:22px;font-weight:900;">{agora_tela}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if df.empty:
        st.info("Nenhum chamado encontrado.")
    else:
        df["criado_em"] = pd.to_datetime(df["criado_em"], errors="coerce", utc=True)
        df["sla"] = df.apply(calcular_sla, axis=1)

        abertos = len(df[df["status"] == "Aberto"])
        andamento = len(df[df["status"] == "Em andamento"])
        atrasados = len(df[df["sla"] == "Atrasado"])
        finalizados = len(df[df["status"] == "Finalizado"])

        c1, c2, c3, c4 = st.columns(4)

        tvs = [
            (c1, abertos, "ABERTOS", "#f97316"),
            (c2, andamento, "EM ANDAMENTO", "#7c3aed"),
            (c3, atrasados, "ATRASADOS (SLA)", "#ef4444"),
            (c4, finalizados, "FINALIZADOS", "#22c55e")
        ]

        for col, num, label, cor in tvs:
            with col:
                st.markdown(
                    f"""
                    <div class="tv-card">
                        <div class="tv-number" style="color:{cor};">{num}</div>
                        <div class="tv-label">{label}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown('<div class="tv-table">', unsafe_allow_html=True)
        st.markdown("### Últimos chamados")

        colunas_tv = [
            "protocolo",
            "unidade",
            "setor",
            "descricao",
            "prioridade",
            "status",
            "sla",
            "responsavel",
            "criado_em"
        ]

        colunas_existentes = [c for c in colunas_tv if c in df.columns]
        tv_df = df[colunas_existentes].head(10).copy()

        st.dataframe(
            tv_df,
            use_container_width=True,
            hide_index=True
        )

        st.caption("Atualização automática a cada 30 segundos")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# RELATÓRIOS
# =========================

elif menu == "Relatórios":
    st.markdown('<div class="main-title">Relatórios</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Analise e exporte os chamados do sistema.</div>', unsafe_allow_html=True)

    df = carregar_chamados()
    df = aplicar_permissao_chamados(df, usuario)

    if df.empty:
        st.info("Nenhum chamado encontrado.")
    else:
        df["criado_em"] = pd.to_datetime(df["criado_em"], errors="coerce", utc=True)
        df["sla"] = df.apply(calcular_sla, axis=1)
        df["data"] = df["criado_em"].dt.date

        with st.expander("Filtros", expanded=True):
            c1, c2, c3 = st.columns(3)

            with c1:
                data_inicio = st.date_input("Data inicial", value=df["data"].min())

            with c2:
                data_fim = st.date_input("Data final", value=df["data"].max())

            with c3:
                status_filtro = st.multiselect(
                    "Status",
                    sorted(df["status"].dropna().unique()),
                    default=list(df["status"].dropna().unique())
                )

            c4, c5, c6 = st.columns(3)

            with c4:
                setor_filtro = st.multiselect(
                    "Setor",
                    sorted(df["setor"].dropna().unique()),
                    default=list(df["setor"].dropna().unique())
                )

            with c5:
                unidade_filtro = st.multiselect(
                    "Unidade",
                    sorted(df["unidade"].dropna().unique()),
                    default=list(df["unidade"].dropna().unique())
                )

            with c6:
                prioridade_filtro = st.multiselect(
                    "Prioridade",
                    sorted(df["prioridade"].dropna().unique()),
                    default=list(df["prioridade"].dropna().unique())
                )

        df_relatorio = df[
            (df["data"] >= data_inicio) &
            (df["data"] <= data_fim) &
            (df["status"].isin(status_filtro)) &
            (df["setor"].isin(setor_filtro)) &
            (df["unidade"].isin(unidade_filtro)) &
            (df["prioridade"].isin(prioridade_filtro))
        ]

        st.dataframe(df_relatorio, use_container_width=True, hide_index=True)

        csv = df_relatorio.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="⬇️ Baixar relatório em Excel/CSV",
            data=csv,
            file_name="relatorio_chamados.csv",
            mime="text/csv"
        )


# =========================
# GERENCIAR USUÁRIOS
# =========================

elif menu == "Gerenciar Usuários":
    st.markdown('<div class="main-title">Gerenciar Usuários</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Cadastre, edite e desative usuários do sistema.</div>', unsafe_allow_html=True)

    if usuario["perfil"] != "Administrador":
        st.error("Acesso negado.")
        st.stop()

    aba1, aba2 = st.tabs(["➕ Cadastrar usuário", "✏️ Editar usuário existente"])

    with aba1:
        col_form, col_lista = st.columns([1, 1.4])

        with col_form:
            st.markdown('<div class="detail-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Novo usuário</div>', unsafe_allow_html=True)

            with st.form("form_usuario"):
                nome = st.text_input("Nome")
                email = st.text_input("E-mail")
                senha = st.text_input("Senha", type="password")

                perfil = st.selectbox(
                    "Perfil",
                    ["Colaborador", "Gestor", "Diretoria", "Administrador", "TV"]
                )

                setor = st.selectbox(
                    "Setor",
                    ["LegalOne"]
                )

                unidades_novo_usuario = opcoes_unidade("LegalOne")
                unidade = st.selectbox(
                    "Unidade",
                    unidades_novo_usuario,
                    index=indice_unidade(unidades_novo_usuario, "LegalOne")
                )

                salvar_usuario = st.form_submit_button("Cadastrar usuário", use_container_width=True)

                if salvar_usuario:
                    if not nome or not email or not senha:
                        st.error("Preencha nome, e-mail e senha.")
                    else:
                        dados_insert = {
                            "nome": nome,
                            "email": email,
                            "senha": gerar_hash_senha(senha),
                            "perfil": perfil,
                            "setor": setor,
                            "unidade": unidade
                        }

                        try:
                            supabase.table("usuarios_legalone").insert(dados_insert).execute()
                            st.success("Usuário cadastrado com sucesso.")
                            st.rerun()
                        except Exception as e:
                            st.error("Erro ao cadastrar usuário.")
                            st.code(str(e))

            st.markdown('</div>', unsafe_allow_html=True)

        with col_lista:
            st.markdown('<div class="detail-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Usuários cadastrados</div>', unsafe_allow_html=True)

            usuarios = supabase.table("usuarios_legalone") \
                .select("*") \
                .order("nome") \
                .execute()

            df_usuarios = pd.DataFrame(usuarios.data or [])

            if df_usuarios.empty:
                st.info("Nenhum usuário encontrado.")
            else:
                colunas_user = [
                    "nome",
                    "email",
                    "perfil",
                    "setor",
                    "unidade",
                    "criado_em"
                ]

                st.dataframe(
                    df_usuarios[[c for c in colunas_user if c in df_usuarios.columns]],
                    use_container_width=True,
                    hide_index=True
                )

            st.markdown('</div>', unsafe_allow_html=True)

    with aba2:
        st.markdown('<div class="detail-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Editar usuário existente</div>', unsafe_allow_html=True)

        usuarios = supabase.table("usuarios_legalone") \
            .select("*") \
            .order("nome") \
            .execute()

        df_edit = pd.DataFrame(usuarios.data or [])

        if df_edit.empty:
            st.info("Nenhum usuário encontrado para editar.")
        else:
            df_edit["opcao"] = df_edit["nome"].fillna("") + " - " + df_edit["email"].fillna("")

            usuario_opcao = st.selectbox(
                "Selecione o usuário",
                df_edit["opcao"].tolist()
            )

            usuario_editado = df_edit[df_edit["opcao"] == usuario_opcao].iloc[0]

            with st.form("form_editar_usuario_legalone"):
                col1, col2 = st.columns(2)

                with col1:
                    novo_nome = st.text_input(
                        "Nome",
                        value=usuario_editado.get("nome", "")
                    )

                    novo_email = st.text_input(
                        "E-mail",
                        value=usuario_editado.get("email", "")
                    )

                    nova_senha = st.text_input(
                        "Nova senha",
                        type="password",
                        placeholder="Deixe em branco para manter a senha atual"
                    )

                with col2:
                    perfis = ["Colaborador", "Gestor", "Diretoria", "Administrador", "TV"]
                    perfil_atual = usuario_editado.get("perfil", "Colaborador")

                    if perfil_atual not in perfis:
                        perfil_atual = "Colaborador"

                    novo_perfil = st.selectbox(
                        "Perfil",
                        perfis,
                        index=perfis.index(perfil_atual)
                    )

                    setores = ["LegalOne"]
                    setor_atual = usuario_editado.get("setor", "LegalOne")

                    if setor_atual not in setores:
                        setores.append(setor_atual)

                    novo_setor = st.selectbox(
                        "Setor",
                        setores,
                        index=setores.index(setor_atual)
                    )

                    unidade_atual_edicao = usuario_editado.get("unidade", "LegalOne")
                    unidades_edicao = opcoes_unidade(unidade_atual_edicao)
                    nova_unidade = st.selectbox(
                        "Unidade",
                        unidades_edicao,
                        index=indice_unidade(unidades_edicao, unidade_atual_edicao)
                    )

                salvar_edicao = st.form_submit_button("💾 Salvar alterações", use_container_width=True)

                if salvar_edicao:
                    update = {
                        "nome": novo_nome,
                        "email": novo_email,
                        "perfil": novo_perfil,
                        "setor": novo_setor,
                        "unidade": nova_unidade
                    }

                    if nova_senha:
                        update["senha"] = gerar_hash_senha(nova_senha)

                    try:
                        supabase.table("usuarios_legalone") \
                            .update(update) \
                            .eq("id", int(usuario_editado["id"])) \
                            .execute()

                        st.success("Usuário atualizado com sucesso.")
                        st.rerun()

                    except Exception as e:
                        st.error("Erro ao atualizar usuário.")
                        st.code(str(e))

        st.markdown('</div>', unsafe_allow_html=True)
