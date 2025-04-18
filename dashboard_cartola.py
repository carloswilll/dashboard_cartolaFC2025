import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Dashboard Cartola 2025", layout="wide")

# Carregar os dados
@st.cache_data
def carregar_dados():
    df = pd.read_csv("scouts_jogadores.csv")
    df.columns = df.columns.str.strip()  # Remove espaços em branco das colunas
    return df.convert_dtypes().infer_objects()

df = carregar_dados()
df["Preço (C$)"] = pd.to_numeric(df["Preço (C$)"], errors="coerce").fillna(0.0)
df["Pontos Média"] = pd.to_numeric(df["Pontos Média"], errors="coerce").fillna(0.0)
df["Custo-Benefício"] = df["Pontos Média"] / df["Preço (C$)"].replace(0, 0.1)

st.title("🏟️ Dashboard de Scouts - Cartola FC 2025")

aba1 = st.container()

with aba1:
    col1, col2 = st.columns(2)
    with col1:
        posicoes = df["Posição"].unique().tolist()
        posicao_selecionada = st.multiselect("Filtrar por Posição", posicoes, default=posicoes)

    with col2:
        clubes = df["Clube"].unique().tolist()
        clube_selecionado = st.multiselect("Filtrar por Clube", clubes, default=clubes)

    df_filtrado = df[
        (df["Posição"].isin(posicao_selecionada)) &
        (df["Clube"].isin(clube_selecionado))
    ].copy()

    df_filtrado["Preço (C$)"] = pd.to_numeric(df_filtrado["Preço (C$)"], errors="coerce").fillna(0.0)
    df_filtrado["Custo-Benefício"] = df_filtrado["Pontos Média"] / df_filtrado["Preço (C$)"].replace(0, 0.1)

    st.subheader("🏆 Top Jogadores")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("**Por Pontos Média**")
        st.dataframe(df_filtrado.sort_values("Pontos Média", ascending=False).head(10))

    with col4:
        st.markdown("**Por Custo-Benefício**")
        st.dataframe(df_filtrado.sort_values("Custo-Benefício", ascending=False).head(10))

    st.subheader("📊 Gráfico: Preço vs. Pontos Média")
    fig = px.scatter(
        df_filtrado,
        x="Preço (C$)",
        y="Pontos Média",
        color="Clube",
        hover_name="Nome",
        size_max=15,
        title="Relação entre Preço e Pontos Média",
        labels={"Preço (C$)": "Preço (C$)", "Pontos Média": "Pontos Média"},
    )
    fig.update_traces(marker=dict(size=10, opacity=0.7), selector=dict(mode='markers'))
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📄 Tabela Completa dos Jogadores")
    nome_jogador = st.text_input("🔍 Buscar jogador pelo nome")
    if nome_jogador:
        df_filtrado = df_filtrado[df_filtrado["Nome"].str.contains(nome_jogador, case=False, na=False)]
    st.dataframe(df_filtrado.sort_values("Pontos Média", ascending=False), use_container_width=True)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_filtrado.to_excel(writer, index=False, sheet_name='Jogadores')
    output.seek(0)
    dados_excel = output.getvalue()

    st.download_button(
        label="💾 Baixar tabela como Excel",
        data=dados_excel,
        file_name="jogadores_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.subheader("📉 Análise Sem Scouts-Chave")

    scout_valores = {
        "DS": 1.5, "G": 8.0, "A": 5.0, "SG": 5.0,
        "FS": 0.5, "FF": 0.8, "FD": 1.2, "FT": 3.0, "PS": 1.0,
        "DE": 1.3, "DP": 7.0,
        "GC": -3.0, "CV": -3.0, "CA": -1.0, "GS": -1.0,
        "PP": -4.0, "PC": -1.0, "FC": -0.3, "I": -0.1
    }

    for scout in scout_valores.keys():
        if scout in df_filtrado.columns:
            df_filtrado[scout] = pd.to_numeric(df_filtrado[scout], errors="coerce").fillna(0)

    def calcular_score(linha):
        return sum([linha[scout] * valor for scout, valor in scout_valores.items() if scout in linha])

    atac_mei_sem_ga = df_filtrado[(df_filtrado["Posição"].isin(["ATA", "MEI"])) & (df_filtrado["G"] == 0) & (df_filtrado["A"] == 0)].copy()
    atac_mei_sem_ga["Pontuação Total"] = atac_mei_sem_ga.apply(calcular_score, axis=1)
    atac_mei_sem_ga = atac_mei_sem_ga.sort_values("Pontuação Total", ascending=False)
    colunas_atac_mei = ['Nome', 'Clube', 'Posição', 'Preço (C$)', 'Pontos Média', 'Partidas',
        'DS', 'FC', 'FD', 'FF', 'FS', 'I', 'CA', 'FT', 'CV', 'PP', 'PC', 'DP', 'PS', 'GC', 'Pontuação Total']

    def_lat_sem_sg = df_filtrado[(df_filtrado["Posição"].isin(["ZAG", "LAT"])) & (df_filtrado["SG"] == 0)].copy()
    def_lat_sem_sg["Pontuação Total"] = def_lat_sem_sg.apply(calcular_score, axis=1)
    def_lat_sem_sg = def_lat_sem_sg.sort_values("Pontuação Total", ascending=False)
    colunas_def_lat = ['Nome', 'Clube', 'Posição', 'Preço (C$)', 'Pontos Média', 'Partidas',
        'DS', 'FC', 'FD', 'FF', 'FS', 'I', 'CA', 'FT', 'CV', 'PP', 'PC', 'PS', 'GC', 'Pontuação Total']

    gol_sem_sg = df_filtrado[(df_filtrado["Posição"] == "GOL") & (df_filtrado["SG"] == 0)].copy()
    gol_sem_sg["Pontuação Total"] = gol_sem_sg.apply(calcular_score, axis=1)
    gol_sem_sg = gol_sem_sg.sort_values("Pontuação Total", ascending=False)
    colunas_gol = ['Nome', 'Clube', 'Posição', 'Preço (C$)', 'Pontos Média', 'Partidas',
        'FC', 'FS', 'CA', 'DE', 'GS', 'CV', 'PC', 'DP', 'GC', 'Pontuação Total']

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown(f"**Atacantes e Meias sem Gols ou Assistências ({len(atac_mei_sem_ga)})**")
        st.dataframe(atac_mei_sem_ga[colunas_atac_mei], use_container_width=True)

    with col_b:
        st.markdown(f"**Zagueiros e Laterais sem SG ({len(def_lat_sem_sg)})**")
        st.dataframe(def_lat_sem_sg[colunas_def_lat], use_container_width=True)

    with col_c:
        st.markdown(f"**Goleiros sem SG ({len(gol_sem_sg)})**")
        st.dataframe(gol_sem_sg[colunas_gol], use_container_width=True)

    with st.expander("📘 Dicionário de Scouts"):
        st.markdown("""
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
