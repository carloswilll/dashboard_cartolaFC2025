import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Cartola 2025", layout="wide")

# Carregar os dados
@st.cache_data
def carregar_dados():
    return pd.read_csv("scouts_jogadores.csv")

df = carregar_dados()

st.title("🏟️ Dashboard de Scouts - Cartola FC 2025")

# Filtros
col1, col2 = st.columns(2)
with col1:
    posicoes = df["Posição"].unique().tolist()
    posicao_selecionada = st.multiselect("Filtrar por Posição", posicoes, default=posicoes)

with col2:
    clubes = df["Clube"].unique().tolist()
    clube_selecionado = st.multiselect("Filtrar por Clube", clubes, default=clubes)

# Aplicar filtros
df_filtrado = df[
    (df["Posição"].isin(posicao_selecionada)) &
    (df["Clube"].isin(clube_selecionado))
].copy()

# Criar métrica de custo-benefício
df_filtrado["Custo-Benefício"] = df_filtrado["Pontos Média"] / df_filtrado["Preço (C$)"].replace(0, 0.1)

# Rankings
st.subheader("🏆 Top Jogadores")
col3, col4 = st.columns(2)

with col3:
    st.markdown("**Por Pontos Média**")
    st.dataframe(df_filtrado.sort_values("Pontos Média", ascending=False).head(10))

with col4:
    st.markdown("**Por Custo-Benefício**")
    st.dataframe(df_filtrado.sort_values("Custo-Benefício", ascending=False).head(10))

# Gráficos
st.subheader("📊 Distribuição dos Jogadores")
col5, col6 = st.columns(2)

with col5:
    fig = px.histogram(df_filtrado, x="Pontos Média", nbins=20, title="Distribuição da Média de Pontos")
    st.plotly_chart(fig, use_container_width=True)

with col6:
    fig = px.histogram(df_filtrado, x="Preço (C$)", nbins=20, title="Distribuição dos Preços")
    st.plotly_chart(fig, use_container_width=True)

# Tabela completa
st.subheader("📄 Tabela Completa dos Jogadores")
st.dataframe(df_filtrado.sort_values("Pontos Média", ascending=False), use_container_width=True)

st.subheader("🎯 Ranking Personalizado por Scout")

# Scouts disponíveis (abreviatura + nome completo)
scouts_dict = {
    "DS": "Desarmes (+1,5)",
    "G": "Gols (+8,0)",
    "A": "Assistências (+5,0)",
    "SG": "Saldo de Gols (+5,0)",
    "FS": "Faltas Sofridas (+0,5)",
    "FF": "Finalizações para Fora (+0,8)",
    "FD": "Finalizações Defendidas (+1,2)",
    "FT": "Finalizações na Trave (+3,0)",
    "PS": "Pênaltis Sofridos (+1,0)",
    "DE": "Defesas (+1,3)",
    "DP": "Defesas de Pênalti (+7,0)",
    "GC": "Gols Contra (-3,0)",
    "CV": "Cartões Vermelhos (-3,0)",
    "CA": "Cartões Amarelos (-1,0)",
    "GS": "Gols Sofridos (-1,0)",
    "PP": "Pênaltis Perdidos (-4,0)",
    "PC": "Pênaltis Cometidos (-1,0)",
    "FC": "Faltas Cometidas (-0,3)",
    "I": "Impedimentos (-0,1)",
}

# Seletores interativos
col_s1, col_s2 = st.columns(2)

with col_s1:
    scout_selecionado = st.selectbox("Escolha o Scout", list(scouts_dict.keys()), format_func=lambda x: scouts_dict[x])

with col_s2:
    posicoes_unicas = df_filtrado["Posição"].unique().tolist()
    posicao_ranking = st.selectbox("Escolha a Posição", posicoes_unicas)

# Filtrar dados válidos
df_scout = df_filtrado[df_filtrado["Posição"] == posicao_ranking].copy()
df_scout[scout_selecionado] = df_scout[scout_selecionado].fillna(0)

# Exibir ranking
st.markdown(f"**Top 10 {posicao_ranking} por {scouts_dict[scout_selecionado]}**")
st.dataframe(
    df_scout.sort_values(scout_selecionado, ascending=False)[["Nome", "Clube", scout_selecionado]].head(10),
    use_container_width=True
)


st.caption("Desenvolvido por Carlos Willian - Cartola FC 2025")
