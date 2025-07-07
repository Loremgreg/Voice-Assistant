"""
Service Google Calendar pour l'agent vocal.
Utilise un compte de service Google pour l'authentification.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class GoogleCalendarService:
    """Service pour interagir avec Google Calendar via un compte de service."""
    
    def __init__(self):
        self.service = None
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialise le service Google Calendar avec les credentials du compte de service."""
        try:
            # Récupération du chemin vers le fichier de credentials
            credentials_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
            if not credentials_path:
                raise ValueError("GOOGLE_SERVICE_ACCOUNT_FILE environment variable not set")
            
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"Service account file not found: {credentials_path}")
            
            # Chargement des credentials
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            
            # Construction du service
            self.service = build('calendar', 'v3', credentials=credentials)
            logger.info("Google Calendar service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {e}")
            raise
    
    async def create_appointment(
        self, 
        title: str,
        start_datetime: datetime,
        end_datetime: datetime,
        description: str = "",
        attendee_email: str = None
    ) -> Dict[str, Any]:
        """
        Crée un rendez-vous dans Google Calendar.
        
        Args:
            title: Titre du rendez-vous
            start_datetime: Date et heure de début
            end_datetime: Date et heure de fin
            description: Description du rendez-vous
            attendee_email: Email du patient (optionnel)
        
        Returns:
            Dict contenant les détails du rendez-vous créé
        """
        try:
            # Construction de l'événement
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'Europe/Paris',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'Europe/Paris',
                },
            }
            
            # Ajout de l'invité si fourni
            if attendee_email:
                event['attendees'] = [{'email': attendee_email}]
            
            # Création de l'événement
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            logger.info(f"Appointment created successfully: {created_event.get('id')}")
            
            return {
                'id': created_event.get('id'),
                'title': created_event.get('summary'),
                'start': created_event.get('start', {}).get('dateTime'),
                'end': created_event.get('end', {}).get('dateTime'),
                'html_link': created_event.get('htmlLink'),
                'status': 'created'
            }
            
        except HttpError as e:
            logger.error(f"HTTP error creating appointment: {e}")
            if e.resp.status == 409:
                raise ValueError("Ce créneau est déjà occupé")
            elif e.resp.status == 403:
                raise ValueError("Permissions insuffisantes pour créer le rendez-vous")
            else:
                raise ValueError(f"Erreur lors de la création du rendez-vous: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error creating appointment: {e}")
            raise ValueError("Une erreur inattendue s'est produite lors de la création du rendez-vous")
    
    async def check_availability(
        self, 
        start_datetime: datetime, 
        end_datetime: datetime
    ) -> bool:
        """
        Vérifie si un créneau est disponible.
        
        Args:
            start_datetime: Date et heure de début du créneau
            end_datetime: Date et heure de fin du créneau
        
        Returns:
            True si le créneau est libre, False sinon
        """
        try:
            # Requête freebusy pour vérifier la disponibilité
            freebusy_query = {
                'timeMin': start_datetime.isoformat(),
                'timeMax': end_datetime.isoformat(),
                'items': [{'id': self.calendar_id}]
            }
            
            result = self.service.freebusy().query(body=freebusy_query).execute()
            busy_times = result.get('calendars', {}).get(self.calendar_id, {}).get('busy', [])
            
            # Si pas de créneaux occupés, le créneau est libre
            is_available = len(busy_times) == 0
            
            logger.info(f"Availability check: {start_datetime} - {end_datetime} = {'Available' if is_available else 'Busy'}")
            return is_available
            
        except HttpError as e:
            logger.error(f"HTTP error checking availability: {e}")
            # En cas d'erreur, on considère le créneau comme occupé par sécurité
            return False
        
        except Exception as e:
            logger.error(f"Unexpected error checking availability: {e}")
            return False
    
    async def get_appointments(
        self, 
        start_date: datetime = None, 
        end_date: datetime = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Récupère la liste des rendez-vous.
        
        Args:
            start_date: Date de début de la recherche (par défaut: aujourd'hui)
            end_date: Date de fin de la recherche (par défaut: dans 7 jours)
            max_results: Nombre maximum de résultats
        
        Returns:
            Liste des rendez-vous
        """
        try:
            # Dates par défaut
            if not start_date:
                start_date = datetime.now()
            if not end_date:
                end_date = start_date + timedelta(days=7)
            
            # Récupération des événements
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_date.isoformat(),
                timeMax=end_date.isoformat(),
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Formatage des résultats
            appointments = []
            for event in events:
                appointment = {
                    'id': event.get('id'),
                    'title': event.get('summary', 'Sans titre'),
                    'start': event.get('start', {}).get('dateTime'),
                    'end': event.get('end', {}).get('dateTime'),
                    'description': event.get('description', ''),
                    'status': event.get('status', 'confirmed')
                }
                appointments.append(appointment)
            
            logger.info(f"Retrieved {len(appointments)} appointments")
            return appointments
            
        except HttpError as e:
            logger.error(f"HTTP error retrieving appointments: {e}")
            return []
        
        except Exception as e:
            logger.error(f"Unexpected error retrieving appointments: {e}")
            return []
    
    async def cancel_appointment(self, event_id: str) -> bool:
        """
        Annule un rendez-vous.
        
        Args:
            event_id: ID de l'événement à annuler
        
        Returns:
            True si l'annulation a réussi, False sinon
        """
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"Appointment {event_id} cancelled successfully")
            return True
            
        except HttpError as e:
            logger.error(f"HTTP error cancelling appointment: {e}")
            if e.resp.status == 404:
                logger.warning(f"Appointment {event_id} not found")
            return False
        
        except Exception as e:
            logger.error(f"Unexpected error cancelling appointment: {e}")
            return False
    
    async def reschedule_appointment(
        self, 
        event_id: str, 
        new_start_datetime: datetime, 
        new_end_datetime: datetime
    ) -> Dict[str, Any]:
        """
        Reporte un rendez-vous à une nouvelle date/heure.
        
        Args:
            event_id: ID de l'événement à reporter
            new_start_datetime: Nouvelle date et heure de début
            new_end_datetime: Nouvelle date et heure de fin
        
        Returns:
            Dict contenant les détails du rendez-vous reporté
        """
        try:
            # Récupération de l'événement existant
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Mise à jour des dates
            event['start'] = {
                'dateTime': new_start_datetime.isoformat(),
                'timeZone': 'Europe/Paris',
            }
            event['end'] = {
                'dateTime': new_end_datetime.isoformat(),
                'timeZone': 'Europe/Paris',
            }
            
            # Mise à jour de l'événement
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"Appointment {event_id} rescheduled successfully")
            
            return {
                'id': updated_event.get('id'),
                'title': updated_event.get('summary'),
                'start': updated_event.get('start', {}).get('dateTime'),
                'end': updated_event.get('end', {}).get('dateTime'),
                'status': 'rescheduled'
            }
            
        except HttpError as e:
            logger.error(f"HTTP error rescheduling appointment: {e}")
            if e.resp.status == 404:
                raise ValueError("Rendez-vous non trouvé")
            else:
                raise ValueError(f"Erreur lors du report: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error rescheduling appointment: {e}")
            raise ValueError("Une erreur inattendue s'est produite lors du report")
    
    def parse_datetime_from_text(self, text: str) -> Optional[datetime]:
        """
        Parse une date/heure depuis du texte en français.
        Version simple - peut être améliorée avec des bibliothèques comme dateparser.
        
        Args:
            text: Texte contenant la date/heure
        
        Returns:
            datetime object ou None si le parsing échoue
        """
        import re
        
        # Patterns simples pour les dates/heures courantes
        patterns = {
            r'demain (?:à )?(\d{1,2})h?(?:(\d{2}))?': lambda m: datetime.now().replace(
                hour=int(m.group(1)), 
                minute=int(m.group(2)) if m.group(2) else 0,
                second=0, microsecond=0
            ) + timedelta(days=1),
            
            r'aujourd\'?hui (?:à )?(\d{1,2})h?(?:(\d{2}))?': lambda m: datetime.now().replace(
                hour=int(m.group(1)), 
                minute=int(m.group(2)) if m.group(2) else 0,
                second=0, microsecond=0
            ),
            
            r'(\d{1,2})/(\d{1,2})/(\d{4}) (?:à )?(\d{1,2})h?(?:(\d{2}))?': lambda m: datetime(
                year=int(m.group(3)),
                month=int(m.group(2)),
                day=int(m.group(1)),
                hour=int(m.group(4)),
                minute=int(m.group(5)) if m.group(5) else 0
            )
        }
        
        text_lower = text.lower()
        
        for pattern, parser in patterns.items():
            match = re.search(pattern, text_lower)
            if match:
                try:
                    return parser(match)
                except (ValueError, OverflowError):
                    continue
        
        logger.warning(f"Could not parse datetime from text: {text}")
        return None

# Instance globale du service (singleton)
_calendar_service = None

def get_calendar_service() -> GoogleCalendarService:
    """Retourne l'instance du service Google Calendar (singleton)."""
    global _calendar_service
    if _calendar_service is None:
        _calendar_service = GoogleCalendarService()
    return _calendar_service