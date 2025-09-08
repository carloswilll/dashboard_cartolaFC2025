"""
Dashboard Cartola FC 2025 - Versão Melhorada com Interface Aprimorada
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

# Configuração da página
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
# ESTILO CUSTOMIZADO - NOVA PALETA
# ================================

def aplicar_estilo_customizado():
    """Aplica estilos CSS customizados com paleta roxa mais limpa"""
    st.markdown("""
    <style>
    /* Importar fonte Google */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Tema geral - Gradiente roxo mais suave */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar moderna */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        border-right: 2px solid rgba(255,255,255,0.1);
    }
    
    /* Título da sidebar */
    .css-1d391kg h2 {
        color: white !important;
        font-weight: 600;
        text-align: center;
        margin-bottom: 1.5rem;
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
    
    /* Cards de métricas principais */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #e1e5e9;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15);
    }
    
    /* Multiselect com cor roxa */
    .stMultiSelect [data-baseweb="select"] span {
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
        color: white !important;
        border-radius: 6px;
        font-weight: 500;
    }
    
    /* Botões modernos */
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        background: linear-gradient(45deg, #5a67d8, #6b46c1);
    }
    
    /* Dataframes com fundo branco limpo */
    .stDataFrame {
        background: white !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid #e1e5e9 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    
    /* Cabeçalhos das tabelas */
    .stDataFrame thead th {
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
    }
    
    /* Células das tabelas */
    .stDataFrame tbody td {
        background: white !important;
        border-bottom: 1px solid #f1f3f4 !important;
    }
    
    /* Alternância de cores nas linhas */
    .stDataFrame tbody tr:nth-child(even) {
        background: #f8f9fa !important;
    }
    
    /* Tabs modernas */
    .stTabs [data-baseweb="tab-list"] {
        background: white;
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #666;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
        color: white !important;
    }
    
    /* Alertas personalizados */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid #667eea;
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Headers principais */
    .main h1, .main h2, .main h3 {
        color: #2d3748;
        font-weight: 600;
    }
    
    /* Selectbox melhorado */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 8px;
        color: white;
    }
    
    /* Slider customizado */
    .stSlider > div > div > div > div {
        background: linear-gradient(45deg, #667eea, #764ba2);
    }
    
    /* Gráficos com fundo limpo */
    .js-plotly-plot {
        background: white !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    
    /* Cards de filtros */
    .filter-card {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
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
    """
    Faz requisição para API com retry e tratamento de erro
    """
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

def calcular_estatisticas_avancadas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula estatísticas avançadas dos jogadores
    
    INDICADORES EXPLICADOS:
    
    1. CUSTO-BENEFÍCIO = Pontos Média ÷ Preço (C$)
       - Mede quantos pontos você ganha por cada C$ investido
       - Exemplo: 8 pontos, C$ 10,00 = 0.8 pontos por C$
    
    2. EFICIÊNCIA = (Pontos Média × Partidas) ÷ Preço (C$)  
       - Considera consistência (partidas jogadas) + média
       - Favorece jogadores que jogam mais e mantêm boa média
    
    3. STATUS = Classificação baseada na Pontos Média:
       - 🔴 Baixo: < 2.0 pontos
       - 🟡 Regular: 2.0 - 4.9 pontos  
       - 🟢 Bom: 5.0 - 7.9 pontos
       - 🔵 Excelente: >= 8.0 pontos
    
    4. VALORIZAÇÃO = Simulado (precisa dados históricos)
       - Fórmula real: (Preço Atual - Preço Anterior) ÷ Preço Anterior × 100
    
    5. TENDÊNCIA = 📈 se Valorização > 0, senão 📉
    """
    if df.empty:
        return df
    
    # 1. Custo-Benefício: pontos por cartola$ investido
    df['Custo-Benefício'] = df['Pontos Média'] / df['Preço (C$)'].replace(0, 0.1)
    
    # 2. Eficiência: considera consistência (partidas) + média
    df['Eficiência'] = (df['Pontos Média'] * df['Partidas']) / df['Preço (C$)'].replace(0, 0.1)
    
    # 3. Valorização simulada (no mundo real usaria histórico de preços)
    np.random.seed(42)  # Para resultados consistentes
    df['Valorização (%)'] = np.random.normal(0, 8, len(df)).round(1)
    
    # 4. Tendência baseada na valorização
    df['Tendência'] = np.where(df['Valorização (%)'] > 0, '📈', '📉')
    
    # 5. Status baseado na pontuação média
    df['Status'] = pd.cut(
        df['Pontos Média'], 
        bins=[-np.inf, 2, 5, 8, np.inf], 
        labels=['🔴 Baixo', '🟡 Regular', '🟢 Bom', '🔵 Excelente']
    )
    
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
        
        # Estatísticas avançadas
        df = calcular_estatisticas_avancadas(df)
        
        return df
        
    except ApiException as e:
        st.error(f"❌ Erro na API: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro inesperado: {e}")
        return pd.DataFrame()

# ================================
# COMPONENTES DA INTERFACE - MELHORADOS
# ================================

def criar_filtros_sidebar_melhorados(df: pd.DataFrame) -> Tuple:
    """Cria filtros melhorados na sidebar com interface moderna"""
    if df.empty:
        return [], [], 0, 0, (0, 0), (0, 0), 0, 0
    
    st.sidebar.markdown("## ⚙️ Configurações Avançadas")
    
    # Info do sistema em card
    with st.sidebar.expander("ℹ️ Sistema", expanded=False):
        st.markdown(f"""
        <div class='filter-card'>
            <h4>📊 Status do Sistema</h4>
            <p><strong>🕒 Atualizado:</strong> {datetime.now().strftime('%H:%M:%S')}</p>
            <p><strong>⏱️ Cache:</strong> {CACHE_TTL//60} min</p>
            <p><strong>📈 Total:</strong> {len(df):,} jogadores</p>
        </div>
        """, unsafe_allow_html=True)
    
    # === FILTROS PRINCIPAIS ===
    with st.sidebar.expander("🎯 Filtros Principais", expanded=True):
        st.markdown("### 🧩 Posições")
        posicoes = sorted(df["Posição"].unique().tolist())
        posicao_selecionada = st.multiselect(
            "Selecione as posições:",
            posicoes, 
            default=posicoes,
            help="🎯 Escolha as posições que deseja analisar"
        )
        
        st.markdown("### 🏳️ Clubes")  
        clubes = sorted(df["Clube"].unique().tolist())
        clube_selecionado = st.multiselect(
            "Selecione os clubes:",
            clubes, 
            default=clubes,
            help="🏟️ Escolha os clubes que deseja analisar"
        )
    
    # === FILTROS DE VALORES ===
    with st.sidebar.expander("💰 Filtros de Preço e Performance", expanded=True):
        st.markdown("### 💸 Faixa de Preço")
        preco_min, preco_max = st.slider(
            "Preço em Cartola$ (C$)",
            int(df["Preço (C$)"].min()),
            int(df["Preço (C$)"].max()),
            (int(df["Preço (C$)"].min()), int(df["Preço (C$)"].max())),
            help="💰 Defina a faixa de preço dos jogadores"
        )
        
        st.markdown("### 📊 Pontuação Média")
        media_min, media_max = st.slider(
            "Faixa de pontos por jogo",
            float(df["Pontos Média"].min()),
            float(df["Pontos Média"].max()),
            (float(df["Pontos Média"].min()), float(df["Pontos Média"].max())),
            step=0.1,
            help="📈 Defina a pontuação média desejada"
        )
        
        st.markdown("### 🎯 Participação")
        partidas_min, partidas_max = st.slider(
            "Número de partidas jogadas",
            int(df["Partidas"].min()),
            int(df["Partidas"].max()),
            (int(df["Partidas"].min()), int(df["Partidas"].max())),
            help="⚽ Filtro de consistência do jogador"
        )
    
    # === FILTROS AVANÇADOS ===
    with st.sidebar.expander("🔬 Análise Avançada", expanded=False):
        st.markdown("### 💎 Custo-Benefício")
        cb_min = st.slider(
            "Custo-benefício mínimo",
            0.0,
            float(df["Custo-Benefício"].max()),
            0.0,
            step=0.01,
            help="💡 Pontos por C$ investido (quanto maior, melhor)"
        )
        
        st.markdown("### ⚡ Eficiência")
        eficiencia_min = st.slider(
            "Eficiência mínima",
            0.0,
            float(df["Eficiência"].max()),
            0.0,
            step=0.01,
            help="🎯 Considera média + consistência + preço"
        )
        
        # Resumo dos filtros
        filtros_ativos = []
        if len(posicao_selecionada) < len(posicoes):
            filtros_ativos.append(f"{len(posicao_selecionada)} posições")
        if len(clube_selecionado) < len(clubes):
            filtros_ativos.append(f"{len(clube_selecionado)} clubes")
        if cb_min > 0:
            filtros_ativos.append(f"CB > {cb_min}")
        if eficiencia_min > 0:
            filtros_ativos.append(f"Efic > {eficiencia_min}")
            
        if filtros_ativos:
            st.info(f"🔍 **Filtros ativos:** {', '.join(filtros_ativos)}")
    
    return (posicao_selecionada, clube_selecionado, preco_min, preco_max, 
            (media_min, media_max), (partidas_min, partidas_max), cb_min, eficiencia_min)

def criar_metricas_principais(df: pd.DataFrame):
    """Cria as métricas principais do dashboard"""
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
            help="Preço médio dos jogadores selecionados"
        )
    
    with col3:
        pontos_medio = df['Pontos Média'].mean()
        st.metric(
            "📊 Pontuação",
            f"{pontos_medio:.1f}",
            help="Pontuação média dos jogadores"
        )
    
    with col4:
        cb_medio = df['Custo-Benefício'].mean()
        st.metric(
            "💎 Custo-Benefício",
            f"{cb_medio:.2f}",
            help="Pontos por C$ investido (média)"
        )
    
    with col5:
        eficiencia_media = df['Eficiência'].mean()
        st.metric(
            "⚡ Eficiência",
            f"{eficiencia_media:.1f}",
            help="Média × Partidas ÷ Preço"
        )

def criar_graficos_limpos(df: pd.DataFrame):
    """Cria gráficos com fundo limpo e cores harmoniosas"""
    if df.empty:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Análise Preço vs Performance")
        
        fig = px.scatter(
            df,
            x="Preço (C$)",
            y="Pontos Média",
            color="Posição",
            size="Partidas",
            hover_name="Nome",
            hover_data=["Clube", "Custo-Benefício"],
            title="Relação entre Preço e Pontuação",
            color_discrete_sequence=px.colors.qualitative.Pastel1
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
        st.subheader("🏆 Top Custo-Benefício")
        
        top_cb = df.nlargest(10, 'Custo-Benefício')
        
        # Paleta de cores roxa personalizada
        cores_roxas = ['#667eea', '#764ba2', '#8b5cf6', '#a855f7', '#c084fc', 
                       '#d8b4fe', '#e879f9', '#f0abfc', '#f3e8ff', '#faf5ff']
        
        fig = px.bar(
            top_cb,
            x='Custo-Benefício',
            y='Nome',
            orientation='h',
            hover_data=['Clube', 'Preço (C$)', 'Pontos Média'],
            title="Melhor Retorno por Cartola$ Investido",
            color='Custo-Benefício',
            color_continuous_scale=['#f8f9fa', '#667eea']
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

def criar_comparador_melhorado(df: pd.DataFrame):
    """Comparador com selectbox pesquisável"""
    if df.empty:
        return
    
    st.subheader("⚔️ Comparador Avançado de Jogadores")
    
    # Criar lista para o selectbox com informações extras
    opcoes_jogadores = []
    for idx, jogador in df.iterrows():
        info = f"{jogador['Nome']} - {jogador['Clube']} ({jogador['Posição']}) - C${jogador['Preço (C$)']:.0f}"
        opcoes_jogadores.append(info)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🥇 Primeiro Jogador")
        jogador1_info = st.selectbox(
            "🔍 Digite para pesquisar:",
            options=opcoes_jogadores,
            help="Digite o nome do jogador para filtrar as opções",
            key="jogador1"
        )
        jogador1_nome = jogador1_info.split(" - ")[0] if jogador1_info else None
    
    with col2:
        st.markdown("### 🥈 Segundo Jogador")
        jogador2_info = st.selectbox(
            "🔍 Digite para pesquisar:",
            options=opcoes_jogadores,
            help="Digite o nome do jogador para filtrar as opções",
            key="jogador2"
        )
        jogador2_nome = jogador2_info.split(" - ")[0] if jogador2_info else None
    
    if jogador1_nome and jogador2_nome and jogador1_nome != jogador2_nome:
        j1_data = df[df['Nome'] == jogador1_nome].iloc[0]
        j2_data = df[df['Nome'] == jogador2_nome].iloc[0]
        
        # Cards informativos dos jogadores
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div style='background: white; padding: 1rem; border-radius: 12px; border: 2px solid #667eea; margin-bottom: 1rem;'>
                <h4 style='color: #667eea; margin: 0;'>🥇 {j1_data['Nome']}</h4>
                <p style='margin: 0.5rem 0; color: #666;'><strong>{j1_data['Clube']}</strong> • {j1_data['Posição']}</p>
                <p style='margin: 0; color: #333;'>💰 C$ {j1_data['Preço (C$)']:.0f} • {j1_data['Status']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='background: white; padding: 1rem; border-radius: 12px; border: 2px solid #764ba2; margin-bottom: 1rem;'>
                <h4 style='color: #764ba2; margin: 0;'>🥈 {j2_data['Nome']}</h4>
                <p style='margin: 0.5rem 0; color: #666;'><strong>{j2_data['Clube']}</strong> • {j2_data['Posição']}</p>
                <p style='margin: 0; color: #333;'>💰 C$ {j2_data['Preço (C$)']:.0f} • {j2_data['Status']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Métricas comparativas em layout melhorado
        st.markdown("### 📊 Comparação de Performance")
        
        metricas_comparacao = {
            '💰 Preço (C$)': 'Preço (C$)',
            '📈 Pontos Média': 'Pontos Média', 
            '💎 Custo-Benefício': 'Custo-Benefício',
            '⚽ Partidas': 'Partidas',
            '⚡ Eficiência': 'Eficiência'
        }
        
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]
        
        for i, (nome_metrica, campo) in enumerate(metricas_comparacao.items()):
            with cols[i % 3]:
                valor1 = j1_data[campo]
                valor2 = j2_data[campo]
                diferenca = valor1 - valor2
                
                # Determinar qual é melhor (para algumas métricas menor é melhor)
                if campo == 'Preço (C$)':
                    melhor = "normal" if diferenca <= 0 else "inverse"
                else:
                    melhor = "normal" if diferenca >= 0 else "inverse"
                
                st.metric(
                    nome_metrica,
                    f"{valor1:.2f}",
                    f"{diferenca:+.2f}",
                    delta_color=melhor
                )
        
        # Gráfico radar melhorado
        st.markdown("### 🎯 Comparação Visual")
        
        categorias = ['Pontos Média', 'Custo-Benefício', 'Eficiência']
        
        # Normalizar valores
        valores1 = []
        valores2 = []
        
        for cat in categorias:
            max_val = df[cat].max()
            min_val = df[cat].min()
            
            if max_val != min_val:
                v1_norm = 10 * (j1_data[cat] - min_val) / (max_val - min_val)
                v2_norm = 10 * (j2_data[cat] - min_val) / (max_val - min_val)
            else:
                v1_norm = v2_norm = 5
            
            valores1.append(max(0, v1_norm))
            valores2.append(max(0, v2_norm))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=valores1 + [valores1[0]],
            theta=categorias + [categorias[0]],
            fill='toself',
            name=j1_data['Nome'],
            line_color='#667eea',
            fillcolor='rgba(102, 126, 234, 0.2)'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=valores2 + [valores2[0]],
            theta=categorias + [categorias[0]],
            fill='toself',
            name=j2_data['Nome'],
            line_color='#764ba2',
            fillcolor='rgba(118, 75, 162, 0.2)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10],
                    gridcolor='#e1e5e9',
                    tickcolor='#666'
                ),
                angularaxis=dict(
                    gridcolor='#e1e5e9'
                )
            ),
            showlegend=True,
            title="Comparação Normalizada (0-10)",
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Inter, sans-serif", size=12)
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    else:
        st.info("🔍 Selecione dois jogadores diferentes para começar a comparação")

def criar_analise_clubes(df: pd.DataFrame):
    """Análise por clubes com gráficos limpos"""
    if df.empty:
        return
    
    st.subheader("🏟️ Performance por Clube")
    
    clube_stats = df.groupby('Clube').agg({
        'Pontos Média': ['mean', 'count'],
        'Preço (C$)': 'mean',
        'Custo-Benefício': 'mean'
    }).round(2)
    
    clube_stats.columns = ['Pontos Médios', 'Qtd Jogadores', 'Preço Médio', 'CB Médio']
    clube_stats = clube_stats.reset_index()
    clube_stats = clube_stats.sort_values('Pontos Médios', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏆 Top Clubes por Pontuação")
        fig = px.bar(
            clube_stats.head(10),
            x='Clube',
            y='Pontos Médios',
            color='CB Médio',
            title="Pontuação Média por Clube",
            color_continuous_scale=['#f8f9fa', '#667eea']
        )
        fig.update_xaxes(tickangle=45)
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            coloraxis_showscale=False,
            font=dict(family="Inter, sans-serif", size=12)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.markdown("#### 💰 Análise Preço vs Performance")
        fig = px.scatter(
            clube_stats,
            x='Preço Médio',
            y='Pontos Médios',
            size='Qtd Jogadores',
            hover_name='Clube',
            title="Custo vs Benefício por Clube",
            color='CB Médio',
            color_continuous_scale=['#fef7ff', '#667eea']
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            coloraxis_showscale=False,
            font=dict(family="Inter, sans-serif", size=12)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def criar_ferramentas_exportacao(df: pd.DataFrame):
    """Ferramentas de exportação melhoradas"""
    if df.empty:
        return
    
    st.subheader("📁 Exportar Análises")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📊 Planilha Excel")
        if st.button("📊 Gerar CSV", use_container_width=True):
            csv = df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"cartola_analise_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        st.markdown("#### 📋 Dados JSON")
        if st.button("📋 Gerar JSON", use_container_width=True):
            json_data = df.to_json(orient='records', indent=2)
            st.download_button(
                label="⬇️ Download JSON",
                data=json_data,
                file_name=f"cartola_dados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col3:
        st.markdown("#### 📈 Relatório")
        if st.button("📈 Visualizar", use_container_width=True):
            st.info("📋 **Prévia dos dados abaixo**")
            st.dataframe(
                df[['Nome', 'Clube', 'Posição', 'Preço (C$)', 'Pontos Média', 'Custo-Benefício']].head(20),
                use_container_width=True
            )

# ================================
# FUNÇÃO PRINCIPAL
# ================================

def main():
    """Função principal do dashboard"""
    
    # Aplicar estilos
    aplicar_estilo_customizado()
    
    # Header principal
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0; background: white; border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05);'>
        <h1 style='color: #2d3748; font-weight: 600; margin: 0;'>⚽ Dashboard Cartola FC 2025</h1>
        <p style='color: #666; font-size: 1.1rem; margin: 0.5rem 0 0 0;'>Análise Inteligente e Comparação de Jogadores</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Loading state
    with st.spinner("🔄 Carregando dados da API do Cartola FC..."):
        df = carregar_dados_api()
    
    if df.empty:
        st.error("❌ Não foi possível carregar os dados. Tente novamente mais tarde.")
        st.stop()
    
    # Sucesso no carregamento
    st.success(f"✅ **{len(df)} jogadores carregados** com sucesso da API oficial!")
    
    # Criar filtros melhorados na sidebar
    filtros = criar_filtros_sidebar_melhorados(df)
    posicao_sel, clube_sel, preco_min, preco_max, media_range, partidas_range, cb_min, ef_min = filtros
    
    # Aplicar filtros
    df_filtrado = df[
        (df["Posição"].isin(posicao_sel)) &
        (df["Clube"].isin(clube_sel)) &
        (df["Preço (C$)"] >= preco_min) &
        (df["Preço (C$)"] <= preco_max) &
        (df["Pontos Média"] >= media_range[0]) &
        (df["Pontos Média"] <= media_range[1]) &
        (df["Partidas"] >= partidas_range[0]) &
        (df["Partidas"] <= partidas_range[1]) &
        (df["Custo-Benefício"] >= cb_min) &
        (df["Eficiência"] >= ef_min)
    ].copy()
    
    # Métricas principais
    criar_metricas_principais(df_filtrado)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs organizadas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visão Geral", 
        "🏆 Rankings", 
        "🏟️ Análise de Clubes", 
        "⚔️ Comparador", 
        "📁 Exportar Dados"
    ])
    
    with tab1:
        st.markdown("### 📈 Análise Geral dos Jogadores")
        criar_graficos_limpos(df_filtrado)
        
        # Busca melhorada
        st.markdown("### 🔍 Busca Inteligente")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            nome_busca = st.text_input(
                "Digite o nome do jogador:",
                placeholder="Ex: Pedro, Hulk, Gerson...",
                help="🔍 Busque por qualquer jogador na lista filtrada"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            buscar = st.button("🔍 Buscar", use_container_width=True)
        
        if nome_busca or buscar:
            df_busca = df_filtrado[
                df_filtrado["Nome"].str.contains(nome_busca, case=False, na=False)
            ]
            if not df_busca.empty:
                st.success(f"✅ {len(df_busca)} jogador(es) encontrado(s)")
                st.dataframe(
                    df_busca.sort_values("Pontos Média", ascending=False)[
                        ['Nome', 'Clube', 'Posição', 'Preço (C$)', 'Pontos Média', 'Custo-Benefício', 'Status']
                    ],
                    use_container_width=True,
                    height=300
                )
            else:
                st.warning(f"❌ Nenhum jogador encontrado com '{nome_busca}'")
    
    with tab2:
        st.markdown("### 🏆 Rankings dos Melhores Jogadores")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔝 Melhores por Pontuação")
            top_pontos = df_filtrado.nlargest(15, "Pontos Média")[
                ['Nome', 'Clube', 'Posição', 'Pontos Média', 'Preço (C$)', 'Status']
            ]
            st.dataframe(top_pontos, use_container_width=True, height=400)
        
        with col2:
            st.markdown("#### 💎 Melhores Custo-Benefício")
            top_cb = df_filtrado.nlargest(15, "Custo-Benefício")[
                ['Nome', 'Clube', 'Posição', 'Custo-Benefício', 'Preço (C$)', 'Tendência']
            ]
            st.dataframe(top_cb, use_container_width=True, height=400)
        
        # Ranking por posição
        st.markdown("#### 📍 Análise por Posição")
        posicao_ranking = st.selectbox(
            "Selecione uma posição para análise detalhada:",
            options=df_filtrado['Posição'].unique(),
            help="🎯 Veja o ranking detalhado de cada posição"
        )
        
        if posicao_ranking:
            df_posicao = df_filtrado[df_filtrado['Posição'] == posicao_ranking].nlargest(10, 'Pontos Média')
            
            st.markdown(f"**Top 10 {posicao_ranking}:**")
            st.dataframe(
                df_posicao[['Nome', 'Clube', 'Pontos Média', 'Preço (C$)', 'Custo-Benefício', 'Eficiência', 'Status']],
                use_container_width=True,
                height=350
            )
    
    with tab3:
        criar_analise_clubes(df_filtrado)
    
    with tab4:
        criar_comparador_melhorado(df_filtrado)
    
    with tab5:
        criar_ferramentas_exportacao(df_filtrado)
    
    # Lista completa
    st.markdown("---")
    st.markdown("### 📋 Lista Completa de Jogadores")
    
    # Controles de visualização
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ordenar_por = st.selectbox(
            "📊 Ordenar por:",
            ['Pontos Média', 'Custo-Benefício', 'Preço (C$)', 'Eficiência', 'Nome'],
            help="Escolha o critério de ordenação"
        )
    
    with col2:
        ordem = st.selectbox("📈 Ordem:", ['Decrescente', 'Crescente'])
    
    with col3:
        mostrar_scouts = st.checkbox("⚽ Mostrar Scouts", help="Exibir estatísticas detalhadas")
    
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Atualizar Lista", use_container_width=True):
            st.rerun()
    
    # Aplicar ordenação
    ascending = ordem == 'Crescente'
    df_ordenado = df_filtrado.sort_values(ordenar_por, ascending=ascending)
    
    # Definir colunas
    colunas_base = ['Nome', 'Clube', 'Posição', 'Pontos Média', 'Preço (C$)', 'Custo-Benefício', 'Partidas', 'Status', 'Tendência']
    
    if mostrar_scouts:
        scouts_cols = [col for col in df_ordenado.columns 
                      if col not in colunas_base + ['ID', 'Foto', 'Status_Mercado', 'Eficiência', 'Valorização (%)']]
        colunas_exibir = colunas_base + scouts_cols[:5]  # Limitar scouts para não sobrecarregar
    else:
        colunas_exibir = colunas_base
    
    # Exibir tabela
    st.dataframe(
        df_ordenado[colunas_exibir],
        use_container_width=True,
        height=600
    )
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; padding: 1rem; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);'>
        <p style='margin: 0; color: #666;'><strong>Desenvolvido por Carlos Willian</strong> • Dashboard Cartola FC 2025 (Versão Pro)</p>
        <p style='margin: 0.5rem 0 0 0; color: #999; font-size: 0.9rem;'>Última atualização: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')} • Dados da API oficial do Cartola FC</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

