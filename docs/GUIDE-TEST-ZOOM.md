# 🎥 Guide : Tester l'Intégration Zoom avec des Enregistrements

## 📋 Sommaire
Ce guide vous explique comment tester l'intégration Zoom avec des enregistrements (recordings).

---

## ✅ Option 1 : Utiliser de VRAIS Enregistrements Zoom (Recommandé)

### Étape 1 : Créer un enregistrement Cloud Zoom

1. **Démarrez une réunion Zoom** (instantanée ou planifiée)
   - Ouvrez Zoom Desktop ou Web
   - Cliquez sur "Nouvelle réunion" ou "Démarrer" sur une réunion planifiée

2. **Activez l'Enregistrement Cloud**
   - Pendant la réunion, cliquez sur le bouton "Enregistrer" (en bas)
   - Sélectionnez **"Enregistrer dans le cloud"** (pas "sur cet ordinateur")
   
3. **Parlez pendant 2-3 minutes** (ou laissez tourner)
   - Vous pouvez parler seul ou inviter quelqu'un
   - Le contenu n'a pas d'importance pour les tests

4. **Terminez la réunion**
   - Cliquez sur "Terminer la réunion"

5. **Attendez le traitement** (5-15 minutes)
   - Zoom traite automatiquement l'enregistrement
   - Vous recevrez un email quand c'est prêt

### Étape 2 : Vérifier vos enregistrements

1. Allez sur : **https://zoom.us/recording**
2. Vous devriez voir votre enregistrement dans la liste
3. Notez que seuls les enregistrements **Cloud** apparaissent (pas les locaux)

### Étape 3 : Tester dans l'application

1. Lancez votre application frontend et backend
2. Connectez-vous à Zoom via l'application
3. Cliquez sur "Sync Zoom" dans le Dashboard
4. Vous devriez voir vos enregistrements !

---

## 🧪 Option 2 : Utiliser des Données MOCK (Pour Tests Rapides)

Si vous voulez tester **sans créer de vrais enregistrements**, utilisez le mode mock :

### Activer le mode Mock

1. **Créez un fichier `.env.local`** dans `frontend/` :
   ```bash
   cd frontend
   cp .env.example .env.local
   ```

2. **Éditez `.env.local`** et changez :
   ```env
   VITE_USE_MOCK_ZOOM=true
   ```

3. **Redémarrez le serveur frontend** :
   ```bash
   npm run dev
   ```

4. **Testez** :
   - Cliquez sur "Sync Zoom" dans le Dashboard
   - Vous verrez 5 enregistrements fictifs
   - Console : `🧪 Using MOCK Zoom recordings data`

### Avantages du Mode Mock
- ✅ Pas besoin de créer de vrais enregistrements
- ✅ Données de test cohérentes
- ✅ Idéal pour le développement/démo
- ✅ 5 enregistrements variés avec différentes dates/durées

### Désactiver le Mode Mock
```env
VITE_USE_MOCK_ZOOM=false
```

---

## 🔍 Option 3 : Compte Zoom de Test

Si vous avez besoin d'un compte avec beaucoup d'enregistrements :

1. **Créez un compte Zoom gratuit de test** :
   - Allez sur https://zoom.us/signup
   - Utilisez un email temporaire (ex: temp-mail.org)

2. **Créez plusieurs enregistrements** :
   - Répétez l'Option 1 plusieurs fois
   - Ou utilisez des outils comme Zoom's Test Mode

---

## 📊 Scénarios de Test Recommandés

### 🎯 Scénarios à tester :

1. **Aucun enregistrement** :
   - Compte Zoom neuf sans enregistrements
   - Devrait afficher : "Aucun enregistrement trouvé"

2. **Quelques enregistrements** :
   - 2-3 enregistrements
   - Vérifier l'affichage de la liste

3. **Beaucoup d'enregistrements** :
   - 10+ enregistrements
   - Tester le scroll, la performance

4. **Importation** :
   - Cliquer sur "Importer" sur un enregistrement
   - Vérifier que les données sont pré-remplies dans le formulaire

5. **Erreurs** :
   - Déconnecter Zoom
   - Vérifier le message d'erreur

---

## ⚠️ Résolution de Problèmes

### "Aucun enregistrement trouvé" mais j'en ai créés

**Causes possibles :**
1. L'enregistrement est encore en traitement (attendez 5-15 min)
2. C'est un enregistrement LOCAL (pas Cloud)
3. Les scopes Zoom ne sont pas corrects

**Solution :**
- Vérifiez sur https://zoom.us/recording
- Assurez-vous que c'est un enregistrement Cloud
- Reconnectez votre compte Zoom (pour rafraîchir les scopes)

### Erreur 400 "Invalid access token"

**Solution :**
- Reconnectez-vous à Zoom via l'application
- Vérifiez les scopes dans votre app Zoom Marketplace

---

## 🚀 Commandes Utiles

```bash
# Mode Mock activé
cd frontend
echo "VITE_USE_MOCK_ZOOM=true" >> .env.local
npm run dev

# Mode Real (désactiver mock)
cd frontend
echo "VITE_USE_MOCK_ZOOM=false" >> .env.local
npm run dev

# Voir les logs
# Dans le navigateur : F12 > Console
# Cherchez : "🧪 Using MOCK Zoom recordings data"
```

---

## 📝 Notes Importantes

- Les enregistrements **locaux** (enregistrés sur votre ordinateur) n'apparaîtront **PAS** dans l'API
- Seuls les enregistrements **Cloud** sont accessibles via l'API Zoom
- Le plan gratuit Zoom a une limite de stockage Cloud (1 Go)
- Les enregistrements sont supprimés automatiquement après 30 jours (plan gratuit)

---

## ✨ Résumé

| Méthode | Avantages | Inconvénients |
|---------|-----------|---------------|
| **Vrais Enregistrements** | Réaliste, teste le vrai flux | Prend du temps à créer |
| **Mode Mock** | Rapide, pas de configuration | Pas de vraies données |
| **Compte de Test** | Données réelles variées | Besoin de créer un compte |

**Recommandation :** Commencez avec le **Mode Mock** pour le développement, puis testez avec de **vrais enregistrements** avant la production.
