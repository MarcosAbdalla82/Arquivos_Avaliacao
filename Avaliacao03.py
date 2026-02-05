#streamlit run app.py --server.port 8501

import streamlit as st
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import pandas as pd
import base64
import psycopg2

conexao = psycopg2.connect(
    host=st.secrets["db"]["host"],
    port=6543,  
    database=st.secrets["db"]["name"],
    user=st.secrets["db"]["user"],
    password=st.secrets["db"]["password"],
    sslmode="require"
)

st.set_page_config(
    page_title="Opiniômetro",
    page_icon="📈",
)

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

set_bg("Logo01.png")

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        background-color: #e8490f;  /* dark slate */
    }
    </style>
    """,
    unsafe_allow_html=True
)


#query = "SELECT name FROM sqlite_master WHERE type='table';"
#df_tabelas = pd.read_sql_query(query, conexao)
#print(df_tabelas)

def le_funcionarios():
    dados = pd.read_sql_query('''
    SELECT * FROM Funcionario
    ''', conexao)
    return dados

def le_avaliacoes():
    dados = pd.read_sql_query(
        """
        SELECT ID
        FROM Avaliacao
        ORDER BY ID DESC
        LIMIT 1
        """, conexao)
    return dados

Avas = le_avaliacoes()
Ult_ava = int(Avas.iloc[0]["id"])+1

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

funs = le_funcionarios()

IDs = list(funs['id'])
Nomes = list(funs['nome'])
Cargos = list(funs['cargo'])

#agora = datetime.now(timezone.utc).replace(tzinfo=None)
agora_utc = datetime.now(timezone.utc)
agora = agora_utc.astimezone(ZoneInfo("America/Sao_Paulo"))
data_formatada = agora.strftime("%d/%m/%Y - %H:%M")

st.markdown("""
    <style>
    /* Tamanho do rótulo principal (Label) */
    label[data-testid="stWidgetLabel"] > div {
        font-size: 22px;
    }
    
    /* Tamanho dos valores das opções (Labels abaixo do slider) */
    div[data-baseweb="slider"] div {
        font-size: 18px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Dicionário simulando um banco de dados de funcionários
funcionarios = {
    "João Silva": {
        "ID": 1,
        "foto": "1.png",
        "cargo": "Secretaria"
    },
    "Maria Souza": {
        "ID": 2,
        "foto": "2.png",
        "cargo": "Coordenação"
    }
}

# Configuração da Barra Lateral

st.sidebar.markdown('# **SENAI** SAT #')

st.sidebar.title("Identificação")

# Selectbox para escolher o funcionário
nome_selecionado = st.sidebar.selectbox("Selecione o funcionário:", Nomes)
indice = Nomes.index(nome_selecionado)
id_selecionado = IDs[indice]
cargo_selecionado = Cargos[indice]
foto_selecionado = str(id_selecionado)+'.png'

# Exibindo a foto e informações na sidebar
st.sidebar.image(foto_selecionado, width=100, caption=f"ID: {cargo_selecionado}")

# Corpo principal do sistema de notas
st.title(f"Avaliação de Atendimento: {nome_selecionado}")
# ... aqui entra o seu formulário de 0 a 5

FORM = st.form('Pesquisa de satisfação', clear_on_submit=True)
FORM.header('Avaliação do Funcionário')
FORM.text(f'Por favor avalie o/a {nome_selecionado} com uma nota de 1 a 5.')

FORM.subheader('Cordialidade e Empatia')
P1 = FORM.select_slider(
    "O funcionário foi educado e demonstrou interesse em resolver a sua questão?",
    options=[1,2,3,4,5],
    value=1
)
FORM.subheader('Clareza na comunicação')
P2 = FORM.select_slider(
    "As informações foram passadas de forma clara e objetiva?",
    options=[1,2,3,4,5],
    value=1
)
FORM.subheader('Agilidade')
P3 = FORM.select_slider(
    "O tempo de espera e a rapidez do funcionário foram satisfatórios",
    options=[1,2,3,4,5],
    value=1
)

FORM.header('Avaliação do Serviço')

FORM.subheader('Eficácia')
P4 = FORM.select_slider(
    "Seu problema ou dúvida foi totalmente resolvido?",
    options=[1,2,3,4,5],
    value=1
)
FORM.subheader('Facilidade do Processo')
P5 = FORM.select_slider(
    "Foi fácil realizar o seu procedimento ou solicitação?",
    options=[1,2,3,4,5],
    value=1
)

FORM.subheader('Dê sua opinião')
P7 = FORM.select_slider(
    "Em uma escala de 0 a 10, o quanto você recomendaria o Senai a um amigo?",
    options=[1,2,3,4,5,6,7,8,9,10],
    value=1
)
FORM.subheader('Queremos ouvir você!')
OPN = FORM.text_area('Comentários adicionais:')

st.header('O SENAI agradece a sua participação!')
st.header('Volte Sempre!')

bt1 = FORM.form_submit_button('Enviar')

if bt1:
    a = 1
    inserir_avaliacao(id_selecionado,P1,P2,P3,P4,P5,data_formatada)
    inserir_comentario(Ult_ava,OPN)

    inserir_nps(Ult_ava,P7)








