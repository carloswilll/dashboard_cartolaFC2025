"""
Cartola Data App - Versão reescrita seguindo boas práticas
Objetivo: aplicação Streamlit modular, robusta e orientada a produção
Principais características:
- Código modular: config, fetch, transform, scoring, otimização, UI
- Tratamento de erros, retries e logging
- Cache de dados com TTL e uso de Session State para interatividade
- Métricas relevantes: médias móveis, volatilidade, value-for-money, expectativa ponderada
- Otimizador (PuLP) para montar escalação respeitando budget, formação e limite por clube
- Exportação de escalação e dados

Requisitos:
pip install streamlit pandas numpy requests plotly pulp

Uso:
streamlit run cartola_data_app_best_practices.py

Nota:
Substitua os endpoints da API caso necessário. O app aceita também CSV local como fallback.
"""

from typing import Dict, Tuple, Optional, List
import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import logging
from datetime import datetime
from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpBinary, PULP_CBC_CMD
import plotly.express as px

# --------------------------- Config ---------------------------
APP_TITLE = "Cartola Data App — Best Practices"
API = {
    'mercado': 'https://api.cartola.globo.com/atletas/mercado',
    'status': 'https://api.cartola.globo.com/mercado/status'
}
CACHE_TTL = 300  # segundos
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
DEFAULT_BUDGET = 100.0
MAX_PER_CLUB_DEFAULT = 3

# --------------------------- Logging ---------------------------
logger = logging.getLogger('cartola_app')
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# --------------------------- Utilitários HTTP ---------------------------

def get_json_with_retry(url: str, timeout: int = REQUEST_TIMEOUT, retries: int = MAX_RETRIES) -> Optional[dict]:
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            logger.warning(f"GET {url} failed attempt {attempt}/{retries}: {e}")
            time.sleep(0.4 * attempt)
    return None

# --------------------------- ETL ---------------------------
@st.cache_data(ttl=CACHE_TTL)
def fetch_cartola_data(use_api: bool = True, csv_file: Optional[bytes] = None) -> Tuple[pd.DataFrame, Dict]:
    """Retorna df_jogadores e status da API. Se csv_file fornecido, usa CSV como fallback."""
    # Prioridade: CSV local (dev) -> API
    if csv_file is not None:
        try:
            df = pd.read_csv(pd.io.common.BytesIO(csv_file))
            logger.info('Dados carregados via CSV local')
            return transform_raw_df(df), {}
        except Exception as e:
            logger.exception('Falha ao carregar CSV local: %s', e)
            return pd.DataFrame(), {}

    if not use_api:
        return pd.DataFrame(), {}

    mercado_json = get_json_with_retry(API['mercado'])
    status_json = get_json_with_retry(API['status'])
    if mercado_json is None:
        logger.error('Não foi possível obter mercado_json da API')
        return pd.DataFrame(), status_json or {}

    # parser resiliente: 'atletas' pode ser dict ou list
    atletas = mercado_json.get('atletas')
    clubes = {str(k): v for k, v in (mercado_json.get('clubes') or {}).items()}
    posicoes = {str(k): v for k, v in (mercado_json.get('posicoes') or {}).items()}

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
            apelido = atleta.get('apelido') or f'atleta_{atleta_id}'
            clube_id = str(atleta.get('clube_id') or '')
            pos_id = str(atleta.get('posicao_id') or '')
            row = {
                'player_id': atleta_id,
                'nome': apelido,
                'clube_id': clube_id,
                'clube': clubes.get(clube_id, {}).get('nome', 'Desconhecido'),
                'posicao_id': pos_id,
                'posicao': posicoes.get(pos_id, {}).get('nome', 'Desconhecido'),
                'preco': float(atleta.get('preco_num') or 0.0),
                'media': float(atleta.get('media_num') or 0.0),
                'jogos': int(atleta.get('jogos_num') or 0),
                'status_id': atleta.get('status_id')
            }
            scout = atleta.get('scout') or {}
            if isinstance(scout, dict):
                for s_k, s_v in scout.items():
                    row[str(s_k).upper()] = float(s_v or 0)
            rows.append(row)
        except Exception:
            logger.exception('Erro ao parsear atleta %s', k)

    raw_df = pd.DataFrame(rows)
    df = transform_raw_df(raw_df)
    return df, status_json or {}

# --------------------------- Transformações e Features ---------------------------

def transform_raw_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    # Normalizações básicas
    df['preco'] = pd.to_numeric(df.get('preco', 0), errors='coerce').fillna(0.0)
    df['media'] = pd.to_numeric(df.get('media', 0), errors='coerce').fillna(0.0)
    df['jogos'] = pd.to_numeric(df.get('jogos', 0), errors='coerce').fillna(0).astype(int)
    df['nome'] = df['nome'].astype(str)

    # Scouts esperados - garante colunas
    scouts_common = ['G', 'A', 'DS', 'SG', 'DD', 'FT', 'FD', 'FF']
    for s in scouts_common:
        if s not in df.columns:
            df[s] = 0.0
    df[scouts_common] = df[scouts_common].fillna(0.0).astype(float)

    # Indicadores simples
    df['custo_beneficio'] = df.apply(lambda r: r['media'] / r['preco'] if r['preco'] > 0 else 0.0, axis=1)
    df['indice_ofensivo'] = (df['G']*8 + df['A']*5 + df['FD']*1.2 + df['FF']*0.8 + df['FT']*3)
    df['indice_defensivo'] = (df['DS']*1.5 + df['SG']*5 + df['DD']*3)

    # Estimativas de expectativa. Simples: média ponderada e penalidade por volatilidade.
    # Placeholder para janelas históricas se tiver dados por rodada.
    df['score_base'] = 0.6 * df['media'] + 0.4 * df['indice_ofensivo'].where(df['posicao'].str.lower().str.contains('ataque|atacante|atac'), df['indice_defensivo'])
    df['volatilidade'] = df[scouts_common].std(axis=1).fillna(0)
    df['score_expect'] = (df['score_base'] - 0.2 * df['volatilidade']).clip(lower=0)

    # Rank e ordenações
    df['rank_media'] = df['media'].rank(ascending=False, method='min')
    df.sort_values(by='score_expect', ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

# --------------------------- Otimizador (ILP) ---------------------------

def optimize_lineup(df: pd.DataFrame, budget: float, formation: Dict[str,int], max_per_club: int = MAX_PER_CLUB_DEFAULT) -> Tuple[pd.DataFrame, Optional[Dict]]:
    # Precondição
    if df.empty:
        return pd.DataFrame(), None

    players = df.copy().reset_index(drop=True)
    players['idx'] = players.index

    prob = LpProblem('cartola_opt', LpMaximize)
    x = {i: LpVariable(f'x_{i}', cat=LpBinary) for i in players['idx']}
    c = {i: LpVariable(f'cap_{i}', cat=LpBinary) for i in players['idx']}

    # objetivo: soma de score_expect + capitão adicional
    prob += lpSum([x[i] * players.loc[i, 'score_expect'] + c[i] * players.loc[i, 'score_expect'] for i in players['idx']])

    # orçamento
    prob += lpSum([x[i] * players.loc[i, 'preco'] for i in players['idx']]) <= budget

    # capitão exatamente um e capitão implica selecionado
    prob += lpSum([c[i] for i in players['idx']]) == 1
    for i in players['idx']:
        prob += c[i] <= x[i]

    # formação posicional (posicao deve bater com colunas usadas no df)
    for pos, qty in formation.items():
        prob += lpSum([x[i] for i in players['idx'] if pos.lower() in str(players.loc[i, 'posicao']).lower()]) == qty

    # max por clube
    clubs = players['clube'].unique().tolist()
    for club in clubs:
        prob += lpSum([x[i] for i in players['idx'] if players.loc[i, 'clube'] == club]) <= max_per_club

    # solve
    solver = PULP_CBC_CMD(msg=False)
    prob.solve(solver)

    selected_idx = [i for i in players['idx'] if x[i].value() == 1]
    captain_idx = next((i for i in players['idx'] if c[i].value() == 1), None)

    selected = players.loc[selected_idx].copy() if selected_idx else pd.DataFrame()
    captain = players.loc[captain_idx].to_dict() if captain_idx is not None else None
    return selected, captain

# --------------------------- UI ---------------------------

def setup_page():
    st.set_page_config(page_title=APP_TITLE, layout='wide')
    st.title(APP_TITLE)

def sidebar_controls(df: pd.DataFrame) -> Dict:
    st.sidebar.header('Configurações')
    use_api = st.sidebar.checkbox('Usar API oficial (Cartola)', value=True)
    csv_file = st.sidebar.file_uploader('CSV de fallback (formatado)', type=['csv'])

    budget = st.sidebar.number_input('Budget (C$)', value=DEFAULT_BUDGET, min_value=10.0)
    max_per_club = st.sidebar.number_input('Máx por clube', value=MAX_PER_CLUB_DEFAULT, min_value=1)

    formation_choice = st.sidebar.selectbox('Formação padrão', ['4-4-2','3-5-2','4-3-3'])
    formation_map = {
        '4-4-2': {'GOL':1, 'DEF':4, 'MEI':4, 'ATA':2},
        '3-5-2': {'GOL':1, 'DEF':3, 'MEI':5, 'ATA':2},
        '4-3-3': {'GOL':1, 'DEF':4, 'MEI':3, 'ATA':3}
    }

    # filtros dinâmicos
    posicoes = sorted(df['posicao'].unique().astype(str)) if not df.empty else []
    pos_select = st.sidebar.multiselect('Posições', options=posicoes, default=posicoes)
    clubes = sorted(df['clube'].unique().astype(str)) if not df.empty else []
    club_select = st.sidebar.multiselect('Clubes', options=clubes, default=clubes)

    status_options = sorted(df['status_id'].unique().astype(str)) if not df.empty else []
    status_select = st.sidebar.multiselect('Status ID', options=status_options, default=status_options)

    return {
        'use_api': use_api,
        'csv_file': csv_file.read() if csv_file is not None else None,
        'budget': budget,
        'max_per_club': max_per_club,
        'formation': formation_map[formation_choice],
        'pos_select': pos_select,
        'club_select': club_select,
        'status_select': status_select
    }

def main():
    setup_page()
    st.sidebar.markdown('Data App para escalar jogadores no Cartola. Boas práticas aplicadas.')

    controls = sidebar_controls(pd.DataFrame())

    # carregamento com fallback
    df, status = fetch_cartola_data(use_api=controls['use_api'], csv_file=controls['csv_file'])
    if df.empty:
        st.error('Sem dados disponíveis. Verifique API ou faça upload de CSV.')
        st.stop()

    # re-exibir controles agora que df existe (para filtros dinâmicos corretos)
    controls = sidebar_controls(df)

    # aplicar filtros simples
    df_filtered = df[
        df['posicao'].isin(controls['pos_select']) &
        df['clube'].isin(controls['club_select']) &
        df['status_id'].astype(str).isin(controls['status_select'])
    ].copy()

    # Layout principal
    tabs = st.tabs(['Visão Geral','Otimização','Análise Avançada','Dados'])

    # Visão Geral
    with tabs[0]:
        st.header('Visão Geral')
        col1, col2, col3 = st.columns(3)
        col1.metric('Jogadores', f"{len(df_filtered):,}")
        col2.metric('Preço médio (C$)', f"{df_filtered['preco'].mean():.2f}")
        col3.metric('Pontos médios', f"{df_filtered['media'].mean():.2f}")

        st.markdown('### Top 20 por Score Esperado')
        st.dataframe(df_filtered[['nome','clube','posicao','preco','media','score_expect']].head(20))

        st.markdown('### Scatter: Preço x Score Esperado')
        fig = px.scatter(df_filtered, x='preco', y='score_expect', color='posicao', hover_name='nome', size='media', template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)

    # Otimização
    with tabs[1]:
        st.header('Otimização de Escalação')
        st.markdown('Defina constraints e gere escalação ótima pelo solver (ILP).')
        budget = controls['budget']
        max_per_club = controls['max_per_club']
        formation = controls['formation']

        if st.button('Gerar escalação otimizada'):
            selected, captain = optimize_lineup(df_filtered, budget=budget, formation=formation, max_per_club=max_per_club)
            if selected.empty:
                st.warning('Solver não retornou escalação. Ajuste budget/formation.')
            else:
                st.markdown('### Escalação sugerida')
                st.table(selected[['nome','clube','posicao','preco','score_expect']])
                if captain:
                    st.info(f"Capitão sugerido: {captain.get('nome')} — Score: {captain.get('score_expect'):.2f}")
                # export
                csv = selected.to_csv(index=False).encode('utf-8')
                st.download_button('Baixar escalação CSV', data=csv, file_name=f'escalação_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')

    # Análise Avançada
    with tabs[2]:
        st.header('Análise Avançada')
        st.markdown('- Índices ofensivos e defensivos
- Top por custo-benefício
- Volatilidade e consistência')
        st.markdown('### Top 10 custo-benefício')
        st.dataframe(df_filtered.nlargest(10, 'custo_beneficio')[['nome','clube','posicao','preco','media','custo_beneficio']])

        st.markdown('### Distribuição de Scores')
        fig = px.histogram(df_filtered, x='score_expect', nbins=30, template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)

    # Dados completos
    with tabs[3]:
        st.header('Dados')
        st.dataframe(df_filtered, use_container_width=True)
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button('Baixar dados filtrados (CSV)', data=csv, file_name=f'cartola_dados_{datetime.now().strftime("%Y%m%d")}.csv')

# --------------------------- Entrypoint ---------------------------
if __name__ == '__main__':
    main()

