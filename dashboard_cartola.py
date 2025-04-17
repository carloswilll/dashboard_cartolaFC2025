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

# Métricas adicionais
# 1. Relação entre Scouts e Pontos
scouts_colunas = [col for col in df.columns if col not in ["Nome", "Clube", "Posição", "Preço (C$)", "Pontos Média"]]
scout_escolhido = st.selectbox("Escolha um Scout para análise de correlação com Pontos Média:", scouts_colunas)

fig_cb = px.scatter(df_filtrado, x=scout_escolhido, y="Pontos Média", color="Posição",
                    title=f"Relação entre {scout_escolhido} e Pontos Média",
                    labels={scout_escolhido: scout_escolhido, "Pontos Média": "Pontos"})
st.plotly_chart(fig_cb, use_container_width=True)

# 2. Ranking por Eficiência em Scouts
st.markdown("### 🧠 Ranking por Eficiência nos Scouts")
scout_eficiencia = scout_escolhido

if scout_eficiencia in df_filtrado.columns:
    df_filtrado[f"Eficiência {scout_eficiencia}"] = df_filtrado["Pontos Média"] / df_filtrado[scout_eficiencia].replace(0, 0.1)
    st.dataframe(df_filtrado.sort_values(f"Eficiência {scout_eficiencia}", ascending=False)[["Nome", scout_eficiencia, "Pontos Média", f"Eficiência {scout_eficiencia}"]].head(10))

# 3. Projeção de Valorização
st.markdown("### 📉 Projeção de Valorização")
df_filtrado["Projeção Valorização"] = df_filtrado["Pontos Média"] * df_filtrado["Custo-Benefício"]
st.dataframe(df_filtrado.sort_values("Projeção Valorização", ascending=False)[["Nome", "Preço (C$)", "Pontos Média", "Custo-Benefício", "Projeção Valorização"]].head(10))

st.caption("Desenvolvido por Carlos Willian - Cartola FC 2025")



