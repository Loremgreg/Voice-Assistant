from livekit.agents import (
    AgentSession,
    Agent,
    RoomInputOptions
)
from livekit.plugins import (
    elevenlabs,
    deepgram,
    openai,
    silero,
    noise_cancellation,
)
from livekit import agents

from livekit.plugins.turn_detector.multilingual import MultilingualModel

from prompts import INSTRUCTIONS   
from dotenv import load_dotenv            

load_dotenv()

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=INSTRUCTIONS)


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=elevenlabs.TTS(
            voice_id="FpvROcY4IGWevepmBWO2", 
            model="eleven_flash_v2_5",
            language="fr",
        ),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )
   


    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(), 
        ),
    )
    
    await ctx.connect()

    # Speak the predefined welcome message, then listen
    await session.generate_reply(instructions=INSTRUCTIONS)




# Lancement de l’agent vocal (uniquement si le script est exécuté directement)
if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))