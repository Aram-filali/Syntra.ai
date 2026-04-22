# Meeting Intelligence - Frontend React

Interface web moderne pour Meeting Intelligence, propulsée par React 18 et Vite.

## 🚀 Démarrage Rapide

### Prérequis
- Node.js 16+ 
- npm ou yarn

### Installation

```bash
# Installer les dépendances
npm install

# Créer le fichier .env
cp .env.example .env

# Démarrer le serveur de développement
npm run dev
```

L'application sera accessible sur **http://localhost:3000**

## 📁 Structure du Projet

```
frontend/
├── src/
│   ├── api/
│   │   └── client.js          # Client API Axios
│   ├── components/
│   │   ├── Navbar.jsx          # Navigation principale
│   │   ├── MeetingCard.jsx     # Carte de meeting
│   │   ├── ActionItem.jsx      # Item d'action
│   │   ├── LoadingSpinner.jsx  # Spinner de chargement
│   │   └── ErrorMessage.jsx    # Message d'erreur
│   ├── pages/
│   │   ├── Landing.jsx         # Page d'accueil
│   │   ├── Dashboard.jsx       # Liste des meetings
│   │   ├── MeetingDetail.jsx   # Détail d'un meeting
│   │   └── CreateMeeting.jsx   # Formulaire création
│   ├── App.jsx                 # Composant principal + routing
│   ├── main.jsx                # Point d'entrée
│   └── index.css               # Styles globaux + Tailwind
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## 🎨 Stack Technique

- **React 18** - Framework UI
- **Vite** - Build tool ultra-rapide
- **React Router v6** - Routing
- **Axios** - Client HTTP
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **React Markdown** - Affichage des résumés

## 📄 Pages

### Landing Page (`/`)
Page d'accueil avec présentation du produit, features et CTA.

### Dashboard (`/dashboard`)
Liste de tous les meetings avec :
- Recherche par titre
- Filtres de statut
- Aperçu rapide de chaque meeting

### Meeting Detail (`/meetings/:id`)
Détail complet d'un meeting avec :
- Onglet Résumé (markdown généré par IA)
- Onglet Transcription complète
- Onglet Actions avec checkboxes
- Bouton "Analyser avec IA"
- Export PDF (à venir)

### Create Meeting (`/create`)
Formulaire de création avec :
- Titre, date, durée
- Zone de texte pour transcription
- Création + ajout transcription en une seule fois

## 🔌 API Client

Toutes les interactions avec le backend passent par `src/api/client.js` :

```javascript
import { meetingsAPI } from './api/client';

// Récupérer tous les meetings
const meetings = await meetingsAPI.getAll();

// Récupérer un meeting spécifique
const meeting = await meetingsAPI.getById(1);

// Analyser un meeting
await meetingsAPI.analyze(1);

// Mettre à jour le statut d'une action
await meetingsAPI.updateActionStatus(actionId, 'completed');
```

## 🎨 Composants Réutilisables

### Classes CSS Custom (Tailwind)

```jsx
// Boutons
<button className="btn-primary">Action</button>
<button className="btn-secondary">Annuler</button>
<button className="btn-danger">Supprimer</button>

// Cartes
<div className="card">...</div>

// Badges
<span className="badge badge-success">Terminé</span>
<span className="badge badge-warning">En attente</span>
<span className="badge badge-info">Info</span>
```

## 🌐 Variables d'Environnement

Créez un fichier `.env` à la racine du frontend :

```bash
# URL de l'API Backend
VITE_API_URL=http://localhost:8000/api
```

## 🛠️ Scripts Disponibles

```bash
# Développement
npm run dev

# Build production
npm run build

# Preview du build
npm run preview
```

## 🎯 Fonctionnalités

### ✅ Implémentées
- [x] Landing page attractive
- [x] Dashboard avec liste meetings
- [x] Recherche de meetings
- [x] Détail meeting avec tabs
- [x] Affichage transcription
- [x] Affichage summary (markdown)
- [x] Liste actions avec checkbox
- [x] Bouton analyser IA
- [x] Formulaire création meeting
- [x] Loading states
- [x] Error handling
- [x] Responsive design

### 🔜 À Venir
- [ ] Export PDF
- [ ] Real-time updates (WebSocket)
- [ ] Dark mode
- [ ] Filtres avancés
- [ ] Analytics dashboard
- [ ] Notifications

## 🐛 Développement

### Lancer le Backend

Avant de démarrer le frontend, assurez-vous que le backend tourne :

```bash
cd backend
uvicorn app.main:app --reload
```

Backend accessible sur : `http://localhost:8000`

### Tester l'Application

1. Démarrer le backend
2. Démarrer le frontend (`npm run dev`)
3. Ouvrir `http://localhost:3000`
4. Créer un meeting avec une transcription
5. Cliquer sur "Analyser avec IA"

## 📱 Responsive Design

L'application est entièrement responsive :
- **Mobile** : < 768px
- **Tablet** : 768px - 1024px
- **Desktop** : > 1024px

## 🎨 Palette de Couleurs

```css
Primary Blue: #3B82F6
Success Green: #10B981
Warning Yellow: #F59E0B
Error Red: #EF4444
Gray Neutral: #6B7280
Background: #F9FAFB
```

## 💡 Tips de Développement

### Hot Reload
Vite offre un HMR (Hot Module Replacement) extrêmement rapide. Vos modifications apparaissent instantanément.

### Proxy API
Le proxy est configuré dans `vite.config.js` pour rediriger `/api/*` vers `http://localhost:8000/api/*`, évitant les problèmes CORS en développement.

### Debug
Ouvrez les DevTools React pour inspecter l'état des composants et le routing.

---

**Créé avec ❤️ par l'équipe Meeting Intelligence**
