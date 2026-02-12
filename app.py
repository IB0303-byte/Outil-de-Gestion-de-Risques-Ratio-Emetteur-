"""
PROTOTYPE - Contrôle des ratios émetteurs OPCVM
CDVM Circulaire n°01-09 - Article 6
Version ULTRA CORRIGÉE - Gestion des erreurs + Debug
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import re

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
        value = value.replace(' ', '')  # Espace insécable
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
# CSS
# =============================================================================

st.markdown("""
<style>
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
    .stApp {
        background-color: #f5f7fa;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# EN-TÊTE
# =============================================================================

st.markdown("""
<div class="main-header">
    <h1 style="color: white; margin: 0;">📊 Contrôle des ratios émetteurs OPCVM</h1>
    <p style="color: white; opacity: 0.9; margin: 0;">CDVM - Circulaire n°01-09</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR - PARAMÈTRES
# =============================================================================

with st.sidebar:
    st.markdown("### ⚙️ Paramètres")
    
    # Plafonds
    plafond_etat = st.number_input("État (%)", 0, 100, 100) / 100
    plafond_action = st.number_input("Actions éligibles 15% (%)", 0, 100, 15) / 100
    plafond_std = st.number_input("Plafond standard (%)", 0, 100, 10) / 100
    
    # Actions éligibles
    actions_15 = st.text_input("Actions éligibles 15%", "ATW, IAM, BCP, BOA")
    actions_list = [a.strip() for a in actions_15.split(',') if a.strip()]
    
    # Seuil 45%
    seuil_45 = st.number_input("Seuil règle 45% (%)", 0, 100, 45) / 100
    
    # Table émetteurs
    issuer_file = st.file_uploader("Table émetteurs (CSV)", type=['csv'])
    issuer_table = pd.read_csv(issuer_file) if issuer_file else create_default_issuer_table()
    
    # Bouton calcul
    calculate = st.button("🚀 LANCER LE CALCUL", type="primary", use_container_width=True)

# =============================================================================
# CHARGEMENT DU FICHIER
# =============================================================================

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📂 Fichier de données")
    uploaded_file = st.file_uploader("Charger FOND.xlsx", type=['xlsx'])

# =============================================================================
# EXÉCUTION PRINCIPALE
# =============================================================================

if uploaded_file:
    with st.spinner("Chargement..."):
        portfolio, actif_net_dict = load_portfolio(uploaded_file)
        
        if portfolio is not None and actif_net_dict:
            
            # Afficher les fonds
            with col2:
                st.markdown("### 💼 Fonds détectés")
                cols = st.columns(len(actif_net_dict))
                for i, (fonds, actif) in enumerate(actif_net_dict.items()):
                    with cols[i]:
                        st.metric(fonds, f"{actif:,.0f} MAD".replace(',', ' '))
            
            st.success(f"✅ {len(portfolio)} lignes chargées")
            
            # Aperçu des données
            with st.expander("👁️ Aperçu des données brutes"):
                st.dataframe(portfolio.head(10), use_container_width=True)
            
            # CALCUL
            if calculate:
                with st.spinner("🔍 Calcul en cours..."):
                    
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
                    # INDICATEURS
                    # -----------------------------------------------------------------
                    
                    total_conformes = len(ratios_df[ratios_df['Conformite'] == '✅'])
                    total_non_conformes = len(ratios_df[ratios_df['Conformite'] == '❌'])
                    taux_conformite = total_conformes / len(ratios_df) * 100
                    
                    st.markdown("---")
                    st.markdown("### 📊 Indicateurs clés")
                    
                    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
                    
                    with kpi1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4 style="margin:0;">📋 Ratios</h4>
                            <p style="font-size: 2rem; font-weight: bold; margin:0;">{len(ratios_df)}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with kpi2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4 style="margin:0;">✅ Conformes</h4>
                            <p style="font-size: 2rem; font-weight: bold; color:#28a745; margin:0;">{total_conformes}</p>
                            <p>{taux_conformite:.1f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with kpi3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4 style="margin:0;">❌ Non-conformes</h4>
                            <p style="font-size: 2rem; font-weight: bold; color:#dc3545; margin:0;">{total_non_conformes}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with kpi4:
                        nb_etat = len(ratios_df[ratios_df['Emetteur'] == 'État marocain'])
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4 style="margin:0;">🏛️ État</h4>
                            <p style="font-size: 2rem; font-weight: bold; margin:0;">{nb_etat}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with kpi5:
                        nb_prive = len(ratios_df[ratios_df['Type'] == 'privé'])
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4 style="margin:0;">🏢 Privé</h4>
                            <p style="font-size: 2rem; font-weight: bold; margin:0;">{nb_prive}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # -----------------------------------------------------------------
                    # ONGLETS
                    # -----------------------------------------------------------------
                    
                    tab1, tab2, tab3, tab4 = st.tabs([
                        "📊 Ratios", 
                        "⚠️ Alertes", 
                        "🎯 Règle 45%",
                        "📤 Export"
                    ])
                    
                    with tab1:
                        st.markdown("### 📋 Ratios par fonds/émetteur")
                        
                        display_cols = ['Fonds', 'Emetteur', 'Montant_MAD', 'Ratio_%', 
                                       'Plafond_%', 'Conformite', 'Ecart_%']
                        
                        df_show = ratios_df[display_cols].copy()
                        df_show['Montant_MAD'] = df_show['Montant_MAD'].apply(
                            lambda x: f"{x:,.0f}".replace(',', ' ')
                        )
                        df_show['Ecart_%'] = df_show['Ecart_%'].apply(lambda x: f"{x:.2f}%")
                        
                        st.dataframe(df_show, use_container_width=True, height=500)
                    
                    with tab2:
                        st.markdown("### ⚠️ Non-conformités")
                        
                        non_conformes = ratios_df[ratios_df['Conformite'] == '❌']
                        
                        if len(non_conformes) > 0:
                            st.error(f"🚨 {len(non_conformes)} non-conformité(s) détectée(s)")
                            st.dataframe(non_conformes[display_cols], use_container_width=True)
                        else:
                            st.success("✅ Aucune non-conformité")
                    
                    with tab3:
                        st.markdown("### 🎯 Règle des 45%")
                        st.info("Somme des émetteurs actions > 10% ≤ 45% de l'actif net")
                        
                        if len(rule_45_df) > 0:
                            st.dataframe(rule_45_df, use_container_width=True)
                        else:
                            st.warning("Aucune donnée pour la règle 45%")
                    
                    with tab4:
                        st.markdown("### 📤 Export")
                        
                        # Préparer l'export
                        export_dict = {
                            'Ratios': ratios_df,
                            'Regle_45': rule_45_df
                        }
                        
                        if len(non_conformes) > 0:
                            export_dict['Alertes'] = non_conformes
                        
                        # Export Excel
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            for sheet_name, df in export_dict.items():
                                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
                        
                        output.seek(0)
                        
                        st.download_button(
                            label="📥 Télécharger (Excel)",
                            data=output,
                            file_name="controle_emetteurs.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    
                    # -----------------------------------------------------------------
                    # RAPPORT
                    # -----------------------------------------------------------------
                    
                    st.markdown("---")
                    st.markdown("### 📋 Rapport")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**✅ Points positifs**")
                        st.markdown(f"- {total_conformes} ratios conformes")
                        st.markdown(f"- {len(rule_45_df[rule_45_df['Conformite'] == '✅'])} fonds respectent la règle 45%")
                    
                    with col2:
                        if total_non_conformes > 0:
                            st.markdown("**⚠️ Points d'attention**")
                            st.markdown(f"- {total_non_conformes} non-conformités")
                            st.markdown(f"- Émetteurs: {', '.join(non_conformes['Emetteur'].unique()[:3])}")
                    
        else:
            st.error("❌ Échec du chargement - Voir sidebar pour les détails")
else:
    st.info("👈 Chargez votre fichier FOND.xlsx pour commencer")
