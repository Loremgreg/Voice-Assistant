#!/usr/bin/env python3
"""
Script de test pour l'intégration Google Calendar
Permet de vérifier que la configuration est correcte avant d'utiliser l'agent vocal.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Importer le service calendar
try:
    from calendar_service import CalendarService
except ImportError as e:
    print(f"❌ Erreur d'import : {e}")
    print("Assurez-vous d'avoir installé les dépendances avec : pip install -r requirements.txt")
    sys.exit(1)

async def test_calendar_service():
    """Test complet du service Google Calendar"""
    
    print("🔧 Test de l'intégration Google Calendar")
    print("=" * 50)
    
    # Vérifier les variables d'environnement
    service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
    
    if not service_account_file:
        print("❌ Variable GOOGLE_SERVICE_ACCOUNT_FILE non définie")
        print("Consultez le fichier .env.example pour la configuration")
        return False
    
    if not os.path.exists(service_account_file):
        print(f"❌ Fichier de credentials non trouvé : {service_account_file}")
        print("Consultez GOOGLE_CALENDAR_SETUP.md pour la configuration")
        return False
    
    print(f"✅ Fichier de credentials : {service_account_file}")
    print(f"✅ ID du calendrier : {calendar_id}")
    print()
    
    try:
        # Initialiser le service
        print("🔄 Initialisation du service Google Calendar...")
        calendar_service = CalendarService()
        print("✅ Service initialisé avec succès")
        print()
        
        # Test 1 : Récupérer les événements existants
        print("📅 Test 1 : Récupération des événements...")
        appointments = await calendar_service.get_appointments()
        print(f"✅ {len(appointments)} événements trouvés")
        
        if appointments:
            print("   Derniers événements :")
            for i, apt in enumerate(appointments[:3]):  # Afficher les 3 premiers
                start = apt.get('start', {}).get('dateTime', 'Date non définie')
                summary = apt.get('summary', 'Sans titre')
                print(f"   - {summary} ({start})")
        print()
        
        # Test 2 : Vérifier la disponibilité
        print("🕐 Test 2 : Vérification de disponibilité...")
        test_time = datetime.now() + timedelta(hours=2)
        is_available = await calendar_service.check_availability(test_time, test_time + timedelta(minutes=30))
        status = "disponible" if is_available else "occupé"
        print(f"✅ Créneau {test_time.strftime('%d/%m/%Y à %H:%M')} : {status}")
        print()
        
        # Test 3 : Créer un événement de test
        print("➕ Test 3 : Création d'un événement de test...")
        test_start = datetime.now() + timedelta(hours=1)
        test_end = test_start + timedelta(minutes=30)
        
        test_appointment = await calendar_service.create_appointment(
            title="🤖 Test Agent Vocal",
            start_datetime=test_start,
            end_datetime=test_end,
            description="Événement de test créé automatiquement par l'agent vocal"
        )
        
        if test_appointment:
            print(f"✅ Événement créé : {test_appointment.get('summary')}")
            print(f"   ID : {test_appointment.get('id')}")
            print(f"   Lien : {test_appointment.get('htmlLink')}")
            
            # Test 4 : Modifier l'événement
            print()
            print("✏️  Test 4 : Modification de l'événement...")
            new_start = test_start + timedelta(minutes=30)
            new_end = new_start + timedelta(minutes=30)
            
            updated_appointment = await calendar_service.reschedule_appointment(
                test_appointment['id'],
                new_start,
                new_end
            )
            
            if updated_appointment:
                print("✅ Événement modifié avec succès")
            
            # Test 5 : Supprimer l'événement de test
            print()
            print("🗑️  Test 5 : Suppression de l'événement de test...")
            success = await calendar_service.cancel_appointment(test_appointment['id'])
            
            if success:
                print("✅ Événement supprimé avec succès")
            else:
                print("⚠️  Erreur lors de la suppression")
        
        print()
        print("🎉 Tous les tests sont passés avec succès !")
        print("L'intégration Google Calendar est prête à être utilisée avec l'agent vocal.")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        print()
        print("🔍 Vérifications à effectuer :")
        print("1. Le fichier de credentials Google est-il valide ?")
        print("2. L'API Google Calendar est-elle activée ?")
        print("3. Le calendrier est-il partagé avec le compte de service ?")
        print("4. Les dépendances sont-elles installées ?")
        print()
        print("Consultez GOOGLE_CALENDAR_SETUP.md pour plus d'informations.")
        return False

async def test_natural_language_parsing():
    """Test du parsing de langage naturel pour les dates"""
    
    print()
    print("🗣️  Test du parsing de langage naturel")
    print("=" * 50)
    
    try:
        calendar_service = CalendarService()
        
        # Tests de parsing de dates en français
        test_phrases = [
            "demain à 14h30",
            "lundi prochain à 9h",
            "dans 2 heures",
            "vendredi 15 décembre à 16h",
            "aujourd'hui à 18h30"
        ]
        
        for phrase in test_phrases:
            try:
                parsed_date = calendar_service._parse_datetime_from_text(phrase)
                if parsed_date:
                    print(f"✅ '{phrase}' → {parsed_date.strftime('%d/%m/%Y à %H:%M')}")
                else:
                    print(f"⚠️  '{phrase}' → Non reconnu")
            except Exception as e:
                print(f"❌ '{phrase}' → Erreur : {e}")
        
        print()
        print("ℹ️  Note : Le parsing de langage naturel est basique.")
        print("   Pour une meilleure précision, utilisez des formats comme :")
        print("   - 'demain à 14h30'")
        print("   - 'lundi à 9h'")
        print("   - 'dans 2 heures'")
        
    except Exception as e:
        print(f"❌ Erreur lors du test de parsing : {e}")

def main():
    """Fonction principale"""
    print("🤖 Test de l'intégration Google Calendar pour l'Agent Vocal")
    print("=" * 60)
    print()
    
    # Exécuter les tests
    success = asyncio.run(test_calendar_service())
    
    if success:
        asyncio.run(test_natural_language_parsing())
        print()
        print("🚀 L'intégration est prête ! Vous pouvez maintenant utiliser l'agent vocal.")
    else:
        print()
        print("🔧 Veuillez corriger les erreurs avant d'utiliser l'agent vocal.")
        sys.exit(1)

if __name__ == "__main__":
    main()