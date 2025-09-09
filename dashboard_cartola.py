# Dashboard Cartola Insights - Reboot 2025
"""
Versão reimaginada do Dashboard Cartola FC com foco em UI/UX, Storytelling e Insights Acionáveis.
Tema: Dark Mode Profissional
Especialista: Gemini (Python, Streamlit, UI/UX Design)
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import plotly.express as px
import plotly.graph_objects as go
import time
import json
from typing import Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

# ================================
# CONFIGURAÇÕES GLOBAIS
# ================================
st.set_page_config(
    page_title="Cartola Insights 2025",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URLs e Constantes
API_URLS = {
    'mercado': 'https://api.cartola.globo.com/atletas/mercado',
    'status': 'https://api.cartola.globo.com/mercado/status',
}
CACHE_TTL = 300  # 5 minutos

# ================================
# REBOOT: UI/UX - DESIGN SYSTEM (DARK MODE)
# ================================
def aplicar_design_dark_mode():
    """
    Aplica um CSS customizado para um tema dark sofisticado, focado em contraste e legibilidade.
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    :root {
        --cor-fundo-escuro: #0F172A; /* Slate 900 */
        --cor-fundo-claro: #1E293B;  /* Slate 800 */
        --cor-borda: #334155;       /* Slate 700 */
        --cor-primaria: #22C55E;     /* Green 500 */
        --cor-primaria-hover: #16A34A; /* Green 600 */
        --cor-texto-principal: #F8FAFC; /* Slate 50 */
        --cor-texto-secundario: #94A3B8; /* Slate 400 */
        --cor-sucesso: #22C55E;
        --cor-alerta: #F59E0B;
        --cor-erro: #EF4444;
        --raio-borda: 12px;
        --sombra-card: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
    }

    html, body, .stApp {
        font-family: 'Inter', sans-serif !important;
        background-color: var(--cor-fundo-escuro) !important;
        color: var(--cor-texto-principal) !important;
    }

    /* Títulos */
    h1, h2, h3 {
        font-weight: 700 !important;
        color: var(--cor-texto-principal) !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--cor-fundo-claro) !important;
        border-right: 1px solid var(--cor-borda);
    }

    /* Cards de Métrica (KPIs) */
    [data-testid="metric-container"] {
        background-color: var(--cor-fundo-claro);
        border: 1px solid var(--cor-borda);
        border-radius: var(--raio-borda);
        padding: 1.5rem;
        box-shadow: var(--sombra-card);
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
    }
    [data-testid="metric-label"] {
        color: var(--cor-texto-secundario);
        font-weight: 600;
        font-size: 0.9rem;
    }
    [data-testid="metric-value"] {
        color: var(--cor-texto-principal);
        font-size: 2.25rem;
        font-weight: 800;
    }

    /* Abas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: var(--cor-fundo-claro);
        border-radius: 8px;
        border: 1px solid var(--cor-borda);
        color: var(--cor-texto-secundario);
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--cor-primaria);
        color: var(--cor-fundo-escuro);
        font-weight: 700;
    }

    /* Botões */
    .stButton > button {
        background-color: var(--cor-primaria);
        color: var(--cor-fundo-escuro);
        border: none;
        border-radius: 8px;
        font-weight: 700;
        padding: 0.75rem 1.5rem;
    }
    .stButton > button:hover {
        background-color: var(--cor-primaria-hover);
        color: var(--cor-fundo-escuro);
    }
    
    /* Tabelas */
    .stDataFrame {
        border: 1px solid var(--cor-borda) !important;
        border-radius: var(--raio-borda) !important;
    }
    thead th {
        background-color: var(--cor-fundo-claro);
        color: var(--cor-texto-principal);
        font-weight: 700;
    }
    tbody tr:hover {
        background-color: #334155; /* Um pouco mais claro para hover */
    }
    
    </style>
    """, unsafe_allow_html=True)

# ================================
# LÓGICA DE DADOS (API E CÁLCULOS)
# ================================
@st.cache_data(ttl=CACHE_TTL, show_spinner="Buscando dados na API oficial do Cartola... ⚽")
def carregar_dados_api() -> Tuple[pd.DataFrame, Dict]:
    try:
        status_data = requests.get(API_URLS['status'], timeout=10).json()
        mercado_data = requests.get(API_URLS['mercado'], timeout=10).json()
        
        jogadores = mercado_data['atletas']
        clubes = {str(k): v for k, v in mercado_data['clubes'].items()}
        posicoes = {str(k): v for k, v in mercado_data['posicoes'].items()}
        
        dados_processados = []
        for jogador in jogadores:
            dados_jogador = {
                'ID': jogador.get('atleta_id', 0),
                'Nome': jogador.get('apelido', 'N/A'),
                'Clube': clubes.get(str(jogador['clube_id']), {}).get('nome', 'Desconhecido'),
                'Posição': posicoes.get(str(jogador['posicao_id']), {}).get('nome', 'Desconhecido'),
                'Preço (C$)': float(jogador.get('preco_num', 0)),
                'Pontos Média': float(jogador.get('media_num', 0)),
                'Partidas': int(jogador.get('jogos_num', 0)),
                'Status': jogador.get('status_id', 0)
            }
            dados_jogador.update(jogador.get('scout', {}))
            dados_processados.append(dados_jogador)
        
        df = pd.DataFrame(dados_processados)
        return calcular_metricas(df), status_data
        
    except requests.RequestException as e:
        st.error(f"Falha na comunicação com a API do Cartola. Verifique sua conexão. (Erro: {e})")
        return pd.DataFrame(), {}

def calcular_metricas(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    
    df['Pontos por C$'] = (df['Pontos Média'] / df['Preço (C$)'].replace(0, 0.1)).round(3)
    
    status_map = {
        7: 'Provável', 6: 'Dúvida', 2: 'Contundido/Suspenso', 5: 'Nulo'
    }
    df['Status'] = df['Status'].map(status_map).fillna('Indefinido')
    
    scouts = ['G', 'A', 'DS', 'SG', 'DD', 'FT', 'FD', 'FF']
    for scout in scouts:
        if scout not in df.columns: df[scout] = 0
    df[scouts] = df[scouts].fillna(0)
    
    df['Índice Ofensivo'] = (df['G']*8 + df['A']*5 + df['FD']*1.2 + df['FF']*0.8 + df['FT']*3).round(2)
    df['Índice Defensivo'] = (df['DS']*1.5 + df['SG']*5 + df['DD']*3).round(2)
    
    return df

# ================================
# COMPONENTES DE UI E STORYTELLING
# ================================
def display_header(status_data: Dict):
    status_mercado = status_data.get('status_mercado_desc', 'Indisponível')
    rodada_atual = status_data.get('rodada_atual', 'N/A')
    
    st.markdown(f"""
    <div style="background-color: var(--cor-fundo-claro); padding: 2rem; border-radius: var(--raio-borda); text-align: center; margin-bottom: 2rem;">
        <h1 style="font-size: 3rem; font-weight: 800; color: var(--cor-primaria);">⭐ Cartola Insights 2025</h1>
        <p style="font-size: 1.25rem; color: var(--cor-texto-secundario);">A sua ferramenta definitiva para mitar no Cartola FC.</p>
        <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 1rem;">
            <span><strong>Rodada Atual:</strong> {rodada_atual}</span>
            <span><strong>Mercado:</strong> <span style="color: var(--cor-sucesso);">{status_mercado}</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_kpis(df: pd.DataFrame):
    if df.empty:
        st.warning("Nenhum jogador encontrado para os filtros selecionados.")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Jogadores na Análise", f"{len(df):,}")
    with col2:
        st.metric("💰 Preço Médio (C$)", f"{df['Preço (C$)'].mean():.2f}")
    with col3:
        st.metric("📊 Pontuação Média", f"{df['Pontos Média'].mean():.2f}")
    with col4:
        st.metric("💎 Custo-Benefício Médio", f"{df['Pontos por C$'].mean():.3f}")

def display_highlights(df: pd.DataFrame):
    st.markdown("### 🔥 Destaques da Rodada")
    if df.empty: return

    mais_caro = df.loc[df['Preço (C$)'].idxmax()]
    melhor_media = df.loc[df['Pontos Média'].idxmax()]
    melhor_custo_beneficio = df.loc[df[df['Status'] == 'Provável']['Pontos por C$'].idxmax()]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"💰 **Mais Caro:** {mais_caro['Nome']} ({mais_caro['Clube']}) custando C$ {mais_caro['Preço (C$)']:.2f}", icon="💰")
    with col2:
        st.info(f"🏆 **Melhor Média:** {melhor_media['Nome']} ({melhor_media['Clube']}) com {melhor_media['Pontos Média']:.2f} pts/jogo", icon="🏆")
    with col3:
        st.info(f"💎 **Jóia Rara (Custo/Benefício):** {melhor_custo_beneficio['Nome']} ({melhor_custo_beneficio['Clube']})", icon="💎")

def display_charts(df: pd.DataFrame):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📈 Preço vs. Performance")
        fig = px.scatter(
            df, x="Preço (C$)", y="Pontos Média", color="Posição", size="Partidas",
            hover_name="Nome", template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("#### 💎 Top 15 Custo-Benefício")
        top_cb = df.nlargest(15, 'Pontos por C$')
        fig = px.bar(
            top_cb, y='Nome', x='Pontos por C$', orientation='h', color='Posição',
            template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel
        ).update_yaxes(categoryorder="total ascending")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

# ================================
# FUNÇÃO PRINCIPAL
# ================================
def main():
    aplicar_design_dark_mode()
    
    df, status_data = carregar_dados_api()
    if df.empty:
        st.error("Não foi possível carregar os dados. A API do Cartola pode estar offline. Tente novamente mais tarde.")
        st.stop()

    display_header(status_data)

    # --- FILTROS NA SIDEBAR ---
    st.sidebar.title("🔧 Painel de Filtros")
    posicoes = sorted(df["Posição"].unique())
    posicao_sel = st.sidebar.multiselect("Posições", posicoes, default=posicoes)
    
    clubes = sorted(df["Clube"].unique())
    clube_sel = st.sidebar.multiselect("Clubes", clubes, default=clubes)
    
    status_disp = sorted(df["Status"].unique())
    status_sel = st.sidebar.multiselect("Status do Jogador", status_disp, default=['Provável'])
    
    preco_range = st.sidebar.slider(
        "Faixa de Preço (C$)", 
        float(df["Preço (C$)"].min()), float(df["Preço (C$)"].max()), 
        (float(df["Preço (C$)"].min()), float(df["Preço (C$)"].max()))
    )
    
    # --- APLICAÇÃO DOS FILTROS ---
    df_filtrado = df[
        (df["Posição"].isin(posicao_sel)) &
        (df["Clube"].isin(clube_sel)) &
        (df["Status"].isin(status_sel)) &
        (df["Preço (C$)"] >= preco_range[0]) & (df["Preço (C$)"] <= preco_range[1])
    ].copy()

    # --- LAYOUT PRINCIPAL COM ABAS ---
    tab_geral, tab_analise, tab_dados = st.tabs(["📊 Visão Geral", "🎯 Análise Detalhada", "📋 Dados Completos"])

    with tab_geral:
        display_kpis(df_filtrado)
        st.divider()
        display_highlights(df_filtrado)
        st.divider()
        display_charts(df_filtrado)
        
    with tab_analise:
        st.markdown("### 🎯 Análise de Índices Ofensivos e Defensivos")
        st.info("Aqui você encontra os jogadores que mais se destacam em ações de ataque e defesa, independente da pontuação geral.", icon="💡")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🔥 Top Atacantes")
            top_ofensivo = df_filtrado.nlargest(15, "Índice Ofensivo")
            st.dataframe(top_ofensivo[['Nome', 'Clube', 'Posição', 'Índice Ofensivo', 'Pontos Média']], use_container_width=True)
        with col2:
            st.markdown("#### 🛡️ Top Defensores")
            top_defensivo = df_filtrado.nlargest(15, "Índice Defensivo")
            st.dataframe(top_defensivo[['Nome', 'Clube', 'Posição', 'Índice Defensivo', 'Pontos Média']], use_container_width=True)

    with tab_dados:
        st.markdown("### 📋 Tabela Completa de Jogadores")
        st.dataframe(df_filtrado, use_container_width=True, height=500)
        
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Baixar Dados como CSV",
            data=csv,
            file_name=f"cartola_insights_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

if __name__ == "__main__":
    main()
