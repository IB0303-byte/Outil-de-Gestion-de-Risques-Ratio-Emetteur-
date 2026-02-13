"""
PROTOTYPE - Contrôle des ratios émetteurs OPCVM
CDVM Circulaire n°01-09 - Article 6
Version Premium Design
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
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# GESTION SESSION - PAGE D'ACCUEIL
# =============================================================================
if 'app_started' not in st.session_state:
    st.session_state.app_started = False

# =============================================================================
# CSS PREMIUM DESIGN
# =============================================================================

st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Reset et Police globale */
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* ===== PAGE D'ACCUEIL ===== */
    .landing-page {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        padding: 2rem;
    }
    
    .hero-container {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 30px;
        padding: 4rem 3rem;
        box-shadow: 0 30px 80px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        max-width: 900px;
        text-align: center;
    }
    
    .logo-badge {
        display: inline-block;
        background: linear-gradient(135deg, #e63946 0%, #f72d42 100%);
        padding: 1.2rem 3.5rem;
        border-radius: 15px;
        margin-bottom: 3rem;
        box-shadow: 0 10px 40px rgba(230, 57, 70, 0.4);
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .logo-badge h1 {
        color: white;
        font-size: 3.2rem;
        font-weight: 900;
        margin: 0;
        letter-spacing: 6px;
        text-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    /* Nouvelle section logo SVG */
    .logo-section {
        margin-bottom: 3rem;
        animation: float 3s ease-in-out infinite;
    }
    
    .logo-section svg {
        filter: drop-shadow(0 10px 30px rgba(230, 57, 70, 0.3));
    }
    
    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 2rem 0 1.5rem 0;
        line-height: 1.3;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: #a0a0a0;
        font-weight: 400;
        margin: 1.5rem 0 3rem 0;
        line-height: 1.6;
    }
    
    .hero-badge {
        display: inline-block;
        background: rgba(230, 57, 70, 0.15);
        color: #e63946;
        padding: 0.6rem 1.5rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 2rem;
        border: 1px solid rgba(230, 57, 70, 0.3);
    }
    
    /* Bouton d'entrée stylisé */
    .stButton > button {
        background: linear-gradient(135deg, #e63946 0%, #f72d42 100%);
        color: white;
        border: none;
        padding: 1.2rem 3.5rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1.15rem;
        transition: all 0.4s ease;
        box-shadow: 0 10px 30px rgba(230, 57, 70, 0.4);
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(230, 57, 70, 0.6);
        background: linear-gradient(135deg, #f72d42 0%, #e63946 100%);
    }
    
    /* ===== APPLICATION PRINCIPALE ===== */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
    }
    
    .main-container {
        background: white;
        border-radius: 25px;
        padding: 2.5rem;
        margin: 1.5rem auto;
        max-width: 1600px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
    }
    
    /* En-tête moderne */
    .app-header {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    }
    
    .app-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0 0 0.8rem 0;
        letter-spacing: -0.5px;
    }
    
    .app-header .subtitle {
        color: #a0a0a0;
        font-size: 1.05rem;
        font-weight: 400;
        margin: 0.5rem 0 0 0;
    }
    
    .badge-red {
        display: inline-block;
        background: linear-gradient(135deg, #e63946 0%, #f72d42 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-left: 1rem;
    }
    
    /* Cartes métriques ultra-modernes */
    .metric-card {
        background: white;
        border-radius: 18px;
        padding: 2rem 1.5rem;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #e63946;
        transition: all 0.3s ease;
        margin-bottom: 1.5rem;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.12);
    }
    
    .metric-card h4 {
        color: #6c757d;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0 0 1rem 0;
    }
    
    .metric-card .value {
        font-size: 2.8rem;
        font-weight: 800;
        color: #1e1e2e;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .metric-card .subvalue {
        color: #9ca3af;
        font-size: 0.95rem;
        font-weight: 500;
    }
    
    /* Variantes de couleurs */
    .metric-success {
        border-left-color: #10b981;
        background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
    }
    
    .metric-success .value {
        color: #10b981;
    }
    
    .metric-danger {
        border-left-color: #ef4444;
        background: linear-gradient(135deg, #ffffff 0%, #fef2f2 100%);
    }
    
    .metric-danger .value {
        color: #ef4444;
    }
    
    .metric-info {
        border-left-color: #3b82f6;
        background: linear-gradient(135deg, #ffffff 0%, #eff6ff 100%);
    }
    
    .metric-info .value {
        color: #3b82f6;
    }
    
    .metric-warning {
        border-left-color: #f59e0b;
        background: linear-gradient(135deg, #ffffff 0%, #fffbeb 100%);
    }
    
    .metric-warning .value {
        color: #f59e0b;
    }
    
    /* Section titles */
    .section-header {
        margin: 2.5rem 0 1.5rem 0;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .section-header h2 {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e1e2e;
        margin: 0;
        display: inline-block;
    }
    
    .section-icon {
        font-size: 2rem;
        margin-right: 1rem;
        vertical-align: middle;
    }
    
    /* Tableaux élégants */
    .dataframe {
        border: none !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
    }
    
    .dataframe thead tr th {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.5px !important;
        padding: 1.2rem 1rem !important;
        border: none !important;
    }
    
    .dataframe tbody tr {
        border-bottom: 1px solid #f0f0f0 !important;
    }
    
    .dataframe tbody tr:hover {
        background-color: #f8f9fa !important;
        transition: all 0.2s ease;
    }
    
    .dataframe tbody td {
        padding: 1rem !important;
        color: #374151 !important;
        font-size: 0.95rem !important;
    }
    
    /* Onglets stylisés */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: transparent;
        border-bottom: 2px solid #e5e7eb;
        padding: 0 0 0 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: auto;
        padding: 1rem 2rem;
        background: transparent;
        border-radius: 12px 12px 0 0;
        color: #6b7280;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #f9fafb;
        color: #1e1e2e;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        color: white !important;
    }
    
    /* Sidebar élégante */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1e2e 0%, #2d2d44 100%);
        padding: 2rem 1rem;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    
    [data-testid="stSidebar"] label {
        color: #d1d5db !important;
        font-weight: 500 !important;
    }
    
    /* Alerts élégantes */
    .stAlert {
        border-radius: 12px;
        border: none;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #f9fafb;
        border-radius: 12px;
        font-weight: 600;
        color: #1e1e2e;
        padding: 1rem 1.5rem;
    }
    
    .streamlit-expanderHeader:hover {
        background: #f3f4f6;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
        border: 2px dashed #d1d5db;
        border-radius: 15px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #e63946;
        background: white;
    }
    
    /* Cartes de fonds */
    .fund-card {
        background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
        border: 2px solid #e5e7eb;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .fund-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border-color: #e63946;
    }
    
    .fund-card .fund-name {
        font-weight: 800;
        font-size: 1.4rem;
        color: #1e1e2e;
        margin-bottom: 0.8rem;
        letter-spacing: 1px;
    }
    
    .fund-card .fund-value {
        font-size: 1.05rem;
        color: #6b7280;
        font-weight: 500;
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #e63946 0%, #f72d42 100%);
    }
    
    /* Inputs stylisés */
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        padding: 0.8rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #e63946;
        box-shadow: 0 0 0 3px rgba(230, 57, 70, 0.1);
    }
    
    /* Scrollbar personnalisée */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #e63946 0%, #f72d42 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #d62839;
    }
    
    /* Animation de chargement */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading {
        animation: pulse 2s ease-in-out infinite;
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
        value = value.strip()
        value = value.replace(' ', '')
        value = value.replace(',', '')
        value = value.replace(' ', '')
        value = value.replace('\xa0', '')
        value = value.replace('\t', '')
        value = value.replace('\n', '')
        if value == '' or value == '-' or value == 'nan':
            return 0.0
        try:
            return float(value)
        except ValueError:
            value = re.sub(r'[^\d.-]', '', value)
            try:
                return float(value) if value else 0.0
            except:
                return 0.0
    return 0.0

# =============================================================================
# FONCTION DE CHARGEMENT
# =============================================================================

@st.cache_data
def load_portfolio(file):
    """Charge le fichier Excel avec correction des noms de fonds"""
    try:
        xl = pd.ExcelFile(file)
        all_data = []
        actif_net_dict = {}
        
        fonds_mapping = {
            'Action': 'CFP',
            'Diversifie': 'TIJ',
            'OMLT': 'PRV',
            'OCT': 'CLB',
            'Monetaire': 'CCS'
        }
        
        actif_net_values = {
            'CFP': 276403573.05,
            'CCS': 356674412.16,
            'TIJ': 478502756.69,
            'CLB': 1704711189.03,
            'PRV': 708721589.76
        }
        
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(file, sheet_name=sheet_name, header=None)
            fonds_name = fonds_mapping.get(sheet_name, sheet_name)
            actif_net = actif_net_values.get(fonds_name, 0)
            
            df_data = df.iloc[1:].copy()
            df_data = df_data.dropna(how='all')
            
            if len(df_data) > 0 and len(df_data.columns) >= 9:
                df_data.columns = ['Code_ISIN', 'Type', 'Description', 'Quantite', 
                                  'Prix_revient', 'Valo_j', 'Prix_revient_global',
                                  'Valo_globale', 'Plus_moins_value'] + [f'Col{i}' for i in range(10, len(df_data.columns)+1)]
                
                if 'Valo_globale' in df_data.columns:
                    df_clean = df_data[['Type', 'Description', 'Valo_globale']].copy()
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
# TABLE DES ÉMETTEURS
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
            'CDM', 'CIH', 'MUTANDIS',
            'LBV', 'LABEL VIE',
            'COSUMAR', 'CSR',
            'ONCF', 'OBLONCF',
            'CAM', 'OBLCAM',
            'RCI', 'BSFRCI',
            'BDT', 'CFG', 'IRGAM',
            'PRS', 'INSTICASH', 'TWIN'
        ],
        'emetteur': [
            'ATW', 'ATW', 'ATW', 'ATW',
            'ARADEI', 'ARADEI',
            'BCP', 'BCP',
            'IAM', 'IAM',
            'BOA', 'BOA',
            'CDM', 'CIH', 'MUTANDIS',
            'LBV', 'LBV',
            'COSUMAR', 'COSUMAR',
            'ONCF', 'ONCF',
            'CAM', 'CAM',
            'RCI', 'RCI',
            'État marocain', 'CFG', 'IRGAM',
            'CFG', 'CFG', 'TWIN'
        ],
        'type': [
            'privé', 'privé', 'privé', 'privé',
            'privé', 'privé',
            'privé', 'privé',
            'privé', 'privé',
            'privé', 'privé',
            'privé', 'privé', 'privé',
            'privé', 'privé',
            'privé', 'privé',
            'privé', 'privé',
            'privé', 'privé',
            'privé', 'privé',
            'public', 'privé', 'privé',
            'privé', 'privé', 'privé'
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
    
    if 'BDT' in desc:
        return 'État marocain', 'public'
    
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
    issuers = result['Description'].apply(
        lambda x: identify_issuer(x, issuer_table)
    )
    
    result['Emetteur'] = [i[0] for i in issuers]
    result['Type_Emetteur'] = [i[1] for i in issuers]
    
    return result

# =============================================================================
# CALCUL DES RATIOS
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
        
        grouped = fonds_data.groupby('Emetteur').agg({
            'Valo_globale': 'sum',
            'Type_Emetteur': 'first'
        }).reset_index()
        
        for _, row in grouped.iterrows():
            total = row['Valo_globale']
            ratio = total / actif_net
            
            if row['Emetteur'] == 'État marocain' or row['Type_Emetteur'] == 'public':
                plafond = params.get('plafond_etat', 1.0)
            else:
                emetteur_data = fonds_data[fonds_data['Emetteur'] == row['Emetteur']]
                is_action = any('ACTION' in str(t).upper() for t in emetteur_data['Type'])
                
                if is_action and row['Emetteur'] in params.get('actions_eligibles_15pct', []):
                    plafond = params.get('plafond_action_eligible', 0.15)
                else:
                    plafond = params.get('plafond_standard', 0.10)
            
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
        
        fonds_ratios = ratios_df[ratios_df['Fonds'] == fonds]
        
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
# PAGE D'ACCUEIL
# =============================================================================

if not st.session_state.app_started:
    st.markdown("""
    <div class="landing-page">
        <div class="hero-container">
            <div class="hero-badge">
                🔒 Application Sécurisée
            </div>
            
            <div class="logo-section">
                <img src="data:image/png;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAC5AlcDASIAAhEBAxEB/8QAHAABAQEBAAMBAQAAAAAAAAAAAAgHBgMEBQEC/8QAXxAAAQMCAgQGDAYOBQkHBQAAAQACAwQFBgEHEiExCBQUQVFhGCI3U1VxgZGSk7LTFTJSUnWhFiM1NmJyc3SChLGztMEXVqLR0iQlM1SUo6TCwyY0Q4OV4fBERWNl8f/EABsBAQACAwEBAAAAAAAAAAAAAAAEBQMGBwIB/8QARBEAAQIDAgkIBwcDBQEBAAAAAQACAwQhBSExkRIcEhNRScGx8AYUMTVBcdEEUmGBoaLhIjJCkvEzYhYjcrLSw+I0of/aAAwDAQACEQMRAD8AgtEREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREX45zWNLnODWgZkk5ABEX6uVxrpBwthHWjutwDqsNzFJANeU9Gzc39IhZfpb00PD5rLg6YADNk1xG3PpEX+PzcxXA4F0b4jxm511nk5DbXEvmuNWSdf5xaCc38+ZzA37VRx7QJdycAYx7FulnYLMbB+1Wm/k2atJ+G6ldy6fFWnu/1kjo8P0NPbINwklAmlPXt7UeLI+NcVLjLSDfZixl9vdS92+Olke0H9GPIfUu6krdD+BhxVJQvxfdIxtlkIdDreM9pl1ta7xr0K/TpiPi+T2W02204+I1kRe5v1hv9lV0R5J/rRb9Qv8AgFtcnAhsb/oZEU2n0b4hzvBco63aSZGmR1Bi143FxhqCPPkvUku+NLK8NqK29UZz2MqHSAeZ2xdXZtKOlK9XWKht12ZLPJmQzkkDWgAZlxJbsAAJJJXlt+m/GjCWV0FtucGX21ktNlm3xtIH1LEORzh7h1eamuE8SWvl4TqaA6+/e2mhfMs2lXENI9rbhHT3CIb9ZvFv87dn1LR8KY8sWIHMgZMaSsdsFPPsLj+Cdx/b1LnGYl0T4yIgxBhx+Gq2TYKyjIEbT0ktA/tMPjXwMc6KrvYqL4ZstTHfbKW8Y2qpci5jelzQTmPwmkjpyUqHHjwxjNdjt7fiqObsuy5x3JRoRl4pzZsUnoI9k7ritsRYtgDSTU290duvz31NHmGtqCSZIvH85v1jr3LZaeaGogZPTyslikaHMew5hwPOqOXmWR21atHtaxpmy4uJGFxzEZj9al5ERFIVStDREWVeUREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREWAcIfSM+SebB1jqMomdrcZmHa53egegfK6Ts5jnqOlzFYwhgqquMTm8tl+0UbTzyO58vwQC7yZc6nXRBhNuLsTy1d3kItFA01VxmkdkHDaQ0u/CyJJ6A5VVoR3EiBDznPvW64LWdBYx9pzQ9iHm6T9UA6dy+ro5wVaaKxfZ3jsmGzREGkpCO3rHc2znaeYc+0nJo2/Gx9pAvuNaxlvgaaK1hwjpbdTnJp25N1svjHd1DmAX96ScWVOPcW09HQjiLXFK2lt1PlqtaCQ0PI5idniGQ5lq9BNhnAGLLNg6gwfLU1lTNFFJd6mIN13OIzexxBLss9wIAy6lAawPBhw3UYLidZW0xoz5d7ZmZh48ZwJayooxoz59Os5ybhcF/FBZ8A6JcP01TiWKC4X2ZmuRxTZZC7nEbTsa0btY5Z9PMuVxHpK0e4nhkpbzgmohacwyrpXR8oZ1jY3zEkdK5fT1ejedJVwzpmQChPKmlpzLwwntj1kk+TILg14jzZY4woYGKLs2dZbMsJseG2cmnuMV19cYilb6ChzLS8CUcdBojxviWnBM7hHboZHDJzY3vYJB1Zh7c/Eu8wxW1+C9Adqu2H7c2qrqupElQBEX67XSOzzA2/FaG582a5TCjR2MeK3Eb7oz6nUy46zaRsaWeyxWa23ySnooQRHGIYyWgkk5OLdbeTzr22K2AGk6W6NZJWGNIxrSMUNocWMKhxIBa1gFLgdJqtR0saPJMUWe14rwrYJKW41jWuraENERGs3W1iHZDWB2E8+YK4Wx12kLRXWsqKi3VlPQyOylp6hpdTS9WYzAd1g5+MbF8+PSjj5lOyEYlqy1j9cFzWF2e3YXEZkbdxzG7oW2aFMb1OkG1XOz4koqeokp42iR4jHFzsfmMnN3A7ObYegZL2wwZiLWGS1/ZVR5ltoWVIls0xkWAM4qcYAm686q3aVnuM8K2TGeHpccYCh4qWLbc7S0dtE7LMuaB5TkNhG0ZEEL4WibGT7VWstFxm/zbO7JjnH/QPPP1NPP0b+lBdJtGGlqvFokfLR0tU6KSHX2SwHbqE9IB39IzXtabcL0NFVUeLcPBrrFe28azUGTYpSMy3LmB2kDmIcNmSxFxaTGZc5v3h/PxU0QYcaGJCZJdCiisNxzi6uKTrAvadIqCtnRcVogxEb1hwUlTJrVlDlG8k7XM+Q76iPJ1or2FEEVgeNK5TPScSSmHy8TO00+B6xet4REUlQ0RERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERFM/Cgvrq/GkFkY77TbIAXDPfJIA4n0dT61/eJn/YToOtVih+13LEbjVVhHxhFsIb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" 
                     alt="CFG Bank Logo" 
                     style="width: 250px; height: auto; margin-bottom: 2rem; filter: drop-shadow(0 10px 30px rgba(230, 57, 70, 0.3));">
            </div>
            
            <div class="hero-title">
                Contrôle des ratios<br>émetteurs OPCVM
            </div>
            
            <div class="hero-subtitle">
                CFG Bank • Contrôle Interne • By Thierno Ibrahima Diallo
                <br>
                CDVM - Circulaire n°01-09 | Article 6
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Accéder à l'Application", key="enter_app", use_container_width=True):
            st.session_state.app_started = True
            st.rerun()
    
    st.stop()

# =============================================================================
# APPLICATION PRINCIPALE
# =============================================================================

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# En-tête
st.markdown("""
<div class="app-header">
    <h1>🏦 Contrôle des Ratios Émetteurs OPCVM</h1>
    <div class="subtitle">
        CFG Bank • Contrôle Interne • By Thierno Ibrahima Diallo
        <span class="badge-red">CDVM n°01-09</span>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown("### 🏠 Navigation")
    if st.button("← Retour à l'accueil", use_container_width=True, type="secondary"):
        st.session_state.app_started = False
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("### ⚙️ Paramètres Réglementaires")
    
    st.markdown("#### 📊 Plafonds")
    plafond_etat = st.number_input("État (%)", 0, 100, 100, help="Plafond émetteurs publics") / 100
    plafond_action = st.number_input("Actions éligibles (%)", 0, 100, 15, help="Actions cotées éligibles") / 100
    plafond_std = st.number_input("Standard (%)", 0, 100, 10, help="Plafond standard") / 100
    
    st.markdown("---")
    
    st.markdown("#### 📈 Actions Éligibles 15%")
    actions_15 = st.text_area("Liste", "ATW, IAM, BCP, BOA", help="Séparer par virgules")
    actions_list = [a.strip() for a in actions_15.split(',') if a.strip()]
    
    st.markdown("---")
    
    st.markdown("#### 🎯 Règle 45%")
    seuil_45 = st.number_input("Seuil (%)", 0, 100, 45, help="Concentration max >10%") / 100
    
    st.markdown("---")
    
    st.markdown("#### 📋 Table Émetteurs")
    issuer_file = st.file_uploader("CSV (optionnel)", type=['csv'])
    issuer_table = pd.read_csv(issuer_file) if issuer_file else create_default_issuer_table()
    
    st.markdown("---")
    
    st.markdown("#### 📅 Date")
    control_date = st.date_input("Date du contrôle", datetime.now())
    
    st.markdown("---")
    
    calculate = st.button("🚀 LANCER L'ANALYSE", type="primary", use_container_width=True)

# =============================================================================
# CHARGEMENT FICHIER
# =============================================================================

st.markdown('<div class="section-header"><h2><span class="section-icon">📂</span>Chargement des Données</h2></div>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Sélectionnez votre fichier Excel (FOND.xlsx)", 
        type=['xlsx'],
        help="Format: Excel avec onglets par fonds"
    )

if uploaded_file:
    with st.spinner("⏳ Chargement en cours..."):
        portfolio, actif_net_dict = load_portfolio(uploaded_file)
        
        if portfolio is not None and actif_net_dict:
            
            with col2:
                st.markdown("##### 📊 Statut")
                st.success(f"✓ {len(actif_net_dict)} fonds")
            
            st.markdown("")
            st.markdown('<div class="section-header"><h2><span class="section-icon">💼</span>Portfolio Chargé</h2></div>', unsafe_allow_html=True)
            
            # Cartes des fonds
            cols = st.columns(len(actif_net_dict))
            for i, (fonds, actif) in enumerate(actif_net_dict.items()):
                with cols[i]:
                    st.markdown(f"""
                    <div class="fund-card">
                        <div class="fund-name">{fonds}</div>
                        <div class="fund-value">{actif:,.0f} MAD</div>
                    </div>
                    """.replace(',', ' '), unsafe_allow_html=True)
            
            st.markdown("")
            st.success(f"✅ **{len(portfolio):,} positions** chargées avec succès".replace(',', ' '))
            
            with st.expander("👁️ Aperçu des données (10 premières lignes)"):
                st.dataframe(portfolio.head(10), use_container_width=True)
            
            st.markdown("---")
            
            # CALCUL
            if calculate:
                with st.spinner("🔍 Analyse réglementaire en cours..."):
                    
                    portfolio = add_issuers(portfolio, issuer_table)
                    
                    params = {
                        'plafond_etat': plafond_etat,
                        'plafond_action_eligible': plafond_action,
                        'plafond_standard': plafond_std,
                        'actions_eligibles_15pct': actions_list
                    }
                    
                    ratios_df = calculate_issuer_ratios(portfolio, actif_net_dict, params)
                    rule_45_df = check_45_percent_rule(ratios_df, portfolio, actif_net_dict, seuil_45)
                    
                    if len(ratios_df) == 0:
                        st.error("❌ Aucun ratio calculé")
                        st.stop()
                    
                    if 'Fonds' not in ratios_df.columns:
                        st.error("❌ Erreur structure")
                        st.stop()
                    
                    # INDICATEURS
                    total_conformes = len(ratios_df[ratios_df['Conformite'] == '✅'])
                    total_non_conformes = len(ratios_df[ratios_df['Conformite'] == '❌'])
                    taux_conformite = total_conformes / len(ratios_df) * 100 if len(ratios_df) > 0 else 0
                    
                    st.markdown('<div class="section-header"><h2><span class="section-icon">📊</span>Tableau de Bord</h2></div>', unsafe_allow_html=True)
                    
                    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
                    
                    with kpi1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>Total Ratios</h4>
                            <div class="value">{len(ratios_df)}</div>
                            <div class="subvalue">Contrôles</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with kpi2:
                        st.markdown(f"""
                        <div class="metric-card metric-success">
                            <h4>✓ Conformes</h4>
                            <div class="value">{total_conformes}</div>
                            <div class="subvalue">{taux_conformite:.1f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with kpi3:
                        st.markdown(f"""
                        <div class="metric-card metric-danger">
                            <h4>✗ Alertes</h4>
                            <div class="value">{total_non_conformes}</div>
                            <div class="subvalue">Non-conformes</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with kpi4:
                        nb_etat = len(ratios_df[ratios_df['Emetteur'] == 'État marocain'])
                        st.markdown(f"""
                        <div class="metric-card metric-info">
                            <h4>🏛️ Public</h4>
                            <div class="value">{nb_etat}</div>
                            <div class="subvalue">Positions État</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with kpi5:
                        nb_prive = len(ratios_df[ratios_df['Type'] == 'privé'])
                        st.markdown(f"""
                        <div class="metric-card metric-warning">
                            <h4>🏢 Privé</h4>
                            <div class="value">{nb_prive}</div>
                            <div class="subvalue">Positions privées</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("")
                    st.markdown("---")
                    
                    # ONGLETS
                    tab1, tab2, tab3, tab4 = st.tabs([
                        "📊 Vue Complète", 
                        "⚠️ Non-Conformités", 
                        "🎯 Règle 45%",
                        "📤 Export"
                    ])
                    
                    with tab1:
                        st.markdown('<div class="section-header"><h2>Ratios par Émetteur</h2></div>', unsafe_allow_html=True)
                        
                        display_cols = ['Fonds', 'Emetteur', 'Montant_MAD', 'Ratio_%', 
                                       'Plafond_%', 'Conformite', 'Ecart_%']
                        
                        df_show = ratios_df[display_cols].copy()
                        df_show['Montant_MAD'] = df_show['Montant_MAD'].apply(
                            lambda x: f"{x:,.0f}".replace(',', ' ')
                        )
                        df_show['Ecart_%'] = df_show['Ecart_%'].apply(lambda x: f"{x:.2f}%")
                        
                        st.dataframe(df_show, use_container_width=True, height=500)
                        
                        # Graphique
                        st.markdown("")
                        st.markdown("##### 📈 Répartition")
                        
                        conf_counts = ratios_df['Conformite'].value_counts()
                        fig = go.Figure(data=[go.Pie(
                            labels=['Conformes ✓', 'Non-conformes ✗'],
                            values=[conf_counts.get('✅', 0), conf_counts.get('❌', 0)],
                            hole=.5,
                            marker_colors=['#10b981', '#ef4444'],
                            textfont_size=16
                        )])
                        fig.update_layout(
                            height=400,
                            showlegend=True,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(family="Poppins", size=14)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with tab2:
                        st.markdown('<div class="section-header"><h2>Alertes Réglementaires</h2></div>', unsafe_allow_html=True)
                        
                        non_conformes = ratios_df[ratios_df['Conformite'] == '❌']
                        
                        if len(non_conformes) > 0:
                            st.error(f"🚨 **{len(non_conformes)} non-conformité(s)** détectée(s)")
                            
                            alert_cols = ['Fonds', 'Emetteur', 'Ratio_%', 'Plafond_%', 'Ecart_%']
                            df_alert = non_conformes[alert_cols].copy()
                            
                            st.dataframe(df_alert, use_container_width=True)
                            
                            st.markdown("")
                            st.markdown("##### 📊 Détails des Dépassements")
                            
                            for _, row in non_conformes.iterrows():
                                with st.expander(f"🔴 {row['Fonds']} - {row['Emetteur']} | Écart: {row['Ecart_%']:.2f}%"):
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Montant", f"{row['Montant_MAD']:,.0f} MAD".replace(',', ' '))
                                    with col2:
                                        st.metric("Ratio", row['Ratio_%'])
                                    with col3:
                                        st.metric("Plafond", row['Plafond_%'])
                        else:
                            st.success("✅ **Conformité totale** - Tous les ratios respectent les limites CDVM")
                            st.balloons()
                    
                    with tab3:
                        st.markdown('<div class="section-header"><h2>Règle de Concentration 45%</h2></div>', unsafe_allow_html=True)
                        st.info("📖 **Règle CDVM**: La somme des émetteurs >10% ne peut dépasser 45% de l'actif net")
                        
                        if len(rule_45_df) > 0:
                            st.dataframe(rule_45_df, use_container_width=True)
                            
                            st.markdown("")
                            conformes_45 = len(rule_45_df[rule_45_df['Conformite'] == '✅'])
                            non_conformes_45 = len(rule_45_df[rule_45_df['Conformite'] == '❌'])
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("✅ Conformes", conformes_45)
                            with col2:
                                st.metric("❌ Non-conformes", non_conformes_45)
                        else:
                            st.warning("⚠️ Aucune donnée")
                    
                    with tab4:
                        st.markdown('<div class="section-header"><h2>Export & Rapports</h2></div>', unsafe_allow_html=True)
                        
                        export_dict = {
                            'Ratios': ratios_df,
                            'Regle_45': rule_45_df
                        }
                        
                        if len(non_conformes) > 0:
                            export_dict['Alertes'] = non_conformes
                        
                        summary_data = {
                            'Indicateur': [
                                'Date du contrôle',
                                'Ratios analysés',
                                'Conformes',
                                'Non-conformes',
                                'Taux conformité',
                                'Positions État',
                                'Positions privées',
                                'Fonds'
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
                        
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            for sheet_name, df in export_dict.items():
                                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
                        
                        output.seek(0)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.download_button(
                                label="📥 Télécharger Rapport Excel",
                                data=output,
                                file_name=f"controle_opcvm_{control_date.strftime('%Y%m%d')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                        
                        with col2:
                            if len(non_conformes) > 0:
                                csv = non_conformes.to_csv(index=False)
                                st.download_button(
                                    label="📥 Télécharger Alertes CSV",
                                    data=csv,
                                    file_name=f"alertes_{control_date.strftime('%Y%m%d')}.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
                        
                        st.markdown("")
                        st.info(f"""
                        **📋 Contenu du rapport**: {len(export_dict)} onglets
                        - Ratios_Complet ({len(ratios_df)} lignes)
                        - Regle_45 ({len(rule_45_df)} lignes)
                        {f"- Alertes ({len(non_conformes)} lignes)" if len(non_conformes) > 0 else ""}
                        - Synthèse
                        """)
                    
                    # SYNTHÈSE
                    st.markdown("---")
                    st.markdown('<div class="section-header"><h2><span class="section-icon">📋</span>Rapport de Synthèse</h2></div>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("##### ✅ Points Positifs")
                        st.success(f"""
                        - ✓ **{total_conformes}** ratios conformes sur **{len(ratios_df)}**
                        - ✓ Taux de conformité: **{taux_conformite:.1f}%**
                        - ✓ **{len(rule_45_df[rule_45_df['Conformite'] == '✅'])}** fonds OK règle 45%
                        - ✓ **{len(actif_net_dict)}** fonds analysés
                        """)
                    
                    with col2:
                        if total_non_conformes > 0:
                            st.markdown("##### ⚠️ Actions Requises")
                            emetteurs = ', '.join(non_conformes['Emetteur'].unique()[:5])
                            st.warning(f"""
                            - ⚠ **{total_non_conformes}** dépassements
                            - ⚠ Émetteurs: **{emetteurs}**
                            - ⚠ Régularisation nécessaire
                            - ⚠ Suivi renforcé
                            """)
                        else:
                            st.markdown("##### ✅ Conformité Totale")
                            st.success("""
                            - ✓ Aucun dépassement
                            - ✓ Conformité CDVM 100%
                            - ✓ Portfolio régulier
                            - ✓ Seuils respectés
                            """)
                    
        else:
            st.error("❌ Échec du chargement")
else:
    st.info("👆 **Pour commencer**: Chargez votre fichier Excel FOND.xlsx")
    
    with st.expander("📖 Guide d'Utilisation"):
        st.markdown("""
        ### 🎯 Mode d'Emploi
        
        **1. Chargement**
        - Uploadez votre fichier FOND.xlsx
        - Vérifiez les fonds détectés
        
        **2. Configuration** (Optionnel)
        - Ajustez les plafonds dans la sidebar
        - Définissez les actions éligibles
        - Configurez la règle 45%
        
        **3. Analyse**
        - Cliquez sur "🚀 LANCER L'ANALYSE"
        - Consultez le tableau de bord
        
        **4. Export**
        - Téléchargez le rapport Excel complet
        - Exportez les alertes en CSV
        
        ---
        
        ### 📋 Format Attendu
        
        **Structure Excel**:
        - Onglets par fonds (Action, Diversifie, OMLT, OCT, Monetaire)
        - Colonnes: ISIN, Type, Description, Quantité, Prix, Valorisation
        
        **Contrôles CDVM**:
        - ✓ Ratio par émetteur ≤ plafonds
        - ✓ Règle concentration 45%
        - ✓ Distinction public/privé
        - ✓ Actions éligibles 15%
        
        ---
        
        ### 📞 Support
        
        En cas de problème, contactez:
        **Le responsable** - Contrôle Interne CFG Bank
        """)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #9ca3af; font-size: 0.9rem; padding: 2rem 0 1rem 0;">
    <p style="margin: 0.5rem 0;"><strong>📊 Application de Contrôle Réglementaire OPCVM</strong></p>
    <p style="margin: 0.5rem 0;">Version 3.0 Premium • CFG Bank - Contrôle Interne</p>
    <p style="margin: 0.5rem 0;">Conforme CDVM Circulaire n°01-09 | Développé par Thierno Ibrahima Diallo</p>
</div>
""", unsafe_allow_html=True)
