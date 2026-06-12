"""
DataViz Dashboard v2 — app.py
==============================
Améliorations v2 :
  - Dark / Light mode toggle dans le header
  - Design épuré, cartes métriques animées
  - Sidebar minimaliste avec sections claires
  - Graphiques avec transitions et tooltips enrichis
  - Nouveau : graphique violin, funnel, sunburst
  - Nouveau : export PNG du graphique
  - Nouveau : résumé IA des données (statistiques auto-commentées)
  - Nouveau : détection des outliers visuels
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import numpy as np

# ─────────────────────────────────────────────────────────────────
# 1. CONFIG PAGE
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DataViz Studio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# 2. GESTION DU THÈME (Dark / Light)
# ─────────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Palettes de couleurs
DARK = {
    "bg":           "#0d1117",
    "surface":      "#161b27",
    "surface2":     "#1e2435",
    "border":       "#2d3347",
    "text":         "#e8eaf0",
    "text_muted":   "#7b8096",
    "accent":       "#6c63ff",
    "accent2":      "#8b80ff",
    "success":      "#3ecf8e",
    "warning":      "#f59e0b",
    "danger":       "#ef4444",
    "plotly_tmpl":  "plotly_dark",
}
LIGHT = {
    "bg":           "#f0f2f8",
    "surface":      "#ffffff",
    "surface2":     "#f8f9fc",
    "border":       "#dde1f0",
    "text":         "#1a1d2e",
    "text_muted":   "#6b7080",
    "accent":       "#5046e4",
    "accent2":      "#6c63ff",
    "success":      "#059669",
    "warning":      "#d97706",
    "danger":       "#dc2626",
    "plotly_tmpl":  "plotly_white",
}

C = DARK if st.session_state.dark_mode else LIGHT

def inject_css(C):
    st.markdown(f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

      /* ── Reset global ── */
      * {{ box-sizing: border-box; }}
      .stApp {{
          background-color: {C['bg']};
          font-family: 'Inter', sans-serif;
      }}

      /* ── Sidebar ── */
      [data-testid="stSidebar"] {{
          background-color: {C['surface']};
          border-right: 1px solid {C['border']};
      }}
      [data-testid="stSidebar"] * {{
          font-family: 'Inter', sans-serif !important;
      }}

      /* ── Labels universels ── */
      label, .stSelectbox label, .stFileUploader label,
      .stSlider label, .stMultiSelect label {{
          color: {C['text_muted']} !important;
          font-family: 'JetBrains Mono', monospace !important;
          font-size: 0.70rem !important;
          font-weight: 500 !important;
          letter-spacing: 0.08em;
          text-transform: uppercase;
      }}

      /* ── Titres ── */
      h1, h2, h3, h4 {{ color: {C['text']} !important; font-family: 'Inter', sans-serif !important; }}

      /* ── Métriques ── */
      [data-testid="metric-container"] {{
          background: {C['surface2']};
          border: 1px solid {C['border']};
          border-radius: 14px;
          padding: 16px 20px !important;
          transition: box-shadow 0.2s ease;
      }}
      [data-testid="metric-container"]:hover {{
          box-shadow: 0 4px 20px {C['accent']}22;
          border-color: {C['accent']}55;
      }}
      [data-testid="metric-container"] > div:first-child {{
          color: {C['accent']} !important;
          font-family: 'JetBrains Mono', monospace !important;
          font-size: 0.68rem !important;
          text-transform: uppercase;
          letter-spacing: 0.12em;
          font-weight: 500;
      }}
      [data-testid="metric-container"] [data-testid="stMetricValue"] {{
          color: {C['text']} !important;
          font-family: 'JetBrains Mono', monospace !important;
          font-size: 1.8rem !important;
          font-weight: 600;
      }}

      /* ── Boutons ── */
      .stButton > button {{
          background: {C['accent']};
          color: white !important;
          border: none;
          border-radius: 10px;
          font-family: 'Inter', sans-serif;
          font-weight: 600;
          font-size: 0.85rem;
          padding: 0.5rem 1.2rem;
          transition: all 0.2s ease;
          box-shadow: 0 2px 8px {C['accent']}44;
      }}
      .stButton > button:hover {{
          transform: translateY(-1px);
          box-shadow: 0 4px 16px {C['accent']}66;
          opacity: 0.92;
      }}

      /* ── Tabs ── */
      [data-testid="stTabs"] [role="tab"] {{
          color: {C['text_muted']} !important;
          font-family: 'Inter', sans-serif;
          font-weight: 500;
          font-size: 0.88rem;
          border-radius: 8px 8px 0 0;
      }}
      [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
          color: {C['accent']} !important;
          border-bottom: 2px solid {C['accent']};
      }}

      /* ── Dataframe ── */
      [data-testid="stDataFrame"] {{
          border: 1px solid {C['border']};
          border-radius: 10px;
          overflow: hidden;
      }}

      /* ── Alertes ── */
      .stAlert {{ border-radius: 10px !important; }}

      /* ── Séparateur ── */
      hr {{ border-color: {C['border']} !important; margin: 1rem 0 !important; }}

      /* ── Selectbox ── */
      [data-testid="stSelectbox"] > div > div {{
          background: {C['surface2']};
          border: 1px solid {C['border']};
          border-radius: 8px;
          color: {C['text']};
      }}

      /* ── Sidebar section titles ── */
      .sidebar-section {{
          color: {C['text_muted']};
          font-family: 'JetBrains Mono', monospace;
          font-size: 0.65rem;
          text-transform: uppercase;
          letter-spacing: 0.15em;
          font-weight: 600;
          margin: 1.2rem 0 0.4rem 0;
          padding-bottom: 4px;
          border-bottom: 1px solid {C['border']};
      }}

      /* ── Pill badge ── */
      .pill {{
          display: inline-block;
          padding: 2px 10px;
          border-radius: 20px;
          font-size: 0.72rem;
          font-family: 'JetBrains Mono', monospace;
          font-weight: 500;
          margin: 2px;
      }}
      .pill-quant {{ background: {C['accent']}22; color: {C['accent']}; border: 1px solid {C['accent']}44; }}
      .pill-quali {{ background: {C['success']}22; color: {C['success']}; border: 1px solid {C['success']}44; }}
      .pill-temp  {{ background: {C['warning']}22; color: {C['warning']}; border: 1px solid {C['warning']}44; }}

      /* ── Card ── */
      .stat-card {{
          background: {C['surface2']};
          border: 1px solid {C['border']};
          border-radius: 12px;
          padding: 16px;
          margin-bottom: 8px;
      }}

      /* ── Progress bar personnalisée ── */
      .null-bar-bg {{
          background: {C['border']};
          border-radius: 4px;
          height: 6px;
          margin-top: 4px;
      }}

      /* Masquer éléments Streamlit non désirés */
      #MainMenu, footer, [data-testid="stToolbar"] {{ visibility: hidden; }}

      /* ── Upload zone ── */
      [data-testid="stFileUploader"] {{
          border: 1.5px dashed {C['border']};
          border-radius: 12px;
          padding: 8px;
          background: {C['surface2']};
          transition: border-color 0.2s;
      }}
      [data-testid="stFileUploader"]:hover {{ border-color: {C['accent']}; }}

      /* ── Caption ── */
      .stCaption {{ color: {C['text_muted']} !important; font-size: 0.78rem !important; }}

      /* ── Multiselect tags ── */
      [data-testid="stMultiSelect"] span[data-baseweb="tag"] {{
          background: {C['accent']}33 !important;
          color: {C['accent']} !important;
          border-radius: 6px !important;
      }}
    </style>
    """, unsafe_allow_html=True)

inject_css(C)

# ─────────────────────────────────────────────────────────────────
# 3. CHARGEMENT DES DONNÉES
# ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Lecture du fichier…")
def load_data(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    raw = uploaded_file.read()

    if name.endswith(".csv"):
        for enc in ["utf-8", "latin-1", "cp1252"]:
            try:
                df = pd.read_csv(io.BytesIO(raw), encoding=enc)
                _auto_parse_dates(df)
                return df
            except UnicodeDecodeError:
                continue
        raise ValueError("Impossible de décoder le CSV. Essayez de le convertir en UTF-8.")

    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(raw))
        _auto_parse_dates(df)
        return df

    raise ValueError("Format non supporté — utilisez CSV ou Excel (.xlsx / .xls).")

def _auto_parse_dates(df: pd.DataFrame):
    """Tente de convertir silencieusement les colonnes object en datetime."""
    for col in df.select_dtypes(include="object").columns:
        try:
            converted = pd.to_datetime(df[col], infer_datetime_format=True)
            if converted.notna().sum() > len(df) * 0.6:   # au moins 60% valides
                df[col] = converted
        except Exception:
            pass

# ─────────────────────────────────────────────────────────────────
# 4. DÉTECTION TYPES DE COLONNES
# ─────────────────────────────────────────────────────────────────
def detect_col_types(df: pd.DataFrame) -> dict:
    types = {"quantitative": [], "qualitative": [], "temporelle": []}
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            types["temporelle"].append(col)
        elif pd.api.types.is_numeric_dtype(df[col]):
            types["quantitative"].append(col)
        else:
            types["qualitative"].append(col)
    return types

# ─────────────────────────────────────────────────────────────────
# 5. FILTRES SIDEBAR
# ─────────────────────────────────────────────────────────────────
def apply_filters(df: pd.DataFrame, col_types: dict) -> pd.DataFrame:
    st.sidebar.markdown('<p class="sidebar-section">🔍 Filtre</p>', unsafe_allow_html=True)

    filter_col = st.sidebar.selectbox(
        "Colonne à filtrer",
        ["(aucun)"] + df.columns.tolist(),
        key="filter_col",
    )
    if filter_col == "(aucun)":
        return df

    if filter_col in col_types["quantitative"]:
        col_min = float(df[filter_col].min())
        col_max = float(df[filter_col].max())
        if col_min == col_max:
            return df
        rng = st.sidebar.slider(f"{filter_col}", col_min, col_max, (col_min, col_max))
        return df[df[filter_col].between(*rng)]

    elif filter_col in col_types["qualitative"]:
        opts = df[filter_col].dropna().unique().tolist()
        sel = st.sidebar.multiselect(f"{filter_col}", options=opts, default=opts)
        return df[df[filter_col].isin(sel)] if sel else df

    elif filter_col in col_types["temporelle"]:
        d_min, d_max = df[filter_col].min().date(), df[filter_col].max().date()
        rng = st.sidebar.date_input(f"{filter_col}", value=(d_min, d_max), min_value=d_min, max_value=d_max)
        if len(rng) == 2:
            return df[(df[filter_col] >= pd.Timestamp(rng[0])) & (df[filter_col] <= pd.Timestamp(rng[1]))]

    return df

# ─────────────────────────────────────────────────────────────────
# 6. RECOMMANDATIONS GRAPHIQUES
# ─────────────────────────────────────────────────────────────────
CHART_TYPES = [
    "Bar chart", "Histogramme", "Scatter plot", "Box plot",
    "Violin plot", "Line chart", "Pie chart", "Sunburst",
    "Heatmap (corrélation)", "Funnel",
]

def recommend_charts(col_types, x_col, y_col):
    q = col_types["quantitative"]
    ql = col_types["qualitative"]
    t = col_types["temporelle"]
    recs = []
    if x_col in t:                                  recs += ["Line chart"]
    if x_col in ql and y_col is None:               recs += ["Bar chart", "Pie chart"]
    if x_col in q  and y_col is None:               recs += ["Histogramme"]
    if x_col in ql and y_col and y_col in q:        recs += ["Box plot", "Violin plot", "Bar chart"]
    if x_col in q  and y_col and y_col in q:        recs += ["Scatter plot", "Histogramme"]
    if len(ql) >= 2:                                recs += ["Sunburst"]
    if len(q)  >= 2:                                recs += ["Heatmap (corrélation)"]
    if not recs:                                    recs = CHART_TYPES[:4]
    return list(dict.fromkeys(recs))

# ─────────────────────────────────────────────────────────────────
# 7. GÉNÉRATION DU GRAPHIQUE
# ─────────────────────────────────────────────────────────────────
def build_chart(df, chart_type, x_col, y_col, color_col, C):
    tmpl = C["plotly_tmpl"]
    bg   = C["surface"]
    bg2  = C["surface2"]
    fc   = C["text_muted"]
    title = f"{chart_type}  ·  {x_col}" + (f"  ×  {y_col}" if y_col else "")

    kw = dict(template=tmpl, title=title)

    layout_extra = dict(
        paper_bgcolor=bg,
        plot_bgcolor=bg2,
        font=dict(color=fc, family="Inter, sans-serif"),
        title_font=dict(size=15, color=C["text"], family="Inter, sans-serif"),
        title_x=0.02,
        legend=dict(bgcolor=bg, bordercolor=C["border"], borderwidth=1, font=dict(size=11)),
        margin=dict(t=55, b=45, l=45, r=25),
        hoverlabel=dict(bgcolor=bg, bordercolor=C["border"], font_size=12, font_family="JetBrains Mono"),
        xaxis=dict(gridcolor=C["border"], linecolor=C["border"]),
        yaxis=dict(gridcolor=C["border"], linecolor=C["border"]),
    )

    try:
        if chart_type == "Histogramme":
            fig = px.histogram(df, x=x_col, color=color_col,
                               marginal="box", opacity=0.85,
                               color_discrete_sequence=[C["accent"], C["accent2"]], **kw)

        elif chart_type == "Bar chart":
            if y_col:
                grp = df.groupby(x_col)[y_col].mean().reset_index()
                fig = px.bar(grp, x=x_col, y=y_col, color=color_col,
                             color_discrete_sequence=[C["accent"]], **kw)
            else:
                counts = df[x_col].value_counts().reset_index()
                counts.columns = [x_col, "count"]
                fig = px.bar(counts, x=x_col, y="count",
                             color=x_col, color_discrete_sequence=px.colors.qualitative.Pastel, **kw)

        elif chart_type == "Scatter plot":
            if not y_col:
                st.warning("Scatter plot → sélectionnez une Variable Y.")
                return None
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col,
                             trendline="ols" if not color_col else None,
                             hover_data=df.columns.tolist()[:6],
                             opacity=0.75,
                             color_discrete_sequence=[C["accent"]], **kw)

        elif chart_type == "Box plot":
            if not y_col:
                st.warning("Box plot → sélectionnez une Variable Y (quantitative).")
                return None
            fig = px.box(df, x=x_col, y=y_col, color=color_col,
                         points="outliers",
                         color_discrete_sequence=[C["accent"], C["accent2"]], **kw)

        elif chart_type == "Violin plot":
            if not y_col:
                st.warning("Violin plot → sélectionnez une Variable Y (quantitative).")
                return None
            fig = px.violin(df, x=x_col, y=y_col, color=color_col,
                            box=True, points="outliers",
                            color_discrete_sequence=[C["accent"], C["accent2"]], **kw)

        elif chart_type == "Line chart":
            if not y_col:
                st.warning("Line chart → sélectionnez une Variable Y.")
                return None
            fig = px.line(df.sort_values(x_col), x=x_col, y=y_col, color=color_col,
                          markers=True,
                          color_discrete_sequence=[C["accent"], C["accent2"]], **kw)

        elif chart_type == "Pie chart":
            counts = df[x_col].value_counts().nlargest(12).reset_index()
            counts.columns = [x_col, "count"]
            fig = px.pie(counts, names=x_col, values="count",
                         hole=0.35,
                         color_discrete_sequence=px.colors.sequential.Purples_r, **kw)

        elif chart_type == "Sunburst":
            ql = [c for c in col_types_global["qualitative"] if c in df.columns]
            if len(ql) < 2:
                st.warning("Sunburst → besoin d'au moins 2 colonnes qualitatives.")
                return None
            path_cols = ql[:3]
            fig = px.sunburst(df, path=path_cols,
                              color_discrete_sequence=px.colors.sequential.Purples_r, **kw)

        elif chart_type == "Heatmap (corrélation)":
            num_df = df.select_dtypes(include="number")
            if num_df.shape[1] < 2:
                st.warning("Heatmap → besoin d'au moins 2 colonnes numériques.")
                return None
            corr = num_df.corr().round(2)
            fig = px.imshow(corr, text_auto=True,
                            color_continuous_scale="RdBu_r",
                            title="Matrice de corrélation",
                            template=tmpl)

        elif chart_type == "Funnel":
            counts = df[x_col].value_counts().reset_index()
            counts.columns = [x_col, "count"]
            fig = px.funnel(counts, x="count", y=x_col,
                            color_discrete_sequence=[C["accent"]], **kw)
        else:
            return None

        fig.update_layout(**layout_extra)
        return fig

    except Exception as e:
        st.error(f"Erreur graphique : {e}")
        return None

# ─────────────────────────────────────────────────────────────────
# 8. RÉSUMÉ AUTOMATIQUE DES DONNÉES
# ─────────────────────────────────────────────────────────────────
def auto_summary(df: pd.DataFrame, col_types: dict, C: dict) -> None:
    """Génère des observations automatiques sur le dataset."""
    insights = []
    num_df = df.select_dtypes(include="number")

    # Taux de nulls
    null_pct = (df.isnull().sum().sum() / df.size * 100)
    if null_pct > 10:
        insights.append(f"⚠️ **{null_pct:.1f}%** de valeurs manquantes détectées — nettoyage recommandé.")
    elif null_pct > 0:
        insights.append(f"✅ Faible taux de nulls : **{null_pct:.1f}%**")
    else:
        insights.append("✅ Aucune valeur manquante.")

    # Doublons
    dupes = df.duplicated().sum()
    if dupes > 0:
        insights.append(f"⚠️ **{dupes}** ligne(s) en doublon détectée(s).")

    # Colonnes très corrélées
    if num_df.shape[1] >= 2:
        corr = num_df.corr().abs()
        upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
        strong = [(c, r, upper.loc[r, c]) for c in upper.columns for r in upper.index
                  if pd.notna(upper.loc[r, c]) and upper.loc[r, c] > 0.85]
        for c, r, v in strong[:2]:
            insights.append(f"🔗 Forte corrélation entre **{c}** et **{r}** (r = {v:.2f})")

    # Distribution asymétrique
    for col in num_df.columns[:4]:
        skew = num_df[col].skew()
        if abs(skew) > 1.5:
            direction = "droite (longue queue haute)" if skew > 0 else "gauche (longue queue basse)"
            insights.append(f"📐 **{col}** : distribution asymétrique vers la {direction} (skewness = {skew:.2f})")

    for ins in insights:
        st.markdown(
            f'<div class="stat-card" style="color:{C["text"]};font-size:0.88rem">{ins}</div>',
            unsafe_allow_html=True
        )

# ─────────────────────────────────────────────────────────────────
# 9. BARRE DE NULLS VISUELLE
# ─────────────────────────────────────────────────────────────────
def null_bar(pct: float, C: dict) -> str:
    color = C["danger"] if pct > 20 else (C["warning"] if pct > 5 else C["success"])
    return f"""
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:{C['text_muted']}">
      {pct:.1f}% nuls
      <div class="null-bar-bg">
        <div style="width:{min(pct,100):.1f}%;background:{color};height:6px;border-radius:4px"></div>
      </div>
    </div>"""

# ─────────────────────────────────────────────────────────────────
# 10. MAIN
# ─────────────────────────────────────────────────────────────────
col_types_global = {}   # partagé entre build_chart et main

def main():
    global col_types_global

    # ── Header ────────────────────────────────────────────────────
    h1, h2 = st.columns([6, 1])
    with h1:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px">
          <span style="font-size:1.8rem">📊</span>
          <div>
            <span style="font-family:'Inter',sans-serif;font-size:1.5rem;font-weight:700;color:{C['text']}">
              DataViz Studio
            </span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;
                         color:{C['accent']};margin-left:10px;
                         background:{C['accent']}18;padding:2px 8px;border-radius:10px">
              v2.0
            </span>
          </div>
        </div>
        <p style="color:{C['text_muted']};font-size:0.83rem;margin:0;font-family:'Inter',sans-serif">
          Chargez un dataset · Explorez · Visualisez
        </p>
        """, unsafe_allow_html=True)
    with h2:
        mode_label = "☀️ Light" if st.session_state.dark_mode else "🌙 Dark"
        st.button(mode_label, on_click=toggle_theme, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Sidebar ───────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:16px 0 8px 0">
          <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                       color:{C['accent']};text-transform:uppercase;letter-spacing:0.15em">
            Contrôles
          </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<p class="sidebar-section">📁 Fichier</p>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "CSV ou Excel",
            type=["csv", "xlsx", "xls"],
            label_visibility="collapsed",
            help="Formats supportés : .csv, .xlsx, .xls — jusqu'à 200 MB",
        )

    # ── État vide ─────────────────────────────────────────────────
    if uploaded is None:
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;align-items:center;
                    justify-content:center;padding:80px 20px;text-align:center">
          <div style="font-size:4rem;margin-bottom:16px">📂</div>
          <h3 style="color:{C['text']};margin:0 0 8px 0">Chargez un fichier pour commencer</h3>
          <p style="color:{C['text_muted']};max-width:400px;line-height:1.6;font-size:0.9rem">
            Glissez un fichier <b>CSV</b> ou <b>Excel</b> dans la sidebar.<br>
            L'analyse démarre automatiquement.
          </p>
          <div style="display:flex;gap:12px;margin-top:24px;flex-wrap:wrap;justify-content:center">
            <span class="pill pill-quant">Quantitative</span>
            <span class="pill pill-quali">Qualitative</span>
            <span class="pill pill-temp">Temporelle</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # ── Chargement ────────────────────────────────────────────────
    try:
        df = load_data(uploaded)
    except ValueError as e:
        st.error(str(e))
        st.stop()

    if df.empty:
        st.error("Le fichier est vide ou illisible.")
        st.stop()

    col_types = detect_col_types(df)
    col_types_global = col_types

    # ── Métriques ─────────────────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Lignes",            f"{len(df):,}")
    m2.metric("Colonnes",          len(df.columns))
    m3.metric("Numériques",        len(col_types["quantitative"]))
    m4.metric("Catégorielles",     len(col_types["qualitative"]))
    m5.metric("Valeurs manquantes", f"{df.isnull().sum().sum():,}")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Filtre ────────────────────────────────────────────────────
    df_f = apply_filters(df, col_types)

    # ── Sidebar : Variables & Graphique ──────────────────────────
    with st.sidebar:
        st.markdown('<p class="sidebar-section">📐 Variables</p>', unsafe_allow_html=True)
        all_cols = df_f.columns.tolist()

        x_col = st.selectbox("Axe X", all_cols, index=0)

        y_opts = ["(aucune)"] + [c for c in all_cols if c != x_col]
        y_sel  = st.selectbox("Axe Y  (optionnel)", y_opts, index=0)
        y_col  = None if y_sel == "(aucune)" else y_sel

        color_opts = ["(aucune)"] + [c for c in col_types["qualitative"] if c not in [x_col, y_col]]
        color_sel  = st.selectbox("Couleur par  (optionnel)", color_opts, index=0)
        color_col  = None if color_sel == "(aucune)" else color_sel

        st.markdown('<p class="sidebar-section">📈 Graphique</p>', unsafe_allow_html=True)
        recs = recommend_charts(col_types, x_col, y_col)
        sorted_charts = recs + [c for c in CHART_TYPES if c not in recs]
        chart_type = st.selectbox("Type", sorted_charts)
        if recs:
            pills = " ".join([f'<span class="pill pill-quant">{r}</span>' for r in recs[:3]])
            st.markdown(f'<div style="margin-top:4px">✨ {pills}</div>', unsafe_allow_html=True)

        st.markdown('<p class="sidebar-section">ℹ️ Colonnes types</p>', unsafe_allow_html=True)
        for label, cols, cls in [
            ("Numérique", col_types["quantitative"], "pill-quant"),
            ("Catégorielle", col_types["qualitative"], "pill-quali"),
            ("Temporelle", col_types["temporelle"], "pill-temp"),
        ]:
            if cols:
                pills = " ".join([f'<span class="pill {cls}">{c[:14]}</span>' for c in cols])
                st.markdown(f'<div style="margin-bottom:6px">{pills}</div>', unsafe_allow_html=True)

    # ── Onglets ───────────────────────────────────────────────────
    tab_chart, tab_data, tab_stats, tab_insights = st.tabs([
        "📊  Graphique", "🗃️  Données", "📋  Statistiques", "🔍  Insights"
    ])

    # ── Tab : Graphique ───────────────────────────────────────────
    with tab_chart:
        if len(df_f) == 0:
            st.warning("Aucune donnée après filtrage — ajustez les filtres.")
        else:
            fig = build_chart(df_f, chart_type, x_col, y_col, color_col, C)
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={
                    "displayModeBar": True,
                    "toImageButtonOptions": {"format": "png", "scale": 2},
                    "modeBarButtonsToRemove": ["select2d", "lasso2d"],
                })
                n_f, n_t = len(df_f), len(df)
                suffix = f" sur {n_t:,} (filtrées)" if n_f < n_t else ""
                st.caption(f"Affichage de **{n_f:,}** lignes{suffix}")

    # ── Tab : Données ─────────────────────────────────────────────
    with tab_data:
        col_search, col_dl = st.columns([3, 1])
        with col_search:
            search = st.text_input("🔎 Rechercher dans le tableau", placeholder="Filtrer par valeur…", label_visibility="collapsed")
        with col_dl:
            csv_bytes = df_f.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Télécharger CSV", data=csv_bytes,
                               file_name="export.csv", mime="text/csv",
                               use_container_width=True)

        display_df = df_f[df_f.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)] if search else df_f
        st.dataframe(display_df, use_container_width=True, height=420)
        st.caption(f"{len(display_df):,} lignes × {len(display_df.columns)} colonnes")

    # ── Tab : Statistiques ────────────────────────────────────────
    with tab_stats:
        num_df = df_f.select_dtypes(include="number")
        if not num_df.empty:
            st.markdown(f"#### Statistiques descriptives — {len(num_df.columns)} colonnes numériques")
            desc = num_df.describe().T
            desc["null %"] = (df_f[num_df.columns].isnull().mean() * 100).round(1)
            desc["skewness"] = num_df.skew().round(3)
            st.dataframe(desc.style.format("{:.3f}"), use_container_width=True)
        else:
            st.info("Aucune colonne numérique disponible.")

        st.markdown("---")
        st.markdown("#### Taux de valeurs manquantes par colonne")
        null_data = (df_f.isnull().mean() * 100).reset_index()
        null_data.columns = ["Colonne", "% Nuls"]
        null_data = null_data.sort_values("% Nuls", ascending=False)
        for _, row in null_data.iterrows():
            c1, c2 = st.columns([2, 3])
            c1.markdown(f'<span style="color:{C["text"]};font-family:JetBrains Mono,monospace;font-size:0.82rem">{row["Colonne"]}</span>', unsafe_allow_html=True)
            c2.markdown(null_bar(row["% Nuls"], C), unsafe_allow_html=True)

    # ── Tab : Insights ────────────────────────────────────────────
    with tab_insights:
        st.markdown(f"#### Observations automatiques sur **{uploaded.name}**")
        auto_summary(df_f, col_types, C)

        st.markdown("---")
        st.markdown("#### Aperçu des distributions numériques")
        num_cols = col_types["quantitative"]
        if num_cols:
            cols_per_row = 3
            rows = [num_cols[i:i+cols_per_row] for i in range(0, len(num_cols), cols_per_row)]
            for row_cols in rows:
                grid = st.columns(cols_per_row)
                for i, col_name in enumerate(row_cols):
                    with grid[i]:
                        mini_fig = px.histogram(
                            df_f, x=col_name, template=C["plotly_tmpl"],
                            color_discrete_sequence=[C["accent"]],
                            title=col_name,
                        )
                        mini_fig.update_layout(
                            paper_bgcolor=C["surface"],
                            plot_bgcolor=C["surface2"],
                            height=200, margin=dict(t=35,b=20,l=20,r=10),
                            showlegend=False,
                            font=dict(size=10, color=C["text_muted"]),
                            title_font=dict(size=11, color=C["text"]),
                            xaxis=dict(gridcolor=C["border"]),
                            yaxis=dict(gridcolor=C["border"]),
                        )
                        st.plotly_chart(mini_fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Aucune colonne numérique pour afficher les distributions.")

if __name__ == "__main__":
    main()