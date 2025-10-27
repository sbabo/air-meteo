"""
Script d'ingestion des données de pollution via l'API OpenAQ.

Ce script récupère les dernières mesures de pollution pour une location spécifique 
à Paris (ID 4067) et enrichit ces données avec les unités de mesure de chaque capteur
via des appels individuels à l'endpoint /v3/sensors/{sensor_id}.

Fonctionnalités:
- Récupération des mesures les plus récentes pour une location donnée
- Enrichissement avec les unités de mesure pour chaque capteur
- Construction d'un DataFrame pandas avec toutes les informations

Prérequis:
- Clé API OpenAQ (optionnelle mais recommandée) dans un fichier .env : OPENAQ_API_KEY=votre_cle
- Packages Python : pandas, requests, python-dotenv

Usage:
    python scripts/ingestion_pollution.py

Author: Samuel
Date: October 2025
"""

import pandas as pd
import requests
import json
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

# Constantes de configuration
COUNTRY_ID = 22  # ID pour la France dans l'API OpenAQ
latitude = 48.8588897    # Latitude de Paris (Notre-Dame)
longitude = 2.3200410217200766  # Longitude de Paris (Notre-Dame)
locations_id = []  # Liste pour stocker les IDs de locations (actuellement non utilisée)

def connection_string():
    """
    Récupère la chaîne de connexion à la base de données depuis les variables d'environnement.
    
    Returns:
        str: Chaîne de connexion au format PostgreSQL.
    
    Note:
        Utilise les variables d'environnement suivantes :
        - POSTGRES_USER
        - POSTGRES_PASSWORD
        - POSTGRES_HOST
        - POSTGRES_PORT
        - POSTGRES_DB
    """
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db_name = os.getenv("POSTGRES_DB")

    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

def save_to_db(df, table_name="pollution"):
    """
    Sauvegarde le DataFrame dans la base de données PostgreSQL.
    
    Args:
        df (pandas.DataFrame): DataFrame à sauvegarder.
        table_name (str): Nom de la table dans laquelle sauvegarder les données.
    
    Note:
        Utilise SQLAlchemy pour gérer la connexion et l'insertion des données.
    """
    engine = create_engine(connection_string())
    df.to_sql(table_name, engine, if_exists='append', index=False)
    print(f"Données sauvegardées dans la table '{table_name}' de la base de données.")   

def get_paris_latest_measurements():
    """
    Récupère les dernières mesures de pollution pour la location ID 4067 (Paris).
    
    Cette fonction interroge l'endpoint /v3/locations/4067/latest de l'API OpenAQ
    pour obtenir les mesures les plus récentes de tous les capteurs de cette location.
    
    Returns:
        pandas.DataFrame: DataFrame contenant les colonnes suivantes:
            - locationsId: ID de la location (4067 pour cette location parisienne)
            - sensorsId: ID unique du capteur qui a effectué la mesure
            - latitude: Latitude de la station de mesure
            - longitude: Longitude de la station de mesure
            - value: Valeur mesurée (nombre décimal)
            - datetime_utc: Timestamp UTC de la mesure
            - datetime_local: Timestamp local de la mesure
    
    Raises:
        requests.exceptions.RequestException: En cas d'erreur de connexion à l'API
        json.JSONDecodeError: En cas de réponse API invalide
    
    Note:
        Utilise la clé API OpenAQ depuis la variable d'environnement OPENAQ_API_KEY
        si elle est définie. L'API peut fonctionner sans clé mais avec des limitations.
    """
    # Configuration des headers avec la clé API si disponible
    headers = {
        "X-API-Key": os.getenv("OPENAQ_API_KEY")
    }
    
    # URL pour récupérer les dernières mesures de la location 4067 (Paris)
    url = "https://api.openaq.org/v3/locations/4067/latest"
    
    # Appel à l'API OpenAQ
    response = requests.get(url, headers=headers)
    data = response.json()
    
    # Construction de la liste des enregistrements
    records = []
    for result in data.get("results", []):
        records.append({
            "locationsId": result.get("locationsId"),
            "sensorsId": result.get("sensorsId"), 
            "latitude": result.get("coordinates", {}).get("latitude"),
            "longitude": result.get("coordinates", {}).get("longitude"),
            "value": result.get("value"),
            "datetime_utc": result.get("datetime", {}).get("utc"),
            "datetime_local": result.get("datetime", {}).get("local")
        })

    # Conversion en DataFrame pandas
    df = pd.DataFrame(records)
    return df


def get_sensors_units(df):
    """
    Enrichit le DataFrame avec les unités de mesure de chaque capteur.
    
    Pour chaque sensor ID présent dans le DataFrame, cette fonction effectue
    un appel à l'endpoint /v3/sensors/{sensor_id} pour récupérer les détails
    du capteur, notamment l'unité de mesure du paramètre mesuré.
    
    Args:
        df (pandas.DataFrame): DataFrame contenant au minimum une colonne 'sensorsId'
                              avec les IDs des capteurs à enrichir
    
    Returns:
        pandas.DataFrame: DataFrame enrichi avec une colonne 'unit' contenant
                         l'unité de mesure pour chaque capteur
    
    Raises:
        KeyError: Si la colonne 'sensorsId' n'existe pas dans le DataFrame
        requests.exceptions.RequestException: En cas d'erreur de connexion à l'API
        AttributeError: Si la structure de réponse de l'API est inattendue
    
    Note:
        - Cette fonction effectue un appel API par capteur unique, ce qui peut
          prendre du temps si beaucoup de capteurs sont présents
        - Affiche un message de progression pour chaque capteur traité
        - Utilise la même clé API que la fonction get_paris_latest_measurements()
    """
    # Extraction de la liste unique des IDs de capteurs
    sensorsId = df["sensorsId"].tolist()
    sensorsUnits = []
    
    # Traitement de chaque capteur individuellement
    for sensor_id in sensorsId:
        print(f"Récupération des informations pour le capteur ID: {sensor_id}")
        
        # Construction de l'URL pour le capteur spécifique
        url = f"https://api.openaq.org/v3/sensors/{sensor_id}"
        headers = {
            "X-API-Key": os.getenv("OPENAQ_API_KEY")
        }
        
        # Appel à l'API pour récupérer les détails du capteur
        response = requests.get(url, headers=headers)
        data = response.json()

        # Extraction de l'unité depuis la réponse API
        for sensor in data.get("results", []):
            # Navigation dans la structure JSON pour récupérer l'unité
            # Structure attendue: results[].parameter.units
            sensorsUnits.append(sensor.get("parameter").get("units"))
    
    # Ajout de la colonne 'unit' juste après la colonne 'value'
    df.insert(df.columns.get_loc("value") + 1, "unit", "")
    
    # Affectation des unités récupérées à la nouvelle colonne
    df["unit"] = pd.Series(sensorsUnits)
    
    return df

if __name__ == "__main__":
    # Récupération des dernières mesures de pollution pour Paris
    df_meas = get_paris_latest_measurements()
    df_sensors = get_sensors_units(df_meas)
    
    # Sauvegarde des données enrichies dans la base de données
    if not df_sensors.empty:
        save_to_db(df_sensors, table_name="pollution")
    else:
        print("Aucune donnée de pollution à sauvegarder.")