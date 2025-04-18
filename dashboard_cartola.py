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

# Confrontos da Rodada Atual
st.subheader("📅 Confrontos da Rodada Atual")

def obter_jogos_rodada():
    url_rodadas = "https://api.cartolafc.globo.com/rodadas"
    url_partidas = "https://api.cartolafc.globo.com/partidas/"

    try:
        response_rodadas = requests.get(url_rodadas)
        response_rodadas.raise_for_status()
        data_rodadas = response_rodadas.json()

        rodada_atual = None
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        hoje_brasilia = datetime.now(brasilia_tz).date()

        for rodada_info in data_rodadas:
            numero_rodada = rodada_info.get('rodada_id')
            inicio_str = rodada_info.get('inicio')
            fim_str = rodada_info.get('fim')

            if inicio_str and fim_str and numero_rodada is not None:
                inicio_data = datetime.strptime(inicio_str[:10], '%Y-%m-%d').date()
                fim_data = datetime.strptime(fim_str[:10], '%Y-%m-%d').date()

                if inicio_data <= hoje_brasilia <= fim_data:
                    rodada_atual = numero_rodada
                    break

        if rodada_atual:
            url_partidas_atual = f"{url_partidas}{rodada_atual}"
            response_partidas = requests.get(url_partidas_atual)
            response_partidas.raise_for_status()
            data_partidas = response_partidas.json()

            if 'partidas' in data_partidas and 'clubes' in data_partidas:
                clubes_data = data_partidas['clubes']
                for partida in data_partidas['partidas']:
                    clube_casa_id = str(partida.get('clube_casa_id'))
                    clube_visitante_id = str(partida.get('clube_visitante_id'))

                    time_casa = clubes_data.get(clube_casa_id, {}).get('nome', "Casa")
                    time_visitante = clubes_data.get(clube_visitante_id, {}).get('nome', "Visitante")
                    escudo_casa = clubes_data.get(clube_casa_id, {}).get('escudos', {}).get('60x60', "")
                    escudo_visitante = clubes_data.get(clube_visitante_id, {}).get('escudos', {}).get('60x60', "")

                    data_jogo_str = partida.get('partida_data')
                    hora_jogo_str = partida.get('partida_hora')

                    if data_jogo_str and hora_jogo_str:
                        data_hora_str = f"{data_jogo_str} {hora_jogo_str}"
                        data_hora_jogo = datetime.strptime(data_hora_str, '%Y-%m-%d %H:%M')
                        data_hora_local = data_hora_jogo - timedelta(hours=3)
                        st.markdown(f"""
                            <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                                <img src='{escudo_casa}' style='height:30px;margin-right:5px;'>
                                <b>{time_casa}</b>
                                <span style='margin: 0 10px;'>x</span>
                                <b>{time_visitante}</b>
                                <img src='{escudo_visitante}' style='height:30px;margin-left:5px;'>
                                <span style='margin-left: 15px;'>🕒 {data_hora_local.strftime('%d/%m %H:%M')}</span>
                            </div>
                        """, unsafe_allow_html=True)
    except:
        st.error("Erro ao carregar confrontos da rodada atual.")

obter_jogos_rodada()

st.caption("Desenvolvido por Carlos Willian - Cartola FC 2025")


