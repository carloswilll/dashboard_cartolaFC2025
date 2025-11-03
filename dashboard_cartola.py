"""
Cartola Data App - Código completo com fallback de solver (PuLP) embutido.
- Tenta usar PuLP para ILP. Se PuLP não instalado, usa heurística greedy.
- App em Streamlit pronto para rodar: `streamlit run cartola_data_app_complete_fixed.py`

Dependências:
pip install streamlit pandas numpy requests plotly
# PuLP é opcional. Para usar o solver ILP instale: pip install pulp
"""

from typing import Dict, Tuple, Optional, List
import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import logging
from datetime import datetime
import plotly.express as px

# --------------------------- Logging ---------------------------
logger = logging.getLogger('cartola_app_full')
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

# --------------------------- Config ---------------------------
APP_TITLE = "Cartola Data App — Fixed"
API = {
    'mercado': 'https://api.cartola.globo.com/atletas/mercado',
    'status': 'https://api.cartola.globo.com/mercado/status'
}
CACHE_TTL = 300
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
DEFAULT_BUDGET = 100.0
MAX_PER_CLUB_DEFAULT = 3

# --------------------------- Solver import / fallback ---------------------------
PULP_AVAILABLE = False
try:
    from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpBinary, PULP_CBC_CMD
    PULP_AVAILABLE = True
    logger.info('PuLP detectado. Solver ILP ativado.')
except Exception:
    logger.warning('PuLP não detectado. Usando fallback heurístico para otimização. Instale "pip install pulp" para ILP.')

# ILP optimizer (requires pulp)
def optimize_lineup_ilp(df: pd.DataFrame, budget: float, formation: Dict[str,int], max_per_club: int = 3) -> Tuple[pd.DataFrame, Optional[Dict]]:
    if df is None or df.empty:
        return pd.DataFrame(), None
    players = df.copy().reset_index(drop=True)
    players['idx'] = players.index

    prob = LpProblem('cartola_opt', LpMaximize)
    x = {i: LpVariable(f'x_{i}', cat=LpBinary) for i in players['idx']}
    c = {i: LpVariable(f'cap_{i}', cat=LpBinary) for i in players['idx']}

    # objetivo
    prob += lpSum([x[i] * players.loc[i, 'score_expect'] + c[i] * players.loc[i, 'score_expect'] for i in players['idx']])

    # budget
    prob += lpSum([x[i] * players.loc[i, 'preco'] for i in players['idx']]) <= budget

    # capitão exato 1
    prob += lpSum([c[i] for i in players['idx']]) == 1
    for i in players['idx']:
        prob += c[i] <= x[i]

    # formação posicional (caso sensível a substrings)
    for pos_key, qty in formation.items():
        prob += lpSum([x[i] for i in players['idx'] if pos_key.lower() in str(players.loc[i,'posicao']).lower()]) == qty

    # máximo por clube
    clubs = players['clube'].unique().tolist()
    for club in clubs:
        prob += lpSum([x[i] for i in players['idx'] if players.loc[i,'clube'] == club]) <= max_per_club

    solver = PULP_CBC_CMD(msg=False)
    prob.solve(solver)

    selected_idx = [i for i in players['idx'] if x[i].value() == 1]
    captain_idx = next((i for i in players['idx'] if c[i].value() == 1), None)
    selected = players.loc[selected_idx].copy() if selected_idx else pd.DataFrame()
    captain = players.loc[captain_idx].to_dict() if captain_idx is not None else None
    return selected, captain

# Heuristic fallback optimizer
def optimize_lineup_greedy(df: pd.DataFrame, budget: float, formation: Dict[str,int], max_per_club: int = 3) -> Tuple[pd.DataFrame, Optional[Dict]]:
    if df is None or df.empty:
        return pd.DataFrame(), None
    players = df.copy().reset_index(drop=True)
    # avoid zero division
    players['preco_nonzero'] = players['preco'].replace(0, 1.0)
    players['value'] = players['score_expect'] / players['preco_nonzero']

    selected_list = []
    for pos_key, qty in formation.items():
        candidates = players[players['posicao'].str.lower().str.contains(pos_key.lower(), na=False)].sort_values('value', ascending=False)
        chosen = candidates.head(qty)
        selected_list.append(chosen)

    selected = pd.concat(selected_list).drop_duplicates(subset=['player_id']).reset_index(drop=True) if selected_list else pd.DataFrame()

    # enforce max per club
    if not selected.empty:
        while True:
            counts = selected['clube'].value_counts()
            over = counts[counts > max_per_club]
            if over.empty:
                break
            for club, cnt in over.items():
                exceed = cnt - max_per_club
                to_drop = selected[selected['clube'] == club].nsmallest(exceed, 'value')
                selected = selected.drop(to_drop.index).reset_index(drop=True)

    # enforce budget
    if not selected.empty:
        total = selected['preco'].sum()
        while total > budget and not selected.empty:
            drop_idx = selected['value'].idxmin()
            selected = selected.drop(drop_idx).reset_index(drop=True)
            total = selected['preco'].sum()

    captain = None
    if not selected.empty:
        cap_row = selected.loc[selected['score_expect'].idxmax()]
        captain = cap_row.to_dict()

    selected = selected.drop(columns=['preco_nonzero','value'], errors='ignore')
    return selected, captain

# Unified optimizer to call from UI
def optimize_lineup(df: pd.DataFrame, budget: float, formation: Dict[str,int], max_per_club: int = 3) -> Tuple[pd.DataFrame, Optional[Dict]]:
    if PULP_AVAILABLE:
        try:
            return optimize_lineup_ilp(df, budget, formation, max_per_club)
        except Exception as e:
            logger.exception('Erro no ILP solver, usando fallback: %s', e)
            return optimize_lineup_greedy(df, budget, formation, max_per_club)
    else:
        return optimize_lineup_greedy(df, budget, formation, max_per_club)

# --------------------------- HTTP util ---------------------------
def get_json_with_retry(url: str, timeout: int = REQUEST_TIMEOUT, retries: int = MAX_RETRIES) -> Optional[dict]:
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            logger.warning(f"GET {url} failed ({attempt}/{retries}): {e}")
            time.sleep(0.4 * attempt)
    return None

# --------------------------- ETL / Transform ---------------------------
@st.cache_data(ttl=CACHE_TTL)
def fetch_cartola_data(use_api: bool = True, csv_file: Optional[bytes] = None) -> Tuple[pd.DataFrame, Dict]:
    if csv_file is not None:
        try:
            df = pd.read_csv(pd.io.common.BytesIO(csv_file))
            logger.info('Loaded data from CSV fallback')
            return transform_df(df), {}
        except Exception as e:
            logger.exception('CSV load failed: %s', e)
            return pd.DataFrame(), {}

    if not use_api:
        return pd.DataFrame(), {}

    mercado_json = get_json_with_retry(API['mercado'])
    status_json = get_json_with_retry(API['status'])
    if mercado_json is None:
        logger.error('mercado_json None')
        return pd.DataFrame(), status_json or {}

    atletas = mercado_json.get('atletas')
    clubes = {str(k): v for k, v in (mercado_json.get('clubes') or {}).items()}
    posicoes = {str(k): v for k, v in (mercado_json.get('posicoes') or {}).items()}

    rows = []
    iterator = atletas.items() if isinstance(atletas, dict) else enumerate(atletas or [])
    for k, atleta in iterator:
        try:
            row = {
                'player_id': int(atleta.get('atleta_id') or k),
                'nome': atleta.get('apelido') or atleta.get('apelido_abreviado') or f'Jogador_{k}',
                'clube': clubes.get(str(atleta.get('clube_id')), {}).get('nome', 'Desconhecido'),
                'posicao': posicoes.get(str(atleta.get('posicao_id')), {}).get('nome', 'Desconhecido'),
                'preco': float(atleta.get('preco_num') or 0),
                'media': float(atleta.get('media_num') or 0),
                'status': atleta.get('status_id')
            }
            scout = atleta.get('scout') or {}
            if isinstance(scout, dict):
                for s_k, s_v in scout.items():
                    row[str(s_k).upper()] = float(s_v or 0)
            rows.append(row)
        except Exception as e:
            logger.warning('Parse athlete %s failed: %s', k, e)

    raw_df = pd.DataFrame(rows)
    df = transform_df(raw_df)
    return df, status_json or {}

def transform_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.copy()

    # garantir scouts esperados
    scouts_expected = ['G','A','DS','SG','DD','FT','FD','FF']
    for s in scouts_expected:
        if s not in df.columns:
            df[s] = 0.0
    df[scouts_expected] = df[scouts_expected].fillna(0.0).astype(float)

    # garantir colunas numéricas como Series (evita retorno escalar)
    if 'preco' not in df.columns:
        df['preco'] = 0.0
    else:
        df['preco'] = pd.to_numeric(df['preco'], errors='coerce').fillna(0.0)

    if 'media' not in df.columns:
        df['media'] = 0.0
    else:
        df['media'] = pd.to_numeric(df['media'], errors='coerce').fillna(0.0)

    # trata 'jogos' explicitamente como Series
    if 'jogos' not in df.columns:
        df['jogos'] = 0
    else:
        df['jogos'] = pd.to_numeric(df['jogos'], errors='coerce').fillna(0).astype(int)

    # features derivadas
    df['indice_ofensivo'] = df['G']*8 + df['A']*5 + df['FD']*1.2 + df['FF']*0.8 + df['FT']*3
    df['indice_defensivo'] = df['DS']*1.5 + df['SG']*5 + df['DD']*3

    df['custo_beneficio'] = df.apply(lambda r: (r['media']/r['preco']) if r['preco'] > 0 else 0.0, axis=1)

    # score base por posição
    df['score_base'] = np.where(
        df['posicao'].str.lower().str.contains('atac|ataque|avanc', na=False),
        0.5*df['media'] + 0.5*df['indice_ofensivo'],
        0.6*df['media'] + 0.4*df['indice_defensivo']
    )

    df['volatilidade'] = df[scouts_expected].std(axis=1).fillna(0.0)
    df['score_expect'] = (df['score_base'] - 0.2*df['volatilidade']).clip(lower=0.0)

    df.sort_values(by='score_expect', ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


# --------------------------- UI ---------------------------

def setup_page():
    st.set_page_config(page_title=APP_TITLE, layout='wide')
    st.title(APP_TITLE)

def sidebar_controls(df: pd.DataFrame) -> Dict:
    st.sidebar.header('Configurações')
    use_api = st.sidebar.checkbox('Usar API oficial (Cartola)', value=True)
    csv_file = st.sidebar.file_uploader('CSV de fallback (opcional)', type=['csv'])
    budget = st.sidebar.number_input('Budget (C$)', value=DEFAULT_BUDGET, min_value=10.0)
    max_per_club = st.sidebar.number_input('Máx por clube', value=MAX_PER_CLUB_DEFAULT, min_value=1)
    formation_choice = st.sidebar.selectbox('Formação padrão', ['4-4-2','3-5-2','4-3-3'])
    formation_map = {
        '4-4-2': {'GOL':1, 'DEF':4, 'MEI':4, 'ATA':2},
        '3-5-2': {'GOL':1, 'DEF':3, 'MEI':5, 'ATA':2},
        '4-3-3': {'GOL':1, 'DEF':4, 'MEI':3, 'ATA':3}
    }

    pos_options = sorted(df['posicao'].dropna().unique().tolist()) if not df.empty else []
    pos_sel = st.sidebar.multiselect('Posições', options=pos_options, default=pos_options)
    club_options = sorted(df['clube'].dropna().unique().tolist()) if not df.empty else []
    club_sel = st.sidebar.multiselect('Clubes', options=club_options, default=club_options)
    status_options = sorted(df['status'].dropna().unique().tolist()) if not df.empty else []
    status_sel = st.sidebar.multiselect('Status', options=status_options, default=status_options)

    return {
        'use_api': use_api,
        'csv_file': csv_file.read() if csv_file is not None else None,
        'budget': budget,
        'max_per_club': max_per_club,
        'formation': formation_map[formation_choice],
        'pos_sel': pos_sel,
        'club_sel': club_sel,
        'status_sel': status_sel
    }

def main():
    setup_page()
    st.sidebar.markdown('Data App para escalar jogadores no Cartola. Fallback de solver incluso.')

    # initial controls to allow CSV upload before fetch
    initial_controls = sidebar_controls(pd.DataFrame())
    df, status = fetch_cartola_data(use_api=initial_controls['use_api'], csv_file=initial_controls['csv_file'])
    if df.empty:
        st.error('Sem dados. Verifique API ou faça upload de CSV.')
        st.stop()

    controls = sidebar_controls(df)

    # apply filters
    df_filtered = df[
        df['posicao'].isin(controls['pos_sel']) &
        df['clube'].isin(controls['club_sel']) &
        df['status'].astype(str).isin([str(s) for s in controls['status_sel']])
    ].copy()

    tabs = st.tabs(['Visão Geral','Otimização','Análise Avançada','Dados'])

    with tabs[0]:
        st.header('Visão Geral')
        c1, c2, c3 = st.columns(3)
        c1.metric('Jogadores', f"{len(df_filtered):,}")
        c2.metric('Preço médio (C$)', f"{df_filtered['preco'].mean():.2f}")
        c3.metric('Pontos médios', f"{df_filtered['media'].mean():.2f}")

        st.markdown('### Top por Score Esperado')
        st.dataframe(df_filtered[['nome','clube','posicao','preco','media','score_expect']].head(20))
        st.markdown('### Scatter: Preço x Score Esperado')
        fig = px.scatter(df_filtered, x='preco', y='score_expect', color='posicao', hover_name='nome', size='media', template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        st.header('Otimização de Escalação')
        st.markdown('Defina constraints e gere escalação ótima (ILP se PuLP instalado ou heurística fallback).')
        budget = controls['budget']
        max_per_club = controls['max_per_club']
        formation = controls['formation']

        if st.button('Gerar escalação otimizada'):
            selected, captain = optimize_lineup(df_filtered, budget, formation, max_per_club)
            if selected is None or selected.empty:
                st.warning('Solver não retornou escalação. Ajuste parâmetros.')
            else:
                st.markdown('### Escalação sugerida')
                st.table(selected[['nome','clube','posicao','preco','score_expect']])
                if captain:
                    st.info(f"Capitão sugerido: {captain.get('nome')} — Score: {captain.get('score_expect'):.2f}")
                csv = selected.to_csv(index=False).encode('utf-8')
                st.download_button('Baixar escalação (CSV)', data=csv, file_name=f'escalação_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')

    with tabs[2]:
        st.header('Análise Avançada')
        st.markdown("""
        - Índices ofensivos e defensivos
        - Top por custo-benefício
        - Volatilidade e consistência
        """)
        st.markdown('### Top 10 custo-benefício')
        st.dataframe(df_filtered.nlargest(10, 'custo_beneficio')[['nome','clube','posicao','preco','media','custo_beneficio']])
        st.markdown('### Distribuição de Scores')
        fig = px.histogram(df_filtered, x='score_expect', nbins=30, template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)

    with tabs[3]:
        st.header('Dados')
        st.dataframe(df_filtered, use_container_width=True)
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button('Baixar dados filtrados (CSV)', data=csv, file_name=f'cartola_dados_{datetime.now().strftime("%Y%m%d")}.csv')

if __name__ == '__main__':
    main()


