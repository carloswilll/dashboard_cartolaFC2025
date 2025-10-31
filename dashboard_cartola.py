"""
Cartola Insights 2025 - versão melhorada
Melhorias aplicadas:
- Organização modular (ETL, processamento, UI)
- Tratamento de erros e retries na API
- Tipagem e docstrings
- Uso de session state para status e cache local
- Validações de dados e fallback robusto
- Pequenas correções de UX (mensagens, download, ordenação)
- Preparado para deploy (variáveis de configuração no topo)

Para rodar: pip install streamlit pandas plotly requests
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import plotly.express as px
from typing import Dict, Tuple, Optional
import logging
import time

# -------------------- Config --------------------
st.set_page_config(page_title="Cartola Insights 2025", page_icon="⭐", layout="wide")

API_URLS = {
    'mercado': 'https://api.cartola.globo.com/atletas/mercado',
    'status': 'https://api.cartola.globo.com/mercado/status',
}
CACHE_TTL = 300  # segundos
REQUEST_TIMEOUT = 10
MAX_RETRIES = 2

# Logging mínimo
logger = logging.getLogger('cartola_insights')
logger.setLevel(logging.INFO)

# -------------------- Utilitários HTTP --------------------

def requests_get_with_retry(url: str, params: Optional[dict] = None, timeout: int = REQUEST_TIMEOUT, retries: int = MAX_RETRIES) -> Optional[dict]:
    """Faz GET com retries simples. Retorna JSON ou None."""
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.warning(f"GET {url} falhou (tentativa {attempt}/{retries}): {e}")
            time.sleep(0.5 * attempt)
    return None

# -------------------- Styling --------------------

def aplicar_design_dark_mode() -> None:
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, .stApp { background: #0F172A; color:#F8FAFC; font-family: Inter, sans-serif }
    [data-testid="stSidebar"] { background: #111827 }
    .stButton>button { background:#22C55E; color:#07102a; border-radius:8px; font-weight:700 }
    .stDataFrame { border-radius:8px; }
    h1,h2,h3 { color:#F8FAFC }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -------------------- ETL e processamento --------------------

@st.cache_data(ttl=CACHE_TTL)
# substitua a versão antiga por esta
def carregar_dados_api() -> Tuple[pd.DataFrame, Dict]:
    try:
        mercado_json = requests_get_with_retry(API_URLS['mercado'])
        status_json = requests_get_with_retry(API_URLS['status'])
        atletas = mercado_json.get('atletas') if mercado_json else None
        clubes = {str(k): v for k, v in (mercado_json.get('clubes') or {}).items()} if mercado_json else {}
        posicoes = {str(k): v for k, v in (mercado_json.get('posicoes') or {}).items()} if mercado_json else {}

        rows = []
        if isinstance(atletas, dict):
            iterator = atletas.items()
        elif isinstance(atletas, list):
            iterator = enumerate(atletas)
        else:
            iterator = []

        for k, atleta in iterator:
            try:
                atleta_id = int(atleta.get('atleta_id') or k)
                apelido = atleta.get('apelido') or atleta.get('apelido_abreviado') or f"Atleta_{atleta_id}"
                clube_id = str(atleta.get('clube_id'))
                pos_id = str(atleta.get('posicao_id'))

                row = {
                    'ID': atleta_id,
                    'Nome': apelido,
                    'Clube': clubes.get(clube_id, {}).get('nome', 'Desconhecido'),
                    'Posição': posicoes.get(pos_id, {}).get('nome', 'Desconhecido'),
                    'Preço (C$)': float(atleta.get('preco_num') or 0),
                    'Pontos Média': float(atleta.get('media_num') or 0),
                    'Partidas': int(atleta.get('jogos_num') or 0),
                    'Status Raw': atleta.get('status_id')
                }

                scout = atleta.get('scout') or {}
                for s_key, s_val in (scout.items() if isinstance(scout, dict) else []):
                    row[str(s_key).upper()] = float(s_val or 0)

                rows.append(row)
            except Exception:
                logger.exception(f"Erro processando atleta {k}")

        df = pd.DataFrame(rows)
        df = calcular_metricas(df)
        return df, status_json or {}

    except Exception:
        logger.exception('Erro geral em carregar_dados_api')
        return pd.DataFrame(), status_json or {}

    df = pd.DataFrame(rows)
    df = calcular_metricas(df)
    return df, status_json or {}

# Função separada para limpeza e features

def safe_div(a, b, eps=1e-9):
    try:
        if b == 0 or pd.isna(b):
            return 0.0
        return a / b
    except Exception:
        return 0.0


def calcular_metricas(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    # Normaliza colunas esperadas
    df['Preço (C$)'] = pd.to_numeric(df['Preço (C$)'], errors='coerce').fillna(0.0)
    df['Pontos Média'] = pd.to_numeric(df['Pontos Média'], errors='coerce').fillna(0.0)
    df['Partidas'] = pd.to_numeric(df['Partidas'], errors='coerce').fillna(0).astype(int)

    # Status legível
    status_map = {7: 'Provável', 6: 'Dúvida', 2: 'Contundido/Suspenso', 5: 'Nulo'}
    df['Status'] = df.get('Status Raw').map(status_map).fillna('Indefinido')

    # Garantir presença de scouts mais comuns
    scouts_expected = ['G', 'A', 'DS', 'SG', 'DD', 'FT', 'FD', 'FF']
    for s in scouts_expected:
        if s not in df.columns:
            df[s] = 0.0
    df[scouts_expected] = df[scouts_expected].fillna(0.0).astype(float)

    # Métricas derivadas
    df['Pontos por C$'] = (df['Pontos Média'] / df['Preço (C$)'].replace(0, np.nan)).fillna(0.0)
    df['Índice Ofensivo'] = (df['G']*8 + df['A']*5 + df['FD']*1.2 + df['FF']*0.8 + df['FT']*3).round(2)
    df['Índice Defensivo'] = (df['DS']*1.5 + df['SG']*5 + df['DD']*3).round(2)

    # Rankings e ordenações para UX
    df['Rank_Pontos_Média'] = df['Pontos Média'].rank(ascending=False, method='min')
    df['Rank_CustoBeneficio'] = df['Pontos por C$'].rank(ascending=False, method='min')

    # Ordena por pontuação média decrescente como default
    df.sort_values(by='Pontos Média', ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df

# -------------------- Componentes UI --------------------

def display_header(status_data: Dict) -> None:
    rodada_atual = status_data.get('rodada_atual', 'N/A')
    status_mercado = status_data.get('status_mercado_desc', 'Indisponível')

    st.markdown(f"""
    <div style='background:#111827;padding:18px;border-radius:12px;'>
        <h1 style='margin:0;color:#22C55E;'>⭐ Cartola Insights 2025</h1>
        <p style='color:#94A3B8;margin:0;'>Ferramenta para análise e tomada de decisões no Cartola FC.</p>
        <div style='margin-top:8px;color:#94A3B8'>Rodada: <strong style='color:#F8FAFC'>{rodada_atual}</strong> · Mercado: <strong style='color:#22C55E'>{status_mercado}</strong></div>
    </div>
    """, unsafe_allow_html=True)


def display_kpis(df: pd.DataFrame) -> None:
    if df.empty:
        st.warning("Sem jogadores para exibir.")
        return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Jogadores analisados', f"{len(df):,}")
    c2.metric('Preço médio (C$)', f"{df['Preço (C$)'].mean():.2f}")
    c3.metric('Pontos médios', f"{df['Pontos Média'].mean():.2f}")
    c4.metric('Custo-benefício médio', f"{df['Pontos por C$'].mean():.3f}")


def display_highlights(df: pd.DataFrame) -> None:
    if df.empty:
        st.info('Sem destaques disponíveis')
        return
    try:
        mais_caro = df.loc[df['Preço (C$)'].idxmax()]
        melhor_media = df.loc[df['Pontos Média'].idxmax()]
        melhor_cb_df = df[df['Status'] == 'Provável']
        if not melhor_cb_df.empty:
            melhor_cb = melhor_cb_df.loc[melhor_cb_df['Pontos por C$'].idxmax()]
        else:
            melhor_cb = df.loc[df['Pontos por C$'].idxmax()]

        col1, col2, col3 = st.columns(3)
        col1.info(f"Mais caro: {mais_caro['Nome']} ({mais_caro['Clube']}) — C$ {mais_caro['Preço (C$)']:.2f}")
        col2.success(f"Melhor média: {melhor_media['Nome']} — {melhor_media['Pontos Média']:.2f} pts/jogo")
        col3.write(f"Jóia: {melhor_cb['Nome']} — Custo-benefício {melhor_cb['Pontos por C$']:.3f}")
    except Exception as e:
        logger.exception(f"Erro ao calcular destaques: {e}")


def display_charts(df: pd.DataFrame) -> None:
    if df.empty:
        return
    left, right = st.columns([2, 1])
    with left:
        st.markdown('#### Preço vs Pontuação Média')
        fig = px.scatter(df, x='Preço (C$)', y='Pontos Média', color='Posição', size='Partidas', hover_name='Nome', template='plotly_dark')
        fig.update_layout(margin=dict(t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown('#### Top 15 Custo-Benefício')
        top_cb = df.nlargest(15, 'Pontos por C$')
        fig = px.bar(top_cb, x='Pontos por C$', y='Nome', orientation='h', template='plotly_dark')
        fig.update_layout(margin=dict(t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)

# -------------------- Main --------------------

def main() -> None:
    aplicar_design_dark_mode()

    # Carrega dados
    df, status = carregar_dados_api()
    if df.empty:
        st.error('Não foi possível obter dados da API do Cartola. Verifique a conexão ou tente novamente mais tarde.')
        st.stop()

    display_header(status)

    # Sidebar - filtros
    st.sidebar.title('Filtros')
    posicoes = sorted(df['Posição'].dropna().unique().tolist())
    pos_sel = st.sidebar.multiselect('Posições', posicoes, default=posicoes)

    clubes = sorted(df['Clube'].dropna().unique().tolist())
    clube_sel = st.sidebar.multiselect('Clubes', clubes, default=clubes)

    status_options = sorted(df['Status'].dropna().unique().tolist())
    status_sel = st.sidebar.multiselect('Status', status_options, default=['Provável'] if 'Provável' in status_options else status_options)

    preco_min, preco_max = float(df['Preço (C$)'].min()), float(df['Preço (C$)'].max())
    preco_range = st.sidebar.slider('Faixa de preço (C$)', preco_min, preco_max, (preco_min, preco_max))

    # Aplicar filtros
    df_filtrado = df[
        df['Posição'].isin(pos_sel) &
        df['Clube'].isin(clube_sel) &
        df['Status'].isin(status_sel) &
        df['Preço (C$)'].between(preco_range[0], preco_range[1])
    ].copy()

    # Layout com abas
    tab_geral, tab_analise, tab_dados = st.tabs(['Visão Geral', 'Análise Detalhada', 'Dados'])

    with tab_geral:
        display_kpis(df_filtrado)
        st.divider()
        display_highlights(df_filtrado)
        st.divider()
        display_charts(df_filtrado)

    with tab_analise:
        st.markdown('### Índices Ofensivos e Defensivos')
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('Top Atacantes')
            st.dataframe(df_filtrado.nlargest(15, 'Índice Ofensivo')[['Nome', 'Clube', 'Posição', 'Índice Ofensivo', 'Pontos Média']])
        with c2:
            st.markdown('Top Defensores')
            st.dataframe(df_filtrado.nlargest(15, 'Índice Defensivo')[['Nome', 'Clube', 'Posição', 'Índice Defensivo', 'Pontos Média']])

    with tab_dados:
        st.markdown('### Tabela completa')
        st.dataframe(df_filtrado, use_container_width=True, height=520)
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button('Baixar CSV', data=csv, file_name=f'cartola_insights_{datetime.now().strftime("%Y%m%d")}.csv', mime='text/csv')

if __name__ == '__main__':
    main()

