import os                                            # Importe le module 'os' pour accéder aux variables d'environnement système
from dotenv import load_dotenv                       # Importe la fonction pour charger les variables d'un fichier .env
from ollama import Client                            # Importe la classe Client du module ollama pour se connecter au serveur local

load_dotenv()                                        # Charge les variables d'environnement définies dans le fichier .env
client = Client(host=os.getenv("OLLAMA_HOST"))       # Crée une instance de Client en utilisant l'adresse stockée dans la variable OLLAMA_HOST

# Puis l’utiliser ailleurs avec : from ollama_client import client
