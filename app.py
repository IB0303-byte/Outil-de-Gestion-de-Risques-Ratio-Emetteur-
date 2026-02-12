"""
PROTOTYPE - Contrôle des ratios émetteurs OPCVM
CDVM Circulaire n°01-09 - Article 6
Auteur : Thierno Ibrahima Diallo 
Date : 12/02/2026
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
# CSS PERSONNALISÉ
# =============================================================================
st.markdown("""
<style>
    /* Style général */
    .stApp {
        background-color: #f5f7fa;
    }
    
    /* En-tête */
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    /* Cartes métriques */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    /* Alertes */
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
    
    /* Boutons */
    .stButton > button {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Tableaux */
    .dataframe {
        font-size: 14px;
        border-collapse: collapse;
        width: 100%;
    }
    
    .dataframe th {
        background-color: #1e3c72;
        color: white;
        padding: 12px;
    }
    
    .dataframe td {
        padding: 8px;
        border-bottom: 1px solid #ddd;
    }
    
    /* Footer */
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
# FONCTIONS DE CHARGEMENT
# =============================================================================

@st.cache_data
def load_portfolio(file):
    """
    Charge le fichier Excel et extrait les données de tous les fonds
    """
    try:
        xl = pd.ExcelFile(file)
        all_data = []
        actif_net_dict = {}
        
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(file, sheet_name=sheet_name, header=1)
            
            # Récupérer le nom du fonds et l'actif net
            fonds_name = df.iloc[0, 0] if not pd.isna(df.iloc[0, 0]) else sheet_name
            actif_net = df.iloc[0, 2] if len(df.columns) > 2 else 0
            
            # Nettoyer le dataframe
            df = df.iloc[1:].copy()
            df = df[df.iloc[:, 8] != 0]  # Valorisation non nulle
            df = df[df.iloc[:, 8] > 0]   # Valorisation positive
            
            if len(df) > 0:
                df['Fonds'] = fonds_name
                df['Actif_Net'] = actif_net
                
                # Garder les colonnes utiles
                cols_to_keep = ['Fonds', 'Actif_Net', df.columns[2], df.columns[3], 
                              df.columns[4], df.columns[6], df.columns[8]]
                df = df[cols_to_keep]
                df.columns = ['Fonds', 'Actif_Net', 'Type', 'Description', 
                            'Quantite', 'Prix_Revient', 'Valorisation']
                
                all_data.append(df)
                actif_net_dict[fonds_name] = actif_net
        
        if all_data:
            return pd.concat(all_data, ignore_index=True), actif_net_dict
        else:
            return None, None
            
    except Exception as e:
        st.error(f"Erreur lors du chargement : {str(e)}")
        return None, None

@st.cache_data
def create_default_issuer_table():
    """
    Crée une table des émetteurs par défaut basée sur les données
    """
    issuer_data = {
        'mot_cle': [
            'ATW', 'ATTIJARI', 'OBLATW', 'CD ATW',
            'ARADEI', 'OBLARADEI',
            'BCP', 'OBLBCP',
            'IAM', 'ITISSALAT',
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
            'IAM', 'IAM',
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
            'prive', 'prive',
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
        fonds_data = df[df['Fonds'] == fonds]
        
        # Grouper par émetteur
        grouped = fonds_data.groupby('Emetteur').agg({
            'Valorisation': 'sum',
            'Type_Emetteur': 'first'
        }).reset_index()
        
        for _, row in grouped.iterrows():
            total = row['Valorisation']
            ratio = total / actif_net if actif_net > 0 else 0
            
            # Déterminer le plafond
            if row['Emetteur'] == 'État marocain':
                plafond = params['plafond_etat']
            elif row['Type_Emetteur'] == 'public':
                plafond = params['plafond_etat']
            else:
                # Vérifier si c'est une action éligible au plafond 15%
                fonds_emetteur = fonds_data[fonds_data['Emetteur'] == row['Emetteur']]
                is_action = any('ACTION' in str(t).upper() for t in fonds_emetteur['Type'])
                
                if is_action and row['Emetteur'] in params['actions_eligibles_15pct']:
                    plafond = params['plafond_action_eligible']
                else:
                    plafond = params['plafond_standard']
            
            conformite = '✅' if ratio <= plafond else '❌'
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
                'Alerte': ecart > 0
            })
    
    return pd.DataFrame(results)

def check_45_percent_rule(ratios_df, portfolio_df, actif_net_dict, seuil=0.45):
    """
    Vérifie la règle des 45% pour les actions
    """
    results = []
    
    for fonds in ratios_df['Fonds'].unique():
        actif_net = actif_net_dict.get(fonds, 0)
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
        
        # Liste des émetteurs concernés
        emetteurs_list = ', '.join(actions_above_10['Emetteur'].unique()) if len(actions_above_10) > 0 else 'Aucun'
        
        results.append({
            'Fonds': fonds,
            'Actif_net_MAD': actif_net,
            'Total_emetteurs_sup_10pct_MAD': total_above_10,
            'Ratio_cumul': ratio_45,
            'Ratio_cumul_pct': f"{ratio_45:.2%}",
            'Seuil': seuil,
            'Seuil_pct': f"{seuil:.0%}",
            'Conformite': '✅' if ratio_45 <= seuil else '❌',
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
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)
    return output

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
    
    # Chargement de la table des émetteurs
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
        with st.expander("Voir la table par défaut"):
            st.dataframe(issuer_table, use_container_width=True)
    
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

with col2:
    if uploaded_file:
        st.markdown("### 📊 Aperçu des données")
        with st.spinner("Chargement du fichier..."):
            portfolio, actif_net_dict = load_portfolio(uploaded_file)
            if portfolio is not None:
                st.success(f"✅ {len(portfolio)} lignes chargées")
                st.success(f"✅ {len(actif_net_dict)} fonds détectés")
                
                # Afficher les fonds
                fonds_list = list(actif_net_dict.keys())
                cols = st.columns(len(fonds_list))
                for i, (fonds, actif) in enumerate(actif_net_dict.items()):
                    with cols[i]:
                        st.metric(fonds, f"{actif:,.0f} MAD")
            else:
                st.error("❌ Erreur lors du chargement")

# =============================================================================
# CALCUL ET AFFICHAGE DES RÉSULTATS
# =============================================================================

if uploaded_file and portfolio is not None and calculate:
    
    # Paramètres
    params = {
        'plafond_etat': plafond_etat,
        'plafond_action_eligible': plafond_action_eligible,
        'plafond_standard': plafond_standard,
        'actions_eligibles_15pct': actions_eligibles,
        'seuil_45': seuil_45
    }
    
    with st.spinner("🔍 Analyse des données en cours..."):
        
        # Étape 1 : Identifier les émetteurs
        portfolio_with_issuers = add_issuers(portfolio, issuer_table)
        
        # Étape 2 : Calculer les ratios
        ratios_df = calculate_issuer_ratios(portfolio_with_issuers, actif_net_dict, params)
        
        # Étape 3 : Vérifier la règle des 45%
        rule_45_df = check_45_percent_rule(ratios_df, portfolio_with_issuers, actif_net_dict, seuil_45)
        
        # Étape 4 : Statistiques globales
        total_conformes = len(ratios_df[ratios_df['Conformite'] == '✅'])
        total_non_conformes = len(ratios_df[ratios_df['Conformite'] == '❌'])
        taux_conformite = total_conformes / len(ratios_df) * 100 if len(ratios_df) > 0 else 0
        
        total_emetteurs = ratios_df['Emetteur'].nunique()
        total_etat = len(ratios_df[ratios_df['Emetteur'] == 'État marocain'])
        total_prive = len(ratios_df[ratios_df['Type_Emetteur'] == 'prive'])
        
        # =========================================================================
        # INDICATEURS CLÉS
        # =========================================================================
        
        st.markdown("---")
        st.markdown("### 📊 Indicateurs clés")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="margin:0; color:#1e3c72;">📋 Ratios</h3>
                <p style="font-size: 2rem; font-weight: bold; margin:0;">{}</p>
                <p style="color:#6c757d;">Calculés</p>
            </div>
            """.format(len(ratios_df)), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3 style="margin:0; color:#1e3c72;">✅ Conformes</h3>
                <p style="font-size: 2rem; font-weight: bold; color:#28a745; margin:0;">{}</p>
                <p style="color:#6c757d;">{:.1f}%</p>
            </div>
            """.format(total_conformes, taux_conformite), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3 style="margin:0; color:#1e3c72;">❌ Non-conformes</h3>
                <p style="font-size: 2rem; font-weight: bold; color:#dc3545; margin:0;">{}</p>
                <p style="color:#6c757d;">À traiter</p>
            </div>
            """.format(total_non_conformes), unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3 style="margin:0; color:#1e3c72;">🏛️ État</h3>
                <p style="font-size: 2rem; font-weight: bold; margin:0;">{}</p>
                <p style="color:#6c757d;">Plafond {:.0f}%</p>
            </div>
            """.format(total_etat, plafond_etat*100), unsafe_allow_html=True)
        
        with col5:
            st.markdown("""
            <div class="metric-card">
                <h3 style="margin:0; color:#1e3c72;">🏢 Privé</h3>
                <p style="font-size: 2rem; font-weight: bold; margin:0;">{}</p>
                <p style="color:#6c757d;">Plafond {:.0f}%/{:.0f}%</p>
            </div>
            """.format(total_prive, plafond_action_eligible*100, plafond_standard*100), unsafe_allow_html=True)
        
        # =========================================================================
        # ONGLETS DE RÉSULTATS
        # =========================================================================
        
        st.markdown("---")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Ratios par émetteur",
            "📈 Analyse graphique",
            "⚠️ Alertes et non-conformités",
            "🎯 Règle des 45%",
            "📤 Export des résultats"
        ])
        
        # -------------------------------------------------------------------------
        # ONGLET 1 : Ratios par émetteur
        # -------------------------------------------------------------------------
        with tab1:
            st.markdown("### 📋 Détail des ratios par fonds et par émetteur")
            
            # Filtres
            col1, col2 = st.columns(2)
            with col1:
                fonds_filter = st.multiselect(
                    "Filtrer par fonds",
                    options=ratios_df['Fonds'].unique(),
                    default=ratios_df['Fonds'].unique()
                )
            with col2:
                conformite_filter = st.multiselect(
                    "Filtrer par conformité",
                    options=['✅', '❌'],
                    default=['✅', '❌']
                )
            
            filtered_df = ratios_df[
                (ratios_df['Fonds'].isin(fonds_filter)) &
                (ratios_df['Conformite'].isin(conformite_filter))
            ]
            
            # Afficher le tableau
            display_cols = ['Fonds', 'Emetteur', 'Total_detenu_MAD', 'Actif_net_MAD', 
                           'Ratio_pct', 'Plafond_pct', 'Conformite', 'Ecart_pct']
            
            styled_df = filtered_df[display_cols].style.format({
                'Total_detenu_MAD': '{:,.0f} MAD',
                'Actif_net_MAD': '{:,.0f} MAD',
                'Ecart_pct': '{:.2f}%'
            }).applymap(
                lambda x: 'color: red; font-weight: bold' if x == '❌' else 'color: green',
                subset=['Conformite']
            ).applymap(
                lambda x: 'background-color: #ffebee' if isinstance(x, float) and x > 0 else '',
                subset=['Ecart_pct']
            )
            
            st.dataframe(styled_df, use_container_width=True, height=500)
            
            # Statistiques du filtre
            st.markdown(f"""
            <div class="alert-success">
                📊 Affichage de {len(filtered_df)} ratios sur {len(ratios_df)} | 
                ✅ {len(filtered_df[filtered_df['Conformite'] == '✅'])} conformes | 
                ❌ {len(filtered_df[filtered_df['Conformite'] == '❌'])} non-conformes
            </div>
            """, unsafe_allow_html=True)
        
        # -------------------------------------------------------------------------
        # ONGLET 2 : Analyse graphique
        # -------------------------------------------------------------------------
        with tab2:
            st.markdown("### 📈 Visualisations interactives")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Graphique 1 : Top 10 des expositions
                st.markdown("#### 🥇 Top 10 des expositions par émetteur")
                
                top_emetteurs = ratios_df.nlargest(10, 'Total_detenu_MAD')
                
                fig1 = px.bar(
                    top_emetteurs,
                    x='Total_detenu_MAD',
                    y='Emetteur',
                    color='Fonds',
                    orientation='h',
                    title="Montants détenus par émetteur",
                    labels={'Total_detenu_MAD': 'Montant (MAD)', 'Emetteur': ''},
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    text='Ratio_pct'
                )
                
                fig1.update_layout(
                    height=500,
                    showlegend=True,
                    hoverlabel=dict(bgcolor="white", font_size=12)
                )
                
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Graphique 2 : Répartition par fonds
                st.markdown("#### 🥧 Répartition des actifs par fonds")
                
                fonds_sum = ratios_df.groupby('Fonds')['Total_detenu_MAD'].sum().reset_index()
                
                fig2 = px.pie(
                    fonds_sum,
                    values='Total_detenu_MAD',
                    names='Fonds',
                    title="Distribution des actifs par fonds",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                
                fig2.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>Montant: %{value:,.0f} MAD<br>Proportion: %{percent}'
                )
                
                fig2.update_layout(height=500)
                
                st.plotly_chart(fig2, use_container_width=True)
            
            # Graphique 3 : Ratios vs Plafonds
            st.markdown("#### 📊 Ratios vs Plafonds réglementaires")
            
            # Préparer les données pour le graphique
            plot_data = ratios_df.copy()
            plot_data['Ratio_num'] = plot_data['Ratio'] * 100
            plot_data['Plafond_num'] = plot_data['Plafond'] * 100
            
            fig3 = px.scatter(
                plot_data,
                x='Fonds',
                y='Ratio_num',
                color='Emetteur',
                size='Total_detenu_MAD',
                hover_data=['Ratio_pct', 'Plafond_pct', 'Conformite'],
                title="Ratios par fonds et émetteur",
                labels={'Ratio_num': 'Ratio (%)', 'Fonds': ''},
                size_max=50
            )
            
            # Ajouter une ligne horizontale pour chaque plafond
            for fonds in plot_data['Fonds'].unique():
                fonds_plafonds = plot_data[plot_data['Fonds'] == fonds]
                max_plafond = fonds_plafonds['Plafond_num'].max()
                
                fig3.add_hline(
                    y=max_plafond,
                    line_dash="dash",
                    line_color="red",
                    opacity=0.3,
                    annotation_text=f"Plafond max {fonds}",
                    annotation_position="top right"
                )
            
            fig3.update_layout(height=600, showlegend=True)
            st.plotly_chart(fig3, use_container_width=True)
            
            # Graphique 4 : Évolution des écarts
            st.markdown("#### 📉 Analyse des écarts (non-conformités)")
            
            non_conformes = ratios_df[ratios_df['Conformite'] == '❌']
            
            if len(non_conformes) > 0:
                fig4 = px.bar(
                    non_conformes,
                    x='Emetteur',
                    y='Ecart_pct',
                    color='Fonds',
                    title="Écarts par rapport au plafond (%)",
                    labels={'Ecart_pct': 'Écart (%)', 'Emetteur': ''},
                    barmode='group',
                    text='Ecart_pct'
                )
                
                fig4.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig4.update_layout(height=500)
                
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.markdown("""
                <div class="alert-success">
                    🎉 Aucune non-conformité détectée ! Tous les ratios respectent les plafonds.
                </div>
                """, unsafe_allow_html=True)
        
        # -------------------------------------------------------------------------
        # ONGLET 3 : Alertes et non-conformités
        # -------------------------------------------------------------------------
        with tab3:
            st.markdown("### ⚠️ Détection des non-conformités")
            
            non_conformes = ratios_df[ratios_df['Conformite'] == '❌']
            
            if len(non_conformes) > 0:
                st.markdown(f"""
                <div class="alert-danger">
                    🚨 {len(non_conformes)} non-conformité(s) détectée(s) - Action requise
                </div>
                """, unsafe_allow_html=True)
                
                # Tableau des non-conformités
                alert_cols = ['Fonds', 'Emetteur', 'Total_detenu_MAD', 'Ratio_pct', 
                             'Plafond_pct', 'Ecart_pct']
                
                st.dataframe(
                    non_conformes[alert_cols].style.format({
                        'Total_detenu_MAD': '{:,.0f} MAD',
                        'Ecart_pct': '{:.2f}%'
                    }).applymap(
                        lambda x: 'background-color: #ffebee',
                        subset=['Ecart_pct']
                    ),
                    use_container_width=True
                )
                
                # Recommandations
                st.markdown("#### 📋 Recommandations")
                
                for _, row in non_conformes.iterrows():
                    with st.expander(f"🔴 {row['Fonds']} - {row['Emetteur']} : {row['Ratio_pct']} > {row['Plafond_pct']}"):
                        montant_excedent = row['Total_detenu_MAD'] - (row['Plafond'] * row['Actif_net_MAD'])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric(
                                "Montant à réduire",
                                f"{montant_excedent:,.0f} MAD",
                                delta=f"{row['Ecart_pct']:.1f}%",
                                delta_color="inverse"
                            )
                        with col2:
                            st.metric(
                                "Ratio actuel",
                                row['Ratio_pct'],
                                delta=f"+{row['Ecart_pct']:.1f}%",
                                delta_color="inverse"
                            )
                        
                        st.markdown(f"""
                        **Action recommandée :**
                        - Réduire l'exposition à **{row['Emetteur']}** de **{montant_excedent:,.0f} MAD**
                        - Vérifier les lignes suivantes dans le portefeuille :
                        """)
                        
                        # Afficher les lignes concernées
                        concerned_lines = portfolio_with_issuers[
                            (portfolio_with_issuers['Fonds'] == row['Fonds']) &
                            (portfolio_with_issuers['Emetteur'] == row['Emetteur'])
                        ][['Type', 'Description', 'Quantite', 'Valorisation']]
                        
                        st.dataframe(
                            concerned_lines.style.format({
                                'Quantite': '{:,.0f}',
                                'Valorisation': '{:,.0f} MAD'
                            }),
                            use_container_width=True
                        )
            else:
                st.markdown("""
                <div class="alert-success">
                    ✅ Aucune non-conformité détectée. Tous les ratios respectent les plafonds réglementaires.
                </div>
                """, unsafe_allow_html=True)
                
                # Distribution des ratios
                st.markdown("#### 📊 Distribution des ratios")
                
                fig5 = px.histogram(
                    ratios_df,
                    x='Ratio',
                    nbins=20,
                    title="Distribution des ratios d'exposition",
                    labels={'Ratio': 'Ratio', 'count': 'Nombre de ratios'},
                    color_discrete_sequence=['#1e3c72']
                )
                
                # Ajouter les lignes de plafond
                fig5.add_vline(x=plafond_etat, line_dash="dash", line_color="green",
                              annotation_text=f"État {plafond_etat:.0%}")
                fig5.add_vline(x=plafond_action_eligible, line_dash="dash", line_color="orange",
                              annotation_text=f"Actions 15% {plafond_action_eligible:.0%}")
                fig5.add_vline(x=plafond_standard, line_dash="dash", line_color="red",
                              annotation_text=f"Standard {plafond_standard:.0%}")
                
                fig5.update_layout(height=500)
                st.plotly_chart(fig5, use_container_width=True)
        
        # -------------------------------------------------------------------------
        # ONGLET 4 : Règle des 45%
        # -------------------------------------------------------------------------
        with tab4:
            st.markdown("### 🎯 Contrôle spécifique - Règle des 45%")
            st.markdown("""
            <div class="alert-info">
                📋 Règle : La somme des émetteurs (actions) dans lesquels l'OPCVM investit plus de 10% 
                ne peut excéder 45% de l'actif net.
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Résultats par fonds")
                
                display_45 = rule_45_df[['Fonds', 'Ratio_cumul_pct', 'Seuil_pct', 
                                        'Conformite', 'Emetteurs_concerning', 'Nb_emetteurs']]
                
                styled_45 = display_45.style.applymap(
                    lambda x: 'color: red; font-weight: bold' if x == '❌' else 'color: green',
                    subset=['Conformite']
                )
                
                st.dataframe(styled_45, use_container_width=True)
            
            with col2:
                st.markdown("#### 📈 Visualisation")
                
                fig6 = px.bar(
                    rule_45_df,
                    x='Fonds',
                    y='Ratio_cumul',
                    color='Conformite',
                    title="Règle des 45% - Ratio cumulé",
                    labels={'Ratio_cumul': 'Ratio cumulé', 'Fonds': ''},
                    color_discrete_map={'✅': '#28a745', '❌': '#dc3545'},
                    text='Ratio_cumul_pct'
                )
                
                fig6.add_hline(
                    y=seuil_45,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Seuil {seuil_45:.0%}",
                    annotation_position="top right"
                )
                
                fig6.update_traces(textposition='outside')
                fig6.update_layout(height=400)
                
                st.plotly_chart(fig6, use_container_width=True)
            
            # Détail par fonds
            st.markdown("#### 🔍 Détail des émetteurs > 10%")
            
            for fonds in rule_45_df['Fonds'].unique():
                with st.expander(f"📁 {fonds}"):
                    # Trouver les émetteurs actions > 10%
                    fonds_ratios = ratios_df[
                        (ratios_df['Fonds'] == fonds) &
                        (ratios_df['Ratio'] > 0.10) &
                        (ratios_df['Emetteur'] != 'État marocain')
                    ]
                    
                    # Vérifier que ce sont des actions
                    fonds_portfolio = portfolio_with_issuers[
                        portfolio_with_issuers['Fonds'] == fonds
                    ]
                    
                    actions_above_10 = []
                    for _, row in fonds_ratios.iterrows():
                        emetteur_data = fonds_portfolio[fonds_portfolio['Emetteur'] == row['Emetteur']]
                        if any('ACTION' in str(t).upper() for t in emetteur_data['Type']):
                            actions_above_10.append(row)
                    
                    if actions_above_10:
                        df_detail = pd.DataFrame(actions_above_10)
                        st.dataframe(
                            df_detail[['Emetteur', 'Total_detenu_MAD', 'Ratio_pct', 'Plafond_pct']],
                            use_container_width=True
                        )
                    else:
                        st.info("ℹ️ Aucun émetteur action avec exposition > 10%")
        
        # -------------------------------------------------------------------------
        # ONGLET 5 : Export
        # -------------------------------------------------------------------------
        with tab5:
            st.markdown("### 📤 Export des résultats")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📁 Format d'export")
                export_format = st.radio(
                    "Choisir le format",
                    options=["Excel (.xlsx)", "CSV"],
                    horizontal=True
                )
            
            with col2:
                st.markdown("#### 📋 Données à exporter")
                export_ratios = st.checkbox("Ratios par émetteur", value=True)
                export_alertes = st.checkbox("Alertes non-conformités", value=True)
                export_rule45 = st.checkbox("Règle des 45%", value=True)
                export_synthese = st.checkbox("Synthèse par fonds", value=True)
            
            if st.button("📥 GÉNÉRER L'EXPORT", use_container_width=True):
                
                export_dict = {}
                
                if export_ratios:
                    export_dict['Ratios_emetteurs'] = ratios_df
                
                if export_alertes and len(non_conformes) > 0:
                    export_dict['Alertes'] = non_conformes
                
                if export_rule45:
                    export_dict['Regle_45pct'] = rule_45_df
                
                if export_synthese:
                    synthese = ratios_df.groupby('Fonds').agg({
                        'Total_detenu_MAD': 'sum',
                        'Actif_net_MAD': 'first',
                        'Conformite': lambda x: (x == '✅').sum(),
                        'Emetteur': 'count'
                    }).reset_index()
                    synthese.columns = ['Fonds', 'Total_portefeuille', 'Actif_net', 
                                       'Ratios_conformes', 'Total_emetteurs']
                    synthese['Taux_conformite'] = synthese['Ratios_conformes'] / synthese['Total_emetteurs']
                    export_dict['Synthese'] = synthese
                
                if export_format == "Excel (.xlsx)":
                    excel_data = to_excel(export_dict)
                    st.download_button(
                        label="⬇️ Télécharger Excel",
                        data=excel_data,
                        file_name="controle_emetteurs.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                else:
                    for sheet_name, df in export_dict.items():
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label=f"⬇️ Télécharger {sheet_name}.csv",
                            data=csv,
                            file_name=f"{sheet_name}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
            
            # Aperçu de l'export
            with st.expander("👁️ Aperçu des données exportées"):
                st.markdown("**Ratios par émetteur**")
                st.dataframe(ratios_df.head(10), use_container_width=True)
        
        # =========================================================================
        # INTERPRÉTATION AUTOMATIQUE
        # =========================================================================
        
        st.markdown("---")
        st.markdown("### 📋 Rapport d'interprétation")
        
        interpretation = f"""
        <div style="background-color: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h4 style="color: #1e3c72;">📊 Analyse globale</h4>
            <p style="font-size: 1.1rem;">
                L'analyse porte sur <strong>{len(ratios_df)} ratios</strong> répartis sur <strong>{len(actif_net_dict)} fonds</strong> 
                et <strong>{ratios_df['Emetteur'].nunique()} émetteurs distincts</strong>.
            </p>
            
            <h4 style="color: #1e3c72; margin-top: 1.5rem;">✅ Conformité</h4>
            <p style="font-size: 1.1rem;">
                Taux de conformité global : <strong>{taux_conformite:.1f}%</strong><br>
                - {total_conformes} ratios conformes aux plafonds<br>
                - {total_non_conformes} ratios non conformes nécessitant une action
            </p>
        """
        
        if total_non_conformes > 0:
            interpretation += f"""
            <h4 style="color: #1e3c72; margin-top: 1.5rem;">⚠️ Points d'attention</h4>
            <p style="font-size: 1.1rem;">
                <strong style="color: #dc3545;">{total_non_conformes} non-conformité(s)</strong> à traiter en priorité :<br>
                {', '.join(non_conformes['Emetteur'].unique()[:5])}
                {'...' if len(non_conformes['Emetteur'].unique()) > 5 else ''}
            </p>
            """
        
        interpretation += f"""
            <h4 style="color: #1e3c72; margin-top: 1.5rem;">🏛️ Exposition État</h4>
            <p style="font-size: 1.1rem;">
                {total_etat} ratios concernant l'État marocain<br>
                Plafond appliqué : {plafond_etat:.0%}<br>
                Fonds le plus exposé : {ratios_df[ratios_df['Emetteur'] == 'État marocain'].sort_values('Ratio', ascending=False).iloc[0]['Fonds'] if len(ratios_df[ratios_df['Emetteur'] == 'État marocain']) > 0 else 'N/A'}
            </p>
            
            <h4 style="color: #1e3c72; margin-top: 1.5rem;">🎯 Règle des 45%</h4>
            <p style="font-size: 1.1rem;">
                {len(rule_45_df[rule_45_df['Conformite'] == '✅'])} fonds conformes<br>
                {len(rule_45_df[rule_45_df['Conformite'] == '❌'])} fonds non conformes
            </p>
            
            <h4 style="color: #1e3c72; margin-top: 1.5rem;">💡 Recommandations</h4>
            <ul style="font-size: 1.1rem;">
        """
        
        if total_non_conformes > 0:
            interpretation += "<li>Réduire les expositions des émetteurs en dépassement</li>"
        else:
            interpretation += "<li>Maintenir les expositions actuelles dans les limites réglementaires</li>"
        
        if len(rule_45_df[rule_45_df['Conformite'] == '❌']) > 0:
            interpretation += "<li>Revoir la diversification des actions pour respecter la règle des 45%</li>"
        
        interpretation += """
                <li>Vérifier régulièrement la table des émetteurs</li>
                <li>Surveiller les émetteurs approchant les plafonds (>90%)</li>
            </ul>
            
            <p style="color: #6c757d; margin-top: 2rem; font-style: italic;">
                Rapport généré automatiquement le {date}
            </p>
        </div>
        """.format(date=pd.Timestamp.now().strftime("%d/%m/%Y à %H:%M"))
        
        st.markdown(interpretation, unsafe_allow_html=True)

else:
    # Message d'accueil si aucun fichier n'est chargé
    st.markdown("""
    <div style="background: white; padding: 3rem; border-radius: 10px; text-align: center; margin-top: 2rem;">
        <h2 style="color: #1e3c72;">🚀 Bienvenue dans l'outil de contrôle des ratios émetteurs</h2>
        <p style="font-size: 1.2rem; color: #6c757d; margin: 2rem 0;">
            Pour commencer, chargez votre fichier FOND.xlsx dans le panneau de gauche.
        </p>
        <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 2rem;">
            <div style="text-align: center;">
                <h3 style="color: #1e3c72;">📊 5 fonds</h3>
                <p>CFP, CCS, TIJ, CLB, PRV</p>
            </div>
            <div style="text-align: center;">
                <h3 style="color: #1e3c72;">⚙️ Paramétrable</h3>
                <p>Plafonds, seuils, émetteurs</p>
            </div>
            <div style="text-align: center;">
                <h3 style="color: #1e3c72;">📈 Interactif</h3>
                <p>Graphiques, alertes, export</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("""
<div class="footer">
    <p>Développé Par Thierno Ibrahima pour le contrôle des ratios émetteurs - CDVM Circulaire n°01-09</p>
    <p style="font-size: 0.9rem;">Prototype fonctionnel - Version 1.0</p>
</div>
""", unsafe_allow_html=True)


