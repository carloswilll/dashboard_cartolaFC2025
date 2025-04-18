import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
import pytz

st.set_page_config(page_title="Dashboard Cartola 2025", layout="wide")

# Carregar os dados
@st.cache_data
def carregar_dados():
    return pd.read_csv("scouts_jogadores.csv")

df = carregar_dados()

st.title("\U0001F3DF️ Dashboard de Scouts - Cartola FC 2025")

aba1, aba2, aba3 = st.tabs(["🔎 Análises Gerais", "🧮 Time Ideal", "🔕️ Confrontos"])

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

    for scout in scouts_ofensivos + scouts_defensivos:
        if scout in df_filtrado.columns:
            df_filtrado[scout] = pd.to_numeric(df_filtrado[scout], errors="coerce").fillna(0)

    df_filtrado["Score Ofensivo"] = df_filtrado[[s for s in scouts_ofensivos if s in df_filtrado.columns]].sum(axis=1)
    df_filtrado["Score Defensivo"] = df_filtrado[[s for s in scouts_defensivos if s in df_filtrado.columns]].sum(axis=1)

    col5, col6 = st.columns(2)
    with col5:
        st.markdown("**Top 10 - Scouts Ofensivos**")
        st.dataframe(df_filtrado.sort_values("Score Ofensivo", ascending=False)[["Nome", "Clube", "Posição", "Score Ofensivo"]].head(10))

    with col6:
        st.markdown("**Top 10 - Scouts Defensivos**")
        st.dataframe(df_filtrado.sort_values("Score Defensivo", ascending=False)[["Nome", "Clube", "Posição", "Score Defensivo"]].head(10))

    with st.expander("📘 Dicionário de Scouts"):
        st.markdown("""
        **J** - Jogos

        **SCOUTS POSITIVOS**
        - **DS** - Desarme (+1,5)
        - **G** - Gol (+8,0)
        - **A** - Assistência (+5,0)
        - **SG** - Saldo de Gols (sem sofrer gol) (+5,0)
        - **FS** - Falta Sofrida (+0,5)
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

with aba2:
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
    faltando_posicoes = []

    for posicao, qtd in formacao.items():
        jogadores_posicao = df[df["Posição"] == posicao].sort_values("Custo-Benefício", ascending=False)
        selecionados = pd.DataFrame()
        for _, jogador in jogadores_posicao.iterrows():
            if len(selecionados) < qtd and jogador["Preço (C$)"] <= orçamento_disponivel:
                selecionados = pd.concat([selecionados, pd.DataFrame([jogador])])
                orçamento_disponivel -= jogador["Preço (C$)"]
        if len(selecionados) < qtd:
            faltando_posicoes.append(posicao)
        time_ideal = pd.concat([time_ideal, selecionados])

    if not time_ideal.empty:
        st.dataframe(time_ideal[["Nome", "Posição", "Clube", "Preço (C$)", "Pontos Média", "Custo-Benefício"]])
        st.write(f"💰 Orçamento restante: {orçamento_disponivel:.2f} C$")
        if faltando_posicoes:
            st.warning(f"Não foi possível preencher todas as posições: {', '.join(faltando_posicoes)}")
    else:
        st.warning("Nenhum jogador selecionado para o time ideal. Verifique os filtros ou aumente o orçamento.")

with aba3:
    st.subheader("🔕 Confrontos da Rodada")

    url = "https://api.cartola.globo.com/partidas"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()
            partidas = dados["partidas"]
            clubes_dict = dados.get("clubes", {})

            for partida in partidas:
                id_casa = str(partida["clube_casa_id"])
                id_visitante = str(partida["clube_visitante_id"])

                nome_casa = clubes_dict.get(id_casa, {}).get("nome", "Desconhecido")
                nome_visitante = clubes_dict.get(id_visitante, {}).get("nome", "Desconhecido")

                placar = f"{nome_casa} x {nome_visitante}"
                st.markdown(f"- {placar}")
        else:
            st.error("Erro ao buscar dados da API do Cartola.")
    except Exception as e:
        st.error(f"Erro na requisição: {e}")

st.caption("Desenvolvido por Carlos Willian - Cartola FC 2025")

