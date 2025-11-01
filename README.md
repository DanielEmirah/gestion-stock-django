# 🏪 Gestion de Stock - Application Django

Une application web complète de gestion de stock développée avec Django, Bootstrap 5 et SQLite/PostgreSQL.

## 🚀 Fonctionnalités

### Gestion des Données
- ✅ **Produits** avec catégories et fournisseurs
- ✅ **Mouvements de stock** (entrées/sorties) avec historique
- ✅ **Calcul automatique** des stocks et valeurs
- ✅ **Alertes** pour stocks faibles et ruptures

### Interface Utilisateur
- ✅ **Tableau de bord** avec statistiques en temps réel
- ✅ **Système d'authentification** sécurisé

### Validation des Données
- ✅ **Stock cohérent** (pas de sorties supérieures au stock)
- ✅ **Contrôle d'intégrité** des données

## 🛠 Technologies

- **Backend**: Django, Python
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Base de données**: SQLite
- **Authentification**: Système Django

## 📦 Installation

```bash
# Cloner le projet
git clone https://github.com/VOTRE_NOM_UTILISATEUR/gestion-stock-django.git](https://github.com/DanielEmirah/gestion-stock-django.git
cd gestion-stock-django

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer la base de données
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
