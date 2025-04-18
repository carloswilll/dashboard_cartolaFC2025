import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Cartola 2025", layout="wide")

# Carregar os dados
@st.cache_data
def carregar_dados():
    df = pd.read_csv("scouts_jogadores.csv")
    return df.convert_dtypes().infer_objects()

df = carregar_dados()
df["Preço (C$)"] = pd.to_numeric(df["Preço (C$)"], errors="coerce").fillna(0.0)
df["Pontos Média"] = pd.to_numeric(df["Pontos Média"], errors="coerce").fillna(0.0)
df["Custo-Benefício"] = df["Pontos Média"] / df["Preço (C$)"].replace(0, 0.1)

st.title("\U0001F3DF️ Dashboard de Scouts - Cartola FC 2025")

# Apenas uma aba ativa agora
aba1 = st.container()

with aba1:
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

    df_filtrado["Preço (C$)"] = pd.to_numeric(df_filtrado["Preço (C$)"], errors="coerce").fillna(0.0)
    df_filtrado["Custo-Benefício"] = df_filtrado["Pontos Média"] / df_filtrado["Preço (C$)"].replace(0, 0.1)

    # Rankings
    st.subheader("\U0001F3C6 Top Jogadores")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("**Por Pontos Média**")
        st.dataframe(df_filtrado.sort_values("Pontos Média", ascending=False).head(10))

    with col4:
        st.markdown("**Por Custo-Benefício**")
        st.dataframe(df_filtrado.sort_values("Custo-Benefício", ascending=False).head(10))

    # Tabela completa com filtro de nome
    st.subheader("\U0001F4C4 Tabela Completa dos Jogadores")
    nome_jogador = st.text_input("\U0001F50D Buscar jogador pelo nome")
    if nome_jogador:
        df_filtrado = df_filtrado[df_filtrado["Nome"].str.contains(nome_jogador, case=False, na=False)]
    st.dataframe(df_filtrado.sort_values("Pontos Média", ascending=False), use_container_width=True)

    # Análise por Perfil de Jogador - Separado em duas tabelas
    st.subheader("\U0001F4CA Análise por Perfil de Jogador")

    scouts_ofensivos = ["G", "A", "FS", "FF", "FD", "FT", "PS"]
    scouts_defensivos = ["SG", "DS", "DE", "DP"]
    scouts_negativos = ["GC", "CV", "CA", "GS", "PP", "PC", "FC", "I"]

    for scout in scouts_ofensivos + scouts_defensivos + scouts_negativos:
        if scout in df_filtrado.columns:
            df_filtrado[scout] = pd.to_numeric(df_filtrado[scout], errors="coerce").fillna(0)

    df_filtrado["Score Ofensivo"] = df_filtrado[scouts_ofensivos].sum(axis=1)
    df_filtrado["Score Defensivo"] = df_filtrado[scouts_defensivos].sum(axis=1)
    df_filtrado["Score Negativo"] = df_filtrado[scouts_negativos].sum(axis=1)

    col5, col6 = st.columns(2)
    with col5:
        st.markdown("**Top 10 - Scouts Ofensivos**")
        st.dataframe(df_filtrado.sort_values("Score Ofensivo", ascending=False)[["Nome", "Clube", "Posição", "Score Ofensivo"]].head(10))

    with col6:
        st.markdown("**Top 10 - Scouts Defensivos**")
        st.dataframe(df_filtrado.sort_values("Score Defensivo", ascending=False)[["Nome", "Clube", "Posição", "Score Defensivo"]].head(10))

    # Análise sem G/A ou SG por posição
    st.subheader("\U0001F4C9 Análise Sem Scouts-Chave")

    atac_mei_sem_ga = df_filtrado[(df_filtrado["Posição"].isin(["ATA", "MEI"])) & (df_filtrado["G"] == 0) & (df_filtrado["A"] == 0)]
    def_lat_sem_sg = df_filtrado[(df_filtrado["Posição"].isin(["ZAG", "LAT"])) & (df_filtrado["SG"] == 0)]
    gol_sem_sg = df_filtrado[(df_filtrado["Posição"] == "GOL") & (df_filtrado["SG"] == 0)]

    col7, col8 = st.columns(2)
    with col7:
        st.markdown(f"**Atacantes e Meias sem Gols ou Assistências ({len(atac_mei_sem_ga)})**")
        st.dataframe(atac_mei_sem_ga[["Nome", "Clube", "Posição", "G", "A"]])

    with col8:
        st.markdown(f"**Zagueiros e Laterais sem SG ({len(def_lat_sem_sg)})**")
        st.dataframe(def_lat_sem_sg[["Nome", "Clube", "Posição", "SG"]])

    st.markdown(f"**Goleiros sem SG ({len(gol_sem_sg)})**")
    st.dataframe(gol_sem_sg[["Nome", "Clube", "Posição", "SG"]])

    with st.expander("\U0001F4D8 Dicionário de Scouts"):
        st.markdown("""
        **J** - Jogos

        **SCOUTS POSITIVOS**
        - **DS** - Desarme (+1,5)
        - **G** - Gol (+8,0)
        - **A** - Assistência (+5,0)
        - **SG** - Saldo de Gols (sem sofrer gol) (+5,0)
        - **FS** - Falta Sofrida ( +0,5)
        - **FF** - Finalização para Fora (+0,8)
        - **FD** - Finalização Defendida (+1,2)
        - **FT** - Finalização na Trave (+3,0)
        - **PS** - Pênalti Sofrido (+1,0)
        - **DE** - Defesa (+1,3)
        - **DP** - Defesa de Pênalti (+7,0)

        **SCOUTS NEGATIVOS**
        - **GC** - Gol Contra (-3,0)
        - **CV** - Cartão Vermelho (-3,0)
        - **CA** - Cartão Amarelo (-1,0)
        - **GS** - Gol Sofrido (-1,0)
        - **PP** - Pênalti Perdido (-4,0)
        - **PC** - Pênalti Cometido (-1,0)
        - **FC** - Falta Cometida (-0,3)
        - **I** - Impedimento (-0,1)
        """)

st.caption("Desenvolvido por Carlos Willian - Cartola FC 2025")

