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
    assistant = AssistantFnc()
    assistant = MultimodalAgent(model=model, fnc_ctx=AssistantFnc)      #assistant :on crée un agent, il va utiliser un model, lui donner des outils dans la classe AssistantFnc
    assistant.start(ctx.room).  # on connecte l'assistant à une room -> await ctx.wait_for_participant()
        #add chat message:
    session = model.session[0]            #on dit a l'assistant ce qu'il fait dans la room : parler avec le user. On prend la 1ere session [0] 
    session.conversation.item.create(                              #create a new conversation item
        llm.chatMessage(                               #create a new llm chat:
            role="assistant",                                            #son role sera assistant
            content=""
        )
    )
        #repondre au message:
    session.response.create()
                                                #Jusqu'a mtn on a créé un functionning AI assistant, mtn il faut appelé cette entrypoint function:
        
if __name__ == "__main__":                        # Fonction qui permet de vérifier si le fichier est exécuté directement (ex: python agent.py) plutôt que importé comme un module dans un autre script.
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))   #cli est l’outil de commande LiveKit importé plus haut | run_app(...) est la fonction qui démarre l agent vocal | WorkerOptions(entrypoint_fnc=entrypoint):Voici les options de configuration pour mon agent, et la fonction d’entrée à exécuter c’est entrypoint »
                                                # Résumé du bloc: → Démarre l’assistant vocal uniquement si j exécutes ce fichier directement. Il utilise les options de l’agent pour lancer la fonction entrypoint(), qui établit la connexion et initialise l’assistant.