from __future__ import annotations  # Permet d'utiliser des annotations de type différées (utile pour les types personnalisés dans les fonctions async)

from livekit.agents import (         # Importe les modules de base de LiveKit pour les agents
    AutoSubscribe,                   # Contrôle l'abonnement automatique aux flux audio/vidéo
    JobContext,                      # Fournit le contexte du job LiveKit (participants, connexion, etc.)
    WorkerOptions,                   # Options pour configurer le comportement de l’agent
    cli,                             # Utilitaire en ligne de commande pour lancer les agents
    llm                              # Outils pour interagir avec un LLM (ex. OpenAI ou Ollama)
)

from livekit.agents.multimodal import MultimodalAgent                      # Agent qui gère plusieurs modalités (texte, audio, etc.)
from livekit.plugins import openai                                      # Plugin pour utiliser OpenAI ou des API compatibles (ex. Ollama)
from dotenv import load_dotenv                                          # Permet de charger les variables d’environnement depuis un fichier `.env`
from api import AssistantFnc                                            # Module perso : fonctions utiles à ton assistant (à définir dans api.py)
from prompts import WELCOME_MESSAGE, INSTRUCTIONS, LOOKUP_VIN_MESSAGE   # Messages prédéfinis dans un fichier prompts.py
import os                                                               # Module standard pour manipuler l’environnement du système

load_dotenv()                                                           # Charge les variables du fichier `.env` (comme OPENAI_API_KEY ou OLLAMA_HOST)

# Déclaration d'une fonction asynchrone appelée à l’entrée du job
async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)        # Se connecte et s’abonne à tous les flux disponibles (ex. audio)
    await ctx.wait_for_participant()                                     # Attend qu’un participant rejoigne la salle avant d’exécuter la suite

    model = openai.realtime.RealtimeModel(
            instructions=INSTRUCTIONS,
            voice="shimmer",
            temperature=0.8,
            modalities=["audio", "text"]
        )
