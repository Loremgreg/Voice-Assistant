import os
import functools
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
    JobProcess,          
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

from prompts import (
    INSTRUCTIONS,
    book_appointment,
    reschedule_appointment,
    cancel_appointment,
)

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
    import gc

    # Silero VAD weights (~15 MB) – loaded once, reused by all jobs in the process
    proc.userdata["vad"] = silero.VAD.load()

    # Load the multilingual embedding model once per process
    # Utiliser un modèle encore plus léger si nécessaire
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    # Force garbage collection
    gc.collect()
# -----------------------------------------------------------------------

def create_query_info_tool(query_engine):
    @agents.llm.function_tool
    async def query_info(query: str) -> str:
        """Recherche d'information dans la base documentaire vectorielle."""
        res = await query_engine.aquery(query)
        return str(res)
    return query_info

class Assistant(Agent):
    def __init__(self) -> None:
        # Initialiser le query_engine une seule fois par session
        self.query_engine = index.as_query_engine(use_async=True)

        # Créer l'outil query_info avec le query_engine de la session
        query_info_tool = create_query_info_tool(self.query_engine)

        tools = [
            query_info_tool,
            book_appointment,
            reschedule_appointment,
            cancel_appointment,
        ]  # expose TOUS les outils au LLM

        super().__init__(instructions=INSTRUCTIONS, tools=tools)

    async def on_enter(self):
        # Laisse le LLM commencer la conversation en se basant sur ses instructions.
        # Le LLM utilisera le message de salutation défini dans prompts.py.
        # "allow_interruptions=False" est conservé pour s'assurer que le message d'accueil n'est pas coupé.
        await self.session.say(text="", allow_interruptions=False)


async def entrypoint(ctx: agents.JobContext):
    # Establish the connection first so ctx.room is populated
    await ctx.connect()

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=openai.LLM(model="gpt-4o-mini", temperature=0.2),
        tts=elevenlabs.TTS(
            voice_id=os.environ.get("ELEVEN_VOICE_ID", "FpvROcY4IGWevepmBWO2"),
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
    def _index_history(
        ev: ConversationItemAddedEvent,
    ) -> None:  # This callback is intentionally left empty for GDPR compliance.
        pass  # It no longer needs to be async as it doesn't perform any awaitable operations.

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
            prewarm_fnc=prewarm,  # use the pre‑loaded resources
            num_idle_processes=1,  # Start with 1 process to avoid download race conditions
        )
    )
