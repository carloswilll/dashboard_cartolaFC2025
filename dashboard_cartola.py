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

# Análise por perfil de jogador
st.subheader("👤 Análise por Perfil de Jogador")
perfil = st.selectbox("Escolha um perfil", ["Finalizadores", "Criadores", "Defensores"])

if perfil == "Finalizadores":
    st.dataframe(df_filtrado.sort_values("Finalizações", ascending=False).head(10))
elif perfil == "Criadores":
    st.dataframe(df_filtrado.sort_values("Assistência", ascending=False).head(10))
elif perfil == "Defensores":
    st.dataframe(df_filtrado.sort_values("Desarmes", ascending=False).head(10))

# Simulador de Time Ideal
st.subheader("🧮 Simulador de Time Ideal")
orçamento = st.number_input("Informe o valor disponível em cartoletas", min_value=10.0, max_value=200.0, value=120.0)

opcoes_formacao = {
    "4-3-3": {"GOL": 1, "ZAG": 2, "LAT": 2, "MEI": 3, "ATA": 3},
    "4-4-2": {"GOL": 1, "ZAG": 2, "LAT": 2, "MEI": 4, "ATA": 2},
    "3-5-2": {"GOL": 1, "ZAG": 3, "LAT": 0, "MEI": 5, "ATA": 2},
    "3-4-3": {"GOL": 1, "ZAG": 3, "LAT": 0, "MEI": 4, "ATA": 3}
}

formacao_escolhida = st.selectbox("Escolha a formação tática", list(opcoes_formacao.keys()))
formacao = opcoes_formacao[formacao_escolhida]

time_ideal = pd.DataFrame()
orçamento_disponivel = orçamento

for posicao, qtd in formacao.items():
    jogadores_posicao = df_filtrado[df_filtrado["Posição"] == posicao]
    jogadores_posicao = jogadores_posicao.sort_values("Custo-Benefício", ascending=False).head(10)
    selecionados = jogadores_posicao.head(qtd)
    time_ideal = pd.concat([time_ideal, selecionados])
    orçamento_disponivel -= selecionados["Preço (C$)"].sum()

if not time_ideal.empty:
    st.dataframe(time_ideal[["Nome", "Posição", "Clube", "Preço (C$)", "Pontos Média", "Custo-Benefício"]])
    st.write(f"💰 Orçamento restante: {orçamento_disponivel:.2f} C$")
else:
    st.warning("Nenhum jogador selecionado para o time ideal. Verifique os filtros ou aumente o orçamento.")

st.caption("Desenvolvido por Carlos Willian - Cartola FC 2025")


