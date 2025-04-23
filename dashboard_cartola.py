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
df["Preço (C$)"] = pd.to_numeric(df["Preço (C$)"], errors="coerce").fillna(0.0)
df["Pontos Média"] = pd.to_numeric(df["Pontos Média"], errors="coerce").fillna(0.0)
df["Custo-Benefício"] = df["Pontos Média"] / df["Preço (C$)"].replace(0, 0.1)

# 🎛️ SIDEBAR - Filtros com Ícones
with st.sidebar:
    st.header("🎛️ Filtros")

    posicoes = df["Posição"].unique().tolist()
    posicao_selecionada = st.multiselect("🧩 Posição", posicoes, default=posicoes)

    clubes = df["Clube"].unique().tolist()
    clube_selecionado = st.multiselect("🏳️ Clube", clubes, default=clubes)

    preco_min = st.slider("💰 Preço mínimo (C$)", float(df["Preço (C$)"].min()), float(df["Preço (C$)"].max()), 0.0)
    media_min = st.slider("📈 Pontos Média mínima", float(df["Pontos Média"].min()), float(df["Pontos Média"].max()), 0.0)

# 📊 Aplicar Filtros
df_filtrado = df[
    (df["Posição"].isin(posicao_selecionada)) &
    (df["Clube"].isin(clube_selecionado)) &
    (df["Preço (C$)"] >= preco_min) &
    (df["Pontos Média"] >= media_min)
].copy()

df_filtrado["Custo-Benefício"] = df_filtrado["Pontos Média"] / df_filtrado["Preço (C$)"].replace(0, 0.1)

# 🏆 Título
st.title("⚽ Top Jogadores - Cartola FC 2025")
st.markdown("Visualize os melhores jogadores da rodada com base em pontuação e custo-benefício.")

# 🔢 Painéis de Estatísticas
col_a, col_b, col_c, col_d = st.columns(4)

col_a.metric("📋 Jogadores filtrados", len(df_filtrado))
col_b.metric("🪙 Preço médio (C$)", f"{df_filtrado['Preço (C$)'].mean():.2f}")
col_c.metric("📊 Pontuação média", f"{df_filtrado['Pontos Média'].mean():.2f}")
col_d.metric("💸 Custo-Benefício médio", f"{df_filtrado['Custo-Benefício'].mean():.2f}")

# 🔝 Destaques
st.markdown("---")
st.subheader("🏅 Destaques da Rodada")
col1, col2 = st.columns(2)

with col1:
    st.markdown("🔝 **Top 10 por Pontos Média**")
    st.dataframe(df_filtrado.sort_values("Pontos Média", ascending=False).head(10), use_container_width=True, height=300)

with col2:
    st.markdown("💸 **Top 10 por Custo-Benefício**")
    st.dataframe(df_filtrado.sort_values("Custo-Benefício", ascending=False).head(10), use_container_width=True, height=300)

# 📊 Gráfico de Dispersão
st.markdown("---")
st.subheader("📊 Relação entre Preço e Pontos")
fig = px.scatter(
    df_filtrado,
    x="Preço (C$)",
    y="Pontos Média",
    color="Clube",
    hover_name="Nome",
    size_max=15,
    color_discrete_sequence=px.colors.qualitative.Safe,
    labels={"Preço (C$)": "Preço (C$)", "Pontos Média": "Pontos Média"},
)
fig.update_traces(marker=dict(size=10, opacity=0.75))
fig.update_layout(height=600, title_font_size=20)
st.plotly_chart(fig, use_container_width=True)

# 🧍 Buscar Jogador
st.markdown("---")
st.subheader("📄 Lista Completa")
nome_jogador = st.text_input("🔍 Buscar por nome do jogador", placeholder="Ex: Pedro, Hulk, Gerson...")

if nome_jogador:
    df_filtrado = df_filtrado[df_filtrado["Nome"].str.contains(nome_jogador, case=False, na=False)]

st.dataframe(df_filtrado.sort_values("Pontos Média", ascending=False), use_container_width=True, height=400)

st.caption("Desenvolvido por Carlos Willian - Cartola FC 2025")

