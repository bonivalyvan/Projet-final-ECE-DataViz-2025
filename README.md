# Projet-final-ECE-DataViz-2025

# 🎯 RETAIL ANALYTICS DASHBOARD

**Une application Streamlit pour piloter vos décisions marketing par les données.**

---

## 📋 TABLE DES MATIÈRES

1. [À Propos](#à-propos)
2. [Installation](#installation)
3. [Lancement Rapide](#lancement-rapide)
4. [Structure du Projet](#structure-du-projet)
5. [Utilisation](#utilisation)
6. [Documentation](#documentation)

---

## 🎯 À Propos

Cette application permet à votre **équipe marketing** de :

✅ **Diagnostiquer** la rétention des clients par cohorte d'acquisition  
✅ **Segmenter** la base client avec RFM (Récence, Fréquence, Montant)  
✅ **Estimer** la Customer Lifetime Value (CLV) via deux approches :
- Empirique (données réelles)
- Formule fermée (modèle mathématique)

✅ **Simuler** l'impact business de scénarios (remise, rétention, marge)  
✅ **Exporter** des listes activables pour votre CRM/emailing  

### 📊 Données
- **Source** : Online Retail II (UCI Machine Learning Repository)
- **Période** : Décembre 2009 - Décembre 2011 (~1,07M transactions)
- **Géographie** : Détaillant UK avec clients mondiaux

---

## 🚀 Installation

### Prérequis
- Python 3.8+ ([télécharger](https://www.python.org/downloads/))
- Git (optionnel, pour cloner le repo)

### Étape 1 : Cloner/Télécharger le Projet

```bash
# Via Git
git clone https://github.com/bonivalyvan/Projet-final-ECE-DataViz-2025.git
cd Projet-final-ECE-DataViz-2025

# Ou manuellement via ZIP
# Extaire le dossier à votre emplacement préféré
```

### Étape 2 : Créer un Environnement Virtuel (Recommandé)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Étape 3 : Installer les Dépendances

```bash
pip install -r requirement.txt
```

**Contenu du requirement.txt** :
```plaintext
streamlit>=1.0.0
pandas>=1.3.0
numpy>=1.20.0
plotly>=5.0.0
openpyxl>=3.6.0  # Pour export Excel
matplotlib>=3.3.0
```

### Étape 4 : Préparer les Données

Téléchargez **Online Retail II** du [UCI Repository](https://archive.ics.uci.edu/dataset/352/online+retail+ii) et placez-le :

```
Projet-final-ECE-DataViz-2025/
├── data/
│   └── raw/
│       └── online_retail_II.xlsx  ← Placer ici
├── app/
│   ├── streamlit_app.py
│   ├── pages/
│   └── utils/
└── README.md
```

**Colonnes attendues dans le fichier Excel** :
- Invoice
- StockCode
- Description
- Quantity
- InvoiceDate
- Price
- Customer ID
- Country

---

## ▶️ Lancement Rapide

### Démarrer l'Application

```bash
cd app/
streamlit run streamlit_app.py
```

**Ou directement depuis le dossier racine** :
```bash
streamlit run app/streamlit_app.py
```

### Accéder à l'App

L'app s'ouvrira automatiquement à :
```
http://localhost:8501
```

Si ce n'est pas le cas, copiez le lien affiché dans le terminal.

### Configuration Streamlit (Optionnel)

Créez `.streamlit/config.toml` à la racine pour personnaliser :

```toml
[theme]
primaryColor = "#4F46E5"
backgroundColor = "#F3F4F6"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#1E293B"
font = "sans serif"

[client]
showErrorDetails = false
toolbarMode = "minimal"

[server]
port = 8501
headless = true
```

---

## 📁 Structure du Projet

```
Projet-final-ECE-DataViz-2025/
│
├── 📄 README.md (ce fichier)
├── 📄 AUDIT_RECOMMANDATIONS.md (audit complet)
├── 📄 GUIDE_UTILISATEUR.md (guide marketing)
├── 📄 GUIDE_TECHNIQUE.md (guide développeur)
├── 📄 requirement.txt (dépendances)
│
├── 📁 app/
│   ├── 📄 streamlit_app.py (entrée principale)
│   │
│   ├── 📁 pages/ (pages multipage)
│   │   ├── 1_kpis_overview.py
│   │   ├── 2_cohortes_diagnostiquer.py
│   │   ├── 3_segments_prioriser.py
│   │   ├── 4_scenarios_simuler.py
│   │   └── 5_plan_action_exporter.py
│   │
│   └── 📁 utils/ (utilitaires réutilisables)
│       ├── __init__.py
│       ├── data_loader.py (chargement + filtres)
│       ├── rfm_calculator.py (calcul RFM)
│       ├── cohort_calculator.py (calcul cohortes)
│       ├── visualization.py (styles + graphiques)
│       └── kpi_helpers.py (✨ NEW - définitions KPI)
│
├── 📁 data/
│   └── raw/
│       └── online_retail_II.xlsx (à télécharger)
│
└── 📁 .streamlit/
    └── config.toml (configuration optionnelle)
```

### Explication des Fichiers Clés

| Fichier | Rôle |
|---------|------|
| **streamlit_app.py** | Entrée principale (structure page, navigation) |
| **data_loader.py** | Chargement Excel, filtres (date, pays, retours) |
| **rfm_calculator.py** | Calcul des scores RFM et segmentation |
| **cohort_calculator.py** | Construction matrice rétention par cohorte |
| **visualization.py** | Styles Streamlit, fonctions graphiques, CSS |
| **kpi_helpers.py** | ✨ Définitions centralisées des KPI + infobulles |

---

## 📖 Utilisation

### 🎯 Workflow Typique

1. **📊 Accueil/KPIs Overview** :
   - Voir snapshot de l'état actuel
   - Vérifier les tendances mensuelles
   - Observer la distribution RFM

2. **📈 Cohortes Diagnostiquer** :
   - Heatmap rétention : quelles cohortes décrochent?
   - Focus cohorte spécifique pour investigate
   - Comparaison B2B vs B2C

3. **🎯 Segments Prioriser** :
   - Voir la répartition des segments
   - Identifier champions vs. à risque
   - Lire guide CRM pour chaque segment

4. **🎮 Scénarios Simuler** :
   - Tester impact d'une campagne (rétention +5%)
   - Calculer ROI avant budget
   - Comparer scénarios pour décider

5. **📥 Exporter** :
   - Créer liste activable (CSV ou Excel)
   - Importer dans CRM/emailing
   - Suivre guide CRM pour messages

### 🔍 Filtres Utiles

**Pour analyser uniquement le cœur de métier UK B2C** :
- Période : 12 derniers mois
- Pays : United Kingdom
- Retours : Exclure

**Pour voir l'impact des retours** :
- Même période/pays
- Mode Retours : Inclure → puis Exclure (comparer)

**Pour étudier une cohorte spécifique** :
- Période : 2010-01 à 2010-01 (janvier 2010)
- Voir PAGE 2 avec focus sur cette cohorte

---

## 📚 Documentation

### Pour les Utilisateurs Marketing
👉 **Lire** : `GUIDE_UTILISATEUR.md`

- Comment naviguer l'app
- Interpréter chaque graphique
- Cas d'usage pratiques
- Glossaire des termes

### Pour les Développeurs
👉 **Lire** : `GUIDE_TECHNIQUE.md`

- Détail des modifications
- Architecture du code
- Bonnes pratiques implémentées
- Prochaines étapes d'amélioration

### Audit Complet
👉 **Lire** : `AUDIT_RECOMMANDATIONS.md`

- Évaluation vs exigences du projet
- Points forts et faibles
- Recommandations futures
- Statut production-ready

---

## ⚙️ Commandes Utiles

### Lancer l'App
```bash
streamlit run app/streamlit_app.py
```

### Recharger les Pages
Dans Streamlit : Appuyez sur **R** ou cliquez ⟳ en haut à droite

### Arrêter l'App
```bash
# Dans terminal : Ctrl+C
```

### Forcer la Réinitialisation du Cache
```bash
streamlit cache clear
```

### Mode Développement (Log Verbose)
```bash
streamlit run app/streamlit_app.py --logger.level=debug
```

---

## 🐛 Dépannage

### ❌ "Fichier online_retail_II.xlsx introuvable"
**Solution** : Télécharger depuis [UCI Repository](https://archive.ics.uci.edu/dataset/352/online+retail+ii) et placer dans `data/raw/`

### ❌ "ModuleNotFoundError: No module named 'streamlit'"
**Solution** : Vérifier que l'environnement virtuel est activé et `pip install -r requirement.txt`

### ❌ "Les graphiques sont vides"
**Solution** : Les filtres sont trop restrictifs. Élargir la période ou les pays.

### ❌ "AttributeError: 'DataFrame' object has no attribute 'map'"
**Solution** : Mise à jour pandas requise. Faire `pip install --upgrade pandas`

### ❌ Export PNG ne fonctionne pas
**Solution** : Installer `kaleido` avec `pip install kaleido`

---

## 🔐 Sécurité des Données

- ✅ Les données ne sont PAS envoyées en ligne
- ✅ Tout se passe localement (votre ordinateur)
- ✅ Pas d'authentification requise (environnement interne)
- ✅ Exports en CSV/Excel (format standard, pas cloud)

---

## 🤝 Support

Pour des questions ou bugs :
1. Consultez les 3 guides (utilisateur, technique, audit)
2. Vérifiez la section "Dépannage" ci-dessus
3. Contactez l'équipe analytics

---

## 📈 Roadmap Futur

- [ ] **Court terme** : Export PNG, filtre granularité temps
- [ ] **Moyen terme** : Dashboard historique, alertes automatiques
- [ ] **Long terme** : Prédictions ML, API REST, mobile responsive

---

## 📝 Licence & Crédits

- **Données** : [UCI Online Retail II Dataset](https://archive.ics.uci.edu/dataset/352/online+retail+ii)
- **Framework** : [Streamlit](https://streamlit.io/)
- **Visualisations** : [Plotly](https://plotly.com/)
- **Auteur** : Équipe Analytics ECE 2025

---

## 📞 Contact

**Questions sur l'app?**
- 📖 Consultez `GUIDE_UTILISATEUR.md`

**Questions techniques?**
- 📖 Consultez `GUIDE_TECHNIQUE.md`

**Feedback général?**
- 📋 Consultez `AUDIT_RECOMMANDATIONS.md`

---

**Version** : 1.1 - Production Ready  
**Dernière mise à jour** : 28 Novembre 2025  




