# 🎙️ Voice Assistant with Ollama and LLaMA 3.2

It was initially set up to use [Ollama](https://ollama.com/) running entirely on my machine with the LLaMA 3.2 model locally, but now uses OpenAI's API instead.

---

## 🚀 What I Learned / Built

### 🔧 Project Setup
- Created a Python virtual environment (`.venv`)
- Initialized a project in VS Code with Git
- Configured a `.env` file to simulate a local API key
- Installed project dependencies using `pip install -r requirements.txt`

### 🧠 Local LLM Model
- Downloaded **LLaMA 3.2** via [Ollama](https://ollama.com/library/llama3.2)
- Tested Ollama integration with LLaMA 3.2 via the REST API (`localhost:11434`) and also explored using it with LiveKit Agents
- Tested the model with custom prompts inside VS Code

### 🧪 What I Understood
- The difference between local and remote APIs (e.g. OpenAI)
- The role of `localhost` and ports (like `11434`)
- Why we use `.env` files to store secrets
- How to use `Client()` to communicate with Ollama
- How to run local LLMs with LiveKit using the OpenAI-compatible plugin
