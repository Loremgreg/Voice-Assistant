# 🎙️ Voice Assistant with Ollama and LLaMA 3.2

This project is a local voice assistant based on an LLM model running **entirely on my machine**.  
It uses [Ollama](https://ollama.com/) and the **LLaMA 3.2** model, downloaded and executed locally.

---

## 🚀 What I Learned / Built

### 🔧 Project Setup
- Created a Python virtual environment (`.venv`)
- Initialized a project in VS Code with Git
- Configured a `.env` file to simulate a local API key

### 🧠 Local LLM Model
- Downloaded **LLaMA 3.2** via [Ollama](https://ollama.com/library/llama3.2)
- Connected to the model at `localhost:11434` using `ollama-python`
- Tested the model with custom prompts inside VS Code

### 🧪 What I Understood
- The difference between local and remote APIs (e.g. OpenAI)
- The role of `localhost` and ports (like `11434`)
- Why we use `.env` files to store secrets
- How to use `Client()` to communicate with Ollama
