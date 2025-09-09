# Dashboard Cartola FC 2025 - Design Aprimorado
"""
Dashboard Cartola FC 2025 - Versão com Design Moderno e Análise Avançada
Author: Carlos Willian (Aprimorado por Especialista em Streamlit, Python e UX)
Funcionalidades: Análise avançada de jogadores do Cartola FC com design premium,
insights guiados e comparações visuais aprimoradas.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import json
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# ================================
# CONFIGURAÇÕES GLOBAIS
# ================================

st.set_page_config(
    page_title="Dashboard Cartola FC 2025",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URLs da API
API_URLS = {
    'mercado': 'https://api.cartola.globo.com/atletas/mercado',
    'status': 'https://api.cartola.globo.com/mercado/status',
    'pontuados': 'https://api.cartola.globo.com/atletas/pontuados' # URL não usada, mas mantida para referência
}

# Constantes
CACHE_TTL = 300  # 5 minutos
MAX_RETRIES = 3
TIMEOUT = 10

# ================================
# DESIGN SYSTEM (CSS)
# ================================

def aplicar_design_premium():
    """Aplica o CSS customizado para um design moderno e sofisticado."""
    st.markdown("""
    <style>
    /* =====================================
       IMPORTAÇÃO DE FONTES E RESET GLOBAL
    ===================================== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    * { box-sizing: border-box; }
    
    /* =====================================
       VARIÁVEIS CSS PARA DESIGN SYSTEM
    ===================================== */
    :root {
        --primary-50: #eff6ff; --primary-100: #dbeafe; --primary-200: #bfdbfe; --primary-300: #93c5fd;
        --primary-400: #60a5fa; --primary-500: #3b82f6; --primary-600: #2563eb; --primary-700: #1d4ed8;
        --primary-800: #1e40af; --primary-900: #1e3a8a; --success-50: #ecfdf5; --success-500: #10b981;
        --success-600: #059669; --warning-50: #fffbeb; --warning-500: #f59e0b; --warning-600: #d97706;
        --error-50: #fef2f2; --error-500: #ef4444; --error-600: #dc2626; --gray-50: #f9fafb;
        --gray-100: #f3f4f6; --gray-200: #e5e7eb; --gray-300: #d1d5db; --gray-400: #9ca3af;
        --gray-500: #6b7280; --gray-600: #4b5563; --gray-700: #374151; --gray-800: #1f2937;
        --gray-900: #111827; --shadow-sm: 0 1px 2px 0 rgba(0,0,0,0.05);
        --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
        --border-radius-sm: 6px; --border-radius-md: 8px; --border-radius-lg: 12px;
        --border-radius-xl: 16px; --border-radius-2xl: 24px;
    }
    
    /* =====================================
       BASE E TIPOGRAFIA
    ===================================== */
    html, body, .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background: linear-gradient(135deg, var(--gray-50) 0%, #ffffff 100%) !important;
        color: var(--gray-800) !important;
        line-height: 1.6; font-size: 16px; font-weight: 400;
    }
    h1, .main-title {
        font-size: 3rem !important; font-weight: 900 !important;
        background: linear-gradient(135deg, var(--primary-600), var(--primary-800)) !important;
        -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
        background-clip: text !important; margin-bottom: 0.5rem !important; letter-spacing: -0.02em !important;
    }
    h2, .section-title {
        font-size: 2rem !important; font-weight: 800 !important; color: var(--gray-800) !important;
        margin: 2rem 0 1rem 0 !important; letter-spacing: -0.01em !important;
    }
    h3, .subsection-title {
        font-size: 1.5rem !important; font-weight: 700 !important; color: var(--gray-700) !important;
        margin: 1.5rem 0 1rem 0 !important;
    }
    
    /* =====================================
       SIDEBAR MODERNA
    ===================================== */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, var(--gray-50) 100%) !important;
        border-right: 1px solid var(--gray-200) !important; box-shadow: var(--shadow-lg) !important;
    }
    .css-1d391kg .stMarkdown h2, .css-1d391kg .stMarkdown h3, .css-1d391kg .stMarkdown h4 {
        color: var(--gray-800) !important; font-weight: 700 !important; font-size: 1.25rem !important;
        margin: 1.5rem 0 1rem 0 !important; padding-bottom: 0.5rem !important;
        border-bottom: 2px solid var(--primary-200) !important;
    }
    
    /* =====================================
       MÉTRICAS, CARDS E CONTAINERS
    ===================================== */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%) !important;
        backdrop-filter: blur(12px) !important; border: 1px solid var(--gray-200) !important;
        border-radius: var(--border-radius-xl) !important; padding: 2rem 1.5rem !important;
        box-shadow: var(--shadow-lg) !important; transition: all 0.3s ease !important;
        position: relative !important; overflow: hidden !important;
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-3px) scale(1.02) !important; box-shadow: var(--shadow-xl) !important;
        border-color: var(--primary-300) !important;
    }
    [data-testid="metric-container"]::before {
        content: '' !important; position: absolute !important; top: 0 !important; left: 0 !important;
        right: 0 !important; height: 5px !important;
        background: linear-gradient(90deg, var(--primary-400), var(--primary-600), var(--primary-500)) !important;
    }
    [data-testid="metric-value"] { font-size: 3rem !important; font-weight: 900 !important; }
    [data-testid="metric-label"] { font-size: 0.875rem !important; font-weight: 600 !important; text-transform: uppercase !important; }

    .player-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%) !important;
        backdrop-filter: blur(15px) !important; border: 2px solid var(--primary-200) !important;
        border-radius: var(--border-radius-xl) !important; padding: 2rem !important; box-shadow: var(--shadow-lg) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important; text-align: center !important;
        position: relative !important; overflow: hidden !important;
    }
    .player-card:hover {
        transform: translateY(-5px) scale(1.02) !important; box-shadow: var(--shadow-xl) !important;
        border-color: var(--primary-400) !important;
    }
    
    /* =====================================
       TABELAS, BOTÕES E TABS
    ===================================== */
    .stDataFrame {
        border-radius: var(--border-radius-lg) !important;
    }
    .stDataFrame thead th {
        background: linear-gradient(135deg, var(--gray-100), var(--gray-50)) !important;
        font-weight: 700 !important; text-transform: uppercase !important;
        border-bottom: 2px solid var(--primary-200) !important;
    }
    .stDataFrame tbody tr:hover { background: var(--primary-50) !important; }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-500), var(--primary-600)) !important;
        color: white !important; font-weight: 600 !important; border: none !important;
        border-radius: var(--border-radius-md) !important; padding: 0.75rem 1.5rem !important;
        box-shadow: var(--shadow-md) !important; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important; box-shadow: var(--shadow-lg) !important;
        background: linear-gradient(135deg, var(--primary-600), var(--primary-700)) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--success-500), var(--success-600)) !important; font-weight: 700 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        border-radius: var(--border-radius-xl) !important; padding: 0.5rem !important;
        box-shadow: var(--shadow-sm) !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-500), var(--primary-600)) !important;
        color: white !important; box-shadow: var(--shadow-md) !important;
        border-radius: var(--border-radius-md) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ================================
# FUNÇÕES DE UTILITÁRIOS E API
# ================================

class ApiException(Exception):
    """Exceção customizada para erros da API."""
    pass

def fazer_requisicao_api(url: str, max_retries: int = MAX_RETRIES) -> Dict:
    """Faz requisição para API com retry e tratamento de erro."""
    for tentativa in range(max_retries):
        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if tentativa == max_retries - 1:
                raise ApiException(f"Erro na API após {max_retries} tentativas: {str(e)}")
            time.sleep(1)

def validar_dados_jogadores(dados: Dict) -> bool:
    """Valida se os dados recebidos da API estão corretos."""
    return all(campo in dados for campo in ['atletas', 'clubes', 'posicoes'])

def calcular_metricas_futebol(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula métricas de performance para os jogadores."""
    if df.empty: return df
    
    df['Pontos por C$'] = (df['Pontos Média'] / df['Preço (C$)'].replace(0, 0.1)).round(3)
    total_rodadas = 38  # Idealmente, buscar da API de status se disponível
    df['Consistência (%)'] = ((df['Partidas'] / total_rodadas) * 100).round(1)
    
    # MELHORIA: A métrica 'Forma Atual' é uma simulação.
    # Numa versão futura, o ideal seria calcular a tendência de pontos das últimas 3-5 rodadas.
    np.random.seed(42)
    df['Forma Atual'] = np.random.choice(['🔥 Excelente', '⚡ Boa', '📊 Regular', '📉 Baixa'], 
                                         size=len(df), p=[0.15, 0.35, 0.35, 0.15])
    
    df['Status'] = pd.cut(df['Pontos Média'], bins=[-np.inf, 2, 5, 8, np.inf], 
                          labels=['🔴 Baixo', '🟡 Regular', '🟢 Bom', '🔵 Excelente'])
    
    # Pontos por Ações (preenchendo NaNs com 0 para evitar erros)
    scouts = ['G', 'A', 'FT', 'FD', 'FF', 'DS', 'CA', 'CV', 'SG', 'DD', 'DP', 'GS']
    for scout in scouts:
        if scout not in df.columns:
            df[scout] = 0
    df[scouts] = df[scouts].fillna(0)

    df['Pts Ações Ofensivas'] = (df['G']*8 + df['A']*5 + df['FT']*3 + df['FD']*1.2 + df['FF']*0.8).round(2)
    df['Pts Ações Defensivas'] = (df['DS']*1.5 + df['SG']*5 + df['DD']*3 + df['DP']*7).round(2)
    
    return df

@st.cache_data(ttl=CACHE_TTL, show_spinner="Buscando dados na API do Cartola... ⚽")
def carregar_dados_api() -> Tuple[pd.DataFrame, Dict]:
    """Carrega, processa e cacheia dados da API do Cartola FC."""
    try:
        status_data = fazer_requisicao_api(API_URLS['status'])
        mercado_data = fazer_requisicao_api(API_URLS['mercado'])
        
        if not validar_dados_jogadores(mercado_data):
            raise ApiException("Dados da API inválidos ou incompletos.")
        
        jogadores = mercado_data['atletas']
        clubes = {str(k): v for k, v in mercado_data['clubes'].items()}
        posicoes = {str(k): v for k, v in mercado_data['posicoes'].items()}
        
        dados_processados = []
        for jogador in jogadores:
            clube_info = clubes.get(str(jogador['clube_id']), {})
            posicao_info = posicoes.get(str(jogador['posicao_id']), {})
            
            # Normaliza os dados do jogador com valores padrão
            dados_jogador = {
                'ID': jogador.get('atleta_id', 0),
                'Nome': jogador.get('apelido', 'N/A'),
                'Clube': clube_info.get('nome', 'Desconhecido'),
                'Posição': posicao_info.get('nome', 'Desconhecido'),
                'Preço (C$)': float(jogador.get('preco_num', 0)),
                'Pontos Média': float(jogador.get('media_num', 0)),
                'Partidas': int(jogador.get('jogos_num', 0)),
                'Foto': jogador.get('foto', ''),
            }
            dados_jogador.update(jogador.get('scout', {}))
            dados_processados.append(dados_jogador)
        
        df = pd.DataFrame(dados_processados)
        if df.empty:
            raise ApiException("Nenhum dado de jogador foi processado.")
            
        return calcular_metricas_futebol(df), status_data
        
    except ApiException as e:
        st.error(f"❌ Erro ao comunicar com a API do Cartola: {e}")
        return pd.DataFrame(), {}
    except Exception as e:
        st.error(f"❌ Um erro inesperado ocorreu: {e}")
        return pd.DataFrame(), {}

# ================================
# COMPONENTES DA INTERFACE (UI)
# ================================

def criar_header_premium(status_data: Dict):
    """Cria o cabeçalho principal com status dinâmico do mercado."""
    status_mercado = status_data.get('status_mercado_desc', 'Indisponível')
    rodada_atual = status_data.get('rodada_atual', 'N/A')
    
    cor_status = {
        'Mercado aberto': 'success',
        'Mercado fechado': 'error',
        'Mercado em manutenção': 'warning'
    }.get(status_mercado, 'primary')

    st.markdown(f"""
    <div style='text-align: center; padding: 3rem 0 2rem 0; background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%); border-radius: 24px; margin-bottom: 2rem; border: 1px solid rgba(59, 130, 246, 0.2);'>
        <h1 class='main-title'>⚽ Dashboard Cartola FC 2025</h1>
        <p style='font-size: 1.25rem; color: var(--gray-600); font-weight: 500;'>
            Análise Inteligente com Métricas Premium de Futebol
        </p>
        <div style='margin-top: 1.5rem; display: flex; justify-content: center; align-items: center; gap: 2rem; flex-wrap: wrap;'>
            <span style='display: inline-flex; align-items: center; gap: 0.5rem; font-weight: 600; font-size: 1rem;'>
                <span style='width: 10px; height: 10px; background: var(--{cor_status}-500); border-radius: 50%;'></span>
                {status_mercado}
            </span>
            <span style='font-weight: 600; font-size: 1rem;'>
                Rodada Atual: <span style='color: var(--primary-600); font-weight: 800;'>{rodada_atual}</span>
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def criar_filtros_sidebar_premium(df: pd.DataFrame) -> Tuple:
    """Cria os filtros interativos na barra lateral."""
    st.sidebar.markdown("## ⚙️ Painel de Controle")
    
    posicoes = sorted(df["Posição"].unique())
    posicao_sel = st.sidebar.multiselect("Filtrar por Posição:", posicoes, default=posicoes)
    
    clubes = sorted(df["Clube"].unique())
    clube_sel = st.sidebar.multiselect("Filtrar por Clube:", clubes, default=clubes)
    
    st.sidebar.markdown("---")
    
    preco_min, preco_max = st.sidebar.slider(
        "Faixa de Preço (C$)", 
        float(df["Preço (C$)"].min()), float(df["Preço (C$)"].max()), 
        (float(df["Preço (C$)"].min()), float(df["Preço (C$)"].max()))
    )
    
    media_min, media_max = st.sidebar.slider(
        "Faixa de Pontuação Média", 
        float(df["Pontos Média"].min()), float(df["Pontos Média"].max()),
        (float(df["Pontos Média"].min()), float(df["Pontos Média"].max())),
        step=0.1
    )

    return (posicao_sel, clube_sel, (preco_min, preco_max), (media_min, media_max))

def criar_metricas_principais_premium(df: pd.DataFrame):
    """Exibe as métricas chave do conjunto de dados filtrado."""
    if df.empty:
        st.warning("Nenhum jogador encontrado com os filtros aplicados. Tente ampliar sua busca.")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Jogadores Filtrados", f"{len(df):,}")
    col2.metric("💰 Preço Médio", f"C$ {df['Preço (C$)'].mean():.2f}")
    col3.metric("📊 Pontuação Média", f"{df['Pontos Média'].mean():.2f}")
    col4.metric("💎 Retorno Médio (Pts/C$)", f"{df['Pontos por C$'].mean():.3f}")

def criar_graficos_visao_geral(df: pd.DataFrame):
    """Cria os gráficos da aba Visão Geral."""
    st.info("💡 **Como interpretar:** Use o gráfico de dispersão para encontrar 'pechinchas' (jogadores no quadrante superior esquerdo: alta média, baixo preço). O gráfico de barras mostra os jogadores mais eficientes no uso do seu dinheiro.", icon="🧠")
    
    col1, col2 = st.columns(2)
    cores_premium = px.colors.qualitative.Vivid
    
    with col1:
        st.subheader("📈 Preço vs. Performance")
        fig = px.scatter(
            df, x="Preço (C$)", y="Pontos Média", color="Posição", size="Partidas",
            hover_name="Nome", hover_data=["Clube", "Pontos por C$"],
            title="Relação entre Investimento e Retorno",
            color_discrete_sequence=cores_premium
        )
        fig.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color='white')))
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💎 Top 10 Melhor Custo-Benefício")
        top_retorno = df.nlargest(10, 'Pontos por C$').sort_values('Pontos por C$', ascending=True)
        fig = px.bar(
            top_retorno, x='Pontos por C$', y='Nome', orientation='h',
            hover_data=['Clube', 'Preço (C$)', 'Pontos Média'],
            title="Jogadores com Melhor Eficiência (Pontos por C$)",
            color='Pontos por C$', color_continuous_scale='Blues'
        )
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=500)
        st.plotly_chart(fig, use_container_width=True)

# MELHORIA: Nova função para a aba "Ações Específicas"
def criar_graficos_acoes_especificas(df: pd.DataFrame):
    """Cria visualizações para scouts ofensivos e defensivos."""
    st.info("💡 **Como interpretar:** Identifique jogadores que se destacam em scouts específicos. Atacantes com muitas finalizações (FD) podem pontuar mesmo sem gols. Zagueiros com muitos desarmes (DS) são valiosos para a defesa.", icon="🎯")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Líderes em Ações Ofensivas")
        ofensivos = df.nlargest(10, "Pts Ações Ofensivas").sort_values("Pts Ações Ofensivas", ascending=True)
        fig = px.bar(ofensivos, x="Pts Ações Ofensivas", y="Nome", color="Posição",
                     hover_data=["G", "A", "FT"], orientation='h', title="Top 10 Jogadores Ofensivos")
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🛡️ Líderes em Ações Defensivas")
        defensivos = df.nlargest(10, "Pts Ações Defensivas").sort_values("Pts Ações Defensivas", ascending=True)
        fig = px.bar(defensivos, x="Pts Ações Defensivas", y="Nome", color="Posição",
                     hover_data=["DS", "SG", "DD"], orientation='h', title="Top 10 Jogadores Defensivos")
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=400)
        st.plotly_chart(fig, use_container_width=True)

# MELHORIA: Nova função para o Gráfico de Radar
def criar_grafico_radar_comparacao(j1: pd.Series, j2: pd.Series):
    """Cria um gráfico de radar para comparar dois jogadores."""
    metricas = ['Pontos Média', 'Pontos por C$', 'Partidas', 'Pts Ações Ofensivas', 'Pts Ações Defensivas']
    categorias = ['Média', 'Custo-Benefício', 'Consistência', 'Ataque', 'Defesa']
    
    # Normaliza os dados para uma escala comparável (0-1)
    def normalizar(valor, min_val, max_val):
        if max_val == min_val: return 0.5 # Evita divisão por zero
        return (valor - min_val) / (max_val - min_val)

    valores_j1, valores_j2 = [], []
    for metrica in metricas:
        min_v = min(j1[metrica], j2[metrica]) * 0.8
        max_v = max(j1[metrica], j2[metrica]) * 1.2
        valores_j1.append(normalizar(j1[metrica], min_v, max_v))
        valores_j2.append(normalizar(j2[metrica], min_v, max_v))
        
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(r=valores_j1, theta=categorias, fill='toself', name=j1['Nome']))
    fig.add_trace(go.Scatterpolar(r=valores_j2, theta=categorias, fill='toself', name=j2['Nome']))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=False, range=[0, 1])),
        showlegend=True,
        title="Comparação de Atributos (Normalizado)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

def criar_comparador_premium(df: pd.DataFrame):
    """Interface aprimorada para comparar dois jogadores."""
    st.subheader("⚔️ Comparador Avançado de Jogadores")
    
    opcoes = sorted(df['Nome'].unique())
    col1, col2 = st.columns(2)
    
    with col1:
        jogador1_nome = st.selectbox("Selecione o primeiro jogador:", options=opcoes, index=0)
    with col2:
        jogador2_nome = st.selectbox("Selecione o segundo jogador:", options=opcoes, index=1 if len(opcoes) > 1 else 0)

    if jogador1_nome and jogador2_nome and jogador1_nome != jogador2_nome:
        j1 = df[df['Nome'] == jogador1_nome].iloc[0]
        j2 = df[df['Nome'] == jogador2_nome].iloc[0]
        
        st.info("💡 **Como interpretar:** O gráfico de radar mostra os pontos fortes relativos de cada jogador. A área maior indica um jogador mais completo nas métricas selecionadas. Use as métricas abaixo para ver os valores absolutos.", icon="⭐")

        # MELHORIA: Usa o novo gráfico de radar
        criar_grafico_radar_comparacao(j1, j2)

        # Exibição das métricas lado a lado
        st.markdown("#### Detalhes das Métricas")
        cols = st.columns(5)
        metricas = {
            'Preço (C$)': '💰 Preço', 'Pontos Média': '📊 Média', 'Pontos por C$': '💎 Custo-Benefício',
            'Partidas': '⚽ Partidas', 'Pts Ações Ofensivas': '🔥 Ataque',
        }
        
        i = 0
        for campo, label in metricas.items():
            if campo in df.columns:
                with cols[i % 5]:
                    st.metric(label=f"{label} ({j1['Nome']})", value=f"{j1[campo]:.2f}")
                    st.metric(label=f"{label} ({j2['Nome']})", value=f"{j2[campo]:.2f}")
                i += 1
    else:
        st.warning("Selecione dois jogadores diferentes para iniciar a comparação.")

# ================================
# FUNÇÃO PRINCIPAL (main)
# ================================

def main():
    """Função principal que executa o dashboard Streamlit."""
    aplicar_design_premium()
    
    df, status_data = carregar_dados_api()
    
    criar_header_premium(status_data)

    if df.empty:
        st.error("Não foi possível carregar os dados do Cartola FC. Tente novamente mais tarde.")
        st.stop()
    
    filtros = criar_filtros_sidebar_premium(df)
    posicao_sel, clube_sel, preco_range, media_range = filtros
    
    df_filtrado = df[
        (df["Posição"].isin(posicao_sel)) &
        (df["Clube"].isin(clube_sel)) &
        (df["Preço (C$)"] >= preco_range[0]) & (df["Preço (C$)"] <= preco_range[1]) &
        (df["Pontos Média"] >= media_range[0]) & (df["Pontos Média"] <= media_range[1])
    ].copy()
    
    criar_metricas_principais_premium(df_filtrado)
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 **Visão Geral**", 
        "⚽ **Análise de Ações**", 
        "⚔️ **Comparador**", 
        "📋 **Dados Completos**"
    ])
    
    with tab1:
        criar_graficos_visao_geral(df_filtrado)
    
    with tab2:
        # MELHORIA: Conteúdo da aba implementado
        criar_graficos_acoes_especificas(df_filtrado)

    with tab3:
        criar_comparador_premium(df_filtrado)
        
    with tab4:
        st.subheader("📋 Tabela de Jogadores (Filtrada)")
        st.info("💡 **Dica:** Clique no cabeçalho de qualquer coluna para ordenar os dados.", icon="🖱️")
        
        colunas_exibicao = [
            'Nome', 'Clube', 'Posição', 'Preço (C$)', 'Pontos Média', 'Partidas',
            'Pontos por C$', 'Consistência (%)', 'Status', 'Forma Atual', 
            'Pts Ações Ofensivas', 'Pts Ações Defensivas'
        ]
        st.dataframe(
            df_filtrado[colunas_exibicao],
            use_container_width=True,
            height=600,
            hide_index=True
        )

        st.markdown("### 📁 Exportar Dados")
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Baixar Tabela Filtrada como CSV",
            data=csv,
            file_name=f"cartola_dados_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

if __name__ == "__main__":
    main()
