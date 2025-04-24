import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Dashboard Cartola 2025", layout="wide")

# 🎨 Estilo customizado para roxo nos multiselects e modo escuro/claro
st.markdown("""
    <style>
    .stMultiSelect [data-baseweb="select"] span {
        background-color: #7e57c2 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# SIDEBAR
st.sidebar.title("⚙️ Filtros e Configurações")

# Filtro por posição
posicao_filtro = st.sidebar.multiselect("Filtrar por Posição", [], placeholder="Carregando posições...")

# Filtro por clube
clube_filtro = st.sidebar.multiselect("Filtrar por Clube", [], placeholder="Carregando clubes...")

# Filtros numéricos máximos
preco_max = st.sidebar.slider("Preço máximo (C$)", 0.0, 30.0, 30.0, step=0.1)
media_max = st.sidebar.slider("Média máxima de pontos", 0.0, 20.0, 20.0, step=0.1)

# Exibir horário da atualização
agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
st.sidebar.markdown(f"🕒 Dados atualizados em: `{agora}`")

# Carregar dados da API
@st.cache_data(show_spinner="Carregando dados da API...")
def carregar_dados_api():
    url_scouts = 'https://api.cartola.globo.com/atletas/mercado'
    res_scouts = requests.get(url_scouts).json()

    jogadores = res_scouts['atletas']
    clubes = res_scouts['clubes']
    posicoes = res_scouts['posicoes']

    scouts_data = []
    for jogador in jogadores:
        clube = clubes[str(jogador['clube_id'])]['nome']
        posicao = posicoes[str(jogador['posicao_id'])]['nome']
        scouts = jogador.get('scout', {})

        dados_jogador = {
            'Nome': jogador['apelido'],
            'Clube': clube,
            'Posição': posicao,
            'Preço (C$)': jogador['preco_num'],
            'Pontos Média': jogador['media_num'],
            'Partidas': jogador['jogos_num'],
        }
        dados_jogador.update(scouts)
        scouts_data.append(dados_jogador)

    df = pd.DataFrame(scouts_data)
    df.columns = df.columns.str.strip()
    return df.convert_dtypes().infer_objects()

# Título principal
df = None
st.title("🏟️ Dashboard de Scouts - Cartola FC 2025")
aba1 = st.container()

with aba1:
    df = carregar_dados_api()
    df["Preço (C$)"] = pd.to_numeric(df["Preço (C$)"], errors="coerce").fillna(0.0)
    df["Pontos Média"] = pd.to_numeric(df["Pontos Média"], errors="coerce").fillna(0.0)
    df["Custo-Benefício"] = df["Pontos Média"] / df["Preço (C$)"].replace(0, 0.1)

    # Atualiza opções dos filtros agora que os dados estão carregados
    st.sidebar.multiselect("Filtrar por Posição", df["Posição"].unique().tolist(), default=df["Posição"].unique().tolist(), key="pos_filtro")
    st.sidebar.multiselect("Filtrar por Clube", df["Clube"].unique().tolist(), default=df["Clube"].unique().tolist(), key="clube_filtro")

    # Atualização manual dos dados
    if st.sidebar.button("🔄 Atualizar Dados"):
        carregar_dados_api.clear()
        st.experimental_rerun()

    posicao_selecionada = st.session_state.get("pos_filtro", df["Posição"].unique().tolist())
    clube_selecionado = st.session_state.get("clube_filtro", df["Clube"].unique().tolist())

    df_filtrado = df[
        (df["Posição"].isin(posicao_selecionada)) &
        (df["Clube"].isin(clube_selecionado)) &
        (df["Preço (C$)"] <= preco_max) &
        (df["Pontos Média"] <= media_max)
    ].copy()

    df_filtrado["Custo-Benefício"] = df_filtrado["Pontos Média"] / df_filtrado["Preço (C$)"].replace(0, 0.1)

    st.subheader("🏆 Top Jogadores")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("**Por Pontos Média**")
        st.dataframe(df_filtrado.sort_values("Pontos Média", ascending=False).head(10))

    with col4:
        st.markdown("**Por Custo-Benefício**")
        st.dataframe(df_filtrado.sort_values("Custo-Benefício", ascending=False).head(10))


