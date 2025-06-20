from __future__ import annotations  # Permet d'utiliser des annotations de type différées (utile pour les types personnalisés dans les fonctions async)

from livekit.agents import (         # Importe les modules de base de LiveKit pour les agents
    AgentSession,
    Agent,
    AutoSubscribe,                   # Contrôle l'abonnement automatique aux flux audio/vidéo
    JobContext,                      # Fournit le contexte du job LiveKit (participants, connexion, etc.)
    WorkerOptions,                   # Options pour configurer le comportement de l’agent
    cli,                             # Utilitaire en ligne de commande pour lancer les agents
    llm,                              # Outils pour interagir avec un LLM (ex. OpenAI ou Ollama)
    RoomInputOptions,
)

from livekit.plugins import openai                   # ajouter ceux ci plus tard si besoin: silero, elevenlabs, deepgram, noise_cancellation
                                                            # from livekit.plugins.turn_detector.multilingual import MultilingualModel
from dotenv import load_dotenv                                          # Permet de charger les variables d’environnement depuis un fichier `.env`
#from api import AssistantFnc                                            # Module perso : fonctions utiles à ton assistant (à définir dans api.py)
from prompts import WELCOME_MESSAGE, INSTRUCTIONS    # Messages prédéfinis dans un fichier prompts.py
import os                                                               # Module standard pour manipuler l’environnement du système

load_dotenv()                                                           # Charge les variables du fichier `.env` (comme OPENAI_API_KEY ou OLLAMA_HOST)
#definition de l'agent vocal personnalisé
class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=INSTRUCTIONS)

# Point d’entrée de l’application async def entrypoint(ctx: JobContext):
async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)        # Se connecte et s’abonne à tous les flux disponibles (ex. audio)     # Se connecte à la salle LiveKit
    # Crée la session avec tous les modules nécessaires
    session = AgentSession(
                                                                         # stt=deepgram.STT(),                         # Reconnaissance vocale (Deepgram, à adapter)
        llm=openai.realtime.RealtimeModel(
            voice="echo",
            temperature=0.7,
        ),
                                                                     # tts=elevenlabs.TTS(),                       # Synthèse vocale (ElevenLabs ici)
       # vad=silero.VAD.load(),                      # Détection de voix (Silero)
       # turn_detection=MultilingualModel(),          # Pour la gestion des tours de parole dans plusieurs langues
    )
    await session.start(
        room=ctx.room,                              # Rejoint la room actuelle
        agent=Assistant(),                          # Utilise ton agent personnalisé
        room_input_options=RoomInputOptions(
     #       noise_cancellation=noise_cancellation.BVC(),  # Annulation de bruit
        )
    )
    # Fait parler l’agent dès le début
    await session.generate_reply(instructions=WELCOME_MESSAGE)

# Lancement de l’agent vocal (uniquement si le script est exécuté directement)
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))  #cli est l’outil de commande LiveKit importé plus haut | run_app(...) est la fonction qui démarre l agent vocal | WorkerOptions(entrypoint_fnc=entrypoint):Voici les options de configuration pour mon agent, et la fonction d’entrée à exécuter c’est entrypoint »
