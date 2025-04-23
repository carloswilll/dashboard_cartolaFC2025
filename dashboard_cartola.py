import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Top Jogadores - Cartola FC 2025", layout="wide")

@st.cache_data
def carregar_dados():
    df = pd.read_csv("scouts_jogadores.csv")
    df.columns = df.columns.str.strip()
    return df.convert_dtypes().infer_objects()

df = carregar_dados()

# Tratamento de dados
df["Preço (C$)"] = pd.to_numeric(df["Preço (C$)"], errors="coerce").fillna(0.0)
df["Pontos Média"] = pd.to_numeric(df["Pontos Média"], errors="coerce").fillna(0.0)
df["Custo-Benefício"] = df["Pontos Média"] / df["Preço (C$)"].replace(0, 0.1)

st.title("⚽ Top Jogadores - Cartola FC 2025")
st.markdown("Use os filtros abaixo para analisar os destaques por pontuação e custo-benefício.")

# Filtros
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        posicoes = df["Posição"].unique().tolist()
        posicao_selecionada = st.multiselect("📌 Filtrar por Posição", posicoes, default=posicoes)

    with col2:
        clubes = df["Clube"].unique().tolist()
        clube_selecionado = st.multiselect("🏳️ Filtrar por Clube", clubes, default=clubes)

df_filtrado = df[
    (df["Posição"].isin(posicao_selecionada)) &
    (df["Clube"].isin(clube_selecionado))
].copy()

df_filtrado["Custo-Benefício"] = df_filtrado["Pontos Média"] / df_filtrado["Preço (C$)"].replace(0, 0.1)

# Top 10
st.markdown("---")
st.subheader("🏅 Destaques da Rodada")
col3, col4 = st.columns(2)
with col3:
    st.markdown("🔝 **Top 10 por Pontos Média**")
    st.dataframe(df_filtrado.sort_values("Pontos Média", ascending=False).head(10), use_container_width=True, height=300)

with col4:
    st.markdown("💸 **Top 10 por Custo-Benefício**")
    st.dataframe(df_filtrado.sort_values("Custo-Benefício", ascending=False).head(10), use_container_width=True, height=300)

# Gráfico
st.markdown("---")
st.subheader("📊 Relação entre Preço e Pontos")
fig = px.scatter(
    df_filtrado,
    x="Preço (C$)",
    y="Pontos Média",
    color="Clube",
    hover_name="Nome",
    size_max=15,
    color_discrete_sequence=px.colors.qualitative.Safe,  # paleta suave
    labels={"Preço (C$)": "Preço (C$)", "Pontos Média": "Pontos Média"},
)
fig.update_traces(marker=dict(size=10, opacity=0.75))
fig.update_layout(height=600, title_font_size=20)
st.plotly_chart(fig, use_container_width=True)

# Tabela com filtro por nome
st.markdown("---")
st.subheader("📄 Lista de Jogadores")
nome_jogador = st.text_input("🔍 Digite parte do nome do jogador para buscar", placeholder="Ex: Pedro, Hulk, Gerson...")

if nome_jogador:
    df_filtrado = df_filtrado[df_filtrado["Nome"].str.contains(nome_jogador, case=False, na=False)]

st.dataframe(
    df_filtrado.sort_values("Pontos Média", ascending=False),
    use_container_width=True,
    height=400
)

st.caption("Desenvolvido por Carlos Willian - Cartola FC 2025")

