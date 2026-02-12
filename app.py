"""
PROTOTYPE - Contrôle des ratios émetteurs OPCVM
CDVM Circulaire n°01-09 - Article 6
 - Gestion des nombres au format marocain
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import openpyxl
from io import BytesIO
import re

# =============================================================================
# CONFIGURATION DE LA PAGE
# =============================================================================
st.set_page_config(
    page_title="Contrôle Émetteurs OPCVM",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# FONCTIONS DE NETTOYAGE DES NOMBRES
# =============================================================================

def clean_number(value):
    """
    Convertit une valeur en nombre décimal.
    Gère les formats marocains : espaces, virgules, etc.
    """
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Supprimer les espaces et remplacer la virgule par le point
        value = value.strip()
        value = value.replace(' ', '')
        value = value.replace(',', '')
        value = value.replace(' ', '')  # Espace insécable
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0

# =============================================================================
# FONCTIONS DE CHARGEMENT
# =============================================================================

@st.cache_data
def load_portfolio(file):
    """
    Charge le fichier Excel et extrait les données de tous les fonds
    Version robuste pour les fichiers marocains
    """
    try:
        xl = pd.ExcelFile(file)
        all_data = []
        actif_net_dict = {}
        
        for sheet_name in xl.sheet_names:
            # Lire la feuille
            df = pd.read_excel(file, sheet_name=sheet_name, header=None)
            
            # Le nom du fonds est en A1
            fonds_name = str(df.iloc[0, 0]) if not pd.isna(df.iloc[0, 0]) else sheet_name
            
            # L'actif net est en C1 (colonne 2, ligne 0)
            actif_net_raw = df.iloc[0, 2] if len(df.columns) > 2 else 0
            actif_net = clean_number(actif_net_raw)
            
            # Lire les données à partir de la ligne 2 (index 1)
            data_start = 1
            df_data = df.iloc[data_start:].copy()
            
            # Renommer les colonnes
            if len(df_data.columns) >= 9:
                df_data.columns = ['Code_ISIN', 'Type', 'Description', 'Quantite', 
                                  'Prix_revient', 'Valo_j', 'Prix_revient_global',
                                  'Valo_globale', 'Plus_moins_value', 'Col10'] + [f'Col{i}' for i in range(11, len(df_data.columns) + 1)]
                
                # Garder seulement les colonnes utiles
                keep_cols = ['Type', 'Description', 'Quantite', 'Prix_revient', 'Valo_globale']
                df_data = df_data[[c for c in keep_cols if c in df_data.columns]]
                
                # Nettoyer les données
                df_data = df_data.dropna(subset=['Valo_globale'], how='all')
                
                if len(df_data) > 0:
                    # Convertir les colonnes en nombres
                    if 'Quantite' in df_data.columns:
                        df_data['Quantite'] = df_data['Quantite'].apply(clean_number)
                    if 'Prix_revient' in df_data.columns:
                        df_data['Prix_revient'] = df_data['Prix_revient'].apply(clean_number)
                    if 'Valo_globale' in df_data.columns:
                        df_data['Valo_globale'] = df_data['Valo_globale'].apply(clean_number)
                    
                    # Ajouter les colonnes Fonds et Actif_Net
                    df_data['Fonds'] = fonds_name
                    df_data['Actif_Net'] = actif_net
                    
                    # Garder seulement les lignes avec valorisation positive
                    df_data = df_data[df_data['Valo_globale'] > 0]
                    
                    all_data.append(df_data)
                    actif_net_dict[fonds_name] = actif_net
        
        if all_data:
            return pd.concat(all_data, ignore_index=True), actif_net_dict
        else:
            st.warning("Aucune donnée valide trouvée dans le fichier")
            return None, None
            
    except Exception as e:
        st.error(f"Erreur lors du chargement : {str(e)}")
        return None, None

@st.cache_data
def create_default_issuer_table():
    """
    Crée une table des émetteurs par défaut
    """
    issuer_data = {
        'mot_cle': [
            'ATW', 'ATTIJARI', 'OBLATW', 'CD ATW',
            'ARADEI', 'OBLARADEI',
            'BCP', 'OBLBCP',
            'IAM', 'ITISSALAT', 'ITIS SALAT',
            'BOA', 'BANK OF AFRICA',
            'CDM',
            'CIH',
            'MUTANDIS',
            'LBV', 'LABEL VIE',
            'COSUMAR', 'CSR',
            'ONCF', 'OBLONCF',
            'CAM', 'OBLCAM',
            'RCI', 'BSFRCI',
            'BDT',
            'CFG',
            'IRGAM',
            'PRS', 'INSTICASH',
            'TWIN'
        ],
        'emetteur': [
            'ATW', 'ATW', 'ATW', 'ATW',
            'ARADEI', 'ARADEI',
            'BCP', 'BCP',
            'IAM', 'IAM', 'IAM',
            'BOA', 'BOA',
            'CDM',
            'CIH',
            'MUTANDIS',
            'LBV', 'LBV',
            'COSUMAR', 'COSUMAR',
            'ONCF', 'ONCF',
            'CAM', 'CAM',
            'RCI', 'RCI',
            'État marocain',
            'CFG',
            'IRGAM',
            'CFG', 'CFG',
            'TWIN'
        ],
        'type_emetteur': [
            'prive', 'prive', 'prive', 'prive',
            'prive', 'prive',
            'prive', 'prive',
            'prive', 'prive', 'prive',
            'prive', 'prive',
            'prive',
            'prive',
            'prive',
            'prive', 'prive',
            'prive', 'prive',
            'prive', 'prive',
            'prive', 'prive',
            'prive', 'prive',
            'public',
            'prive',
            'prive',
            'prive', 'prive',
            'prive'
        ]
    }
    return pd.DataFrame(issuer_data)

# =============================================================================
# FONCTIONS D'IDENTIFICATION
# =============================================================================

def identify_issuer(description, issuer_table):
    """
    Identifie l'émetteur à partir de la description
    """
    description = str(description).upper()
    
    for _, row in issuer_table.iterrows():
        mot_cle = str(row['mot_cle']).upper()
        if mot_cle in description:
            return row['emetteur'], row['type_emetteur']
    
    # Cas spéciaux
    if 'BDT' in description:
        return 'État marocain', 'public'
    elif 'OBL' in description and any(x in description for x in ['ÉTAT', 'ETAT']):
        return 'État marocain', 'public'
    
    return 'À vérifier', 'à vérifier'

def add_issuers(df, issuer_table):
    """
    Ajoute les colonnes émetteur et type_emetteur
    """
    result = df.copy()
    issuers = result['Description'].apply(
        lambda x: identify_issuer(x, issuer_table)
    )
    result['Emetteur'] = [i[0] for i in issuers]
    result['Type_Emetteur'] = [i[1] for i in issuers]
    return result

# =============================================================================
# FONCTIONS DE CALCUL
# =============================================================================

def calculate_issuer_ratios(df, actif_net_dict, params):
    """
    Calcule les ratios par fonds et par émetteur
    """
    results = []
    
    for fonds in df['Fonds'].unique():
        actif_net = actif_net_dict.get(fonds, 0)
        if actif_net == 0:
            continue
            
        fonds_data = df[df['Fonds'] == fonds]
        
        # Grouper par émetteur
        grouped = fonds_data.groupby('Emetteur').agg({
            'Valo_globale': 'sum',
            'Type_Emetteur': 'first'
        }).reset_index()
        
        for _, row in grouped.iterrows():
            total = row['Valo_globale']
            ratio = total / actif_net if actif_net > 0 else 0
            
            # Déterminer le plafond
            if row['Emetteur'] == 'État marocain' or row['Type_Emetteur'] == 'public':
                plafond = params['plafond_etat']
            else:
                # Vérifier si c'est une action éligible au plafond 15%
                fonds_emetteur = fonds_data[fonds_data['Emetteur'] == row['Emetteur']]
                is_action = any('ACTION' in str(t).upper() for t in fonds_emetteur['Type'])
                
                if is_action and row['Emetteur'] in params['actions_eligibles_15pct']:
                    plafond = params['plafond_action_eligible']
                else:
                    plafond = params['plafond_standard']
            
            conformite = '✅' if ratio <= plafond + 0.0001 else '❌'  # Tolérance arrondi
            ecart = (ratio - plafond) * 100
            
            results.append({
                'Fonds': fonds,
                'Emetteur': row['Emetteur'],
                'Type_Emetteur': row['Type_Emetteur'],
                'Total_detenu_MAD': total,
                'Actif_net_MAD': actif_net,
                'Ratio': ratio,
                'Ratio_pct': f"{ratio:.2%}",
                'Plafond': plafond,
                'Plafond_pct': f"{plafond:.0%}",
                'Conformite': conformite,
                'Ecart_pct': ecart,
                'Alerte': ecart > 0.1  # Tolérance 0.1%
            })
    
    return pd.DataFrame(results)

def check_45_percent_rule(ratios_df, portfolio_df, actif_net_dict, seuil=0.45):
    """
    Vérifie la règle des 45% pour les actions
    """
    results = []
    
    for fonds in ratios_df['Fonds'].unique():
        actif_net = actif_net_dict.get(fonds, 0)
        if actif_net == 0:
            continue
            
        fonds_ratios = ratios_df[ratios_df['Fonds'] == fonds].copy()
        
        # Filtrer les actions avec ratio > 10%
        actions_above_10 = fonds_ratios[
            (fonds_ratios['Ratio'] > 0.10) & 
            (fonds_ratios['Emetteur'] != 'État marocain')
        ]
        
        # Vérifier que ce sont bien des actions
        portfolio_fonds = portfolio_df[portfolio_df['Fonds'] == fonds]
        valid_emetteurs = []
        
        for emetteur in actions_above_10['Emetteur']:
            emetteur_data = portfolio_fonds[portfolio_fonds['Emetteur'] == emetteur]
            if any('ACTION' in str(t).upper() for t in emetteur_data['Type']):
                valid_emetteurs.append(emetteur)
        
        actions_above_10 = actions_above_10[actions_above_10['Emetteur'].isin(valid_emetteurs)]
        
        total_above_10 = actions_above_10['Total_detenu_MAD'].sum()
        ratio_45 = total_above_10 / actif_net if actif_net > 0 else 0
        
        emetteurs_list = ', '.join(actions_above_10['Emetteur'].unique()) if len(actions_above_10) > 0 else 'Aucun'
        
        results.append({
            'Fonds': fonds,
            'Actif_net_MAD': actif_net,
            'Total_emetteurs_sup_10pct_MAD': total_above_10,
            'Ratio_cumul': ratio_45,
            'Ratio_cumul_pct': f"{ratio_45:.2%}",
            'Seuil': seuil,
            'Seuil_pct': f"{seuil:.0%}",
            'Conformite': '✅' if ratio_45 <= seuil + 0.0001 else '❌',
            'Emetteurs_concerning': emetteurs_list,
            'Nb_emetteurs': len(actions_above_10)
        })
    
    return pd.DataFrame(results)

# =============================================================================
# FONCTIONS D'EXPORT
# =============================================================================

def to_excel(df_dict):
    """
    Exporte les données vers Excel
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in df_dict.items():
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    output.seek(0)
    return output

# =============================================================================
# CSS PERSONNALISÉ
# =============================================================================

st.markdown("""
<style>
    .stApp {
        background-color: #f5f7fa;
    }
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .alert-success {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
    .alert-warning {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
    }
    .alert-danger {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1rem;
        color: #6c757d;
        border-top: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# EN-TÊTE PRINCIPALE
# =============================================================================

st.markdown("""
<div class="main-header">
    <h1 style="color: white; margin: 0;">📊 Contrôle des ratios émetteurs OPCVM</h1>
    <p style="color: white; opacity: 0.9; margin: 0; font-size: 1.2rem;">
        CDVM - Circulaire n°01-09 | Article 6 - Division des risques
    </p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR - PARAMÈTRES
# =============================================================================

with st.sidebar:
    st.markdown("### ⚙️ Paramètres de contrôle")
    st.markdown("---")
    
    # Plafonds
    st.markdown("#### 📊 Plafonds réglementaires")
    plafond_etat = st.number_input(
        "État marocain (%)",
        min_value=0, max_value=100, value=100, step=5
    ) / 100
    
    plafond_action_eligible = st.number_input(
        "Actions éligibles 15% (%)",
        min_value=0, max_value=100, value=15, step=5
    ) / 100
    
    plafond_standard = st.number_input(
        "Plafond standard (%)",
        min_value=0, max_value=100, value=10, step=5
    ) / 100
    
    st.markdown("---")
    
    # Actions éligibles au plafond 15%
    st.markdown("#### 🎯 Actions éligibles 15%")
    actions_default = "ATW, IAM, BCP, BOA"
    actions_input = st.text_input(
        "Liste des émetteurs (séparés par des virgules)",
        value=actions_default
    )
    actions_eligibles = [a.strip() for a in actions_input.split(',') if a.strip()]
    
    st.markdown("---")
    
    # Seuil règle 45%
    st.markdown("#### 📈 Règle des 45%")
    seuil_45 = st.number_input(
        "Seuil maximum (%)",
        min_value=0, max_value=100, value=45, step=5
    ) / 100
    
    st.markdown("---")
    
    # Table des émetteurs
    st.markdown("#### 📋 Table des émetteurs")
    issuer_file = st.file_uploader(
        "Charger un fichier CSV (optionnel)",
        type=['csv']
    )
    
    if issuer_file:
        issuer_table = pd.read_csv(issuer_file)
        st.success(f"✅ Table chargée : {len(issuer_table)} entrées")
    else:
        issuer_table = create_default_issuer_table()
        st.info("ℹ️ Table par défaut utilisée")
    
    st.markdown("---")
    
    # Bouton de calcul
    calculate = st.button("🚀 LANCER LE CALCUL", type="primary", use_container_width=True)

# =============================================================================
# CHARGEMENT DES DONNÉES
# =============================================================================

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📂 Fichier de données")
    uploaded_file = st.file_uploader(
        "Charger le fichier FOND.xlsx",
        type=['xlsx'],
        key="portfolio_uploader"
    )

if uploaded_file:
    with st.spinner("Chargement du fichier..."):
        portfolio, actif_net_dict = load_portfolio(uploaded_file)
        
        if portfolio is not None and actif_net_dict:
            with col2:
                st.markdown("### 📊 Fonds détectés")
                fonds_list = list(actif_net_dict.keys())
                cols = st.columns(len(fonds_list))
                for i, (fonds, actif) in enumerate(actif_net_dict.items()):
                    with cols[i]:
                        st.metric(
                            label=fonds,
                            value=f"{actif:,.0f} MAD".replace(',', ' '),
                            delta=None
                        )
            
            st.success(f"✅ {len(portfolio)} lignes de portefeuille chargées")
        else:
            st.error("❌ Impossible de charger les données")

# =============================================================================
# CALCUL ET AFFICHAGE
# =============================================================================

if uploaded_file and portfolio is not None and actif_net_dict and calculate:
    
    # Paramètres
    params = {
        'plafond_etat': plafond_etat,
        'plafond_action_eligible': plafond_action_eligible,
        'plafond_standard': plafond_standard,
        'actions_eligibles_15pct': actions_eligibles
    }
    
    with st.spinner("🔍 Analyse des données en cours..."):
        
        # Étape 1 : Identifier les émetteurs
        portfolio_with_issuers = add_issuers(portfolio, issuer_table)
        
        # Étape 2 : Calculer les ratios
        ratios_df = calculate_issuer_ratios(portfolio_with_issuers, actif_net_dict, params)
        
        # Étape 3 : Vérifier la règle des 45%
        rule_45_df = check_45_percent_rule(ratios_df, portfolio_with_issuers, actif_net_dict, seuil_45)
        
        if len(ratios_df) > 0:
            
            # =========================================================================
            # INDICATEURS CLÉS
            # =========================================================================
            
            total_conformes = len(ratios_df[ratios_df['Conformite'] == '✅'])
            total_non_conformes = len(ratios_df[ratios_df['Conformite'] == '❌'])
            taux_conformite = total_conformes / len(ratios_df) * 100 if len(ratios_df) > 0 else 0
            
            st.markdown("---")
            st.markdown("### 📊 Indicateurs clés")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin:0; color:#1e3c72;">📋 Ratios</h4>
                    <p style="font-size: 2rem; font-weight: bold; margin:0;">{len(ratios_df)}</p>
                    <p style="color:#6c757d;">Calculés</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin:0; color:#1e3c72;">✅ Conformes</h4>
                    <p style="font-size: 2rem; font-weight: bold; color:#28a745; margin:0;">{total_conformes}</p>
                    <p style="color:#6c757d;">{taux_conformite:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin:0; color:#1e3c72;">❌ Non-conformes</h4>
                    <p style="font-size: 2rem; font-weight: bold; color:#dc3545; margin:0;">{total_non_conformes}</p>
                    <p style="color:#6c757d;">À traiter</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                nb_etat = len(ratios_df[ratios_df['Emetteur'] == 'État marocain'])
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin:0; color:#1e3c72;">🏛️ État</h4>
                    <p style="font-size: 2rem; font-weight: bold; margin:0;">{nb_etat}</p>
                    <p style="color:#6c757d;">Plafond {plafond_etat:.0%}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                nb_prive = len(ratios_df[ratios_df['Type_Emetteur'] == 'prive'])
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin:0; color:#1e3c72;">🏢 Privé</h4>
                    <p style="font-size: 2rem; font-weight: bold; margin:0;">{nb_prive}</p>
                    <p style="color:#6c757d;">Plafond {plafond_action_eligible:.0%}/{plafond_standard:.0%}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # =========================================================================
            # ONGLETS
            # =========================================================================
            
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Ratios par émetteur",
                "📈 Analyse graphique",
                "⚠️ Alertes",
                "🎯 Règle 45%",
                "📤 Export"
            ])
            
            # -------------------------------------------------------------------------
            # ONGLET 1 : Ratios par émetteur
            # -------------------------------------------------------------------------
            with tab1:
                st.markdown("### 📋 Détail des ratios par fonds et émetteur")
                
                display_cols = ['Fonds', 'Emetteur', 'Total_detenu_MAD', 'Actif_net_MAD', 
                               'Ratio_pct', 'Plafond_pct', 'Conformite']
                
                df_display = ratios_df[display_cols].copy()
                df_display['Total_detenu_MAD'] = df_display['Total_detenu_MAD'].apply(
                    lambda x: f"{x:,.0f}".replace(',', ' ')
                )
                df_display['Actif_net_MAD'] = df_display['Actif_net_MAD'].apply(
                    lambda x: f"{x:,.0f}".replace(',', ' ')
                )
                
                st.dataframe(df_display, use_container_width=True, height=500)
            
            # -------------------------------------------------------------------------
            # ONGLET 2 : Graphiques
            # -------------------------------------------------------------------------
            with tab2:
                st.markdown("### 📈 Visualisations")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Top 10 expositions
                    top_emetteurs = ratios_df.nlargest(10, 'Total_detenu_MAD')
                    fig1 = px.bar(
                        top_emetteurs,
                        x='Total_detenu_MAD',
                        y='Emetteur',
                        color='Fonds',
                        orientation='h',
                        title="Top 10 des expositions par émetteur",
                        labels={'Total_detenu_MAD': 'Montant (MAD)', 'Emetteur': ''}
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # Répartition par fonds
                    fonds_sum = ratios_df.groupby('Fonds')['Total_detenu_MAD'].sum().reset_index()
                    fig2 = px.pie(
                        fonds_sum,
                        values='Total_detenu_MAD',
                        names='Fonds',
                        title="Répartition des actifs par fonds",
                        hole=0.4
                    )
                    st.plotly_chart(fig2, use_container_width=True)
            
            # -------------------------------------------------------------------------
            # ONGLET 3 : Alertes
            # -------------------------------------------------------------------------
            with tab3:
                st.markdown("### ⚠️ Non-conformités détectées")
                
                non_conformes = ratios_df[ratios_df['Conformite'] == '❌']
                
                if len(non_conformes) > 0:
                    st.markdown(f"""
                    <div class="alert-danger">
                        🚨 {len(non_conformes)} non-conformité(s) détectée(s)
                    </div>
                    """, unsafe_allow_html=True)
                    
                    alert_cols = ['Fonds', 'Emetteur', 'Total_detenu_MAD', 'Ratio_pct', 
                                 'Plafond_pct', 'Ecart_pct']
                    
                    df_alert = non_conformes[alert_cols].copy()
                    df_alert['Total_detenu_MAD'] = df_alert['Total_detenu_MAD'].apply(
                        lambda x: f"{x:,.0f}".replace(',', ' ')
                    )
                    df_alert['Ecart_pct'] = df_alert['Ecart_pct'].apply(lambda x: f"{x:.2f}%")
                    
                    st.dataframe(df_alert, use_container_width=True)
                else:
                    st.markdown("""
                    <div class="alert-success">
                        ✅ Aucune non-conformité détectée
                    </div>
                    """, unsafe_allow_html=True)
            
            # -------------------------------------------------------------------------
            # ONGLET 4 : Règle 45%
            # -------------------------------------------------------------------------
            with tab4:
                st.markdown("### 🎯 Règle des 45%")
                st.markdown("""
                **Règle :** La somme des émetteurs (actions) dans lesquels l'OPCVM investit plus de 10% 
                ne peut excéder 45% de l'actif net.
                """)
                
                display_45 = rule_45_df[['Fonds', 'Ratio_cumul_pct', 'Seuil_pct', 
                                        'Conformite', 'Emetteurs_concerning']]
                st.dataframe(display_45, use_container_width=True)
            
            # -------------------------------------------------------------------------
            # ONGLET 5 : Export
            # -------------------------------------------------------------------------
            with tab5:
                st.markdown("### 📤 Export des résultats")
                
                export_dict = {
                    'Ratios_emetteurs': ratios_df,
                    'Regle_45pct': rule_45_df
                }
                
                if len(non_conformes) > 0:
                    export_dict['Alertes'] = non_conformes
                
                excel_data = to_excel(export_dict)
                st.download_button(
                    label="📥 Télécharger le rapport complet (Excel)",
                    data=excel_data,
                    file_name="controle_emetteurs.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            # =========================================================================
            # RAPPORT D'INTERPRÉTATION
            # =========================================================================
            
            st.markdown("---")
            st.markdown("### 📋 Rapport d'interprétation")
            
            interpretation = f"""
            <div style="background: white; padding: 2rem; border-radius: 10px;">
                <h4 style="color: #1e3c72;">📊 Synthèse du contrôle</h4>
                <p><strong>{len(ratios_df)} ratios</strong> analysés sur <strong>{len(actif_net_dict)} fonds</strong></p>
                <p>Taux de conformité global : <strong style="color: {'#28a745' if taux_conformite >= 95 else '#dc3545'}">{taux_conformite:.1f}%</strong></p>
                
                <h4 style="color: #1e3c72; margin-top: 1.5rem;">✅ Points positifs</h4>
                <ul>
                    <li>{total_conformes} ratios conformes aux plafonds</li>
                    <li>{len(rule_45_df[rule_45_df['Conformite'] == '✅'])} fonds respectent la règle des 45%</li>
                </ul>
            """
            
            if total_non_conformes > 0:
                interpretation += f"""
                <h4 style="color: #1e3c72; margin-top: 1.5rem;">⚠️ Points d'attention</h4>
                <ul>
                    <li style="color: #dc3545;"><strong>{total_non_conformes} non-conformité(s)</strong> à traiter</li>
                    <li>Émetteurs concernés : {', '.join(non_conformes['Emetteur'].unique()[:5])}</li>
                </ul>
                """
            
            interpretation += """
                <p style="color: #6c757d; margin-top: 2rem;">
                    Rapport généré automatiquement
                </p>
            </div>
            """
            
            st.markdown(interpretation, unsafe_allow_html=True)
            
        else:
            st.warning("Aucun ratio n'a pu être calculé")

else:
    st.info("👈 Chargez votre fichier FOND.xlsx et cliquez sur 'LANCER LE CALCUL'")

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("""
<div class="footer">
    <p>Développé Par Thierno Ibrahima pour le Contrôle des ratios émetteurs - CDVM Circulaire n°01-09</p>
    <p style="font-size: 0.9rem;"> - Gestion des risques</p>
</div>
""", unsafe_allow_html=True)


