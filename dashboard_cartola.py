# -*- coding: utf-8 -*-
"""
Dashboard Cartola FC 2025 — versão otimizada
Autor original: Carlos Willian | Refatoração: IA

Principais melhorias desta versão:
- UX: organização por seções/tabs, cabeçalho compacto, métricas claras, tooltips e ajuda contextual
- Filtros: formação + orçamento, filtros salvos na URL (deep-linking), reset rápido e botão de atualizar cache
- KPIs: novos indicadores (distribuição por posição/clubes, variação de preço quando existir)
- Visual: layout com st.columns, st.metric, uso consistente do tema e cores do Plotly
- Storytelling: mensagens/insights automáticos baseados no recorte atual
- Ações específicas: gráfico de eficiência por posição e ranking ofensivo/defensivo
- Comparador: melhorias e gráfico radar com Plotly para ver perfil dos 2 atletas
- Exportação: CSV e Excel (xlsx)
- Robustez: headers na API, retry, degradação graciosa quando um endpoint falhar

Observação: o endpoint oficial do Cartola pode variar ao longo da temporada. Caso a autenticação
ou o CORS mude, acrescente um token/headers válidos em `API_HEADERS`.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import plotly.express as px
import plotly.graph_objects as go
import io
import json
import time
from typing import Dict, Tuple, List

# ----------------------------------
# CONFIG BÁSICO
# ----------------------------------
st.set_page_config(
    page_title="Cartola FC 2025 — Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------
# CONSTANTES & API
# ----------------------------------
API_URLS = {
    "mercado": "https://api.cartola.globo.com/atletas/mercado",
    "status": "https://api.cartola.globo.com/mercado/status",
    "pontuados": "https://api.cartola.globo.com/atletas/pontuados",
}
API_HEADERS = {
    # Ajuste estes headers se a API exigir. Mantemos um User-Agent "humano".
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}
CACHE_TTL = 300  # 5 min
TIMEOUT = 12
MAX_RETRIES = 3

# ----------------------------------
# ESTILO (CSS SUAVE)
# ----------------------------------
CSS = """
<style>
/********* Tipografia básica *********/
:root{--c0:#0f172a;--c1:#1e293b;--c2:#334155;--b0:#ffffff;--b1:#f8fafc;--p:#3b82f6;--s:#10b981;--w:#f59e0b;--d:#ef4444}
html, body, .stApp{background:linear-gradient(135deg,#f8fafc,#ffffff);}
h1,h2,h3{letter-spacing:-.02em}

/********* Métricas *********/
[data-testid="metric-container"]{border:1px solid #e5e7eb;border-radius:16px;padding:1.2rem;background:rgba(255,255,255,.9)}

/********* Tabela *********/
.stDataFrame{border:1px solid #e5e7eb;border-radius:12px;background:#fff}

/********* Botões *********/
.stButton>button{border-radius:10px}

/********* Tabs *********/
.stTabs [data-baseweb="tab-list"]{border:1px solid #e5e7eb;border-radius:14px;padding:.3rem;background:#fff}
.stTabs [data-baseweb="tab"]{text-transform:uppercase;font-size:.8rem}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ----------------------------------
# FUNÇÕES UTILITÁRIAS
# ----------------------------------
class ApiException(Exception):
    pass

def _request_json(url: str) -> Dict:
    last_err = None
    for _ in range(MAX_RETRIES):
        try:
            r = requests.get(url, headers=API_HEADERS, timeout=TIMEOUT)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_err = e
            time.sleep(1)
    raise ApiException(f"API falhou em {url}: {last_err}")

@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_data() -> pd.DataFrame:
    # status (opcional)
    try:
        status = _request_json(API_URLS["status"]) or {}
        status_desc = status.get("status_mercado_desc", "Desconhecido")
    except Exception:
        status_desc = "Indisponível"

    # mercado
    dados = _request_json(API_URLS["mercado"])
    if not all(k in dados for k in ("atletas", "clubes", "posicoes")):
        raise ApiException("Resposta inesperada do endpoint de mercado.")

    clubes = dados["clubes"]  # dict str(id)->obj
    posicoes = dados["posicoes"]

    registros = []
    for j in dados["atletas"]:
        scouts = j.get("scout", {}) or {}
        registros.append({
            "ID": j.get("atleta_id"),
            "Nome": j.get("apelido", "-"),
            "Clube": (clubes.get(str(j.get("clube_id")), {}) or {}).get("nome", "-"),
            "Posição": (posicoes.get(str(j.get("posicao_id")), {}) or {}).get("nome", "-"),
            "Preço (C$)": float(j.get("preco_num", 0.0)),
            "Pontos Média": float(j.get("media_num", 0.0)),
            "Partidas": int(j.get("jogos_num", 0)),
            "Variação": float(j.get("variacao_num", 0.0)),
            "Status Mercado": status_desc,
            **scouts,
        })

    df = pd.DataFrame(registros)
    if df.empty:
        return df

    # Métricas derivadas
    df["Pontos por C$"] = (df["Pontos Média"] / df["Preço (C$)"].replace(0, np.nan)).fillna(0).round(3)
    df["Consistência (%)"] = ((df["Partidas"].clip(lower=0) / 38) * 100).round(1)

    # Status (com base em média)
    df["Status"] = pd.cut(
        df["Pontos Média"],
        bins=[-np.inf, 2, 5, 8, np.inf],
        labels=["🔴 Baixo", "🟡 Regular", "🟢 Bom", "🔵 Excelente"],
    )

    # Ações ofensivas/defensivas (heurístico)
    def _safe(row, key):
        v = row.get(key, 0)
        return 0 if pd.isna(v) else v
    df["Pts Ofensivos"] = df.apply(lambda r: _safe(r, "G")*8 + _safe(r, "A")*5 + _safe(r, "FC")*1.2, axis=1)
    df["Pts Def. Linha"] = df.apply(lambda r: _safe(r, "DS")*1.7 + _safe(r, "I")*1.8 + _safe(r, "FS")*0.5, axis=1)
    df["Pts Def. Goleiro"] = df.apply(lambda r: (_safe(r, "DD")*3.2 + _safe(r, "GC")*(-4)) if r["Posição"]=="Goleiro" else 0, axis=1)

    # Pequena coluna de "Forma" (proxy: últimas 5 partidas não disponíveis -> usamos pontuação média)
    df["Forma (proxy)"] = pd.cut(
        df["Pontos Média"],
        bins=[-np.inf, 2, 4, 6, np.inf],
        labels=["📉 Baixa", "📊 Regular", "⚡ Boa", "🔥 Excelente"],
    )
    return df

# ----------------------------------
# PERSISTÊNCIA DE FILTROS NA URL
# ----------------------------------

def sync_query_params(**kwargs):
    st.experimental_set_query_params(**{k: v for k, v in kwargs.items() if v not in (None, "", [])})

def read_query_list(name: str, options: List[str]) -> List[str]:
    qp = st.experimental_get_query_params().get(name, [])
    sel = [q for q in qp if q in options]
    return sel or options  # fallback: tudo

# ----------------------------------
# SIDEBAR
# ----------------------------------

def sidebar_filters(df: pd.DataFrame) -> Tuple:
    st.sidebar.header("⚙️ Painel de Controle")

    with st.sidebar.expander("🎯 Filtros principais", expanded=True):
        posicoes = sorted(df["Posição"].dropna().unique().tolist())
        pos_sel_default = read_query_list("pos", posicoes)
        pos_sel = st.multiselect("Posição", posicoes, default=pos_sel_default)

        clubes = sorted(df["Clube"].dropna().unique().tolist())
        club_sel_default = read_query_list("club", clubes)
        club_sel = st.multiselect("Clube", clubes, default=club_sel_default)

    with st.sidebar.expander("💰 Orçamento e formação", expanded=True):
        budget = st.slider("Orçamento (C$)", 50, int(max(200, df["Preço (C$)"].max())), 100)
        formacoes = {
            "3-4-3": {"Goleiro":1, "Zagueiro":3, "Lateral":0, "Meia":4, "Atacante":3},
            "4-3-3": {"Goleiro":1, "Zagueiro":2, "Lateral":2, "Meia":3, "Atacante":3},
            "4-4-2": {"Goleiro":1, "Zagueiro":2, "Lateral":2, "Meia":4, "Atacante":2},
            "3-5-2": {"Goleiro":1, "Zagueiro":3, "Lateral":0, "Meia":5, "Atacante":2},
        }
        formacao_nome = st.selectbox("Formação", list(formacoes.keys()), index=0)

    with st.sidebar.expander("📊 Faixas de valores", expanded=True):
        pmin, pmax = float(df["Preço (C$)"].min()), float(df["Preço (C$)"].max())
        pr = st.slider("Preço (C$)", int(pmin), int(pmax), (int(pmin), int(pmax)))
        mmin, mmax = float(df["Pontos Média"].min()), float(df["Pontos Média"].max())
        mr = st.slider("Pontos média", float(mmin), float(mmax), (float(mmin), float(mmax)))
        jmin, jmax = int(df["Partidas"].min()), int(df["Partidas"].max())
        jr = st.slider("Partidas", jmin, jmax, (jmin, jmax))

    with st.sidebar.expander("⚡ Avançado", expanded=False):
        pc_min = st.slider("Pontos por C$ mínimo", 0.0, float(df["Pontos por C$"].max() or 1.0), 0.0, step=0.01)
        cons_min = st.slider("Consistência mínima (%)", 0.0, 100.0, 0.0, step=1.0)
        st.caption("Dica: combine eficiência com consistência para times mais estáveis.")

    col_a, col_b = st.sidebar.columns(2)
    with col_a:
        if st.button("🔄 Atualizar cache"):
            load_data.clear()
            st.experimental_rerun()
    with col_b:
        if st.button("♻️ Reset filtros"):
            st.experimental_set_query_params()
            st.experimental_rerun()

    # refletir filtros na URL
    sync_query_params(pos=pos_sel, club=club_sel)
    return pos_sel, club_sel, pr, mr, jr, pc_min, cons_min, budget, formacao_nome

# ----------------------------------
# FILTRAGEM
# ----------------------------------

def apply_filters(df: pd.DataFrame, pos_sel, club_sel, pr, mr, jr, pc_min, cons_min) -> pd.DataFrame:
    if df.empty:
        return df
    f = df[
        df["Posição"].isin(pos_sel)
        & df["Clube"].isin(club_sel)
        & df["Preço (C$)"].between(pr[0], pr[1])
        & df["Pontos Média"].between(mr[0], mr[1])
        & df["Partidas"].between(jr[0], jr[1])
    ].copy()
    if pc_min > 0:
        f = f[f["Pontos por C$"] >= pc_min]
    if cons_min > 0:
        f = f[f["Consistência (%)"] >= cons_min]
    return f

# ----------------------------------
# SELEÇÃO IDEAL (heurística simples)
# ----------------------------------

def pick_best_team(df: pd.DataFrame, formacao: Dict[str, int], budget: float) -> Tuple[pd.DataFrame, float, float]:
    """Seleciona um time por eficiência (Pontos/C$), respeitando posições e orçamento.
    Heurística gananciosa + queda de preço se extrapolar.
    """
    picks = []
    total = 0.0
    # escolhe por posição, priorizando eficiência
    for pos, qtd in formacao.items():
        cand = df[df["Posição"] == pos].sort_values(["Pontos por C$", "Pontos Média"], ascending=False)
        if cand.empty:
            continue
        picks.append(cand.head(qtd))
    if not picks:
        return pd.DataFrame(), 0.0, 0.0
    team = pd.concat(picks, ignore_index=True)

    # se estourou orçamento, tenta reduzir por menos preço mantendo média decente
    cost = team["Preço (C$)"].sum()
    if cost > budget:
        for pos, qtd in formacao.items():
            # substitui os mais caros por opções mais baratas da mesma posição
            pool = df[df["Posição"] == pos].sort_values(["Preço (C$)", "Pontos Média"], ascending=[True, False])
            need = qtd
            repl = pool.head(need)
            team = team[team["Posição"] != pos]
            team = pd.concat([team, repl], ignore_index=True)
            cost = team["Preço (C$)"].sum()
            if cost <= budget:
                break

    points = team["Pontos Média"].sum()
    return team, float(cost), float(points)

# ----------------------------------
# GRÁFICOS
# ----------------------------------

def price_vs_points(df: pd.DataFrame):
    fig = px.scatter(
        df,
        x="Preço (C$)", y="Pontos Média", color="Posição", size="Partidas",
        hover_name="Nome", hover_data=["Clube", "Pontos por C$"],
        title="Preço x Pontuação média (tamanho = partidas)", height=520,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def top_efficiency(df: pd.DataFrame, n=12):
    if "Pontos por C$" not in df:
        return
    top = df.sort_values("Pontos por C$", ascending=False).head(n)
    fig = px.bar(top, x="Pontos por C$", y="Nome", orientation="h", hover_data=["Clube", "Preço (C$)", "Pontos Média"], title=f"Top {n} eficiência (Pontos/C$)")
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def position_distribution(df: pd.DataFrame):
    ct = df["Posição"].value_counts().reset_index()
    ct.columns = ["Posição", "Qtd"]
    fig = px.pie(ct, values="Qtd", names="Posição", title="Distribuição por posição")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def club_distribution(df: pd.DataFrame, topn=12):
    ct = df["Clube"].value_counts().head(topn).reset_index()
    ct.columns = ["Clube", "Qtd"]
    fig = px.bar(ct, x="Clube", y="Qtd", title=f"Top {topn} clubes (qtd jogadores no recorte)")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def radar_two_players(p1: pd.Series, p2: pd.Series):
    # normaliza métricas
    cols = ["Pontos Média", "Pontos por C$", "Partidas", "Pts Ofensivos", "Pts Def. Linha", "Pts Def. Goleiro"]
    df = pd.DataFrame([p1[cols], p2[cols]], index=[p1["Nome"], p2["Nome"]]).fillna(0)
    # escala 0-1
    norm = (df - df.min())/(df.max()-df.min()+1e-9)
    categories = cols
    fig = go.Figure()
    for idx, row in norm.iterrows():
        fig.add_trace(go.Scatterpolar(r=row.values.tolist()+[row.values[0]], theta=categories+[categories[0]], fill='toself', name=idx))
    fig.update_layout(title="Perfil comparativo (normalizado)", polar=dict(radialaxis=dict(visible=True)), showlegend=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ----------------------------------
# UI — CABEÇALHO
# ----------------------------------

def header(df: pd.DataFrame):
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("👥 Jogadores", f"{len(df):,}")
    col2.metric("💰 Preço médio", f"C$ {df['Preço (C$)'].mean():.1f}")
    col3.metric("📊 Pontos médios", f"{df['Pontos Média'].mean():.1f}")
    col4.metric("💎 Retorno médio", f"{df['Pontos por C$'].mean():.3f}")
    col5.metric("🎯 Consistência", f"{df['Consistência (%)'].mean():.1f}%")

    # insight curto
    best = df.sort_values("Pontos por C$", ascending=False).head(1)
    if not best.empty:
        b = best.iloc[0]
        st.info(f"Melhor eficiência agora: **{b['Nome']}** ({b['Clube']}, {b['Posição']}) com **{b['Pontos por C$']:.3f} pts/C$**.")

# ----------------------------------
# PÁGINA PRINCIPAL
# ----------------------------------

def main():
    st.title("⚽ Dashboard Cartola FC 2025")
    with st.spinner("Carregando dados do Cartola..."):
        try:
            df = load_data()
        except Exception as e:
            st.error(f"Não foi possível carregar os dados: {e}")
            st.stop()

    if df.empty:
        st.warning("Nenhum dado retornado pela API.")
        st.stop()

    # filtros
    pos_sel, club_sel, pr, mr, jr, pc_min, cons_min, budget, formacao_nome = sidebar_filters(df)
    df_f = apply_filters(df, pos_sel, club_sel, pr, mr, jr, pc_min, cons_min)

    # header KPIs
    header(df_f if not df_f.empty else df)

    st.markdown("---")

    tab_overview, tab_actions, tab_compare, tab_team, tab_export = st.tabs([
        "📊 Visão Geral", "⚙️ Ações Específicas", "⚔️ Comparador", "🧠 Seleção Ideal", "📁 Exportar"
    ])

    with tab_overview:
        st.subheader("Panorama do recorte atual")
        c1, c2 = st.columns([3,2])
        with c1:
            price_vs_points(df_f)
        with c2:
            top_efficiency(df_f, n=12)
        c3, c4 = st.columns(2)
        with c3:
            position_distribution(df_f)
        with c4:
            club_distribution(df_f)

        st.markdown("### Lista de jogadores (ordenável)")
        cols = ["Nome","Clube","Posição","Preço (C$)","Pontos Média","Pontos por C$","Partidas","Consistência (%)","Status","Forma (proxy)"]
        cols = [c for c in cols if c in df_f.columns]
        st.dataframe(
            df_f.sort_values(["Pontos Média","Pontos por C$"], ascending=False)[cols],
            use_container_width=True, height=420,
        )

    with tab_actions:
        st.subheader("Eficiência por posição")
        colA, colB = st.columns(2)
        with colA:
            g1 = df_f.groupby("Posição")["Pontos por C$"].mean().reset_index().sort_values("Pontos por C$", ascending=False)
            fig = px.bar(g1, x="Posição", y="Pontos por C$", title="Média de Pontos/C$ por posição")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        with colB:
            g2 = df_f.groupby("Posição")["Pontos Média"].mean().reset_index().sort_values("Pontos Média", ascending=False)
            fig2 = px.bar(g2, x="Posição", y="Pontos Média", title="Média de pontos por posição")
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        st.markdown("### Rankings ofensivo/defensivo")
        cc1, cc2 = st.columns(2)
        with cc1:
            top_of = df_f.sort_values("Pts Ofensivos", ascending=False).head(15)
            st.dataframe(top_of[["Nome","Clube","Posição","Pts Ofensivos","Pontos Média","Preço (C$)"]], use_container_width=True, height=350)
        with cc2:
            top_def = df_f.assign(DefTotal=lambda d: d["Pts Def. Linha"]+d["Pts Def. Goleiro"]).sort_values("DefTotal", ascending=False).head(15)
            st.dataframe(top_def[["Nome","Clube","Posição","DefTotal","Pontos Média","Preço (C$)"]], use_container_width=True, height=350)

    with tab_compare:
        st.subheader("Comparador de dois jogadores")
        options = df_f["Nome"].sort_values().unique().tolist()
        col1, col2 = st.columns(2)
        with col1:
            a = st.selectbox("Jogador A", options, key="cmpA")
        with col2:
            b = st.selectbox("Jogador B", options, key="cmpB")
        if a and b and a != b:
            p1 = df_f[df_f["Nome"]==a].iloc[0]
            p2 = df_f[df_f["Nome"]==b].iloc[0]
            c1, c2, c3 = st.columns(3)
            c1.metric("Preço A", f"C$ {p1['Preço (C$)']:.1f}")
            c2.metric("Pontos médios A", f"{p1['Pontos Média']:.2f}")
            c3.metric("Pontos/C$ A", f"{p1['Pontos por C$']:.3f}")
            d1, d2, d3 = st.columns(3)
            d1.metric("Preço B", f"C$ {p2['Preço (C$)']:.1f}")
            d2.metric("Pontos médios B", f"{p2['Pontos Média']:.2f}")
            d3.metric("Pontos/C$ B", f"{p2['Pontos por C$']:.3f}")
            radar_two_players(p1, p2)
        else:
            st.info("Escolha dois jogadores distintos para comparar.")

    with tab_team:
        st.subheader("Seleção ideal por formação e orçamento")
        formacoes = {
            "3-4-3": {"Goleiro":1, "Zagueiro":3, "Lateral":0, "Meia":4, "Atacante":3},
            "4-3-3": {"Goleiro":1, "Zagueiro":2, "Lateral":2, "Meia":3, "Atacante":3},
            "4-4-2": {"Goleiro":1, "Zagueiro":2, "Lateral":2, "Meia":4, "Atacante":2},
            "3-5-2": {"Goleiro":1, "Zagueiro":3, "Lateral":0, "Meia":5, "Atacante":2},
        }
        team, cost, pts = pick_best_team(df_f, formacoes[formacao_nome], budget)
        if team.empty:
            st.warning("Não foi possível montar time com os filtros atuais. Amplie o recorte ou aumente o orçamento.")
        else:
            colx, coly, colz = st.columns(3)
            colx.metric("👥 Jogadores", str(len(team)))
            coly.metric("💰 Custo total", f"C$ {cost:.1f}")
            colz.metric("📈 Pontos médios somados", f"{pts:.1f}")
            st.dataframe(team[["Nome","Clube","Posição","Preço (C$)","Pontos Média","Pontos por C$"]].sort_values(["Posição","Pontos por C$"], ascending=[True, False]), use_container_width=True, height=380)

    with tab_export:
        st.subheader("Exportar dados do recorte atual")
        c1, c2 = st.columns(2)
        with c1:
            csv = df_f.to_csv(index=False)
            st.download_button("⬇️ Baixar CSV", data=csv, file_name=f"cartola_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")
        with c2:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df_f.to_excel(writer, index=False, sheet_name="dados")
            st.download_button("⬇️ Baixar Excel", data=buffer.getvalue(), file_name=f"cartola_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.caption("O resumo JSON pode ser útil para integrações rápidas com outras aplicações.")
        resumo = {
            "total_jogadores": int(len(df_f)),
            "data_exportacao": datetime.now().isoformat(),
            "top_10": df_f.sort_values("Pontos Média", ascending=False).head(10)[["Nome","Clube","Pontos Média"]].to_dict("records"),
        }
        st.download_button("⬇️ Baixar resumo JSON", data=json.dumps(resumo, ensure_ascii=False, indent=2), file_name=f"cartola_resumo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

    # rodapé
    st.markdown("---")
    st.caption("Fonte: API oficial do Cartola FC • Atualizado agora em " + datetime.now().strftime("%d/%m/%Y %H:%M"))


if __name__ == "__main__":
    main()
