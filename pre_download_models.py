from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import nltk

if __name__ == "__main__":
    print("Début du téléchargement des modèles. Cela peut prendre quelques minutes...")

    # 1. Forcer le téléchargement du modèle d'embedding
    print("Téléchargement du modèle sentence-transformer...")
    try:
        HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        print("...modèle sentence-transformer téléchargé avec succès.")
    except Exception as e:
        print(f"Une erreur est survenue lors du téléchargement du modèle sentence-transformer : {e}")


    # 2. Forcer le téléchargement du tokenizer NLTK
    print("\nTéléchargement du tokenizer NLTK 'punkt'...")
    try:
        nltk.download('punkt', quiet=True)
        print("...tokenizer NLTK téléchargé avec succès.")
    except Exception as e:
        print(f"Une erreur est survenue lors du téléchargement de NLTK 'punkt' : {e}")


    print("\nTous les modèles nécessaires ont été téléchargés et mis en cache.")
    print("Vous pouvez maintenant lancer l'agent principal avec 'python agent.py'.")

