import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# CONFIGURATION DE LA PAGE
# ==========================================
st.set_page_config(
    page_title="Data Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# FONCTIONS UTILITAIRES
# ==========================================

def load_data(uploaded_file):
    """Charge les données depuis un fichier CSV ou Excel."""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            st.error("Format de fichier non supporté. Veuillez charger un CSV ou Excel.")
            return None
        
        # Tentative de conversion automatique des colonnes objets en datetime
        for col in df.select_dtypes(include=['object']).columns:
            try:
                df[col] = pd.to_datetime(df[col])
            except (ValueError, TypeError):
                pass
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {e}")
        return None

def get_column_types(df):
    """Classifie les colonnes en Quantitative, Qualitative et Temporelle."""
    quant_cols = []
    qual_cols = []
    temp_cols = []

    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            temp_cols.append(col)
        elif pd.api.types.is_numeric_dtype(df[col]):
            quant_cols.append(col)
        else:
            qual_cols.append(col)
            
    return quant_cols, qual_cols, temp_cols

def get_col_type(col_name, quant_cols, qual_cols, temp_cols):
    """Retourne le type d'une colonne spécifique."""
    if col_name in temp_cols:
        return 'temporelle'
    elif col_name in quant_cols:
        return 'quantitative'
    else:
        return 'qualitative'

def generate_chart(df, chart_type, x_col, y_col, theme):
    """Génère le graphique Plotly approprié."""
    template = "plotly_dark" if theme == "Dark" else "plotly_white"
    
    # Construction du titre dynamique
    if y_col and y_col != "Aucune":
        title = f"{chart_type} : {y_col} en fonction de {x_col}"
    else:
        title = f"{chart_type} : distribution de {x_col}"

    fig = None

    try:
        if chart_type == "Bar chart":
            # Comptage des valeurs pour les variables qualitatives
            count_df = df[x_col].value_counts().reset_index()
            count_df.columns = [x_col, 'Count']
            fig = px.bar(count_df, x=x_col, y='Count', title=title, template=template)
            
        elif chart_type == "Histogramme":
            fig = px.histogram(df, x=x_col, title=title, template=template)
            
        elif chart_type == "Scatter plot":
            if y_col and y_col != "Aucune":
                fig = px.scatter(df, x=x_col, y=y_col, title=title, template=template)
            else:
                st.warning("Le Scatter plot nécessite une variable Y quantitative.")
                
        elif chart_type == "Boxplot":
            if y_col and y_col != "Aucune":
                fig = px.box(df, x=x_col, y=y_col, title=title, template=template)
            else:
                st.warning("Le Boxplot nécessite une variable Y quantitative.")
                
        elif chart_type == "Line chart":
            y_param = y_col if y_col and y_col != "Aucune" else None
            fig = px.line(df, x=x_col, y=y_param, title=title, template=template)
            
        # Amélioration esthétique globale
        if fig:
            fig.update_layout(
                margin=dict(l=20, r=20, t=50, b=20),
                hovermode="x unified"
            )
            
    except Exception as e:
        st.error(f"Erreur lors de la génération du graphique : {e}")

    return fig

# ==========================================
# INTERFACE UTILISATEUR (UI)
# ==========================================

st.title("📊 Data Explorer Interactif")
st.markdown("Chargez vos données et explorez-les visuellement en quelques clics.")

# --- Sidebar ---
with st.sidebar:
    st.header("1. Chargement des données")
    uploaded_file = st.file_uploader("Importer un fichier CSV ou Excel", type=["csv", "xlsx"])
    
    if uploaded_file:
        df = load_data(uploaded_file)
        
        if df is not None and not df.empty:
            quant_cols, qual_cols, temp_cols = get_column_types(df)
            
            st.header("2. Filtres")
            # Filtre simple sur colonne qualitative
            filter_col = st.selectbox("Filtrer par colonne (qualitative)", ["Aucun filtre"] + qual_cols)
            
            df_filtered = df.copy()
            if filter_col != "Aucun filtre":
                unique_vals = df[filter_col].dropna().unique().tolist()
                selected_vals = st.multiselect(f"Valeurs sélectionnées pour {filter_col}", unique_vals, default=unique_vals)
                
                if selected_vals:
                    df_filtered = df_filtered[df_filtered[filter_col].isin(selected_vals)]
                else:
                    df_filtered = pd.DataFrame(columns=df.columns) # Dataframe vide si rien sélectionné
                    st.warning("Aucune valeur sélectionnée pour le filtre.")

            st.header("3. Configuration du graphique")
            # Thème
            theme = st.radio("Thème du graphique", ["Light", "Dark"], horizontal=True)
            
            # Choix de X
            x_col = st.selectbox("Variable X", df_filtered.columns)
            x_type = get_col_type(x_col, quant_cols, qual_cols, temp_cols)
            st.caption(f"Type détecté : {x_type}")
            
            # Choix de Y (Optionnelle)
            y_options = ["Aucune"] + list(df_filtered.columns)
            y_col = st.selectbox("Variable Y (optionnelle)", y_options)
            if y_col != "Aucune":
                y_type = get_col_type(y_col, quant_cols, qual_cols, temp_cols)
                st.caption(f"Type détecté : {y_type}")
            
            # Logique de suggestion du graphique
            available_charts = []
            if x_type == 'qualitative':
                available_charts.append("Bar chart")
                if y_col != "Aucune" and y_type == 'quantitative':
                    available_charts.append("Boxplot")
            elif x_type == 'quantitative':
                available_charts.append("Histogramme")
                if y_col != "Aucune" and y_type == 'quantitative':
                    available_charts.append("Scatter plot")
            elif x_type == 'temporelle':
                available_charts.append("Line chart")
                if y_col != "Aucune" and y_type == 'quantitative':
                    available_charts.append("Scatter plot")
            
            # Si aucun graphique standard ne matche, on propose l'histogramme par défaut
            if not available_charts:
                available_charts.append("Histogramme")
                
            chart_type = st.selectbox("Type de graphique", available_charts)

# --- Main Content ---
if 'df_filtered' in locals() and not df_filtered.empty:
    # Aperçu des données
    with st.expander("👁️ Aperçu des données (5 premières lignes)"):
        st.dataframe(df_filtered.head(), use_container_width=True)
        
    with st.expander("📈 Statistiques descriptives"):
        st.dataframe(df_filtered.describe(include='all'), use_container_width=True)

    # Génération du graphique
    st.header("Visualisation")
    fig = generate_chart(df_filtered, chart_type, x_col, y_col, theme)
    
    if fig:
        st.plotly_chart(fig, use_container_width=True)
        
elif 'df_filtered' in locals() and df_filtered.empty:
    st.warning("Le filtre appliqué a retiré toutes les données. Veuillez ajuster vos filtres.")
else:
    st.info("👆 Veuillez charger un fichier CSV ou Excel dans la barre latérale pour commencer.")