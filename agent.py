from dotenv import load_dotenv

from pathlib import Path

from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)

from livekit import agents
from livekit.agents import (
    AgentSession,
    Agent,
    RoomInputOptions,
    JobProcess,            # ← new
)
from livekit.plugins import (
    elevenlabs,
    deepgram,
    openai,
    silero,
    noise_cancellation,
)

from livekit.plugins.turn_detector.multilingual import MultilingualModel

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

from prompts import INSTRUCTIONS   

load_dotenv()

# ---------- RAG index initialisation ----------
THIS_DIR = Path(__file__).parent
PERSIST_DIR = THIS_DIR / "query-engine-storage"

if not PERSIST_DIR.exists():
    # First run: index all Markdown / text files in the "docs" folder
    documents = SimpleDirectoryReader(THIS_DIR / "docs").load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    # Redémarrage: Re‑use the existing persisted index
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)
# ----------------------------------------------

# -------------------- PREWARM (one‑time per process) --------------------
def prewarm(proc: JobProcess) -> None:
    """Load heavy resources once per process and store them in proc.userdata."""
    # Silero VAD weights (~15 MB) – loaded once, reused by all jobs in the process
    proc.userdata["vad"] = silero.VAD.load()
    # Load the multilingual embedding model once per process
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-m3"  # compact FR/EN/… embeddings
    )
# -----------------------------------------------------------------------

from livekit.agents import llm

@llm.function_tool
async def query_info(query: str) -> str:
    """Recherche d'information dans la base documentaire vectorielle."""
    query_engine = index.as_query_engine(use_async=True)
    res = await query_engine.aquery(query)
    return str(res)

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=INSTRUCTIONS,
            tools=[query_info],   # ← expose RAG lookup to the LLM
        )


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=elevenlabs.TTS(
            voice_id="FpvROcY4IGWevepmBWO2", 
            model="eleven_flash_v2_5",
        ),
        vad=ctx.proc.userdata["vad"],
        turn_detection=MultilingualModel(),
    )
   


    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(), 
        ),
    )

    await ctx.connect()

    await session.generate_reply(instructions=INSTRUCTIONS)




# Lancement de l’agent vocal (uniquement si le script est exécuté directement)
if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,        # use the pre‑loaded resources
            num_idle_processes=2,       # keep 2 warm processes ready (optional)
        )
    )