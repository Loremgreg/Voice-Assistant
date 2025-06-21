from livekit.agents import (
    AgentSession,
    Agent,
    llm,
    RoomInputOptions
)
from livekit.plugins import (
    elevenlabs,
    deepgram,
    google,
    openai,
    silero,
    noise_cancellation,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from prompts import WELCOME_MESSAGE, INSTRUCTIONS    # Messages prédéfinis dans un fichier prompts.py
from dotenv import load_dotenv                                          # Permet de charger les variables d’environnement depuis un fichier `.env`

load_dotenv()

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant.")



async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    session = AgentSession(
        stt=deepgram.STT(),
        llm=openai.realtime.RealtimeModel(
            voice="echo"
            temperature=0.7
        ),
        tts=elevenlabs.TTS(),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )
   

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Instruct the agent to speak first
    await session.generate_reply(instructions=INSTRUCTION)