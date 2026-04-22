# 🎨 Interfaces d'Authentification

## Pages créées

### 1. **Sign In** (`/signin`)
Interface de connexion inspirée de Slack avec:
- Champ email
- Champ mot de passe (avec bouton Show/Hide)
- Bouton "Sign In with Email" (connecté au backend JWT)
- Boutons Google et Apple (affichage uniquement)
- Lien vers Sign Up
- Link "Forgot password?"

### 2. **Sign Up** (`/signup`)
Interface d'inscription avec:
- Champ email
- Champ username (min. 3 caractères)
- Champ full name (optionnel)
- Champ password avec validation:
  - Min 8 caractères
  - 1 majuscule
  - 1 minuscule
  - 1 chiffre
- Champ confirmation password
- Bouton "Continue" (connecté au backend JWT)
- Boutons Google et Apple (affichage uniquement)
- Lien vers Sign In

## Fonctionnalités

### ✅ Authentification Backend
- **Connexion complète** avec l'API JWT backend
- Stockage du token dans localStorage
- Context React (`AuthContext`) pour gérer l'état global
- Protection automatique des routes
- Redirection après connexion vers `/dashboard`

### ✅ Validation des formulaires
- Validation email format
- Validation force du mot de passe
- Vérification correspondance passwords
- Messages d'erreur clairs

### ✅ Design Slack-like
- Interface propre et moderne
- Bordures arrondies
- Couleur principale: Purple (#6B46C1)
- Boutons OAuth stylisés (Google, Apple)
- Footer avec liens

### ⚠️ OAuth (Google/Apple)
Les boutons Google et Apple sont **pour l'affichage uniquement**.
Ils affichent une alerte "Coming soon!" au clic.

## Structure des fichiers

```
frontend/src/
├── context/
│   └── AuthContext.jsx          # Context React pour l'auth
├── pages/
│   ├── SignIn.jsx               # Page de connexion
│   └── SignUp.jsx               # Page d'inscription
├── components/
│   ├── Navbar.jsx               # Navbar avec boutons auth
│   └── ProtectedRoute.jsx       # Protection de routes
└── App.jsx                      # Routes principales
```

## Utilisation

### Se connecter
1. Aller sur `/signin`
2. Entrer email et mot de passe
3. Cliquer sur "Sign In with Email"
4. Redirection automatique vers `/dashboard`

### S'inscrire
1. Aller sur `/signup`
2. Remplir le formulaire
3. Le mot de passe doit respecter les critères
4. Cliquer sur "Continue"
5. Compte créé + connexion automatique

### Routes protégées
Pour protéger une route:

```javascript
import ProtectedRoute from './components/ProtectedRoute';

<Route 
  path="/dashboard" 
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  } 
/>
```

## Context d'authentification

Le `AuthContext` expose:

```javascript
const { 
  user,              // Objet utilisateur courant
  token,             // Token JWT
  loading,           // État de chargement
  login,             // Fonction de connexion
  register,          // Fonction d'inscription
  logout,            // Fonction de déconnexion
  isAuthenticated    // Booléen si authentifié
} = useAuth();
```

## API Backend

### Endpoints utilisés
- `POST /api/auth/login` - Connexion
- `POST /api/auth/register` - Inscription
- `GET /api/auth/verify-token` - Vérification token
- `GET /api/auth/me` - Profil utilisateur

### Configuration API
URL de l'API: `http://localhost:8000/api/auth`

Pour changer l'URL, modifier dans `AuthContext.jsx`:
```javascript
const API_URL = 'http://localhost:8000/api/auth';
```

## Navbar

La Navbar affiche dynamiquement:
- **Non connecté**: Boutons "Sign In" et "Get Started"
- **Connecté**: 
  - Lien "Dashboard"
  - Nom d'utilisateur
  - Bouton "Sign Out"

## Styles

Les pages utilisent:
- **Tailwind CSS** pour le styling
- **Couleur principale**: Purple-700 (#6B46C1)
- **Police**: System default
- **Design**: Minimaliste, épuré, inspiré de Slack

## Screenshots

Les interfaces correspondent exactement aux images fournies:
- Design épuré et professionnel
- Boutons arrondis avec bordures
- Séparateur "OR" / "OR SIGN IN WITH"
- Footer avec liens

## Prochaines améliorations possibles

- [ ] Implémenter vrai OAuth Google/Apple
- [ ] Ajouter "Forgot Password" fonctionnel
- [ ] Ajouter 2FA (Two-Factor Authentication)
- [ ] Email verification
- [ ] Loading states plus élaborés
- [ ] Animations de transition
- [ ] Mode sombre

---

**Design inspiré de Slack, fonctionnalité 100% Meeting AI** 🚀
