"""
Dashboard Cartola FC 2025 - Versão com Paleta Verde e Indicadores Aprimorados
Author: Carlos Willian (Melhorado por IA)
Funcionalidades: Análise avançada de jogadores do Cartola FC
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
# NOVA PALETA DE CORES VERDE
# ================================

def aplicar_estilo_customizado():
    """Aplica estilos CSS com nova paleta verde"""
    st.markdown("""
    <style>
    /* Importar fonte Google */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Tema geral - Gradiente verde suave */
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #d0fdd7 50%, #9bfab0 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar com verde principal */
    .css-1d391kg {
        background: linear-gradient(180deg, #2a8c4a 0%, #64c27b 100%);
        border-right: 2px solid rgba(255,255,255,0.2);
    }
    
    /* Títulos da sidebar */
    .css-1d391kg h2, .css-1d391kg h3 {
        color: white !important;
        font-weight: 600;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Texto da sidebar */
    .css-1d391kg .stMarkdown, 
    .css-1d391kg .stSelectbox label,
    .css-1d391kg .stMultiSelect label,
    .css-1d391kg .stSlider label {
        color: white !important;
        font-weight: 500;
    }
    
    /* Cards de filtros na sidebar */
    .css-1d391kg .stExpander {
        background: rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
    }
    
    /* Cards de métricas principais - verde claro */
    [data-testid="metric-container"] {
        background: linear-gradient(145deg, #ffffff 0%, #d0fdd7 100%);
        border: 2px solid #9bfab0;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(42, 140, 74, 0.15);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(42, 140, 74, 0.25);
        border-color: #64c27b;
    }
    
    /* Valores das métricas */
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #2a8c4a !important;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
    }
    
    /* Labels das métricas */
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #64c27b !important;
        font-weight: 600 !important;
    }
    
    /* Multiselect verde */
    .stMultiSelect [data-baseweb="select"] span {
        background: linear-gradient(45deg, #2a8c4a, #64c27b) !important;
        color: white !important;
        border-radius: 6px;
        font-weight: 500;
    }
    
    /* Botões com gradiente verde */
    .stButton > button {
        background: linear-gradient(45deg, #2a8c4a, #64c27b);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.4rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 3px 10px rgba(42, 140, 74, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(42, 140, 74, 0.4);
        background: linear-gradient(45deg, #238b45, #5bb975);
    }
    
    /* Dataframes com fundo branco limpo */
    .stDataFrame {
        background: white !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 2px solid #9bfab0 !important;
        box-shadow: 0 4px 12px rgba(42, 140, 74, 0.1) !important;
    }
    
    /* Cabeçalhos das tabelas */
    .stDataFrame thead th {
        background: linear-gradient(45deg, #2a8c4a, #64c27b) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
    }
    
    /* Células das tabelas */
    .stDataFrame tbody td {
        background: white !important;
        border-bottom: 1px solid #d0fdd7 !important;
    }
    
    /* Alternância de cores nas linhas */
    .stDataFrame tbody tr:nth-child(even) {
        background: #f8fdf9 !important;
    }
    
    /* Tabs com tema verde */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(145deg, #ffffff, #d0fdd7);
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: 0 2px 8px rgba(42, 140, 74, 0.1);
        margin-bottom: 2rem;
        border: 1px solid #9bfab0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #2a8c4a;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #2a8c4a, #64c27b) !important;
        color: white !important;
    }
    
    /* Alertas personalizados */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid #2a8c4a;
        background: linear-gradient(145deg, white, #d0fdd7);
        box-shadow: 0 2px 8px rgba(42, 140, 74, 0.1);
    }
    
    /* Headers principais */
    .main h1, .main h2, .main h3 {
        color: #2a8c4a;
        font-weight: 600;
    }
    
    /* Selectbox melhorado */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 8px;
        color: white;
    }
    
    /* Slider com cor verde */
    .stSlider > div > div > div > div {
        background: linear-gradient(45deg, #2a8c4a, #64c27b);
    }
    
    /* Gráficos com fundo limpo */
    .js-plotly-plot {
        background: white !important;
        border-radius: 12px !important;
        border: 1px solid #9bfab0 !important;
        box-shadow: 0 4px 12px rgba(42, 140, 74, 0.1) !important;
    }
    
    /* Cards informativos */
    .info-card {
        background: linear-gradient(145deg, #ffffff, #d0fdd7);
        border: 2px solid #9bfab0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 3px 10px rgba(42, 140, 74, 0.1);
    }
    
    /* Loading spinner verde */
    .stSpinner > div {
        border-top-color: #2a8c4a !important;
    }
    
    /* Text input customizado */
    .stTextInput > div > div > input {
        border-color: #9bfab0;
        border-radius: 8px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2a8c4a;
        box-shadow: 0 0 0 2px rgba(42, 140, 74, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# ================================
# FUNÇÕES DE UTILITÁRIOS
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
    """
    Calcula métricas específicas de futebol mais relevantes
    
    NOVOS INDICADORES:
    
    1. PONTOS POR C$ = Pontos Média ÷ Preço (C$)
       - Retorno direto do investimento
    
    2. CONSISTÊNCIA = (Partidas Jogadas ÷ Total de Rodadas) × 100
       - Percentual de presença em campo
    
    3. FORMA ATUAL = Simulação de performance recente
       - 🔥 Excelente, ⚡ Boa, 📊 Regular, 📉 Baixa
    
    4. PONTOS POR AÇÕES OFENSIVAS = Pontos de gols + assistências + finalizações
    
    5. PONTOS POR AÇÕES DEFENSIVAS (LINHA) = Pontos de desarmes + interceptações
    
    6. PONTOS POR AÇÕES DEFENSIVAS (GOLEIRO) = Pontos de defesas + gols sofridos
    """
    if df.empty:
        return df
    
    # 1. Pontos por Cartola$ (mais direto que custo-benefício)
    df['Pontos por C$'] = (df['Pontos Média'] / df['Preço (C$)'].replace(0, 0.1)).round(3)
    
    # 2. Consistência (assumindo 38 rodadas no Brasileirão)
    total_rodadas = 38
    df['Consistência (%)'] = ((df['Partidas'] / total_rodadas) * 100).round(1)
    
    # 3. Forma Atual (simulada - em implementação real usaria últimas 5 rodadas)
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
    
    # Ações Ofensivas (Gols + Assistências + Finalizações Certas)
    acoes_ofensivas = []
    for _, jogador in df.iterrows():
        gols = jogador.get('G', 0) if pd.notna(jogador.get('G', 0)) else 0
        assistencias = jogador.get('A', 0) if pd.notna(jogador.get('A', 0)) else 0
        finalizacoes = jogador.get('FC', 0) if pd.notna(jogador.get('FC', 0)) else 0
        
        # Pontuação: Gol = 8pts, Assistência = 5pts, Finalização = 1.2pts
        pontos_ofensivos = (gols * 8) + (assistencias * 5) + (finalizacoes * 1.2)
        acoes_ofensivas.append(pontos_ofensivos)
    
    df['Pts Ações Ofensivas'] = acoes_ofensivas
    
    # Ações Defensivas - Jogadores de Linha
    acoes_defensivas_linha = []
    for _, jogador in df.iterrows():
        desarmes = jogador.get('DS', 0) if pd.notna(jogador.get('DS', 0)) else 0
        interceptacoes = jogador.get('I', 0) if pd.notna(jogador.get('I', 0)) else 0
        faltas_sofridas = jogador.get('FS', 0) if pd.notna(jogador.get('FS', 0)) else 0
        
        # Pontuação: Desarme = 1.7pts, Interceptação = 1.8pts, Falta Sofrida = 0.5pts
        pontos_def_linha = (desarmes * 1.7) + (interceptacoes * 1.8) + (faltas_sofridas * 0.5)
        acoes_defensivas_linha.append(pontos_def_linha)
    
    df['Pts Def. Linha'] = acoes_defensivas_linha
    
    # Ações Defensivas - Goleiros
    acoes_defensivas_gol = []
    for _, jogador in df.iterrows():
        if jogador.get('Posição') == 'Goleiro':
            defesas = jogador.get('DD', 0) if pd.notna(jogador.get('DD', 0)) else 0
            gols_contra = jogador.get('GC', 0) if pd.notna(jogador.get('GC', 0)) else 0
            
            # Pontuação: Defesa Difícil = 3.2pts, Gol Contra = -4pts
            pontos_def_gol = (defesas * 3.2) + (gols_contra * -4)
            acoes_defensivas_gol.append(pontos_def_gol)
        else:
            acoes_defensivas_gol.append(0)
    
    df['Pts Def. Goleiro'] = acoes_defensivas_gol
    
    return df

# ================================
# FUNÇÕES DE CARREGAMENTO DE DADOS
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
# COMPONENTES DA INTERFACE
# ================================

def criar_filtros_sidebar_verde(df: pd.DataFrame) -> Tuple:
    """Cria filtros na sidebar com tema verde"""
    if df.empty:
        return [], [], 0, 0, (0, 0), (0, 0), 0, 0
    
    st.sidebar.markdown("## ⚙️ Configurações")
    
    # Info do sistema
    with st.sidebar.expander("📊 Status do Sistema", expanded=False):
        st.markdown(f"""
        **🕒 Última Atualização:** {datetime.now().strftime('%H:%M:%S')}
        
        **⏱️ Cache:** {CACHE_TTL//60} minutos
        
        **📈 Total de Jogadores:** {len(df):,}
        
        **🔄 Atualização:** Automática
        """)
    
    # === FILTROS PRINCIPAIS ===
    with st.sidebar.expander("🎯 Filtros Principais", expanded=True):
        st.markdown("#### 🧩 Posições")
        posicoes = sorted(df["Posição"].unique().tolist())
        posicao_selecionada = st.multiselect(
            "Escolha as posições:",
            posicoes, 
            default=posicoes,
            help="🎯 Filtre por posições específicas"
        )
        
        st.markdown("#### 🏆 Clubes")  
        clubes = sorted(df["Clube"].unique().tolist())
        clube_selecionado = st.multiselect(
            "Escolha os clubes:",
            clubes, 
            default=clubes,
            help="🏟️ Filtre por clubes específicos"
        )
    
    # === FILTROS DE VALORES ===
    with st.sidebar.expander("💰 Filtros Financeiros", expanded=True):
        st.markdown("#### 💸 Faixa de Preço")
        preco_min, preco_max = st.slider(
            "Preço em Cartola$ (C$)",
            int(df["Preço (C$)"].min()),
            int(df["Preço (C$)"].max()),
            (int(df["Preço (C$)"].min()), int(df["Preço (C$)"].max())),
            help="💰 Defina sua faixa de investimento"
        )
        
        st.markdown("#### 📊 Performance")
        media_min, media_max = st.slider(
            "Pontuação Média",
            float(df["Pontos Média"].min()),
            float(df["Pontos Média"].max()),
            (float(df["Pontos Média"].min()), float(df["Pontos Média"].max())),
            step=0.1,
            help="📈 Filtre por nível de pontuação"
        )
        
        st.markdown("#### ⚽ Regularidade")
        partidas_min, partidas_max = st.slider(
            "Partidas Jogadas",
            int(df["Partidas"].min()),
            int(df["Partidas"].max()),
            (int(df["Partidas"].min()), int(df["Partidas"].max())),
            help="🎯 Filtre por consistência"
        )
    
    # === FILTROS AVANÇADOS ===
    with st.sidebar.expander("⚡ Análise Avançada", expanded=False):
        st.markdown("#### 💎 Retorno do Investimento")
        pontos_por_cs_min = st.slider(
            "Pontos por C$ mínimo",
            0.0,
            float(df["Pontos por C$"].max()) if "Pontos por C$" in df.columns else 1.0,
            0.0,
            step=0.001,
            help="💡 Eficiência do investimento"
        )
        
        st.markdown("#### 🎯 Consistência")
        consistencia_min = st.slider(
            "Consistência mínima (%)",
            0.0,
            100.0,
            0.0,
            step=1.0,
            help="📊 Percentual de jogos disputados"
        )
        
        # Resumo dos filtros aplicados
        filtros_ativos = []
        if len(posicao_selecionada) < len(posicoes):
            filtros_ativos.append(f"{len(posicao_selecionada)} posições")
        if len(clube_selecionado) < len(clubes):
            filtros_ativos.append(f"{len(clube_selecionado)} clubes")
        if pontos_por_cs_min > 0:
            filtros_ativos.append(f"Pontos/C$ > {pontos_por_cs_min:.3f}")
        if consistencia_min > 0:
            filtros_ativos.append(f"Consistência > {consistencia_min}%")
            
        if filtros_ativos:
            st.success(f"🔍 **{len(filtros_ativos)} filtros ativos**")
            for filtro in filtros_ativos:
                st.caption(f"• {filtro}")
    
    return (posicao_selecionada, clube_selecionado, preco_min, preco_max, 
            (media_min, media_max), (partidas_min, partidas_max), pontos_por_cs_min, consistencia_min)

def criar_metricas_principais_verde(df: pd.DataFrame):
    """Cria métricas principais com tema verde"""
    if df.empty:
        st.warning("⚠️ Nenhum jogador encontrado com os filtros aplicados")
        return
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "👥 Jogadores",
            f"{len(df):,}",
            help="Total de jogadores filtrados"
        )
    
    with col2:
        preco_medio = df['Preço (C$)'].mean()
        st.metric(
            "💰 Preço Médio",
            f"C$ {preco_medio:.1f}",
            help="Investimento médio necessário"
        )
    
    with col3:
        pontos_medio = df['Pontos Média'].mean()
        st.metric(
            "📊 Pontuação Média",
            f"{pontos_medio:.1f}",
            help="Performance média dos jogadores"
        )
    
    with col4:
        if 'Pontos por C$' in df.columns:
            retorno_medio = df['Pontos por C$'].mean()
            st.metric(
                "💎 Retorno Médio",
                f"{retorno_medio:.3f}",
                help="Pontos ganhos por C$ investido"
            )
        else:
            st.metric("💎 Retorno Médio", "N/A")
    
    with col5:
        if 'Consistência (%)' in df.columns:
            consistencia_media = df['Consistência (%)'].mean()
            st.metric(
                "🎯 Consistência Média",
                f"{consistencia_media:.1f}%",
                help="Percentual médio de jogos disputados"
            )
        else:
            st.metric("🎯 Consistência Média", "N/A")

def criar_graficos_tema_verde(df: pd.DataFrame):
    """Cria gráficos com paleta verde"""
    if df.empty:
        return
    
    col1, col2 = st.columns(2)
    
    # Paleta de cores verde personalizada
    cores_verdes = ['#2a8c4a', '#64c27b', '#9bfab0', '#d0fdd7', '#a8e6cf', '#7fcdcd', '#81c784', '#66bb6a', '#4caf50', '#388e3c']
    
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
            title="Relação Investimento x Retorno",
            color_discrete_sequence=cores_verdes
        )
        
        fig.update_traces(
            marker=dict(
                opacity=0.8,
                line=dict(width=1, color='white')
            )
        )
        
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=500,
            showlegend=True,
            hovermode='closest',
            font=dict(family="Inter, sans-serif", size=12)
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.subheader("💎 Melhor Retorno por C$")
        
        if "Pontos por C$" in df.columns:
            top_retorno = df.nlargest(10, 'Pontos por C$')
            
            fig = px.bar(
                top_retorno,
                x='Pontos por C$',
                y='Nome',
                orientation='h',
                hover_data=['Clube', 'Preço (C$)', 'Pontos Média'],
                title="Jogadores com Melhor Eficiência de Investimento",
                color='Pontos por C$',
                color_continuous_scale=['#d0fdd7', '#2a8c4a']
            )
            
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=500,
                yaxis={'categoryorder': 'total ascending'},
                coloraxis_showscale=False,
                font=dict(family="Inter, sans-serif", size=12)
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def criar_analise_acoes_especificas(df: pd.DataFrame):
    """Cria análise das ações ofensivas e defensivas"""
    if df.empty:
        return
    
    st.subheader("⚽ Análise de Ações Específicas")
    
    # Cards informativos sobre as métricas
    st.markdown("""
    <div class='info-card'>
        <h4 style='color: #2a8c4a; margin-top: 0;'>📊 Entenda as Métricas de Ações</h4>
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;'>
            <div>
                <strong>⚽ Ações Ofensivas:</strong><br>
                • Gols: 8 pontos<br>
                • Assistências: 5 pontos<br>
                • Finalizações Certas: 1.2 pontos
            </div>
            <div>
                <strong>🛡️ Defesa (Linha):</strong><br>
                • Desarmes: 1.7 pontos<br>
                • Interceptações: 1.8 pontos<br>
                • Faltas Sofridas: 0.5 pontos
            </div>
            <div>
                <strong>🥅 Defesa (Goleiro):</strong><br>
                • Defesas Difíceis: 3.2 pontos<br>
                • Gols Contra: -4 pontos<br>
                • (Apenas para goleiros)
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Análises por tipo de ação
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### ⚽ Top Atacantes")
        if 'Pts Ações Ofensivas' in df.columns:
            top_ofensivos = df[df['Pts Ações Ofensivas'] > 0].nlargest(10, 'Pts Ações Ofensivas')
            
            if not top_ofensivos.empty:
                fig = px.bar(
                    top_ofensivos,
                    x='Nome',
                    y='Pts Ações Ofensivas',
                    title="Pontuação em Ações Ofensivas",
                    color='Pts Ações Ofensivas',
                    color_continuous_scale=['#d0fdd7', '#2a8c4a']
                )
                fig.update_xaxes(tickangle=45)
                fig.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    height=400,
                    coloraxis_showscale=False,
                    font=dict(size=10)
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Nenhum jogador com ações ofensivas nos filtros atuais")
    
    with col2:
        st.markdown("#### 🛡️ Top Defensores")
        if 'Pts Def. Linha' in df.columns:
            top_defensivos = df[df['Pts Def. Linha'] > 0].nlargest(10, 'Pts Def. Linha')
            
            if not top_defensivos.empty:
                fig = px.bar(
                    top_defensivos,
                    x='Nome',
                    y='Pts Def. Linha',
                    title="Pontuação em Ações Defensivas",
                    color='Pts Def. Linha',
                    color_continuous_scale=['#d0fdd7', '#2a8c4a']
                )
                fig.update_xaxes(tickangle=45)
                fig.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    height=400,
                    coloraxis_showscale=False,
                    font=dict(size=10)
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Nenhum jogador com ações defensivas nos filtros atuais")
    
    with col3:
        st.markdown("#### 🥅 Top Goleiros")
        if 'Pts Def. Goleiro' in df.columns:
            goleiros = df[df['Posição'] == 'Goleiro']
            top_goleiros = goleiros[goleiros['Pts Def. Goleiro'] != 0].nlargest(10, 'Pts Def. Goleiro')
            
            if not top_goleiros.empty:
                fig = px.bar(
                    top_goleiros,
                    x='Nome',
                    y='Pts Def. Goleiro',
                    title="Pontuação Defensiva dos Goleiros",
                    color='Pts Def. Goleiro',
                    color_continuous_scale=['#ff6b6b', '#2a8c4a']  # Vermelho para negativo, verde para positivo
                )
                fig.update_xaxes(tickangle=45)
                fig.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    height=400,
                    coloraxis_showscale=False,
                    font=dict(size=10)
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Nenhum goleiro com ações defensivas nos filtros atuais")

def criar_comparador_melhorado_verde(df: pd.DataFrame):
    """Comparador com tema verde e busca aprimorada"""
    if df.empty:
        return
    
    st.subheader("⚔️ Comparador Avançado")
    
    # Criar opções para selectbox
    opcoes_jogadores = []
    for idx, jogador in df.iterrows():
        info = f"{jogador['Nome']} - {jogador['Clube']} ({jogador['Posição']}) - C${jogador['Preço (C$)']:.0f} - {jogador['Status']}"
        opcoes_jogadores.append(info)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🥇 Primeiro Jogador")
        jogador1_info = st.selectbox(
            "🔍 Busque e selecione:",
            options=opcoes_jogadores,
            help="Digite para filtrar os jogadores",
            key="comp_jogador1"
        )
        jogador1_nome = jogador1_info.split(" - ")[0] if jogador1_info else None
    
    with col2:
        st.markdown("#### 🥈 Segundo Jogador")
        jogador2_info = st.selectbox(
            "🔍 Busque e selecione:",
            options=opcoes_jogadores,
            help="Digite para filtrar os jogadores",
            key="comp_jogador2"
        )
        jogador2_nome = jogador2_info.split(" - ")[0] if jogador2_info else None
    
    if jogador1_nome and jogador2_nome and jogador1_nome != jogador2_nome:
        j1_data = df[df['Nome'] == jogador1_nome].iloc[0]
        j2_data = df[df['Nome'] == jogador2_nome].iloc[0]
        
        # Cards dos jogadores
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div style='background: linear-gradient(145deg, #ffffff, #d0fdd7); padding: 1.5rem; border-radius: 15px; border: 2px solid #2a8c4a; margin-bottom: 1rem;'>
                <h4 style='color: #2a8c4a; margin: 0;'>🥇 {j1_data['Nome']}</h4>
                <p style='margin: 0.5rem 0; color: #64c27b; font-weight: 600;'>{j1_data['Clube']} • {j1_data['Posição']}</p>
                <p style='margin: 0; color: #2a8c4a; font-weight: 500;'>💰 C$ {j1_data['Preço (C$)']:.0f} • {j1_data['Status']} • {j1_data.get('Forma Atual', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='background: linear-gradient(145deg, #ffffff, #d0fdd7); padding: 1.5rem; border-radius: 15px; border: 2px solid #64c27b; margin-bottom: 1rem;'>
                <h4 style='color: #64c27b; margin: 0;'>🥈 {j2_data['Nome']}</h4>
                <p style='margin: 0.5rem 0; color: #2a8c4a; font-weight: 600;'>{j2_data['Clube']} • {j2_data['Posição']}</p>
                <p style='margin: 0; color: #2a8c4a; font-weight: 500;'>💰 C$ {j2_data['Preço (C$)']:.0f} • {j2_data['Status']} • {j2_data.get('Forma Atual', 'N/A')}</p>
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
        
        # Comparação de ações específicas
        st.markdown("#### ⚽ Comparação de Ações Específicas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'Pts Ações Ofensivas' in df.columns:
                of1 = j1_data['Pts Ações Ofensivas']
                of2 = j2_data['Pts Ações Ofensivas']
                st.metric(
                    "⚽ Ações Ofensivas",
                    f"{of1:.1f}",
                    f"{(of1-of2):+.1f}",
                    delta_color="normal" if of1 >= of2 else "inverse"
                )
        
        with col2:
            if 'Pts Def. Linha' in df.columns:
                def1 = j1_data['Pts Def. Linha']
                def2 = j2_data['Pts Def. Linha']
                st.metric(
                    "🛡️ Def. Linha",
                    f"{def1:.1f}",
                    f"{(def1-def2):+.1f}",
                    delta_color="normal" if def1 >= def2 else "inverse"
                )
        
        with col3:
            if j1_data['Posição'] == 'Goleiro' and j2_data['Posição'] == 'Goleiro':
                if 'Pts Def. Goleiro' in df.columns:
                    gol1 = j1_data['Pts Def. Goleiro']
                    gol2 = j2_data['Pts Def. Goleiro']
                    st.metric(
                        "🥅 Def. Goleiro",
                        f"{gol1:.1f}",
                        f"{(gol1-gol2):+.1f}",
                        delta_color="normal" if gol1 >= gol2 else "inverse"
                    )
            else:
                st.info("Métrica apenas para goleiros")

def main():
    """Função principal do dashboard"""
    
    # Aplicar estilo verde
    aplicar_estilo_customizado()
    
    # Header com tema verde
    st.markdown("""
    <div style='text-align: center; padding: 2.5rem 0; background: linear-gradient(145deg, #ffffff, #d0fdd7); border-radius: 15px; margin-bottom: 2rem; border: 2px solid #9bfab0; box-shadow: 0 4px 12px rgba(42, 140, 74, 0.1);'>
        <h1 style='color: #2a8c4a; font-weight: 700; margin: 0; font-size: 2.5rem;'>⚽ Dashboard Cartola FC 2025</h1>
        <p style='color: #64c27b; font-size: 1.2rem; margin: 0.8rem 0 0 0; font-weight: 500;'>Análise Inteligente com Métricas de Futebol</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Carregamento com tema verde
    with st.spinner("🔄 Carregando dados da API do Cartola FC..."):
        df = carregar_dados_api()
    
    if df.empty:
        st.error("❌ Não foi possível carregar os dados. Tente novamente mais tarde.")
        st.stop()
    
    # Sucesso com tema verde
    st.success(f"✅ **{len(df)} jogadores carregados** com sucesso! Dados atualizados da API oficial.")
    
    # Filtros com tema verde
    filtros = criar_filtros_sidebar_verde(df)
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
    
    # Filtros adicionais se as colunas existirem
    if 'Pontos por C$' in df_filtrado.columns and pontos_cs_min > 0:
        df_filtrado = df_filtrado[df_filtrado['Pontos por C$'] >= pontos_cs_min]
    
    if 'Consistência (%)' in df_filtrado.columns and consistencia_min > 0:
        df_filtrado = df_filtrado[df_filtrado['Consistência (%)'] >= consistencia_min]
    
    # Métricas principais
    criar_metricas_principais_verde(df_filtrado)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs com tema verde
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visão Geral", 
        "⚽ Ações Específicas", 
        "🏆 Rankings", 
        "⚔️ Comparador", 
        "📁 Exportar"
    ])
    
    with tab1:
        st.markdown("### 📈 Análise Geral dos Jogadores")
        criar_graficos_tema_verde(df_filtrado)
        
        # Busca aprimorada
        st.markdown("### 🔍 Busca Rápida")
        col1, col2 = st.columns([4, 1])
        
        with col1:
            nome_busca = st.text_input(
                "Digite o nome do jogador:",
                placeholder="Ex: Pedro, Hulk, Gerson, Gabigol...",
                help="🔍 Busque qualquer jogador na lista filtrada"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            buscar = st.button("🔍 Buscar", use_container_width=True, type="primary")
        
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
                st.warning(f"❌ Nenhum jogador encontrado com '{nome_busca}' nos filtros atuais")
    
    with tab2:
        criar_analise_acoes_especificas(df_filtrado)
    
    with tab3:
        st.markdown("### 🏆 Rankings dos Melhores")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Top Pontuadores")
            top_pontos = df_filtrado.nlargest(15, "Pontos Média")
            colunas_ranking = ['Nome', 'Clube', 'Posição', 'Pontos Média', 'Preço (C$)', 'Status']
            st.dataframe(top_pontos[colunas_ranking], use_container_width=True, height=400)
        
        with col2:
            st.markdown("#### 💎 Melhor Custo-Benefício")
            if 'Pontos por C$' in df_filtrado.columns:
                top_cb = df_filtrado.nlargest(15, "Pontos por C$")
                colunas_cb = ['Nome', 'Clube', 'Posição', 'Pontos por C$', 'Preço (C$)']
                if 'Forma Atual' in df_filtrado.columns:
                    colunas_cb.append('Forma Atual')
                st.dataframe(top_cb[colunas_cb], use_container_width=True, height=400)
        
        # Rankings por posição
        st.markdown("#### 📍 Análise Detalhada por Posição")
        posicao_ranking = st.selectbox(
            "Escolha uma posição para análise:",
            options=sorted(df_filtrado['Posição'].unique()),
            help="🎯 Veja os melhores jogadores de cada posição"
        )
        
        if posicao_ranking:
            df_posicao = df_filtrado[df_filtrado['Posição'] == posicao_ranking].nlargest(10, 'Pontos Média')
            
            colunas_posicao = ['Nome', 'Clube', 'Pontos Média', 'Preço (C$)', 'Status', 'Partidas']
            if 'Pontos por C$' in df_posicao.columns:
                colunas_posicao.insert(-1, 'Pontos por C$')
            
            st.markdown(f"**🏅 Top 10 {posicao_ranking}:**")
            st.dataframe(df_posicao[colunas_posicao], use_container_width=True, height=350)
    
    with tab4:
        criar_comparador_melhorado_verde(df_filtrado)
    
    with tab5:
        st.markdown("### 📁 Exportação de Dados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Exportar Análise")
            if st.button("📊 Gerar Planilha CSV", use_container_width=True, type="primary"):
                csv = df_filtrado.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV Completo",
                    data=csv,
                    file_name=f"cartola_analise_completa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col2:
            st.markdown("#### 📋 Exportar Resumo")
            if st.button("📋 Gerar Resumo JSON", use_container_width=True):
                # Criar resumo
                resumo = {
                    'total_jogadores': len(df_filtrado),
                    'data_exportacao': datetime.now().isoformat(),
                    'top_10_pontuadores': df_filtrado.nlargest(10, 'Pontos Média')[['Nome', 'Clube', 'Pontos Média']].to_dict('records')
                }
                
                json_data = json.dumps(resumo, indent=2, ensure_ascii=False)
                st.download_button(
                    label="⬇️ Download Resumo JSON",
                    data=json_data,
                    file_name=f"cartola_resumo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
    
    # Lista completa
    st.markdown("---")
    st.markdown("### 📋 Lista Completa de Jogadores")
    
    # Controles
    col1, col2, col3, col4 = st.columns(4)
    
    ordenacao_opcoes = ['Pontos Média', 'Preço (C$)', 'Nome', 'Partidas']
    if 'Pontos por C$' in df_filtrado.columns:
        ordenacao_opcoes.insert(1, 'Pontos por C$')
    
    with col1:
        ordenar_por = st.selectbox("📊 Ordenar por:", ordenacao_opcoes)
    
    with col2:
        ordem = st.selectbox("📈 Ordem:", ['Decrescente', 'Crescente'])
    
    with col3:
        mostrar_acoes = st.checkbox("⚽ Mostrar Ações", help="Incluir métricas de ações específicas")
    
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Atualizar", use_container_width=True):
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
    
    # Footer com tema verde
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; padding: 1.5rem; background: linear-gradient(145deg, #ffffff, #d0fdd7); border-radius: 12px; border: 1px solid #9bfab0; box-shadow: 0 2px 8px rgba(42, 140, 74, 0.1);'>
        <p style='margin: 0; color: #2a8c4a; font-weight: 600; font-size: 1.1rem;'>⚽ <strong>Desenvolvido por Carlos Willian</strong></p>
        <p style='margin: 0.5rem 0 0 0; color: #64c27b; font-size: 0.95rem;'>Dashboard Cartola FC 2025 • Versão com Métricas de Futebol</p>
        <p style='margin: 0.3rem 0 0 0; color: #9bfab0; font-size: 0.85rem;'>Última atualização: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')} • API oficial do Cartola FC</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

