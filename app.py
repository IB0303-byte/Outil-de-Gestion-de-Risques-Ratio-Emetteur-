"""
PROTOTYPE - Contrôle des ratios émetteurs OPCVM
CDVM Circulaire n°01-09 - Article 6
Version avec Interface Améliorée
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import re
from datetime import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Contrôle Émetteurs OPCVM",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CSS AMÉLIORÉ
# =============================================================================

st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Reset et Police globale */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Container principal blanc */
    .main-container {
        background: white;
        border-radius: 20px;
        padding: 3rem;
        margin: 2rem auto;
        max-width: 1400px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    
    /* En-tête élégant */
    .elegant-header {
        text-align: center;
        margin-bottom: 3rem;
        padding-bottom: 2rem;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .elegant-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .elegant-header .subtitle {
        font-size: 0.95rem;
        color: #666;
        font-weight: 400;
        margin-top: 1rem;
    }
    
    /* Cartes métriques modernes */
    .modern-metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .modern-metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
    }
    
    .modern-metric-card h4 {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0 0 1rem 0;
        opacity: 0.9;
    }
    
    .modern-metric-card .value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        line-height: 1;
    }
    
    .modern-metric-card .subvalue {
        font-size: 0.9rem;
        opacity: 0.8;
        margin-top: 0.5rem;
    }
    
    /* Carte verte pour conformes */
    .metric-success {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    /* Carte rouge pour non-conformes */
    .metric-danger {
        background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
    }
    
    /* Carte bleu clair */
    .metric-info {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    /* Sections */
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }
    
    /* Tableaux */
    .dataframe {
        border: none !important;
        border-radius: 10px;
        overflow: hidden;
    }
    
    .dataframe thead tr th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        padding: 1rem !important;
    }
    
    .dataframe tbody tr:hover {
        background-color: #f8f9ff !important;
    }
    
    /* Boutons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Onglets */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        font-weight: 600;
        color: #666;
        border-radius: 10px 10px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .css-1d391kg .stMarkdown, [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 10px;
        border-left: 4px solid;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f8f9ff;
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Upload box */
    .stFileUploader {
        background: #f8f9ff;
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
    }
    
    /* Metrics fonds */
    .fund-metric {
        background: white;
        border: 2px solid #667eea;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .fund-metric:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }
    
    .fund-metric .fund-name {
        font-weight: 700;
        font-size: 1.1rem;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .fund-metric .fund-value {
        font-size: 0.9rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# FONCTION DE NETTOYAGE ULTRA ROBUSTE
# =============================================================================

def clean_number(value):
    """Convertit ANY valeur en nombre flottant de façon sécurisée"""
    if value is None:
        return 0.0
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Nettoyage agressif
        value = value.strip()
        value = value.replace(' ', '')
        value = value.replace(',', '')
        value = value.replace(' ', '')  # Espace insécable
        value = value.replace('\xa0', '')  # Espace insécable HTML
        value = value.replace('\t', '')
        value = value.replace('\n', '')
        if value == '' or value == '-' or value == 'nan':
            return 0.0
        try:
            return float(value)
        except ValueError:
            # Essayer de garder seulement les chiffres et le point
            value = re.sub(r'[^\d.-]', '', value)
            try:
                return float(value) if value else 0.0
            except:
                return 0.0
    return 0.0

# =============================================================================
# FONCTION DE CHARGEMENT DEBUG
# =============================================================================

@st.cache_data
def load_portfolio(file):
    """
    Charge le fichier Excel avec correction des noms de fonds
    """
    try:
        xl = pd.ExcelFile(file)
        all_data = []
        actif_net_dict = {}
        
        # Mapping des noms de fonds par feuille
        fonds_mapping = {
            'Action': 'CFP',
            'Diversifie': 'TIJ',
            'OMLT': 'PRV',
            'OCT': 'CLB',
            'Monetaire': 'CCS'
        }
        
        # Actif net par fonds (à vérifier dans ton fichier)
        actif_net_values = {
            'CFP': 276403573.05,
            'CCS': 356674412.16,
            'TIJ': 478502756.69,
            'CLB': 1704711189.03,
            'PRV': 708721589.76
        }
        
        for sheet_name in xl.sheet_names:
            # Lire la feuille
            df = pd.read_excel(file, sheet_name=sheet_name, header=None)
            
            # Déterminer le nom du fonds à partir du nom de la feuille
            fonds_name = fonds_mapping.get(sheet_name, sheet_name)
            actif_net = actif_net_values.get(fonds_name, 0)
            
            # Lire les données à partir de la ligne 2
            df_data = df.iloc[1:].copy()
            df_data = df_data.dropna(how='all')
            
            if len(df_data) > 0 and len(df_data.columns) >= 9:
                # Nommer les colonnes
                df_data.columns = ['Code_ISIN', 'Type', 'Description', 'Quantite', 
                                  'Prix_revient', 'Valo_j', 'Prix_revient_global',
                                  'Valo_globale', 'Plus_moins_value'] + [f'Col{i}' for i in range(10, len(df_data.columns)+1)]
                
                # Garder les colonnes utiles
                if 'Valo_globale' in df_data.columns:
                    df_clean = df_data[['Type', 'Description', 'Valo_globale']].copy()
                    
                    # Nettoyer la valorisation
                    df_clean['Valo_globale'] = df_clean['Valo_globale'].apply(clean_number)
                    df_clean = df_clean[df_clean['Valo_globale'] > 0]
                    
                    if len(df_clean) > 0:
                        df_clean['Fonds'] = fonds_name
                        df_clean['Actif_Net'] = actif_net
                        all_data.append(df_clean)
                        actif_net_dict[fonds_name] = actif_net
        
        if all_data:
            return pd.concat(all_data, ignore_index=True), actif_net_dict
        else:
            return None, None
            
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return None, None

# =============================================================================
# TABLE DES ÉMETTEURS PAR DÉFAUT
# =============================================================================

@st.cache_data
def create_default_issuer_table():
    """Table de correspondance émetteurs"""
    
    data = {
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
            'CFG',
            'IRGAM',
            'CFG', 'CFG',
            'TWIN'
        ],
        'type': [
            'privé', 'privé', 'privé', 'privé',
            'privé', 'privé',
            'privé', 'privé',
            'privé', 'privé',
            'privé', 'privé',
            'privé',
            'privé',
            'privé',
            'privé', 'privé',
            'privé', 'privé',
            'privé', 'privé',
            'privé', 'privé',
            'privé', 'privé',
            'public',
            'privé',
            'privé',
            'privé', 'privé',
            'privé'
        ]
    }
    return pd.DataFrame(data)

# =============================================================================
# IDENTIFICATION DES ÉMETTEURS
# =============================================================================

def identify_issuer(description, issuer_table):
    """Identifie l'émetteur à partir de la description"""
    
    if pd.isna(description):
        return 'Inconnu', 'inconnu'
    
    desc = str(description).upper()
    
    # Cas spécial BDT
    if 'BDT' in desc:
        return 'État marocain', 'public'
    
    # Recherche dans la table
    for _, row in issuer_table.iterrows():
        mot_cle = str(row['mot_cle']).upper()
        if mot_cle in desc:
            return row['emetteur'], row['type']
    
    return 'Autre', 'privé'

def add_issuers(df, issuer_table):
    """Ajoute les colonnes émetteur et type"""
    
    if df is None or len(df) == 0:
        return df
    
    result = df.copy()
    
    # Appliquer l'identification
    issuers = result['Description'].apply(
        lambda x: identify_issuer(x, issuer_table)
    )
    
    result['Emetteur'] = [i[0] for i in issuers]
    result['Type_Emetteur'] = [i[1] for i in issuers]
    
    return result

# =============================================================================
# CALCUL DES RATIOS (VERSION ROBUSTE)
# =============================================================================

def calculate_issuer_ratios(df, actif_net_dict, params):
    """Calcule les ratios par fonds et émetteur"""
    
    if df is None or len(df) == 0 or not actif_net_dict:
        return pd.DataFrame()
    
    results = []
    
    for fonds in df['Fonds'].unique():
        actif_net = actif_net_dict.get(fonds, 0)
        
        if actif_net <= 0:
            continue
        
        fonds_data = df[df['Fonds'] == fonds]
        
        # Grouper par émetteur
        grouped = fonds_data.groupby('Emetteur').agg({
            'Valo_globale': 'sum',
            'Type_Emetteur': 'first'
        }).reset_index()
        
        for _, row in grouped.iterrows():
            total = row['Valo_globale']
            ratio = total / actif_net
            
            # Déterminer le plafond
            if row['Emetteur'] == 'État marocain' or row['Type_Emetteur'] == 'public':
                plafond = params.get('plafond_etat', 1.0)
            else:
                # Vérifier si c'est une action
                emetteur_data = fonds_data[fonds_data['Emetteur'] == row['Emetteur']]
                is_action = any('ACTION' in str(t).upper() for t in emetteur_data['Type'])
                
                if is_action and row['Emetteur'] in params.get('actions_eligibles_15pct', []):
                    plafond = params.get('plafond_action_eligible', 0.15)
                else:
                    plafond = params.get('plafond_standard', 0.10)
            
            # Conformité (avec tolérance)
            conformite = '✅' if ratio <= plafond + 0.0001 else '❌'
            ecart = (ratio - plafond) * 100
            
            results.append({
                'Fonds': fonds,
                'Emetteur': row['Emetteur'],
                'Type': row['Type_Emetteur'],
                'Montant_MAD': total,
                'Actif_Net_MAD': actif_net,
                'Ratio': ratio,
                'Ratio_%': f"{ratio:.2%}",
                'Plafond': plafond,
                'Plafond_%': f"{plafond:.0%}",
                'Conformite': conformite,
                'Ecart_%': ecart
            })
    
    return pd.DataFrame(results)

# =============================================================================
# RÈGLE DES 45%
# =============================================================================

def check_45_percent_rule(ratios_df, portfolio_df, actif_net_dict, seuil=0.45):
    """Vérifie la règle des 45% pour les actions"""
    
    if ratios_df is None or len(ratios_df) == 0 or 'Fonds' not in ratios_df.columns:
        return pd.DataFrame()
    
    results = []
    
    for fonds in ratios_df['Fonds'].unique():
        actif_net = actif_net_dict.get(fonds, 0)
        
        if actif_net <= 0:
            continue
        
        # Filtrer les ratios du fonds
        fonds_ratios = ratios_df[ratios_df['Fonds'] == fonds]
        
        # Garder seulement les émetteurs avec ratio > 10% et non-État
        emetteurs_sup_10 = fonds_ratios[
            (fonds_ratios['Ratio'] > 0.10) & 
            (fonds_ratios['Emetteur'] != 'État marocain')
        ]
        
        total_sup_10 = emetteurs_sup_10['Montant_MAD'].sum()
        ratio_45 = total_sup_10 / actif_net if actif_net > 0 else 0
        
        results.append({
            'Fonds': fonds,
            'Total_>10%_MAD': total_sup_10,
            'Actif_Net_MAD': actif_net,
            'Ratio_45%': ratio_45,
            'Ratio_%': f"{ratio_45:.2%}",
            'Seuil': seuil,
            'Seuil_%': f"{seuil:.0%}",
            'Conformite': '✅' if ratio_45 <= seuil + 0.0001 else '❌',
            'Nb_Emetteurs': len(emetteurs_sup_10)
        })
    
    return pd.DataFrame(results)

# =============================================================================
# INTERFACE PRINCIPALE
# =============================================================================

# Container principal
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# En-tête élégant
st.markdown("""
<div class="elegant-header">
    <h1>📊 Contrôle des ratios émetteurs OPCVM</h1>
    <div class="subtitle">CFG Bank • Contrôle Interne • By Thierno Ibrahima Diallo</div>
    <div class="subtitle" style="margin-top: 0.5rem; font-size: 0.85rem; color: #999;">CDVM - Circulaire n°01-09 | Article 6</div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR - PARAMÈTRES
# =============================================================================

with st.sidebar:
    st.markdown("### ⚙️ Paramètres de Contrôle")
    
    # Plafonds
    st.markdown("#### 📊 Plafonds Réglementaires")
    plafond_etat = st.number_input("État (%)", 0, 100, 100, help="Plafond pour les émetteurs publics") / 100
    plafond_action = st.number_input("Actions éligibles 15% (%)", 0, 100, 15, help="Plafond pour actions cotées éligibles") / 100
    plafond_std = st.number_input("Plafond standard (%)", 0, 100, 10, help="Plafond standard pour émetteurs privés") / 100
    
    st.markdown("---")
    
    # Actions éligibles
    st.markdown("#### 📈 Actions Éligibles 15%")
    actions_15 = st.text_area("Liste des actions", "ATW, IAM, BCP, BOA", help="Séparer par des virgules")
    actions_list = [a.strip() for a in actions_15.split(',') if a.strip()]
    
    st.markdown("---")
    
    # Seuil 45%
    st.markdown("#### 🎯 Règle des 45%")
    seuil_45 = st.number_input("Seuil règle 45% (%)", 0, 100, 45, help="Concentration maximale >10%") / 100
    
    st.markdown("---")
    
    # Table émetteurs
    st.markdown("#### 📋 Table des Émetteurs")
    issuer_file = st.file_uploader("Fichier CSV (optionnel)", type=['csv'], help="Remplace la table par défaut")
    issuer_table = pd.read_csv(issuer_file) if issuer_file else create_default_issuer_table()
    
    st.markdown("---")
    
    # Date du rapport
    st.markdown("#### 📅 Date du Contrôle")
    control_date = st.date_input("Date", datetime.now())
    
    st.markdown("---")
    
    # Bouton calcul
    calculate = st.button("🚀 LANCER LE CONTRÔLE", type="primary", use_container_width=True)

# =============================================================================
# CHARGEMENT DU FICHIER
# =============================================================================

st.markdown('<div class="section-title">📂 Chargement des Données</div>', unsafe_allow_html=True)
st.markdown("")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Sélectionnez votre fichier FOND.xlsx", 
        type=['xlsx'],
        help="Format: Excel avec onglets par fonds"
    )

# =============================================================================
# EXÉCUTION PRINCIPALE
# =============================================================================

if uploaded_file:
    with st.spinner("⏳ Chargement des données en cours..."):
        portfolio, actif_net_dict = load_portfolio(uploaded_file)
        
        if portfolio is not None and actif_net_dict:
            
            # Afficher les fonds détectés
            with col2:
                st.markdown("##### 💼 Fonds Chargés")
                st.success(f"{len(actif_net_dict)} fonds détectés")
            
            # Cartes des fonds
            st.markdown("")
            st.markdown('<div class="section-title">💼 Portfolio Global</div>', unsafe_allow_html=True)
            st.markdown("")
            
            cols = st.columns(len(actif_net_dict))
            for i, (fonds, actif) in enumerate(actif_net_dict.items()):
                with cols[i]:
                    st.markdown(f"""
                    <div class="fund-metric">
                        <div class="fund-name">{fonds}</div>
                        <div class="fund-value">{actif:,.0f} MAD</div>
                    </div>
                    """.replace(',', ' '), unsafe_allow_html=True)
            
            st.markdown("")
            st.success(f"✅ {len(portfolio):,} lignes de positions chargées avec succès".replace(',', ' '))
            
            # Aperçu des données
            with st.expander("👁️ Aperçu des données brutes (10 premières lignes)"):
                st.dataframe(portfolio.head(10), use_container_width=True)
            
            st.markdown("---")
            
            # CALCUL
            if calculate:
                with st.spinner("🔍 Analyse en cours... Calcul des ratios et vérifications réglementaires"):
                    
                    # Étape 1: Identifier les émetteurs
                    portfolio = add_issuers(portfolio, issuer_table)
                    
                    # Étape 2: Paramètres
                    params = {
                        'plafond_etat': plafond_etat,
                        'plafond_action_eligible': plafond_action,
                        'plafond_standard': plafond_std,
                        'actions_eligibles_15pct': actions_list
                    }
                    
                    # Étape 3: Calcul des ratios
                    ratios_df = calculate_issuer_ratios(portfolio, actif_net_dict, params)
                    
                    # Étape 4: Règle 45%
                    rule_45_df = check_45_percent_rule(ratios_df, portfolio, actif_net_dict, seuil_45)
                    
                    # VÉRIFICATION CRITIQUE
                    if len(ratios_df) == 0:
                        st.error("❌ Aucun ratio calculé - Vérifiez les données")
                        st.stop()
                    
                    if 'Fonds' not in ratios_df.columns:
                        st.error("❌ Erreur: Colonne 'Fonds' manquante")
                        st.write("Colonnes disponibles:", ratios_df.columns.tolist())
                        st.stop()
                    
                    # -----------------------------------------------------------------
                    # INDICATEURS CLÉS
                    # -----------------------------------------------------------------
                    
                    total_conformes = len(ratios_df[ratios_df['Conformite'] == '✅'])
                    total_non_conformes = len(ratios_df[ratios_df['Conformite'] == '❌'])
                    taux_conformite = total_conformes / len(ratios_df) * 100 if len(ratios_df) > 0 else 0
                    
                    st.markdown('<div class="section-title">📊 Tableau de Bord</div>', unsafe_allow_html=True)
                    st.markdown("")
                    
                    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
                    
                    with kpi1:
                        st.markdown(f"""
                        <div class="modern-metric-card">
                            <h4>Total Ratios</h4>
                            <div class="value">{len(ratios_df)}</div>
                            <div class="subvalue">Contrôles effectués</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with kpi2:
                        st.markdown(f"""
                        <div class="modern-metric-card metric-success">
                            <h4>✓ Conformes</h4>
                            <div class="value">{total_conformes}</div>
                            <div class="subvalue">{taux_conformite:.1f}% du total</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with kpi3:
                        st.markdown(f"""
                        <div class="modern-metric-card metric-danger">
                            <h4>✗ Non-conformes</h4>
                            <div class="value">{total_non_conformes}</div>
                            <div class="subvalue">Alertes actives</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with kpi4:
                        nb_etat = len(ratios_df[ratios_df['Emetteur'] == 'État marocain'])
                        st.markdown(f"""
                        <div class="modern-metric-card metric-info">
                            <h4>🏛️ Secteur Public</h4>
                            <div class="value">{nb_etat}</div>
                            <div class="subvalue">Positions État</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with kpi5:
                        nb_prive = len(ratios_df[ratios_df['Type'] == 'privé'])
                        st.markdown(f"""
                        <div class="modern-metric-card metric-info">
                            <h4>🏢 Secteur Privé</h4>
                            <div class="value">{nb_prive}</div>
                            <div class="subvalue">Positions privées</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("")
                    st.markdown("---")
                    
                    # -----------------------------------------------------------------
                    # ONGLETS
                    # -----------------------------------------------------------------
                    
                    tab1, tab2, tab3, tab4 = st.tabs([
                        "📊 Vue d'Ensemble", 
                        "⚠️ Alertes & Non-conformités", 
                        "🎯 Règle des 45%",
                        "📤 Export & Rapports"
                    ])
                    
                    with tab1:
                        st.markdown('<div class="section-title">📋 Ratios Émetteurs par Fonds</div>', unsafe_allow_html=True)
                        st.markdown("")
                        
                        display_cols = ['Fonds', 'Emetteur', 'Montant_MAD', 'Ratio_%', 
                                       'Plafond_%', 'Conformite', 'Ecart_%']
                        
                        df_show = ratios_df[display_cols].copy()
                        df_show['Montant_MAD'] = df_show['Montant_MAD'].apply(
                            lambda x: f"{x:,.0f}".replace(',', ' ')
                        )
                        df_show['Ecart_%'] = df_show['Ecart_%'].apply(lambda x: f"{x:.2f}%")
                        
                        st.dataframe(df_show, use_container_width=True, height=500)
                        
                        # Graphique de répartition
                        st.markdown("")
                        st.markdown("##### 📈 Répartition des Conformités")
                        
                        conf_counts = ratios_df['Conformite'].value_counts()
                        fig = go.Figure(data=[go.Pie(
                            labels=['Conformes', 'Non-conformes'],
                            values=[conf_counts.get('✅', 0), conf_counts.get('❌', 0)],
                            hole=.4,
                            marker_colors=['#38ef7d', '#ff6a00']
                        )])
                        fig.update_layout(
                            height=400,
                            showlegend=True,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with tab2:
                        st.markdown('<div class="section-title">⚠️ Non-conformités Détectées</div>', unsafe_allow_html=True)
                        st.markdown("")
                        
                        non_conformes = ratios_df[ratios_df['Conformite'] == '❌']
                        
                        if len(non_conformes) > 0:
                            st.error(f"🚨 {len(non_conformes)} non-conformité(s) réglementaire(s) détectée(s)")
                            
                            # Tableau des alertes
                            alert_cols = ['Fonds', 'Emetteur', 'Ratio_%', 'Plafond_%', 'Ecart_%']
                            df_alert = non_conformes[alert_cols].copy()
                            
                            st.dataframe(
                                df_alert.style.apply(
                                    lambda x: ['background-color: #ffe6e6' for i in x],
                                    axis=1
                                ),
                                use_container_width=True
                            )
                            
                            # Détails par émetteur
                            st.markdown("")
                            st.markdown("##### 📊 Analyse des Dépassements")
                            
                            for _, row in non_conformes.iterrows():
                                with st.expander(f"🔴 {row['Fonds']} - {row['Emetteur']} (Écart: {row['Ecart_%']:.2f}%)"):
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Montant", f"{row['Montant_MAD']:,.0f} MAD".replace(',', ' '))
                                    with col2:
                                        st.metric("Ratio Actuel", row['Ratio_%'])
                                    with col3:
                                        st.metric("Plafond", row['Plafond_%'])
                        else:
                            st.success("✅ Aucune non-conformité détectée - Tous les ratios respectent les limites réglementaires")
                            st.balloons()
                    
                    with tab3:
                        st.markdown('<div class="section-title">🎯 Règle de Concentration des 45%</div>', unsafe_allow_html=True)
                        st.info("📖 **Règle**: La somme des émetteurs d'actions dont le ratio individuel dépasse 10% ne peut excéder 45% de l'actif net total du fonds.")
                        st.markdown("")
                        
                        if len(rule_45_df) > 0:
                            # Tableau de la règle 45%
                            st.dataframe(
                                rule_45_df.style.apply(
                                    lambda row: ['background-color: #e6ffe6' if row['Conformite'] == '✅' 
                                                 else 'background-color: #ffe6e6' for _ in row],
                                    axis=1
                                ),
                                use_container_width=True
                            )
                            
                            # Résumé
                            st.markdown("")
                            conformes_45 = len(rule_45_df[rule_45_df['Conformite'] == '✅'])
                            non_conformes_45 = len(rule_45_df[rule_45_df['Conformite'] == '❌'])
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("✅ Fonds Conformes", conformes_45)
                            with col2:
                                st.metric("❌ Fonds Non-conformes", non_conformes_45)
                        else:
                            st.warning("⚠️ Aucune donnée disponible pour l'analyse de la règle des 45%")
                    
                    with tab4:
                        st.markdown('<div class="section-title">📤 Export des Résultats</div>', unsafe_allow_html=True)
                        st.markdown("")
                        
                        # Préparer l'export
                        export_dict = {
                            'Ratios_Complet': ratios_df,
                            'Regle_45pct': rule_45_df
                        }
                        
                        if len(non_conformes) > 0:
                            export_dict['Non_Conformites'] = non_conformes
                        
                        # Statistiques récapitulatives
                        summary_data = {
                            'Indicateur': [
                                'Date du contrôle',
                                'Nombre total de ratios',
                                'Ratios conformes',
                                'Ratios non-conformes',
                                'Taux de conformité',
                                'Positions État',
                                'Positions privées',
                                'Fonds analysés'
                            ],
                            'Valeur': [
                                control_date.strftime('%d/%m/%Y'),
                                len(ratios_df),
                                total_conformes,
                                total_non_conformes,
                                f"{taux_conformite:.1f}%",
                                nb_etat,
                                nb_prive,
                                len(actif_net_dict)
                            ]
                        }
                        export_dict['Synthese'] = pd.DataFrame(summary_data)
                        
                        # Export Excel
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            for sheet_name, df in export_dict.items():
                                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
                        
                        output.seek(0)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.download_button(
                                label="📥 Télécharger Rapport Complet (Excel)",
                                data=output,
                                file_name=f"controle_emetteurs_{control_date.strftime('%Y%m%d')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                        
                        with col2:
                            # Export CSV des non-conformités
                            if len(non_conformes) > 0:
                                csv = non_conformes.to_csv(index=False)
                                st.download_button(
                                    label="📥 Télécharger Alertes (CSV)",
                                    data=csv,
                                    file_name=f"alertes_{control_date.strftime('%Y%m%d')}.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
                        
                        # Aperçu du contenu exporté
                        st.markdown("")
                        st.markdown("##### 📋 Contenu du Rapport")
                        st.info(f"""
                        Le rapport Excel contient **{len(export_dict)} onglets**:
                        - 📊 **Ratios_Complet**: Tous les ratios calculés ({len(ratios_df)} lignes)
                        - 🎯 **Regle_45pct**: Analyse de concentration ({len(rule_45_df)} lignes)
                        {f"- ⚠️ **Non_Conformites**: Alertes réglementaires ({len(non_conformes)} lignes)" if len(non_conformes) > 0 else ""}
                        - 📈 **Synthese**: Indicateurs clés de performance
                        """)
                    
                    # -----------------------------------------------------------------
                    # RAPPORT DE SYNTHÈSE
                    # -----------------------------------------------------------------
                    
                    st.markdown("---")
                    st.markdown('<div class="section-title">📋 Synthèse du Contrôle</div>', unsafe_allow_html=True)
                    st.markdown("")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("##### ✅ Points Positifs")
                        st.markdown(f"""
                        - ✓ **{total_conformes} ratios conformes** sur {len(ratios_df)} contrôles
                        - ✓ **Taux de conformité**: {taux_conformite:.1f}%
                        - ✓ **{len(rule_45_df[rule_45_df['Conformite'] == '✅'])} fonds** respectent la règle des 45%
                        - ✓ **{len(actif_net_dict)} fonds** analysés avec succès
                        """)
                    
                    with col2:
                        if total_non_conformes > 0:
                            st.markdown("##### ⚠️ Points d'Attention")
                            emetteurs_alert = ', '.join(non_conformes['Emetteur'].unique()[:5])
                            st.markdown(f"""
                            - ⚠ **{total_non_conformes} non-conformités** détectées
                            - ⚠ **Émetteurs concernés**: {emetteurs_alert}
                            - ⚠ **Action requise**: Régularisation nécessaire
                            - ⚠ **Suivi**: Monitoring renforcé recommandé
                            """)
                        else:
                            st.markdown("##### ✅ Conformité Totale")
                            st.markdown("""
                            - ✓ Aucun dépassement réglementaire
                            - ✓ Portfolio en conformité CDVM
                            - ✓ Tous les seuils respectés
                            - ✓ Gestion conforme aux normes
                            """)
                    
        else:
            st.error("❌ Échec du chargement des données - Vérifiez le format du fichier Excel")
            st.info("ℹ️ Le fichier doit contenir des onglets nommés: Action, Diversifie, OMLT, OCT, Monetaire")
else:
    st.info("👈 **Pour commencer**: Chargez votre fichier FOND.xlsx dans la zone ci-dessus")
    
    # Instructions
    with st.expander("📖 Guide d'utilisation"):
        st.markdown("""
        ### Mode d'emploi
        
        1. **Chargement**: Uploadez votre fichier Excel FOND.xlsx
        2. **Configuration**: Ajustez les paramètres dans la barre latérale (optionnel)
        3. **Analyse**: Cliquez sur "🚀 LANCER LE CONTRÔLE"
        4. **Résultats**: Consultez les tableaux de bord et alertes
        5. **Export**: Téléchargez le rapport complet
        
        ### Format du fichier attendu
        - Format: Excel (.xlsx)
        - Onglets: Un par fonds (Action, Diversifie, OMLT, OCT, Monetaire)
        - Colonnes: Code ISIN, Type, Description, Quantité, Prix, Valorisation...
        
        ### Contrôles effectués
        - ✓ Ratio par émetteur vs plafonds CDVM
        - ✓ Règle de concentration des 45%
        - ✓ Distinction secteur public/privé
        - ✓ Actions éligibles 15%
        """)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; font-size: 0.85rem; padding: 1rem 0;">
    <p>📊 Application de Contrôle Réglementaire OPCVM | Version 2.0</p>
    <p>CFG Bank - Contrôle Interne | Conforme CDVM Circulaire n°01-09</p>
</div>
""", unsafe_allow_html=True)
