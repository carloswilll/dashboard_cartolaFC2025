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
# Gráfico de Custo-Benefício

# Remover registros com valores ausentes nas colunas usadas no gráfico
df_cb = df_filtrado.dropna(subset=["Preço (C$)", "Pontos Média", "Custo-Benefício", "Nome"])

st.subheader("💸 Análise de Custo-Benefício")

fig_cb = px.scatter(
    df_cb,
    x="Preço (C$)",
    y="Pontos Média",
    size="Custo-Benefício",
    color="Custo-Benefício",
    hover_name="Nome",
    title="Custo-Benefício: Pontos por Cartoleta",
    size_max=15,
    color_continuous_scale="Viridis"
)

st.plotly_chart(fig_cb, use_container_width=True)



st.caption("Desenvolvido por Carlos Willian - Cartola FC 2025")
