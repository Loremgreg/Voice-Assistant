# Utiliser une image Python officielle et légère comme base.
# Cela garantit un environnement propre et de taille réduite.
FROM python:3.11-slim

# Définir le répertoire de travail à l'intérieur du conteneur.
# C'est là que notre code sera (via le montage de volume).
WORKDIR /app

# Copier uniquement le fichier des dépendances.
# Cette étape est mise en cache par Docker. La réinstallation des dépendances
# ne se fera que si le fichier requirements.txt est modifié.
COPY requirements.txt .

# Installer les dépendances Python du projet.
# --no-cache-dir permet de garder l'image plus petite.
RUN pip install --no-cache-dir -r requirements.txt

# Le reste des fichiers du projet (comme agent.py) sera monté dynamiquement
# par l'environnement de sandboxing au démarrage. Il n'est donc pas nécessaire
# de les copier ici. Aucune commande CMD ou ENTRYPOINT n'est requise,
# car la commande à exécuter sera fournie par l'outil Gemini.
