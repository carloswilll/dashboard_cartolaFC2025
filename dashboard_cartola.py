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

# Tabela completa com filtro de nome
st.subheader("📄 Tabela Completa dos Jogadores")

nome_jogador = st.text_input("🔍 Buscar jogador pelo nome")

if nome_jogador:
    df_filtrado = df_filtrado[df_filtrado["Nome"].str.contains(nome_jogador, case=False, na=False)]

st.dataframe(df_filtrado.sort_values("Pontos Média", ascending=False), use_container_width=True)

# Nova Métrica: Desempenho por Scout Específico por Posição
st.subheader("📌 Desempenho por Scout por Posição")
scouts_disponiveis = ['DS', 'G', 'A', 'SG', 'FS', 'FF', 'FD', 'FT', 'PS', 'DE', 'DP', 'GC', 'CV', 'CA', 'GS', 'PP', 'PC', 'FC', 'I']
scout_escolhido = st.selectbox("Escolha o Scout", scouts_disponiveis)

df_scout_posicao = df.groupby("Posição")[scout_escolhido].mean().reset_index()
fig_scout_posicao = px.bar(df_scout_posicao, x="Posição", y=scout_escolhido, color="Posição", title=f"Média de {scout_escolhido} por Posição")
st.plotly_chart(fig_scout_posicao, use_container_width=True)

# Nova Métrica: Análise por Perfil de Jogador
st.subheader("🔎 Análise por Perfil de Jogador")
perfil = st.selectbox("Escolha o perfil de jogador", ["Finalizadores", "Criadores", "Defensores"])

if perfil == "Finalizadores":
    scouts = ["G", "FF", "FD", "FT"]
elif perfil == "Criadores":
    scouts = ["A", "FS", "PS"]
else:
    scouts = ["DS", "SG", "DE", "DP"]

df["Soma Perfil"] = df[scouts].sum(axis=1)
st.dataframe(df.sort_values("Soma Perfil", ascending=False)[["Nome", "Posição", "Clube", "Soma Perfil"] + scouts].head(10), use_container_width=True)

# Nova Métrica: Simulador de Time Ideal com Cartoletas
st.subheader("📋 Simulador de Time Ideal com até 120 C$")
orcamento = 120
formacao = {"GOL": 1, "LAT": 2, "ZAG": 2, "MEI": 3, "ATA": 3}
time_ideal = pd.DataFrame()

for pos, qtd in formacao.items():
    jogadores_pos = df[df["Posição"] == pos].copy()
    jogadores_pos["Custo-Benefício"] = jogadores_pos["Pontos Média"] / jogadores_pos["Preço (C$)"].replace(0, 0.1)
    melhores = jogadores_pos.sort_values("Custo-Benefício", ascending=False).head(qtd)
    time_ideal = pd.concat([time_ideal, melhores])

if time_ideal["Preço (C$)"].sum() <= orcamento:
    st.success(f"💰 Total gasto: {time_ideal['Preço (C$)'].sum():.2f} C$")
else:
    st.warning(f"⚠️ Total acima do orçamento: {time_ideal['Preço (C$)'].sum():.2f} C$")

st.dataframe(time_ideal[["Nome", "Posição", "Clube", "Preço (C$)", "Pontos Média", "Custo-Benefício"]], use_container_width=True)

st.caption("Desenvolvido por Carlos Willian - Cartola FC 2025")



