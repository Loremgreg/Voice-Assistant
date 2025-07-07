# Agent Vocal avec Intégration Google Calendar

Un agent vocal intelligent basé sur LiveKit qui peut gérer votre calendrier Google par la voix.

## 🎯 Fonctionnalités

- **Prise de rendez-vous** : "Peux-tu me prendre un rendez-vous demain à 14h30 ?"
- **Vérification de disponibilité** : "Suis-je libre vendredi à 16h ?"
- **Reprogrammation** : "Peux-tu déplacer mon rendez-vous de demain à après-demain ?"
- **Annulation** : "Annule mon rendez-vous de cet après-midi"
- **Consultation** : "Quels sont mes rendez-vous de la semaine ?"

## 🏗️ Architecture

```
Voice-Assistant/
├── calendar_service.py      # Service Google Calendar
├── prompts.py              # Outils de l'agent vocal
├── requirements.txt        # Dépendances Python
├── .env.example           # Variables d'environnement
├── GOOGLE_CALENDAR_SETUP.md # Guide de configuration
├── test_calendar_integration.py # Script de test
└── README.md              # Ce fichier
```

## 🚀 Installation Rapide

### 1. Cloner et installer les dépendances

```bash
# Installer les dépendances
pip install -r requirements.txt

# Copier le fichier d'environnement
cp .env.example .env
```

### 2. Configuration Google Calendar

Suivez le guide détaillé dans [`GOOGLE_CALENDAR_SETUP.md`](GOOGLE_CALENDAR_SETUP.md) pour :
- Créer un projet Google Cloud
- Activer l'API Google Calendar
- Créer un compte de service
- Télécharger le fichier de credentials JSON
- Configurer les permissions du calendrier

### 3. Configuration des variables d'environnement

Éditez le fichier `.env` :

```bash
# Chemin vers le fichier de credentials Google
GOOGLE_SERVICE_ACCOUNT_FILE=./google-service-account.json

# ID du calendrier (optionnel, par défaut 'primary')
GOOGLE_CALENDAR_ID=primary
```

### 4. Test de l'intégration

```bash
python test_calendar_integration.py
```

Si tous les tests passent, l'intégration est prête !

## 🎤 Utilisation avec l'Agent Vocal

L'agent vocal comprend les demandes en langage naturel :

### Exemples de commandes vocales

**Prise de rendez-vous :**
- "Peux-tu me prendre un rendez-vous demain à 14h30 avec Monsieur Dupont ?"
- "Réserve-moi un créneau lundi prochain à 9h pour une séance de kiné"

**Vérification de disponibilité :**
- "Suis-je libre vendredi à 16h ?"
- "Est-ce que j'ai quelque chose de prévu cet après-midi ?"

**Consultation des rendez-vous :**
- "Quels sont mes rendez-vous aujourd'hui ?"
- "Montre-moi mon planning de la semaine"

**Modification de rendez-vous :**
- "Peux-tu déplacer mon rendez-vous de demain à après-demain à la même heure ?"
- "Reprogramme le rendez-vous de 14h à 15h30"

**Annulation :**
- "Annule mon rendez-vous de cet après-midi"
- "Supprime le rendez-vous avec Madame Martin"

## 🔧 Architecture Technique

### CalendarService (`calendar_service.py`)

Service principal qui gère toutes les interactions avec l'API Google Calendar :

```python
class CalendarService:
    async def create_appointment(title, start_datetime, end_datetime, description=None)
    async def check_availability(start_datetime, end_datetime)
    async def get_appointments(days_ahead=7)
    async def cancel_appointment(event_id)
    async def reschedule_appointment(event_id, new_start, new_end)
```

### Outils de l'Agent (`prompts.py`)

Fonctions intégrées à l'agent vocal LiveKit :

- [`book_appointment()`](prompts.py:45) : Réservation de rendez-vous
- [`reschedule_appointment()`](prompts.py:85) : Reprogrammation
- [`cancel_appointment()`](prompts.py:125) : Annulation
- [`check_availability()`](prompts.py:165) : Vérification de disponibilité
- [`get_appointments()`](prompts.py:185) : Consultation du planning

### Authentification

- **Service Account** : Authentification via fichier JSON
- **Permissions** : Accès en lecture/écriture au calendrier partagé
- **Sécurité** : Credentials stockés localement, non versionnés

## 🛠️ Développement

### Structure du Code

```python
# Exemple d'utilisation du service
from calendar_service import CalendarService
from datetime import datetime, timedelta

calendar_service = CalendarService()

# Créer un rendez-vous
appointment = await calendar_service.create_appointment(
    title="Consultation Kinésithérapie",
    start_datetime=datetime.now() + timedelta(hours=24),
    end_datetime=datetime.now() + timedelta(hours=24, minutes=30),
    description="Séance de rééducation"
)
```

### Tests

```bash
# Test complet de l'intégration
python test_calendar_integration.py

# Test spécifique d'une fonction
python -c "
import asyncio
from calendar_service import CalendarService
async def test():
    service = CalendarService()
    appointments = await service.get_appointments()
    print(f'Rendez-vous trouvés: {len(appointments)}')
asyncio.run(test())
"
```

### Debugging

Activez les logs détaillés :

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📋 Dépendances

- **LiveKit Agents** : Framework pour agents vocaux
- **Google API Client** : Intégration Google Calendar
- **Python-dotenv** : Gestion des variables d'environnement
- **Asyncio** : Programmation asynchrone

Voir [`requirements.txt`](requirements.txt) pour la liste complète.

## 🔒 Sécurité

### Bonnes Pratiques

- ✅ Fichier de credentials non versionné (`.gitignore`)
- ✅ Variables d'environnement pour la configuration
- ✅ Authentification par Service Account
- ✅ Permissions minimales sur le calendrier

### Variables Sensibles

```bash
# À ne JAMAIS committer
google-service-account.json
.env
```

## 🐛 Dépannage

### Erreurs Courantes

**"Permission denied"**
```
Solution : Vérifiez que le calendrier est partagé avec le compte de service
```

**"Calendar not found"**
```
Solution : Vérifiez l'ID du calendrier dans GOOGLE_CALENDAR_ID
```

**"Service account file not found"**
```
Solution : Vérifiez le chemin dans GOOGLE_SERVICE_ACCOUNT_FILE
```

**"API not enabled"**
```
Solution : Activez l'API Google Calendar dans Google Cloud Console
```

### Logs de Debug

```python
# Activer les logs détaillés
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Documentation

- [`GOOGLE_CALENDAR_SETUP.md`](GOOGLE_CALENDAR_SETUP.md) : Configuration Google Calendar
- [`calendar_service.py`](calendar_service.py) : Documentation du service
- [`prompts.py`](prompts.py) : Outils de l'agent vocal

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour toute question ou problème :

1. Consultez la section [Dépannage](#-dépannage)
2. Vérifiez les [Issues GitHub](../../issues)
3. Exécutez le script de test : `python test_calendar_integration.py`

---

**Fait avec ❤️ pour simplifier la gestion de calendrier par la voix**
