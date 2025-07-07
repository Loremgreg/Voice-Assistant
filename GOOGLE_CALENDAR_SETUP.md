# Configuration Google Calendar pour l'Agent Vocal

Ce guide explique comment configurer l'accès à Google Calendar via un compte de service.

## 1. Création du Projet Google Cloud

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet ou sélectionnez un projet existant
3. Notez l'ID du projet

## 2. Activation de l'API Google Calendar

1. Dans la console Google Cloud, allez dans **APIs & Services** > **Library**
2. Recherchez "Google Calendar API"
3. Cliquez sur **Enable**

## 3. Création du Compte de Service

1. Allez dans **APIs & Services** > **Credentials**
2. Cliquez sur **Create Credentials** > **Service Account**
3. Remplissez les informations :
   - **Service account name** : `voice-assistant-calendar`
   - **Service account ID** : `voice-assistant-calendar`
   - **Description** : `Service account for voice assistant calendar integration`
4. Cliquez sur **Create and Continue**
5. Ignorez les rôles pour l'instant (cliquez sur **Continue**)
6. Cliquez sur **Done**

## 4. Génération de la Clé JSON

1. Dans la liste des comptes de service, cliquez sur celui que vous venez de créer
2. Allez dans l'onglet **Keys**
3. Cliquez sur **Add Key** > **Create new key**
4. Sélectionnez **JSON** et cliquez sur **Create**
5. Le fichier JSON sera téléchargé automatiquement
6. **IMPORTANT** : Gardez ce fichier en sécurité, il contient les credentials d'accès

## 5. Configuration du Calendrier

### Option A : Utiliser votre calendrier principal
1. Partagez votre calendrier principal avec le compte de service :
   - Ouvrez [Google Calendar](https://calendar.google.com/)
   - Dans la sidebar, cliquez sur les 3 points à côté de votre calendrier
   - Sélectionnez **Settings and sharing**
   - Dans **Share with specific people**, cliquez sur **Add people**
   - Ajoutez l'email du compte de service (format : `voice-assistant-calendar@your-project-id.iam.gserviceaccount.com`)
   - Donnez les permissions **Make changes to events**
   - Cliquez sur **Send**

### Option B : Créer un calendrier dédié
1. Dans Google Calendar, cliquez sur **+** à côté de **Other calendars**
2. Sélectionnez **Create new calendar**
3. Nommez-le "Cabinet Kinésithérapie" par exemple
4. Cliquez sur **Create calendar**
5. Partagez ce nouveau calendrier avec le compte de service (même procédure qu'Option A)
6. Notez l'ID du calendrier (dans les paramètres du calendrier)

## 6. Configuration de l'Application

1. Copiez le fichier JSON téléchargé dans votre projet
2. Renommez-le par exemple `google-service-account.json`
3. Mettez à jour votre fichier `.env` :

```bash
# Chemin vers le fichier de credentials
GOOGLE_SERVICE_ACCOUNT_FILE=./google-service-account.json

# ID du calendrier (optionnel, par défaut 'primary')
GOOGLE_CALENDAR_ID=primary
# OU si vous avez créé un calendrier dédié :
# GOOGLE_CALENDAR_ID=your-calendar-id@group.calendar.google.com
```

## 7. Test de la Configuration

Vous pouvez tester la configuration avec ce script Python :

```python
import os
from calendar_service import get_calendar_service
from datetime import datetime, timedelta

async def test_calendar():
    try:
        service = get_calendar_service()
        
        # Test de récupération des événements
        appointments = await service.get_appointments()
        print(f"Événements trouvés : {len(appointments)}")
        
        # Test de création d'un événement de test
        test_start = datetime.now() + timedelta(hours=1)
        test_end = test_start + timedelta(minutes=30)
        
        appointment = await service.create_appointment(
            title="Test Agent Vocal",
            start_datetime=test_start,
            end_datetime=test_end,
            description="Test de l'intégration Google Calendar"
        )
        
        print(f"Événement de test créé : {appointment['id']}")
        
        # Nettoyage : supprimer l'événement de test
        await service.cancel_appointment(appointment['id'])
        print("Événement de test supprimé")
        
    except Exception as e:
        print(f"Erreur : {e}")

# Exécuter le test
import asyncio
asyncio.run(test_calendar())
```

## 8. Sécurité

⚠️ **Important** :
- Ne commitez jamais le fichier JSON dans votre repository Git
- Ajoutez `*.json` à votre `.gitignore`
- Stockez le fichier de credentials en sécurité
- En production, utilisez des variables d'environnement ou un service de gestion de secrets

## 9. Dépannage

### Erreur "Permission denied"
- Vérifiez que le calendrier est bien partagé avec le compte de service
- Vérifiez que les permissions "Make changes to events" sont accordées

### Erreur "Calendar not found"
- Vérifiez l'ID du calendrier dans la variable `GOOGLE_CALENDAR_ID`
- Utilisez `primary` pour le calendrier principal

### Erreur "Service account file not found"
- Vérifiez le chemin dans `GOOGLE_SERVICE_ACCOUNT_FILE`
- Assurez-vous que le fichier existe et est accessible

### Erreur "API not enabled"
- Vérifiez que l'API Google Calendar est activée dans Google Cloud Console
- Attendez quelques minutes après l'activation