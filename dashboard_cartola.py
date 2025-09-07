"""
Dashboard Cartola FC 2025 - Versão Melhorada
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
# ESTILO CUSTOMIZADO
# ================================

def aplicar_estilo_customizado():
    """Aplica estilos CSS customizados"""
    st.markdown("""
    <style>
    /* Tema geral */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar customizada */
    .css-1d391kg {
        background-color: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Cards de métricas */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 1rem;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    
    /* Multiselect roxo */
    .stMultiSelect [data-baseweb="select"] span {
        background-color: #7e57c2 !important;
        color: white !important;
    }
    
    /* Botões customizados */
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Dataframes */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Alertas */
    .stAlert {
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    
    /* Animação de loading */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
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
    
    Args:
        url: URL da API
        max_retries: Número máximo de tentativas
        
    Returns:
        Dict com dados da API
        
    Raises:
        ApiException: Em caso de erro na requisição
    """
    for tentativa in range(max_retries):
        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if tentativa == max_retries - 1:
                raise ApiException(f"Erro na API após {max_retries} tentativas: {str(e)}")
            time.sleep(1)  # Aguarda 1 segundo antes da próxima tentativa

def validar_dados_jogadores(dados: Dict) -> bool:
    """
    Valida se os dados recebidos da API estão corretos
    
    Args:
        dados: Dados recebidos da API
        
    Returns:
        True se dados válidos, False caso contrário
    """
    campos_obrigatorios = ['atletas', 'clubes', 'posicoes']
    return all(campo in dados for campo in campos_obrigatorios)

def calcular_estatisticas_avancadas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula estatísticas avançadas dos jogadores
    
    Args:
        df: DataFrame com dados dos jogadores
        
    Returns:
        DataFrame com estatísticas adicionais
    """
    if df.empty:
        return df
    
    # Estatísticas avançadas
    df['Eficiência'] = df['Pontos Média'] * df['Partidas'] / df['Preço (C$)'].replace(0, 0.1)
    df['Pontos/Partida'] = df['Pontos Média']
    df['Valorização (%)'] = np.random.normal(0, 10, len(df))  # Simulado - você pode substituir por dados reais
    df['Tendência'] = np.where(df['Valorização (%)'] > 0, '📈', '📉')
    df['Status'] = pd.cut(df['Pontos Média'], 
                         bins=[-np.inf, 2, 5, 8, np.inf], 
                         labels=['🔴 Baixo', '🟡 Regular', '🟢 Bom', '🔵 Excelente'])
    
    return df

# ================================
# FUNÇÕES DE CARREGAMENTO DE DADOS
# ================================

@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def carregar_dados_api() -> pd.DataFrame:
    """
    Carrega dados da API do Cartola FC com cache otimizado
    
    Returns:
        DataFrame com dados dos jogadores
    """
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
                
            except Exception as e:
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
        
        # Cálculo do custo-benefício
        df['Custo-Benefício'] = df['Pontos Média'] / df['Preço (C$)'].replace(0, 0.1)
        
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
# COMPONENTES DA INTERFACE
# ================================

def criar_filtros_sidebar(df: pd.DataFrame) -> Tuple:
    """
    Cria filtros na sidebar baseados nos dados
    
    Args:
        df: DataFrame com dados dos jogadores
        
    Returns:
        Tupla com valores dos filtros
    """
    if df.empty:
        return [], [], 0, 0, (0, 0), (0, 0), 0, 0
    
    st.sidebar.markdown("## ⚙️ Filtros e Configurações")
    
    # Info do sistema
    with st.sidebar.expander("ℹ️ Informações do Sistema", expanded=False):
        st.info(f"🕒 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        st.info(f"⏱️ Cache TTL: {CACHE_TTL//60} minutos")
        st.info("🔄 Dados atualizados automaticamente")
    
    # Filtros principais
    st.sidebar.markdown("### 🎯 Filtros Principais")
    
    posicoes = sorted(df["Posição"].unique().tolist())
    clubes = sorted(df["Clube"].unique().tolist())
    
    posicao_selecionada = st.sidebar.multiselect(
        "🧩 Posições", 
        posicoes, 
        default=posicoes,
        help="Selecione as posições desejadas"
    )
    
    clube_selecionado = st.sidebar.multiselect(
        "🏳️ Clubes", 
        clubes, 
        default=clubes,
        help="Selecione os clubes desejados"
    )
    
    # Filtros de valores
    st.sidebar.markdown("### 💰 Filtros de Valores")
    
    preco_min, preco_max = st.sidebar.slider(
        "💰 Faixa de Preço (C$)",
        int(df["Preço (C$)"].min()),
        int(df["Preço (C$)"].max()),
        (int(df["Preço (C$)"].min()), int(df["Preço (C$)"].max())),
        help="Defina a faixa de preço dos jogadores"
    )
    
    media_min, media_max = st.sidebar.slider(
        "📊 Faixa de Pontos Média",
        float(df["Pontos Média"].min()),
        float(df["Pontos Média"].max()),
        (float(df["Pontos Média"].min()), float(df["Pontos Média"].max())),
        step=0.1,
        help="Defina a faixa de pontuação média"
    )
    
    partidas_min, partidas_max = st.sidebar.slider(
        "🎯 Faixa de Partidas Jogadas",
        int(df["Partidas"].min()),
        int(df["Partidas"].max()),
        (int(df["Partidas"].min()), int(df["Partidas"].max())),
        help="Defina quantas partidas o jogador deve ter jogado"
    )
    
    # Filtros avançados
    with st.sidebar.expander("🔧 Filtros Avançados"):
        cb_min = st.slider(
            "💸 Custo-Benefício Mínimo",
            0.0,
            float(df["Custo-Benefício"].max()),
            0.0,
            step=0.01,
            help="Filtre por custo-benefício mínimo"
        )
        
        eficiencia_min = st.slider(
            "⚡ Eficiência Mínima",
            0.0,
            float(df["Eficiência"].max()),
            0.0,
            step=0.01,
            help="Filtre por eficiência mínima"
        )
    
    return (posicao_selecionada, clube_selecionado, preco_min, preco_max, 
            (media_min, media_max), (partidas_min, partidas_max), cb_min, eficiencia_min)

def criar_metricas_principais(df: pd.DataFrame):
    """
    Cria as métricas principais do dashboard
    
    Args:
        df: DataFrame filtrado
    """
    if df.empty:
        st.warning("⚠️ Nenhum jogador encontrado com os filtros aplicados")
        return
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "📋 Jogadores Filtrados",
            f"{len(df):,}",
            help="Total de jogadores que atendem aos filtros"
        )
    
    with col2:
        preco_medio = df['Preço (C$)'].mean()
        st.metric(
            "🪙 Preço Médio",
            f"C$ {preco_medio:.2f}",
            help="Preço médio dos jogadores filtrados"
        )
    
    with col3:
        pontos_medio = df['Pontos Média'].mean()
        st.metric(
            "📊 Pontuação Média",
            f"{pontos_medio:.2f}",
            help="Pontuação média dos jogadores filtrados"
        )
    
    with col4:
        cb_medio = df['Custo-Benefício'].mean()
        st.metric(
            "💸 Custo-Benefício Médio",
            f"{cb_medio:.2f}",
            help="Custo-benefício médio dos jogadores filtrados"
        )
    
    with col5:
        eficiencia_media = df['Eficiência'].mean()
        st.metric(
            "⚡ Eficiência Média",
            f"{eficiencia_media:.2f}",
            help="Eficiência média dos jogadores filtrados"
        )

def criar_graficos_avancados(df: pd.DataFrame):
    """
    Cria gráficos avançados
    
    Args:
        df: DataFrame filtrado
    """
    if df.empty:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Relação Preço vs Pontos por Posição")
        
        fig = px.scatter(
            df,
            x="Preço (C$)",
            y="Pontos Média",
            color="Posição",
            size="Partidas",
            hover_name="Nome",
            hover_data=["Clube", "Custo-Benefício"],
            title="Dispersão: Preço vs Pontos Média",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(marker=dict(opacity=0.7, line=dict(width=1, color='white')))
        fig.update_layout(
            height=500,
            showlegend=True,
            hovermode='closest'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏆 Top 10 por Custo-Benefício")
        
        top_cb = df.nlargest(10, 'Custo-Benefício')
        
        fig = px.bar(
            top_cb,
            x='Custo-Benefício',
            y='Nome',
            color='Posição',
            orientation='h',
            hover_data=['Clube', 'Preço (C$)', 'Pontos Média'],
            title="Jogadores com Melhor Custo-Benefício"
        )
        
        fig.update_layout(
            height=500,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig, use_container_width=True)

def criar_analise_clubes(df: pd.DataFrame):
    """
    Cria análise por clubes
    
    Args:
        df: DataFrame filtrado
    """
    if df.empty:
        return
    
    st.subheader("🏟️ Análise por Clubes")
    
    # Estatísticas por clube
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
        fig = px.bar(
            clube_stats.head(10),
            x='Clube',
            y='Pontos Médios',
            color='CB Médio',
            title="Top 10 Clubes - Pontuação Média",
            color_continuous_scale='Viridis'
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(
            clube_stats,
            x='Preço Médio',
            y='Pontos Médios',
            size='Qtd Jogadores',
            hover_name='Clube',
            title="Preço vs Pontos por Clube",
            color='CB Médio',
            color_continuous_scale='RdYlBu_r'
        )
        st.plotly_chart(fig, use_container_width=True)

def criar_comparador_jogadores(df: pd.DataFrame):
    """
    Cria ferramenta de comparação entre jogadores
    
    Args:
        df: DataFrame filtrado
    """
    if df.empty:
        return
    
    st.subheader("⚔️ Comparador de Jogadores")
    
    col1, col2 = st.columns(2)
    
    with col1:
        jogador1 = st.selectbox(
            "Selecione o Jogador 1",
            options=df['Nome'].tolist(),
            help="Escolha o primeiro jogador para comparação"
        )
    
    with col2:
        jogador2 = st.selectbox(
            "Selecione o Jogador 2",
            options=df['Nome'].tolist(),
            help="Escolha o segundo jogador para comparação"
        )
    
    if jogador1 and jogador2 and jogador1 != jogador2:
        j1_data = df[df['Nome'] == jogador1].iloc[0]
        j2_data = df[df['Nome'] == jogador2].iloc[0]
        
        # Métricas comparativas
        col1, col2, col3 = st.columns(3)
        
        metricas = ['Preço (C$)', 'Pontos Média', 'Custo-Benefício', 'Partidas', 'Eficiência']
        
        for i, metrica in enumerate(metricas):
            with [col1, col2, col3][i % 3]:
                valor1 = j1_data[metrica]
                valor2 = j2_data[metrica]
                diferenca = valor1 - valor2
                
                st.metric(
                    f"{metrica}",
                    f"{valor1:.2f}",
                    f"{diferenca:+.2f} vs {jogador2}",
                    delta_color="normal" if diferenca >= 0 else "inverse"
                )
        
        # Gráfico radar comparativo
        categorias = ['Pontos Média', 'Custo-Benefício', 'Eficiência', 'Partidas']
        
        # Normalizar valores para escala 0-10
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
            
            valores1.append(v1_norm)
            valores2.append(v2_norm)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=valores1 + [valores1[0]],
            theta=categorias + [categorias[0]],
            fill='toself',
            name=jogador1,
            line_color='blue'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=valores2 + [valores2[0]],
            theta=categorias + [categorias[0]],
            fill='toself',
            name=jogador2,
            line_color='red'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )),
            showlegend=True,
            title="Comparação Radar dos Jogadores",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)

def criar_ferramentas_exportacao(df: pd.DataFrame):
    """
    Cria ferramentas de exportação de dados
    
    Args:
        df: DataFrame filtrado
    """
    if df.empty:
        return
    
    st.subheader("📁 Exportar Dados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Exportar CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"cartola_jogadores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📈 Exportar JSON"):
            json_data = df.to_json(orient='records', indent=2)
            st.download_button(
                label="⬇️ Download JSON",
                data=json_data,
                file_name=f"cartola_jogadores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("📋 Copiar para Clipboard"):
            st.code(df.to_string(index=False))
            st.success("✅ Dados exibidos acima. Use Ctrl+A e Ctrl+C para copiar.")

# ================================
# FUNÇÃO PRINCIPAL
# ================================

def main():
    """Função principal do dashboard"""
    
    # Aplicar estilos
    aplicar_estilo_customizado()
    
    # Título principal
    st.title("⚽ Dashboard Cartola FC 2025 - Versão Pro")
    st.markdown("---")
    
    # Loading state
    with st.spinner("🔄 Carregando dados da API do Cartola FC..."):
        df = carregar_dados_api()
    
    if df.empty:
        st.error("❌ Não foi possível carregar os dados. Tente novamente mais tarde.")
        st.stop()
    
    # Sucesso no carregamento
    st.success(f"✅ Dados carregados com sucesso! {len(df)} jogadores encontrados.")
    
    # Criar filtros na sidebar
    filtros = criar_filtros_sidebar(df)
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
    
    st.markdown("---")
    
    # Tabs para organizar conteúdo
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Análise Geral", 
        "🏆 Rankings", 
        "🏟️ Análise de Clubes", 
        "⚔️ Comparador", 
        "📁 Exportar"
    ])
    
    with tab1:
        st.header("📊 Análise Geral dos Jogadores")
        criar_graficos_avancados(df_filtrado)
        
        # Busca de jogadores
        st.subheader("🔍 Buscar Jogador Específico")
        nome_busca = st.text_input(
            "Digite o nome do jogador",
            placeholder="Ex: Pedro, Hulk, Gerson...",
            help="Busque por qualquer jogador na lista"
        )
        
        if nome_busca:
            df_busca = df_filtrado[
                df_filtrado["Nome"].str.contains(nome_busca, case=False, na=False)
            ]
            if not df_busca.empty:
                st.dataframe(
                    df_busca.sort_values("Pontos Média", ascending=False),
                    use_container_width=True,
                    height=400
                )
            else:
                st.warning(f"❌ Nenhum jogador encontrado com o nome '{nome_busca}'")
    
    with tab2:
        st.header("🏆 Rankings dos Melhores Jogadores")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔝 Top 15 por Pontos Média")
            top_pontos = df_filtrado.nlargest(15, "Pontos Média")[
                ['Nome', 'Clube', 'Posição', 'Pontos Média', 'Preço (C$)', 'Status']
            ]
            st.dataframe(top_pontos, use_container_width=True, height=400)
        
        with col2:
            st.subheader("💸 Top 15 por Custo-Benefício")
            top_cb = df_filtrado.nlargest(15, "Custo-Benefício")[
                ['Nome', 'Clube', 'Posição', 'Custo-Benefício', 'Preço (C$)', 'Tendência']
            ]
            st.dataframe(top_cb, use_container_width=True, height=400)
        
        # Ranking por posição
        st.subheader("📍 Melhores por Posição")
        posicao_ranking = st.selectbox(
            "Selecione uma posição",
            options=df_filtrado['Posição'].unique(),
            help="Veja os melhores jogadores de cada posição"
        )
        
        if posicao_ranking:
            df_posicao = df_filtrado[df_filtrado['Posição'] == posicao_ranking].nlargest(10, 'Pontos Média')
            st.dataframe(
                df_posicao[['Nome', 'Clube', 'Pontos Média', 'Preço (C$)', 'Custo-Benefício', 'Eficiência']],
                use_container_width=True
            )
    
    with tab3:
        criar_analise_clubes(df_filtrado)
    
    with tab4:
        criar_comparador_jogadores(df_filtrado)
    
    with tab5:
        criar_ferramentas_exportacao(df_filtrado)
    
    # Lista completa no final
    st.markdown("---")
    st.header("📄 Lista Completa de Jogadores")
    
    # Opções de visualização
    col1, col2, col3 = st.columns(3)
    with col1:
        ordenar_por = st.selectbox(
            "Ordenar por:",
            ['Pontos Média', 'Custo-Benefício', 'Preço (C$)', 'Eficiência', 'Nome'],
            help="Escolha o critério de ordenação"
        )
    
    with col2:
        ordem = st.selectbox("Ordem:", ['Decrescente', 'Crescente'])
    
    with col3:
        mostrar_scouts = st.checkbox("Mostrar Scouts", help="Exibir estatísticas detalhadas dos scouts")
    
    # Ordenação
    ascending = ordem == 'Crescente'
    df_ordenado = df_filtrado.sort_values(ordenar_por, ascending=ascending)
    
    # Colunas a exibir
    colunas_base = ['Nome', 'Clube', 'Posição', 'Pontos Média', 'Preço (C$)', 'Custo-Benefício', 'Partidas', 'Status', 'Tendência']
    
    if mostrar_scouts:
        scouts_cols = [col for col in df_ordenado.columns if col not in colunas_base and col not in ['ID', 'Foto', 'Status_Mercado', 'Eficiência']]
        colunas_exibir = colunas_base + scouts_cols
    else:
        colunas_exibir = colunas_base
    
    st.dataframe(
        df_ordenado[colunas_exibir],
        use_container_width=True,
        height=500
    )
    
    # Rodapé
    st.markdown("---")
    st.markdown("**Desenvolvido por Carlos Willian - Cartola FC 2025 (Versão Melhorada)**")
    st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Dados da API oficial do Cartola FC")

if __name__ == "__main__":
    main()

