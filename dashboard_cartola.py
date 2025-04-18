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

st.title("F3DF️ Dashboard de Scouts - Cartola FC 2025")

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

    # Garantir que Preço é numérico
    df_filtrado["Preço (C$)"] = pd.to_numeric(df_filtrado["Preço (C$)"], errors="coerce").fillna(0.0)

    # Criar métrica de custo-benefício
    df_filtrado["Custo-Benefício"] = df_filtrado["Pontos Média"] / df_filtrado["Preço (C$)"].replace(0, 0.1)

    # Rankings
    st.subheader("F3C6 Top Jogadores")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("**Por Pontos Média**")
        st.dataframe(df_filtrado.sort_values("Pontos Média", ascending=False).head(10))

    with col4:
        st.markdown("**Por Custo-Benefício**")
        st.dataframe(df_filtrado.sort_values("Custo-Benefício", ascending=False).head(10))

    # Gráfico de barras: Média de Pontos por Posição
    st.subheader("F4CA Média de Pontos por Posição")

    media_por_posicao = df_filtrado.groupby("Posição")["Pontos Média"].mean().sort_values(ascending=False).reset_index()

    fig = px.bar(
        media_por_posicao,
        x="Posição",
        y="Pontos Média",
        color="Posição",
        text="Pontos Média",
        title="Média de Pontos por Posição",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(xaxis_title=None, yaxis_title="Pontos", showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

    # Tabela completa com filtro de nome
    st.subheader("F4C4 Tabela Completa dos Jogadores")

    nome_jogador = st.text_input("F50D Buscar jogador pelo nome")

    if nome_jogador:
        df_filtrado = df_filtrado[df_filtrado["Nome"].str.contains(nome_jogador, case=False, na=False)]

    st.dataframe(df_filtrado.sort_values("Pontos Média", ascending=False), use_container_width=True)

    # Análise por perfil de jogador
    st.subheader("F4CA Análise por Perfil de Jogador")
    perfil = st.radio("Escolha o perfil para análise:", ["Finalizadores", "Criadores", "Defensores"])

    if perfil == "Finalizadores":
        df_filtrado["FD"] = pd.to_numeric(df_filtrado["FD"], errors="coerce").fillna(0)
        df_filtrado["G"] = pd.to_numeric(df_filtrado["G"], errors="coerce").fillna(0)
        resultado = df_filtrado.sort_values(["FD", "G"], ascending=False).head(10)

    elif perfil == "Criadores":
        df_filtrado["A"] = pd.to_numeric(df_filtrado["A"], errors="coerce").fillna(0)
        df_filtrado["FS"] = pd.to_numeric(df_filtrado["FS"], errors="coerce").fillna(0)
        resultado = df_filtrado.sort_values(["A", "FS"], ascending=False).head(10)

    else:
        df_filtrado["DS"] = pd.to_numeric(df_filtrado["DS"], errors="coerce").fillna(0)
        df_filtrado["SG"] = pd.to_numeric(df_filtrado["SG"], errors="coerce").fillna(0)
        resultado = df_filtrado.sort_values(["DS", "SG"], ascending=False).head(10)

    st.dataframe(resultado)

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
                id_casa = str(partida.get("clube_casa_id"))
                id_visitante = str(partida.get("clube_visitante_id"))

                nome_casa = clubes_dict.get(id_casa, {}).get("nome", "Desconhecido")
                nome_visitante = clubes_dict.get(id_visitante, {}).get("nome", "Desconhecido")

                placar = f"{nome_casa} x {nome_visitante}"
                st.markdown(f"- {placar}")
        else:
            st.error("Erro ao buscar dados da API do Cartola.")
    except Exception as e:
        st.error(f"Erro na requisição: {e}")

st.caption("Desenvolvido por Carlos Willian - Cartola FC 2025")
