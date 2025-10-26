"# Air-Météo : Ingestion de données environnementales

Ce projet permet de récupérer et traiter des données environnementales depuis deux sources principales :
- **Données de pollution** via l'API OpenAQ
- **Données météorologiques** via l'API OpenWeatherMap

## 📋 Table des matières

- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Scripts disponibles](#scripts-disponibles)
- [Structure du projet](#structure-du-projet)
- [APIs utilisées](#apis-utilisées)
- [Contribuer](#contribuer)

## 🔧 Prérequis

- Python 3.8 ou supérieur
- Connexion internet pour accéder aux APIs
- Clés API (optionnelles mais recommandées) :
  - OpenAQ API Key
  - OpenWeatherMap API Key

## 📦 Installation

1. **Cloner le repository** :
```bash
git clone https://github.com/sbabo/air-meteo.git
cd air-meteo
```

2. **Installer les dépendances** :
```bash
pip install pandas requests python-dotenv
```

3. **Créer le dossier de données** (optionnel) :
```bash
mkdir data
```

## ⚙️ Configuration

### Fichier .env

Créez un fichier `.env` à la racine du projet avec vos clés API :

```env
# Clé API OpenAQ (optionnelle mais recommandée)
OPENAQ_API_KEY=votre_cle_openaq_ici

# Clé API OpenWeatherMap (obligatoire pour les données météo)
OPENWEATHER_API_KEY=votre_cle_openweathermap_ici
```

### Obtenir les clés API

**OpenAQ** :
- Site : https://openaq.org/
- Inscription gratuite avec limites généreuses
- L'API fonctionne sans clé mais avec des limitations

**OpenWeatherMap** :
- Site : https://openweathermap.org/api
- Plan gratuit : 1000 calls/jour
- Inscription requise

## 🚀 Utilisation

### Script de pollution (OpenAQ)

```bash
# Exécution basique
python scripts/ingestion_pollution.py

# Le script va :
# 1. Récupérer les mesures de la location 4067 (Paris)
# 2. Enrichir chaque mesure avec l'unité du capteur
# 3. Afficher le DataFrame résultant
```

### Script météorologique (OpenWeatherMap)

```bash
# Exécution basique
python scripts/ingestion_weather.py

# Le script va :
# 1. Récupérer les conditions météo actuelles pour Paris
# 2. Afficher les données formatées
```

## 📁 Scripts disponibles

### `scripts/ingestion_pollution.py`

**Fonctionnalité** : Récupère les données de pollution de l'air depuis OpenAQ

**Données collectées** :
- ID de location et de capteur
- Coordonnées géographiques (latitude, longitude)
- Valeur mesurée avec son unité
- Timestamps UTC et local

**APIs utilisées** :
- `GET /v3/locations/4067/latest` : Mesures récentes
- `GET /v3/sensors/{sensor_id}` : Détails et unités des capteurs

**Sortie** : DataFrame pandas avec colonnes enrichies

### `scripts/ingestion_weather.py`

**Fonctionnalité** : Récupère les données météorologiques actuelles depuis OpenWeatherMap

**Données collectées** :
- Température (°C)
- Humidité (%)
- Pression atmosphérique (hPa)
- Vitesse du vent (m/s)
- Conditions météo principales

**API utilisée** :
- `GET /data/2.5/weather` : Données météo actuelles

**Sortie** : DataFrame pandas avec une ligne de données

## 🏗️ Structure du projet

```
air-meteo/
│
├── scripts/
│   ├── ingestion_pollution.py    # Script OpenAQ
│   └── ingestion_weather.py      # Script OpenWeatherMap
│
├── data/                         # Dossier pour les fichiers de sortie
│   ├── pollution_paris_latest.csv    (optionnel)
│   └── weather_paris_current.csv     (optionnel)
│
├── .env                          # Variables d'environnement (à créer)
├── .gitignore                    # Fichiers à ignorer par Git
└── README.md                     # Cette documentation
```

## 🔌 APIs utilisées

### OpenAQ API v3

- **Base URL** : `https://api.openaq.org/v3`
- **Documentation** : https://docs.openaq.org/
- **Endpoints utilisés** :
  - `/locations/{id}/latest` : Dernières mesures d'une location
  - `/sensors/{id}` : Détails d'un capteur spécifique

### OpenWeatherMap API

- **Base URL** : `https://api.openweathermap.org/data/2.5`
- **Documentation** : https://openweathermap.org/api
- **Endpoints utilisés** :
  - `/weather` : Données météo actuelles

## 📊 Exemples de sortie

### Données de pollution

```
   locationsId  sensorsId   latitude  longitude    value    unit         datetime_utc              datetime_local
0         4067      12345  48.858889   2.320041     23.5    µg/m³   2025-10-26T10:30:00Z   2025-10-26T12:30:00+02:00
1         4067      12346  48.858889   2.320041     45.2    µg/m³   2025-10-26T10:30:00Z   2025-10-26T12:30:00+02:00
```

### Données météorologiques

```
    city                 timestamp  temperature  humidity  pressure  wind_speed weather
0  Paris  2025-10-26 10:30:00+00:00         18.5        65      1013         3.2   Clear
```

## 🛠️ Développement

### Ajouter une nouvelle source de données

1. Créer un nouveau script dans `scripts/`
2. Suivre le pattern des scripts existants :
   - Documentation du module
   - Fonctions avec docstrings détaillées
   - Gestion d'erreurs appropriée
   - Block `if __name__ == "__main__"`

### Personnalisation

**Changer la ville** :
Modifiez les coordonnées dans les constantes :
```python
latitude = 48.8588897    # Nouvelle latitude
longitude = 2.3200410217200766  # Nouvelle longitude
```

**Ajouter la sauvegarde** :
Décommentez les lignes de sauvegarde dans les scripts :
```python
df.to_csv("data/mon_fichier.csv", index=False)
```

## 🤝 Contribuer

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit vos changements (`git commit -am 'Ajouter nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📝 Notes techniques

- **Gestion d'erreurs** : Les scripts incluent une gestion d'erreurs basique
- **Rate limiting** : Respect automatique des limites des APIs
- **Format des données** : Utilisation de pandas DataFrame pour la cohérence
- **Timestamps** : Tous les timestamps sont gérés en UTC avec conversion locale

## 📞 Support

En cas de problème :
1. Vérifiez vos clés API dans le fichier `.env`
2. Vérifiez votre connexion internet
3. Consultez les logs d'erreur pour plus de détails
4. Vérifiez les quotas de vos APIs

---

**Auteur** : Samuel  
**Date** : Octobre 2025  
**Version** : 1.0" 
