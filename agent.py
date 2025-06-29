import traceback
from dotenv import load_dotenv

from pathlib import Path

from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)

from llama_index.core import Document

from livekit import agents
from livekit.agents import (
    AgentSession,
    Agent,
    RoomInputOptions,
    JobProcess, 
    ChatContext,           
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

from prompts import INSTRUCTIONS, book_appointment, reschedule_appointment, cancel_appointment  

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
        model_name="sentence-transformers/all-MiniLM-L6-v2"  # léger, multilingue, idéal pour un POC
    )
# -----------------------------------------------------------------------

from livekit.agents.llm import function_tool

@function_tool
async def query_info(query: str) -> str:
    """Recherche d'information dans la base documentaire vectorielle."""
    query_engine = index.as_query_engine(use_async=True)
    res = await query_engine.aquery(query)
    return str(res)

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=INSTRUCTIONS,
            tools=[
                    query_info,
                    book_appointment,
                    reschedule_appointment,
                    cancel_appointment
                ],  # expose TOUS les outils au LLM
            )

    async def on_enter(self):
        await self.session.say("Bonjour ! Vous êtes en ligne avec l’assistant "
                             "vocal de notre cabinet de kinésithérapie. Pour commencer, pourriez-vous me "
                             "donner votre prénom et votre nom ? Merci aussi de préciser si vous êtes un "
                             "nouveau patient ou si vous avez déjà consulté chez nous. Une fois ces "
                             "informations recueillies, je répondrai volontiers à votre question.",
                             allow_interruptions=False)


async def entrypoint(ctx: agents.JobContext):
    # Establish the connection first so ctx.room is populated
    await ctx.connect()

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

    # ------------------------------------------------------------------
    # Ne pas indexer l'historique de conversation pour la conformité RGPD
    # ------------------------------------------------------------------
    # Laisser ce bloc vide empêche le stockage de données personnelles et de
    # santé potentiellement sensibles dans l'index RAG. L'agent utilisera
    # uniquement les documents statiques du dossier /docs pour ses recherches.
    from livekit.agents import ConversationItemAddedEvent  # type: ignore

    @session.on("conversation_item_added")
    def _index_history(ev: ConversationItemAddedEvent) -> None:  # noqa: N801 | This callback is intentionally left empty for GDPR compliance.
        pass                                                           # It no longer needs to be async as it doesn't perform any awaitable operations.

    # Start the session
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )




# Lancement de l’agent vocal (uniquement si le script est exécuté directement)
if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,        # use the pre‑loaded resources
            num_idle_processes=2,       # keep 2 warm processes ready (optional)
        )
    )