# ErgoSecure - Gestionnaire de Mots de Passe

## Description
Application web et desktop de gestion de mots de passe securisee avec chiffrement AES-256-CBC.

## Design (Ergonomie - Bastien et Scapin)
- **Guidage**: Incitation visuelle, groupement logique
- **Charge de travail**: Formulaires brefs, densite informationnelle adaptee
- **Controle explicite**: Feedback immediat sur les actions
- **Gestion des erreurs**: Messages d'erreur clairs
- **Homogeneite**: Style coherent sur toutes les pages

## Identite Visuelle
- **Police**: Roboto Slab (serif)
- **Couleurs**:
  - Primary: #81A6C6
  - Secondary: #AACDDC
  - Tertiary: #F3E3D0
  - Accent: #D2C4B4

## Installation

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn server:app --port 3000
```

### Frontend Web
```bash
cd frontend
npm install
npm run dev
```

### Application Desktop
```bash
cd desktop
pip install -r requirements.txt
python main.py
```

## Fonctionnalites
- Creation de compte utilisateur
- Connexion securisee
- Ajouter/Modifier/Supprimer des mots de passe
- Recherche de mots de passe
- Copier dans le presse-papiers
- Generation de mot de passe aleatoire
- Toast notifications (web)
- Chiffrement AES-256-CBC par utilisateur
- Sessions安全管理

## Structure
```
backend/
├── app/
│   ├── core/
│   │   ├── database.py
│   │   ├── session.py
│   │   └── crypto.py
│   ├── routes/
│   │   ├── auth.py
│   │   └── vault.py
│   └── models/
│       └── vault.py
└── server.py

frontend/
├── src/
│   ├── pages/
│   │   ├── Login.jsx/css
│   │   ├── Register.jsx/css
│   │   └── Dashboard.jsx/css
│   ├── services/
│   │   └── api.js
│   └── App.jsx

desktop/
├── main.py          # Application CustomTkinter
└── requirements.txt
```
