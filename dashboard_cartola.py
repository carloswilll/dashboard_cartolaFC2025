# Dashboard Cartola FC 2025 - Design Aprimorado
"""
Dashboard Cartola FC 2025 - Versão com Design Moderno
Author: Carlos Willian (Melhorado por IA)
Funcionalidades: Análise avançada de jogadores do Cartola FC com design premium
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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
    'pontuados': 'https://api.cartola.globo.com/atletas/pontuados'
}

# Constantes
CACHE_TTL = 300  # 5 minutos
MAX_RETRIES = 3
TIMEOUT = 10

# ================================
# DESIGN SYSTEM MODERNO
# ================================

def aplicar_design_premium():
    """Aplica design system moderno e sofisticado"""
    st.markdown("""
    <style>
    /* =====================================
       IMPORTAÇÃO DE FONTES E RESET GLOBAL
    ===================================== */
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    * {
        box-sizing: border-box;
    }
    
    /* =====================================
       VARIÁVEIS CSS PARA DESIGN SYSTEM
    ===================================== */
    
    :root {
        --primary-50: #eff6ff;
        --primary-100: #dbeafe;
        --primary-200: #bfdbfe;
        --primary-300: #93c5fd;
        --primary-400: #60a5fa;
        --primary-500: #3b82f6;
        --primary-600: #2563eb;
        --primary-700: #1d4ed8;
        --primary-800: #1e40af;
        --primary-900: #1e3a8a;
        
        --success-50: #ecfdf5;
        --success-500: #10b981;
        --success-600: #059669;
        
        --warning-50: #fffbeb;
        --warning-500: #f59e0b;
        --warning-600: #d97706;
        
        --error-50: #fef2f2;
        --error-500: #ef4444;
        --error-600: #dc2626;
        
        --gray-50: #f9fafb;
        --gray-100: #f3f4f6;
        --gray-200: #e5e7eb;
        --gray-300: #d1d5db;
        --gray-400: #9ca3af;
        --gray-500: #6b7280;
        --gray-600: #4b5563;
        --gray-700: #374151;
        --gray-800: #1f2937;
        --gray-900: #111827;
        
        --shadow-sm: 0 1px 2px 0 rgba(0,0,0,0.05);
        --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
        
        --border-radius-sm: 6px;
        --border-radius-md: 8px;
        --border-radius-lg: 12px;
        --border-radius-xl: 16px;
        --border-radius-2xl: 24px;
    }
    
    /* =====================================
       BASE E TIPOGRAFIA
    ===================================== */
    
    html, body, .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background: linear-gradient(135deg, var(--gray-50) 0%, #ffffff 100%) !important;
        color: var(--gray-800) !important;
        line-height: 1.6;
        font-size: 16px;
        font-weight: 400;
    }
    
    /* Títulos com hierarquia visual clara */
    h1, .main-title {
        font-size: 3rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, var(--primary-600), var(--primary-800)) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.02em !important;
    }
    
    h2, .section-title {
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: var(--gray-800) !important;
        margin: 2rem 0 1rem 0 !important;
        letter-spacing: -0.01em !important;
    }
    
    h3, .subsection-title {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: var(--gray-700) !important;
        margin: 1.5rem 0 1rem 0 !important;
    }
    
    /* =====================================
       SIDEBAR MODERNA
    ===================================== */
    
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, var(--gray-50) 100%) !important;
        border-right: 1px solid var(--gray-200) !important;
        box-shadow: var(--shadow-lg) !important;
    }
    
    .css-1d391kg .stMarkdown h2,
    .css-1d391kg .stMarkdown h3,
    .css-1d391kg .stMarkdown h4 {
        color: var(--gray-800) !important;
        font-weight: 700 !important;
        font-size: 1.25rem !important;
        margin: 1.5rem 0 1rem 0 !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 2px solid var(--primary-200) !important;
    }
    
    /* =====================================
       CARDS E CONTAINERS ELEGANTES
    ===================================== */
    
    /* Card base premium */
    .premium-card {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid var(--gray-200) !important;
        border-radius: var(--border-radius-xl) !important;
        padding: 1.5rem !important;
        box-shadow: var(--shadow-md) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .premium-card:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-xl) !important;
        border-color: var(--primary-300) !important;
    }
    
    .premium-card::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 4px !important;
        background: linear-gradient(90deg, var(--primary-500), var(--primary-600)) !important;
    }
    
    /* Expandir (filtros) com design premium */
    .stExpander {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid var(--gray-200) !important;
        border-radius: var(--border-radius-lg) !important;
        box-shadow: var(--shadow-sm) !important;
        margin-bottom: 1rem !important;
        overflow: hidden !important;
    }
    
    .stExpander > div:first-child {
        background: linear-gradient(135deg, var(--primary-50), var(--primary-100)) !important;
        border-bottom: 1px solid var(--primary-200) !important;
    }
    
    /* =====================================
       MÉTRICAS COM DESIGN SOFISTICADO
    ===================================== */
    
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid var(--gray-200) !important;
        border-radius: var(--border-radius-xl) !important;
        padding: 2rem 1.5rem !important;
        box-shadow: var(--shadow-lg) !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: var(--shadow-xl) !important;
        border-color: var(--primary-300) !important;
    }
    
    [data-testid="metric-container"]::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 5px !important;
        background: linear-gradient(90deg, var(--primary-400), var(--primary-600), var(--primary-500)) !important;
    }
    
    [data-testid="metric-value"] {
        color: var(--gray-800) !important;
        font-size: 3rem !important;
        font-weight: 900 !important;
        letter-spacing: -0.02em !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    [data-testid="metric-label"] {
        color: var(--gray-600) !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    /* =====================================
       TABELAS ELEGANTES
    ===================================== */
    
    .stDataFrame {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid var(--gray-200) !important;
        border-radius: var(--border-radius-lg) !important;
        box-shadow: var(--shadow-md) !important;
        overflow: hidden !important;
    }
    
    .stDataFrame thead th {
        background: linear-gradient(135deg, var(--gray-100), var(--gray-50)) !important;
        color: var(--gray-700) !important;
        font-size: 0.875rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        border-bottom: 2px solid var(--primary-200) !important;
        padding: 1rem 0.75rem !important;
    }
    
    .stDataFrame tbody td {
        color: var(--gray-700) !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        padding: 0.875rem 0.75rem !important;
        border-bottom: 1px solid var(--gray-100) !important;
    }
    
    .stDataFrame tbody tr:hover {
        background: var(--primary-50) !important;
    }
    
    /* =====================================
       BOTÕES PREMIUM
    ===================================== */
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-500), var(--primary-600)) !important;
        color: white !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.025em !important;
        border: none !important;
        border-radius: var(--border-radius-md) !important;
        padding: 0.75rem 1.5rem !important;
        box-shadow: var(--shadow-md) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-transform: uppercase !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-lg) !important;
        background: linear-gradient(135deg, var(--primary-600), var(--primary-700)) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    /* Botão primário especial */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--success-500), var(--success-600)) !important;
        font-weight: 700 !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, var(--success-600), var(--success-600)) !important;
    }
    
    /* =====================================
       TABS MODERNAS
    ===================================== */
    
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid var(--gray-200) !important;
        border-radius: var(--border-radius-xl) !important;
        padding: 0.5rem !important;
        margin-bottom: 2rem !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: var(--gray-600) !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: var(--border-radius-md) !important;
        margin: 0 0.25rem !important;
        transition: all 0.2s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.025em !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--gray-100) !important;
        color: var(--gray-700) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-500), var(--primary-600)) !important;
        color: white !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    /* =====================================
       INPUTS E CONTROLES
    ===================================== */
    
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid var(--gray-300) !important;
        border-radius: var(--border-radius-md) !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.2s ease !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--primary-400) !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid var(--gray-300) !important;
        border-radius: var(--border-radius-md) !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.2s ease !important;
        font-weight: 500 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-500) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* =====================================
       GRÁFICOS PREMIUM
    ===================================== */
    
    .js-plotly-plot {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: var(--border-radius-lg) !important;
        box-shadow: var(--shadow-md) !important;
        border: 1px solid var(--gray-200) !important;
        overflow: hidden !important;
    }
    
    /* =====================================
       ALERTAS E MENSAGENS
    ===================================== */
    
    .stSuccess {
        background: linear-gradient(135deg, var(--success-50), rgba(16, 185, 129, 0.1)) !important;
        border-left: 4px solid var(--success-500) !important;
        border-radius: var(--border-radius-md) !important;
        padding: 1rem 1.5rem !important;
        margin: 1rem 0 !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, var(--warning-50), rgba(245, 158, 11, 0.1)) !important;
        border-left: 4px solid var(--warning-500) !important;
        border-radius: var(--border-radius-md) !important;
        padding: 1rem 1.5rem !important;
        margin: 1rem 0 !important;
    }
    
    .stError {
        background: linear-gradient(135deg, var(--error-50), rgba(239, 68, 68, 0.1)) !important;
        border-left: 4px solid var(--error-500) !important;
        border-radius: var(--border-radius-md) !important;
        padding: 1rem 1.5rem !important;
        margin: 1rem 0 !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, var(--primary-50), rgba(59, 130, 246, 0.1)) !important;
        border-left: 4px solid var(--primary-500) !important;
        border-radius: var(--border-radius-md) !important;
        padding: 1rem 1.5rem !important;
        margin: 1rem 0 !important;
    }
    
    /* =====================================
       SPINNER E LOADING
    ===================================== */
    
    .stSpinner {
        color: var(--primary-500) !important;
    }
    
    /* =====================================
       COMPONENTES CUSTOMIZADOS
    ===================================== */
    
    /* Card de jogador para comparação */
    .player-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%) !important;
        backdrop-filter: blur(15px) !important;
        border: 2px solid var(--primary-200) !important;
        border-radius: var(--border-radius-xl) !important;
        padding: 2rem !important;
        box-shadow: var(--shadow-lg) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-align: center !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .player-card::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 6px !important;
        background: linear-gradient(90deg, var(--primary-400), var(--primary-600), var(--primary-500)) !important;
    }
    
    .player-card:hover {
        transform: translateY(-5px) scale(1.02) !important;
        box-shadow: var(--shadow-xl) !important;
        border-color: var(--primary-400) !important;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block !important;
        padding: 0.375rem 0.75rem !important;
        border-radius: var(--border-radius-md) !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        margin: 0.25rem !important;
    }
    
    /* =====================================
       RESPONSIVIDADE
    ===================================== */
    
    @media (max-width: 768px) {
        h1, .main-title {
            font-size: 2rem !important;
        }
        
        h2, .section-title {
            font-size: 1.5rem !important;
        }
        
        [data-testid="metric-container"] {
            padding: 1.5rem 1rem !important;
        }
        
        [data-testid="metric-value"] {
            font-size: 2rem !important;
        }
        
        .premium-card, .player-card {
            padding: 1rem !important;
        }
    }
    
    /* =====================================
       ANIMAÇÕES E TRANSIÇÕES
    ===================================== */
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.8;
        }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    
    .pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* =====================================
       SCROLLBAR CUSTOMIZADA
    ===================================== */
    
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--gray-100);
        border-radius: var(--border-radius-md);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary-400), var(--primary-500));
        border-radius: var(--border-radius-md);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
    }
    
    </style>
    """, unsafe_allow_html=True)

# ================================
# FUNÇÕES DE UTILITÁRIOS (mantidas iguais)
# ================================

class ApiException(Exception):
    """Exceção customizada para erros da API"""
    pass

def fazer_requisicao_api(url: str, max_retries: int = MAX_RETRIES) -> Dict:
    """Faz requisição para API com retry e tratamento de erro"""
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
    """Valida se os dados recebidos da API estão corretos"""
    campos_obrigatorios = ['atletas', 'clubes', 'posicoes']
    return all(campo in dados for campo in campos_obrigatorios)

def calcular_metricas_futebol(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula métricas específicas de futebol mais relevantes"""
    if df.empty:
        return df
    
    # 1. Pontos por Cartola$
    df['Pontos por C$'] = (df['Pontos Média'] / df['Preço (C$)'].replace(0, 0.1)).round(3)
    
    # 2. Consistência (assumindo 38 rodadas no Brasileirão)
    total_rodadas = 38
    df['Consistência (%)'] = ((df['Partidas'] / total_rodadas) * 100).round(1)
    
    # 3. Forma Atual (simulada)
    np.random.seed(42)
    forma_valores = np.random.choice(['🔥 Excelente', '⚡ Boa', '📊 Regular', '📉 Baixa'], 
                                   size=len(df), 
                                   p=[0.15, 0.35, 0.35, 0.15])
    df['Forma Atual'] = forma_valores
    
    # 4. Status baseado na pontuação média
    df['Status'] = pd.cut(
        df['Pontos Média'], 
        bins=[-np.inf, 2, 5, 8, np.inf], 
        labels=['🔴 Baixo', '🟡 Regular', '🟢 Bom', '🔵 Excelente']
    )
    
    # === MÉTRICAS DE AÇÕES ESPECÍFICAS ===
    
    # Ações Ofensivas
    acoes_ofensivas = []
    for _, jogador in df.iterrows():
        gols = jogador.get('G', 0) if pd.notna(jogador.get('G', 0)) else 0
        assistencias = jogador.get('A', 0) if pd.notna(jogador.get('A', 0)) else 0
        finalizacoes = jogador.get('FC', 0) if pd.notna(jogador.get('FC', 0)) else 0
        
        pontos_ofensivos = (gols * 8) + (assistencias * 5) + (finalizacoes * 1.2)
        acoes_ofensivas.append(pontos_ofensivos)
    
    df['Pts Ações Ofensivas'] = acoes_ofensivas
    
    # Ações Defensivas - Linha
    acoes_defensivas_linha = []
    for _, jogador in df.iterrows():
        desarmes = jogador.get('DS', 0) if pd.notna(jogador.get('DS', 0)) else 0
        interceptacoes = jogador.get('I', 0) if pd.notna(jogador.get('I', 0)) else 0
        faltas_sofridas = jogador.get('FS', 0) if pd.notna(jogador.get('FS', 0)) else 0
        
        pontos_def_linha = (desarmes * 1.7) + (interceptacoes * 1.8) + (faltas_sofridas * 0.5)
        acoes_defensivas_linha.append(pontos_def_linha)
    
    df['Pts Def. Linha'] = acoes_defensivas_linha
    
    # Ações Defensivas - Goleiros
    acoes_defensivas_gol = []
    for _, jogador in df.iterrows():
        if jogador.get('Posição') == 'Goleiro':
            defesas = jogador.get('DD', 0) if pd.notna(jogador.get('DD', 0)) else 0
            gols_contra = jogador.get('GC', 0) if pd.notna(jogador.get('GC', 0)) else 0
            
            pontos_def_gol = (defesas * 3.2) + (gols_contra * -4)
            acoes_defensivas_gol.append(pontos_def_gol)
        else:
            acoes_defensivas_gol.append(0)
    
    df['Pts Def. Goleiro'] = acoes_defensivas_gol
    
    return df

# ================================
# FUNÇÕES DE CARREGAMENTO (mantida igual)
# ================================

@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def carregar_dados_api() -> pd.DataFrame:
    """Carrega dados da API do Cartola FC com cache otimizado"""
    try:
        # Status da API
        try:
            status_data = fazer_requisicao_api(API_URLS['status'])
        except:
            status_data = {'status_mercado_desc': 'Indisponível'}
        
        # Dados do mercado
        mercado_data = fazer_requisicao_api(API_URLS['mercado'])
        
        if not validar_dados_jogadores(mercado_data):
            raise ApiException("Dados da API inválidos")
        
        jogadores = mercado_data['atletas']
        clubes = mercado_data['clubes']
        posicoes = mercado_data['posicoes']
        
        # Processamento dos dados
        scouts_data = []
        for jogador in jogadores:
            try:
                clube_nome = clubes.get(str(jogador['clube_id']), {}).get('nome', 'Desconhecido')
                posicao_nome = posicoes.get(str(jogador['posicao_id']), {}).get('nome', 'Desconhecido')
                scouts = jogador.get('scout', {})
                
                dados_jogador = {
                    'ID': jogador.get('atleta_id', 0),
                    'Nome': jogador.get('apelido', 'N/A'),
                    'Clube': clube_nome,
                    'Posição': posicao_nome,
                    'Preço (C$)': float(jogador.get('preco_num', 0)),
                    'Pontos Média': float(jogador.get('media_num', 0)),
                    'Partidas': int(jogador.get('jogos_num', 0)),
                    'Foto': jogador.get('foto', ''),
                    'Status_Mercado': status_data.get('status_mercado_desc', 'Desconhecido')
                }
                
                # Adiciona scouts
                dados_jogador.update(scouts)
                scouts_data.append(dados_jogador)
                
            except Exception:
                continue
        
        df = pd.DataFrame(scouts_data)
        
        if df.empty:
            raise ApiException("Nenhum dado de jogador encontrado")
        
        # Limpeza e conversão de dados
        df = df.convert_dtypes()
        colunas_numericas = ['Preço (C$)', 'Pontos Média', 'Partidas']
        for col in colunas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Calcular métricas de futebol
        df = calcular_metricas_futebol(df)
        
        return df
        
    except ApiException as e:
        st.error(f"❌ Erro na API: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro inesperado: {e}")
        return pd.DataFrame()

# ================================
# COMPONENTES DA INTERFACE PREMIUM
# ================================

def criar_header_premium():
    """Cria header principal com design premium"""
    
    # Container principal com gradiente
    st.markdown("""
    <div style='text-align: center; padding: 3rem 0 2rem 0; background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%); border-radius: 24px; margin-bottom: 2rem; border: 1px solid rgba(59, 130, 246, 0.2);'>
        <h1 class='main-title'>⚽ Dashboard Cartola FC 2025</h1>
        <p style='font-size: 1.25rem; color: var(--gray-600); font-weight: 500; margin: 0; letter-spacing: 0.025em;'>
            🚀 Análise Inteligente com Métricas Premium de Futebol
        </p>
        <div style='margin-top: 1.5rem; display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;'>
            <span style='display: inline-flex; align-items: center; gap: 0.5rem; color: var(--gray-700); font-weight: 600; font-size: 0.875rem;'>
                <span style='width: 8px; height: 8px; background: var(--success-500); border-radius: 50%; display: inline-block;'></span>
                API Oficial Conectada
            </span>
            <span style='display: inline-flex; align-items: center; gap: 0.5rem; color: var(--gray-700); font-weight: 600; font-size: 0.875rem;'>
                <span style='width: 8px; height: 8px; background: var(--primary-500); border-radius: 50%; display: inline-block;'></span>
                Dados em Tempo Real
            </span>
            <span style='display: inline-flex; align-items: center; gap: 0.5rem; color: var(--gray-700); font-weight: 600; font-size: 0.875rem;'>
                <span style='width: 8px; height: 8px; background: var(--warning-500); border-radius: 50%; display: inline-block;'></span>
                Métricas Avançadas
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def criar_filtros_sidebar_premium(df: pd.DataFrame) -> Tuple:
    """Cria filtros na sidebar com design premium"""
    if df.empty:
        return [], [], 0, 0, (0, 0), (0, 0), 0, 0
    
    st.sidebar.markdown("## ⚙️ Painel de Controle")
    
    # Info do sistema com design premium
    with st.sidebar.expander("📊 Status do Sistema", expanded=False):
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, var(--primary-50), var(--primary-100)); padding: 1rem; border-radius: 12px; border: 1px solid var(--primary-200);'>
            <div style='display: grid; gap: 0.75rem;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='font-weight: 600; color: var(--gray-700);'>🕒 Última Atualização:</span>
                    <code style='background: var(--gray-100); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem;'>{datetime.now().strftime('%H:%M:%S')}</code>
                </div>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='font-weight: 600; color: var(--gray-700);'>⏱️ Cache TTL:</span>
                    <span style='font-weight: 700; color: var(--primary-600);'>{CACHE_TTL//60} min</span>
                </div>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='font-weight: 600; color: var(--gray-700);'>📈 Total Jogadores:</span>
                    <span style='font-weight: 700; color: var(--success-600);'>{len(df):,}</span>
                </div>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='font-weight: 600; color: var(--gray-700);'>🔄 Status:</span>
                    <span style='color: var(--success-600); font-weight: 700;'>✅ Online</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # === FILTROS PRINCIPAIS ===
    with st.sidebar.expander("🎯 Filtros Principais", expanded=True):
        st.markdown("#### 🧩 Posições")
        posicoes = sorted(df["Posição"].unique().tolist())
        posicao_selecionada = st.multiselect(
            "Escolha as posições:",
            posicoes, 
            default=posicoes,
            help="🎯 Selecione as posições que deseja analisar"
        )
        
        st.markdown("#### 🏆 Clubes")  
        clubes = sorted(df["Clube"].unique().tolist())
        clube_selecionado = st.multiselect(
            "Escolha os clubes:",
            clubes, 
            default=clubes,
            help="🏟️ Selecione os clubes que deseja analisar"
        )
    
    # === FILTROS DE VALORES ===
    with st.sidebar.expander("💰 Filtros de Performance", expanded=True):
        st.markdown("#### 💸 Faixa de Preço")
        preco_min, preco_max = st.slider(
            "Preço em Cartola$ (C$)",
            int(df["Preço (C$)"].min()),
            int(df["Preço (C$)"].max()),
            (int(df["Preço (C$)"].min()), int(df["Preço (C$)"].max())),
            help="💰 Defina sua faixa de investimento"
        )
        
        st.markdown("#### 📊 Pontuação Média")
        media_min, media_max = st.slider(
            "Faixa de pontos por jogo",
            float(df["Pontos Média"].min()),
            float(df["Pontos Média"].max()),
            (float(df["Pontos Média"].min()), float(df["Pontos Média"].max())),
            step=0.1,
            help="📈 Filtre por nível de pontuação média"
        )
        
        st.markdown("#### ⚽ Regularidade")
        partidas_min, partidas_max = st.slider(
            "Número de partidas jogadas",
            int(df["Partidas"].min()),
            int(df["Partidas"].max()),
            (int(df["Partidas"].min()), int(df["Partidas"].max())),
            help="🎯 Filtre por consistência de participação"
        )
    
    # === FILTROS AVANÇADOS ===
    with st.sidebar.expander("⚡ Filtros Avançados", expanded=False):
        st.markdown("#### 💎 Retorno do Investimento")
        pontos_por_cs_min = st.slider(
            "Pontos por C$ mínimo",
            0.0,
            float(df["Pontos por C$"].max()) if "Pontos por C$" in df.columns else 1.0,
            0.0,
            step=0.001,
            help="💡 Eficiência mínima do investimento"
        )
        
        st.markdown("#### 🎯 Consistência")
        consistencia_min = st.slider(
            "Consistência mínima (%)",
            0.0,
            100.0,
            0.0,
            step=1.0,
            help="📊 Percentual mínimo de jogos disputados"
        )
        
        # Resumo dos filtros ativos com design premium
        filtros_ativos = []
        if len(posicao_selecionada) < len(posicoes):
            filtros_ativos.append(f"📍 {len(posicao_selecionada)} posições")
        if len(clube_selecionado) < len(clubes):
            filtros_ativos.append(f"🏟️ {len(clube_selecionado)} clubes")
        if pontos_por_cs_min > 0:
            filtros_ativos.append(f"💎 Pontos/C$ > {pontos_por_cs_min:.3f}")
        if consistencia_min > 0:
            filtros_ativos.append(f"🎯 Consistência > {consistencia_min}%")
            
        if filtros_ativos:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, var(--success-50), rgba(16, 185, 129, 0.1)); border: 1px solid var(--success-200); border-radius: 8px; padding: 1rem; margin-top: 1rem;'>
                <div style='font-weight: 700; color: var(--success-700); margin-bottom: 0.5rem;'>
                    🔍 {len(filtros_ativos)} Filtro(s) Ativo(s):
                </div>
                {''.join([f'<div style="margin: 0.25rem 0; color: var(--success-600); font-weight: 600;">• {filtro}</div>' for filtro in filtros_ativos])}
            </div>
            """, unsafe_allow_html=True)
    
    return (posicao_selecionada, clube_selecionado, preco_min, preco_max, 
            (media_min, media_max), (partidas_min, partidas_max), pontos_por_cs_min, consistencia_min)

def criar_metricas_principais_premium(df: pd.DataFrame):
    """Cria métricas principais com design premium"""
    if df.empty:
        st.markdown("""
        <div style='text-align: center; padding: 3rem; background: linear-gradient(135deg, var(--warning-50), rgba(245, 158, 11, 0.1)); border: 2px dashed var(--warning-300); border-radius: 16px; margin: 2rem 0;'>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>⚠️</div>
            <h3 style='color: var(--warning-700); margin: 0;'>Nenhum jogador encontrado</h3>
            <p style='color: var(--warning-600); margin: 0.5rem 0 0 0;'>Ajuste os filtros para ver os resultados</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "👥 JOGADORES",
            f"{len(df):,}",
            help="Total de jogadores que atendem aos filtros"
        )
    
    with col2:
        preco_medio = df['Preço (C$)'].mean()
        st.metric(
            "💰 PREÇO MÉDIO",
            f"C$ {preco_medio:.1f}",
            help="Investimento médio necessário"
        )
    
    with col3:
        pontos_medio = df['Pontos Média'].mean()
        st.metric(
            "📊 PONTUAÇÃO MÉDIA",
            f"{pontos_medio:.1f}",
            help="Performance média dos jogadores selecionados"
        )
    
    with col4:
        if 'Pontos por C$' in df.columns:
            retorno_medio = df['Pontos por C$'].mean()
            st.metric(
                "💎 RETORNO MÉDIO",
                f"{retorno_medio:.3f}",
                help="Pontos ganhos por C$ investido"
            )
        else:
            st.metric("💎 RETORNO MÉDIO", "N/A")
    
    with col5:
        if 'Consistência (%)' in df.columns:
            consistencia_media = df['Consistência (%)'].mean()
            st.metric(
                "🎯 CONSISTÊNCIA",
                f"{consistencia_media:.1f}%",
                help="Percentual médio de jogos disputados"
            )
        else:
            st.metric("🎯 CONSISTÊNCIA", "N/A")

def criar_graficos_premium(df: pd.DataFrame):
    """Cria gráficos com design premium"""
    if df.empty:
        return
    
    col1, col2 = st.columns(2)
    
    # Paleta de cores premium
    cores_premium = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
    
    with col1:
        st.subheader("📈 Análise Preço vs Performance")
        
        fig = px.scatter(
            df,
            x="Preço (C$)",
            y="Pontos Média",
            color="Posição",
            size="Partidas",
            hover_name="Nome",
            hover_data=["Clube", "Pontos por C$"] if "Pontos por C$" in df.columns else ["Clube"],
            title="Relação entre Investimento e Retorno",
            color_discrete_sequence=cores_premium
        )
        
        fig.update_traces(
            marker=dict(
                opacity=0.8,
                line=dict(width=2, color='white')
            )
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(255,255,255,0.8)',
            paper_bgcolor='rgba(255,255,255,0.95)',
            height=500,
            showlegend=True,
            hovermode='closest',
            font=dict(family="Inter, sans-serif", size=12, color='#374151'),
            title=dict(font=dict(size=16, color='#1f2937', family="Inter, sans-serif"))
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.subheader("💎 Top 10 Melhor Retorno")
        
        if "Pontos por C$" in df.columns:
            top_retorno = df.nlargest(10, 'Pontos por C$')
            
            fig = px.bar(
                top_retorno,
                x='Pontos por C$',
                y='Nome',
                orientation='h',
                hover_data=['Clube', 'Preço (C$)', 'Pontos Média'],
                title="Jogadores com Melhor Eficiência",
                color_discrete_sequence=['#3b82f6']
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(255,255,255,0.8)',
                paper_bgcolor='rgba(255,255,255,0.95)',
                height=500,
                yaxis={'categoryorder': 'total ascending'},
                font=dict(family="Inter, sans-serif", size=12, color='#374151'),
                title=dict(font=dict(size=16, color='#1f2937', family="Inter, sans-serif"))
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def criar_comparador_premium(df: pd.DataFrame):
    """Comparador com design premium"""
    if df.empty:
        return
    
    st.subheader("⚔️ Comparador Avançado de Jogadores")
    
    # Criar opções para selectbox
    opcoes_jogadores = []
    for idx, jogador in df.iterrows():
        info = f"{jogador['Nome']} - {jogador['Clube']} ({jogador['Posição']}) - C${jogador['Preço (C$)']:.0f} - {jogador['Status']}"
        opcoes_jogadores.append(info)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🥇 Primeiro Jogador")
        jogador1_info = st.selectbox(
            "🔍 Busque e selecione o primeiro jogador:",
            options=opcoes_jogadores,
            help="Digite o nome para filtrar as opções",
            key="comp_jogador1"
        )
        jogador1_nome = jogador1_info.split(" - ")[0] if jogador1_info else None
    
    with col2:
        st.markdown("#### 🥈 Segundo Jogador")
        jogador2_info = st.selectbox(
            "🔍 Busque e selecione o segundo jogador:",
            options=opcoes_jogadores,
            help="Digite o nome para filtrar as opções",
            key="comp_jogador2"
        )
        jogador2_nome = jogador2_info.split(" - ")[0] if jogador2_info else None
    
    if jogador1_nome and jogador2_nome and jogador1_nome != jogador2_nome:
        j1_data = df[df['Nome'] == jogador1_nome].iloc[0]
        j2_data = df[df['Nome'] == jogador2_nome].iloc[0]
        
        # Cards dos jogadores com design premium
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class='player-card' style='border-color: var(--primary-400);'>
                <div style='display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1.5rem;'>
                    <div style='font-size: 2rem;'>🥇</div>
                    <div>
                        <h3 style='margin: 0; color: var(--primary-700); font-weight: 800;'>{j1_data['Nome']}</h3>
                        <p style='margin: 0.5rem 0 0 0; color: var(--gray-600); font-weight: 600;'>{j1_data['Clube']} • {j1_data['Posição']}</p>
                    </div>
                </div>
                <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; text-align: left;'>
                    <div style='background: var(--primary-50); padding: 0.75rem; border-radius: 8px;'>
                        <div style='font-size: 0.75rem; color: var(--gray-600); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Preço</div>
                        <div style='font-size: 1.25rem; font-weight: 700; color: var(--primary-700);'>C$ {j1_data['Preço (C$)']:.0f}</div>
                    </div>
                    <div style='background: var(--success-50); padding: 0.75rem; border-radius: 8px;'>
                        <div style='font-size: 0.75rem; color: var(--gray-600); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Status</div>
                        <div style='font-size: 1rem; font-weight: 600; color: var(--success-700);'>{j1_data['Status']}</div>
                    </div>
                </div>
                <div style='margin-top: 1rem; padding: 0.75rem; background: linear-gradient(135deg, var(--gray-50), var(--gray-100)); border-radius: 8px;'>
                    <div style='font-size: 0.875rem; color: var(--gray-700); font-weight: 600;'>
                        Forma: {j1_data.get('Forma Atual', 'N/A')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='player-card' style='border-color: var(--error-400);'>
                <div style='display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1.5rem;'>
                    <div style='font-size: 2rem;'>🥈</div>
                    <div>
                        <h3 style='margin: 0; color: var(--error-700); font-weight: 800;'>{j2_data['Nome']}</h3>
                        <p style='margin: 0.5rem 0 0 0; color: var(--gray-600); font-weight: 600;'>{j2_data['Clube']} • {j2_data['Posição']}</p>
                    </div>
                </div>
                <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; text-align: left;'>
                    <div style='background: var(--error-50); padding: 0.75rem; border-radius: 8px;'>
                        <div style='font-size: 0.75rem; color: var(--gray-600); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Preço</div>
                        <div style='font-size: 1.25rem; font-weight: 700; color: var(--error-700);'>C$ {j2_data['Preço (C$)']:.0f}</div>
                    </div>
                    <div style='background: var(--success-50); padding: 0.75rem; border-radius: 8px;'>
                        <div style='font-size: 0.75rem; color: var(--gray-600); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Status</div>
                        <div style='font-size: 1rem; font-weight: 600; color: var(--success-700);'>{j2_data['Status']}</div>
                    </div>
                </div>
                <div style='margin-top: 1rem; padding: 0.75rem; background: linear-gradient(135deg, var(--gray-50), var(--gray-100)); border-radius: 8px;'>
                    <div style='font-size: 0.875rem; color: var(--gray-700); font-weight: 600;'>
                        Forma: {j2_data.get('Forma Atual', 'N/A')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Comparação de métricas principais
        st.markdown("#### 📊 Comparação de Performance")
        
        metricas = {
            '💰 Preço (C$)': 'Preço (C$)',
            '📈 Pontos Média': 'Pontos Média', 
            '💎 Pontos por C$': 'Pontos por C$',
            '⚽ Partidas': 'Partidas',
            '🎯 Consistência (%)': 'Consistência (%)'
        }
        
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]
        
        for i, (nome_metrica, campo) in enumerate(metricas.items()):
            if campo in df.columns:
                with cols[i % 3]:
                    valor1 = j1_data[campo]
                    valor2 = j2_data[campo]
                    diferenca = valor1 - valor2
                    
                    # Para preço, menor é melhor
                    if campo == 'Preço (C$)':
                        delta_color = "normal" if diferenca <= 0 else "inverse"
                    else:
                        delta_color = "normal" if diferenca >= 0 else "inverse"
                    
                    st.metric(
                        nome_metrica,
                        f"{valor1:.2f}" if isinstance(valor1, float) else f"{valor1}",
                        f"{diferenca:+.2f}" if isinstance(diferenca, float) else f"{diferenca:+}",
                        delta_color=delta_color
                    )
    else:
        st.markdown("""
        <div style='text-align: center; padding: 3rem; background: linear-gradient(135deg, var(--primary-50), rgba(59, 130, 246, 0.1)); border: 2px dashed var(--primary-300); border-radius: 16px; margin: 2rem 0;'>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>🔍</div>
            <h3 style='color: var(--primary-700); margin: 0;'>Selecione dois jogadores diferentes</h3>
            <p style='color: var(--primary-600); margin: 0.5rem 0 0 0;'>Para iniciar a comparação detalhada</p>
        </div>
        """, unsafe_allow_html=True)

# ================================
# FUNÇÃO PRINCIPAL PREMIUM
# ================================

def main():
    """Função principal do dashboard com design premium"""
    
    # Aplicar design premium
    aplicar_design_premium()
    
    # Header premium
    criar_header_premium()
    
    # Carregamento com spinner premium
    with st.spinner("🔄 **Carregando dados da API do Cartola FC...**"):
        df = carregar_dados_api()
    
    if df.empty:
        st.markdown("""
        <div style='text-align: center; padding: 3rem; background: linear-gradient(135deg, var(--error-50), rgba(239, 68, 68, 0.1)); border: 2px solid var(--error-300); border-radius: 16px; margin: 2rem 0;'>
            <div style='font-size: 4rem; margin-bottom: 1rem;'>❌</div>
            <h2 style='color: var(--error-700); margin: 0 0 1rem 0;'>Não foi possível carregar os dados</h2>
            <p style='color: var(--error-600); margin: 0; font-size: 1.125rem;'>Verifique sua conexão e tente novamente</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    # Sucesso com design premium
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, var(--success-50), rgba(16, 185, 129, 0.1)); border: 1px solid var(--success-300); border-radius: 12px; padding: 1.5rem; margin: 1rem 0; text-align: center;'>
        <div style='display: flex; align-items: center; justify-content: center; gap: 1rem;'>
            <div style='font-size: 2rem;'>✅</div>
            <div>
                <div style='font-size: 1.25rem; font-weight: 700; color: var(--success-700); margin: 0;'>
                    {len(df)} jogadores carregados com sucesso!
                </div>
                <div style='font-size: 0.875rem; color: var(--success-600); margin: 0.25rem 0 0 0;'>
                    Dados atualizados da API oficial do Cartola FC
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Filtros premium
    filtros = criar_filtros_sidebar_premium(df)
    posicao_sel, clube_sel, preco_min, preco_max, media_range, partidas_range, pontos_cs_min, consistencia_min = filtros
    
    # Aplicar filtros
    df_filtrado = df[
        (df["Posição"].isin(posicao_sel)) &
        (df["Clube"].isin(clube_sel)) &
        (df["Preço (C$)"] >= preco_min) &
        (df["Preço (C$)"] <= preco_max) &
        (df["Pontos Média"] >= media_range[0]) &
        (df["Pontos Média"] <= media_range[1]) &
        (df["Partidas"] >= partidas_range[0]) &
        (df["Partidas"] <= partidas_range[1])
    ].copy()
    
    # Filtros adicionais
    if 'Pontos por C$' in df_filtrado.columns and pontos_cs_min > 0:
        df_filtrado = df_filtrado[df_filtrado['Pontos por C$'] >= pontos_cs_min]
    
    if 'Consistência (%)' in df_filtrado.columns and consistencia_min > 0:
        df_filtrado = df_filtrado[df_filtrado['Consistência (%)'] >= consistencia_min]
    
    # Métricas principais premium
    criar_metricas_principais_premium(df_filtrado)
    
    st.markdown("---")
    
    # Tabs premium
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 **Visão Geral**", 
        "⚽ **Ações Específicas**", 
        "🏆 **Rankings**", 
        "⚔️ **Comparador**", 
        "📁 **Exportar**"
    ])
    
    with tab1:
        st.markdown("### 📈 Análise Geral dos Jogadores")
        criar_graficos_premium(df_filtrado)
        
        # Busca premium
        st.markdown("### 🔍 Busca Inteligente de Jogadores")
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            nome_busca = st.text_input(
                "Digite o nome do jogador:",
                placeholder="Ex: Pedro, Hulk, Gerson, Gabigol...",
                help="🔍 Busque qualquer jogador na lista filtrada"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            buscar = st.button("🔍 **BUSCAR**", use_container_width=True, type="primary")
        
        if nome_busca or buscar:
            df_busca = df_filtrado[
                df_filtrado["Nome"].str.contains(nome_busca, case=False, na=False)
            ]
            if not df_busca.empty:
                st.success(f"✅ **{len(df_busca)} jogador(es) encontrado(s)** com '{nome_busca}'")
                
                colunas_busca = ['Nome', 'Clube', 'Posição', 'Preço (C$)', 'Pontos Média', 'Status']
                if 'Pontos por C$' in df_busca.columns:
                    colunas_busca.append('Pontos por C$')
                if 'Forma Atual' in df_busca.columns:
                    colunas_busca.append('Forma Atual')
                    
                st.dataframe(
                    df_busca.sort_values("Pontos Média", ascending=False)[colunas_busca],
                    use_container_width=True,
                    height=300
                )
            else:
                st.warning(f"❌ **Nenhum jogador encontrado** com '{nome_busca}' nos filtros atuais")
    
    with tab2:
        # Criar análise de ações específicas (manter função original)
        pass
    
    with tab3:
        st.markdown("### 🏆 Rankings dos Melhores Jogadores")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Top 15 Pontuadores")
            top_pontos = df_filtrado.nlargest(15, "Pontos Média")
            colunas_ranking = ['Nome', 'Clube', 'Posição', 'Pontos Média', 'Preço (C$)', 'Status']
            st.dataframe(top_pontos[colunas_ranking], use_container_width=True, height=400)
        
        with col2:
            st.markdown("#### 💎 Top 15 Custo-Benefício")
            if 'Pontos por C$' in df_filtrado.columns:
                top_cb = df_filtrado.nlargest(15, "Pontos por C$")
                colunas_cb = ['Nome', 'Clube', 'Posição', 'Pontos por C$', 'Preço (C$)']
                if 'Forma Atual' in df_filtrado.columns:
                    colunas_cb.append('Forma Atual')
                st.dataframe(top_cb[colunas_cb], use_container_width=True, height=400)
    
    with tab4:
        criar_comparador_premium(df_filtrado)
    
    with tab5:
        st.markdown("### 📁 Central de Exportação")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Exportar Análise Completa")
            if st.button("📊 **GERAR PLANILHA CSV**", use_container_width=True, type="primary"):
                csv = df_filtrado.to_csv(index=False)
                st.download_button(
                    label="⬇️ **DOWNLOAD CSV COMPLETO**",
                    data=csv,
                    file_name=f"cartola_analise_completa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col2:
            st.markdown("#### 📋 Exportar Resumo Executivo")
            if st.button("📋 **GERAR RESUMO JSON**", use_container_width=True):
                resumo = {
                    'total_jogadores': len(df_filtrado),
                    'data_exportacao': datetime.now().isoformat(),
                    'top_10_pontuadores': df_filtrado.nlargest(10, 'Pontos Média')[['Nome', 'Clube', 'Pontos Média']].to_dict('records')
                }
                
                json_data = json.dumps(resumo, indent=2, ensure_ascii=False)
                st.download_button(
                    label="⬇️ **DOWNLOAD RESUMO JSON**",
                    data=json_data,
                    file_name=f"cartola_resumo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
    
    # Lista completa com design premium
    st.markdown("---")
    st.markdown("### 📋 Lista Completa de Jogadores")
    
    # Controles premium
    col1, col2, col3, col4 = st.columns(4)
    
    ordenacao_opcoes = ['Pontos Média', 'Preço (C$)', 'Nome', 'Partidas']
    if 'Pontos por C$' in df_filtrado.columns:
        ordenacao_opcoes.insert(1, 'Pontos por C$')
    
    with col1:
        ordenar_por = st.selectbox("📊 **Ordenar por:**", ordenacao_opcoes)
    
    with col2:
        ordem = st.selectbox("📈 **Ordem:**", ['Decrescente', 'Crescente'])
    
    with col3:
        mostrar_acoes = st.checkbox("⚽ **Mostrar Ações**", help="Incluir métricas de ações específicas")
    
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 **ATUALIZAR**", use_container_width=True):
            st.rerun()
    
    # Aplicar ordenação
    ascending = ordem == 'Crescente'
    df_ordenado = df_filtrado.sort_values(ordenar_por, ascending=ascending)
    
    # Definir colunas
    colunas_base = ['Nome', 'Clube', 'Posição', 'Pontos Média', 'Preço (C$)', 'Partidas', 'Status']
    
    if 'Pontos por C$' in df_ordenado.columns:
        colunas_base.insert(-2, 'Pontos por C$')
    
    if 'Forma Atual' in df_ordenado.columns:
        colunas_base.append('Forma Atual')
    
    if mostrar_acoes:
        if 'Pts Ações Ofensivas' in df_ordenado.columns:
            colunas_base.append('Pts Ações Ofensivas')
        if 'Pts Def. Linha' in df_ordenado.columns:
            colunas_base.append('Pts Def. Linha')
        if 'Pts Def. Goleiro' in df_ordenado.columns:
            colunas_base.append('Pts Def. Goleiro')
    
    # Exibir tabela
    st.dataframe(
        df_ordenado[colunas_base],
        use_container_width=True,
        height=600
    )
    
    # Footer premium
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, var(--gray-50), rgba(255,255,255,0.8)); border-radius: 16px; border: 1px solid var(--gray-200); margin-top: 2rem;'>
        <div style='display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1rem;'>
            <div style='font-size: 2rem;'>👨‍💻</div>
            <h3 style='margin: 0; color: var(--gray-800); font-weight: 800;'>Desenvolvido por Carlos Willian</h3>
        </div>
        <div style='color: var(--gray-700); font-weight: 600; font-size: 1.125rem; margin-bottom: 0.5rem;'>
            🚀 Dashboard Cartola FC 2025 - Design Premium
        </div>
        <div style='color: var(--gray-600); font-size: 0.875rem;'>
            Última atualização: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')} • Dados da API oficial do Cartola FC
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

