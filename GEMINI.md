# Directives pour le projet Voice-Assistant

Ce document fournit les instructions et le contexte nécessaires pour travailler sur ce projet d'assistant vocal.

## 1. Contexte du Projet

- **Objectif :** Créer un assistant vocal intelligent pour un cabinet de kinésithérapie.
- **Fonctionnalités Clés :**
    - Accueillir les patients au téléphone.
    - Répondre aux questions fréquentes (horaires, adresse, tarifs, etc.) en utilisant une base de connaissances (RAG).
    - Gérer les rendez-vous (prise, modification, annulation) via des outils.
- **Persona de l'Agent :** Le ton doit toujours être professionnel, clair, concis et empathique.

## 2. Pile Technique Principale

- **Langage :** Python
- **Framework d'Agent :** LiveKit Agents
- **LLM (Cerveau) :** OpenAI `gpt-4o-mini`
- **STT (Transcription) :** Deepgram `nova-3` (multilingue)
- **TTS (Voix) :** ElevenLabs `eleven_flash_v2_5`
- **RAG (Base de connaissances) :** LlamaIndex
- **Embeddings (pour RAG) :** HuggingFace `BAAI/bge-m3`
- **VAD (Détection de voix) :** Silero VAD

## 3. Conventions et Architecture

- **`agent.py` :** C'est le point d'entrée principal. Il initialise la `AgentSession` de LiveKit et connecte tous les services (STT, LLM, TTS).
- **`prompts.py` :** Ce fichier est central.
    - Il contient la variable `INSTRUCTIONS` qui est le prompt système principal pour le LLM.
    - C'est ici que tous les outils (`@function_tool`) doivent être définis (ex: `book_appointment`).
- **`requirements.txt` :** Toutes les dépendances Python doivent y être listées.
- **Configuration :** Les clés API et autres secrets **doivent** être chargés depuis un fichier `.env` et ne jamais être écrits en dur dans le code. Les valeurs de configuration (ID de voix, nom des modèles) devraient également y figurer.

## 4. Règle Critique : Sécurité et Conformité RGPD

**Ceci est la règle la plus importante du projet.**

- **Priorité absolue :** La protection des données de santé des patients.
- **Interdiction formelle :** **NE JAMAIS** indexer l'historique des conversations des utilisateurs dans la base de données RAG.
- **Raison :** Pour éviter de stocker des données personnelles identifiables (nom, date de naissance) ou des informations de santé protégées en clair dans le dossier `query-engine-storage`.
- **Conséquence :** L'index RAG doit **uniquement** contenir des données statiques et anonymes provenant du dossier `/docs`. La fonction `_index_history` dans `agent.py` doit rester vide.

## 5. Documentation de Référence LiveKit

En cas de doute sur le fonctionnement de LiveKit Agents, se référer en priorité à ces liens :

- **Introduction :** [https://docs.livekit.io/agents/](https://docs.livekit.io/agents/)
- **Playground :** [https://docs.livekit.io/agents/start/playground/](https://docs.livekit.io/agents/start/playground/)
- **Migration v0.x :** [https://docs.livekit.io/agents/start/v0-migration/](https://docs.livekit.io/agents/start/v0-migration/)
- **Construction (Build) :** [https://docs.livekit.io/agents/build/](https://docs.livekit.io/agents/build/)
- **Workflows :** [https://docs.livekit.io/agents/build/workflows/](https://docs.livekit.io/agents/build/workflows/)
- **Audio & Parole :** [https://docs.livekit.io/agents/build/audio/](https://docs.livekit.io/agents/build/audio/)
- **Outils (Tools) :** [https://docs.livekit.io/agents/build/tools/](https://docs.livekit.io/agents/build/tools/)
- **Nodes & Hooks :** [https://docs.livekit.io/agents/build/nodes/](https://docs.livekit.io/agents/build/nodes/)
- **Détection de Tour (Turns) :** [https://docs.livekit.io/agents/build/turns/](https://docs.livekit.io/agents/build/turns/)
- **Données Externes & RAG :** [https://docs.livekit.io/agents/build/external-data/](https://docs.livekit.io/agents/build/external-data/)
- **Événements & Erreurs :** [https://docs.livekit.io/agents/build/events/](https://docs.livekit.io/agents/build/events/)
- **Cycle de vie du Worker :** [https://docs.livekit.io/agents/worker/](https://docs.livekit.io/agents/worker/)
