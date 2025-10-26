"""
Script d'ingestion des données météorologiques via l'API OpenWeatherMap.

Ce script récupère les données météorologiques actuelles pour Paris
en utilisant l'API OpenWeatherMap. Les données incluent la température,
l'humidité, la pression, la vitesse du vent et les conditions météo.

Fonctionnalités:
- Récupération des données météo actuelles pour une position géographique
- Conversion automatique des timestamps Unix en datetime
- Construction d'un DataFrame pandas avec les informations météo
- Support des unités métriques (Celsius, m/s, hPa)

Prérequis:
- Clé API OpenWeatherMap dans un fichier .env : OPENWEATHER_API_KEY=votre_cle
- Packages Python : pandas, requests, python-dotenv

Usage:
    python scripts/ingestion_weather.py

Author: Samuel  
Date: October 2025
"""

from datetime import datetime, timezone
import os
import pandas as pd
import requests
from dotenv import load_dotenv
import json

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration géographique pour Paris (coordonnées de Notre-Dame)
latitude = 48.8588897
longitude = 2.3200410217200766

# Configuration des unités : "metric" pour Celsius, m/s, hPa
units = "metric"

def ingest_weather_data():
    """
    Récupère les données météorologiques actuelles pour Paris via l'API OpenWeatherMap.
    
    Cette fonction interroge l'API OpenWeatherMap Current Weather Data pour obtenir
    les conditions météorologiques actuelles à Paris. Les données sont automatiquement
    converties et formatées dans un DataFrame pandas.
    
    Returns:
        pandas.DataFrame: DataFrame contenant une seule ligne avec les colonnes:
            - city: Nom de la ville ("Paris")
            - timestamp: Horodatage UTC de la mesure (datetime object)
            - temperature: Température en Celsius (float)
            - humidity: Humidité relative en pourcentage (int)
            - pressure: Pression atmosphérique en hPa (int)
            - wind_speed: Vitesse du vent en m/s (float)
            - weather: Condition météo principale (str, ex: "Clear", "Clouds", "Rain")
    
    Raises:
        requests.exceptions.RequestException: En cas d'erreur de connexion à l'API
        KeyError: Si la structure de réponse de l'API est inattendue
        json.JSONDecodeError: En cas de réponse API invalide
        ValueError: Si la clé API est invalide ou manquante
    
    Note:
        - Nécessite une clé API OpenWeatherMap valide dans OPENWEATHER_API_KEY
        - Utilise les coordonnées de Paris définies dans les constantes du module
        - Les unités sont en système métrique (Celsius, m/s, hPa)
        - Le timestamp est converti de Unix timestamp vers datetime UTC
    
    Example:
        >>> df = ingest_weather_data()
        >>> print(df.columns.tolist())
        ['city', 'timestamp', 'temperature', 'humidity', 'pressure', 'wind_speed', 'weather']
    """
    # Construction de l'URL avec les paramètres de requête
    url = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&units={}&appid={}".format(
        latitude,
        longitude,
        units,
        os.getenv("OPENWEATHER_API_KEY")
    )
    
    # Appel à l'API OpenWeatherMap
    response = requests.get(url)
    
    # Vérification du code de statut HTTP
    if response.status_code != 200:
        raise requests.exceptions.RequestException(
            f"Erreur API OpenWeatherMap: {response.status_code} - {response.text}"
        )
    
    # Parsing de la réponse JSON
    data = response.json()
    
    # Construction du DataFrame avec une seule ligne de données
    df = pd.DataFrame([
        {
            "city": "Paris",
            # Conversion du timestamp Unix en datetime UTC
            "timestamp": datetime.fromtimestamp(data["dt"], tz=timezone.utc),
            # Données météorologiques principales
            "temperature": data["main"]["temp"],        # °C
            "humidity": data["main"]["humidity"],       # %
            "pressure": data["main"]["pressure"],      # hPa
            "wind_speed": data["wind"]["speed"],        # m/s
            # Condition météo principale (première entrée du tableau weather)
            "weather": data["weather"][0]["main"],
        }
    ])

    return df

if __name__ == "__main__":
    ingest_weather_data()