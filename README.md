# 🏠 Mini-Projet - Smart Home IoT — Maison Intelligente-ESP32-DHT22-ThingBoard

## Contexte & Objectifs
Système IoT de surveillance et contrôle de température/humidité
en temps réel avec déclenchement automatique du ventilateur
et alertes email.

## Architecture
DHT22 → ESP32 → MQTT TLS → ThingsBoard → IFTTT Email

## Composants
| Composant | Rôle |
|---|---|
| ESP32 | Microcontrôleur WiFi |
| DHT22 | Capteur Temp & Humidité |
| Servo-moteur | Ventilateur simulé |
| ThingsBoard | Dashboard cloud |
| IFTTT | Notifications Email |

## Sécurité
- MQTT avec TLS (port 8883)
- Token d'authentification device
- Dashboard protégé par login

## Instructions d'exécution

### 1. Configurer les credentials
Remplacer dans `main.py` :
- `YOUR_DEVICE_TOKEN_HERE` → votre token ThingsBoard
- `YOUR_IFTTT_KEY_HERE` → votre clé IFTTT

### 2. Lancer la simulation
https://wokwi.com/projects/463408939470382081

### 3. Configurer ThingsBoard
- Créer un device sur ThingsBoard Cloud
- Copier le token dans main.py
- Créer le dashboard avec les widgets .

## Réalisé par
- AIT MBAREK Karim
- IDCHAOUDI Youssef

## Encadrant
Pr. Mohammed FARTITCHOU

## École
ENIAD — Berkane | 2025/2026
