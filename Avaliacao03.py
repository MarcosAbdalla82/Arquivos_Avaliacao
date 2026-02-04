# streamlit run app.py --server.port 8501

import streamlit as st
from datetime import datetime
import pandas as pd
import base64
import psycopg2
import os

# -----------------------------
# Database connection
# -----------------------------
conexao = psycopg2.connect(
    host=st.secrets["db"]["host"],
    port=6543,
    database=st.secrets["db"]["name"],
    user=st.secrets["db"]["user"],
    password=st.secrets["db"]["password"],
    sslmode="require"
)

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Opiniômetro",
    page_icon="📈",
)

# -----------------------------
# Background image
# -----------------------------
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

def set_bg(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        section[data-testid="stMain"] {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-repeat: repeat-y;
            background-position: top center;
        }}

        .block-container {{
            background-color: rgba(255, 255, 255, 0.5);
            border-radius: 16px;
            padding: 2rem;
            margin-top: 1rem;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg(os.path.join(ASSETS_DIR, "Logo01.png"))

# -----------------------------
# Sidebar style
# -----------------------------
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        background-color: #e8490f;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Database readers
# -----------------------------
def le_funcionarios():
    return pd.read_sql_query(
        "SELECT id, nome, cargo FROM funcionario ORDER BY nome",
        conexao
    )

# -----------------------------
# Database writers
# -----------------------------
def inserir_avaliacao(id_funcionario, p1, p2, p3, p4, p5, data_hora):
    cur = conexao.cursor()
    cur.execute(
        """
        INSERT INTO avaliacao
        (id_funcionario, nota_p1, nota_p2, nota_p3, nota_p4, nota_p5, data_hora)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (id_funcionario, p1, p2, p3, p4, p5, data_hora)
    )
    novo_id = cur.fetchone()[0]
    conexao.commit()
    cur.close()
    return novo_id

def inserir_comentario(id_avaliacao, comentario):
    cur = conexao.cursor()
    cur.execute(
        """
        INSERT INTO comentario (id_avaliacao, comentario)
        VALUES (%s, %s)
        """,
        (id_avaliacao, comentario)
    )
    conexao.commit()
    cur.close()

def inserir_nps(id_avaliacao, nps):
    cur = conexao.cursor()
    cur.execute(
        """
        INSERT INTO nps (id_avaliacao, nps)
        VALUES (%s, %s)
        """,
        (id_avaliacao, nps)
    )
    conexao.commit()
    cur.close()

# -----------------------------
# Load employees
# -----------------------------
funs = le_funcionarios()

IDs = list(funs["id"])
Nomes = list(funs["nome"])
Cargos = list(funs["cargo"])

# -----------------------------
# Date/time
# -----------------------------
agora = datetime.now()
data_formatada = agora.strftime("%d/%m/%Y - %H:%M")

# -----------------------------
# UI styles
# -----------------------------
st.markdown(
    """
    <style>
    label[data-testid="stWidgetLabel"] > div {
        font-size: 22px;
    }
    div[data-baseweb="slider"] div {
        font-size: 18px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.markdown('# **SENAI** SAT #')
st.sidebar.title("Identificação")

nome_selecionado = st.sidebar.selectbox(
    "Selecione o funcionário:",
    Nomes
)

indice = Nomes.index(nome_selecionado)
id_selecionado = IDs[indice]
cargo_selecionado = Cargos[indice]

foto_path = os.path.join(ASSETS_DIR, f"{id_selecionado}.png")
if os.path.exists(foto_path):
    st.sidebar.image(foto_path, width=100, caption=f"{cargo_selecionado}")

# -----------------------------
# Main content
# -----------------------------
st.title(f"Avaliação de Atendimento: {nome_selecionado}")

FORM = st.form("Pesquisa de satisfação", clear_on_submit=True)
FORM.header("Avaliação do Funcionário")
FORM.text(f"Por favor avalie o/a {nome_selecionado} com uma nota de 1 a 5.")

FORM.subheader("Cordialidade e Empatia")
P1 = FORM.select_slider(
    "O funcionário foi educado e demonstrou interesse em resolver a sua questão?",
    options=[1, 2, 3, 4, 5],
    value=1
)

FORM.subheader("Clareza na comunicação")
P2 = FORM.select_slider(
    "As informações foram passadas de forma clara e objetiva?",
    options=[1, 2, 3, 4, 5],
    value=1
)

FORM.subheader("Agilidade")
P3 = FORM.select_slider(
    "O tempo de espera e a rapidez do funcionário foram satisfatórios?",
    options=[1, 2, 3, 4, 5],
    value=1
)

FORM.header("Avaliação do Serviço")

FORM.subheader("Eficácia")
P4 = FORM.select_slider(
    "Seu problema ou dúvida foi totalmente resolvido?",
    options=[1, 2, 3, 4, 5],
    value=1
)

FORM.subheader("Facilidade do Processo")
P5 = FORM.select_slider(
    "Foi fácil realizar o seu procedimento ou solicitação?",
    options=[1, 2, 3, 4, 5],
    value=1
)

FORM.subheader("NPS")
P7 = FORM.select_slider(
    "Em uma escala de 0 a 10, o quanto você recomendaria o Senai a um amigo?",
    options=list(range(11)),
    value=5
)

FORM.subheader("Queremos ouvir você!")
OPN = FORM.text_area("Comentários adicionais:")

bt1 = FORM.form_submit_button("Enviar")

# -----------------------------
# Submit
# -----------------------------
if bt1:
    id_avaliacao = inserir_avaliacao(
        id_selecionado, P1, P2, P3, P4, P5, data_formatada
    )

    if OPN.strip():
        inserir_comentario(id_avaliacao, OPN)

    inserir_nps(id_avaliacao, P7)

    st.success("Avaliação registrada com sucesso! Obrigado 🙏")

st.header("O SENAI agradece a sua participação!")
st.header("Volte Sempre!")
