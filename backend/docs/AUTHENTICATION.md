# 🔐 Guide d'Authentification JWT

## Architecture

L'authentification est basée sur **JWT (JSON Web Tokens)** avec les composants suivants:

### 📁 Structure
```
backend/app/
├── models/user.py           # Modèle SQLAlchemy User
├── schemas/user.py          # Schémas Pydantic (validation)
├── services/auth_service.py # Logique d'authentification
├── utils/dependencies.py    # Middlewares de protection
└── api/auth.py             # Routes API
```

## 🚀 Configuration

### 1. Variables d'environnement (.env)

Ajoutez ces variables dans votre fichier `.env`:

```env
# Générez une clé sécurisée avec:
# python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=PUJyrIMcGvUXV1ST5d9ZlLz6wIvQK_teMPp833x0dHo
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 2. Migration de la base de données

```bash
# Appliquer la migration
alembic upgrade head
```

## 📡 API Endpoints

### 1. **Inscription** (Register)

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123",
  "full_name": "John Doe"
}
```

**Règles de validation:**
- Email: Format valide
- Username: 3-50 caractères, unique
- Password: Min 8 caractères, 1 majuscule, 1 minuscule, 1 chiffre

**Réponse (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "is_active": true,
    "is_verified": false,
    "is_superuser": false,
    "created_at": "2026-01-17T09:00:00",
    "last_login": "2026-01-17T09:00:00"
  }
}
```

### 2. **Connexion** (Login)

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Réponse (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": { ... }
}
```

### 3. **Profil Utilisateur**

```http
GET /api/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Réponse (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  ...
}
```

### 4. **Vérifier le Token**

```http
GET /api/auth/verify-token
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 5. **Déconnexion**

```http
POST /api/auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🛡️ Protection des Routes

### Usage basique

```python
from fastapi import APIRouter, Depends
from app.models.user import User
from app.utils.dependencies import get_current_user

router = APIRouter()

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    """Route protégée, nécessite un token JWT valide"""
    return {
        "message": f"Hello {current_user.username}",
        "user_id": current_user.id
    }
```

### Niveaux de protection

#### 1. Utilisateur actif uniquement
```python
from app.utils.dependencies import get_current_active_user

@router.get("/active-only")
async def active_route(user: User = Depends(get_current_active_user)):
    return {"message": "User is active"}
```

#### 2. Admin / Superutilisateur
```python
from app.utils.dependencies import get_current_superuser

@router.get("/admin")
async def admin_route(admin: User = Depends(get_current_superuser)):
    return {"message": "Admin access granted"}
```

#### 3. Authentification optionnelle
```python
from typing import Optional
from app.utils.dependencies import get_optional_current_user

@router.get("/optional")
async def optional_route(user: Optional[User] = Depends(get_optional_current_user)):
    if user:
        return {"message": f"Hello {user.username}"}
    return {"message": "Hello guest"}
```

## 💻 Exemple Frontend (React/JavaScript)

### 1. Inscription

```javascript
async function register(email, username, password) {
  const response = await fetch('http://localhost:8000/api/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      username,
      password,
      full_name: "John Doe"
    }),
  });
  
  const data = await response.json();
  
  if (response.ok) {
    // Sauvegarder le token
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    return data;
  } else {
    throw new Error(data.detail);
  }
}
```

### 2. Connexion

```javascript
async function login(email, password) {
  const response = await fetch('http://localhost:8000/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
  
  const data = await response.json();
  
  if (response.ok) {
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    return data;
  } else {
    throw new Error(data.detail);
  }
}
```

### 3. Appels API protégés

```javascript
async function fetchProtectedData() {
  const token = localStorage.getItem('token');
  
  const response = await fetch('http://localhost:8000/api/protected-route', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
  
  if (response.status === 401) {
    // Token expiré, rediriger vers login
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
    return;
  }
  
  return await response.json();
}
```

### 4. Déconnexion

```javascript
function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = '/login';
}
```

### 5. Context React pour l'authentification

```javascript
// AuthContext.jsx
import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  
  useEffect(() => {
    if (token) {
      // Vérifier le token au chargement
      verifyToken(token);
    }
  }, []);
  
  async function verifyToken(token) {
    try {
      const response = await fetch('http://localhost:8000/api/auth/verify-token', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUser(data);
      } else {
        logout();
      }
    } catch (error) {
      logout();
    }
  }
  
  function login(tokenData) {
    setToken(tokenData.access_token);
    setUser(tokenData.user);
    localStorage.setItem('token', tokenData.access_token);
    localStorage.setItem('user', JSON.stringify(tokenData.user));
  }
  
  function logout() {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
  
  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
```

## 🔒 Sécurité

### ✅ Bonnes pratiques implémentées

1. **Hachage bcrypt** pour les mots de passe (coût: 12 rounds)
2. **Validation stricte** des mots de passe (min 8 chars, majuscule, minuscule, chiffre)
3. **Tokens JWT signés** avec HS256
4. **Expiration des tokens** (60 minutes par défaut)
5. **Index de base de données** sur email et username
6. **Vérification is_active** avant authentification
7. **Protection CORS** configurable

### 🚨 À faire en production

1. **Changer JWT_SECRET_KEY** (utilisez une clé de 32+ caractères)
2. **HTTPS uniquement** pour toutes les requêtes
3. **Rate limiting** sur les endpoints d'authentification
4. **Refresh tokens** pour renouveler les access tokens
5. **Email verification** pour activer les comptes
6. **2FA** (Two-Factor Authentication) optionnel
7. **Logs de sécurité** (tentatives de connexion échouées)

## 🧪 Tests avec cURL

```bash
# 1. Inscription
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123",
    "full_name": "Test User"
  }'

# 2. Connexion
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'

# 3. Accéder à une route protégée (remplacez YOUR_TOKEN)
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📊 Structure de la base de données

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    last_login TIMESTAMP
);

CREATE INDEX ix_users_email ON users(email);
CREATE INDEX ix_users_username ON users(username);
```

## 🎯 Prochaines étapes

- [ ] Ajouter refresh tokens
- [ ] Implémenter email verification
- [ ] Ajouter rate limiting
- [ ] Créer des tests unitaires
- [ ] Implémenter password reset
- [ ] Ajouter OAuth (Google, GitHub)
