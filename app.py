from streamlit_autorefresh import st_autorefresh
import streamlit as st
import pandas as pd
from supabase import create_client, Client
import plotly.express as px
from datetime import datetime, timezone, timedelta
import bcrypt
import requests

st.set_page_config(
    page_title="Painel de Chamados - Molina",
    layout="wide",
    page_icon="📋"
)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# FUNÇÕES
# =========================

def gerar_hash_senha(senha):
    return bcrypt.hashpw(
        senha.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verificar_senha(senha_digitada, senha_salva):
    if senha_salva and senha_salva.startswith("$2b$"):
        return bcrypt.checkpw(
            senha_digitada.encode("utf-8"),
            senha_salva.encode("utf-8")
        )

    return senha_digitada == senha_salva


def fazer_login(email, senha):
    response = supabase.table("usuarios_sistema") \
        .select("*") \
        .eq("email", email) \
        .eq("ativo", True) \
        .execute()

    if response.data:
        usuario = response.data[0]
        senha_salva = usuario.get("senha", "")

        if verificar_senha(senha, senha_salva):
            return usuario

    return None


def enviar_google_chat(mensagem):
    webhook_url = st.secrets.get("GOOGLE_CHAT_WEBHOOK", "")

    if not webhook_url:
        return

    try:
        requests.post(
            webhook_url,
            json={"text": mensagem},
            timeout=10
        )
    except Exception as e:
        print(f"Erro Google Chat: {e}")


def carregar_chamados():
    response = supabase.table("chamados_legalone") \
        .select("*") \
        .order("criado_em", desc=True) \
        .execute()

    return pd.DataFrame(response.data)


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


# =========================
# LOGIN
# =========================

if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = {}

if not st.session_state.logado:
    st.title("🔐 Login - Sistema de Chamados")

    with st.form("login_form"):
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar")

        if entrar:
            usuario_login = fazer_login(email, senha)

            if usuario_login:
                st.session_state.logado = True
                st.session_state.usuario = usuario_login
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

    st.stop()

usuario = st.session_state.usuario

# =========================
# SIDEBAR
# =========================

st.sidebar.title("📋 Chamados Molina")
st.sidebar.success(f"👤 {usuario['nome']}")
st.sidebar.write(f"Perfil: {usuario['perfil']}")

if st.sidebar.button("🚪 Sair"):
    st.session_state.logado = False
    st.session_state.usuario = {}
    st.rerun()

perfil_usuario = usuario["perfil"]

if perfil_usuario == "TV":
    opcoes_menu = ["TV Operacional"]

elif perfil_usuario == "Administrador":
    opcoes_menu = [
        "Abrir Chamado",
        "Painel Geral",
        "TV Operacional",
        "Relatórios",
        "Atualizar Chamado",
        "Gerenciar Usuários"
    ]

elif perfil_usuario == "Gestor":
    opcoes_menu = [
        "Abrir Chamado",
        "Painel Geral",
        "Relatórios",
        "Atualizar Chamado"
    ]

elif perfil_usuario == "Colaborador":
    opcoes_menu = [
        "Abrir Chamado",
        "Painel Geral"
    ]

else:
    opcoes_menu = [
        "Abrir Chamado",
        "Painel Geral"
    ]

query_params = st.query_params

modo_tv = query_params.get("tv", "0") == "1"

if modo_tv and perfil_usuario in ["Administrador", "Diretoria", "TV"]:
    menu = "TV Operacional"
else:
    menu = st.sidebar.radio("Menu", opcoes_menu)

if modo_tv:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="stAppViewContainer"] {
        margin-left: 0;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================
# ABRIR CHAMADO
# =========================

if menu == "Abrir Chamado":
    st.title("➕ Abrir Novo Chamado")

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

            unidade = st.text_input(
                "Unidade",
                value=usuario.get("unidade") or ""
            )

        with col2:
            setor = st.selectbox(
                "Setor responsável",
                [
                    "TI",
                    "RH",
                    "Financeiro",
                    "Jurídico",
                    "Atendimento",
                    "Protocolo",
                    "Marketing",
                    "Estrutura",
                    "Diretoria"
                ]
            )

            categoria = st.text_input("Categoria")

            prioridade = st.selectbox(
                "Prioridade",
                ["Baixa", "Média", "Alta", "Urgente"]
            )

        descricao = st.text_area(
            "Descrição do chamado",
            height=150
        )

        enviar = st.form_submit_button("✅ Abrir chamado")

        if enviar:
            if not descricao:
                st.error("Descreva o chamado.")
            else:
                dados = {
                    "solicitante": solicitante,
                    "email_solicitante": email_solicitante,
                    "unidade": unidade,
                    "setor": setor,
                    "categoria": categoria,
                    "prioridade": prioridade,
                    "descricao": descricao,
                    "status": "Aberto"
                }

                result = supabase.table("chamados_legalone") \
                    .insert(dados) \
                    .execute()

                chamado_id = result.data[0]["id"]
                protocolo = criar_protocolo(chamado_id)

                supabase.table("chamados_legalone") \
                    .update({"protocolo": protocolo}) \
                    .eq("id", chamado_id) \
                    .execute()

                st.success(f"Chamado criado com sucesso! {protocolo}")

                enviar_google_chat(
                    f"🚨 *Novo chamado aberto*\n\n"
                    f"Protocolo: {protocolo}\n"
                    f"Solicitante: {solicitante}\n"
                    f"Unidade: {unidade}\n"
                    f"Setor: {setor}\n"
                    f"Prioridade: {prioridade}\n"
                    f"Descrição: {descricao}"
                )

# =========================
# PAINEL GERAL
# =========================

elif menu == "Painel Geral":

    st.title("📊 Painel Geral")

    df = carregar_chamados()

    df = aplicar_permissao_chamados(df, usuario)

    if df.empty:
        st.info("Nenhum chamado encontrado.")

    else:

        df["criado_em"] = pd.to_datetime(
            df["criado_em"],
            errors="coerce",
            utc=True
        )

        df["sla"] = df.apply(calcular_sla, axis=1)

        total = len(df)

        abertos = len(
            df[df["status"] == "Aberto"]
        )

        andamento = len(
            df[df["status"] == "Em andamento"]
        )

        finalizados = len(
            df[df["status"] == "Finalizado"]
        )

        urgentes = len(
            df[df["prioridade"] == "Urgente"]
        )

        atrasados = len(
            df[df["sla"] == "Atrasado"]
        )

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        col1.metric("Abertos", abertos)
        col2.metric("Andamento", andamento)
        col3.metric("Urgentes", urgentes)
        col4.metric("Atrasados", atrasados)
        col5.metric("Finalizados", finalizados)
        col6.metric("Total", total)

        st.divider()

        colg1, colg2 = st.columns(2)

        with colg1:

            fig_status = px.pie(
                df,
                names="status",
                title="Chamados por Status"
            )

            st.plotly_chart(
                fig_status,
                use_container_width=True
            )

        with colg2:

            fig_prioridade = px.bar(
                df.groupby("prioridade")
                .size()
                .reset_index(name="quantidade"),
                x="prioridade",
                y="quantidade",
                text="quantidade",
                title="Chamados por Prioridade"
            )

            st.plotly_chart(
                fig_prioridade,
                use_container_width=True
            )

        st.subheader("Lista de chamados")

        colunas = [
            "protocolo",
            "status",
            "prioridade",
            "sla",
            "unidade",
            "setor",
            "categoria",
            "solicitante",
            "responsavel",
            "descricao",
            "criado_em"
        ]

        colunas_existentes = [
            c for c in colunas if c in df.columns
        ]

        st.dataframe(
            df[colunas_existentes],
            use_container_width=True,
            hide_index=True
        )

# =========================
# TV OPERACIONAL
# =========================

elif menu == "TV Operacional":

    st_autorefresh(interval=30000, key="tv_refresh")

    st.markdown("""
    <style>
    .main {
        background: #0f172a;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    .tv-header {
        background: linear-gradient(90deg, #111827, #1e293b);
        color: white;
        padding: 24px;
        border-radius: 22px;
        margin-bottom: 22px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.35);
    }
    .tv-title {
        font-size: 50px;
        font-weight: 900;
        letter-spacing: 1px;
    }
    .tv-subtitle {
        font-size: 24px;
        color: #cbd5e1;
        margin-top: 8px;
        font-weight: 700;
    }
    .tv-card {
        padding: 24px;
        border-radius: 22px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.35);
        margin-bottom: 18px;
    }
    .tv-number {
        font-size: 60px;
        font-weight: 900;
        line-height: 1;
    }
    .tv-label {
        font-size: 22px;
        margin-top: 10px;
        font-weight: 800;
    }
    .card-total {background: linear-gradient(135deg, #2563eb, #1e40af);}
    .card-abertos {background: linear-gradient(135deg, #f97316, #c2410c);}
    .card-andamento {background: linear-gradient(135deg, #eab308, #a16207);}
    .card-urgentes {background: linear-gradient(135deg, #dc2626, #991b1b);}
    .card-atrasados {
        background: linear-gradient(135deg, #7f1d1d, #450a0a);
        animation: pulse 1.4s infinite;
    }
    .card-finalizados {background: linear-gradient(135deg, #16a34a, #166534);}
    @keyframes pulse {
        0% {transform: scale(1);}
        50% {transform: scale(1.03);}
        100% {transform: scale(1);}
    }
    .section-title {
        color: white;
        font-size: 32px;
        font-weight: 900;
        margin-top: 16px;
        margin-bottom: 12px;
    }
    .alert-card {
        background: #fee2e2;
        color: #111827;
        padding: 18px;
        border-radius: 16px;
        margin-bottom: 12px;
        border-left: 10px solid #dc2626;
        font-size: 20px;
        font-weight: 700;
        box-shadow: 0 6px 18px rgba(0,0,0,0.25);
    }
    .ok-card {
        background: #dcfce7;
        color: #14532d;
        padding: 22px;
        border-radius: 16px;
        font-size: 24px;
        font-weight: 900;
        text-align: center;
    }
    .last-card {
        background: #ffffff;
        color: #111827;
        padding: 14px;
        border-radius: 14px;
        margin-bottom: 10px;
        font-size: 18px;
        font-weight: 700;
        border-left: 8px solid #2563eb;
    }
    </style>
    """, unsafe_allow_html=True)

    agora_tela = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    st.markdown(f"""
    <div class="tv-header">
        <div class="tv-title">CENTRAL DE CHAMADOS MOLINA ADVOGADOS</div>
        <div class="tv-subtitle">Atualização automática a cada 30 segundos • {agora_tela}</div>
    </div>
    """, unsafe_allow_html=True)

    df = carregar_chamados()
    df = aplicar_permissao_chamados(df, usuario)

    if df.empty:
        st.markdown("""
        <div class="ok-card">
            Nenhum chamado encontrado no momento.
        </div>
        """, unsafe_allow_html=True)

    else:
        df["criado_em"] = pd.to_datetime(
            df["criado_em"],
            errors="coerce",
            utc=True
        )

        df["sla"] = df.apply(calcular_sla, axis=1)

        abertos = len(df[df["status"] == "Aberto"])
        andamento = len(df[df["status"] == "Em andamento"])
        finalizados = len(df[df["status"] == "Finalizado"])
        urgentes = len(df[df["prioridade"] == "Urgente"])
        atrasados = len(df[df["sla"] == "Atrasado"])
        total = len(df)

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            st.markdown(f"""
            <div class="tv-card card-abertos">
                <div class="tv-number">{abertos}</div>
                <div class="tv-label">Abertos</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="tv-card card-andamento">
                <div class="tv-number">{andamento}</div>
                <div class="tv-label">Em andamento</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="tv-card card-urgentes">
                <div class="tv-number">{urgentes}</div>
                <div class="tv-label">Urgentes</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="tv-card card-atrasados">
                <div class="tv-number">{atrasados}</div>
                <div class="tv-label">Atrasados</div>
            </div>
            """, unsafe_allow_html=True)

        with col5:
            st.markdown(f"""
            <div class="tv-card card-finalizados">
                <div class="tv-number">{finalizados}</div>
                <div class="tv-label">Finalizados</div>
            </div>
            """, unsafe_allow_html=True)

        with col6:
            st.markdown(f"""
            <div class="tv-card card-total">
                <div class="tv-number">{total}</div>
                <div class="tv-label">Total</div>
            </div>
            """, unsafe_allow_html=True)

        colg1, colg2 = st.columns(2)

        with colg1:
            st.markdown(
                '<div class="section-title">🏢 Ranking por Setor</div>',
                unsafe_allow_html=True
            )

            ranking_setor = (
                df.groupby("setor")
                .size()
                .reset_index(name="quantidade")
                .sort_values("quantidade", ascending=False)
                .head(8)
            )

            fig_setor = px.bar(
                ranking_setor,
                x="setor",
                y="quantidade",
                text="quantidade"
            )

            fig_setor.update_layout(
                paper_bgcolor="#0f172a",
                plot_bgcolor="#0f172a",
                font=dict(color="white", size=24),
                title_font=dict(size=32),
                xaxis=dict(
                    title_font=dict(size=26),
                    tickfont=dict(size=24)
                ),
                yaxis=dict(
                    title_font=dict(size=26),
                    tickfont=dict(size=24)
                ),
                height=430
            )

            fig_setor.update_traces(
                textfont_size=30,
                textfont_color="white",
                textposition="outside"
            )

            st.plotly_chart(
                fig_setor,
                use_container_width=True
            )

        with colg2:
            st.markdown(
                '<div class="section-title">📍 Ranking por Unidade</div>',
                unsafe_allow_html=True
            )

            ranking_unidade = (
                df.groupby("unidade")
                .size()
                .reset_index(name="quantidade")
                .sort_values("quantidade", ascending=False)
                .head(8)
            )

            fig_unidade = px.bar(
                ranking_unidade,
                x="unidade",
                y="quantidade",
                text="quantidade"
            )

            fig_unidade.update_layout(
                paper_bgcolor="#0f172a",
                plot_bgcolor="#0f172a",
                font=dict(color="white", size=24),
                title_font=dict(size=32),
                xaxis=dict(
                    title_font=dict(size=26),
                    tickfont=dict(size=24)
                ),
                yaxis=dict(
                    title_font=dict(size=26),
                    tickfont=dict(size=24)
                ),
                height=430
            )

            fig_unidade.update_traces(
                textfont_size=30,
                textfont_color="white",
                textposition="outside"
            )

            st.plotly_chart(
                fig_unidade,
                use_container_width=True
            )

        colc1, colc2 = st.columns(2)

        with colc1:
            st.markdown(
                '<div class="section-title">🚨 Chamados Críticos</div>',
                unsafe_allow_html=True
            )

            df_criticos = df[
                (df["sla"] == "Atrasado") |
                (df["prioridade"] == "Urgente")
            ].head(6)

            if df_criticos.empty:
                st.markdown("""
                <div class="ok-card">
                    Nenhum chamado crítico no momento.
                </div>
                """, unsafe_allow_html=True)
            else:
                for _, row in df_criticos.iterrows():
                    st.markdown(f"""
                    <div class="alert-card">
                        <b>{row.get("protocolo", "")}</b> • {row.get("prioridade", "")} • {row.get("sla", "")}<br>
                        <b>Setor:</b> {row.get("setor", "")} |
                        <b>Unidade:</b> {row.get("unidade", "")}<br>
                        <b>Descrição:</b> {row.get("descricao", "")}
                    </div>
                    """, unsafe_allow_html=True)

        with colc2:
            st.markdown(
                '<div class="section-title">🕒 Últimos Chamados</div>',
                unsafe_allow_html=True
            )

            ultimos = df.head(6)

            for _, row in ultimos.iterrows():
                st.markdown(f"""
                <div class="last-card">
                    <b>{row.get("protocolo", "")}</b> • {row.get("status", "")} • {row.get("prioridade", "")}<br>
                    <b>{row.get("setor", "")}</b> - {row.get("unidade", "")}<br>
                    {row.get("descricao", "")}
                </div>
                """, unsafe_allow_html=True)

# =========================
# RELATÓRIOS
# =========================

elif menu == "Relatórios":

    st.title("📄 Relatórios de Chamados")

    df = carregar_chamados()
    df = aplicar_permissao_chamados(df, usuario)

    if df.empty:
        st.info("Nenhum chamado encontrado.")
    else:
        df["criado_em"] = pd.to_datetime(
            df["criado_em"],
            errors="coerce",
            utc=True
        )

        df["sla"] = df.apply(calcular_sla, axis=1)
        df["data"] = df["criado_em"].dt.date

        st.subheader("Filtros do relatório")

        col1, col2, col3 = st.columns(3)

        with col1:
            data_inicio = st.date_input(
                "Data inicial",
                value=df["data"].min()
            )

        with col2:
            data_fim = st.date_input(
                "Data final",
                value=df["data"].max()
            )

        with col3:
            status_filtro = st.multiselect(
                "Status",
                sorted(df["status"].dropna().unique()),
                default=list(df["status"].dropna().unique())
            )

        col4, col5, col6 = st.columns(3)

        with col4:
            setor_filtro = st.multiselect(
                "Setor",
                sorted(df["setor"].dropna().unique()),
                default=list(df["setor"].dropna().unique())
            )

        with col5:
            unidade_filtro = st.multiselect(
                "Unidade",
                sorted(df["unidade"].dropna().unique()),
                default=list(df["unidade"].dropna().unique())
            )

        with col6:
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

        st.divider()

        total = len(df_relatorio)
        abertos = len(df_relatorio[df_relatorio["status"] == "Aberto"])
        andamento = len(df_relatorio[df_relatorio["status"] == "Em andamento"])
        finalizados = len(df_relatorio[df_relatorio["status"] == "Finalizado"])
        atrasados = len(df_relatorio[df_relatorio["sla"] == "Atrasado"])
        urgentes = len(df_relatorio[df_relatorio["prioridade"] == "Urgente"])

        c1, c2, c3, c4, c5, c6 = st.columns(6)

        c1.metric("Total", total)
        c2.metric("Abertos", abertos)
        c3.metric("Andamento", andamento)
        c4.metric("Finalizados", finalizados)
        c5.metric("Atrasados", atrasados)
        c6.metric("Urgentes", urgentes)

        st.divider()

        st.subheader("Resumo por setor")

        if not df_relatorio.empty:
            resumo_setor = (
                df_relatorio.groupby("setor")
                .size()
                .reset_index(name="quantidade")
                .sort_values("quantidade", ascending=False)
            )

            st.dataframe(
                resumo_setor,
                use_container_width=True,
                hide_index=True
            )

            st.subheader("Resumo por unidade")

            resumo_unidade = (
                df_relatorio.groupby("unidade")
                .size()
                .reset_index(name="quantidade")
                .sort_values("quantidade", ascending=False)
            )

            st.dataframe(
                resumo_unidade,
                use_container_width=True,
                hide_index=True
            )

            st.subheader("Chamados do relatório")

            colunas_relatorio = [
                "protocolo",
                "status",
                "prioridade",
                "sla",
                "unidade",
                "setor",
                "categoria",
                "solicitante",
                "responsavel",
                "descricao",
                "criado_em",
                "finalizado_em"
            ]

            colunas_existentes = [
                c for c in colunas_relatorio if c in df_relatorio.columns
            ]

            st.dataframe(
                df_relatorio[colunas_existentes],
                use_container_width=True,
                hide_index=True
            )

            csv = df_relatorio[colunas_existentes].to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                label="⬇️ Baixar relatório em Excel/CSV",
                data=csv,
                file_name="relatorio_chamados.csv",
                mime="text/csv"
            )

        else:
            st.warning("Nenhum chamado encontrado com os filtros selecionados.")

# =========================
# ATUALIZAR CHAMADO
# =========================

elif menu == "Atualizar Chamado":
    st.title("✏️ Atualizar Chamado")

    df = carregar_chamados()
    df = aplicar_permissao_chamados(df, usuario)

    if df.empty:
        st.info("Nenhum chamado encontrado.")
    else:
        df["opcao"] = (
            df["protocolo"].fillna(df["id"].astype(str))
            + " - "
            + df["descricao"].fillna("").str[:50]
        )

        opcao = st.selectbox(
            "Selecione o chamado",
            df["opcao"].tolist()
        )

        chamado = df[df["opcao"] == opcao].iloc[0]

        st.info(f"Descrição: {chamado.get('descricao', '')}")

        novo_status = st.selectbox(
            "Novo status",
            [
                "Aberto",
                "Em andamento",
                "Aguardando",
                "Finalizado",
                "Cancelado"
            ]
        )

        responsavel = st.text_input(
            "Responsável",
            value=chamado.get("responsavel") or ""
        )

        observacoes = st.text_area(
            "Observações",
            value=chamado.get("observacoes") or ""
        )

        if st.button("💾 Salvar alteração"):
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

            supabase.table("historico_chamados") \
                .insert({
                    "chamado_id": int(chamado["id"]),
                    "acao": f"Status alterado para {novo_status}",
                    "usuario": responsavel or usuario["nome"],
                    "observacao": observacoes
                }) \
                .execute()

            st.success("Chamado atualizado.")

            enviar_google_chat(
                f"✅ *Chamado atualizado*\n\n"
                f"Protocolo: {chamado.get('protocolo', '')}\n"
                f"Novo status: {novo_status}\n"
                f"Responsável: {responsavel}\n"
                f"Observação: {observacoes}"
            )

# =========================
# GERENCIAR USUÁRIOS
# =========================

elif menu == "Gerenciar Usuários":
    st.title("👥 Gerenciar Usuários")

    if usuario["perfil"] != "Administrador":
        st.error("Acesso negado.")
        st.stop()

    st.subheader("Cadastrar novo usuário")

    with st.form("form_usuario"):
        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input("Nome")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")

        with col2:
            perfil = st.selectbox(
                "Perfil",
                ["Colaborador", "Gestor", "Diretoria", "Administrador", "TV"]
            )

            setor = st.selectbox(
                "Setor",
                [
                    "TI",
                    "RH",
                    "Financeiro",
                    "Jurídico",
                    "Atendimento",
                    "Protocolo",
                    "Marketing",
                    "Estrutura",
                    "Diretoria"
                ]
            )

            unidade = st.selectbox(
                "Unidade",
                [
                    "Atrium",
                    "Cidade Nova",
                    "Compensa",
                    "Manacapuru",
                    "Itacoatiara",
                    "Parintins",
                    "Humaitá",
                    "Online",
                    "Outro"
                ]
            )

        salvar_usuario = st.form_submit_button("✅ Cadastrar usuário")

        if salvar_usuario:
            if not nome or not email or not senha:
                st.error("Preencha nome, e-mail e senha.")
            else:
                supabase.table("usuarios_sistema").insert({
                    "nome": nome,
                    "email": email,
                    "senha": gerar_hash_senha(senha),
                    "perfil": perfil,
                    "setor": setor,
                    "unidade": unidade,
                    "ativo": True
                }).execute()

                st.success("Usuário cadastrado com sucesso.")

    st.divider()

    st.subheader("Usuários cadastrados")

    usuarios = supabase.table("usuarios_sistema") \
        .select("*") \
        .order("nome") \
        .execute()

    df_usuarios = pd.DataFrame(usuarios.data)

    if df_usuarios.empty:
        st.info("Nenhum usuário encontrado.")
    else:
        st.dataframe(
            df_usuarios[
                [
                    "nome",
                    "email",
                    "perfil",
                    "setor",
                    "unidade",
                    "ativo",
                    "criado_em"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.subheader("Editar / Desativar usuário")

    usuarios_edit = supabase.table("usuarios_sistema") \
        .select("*") \
        .order("nome") \
        .execute()

    df_edit = pd.DataFrame(usuarios_edit.data)

    if df_edit.empty:
        st.info("Nenhum usuário para editar.")
    else:
        df_edit["opcao"] = df_edit["nome"] + " - " + df_edit["email"]

        usuario_opcao = st.selectbox(
            "Selecione o usuário",
            df_edit["opcao"].tolist()
        )

        usuario_editado = df_edit[df_edit["opcao"] == usuario_opcao].iloc[0]

        with st.form("form_editar_usuario"):
            col1, col2 = st.columns(2)

            with col1:
                novo_nome = st.text_input(
                    "Nome",
                    value=usuario_editado["nome"]
                )

                novo_email = st.text_input(
                    "E-mail",
                    value=usuario_editado["email"]
                )

                nova_senha = st.text_input(
                    "Nova senha",
                    type="password",
                    placeholder="Deixe em branco para manter a senha atual"
                )

            with col2:
                perfis = ["Colaborador", "Gestor", "Diretoria", "Administrador", "TV"]

                novo_perfil = st.selectbox(
                    "Perfil",
                    perfis,
                    index=perfis.index(usuario_editado["perfil"])
                    if usuario_editado["perfil"] in perfis else 0
                )

                setores = [
                    "TI",
                    "RH",
                    "Financeiro",
                    "Jurídico",
                    "Atendimento",
                    "Protocolo",
                    "Marketing",
                    "Estrutura",
                    "Diretoria"
                ]

                novo_setor = st.selectbox(
                    "Setor",
                    setores,
                    index=setores.index(usuario_editado["setor"])
                    if usuario_editado["setor"] in setores else 0
                )

                unidades = [
                    "Atrium",
                    "Cidade Nova",
                    "Compensa",
                    "Manacapuru",
                    "Itacoatiara",
                    "Parintins",
                    "Humaitá",
                    "Online",
                    "Outro"
                ]

                nova_unidade = st.selectbox(
                    "Unidade",
                    unidades,
                    index=unidades.index(usuario_editado["unidade"])
                    if usuario_editado["unidade"] in unidades else 0
                )

                novo_ativo = st.checkbox(
                    "Usuário ativo",
                    value=bool(usuario_editado["ativo"])
                )

            salvar_edicao = st.form_submit_button("💾 Salvar alterações")

            if salvar_edicao:
                dados_update = {
                    "nome": novo_nome,
                    "email": novo_email,
                    "perfil": novo_perfil,
                    "setor": novo_setor,
                    "unidade": nova_unidade,
                    "ativo": novo_ativo
                }

                if nova_senha:
                    dados_update["senha"] = gerar_hash_senha(nova_senha)

                supabase.table("usuarios_sistema") \
                    .update(dados_update) \
                    .eq("id", int(usuario_editado["id"])) \
                    .execute()

                st.success("Usuário atualizado com sucesso.")
                st.rerun()
