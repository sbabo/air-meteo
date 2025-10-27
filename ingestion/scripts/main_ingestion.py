import subprocess

# Lancer le script d'ingestion des données météo
subprocess.run(["python", "scripts/ingestion_weather.py"])

# Lancer le script d'ingestion des données de pollution
subprocess.run(["python", "scripts/ingestion_pollution.py"])

print("Ingestion des données météo et pollution terminée.")