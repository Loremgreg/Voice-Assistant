from livekit.agents.llm import function_tool
from llama_index.core.query_engine import BaseQueryEngine
from calendar_service import get_calendar_service
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

INSTRUCTIONS = """
    You are the voice assistant for a physiotherapy clinic (“cabinet de kinésithérapie”).
    Your goal is to welcome callers, collect their basic information, then answer their questions
    or transfer them to the appropriate staff member.

    1. GREETING ─ Start every call with this message : "Bonjour ! Vous êtes en ligne avec l’assistant vocal de notre cabinet de kinésithérapie.
    Comment puis-je vous aider? 
    Use a friendly, professional tone. 
       
    2. PATIENT INFO COLLECTION

       • **For booking an appointment**:
         - Politely ask for the patient's : first name (prénom), last name (nom), phone number (téléphone), and email address.
         - Once these are collected, call the tool `book_appointment` with the requested appointment details.

       • **For cancelling or rescheduling an appointment**:
         - Ask for: first name (prénom), last name (nom), the date of the appointment to cancel, and if rescheduling, the desired new date/time.
         - If the requested date/time is not available, offer only alternative slots that match the patient’s expressed constraints (for example, if the patient is only available on Tuesdays and Thursdays, do not propose other days; if not available in the morning, do not offer morning slots).
         - Always consider and respect any preferences stated by the patient regarding days or times.

    3. HANDLE REQUEST ─ Once the above info is confirmed, address their question or request.
       Typical topics you can handle:
       • Book, reschedule, or cancel an appointment (and send a confirmation via e-mail)
       • Clinic address, access & parking, opening hours
       • Accepted insurance and payment methods
       • General advice about therapy offers
       • Take a detailed message when human help is required

    4. COMMUNICATION STYLE ─ Be clear, concise, empathetic and respectful.
       Use simple language a layperson can understand; avoid medical jargon unless asked.

    5. ESCALATION ─ If you do not know the answer or the caller asks for a clinician,
       take a message (name, phone, reason, preferred callback slot) and explain that a colleague
       will call back as soon as possible.

    6. CLOSING ─ Summarize any actions taken, confirm next steps (e.g., appointment time),
       and thank the patient before ending the call.

    NOTE ON DATA PRIVACY ─ Inform patients that their data is stored securely and used solely
    for managing their care, in accordance with GDPR.


    7. TOOL USAGE ─ If you need information beyond these instructions or the current
       conversation, call the function tool `query_info` with a concise query.
       Do **not** call it if the answer is already evident from the chat history.
       Limit the returned answer (and therefore your reply) to **800 tokens** maximum.

    8. OUT-OF-SCOPE QUESTIONS ─ If a patient asks a question unrelated to physiotherapy, 
       clinic operations, appointments, or general health, **do NOT attempt to answer**.
       Instead, politely reply:
       "Je suis désolé, je ne peux pas répondre à cette question. Je peux uniquement répondre à des questions concernant le cabinet de kinésithérapie, la prise de rendez-vous, ou votre suivi de soins."
       
       Never attempt to answer questions outside this scope (e.g. weather, politics, sports, jokes, etc.). 
       Do not invent or guess.   

    9. BREVITY ─ Always keep responses as brief as possible.
       Use only the information strictly necessary to answer the patient’s question.
       Avoid repeating information already given, and do not use filler words.
       If the answer can be given in a single sentence, do so.
"""




@function_tool
async def book_appointment(details: str) -> str:
    """
    Books an appointment based on a natural language query.
    For example: "tomorrow at 2pm" or "July 2nd at 10:30".
    """
    try:
        calendar_service = get_calendar_service()
        
        # Parse la date/heure depuis le texte
        start_datetime = calendar_service.parse_datetime_from_text(details)
        if not start_datetime:
            return "Je n'ai pas pu comprendre la date et l'heure souhaitées. Pouvez-vous préciser, par exemple 'demain à 14h' ?"
        
        # Durée par défaut de 30 minutes pour un rendez-vous
        end_datetime = start_datetime + timedelta(minutes=30)
        
        # Vérifier la disponibilité
        is_available = await calendar_service.check_availability(start_datetime, end_datetime)
        if not is_available:
            return f"Le créneau du {start_datetime.strftime('%d/%m/%Y à %Hh%M')} n'est pas disponible. Pouvez-vous choisir un autre horaire ?"
        
        # Créer le rendez-vous
        appointment = await calendar_service.create_appointment(
            title="Rendez-vous Kinésithérapie",
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            description="Rendez-vous pris via l'assistant vocal"
        )
        
        formatted_date = start_datetime.strftime('%d/%m/%Y à %Hh%M')
        return f"Parfait ! Votre rendez-vous est confirmé pour le {formatted_date}. Vous recevrez une confirmation par email."
        
    except ValueError as e:
        logger.error(f"Error booking appointment: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"Unexpected error booking appointment: {e}")
        return "Une erreur technique s'est produite. Veuillez réessayer ou contacter directement le cabinet."

@function_tool
async def reschedule_appointment(details: str) -> str:
    """
    Reschedules an existing appointment based on a natural language query.
    For example: "reschedule my appointment from tomorrow at 2pm to next Friday at 4pm".
    """
    try:
        calendar_service = get_calendar_service()
        
        # Pour simplifier le prototype, on récupère les prochains rendez-vous
        # et on demande à l'utilisateur de préciser
        appointments = await calendar_service.get_appointments(max_results=5)
        
        if not appointments:
            return "Je ne trouve aucun rendez-vous à reporter. Souhaitez-vous prendre un nouveau rendez-vous ?"
        
        # Parse la nouvelle date/heure
        new_datetime = calendar_service.parse_datetime_from_text(details)
        if not new_datetime:
            return "Je n'ai pas pu comprendre la nouvelle date souhaitée. Pouvez-vous préciser, par exemple 'vendredi à 16h' ?"
        
        # Pour le prototype, on prend le premier rendez-vous trouvé
        # Dans une version complète, il faudrait une logique plus sophistiquée
        first_appointment = appointments[0]
        new_end_datetime = new_datetime + timedelta(minutes=30)
        
        # Vérifier la disponibilité du nouveau créneau
        is_available = await calendar_service.check_availability(new_datetime, new_end_datetime)
        if not is_available:
            return f"Le nouveau créneau du {new_datetime.strftime('%d/%m/%Y à %Hh%M')} n'est pas disponible. Pouvez-vous choisir un autre horaire ?"
        
        # Reporter le rendez-vous
        updated_appointment = await calendar_service.reschedule_appointment(
            first_appointment['id'],
            new_datetime,
            new_end_datetime
        )
        
        formatted_date = new_datetime.strftime('%d/%m/%Y à %Hh%M')
        return f"Votre rendez-vous a été reporté au {formatted_date}. Vous recevrez une confirmation par email."
        
    except ValueError as e:
        logger.error(f"Error rescheduling appointment: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"Unexpected error rescheduling appointment: {e}")
        return "Une erreur technique s'est produite lors du report. Veuillez réessayer."

@function_tool
async def cancel_appointment(details: str) -> str:
    """
    Cancels an appointment based on a natural language query.
    For example: "the appointment for tomorrow at 2pm".
    """
    try:
        calendar_service = get_calendar_service()
        
        # Récupérer les prochains rendez-vous
        appointments = await calendar_service.get_appointments(max_results=5)
        
        if not appointments:
            return "Je ne trouve aucun rendez-vous à annuler."
        
        # Pour le prototype, on affiche les rendez-vous disponibles
        if len(appointments) == 1:
            appointment = appointments[0]
            success = await calendar_service.cancel_appointment(appointment['id'])
            
            if success:
                start_time = datetime.fromisoformat(appointment['start'].replace('Z', '+00:00'))
                formatted_date = start_time.strftime('%d/%m/%Y à %Hh%M')
                return f"Votre rendez-vous du {formatted_date} a été annulé avec succès."
            else:
                return "Une erreur s'est produite lors de l'annulation. Veuillez réessayer."
        else:
            # Plusieurs rendez-vous - demander précision
            appointments_list = []
            for i, apt in enumerate(appointments[:3], 1):  # Limiter à 3 pour la lisibilité
                start_time = datetime.fromisoformat(apt['start'].replace('Z', '+00:00'))
                formatted_date = start_time.strftime('%d/%m/%Y à %Hh%M')
                appointments_list.append(f"{i}. {formatted_date}")
            
            appointments_text = "\n".join(appointments_list)
            return f"J'ai trouvé plusieurs rendez-vous :\n{appointments_text}\n\nPouvez-vous préciser lequel vous souhaitez annuler ?"
        
    except Exception as e:
        logger.error(f"Unexpected error canceling appointment: {e}")
        return "Une erreur technique s'est produite lors de l'annulation. Veuillez réessayer."

# (Je peux  en ajouter d'autres pour get_patient_info, etc.)
