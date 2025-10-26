# 🔑 Guide de Configuration OpenAI pour GenEX

## 📋 **Étape 1 : Obtenir une clé API OpenAI**

### 1.1 Créer un compte OpenAI
1. Allez sur [https://platform.openai.com/](https://platform.openai.com/)
2. Cliquez sur "Sign up" pour créer un compte
3. Vérifiez votre email

### 1.2 Obtenir une clé API
1. Connectez-vous à votre compte OpenAI
2. Allez dans "API Keys" dans le menu de gauche
3. Cliquez sur "Create new secret key"
4. Donnez un nom à votre clé (ex: "GenEX-Exercises")
5. **Copiez la clé** (elle commence par `sk-` et ressemble à : `sk-1234567890abcdef...`)

⚠️ **Important** : Gardez cette clé secrète et ne la partagez jamais !

## 🔧 **Étape 2 : Configurer la clé dans GenEX**

### Option A : Variable d'environnement (Recommandée)

#### Sur Windows :
```cmd
set OPENAI_API_KEY=sk-votre-cle-ici
```

#### Sur Linux/Mac :
```bash
export OPENAI_API_KEY=sk-votre-cle-ici
```

### Option B : Fichier .env (Alternative)

Créez un fichier `.env` dans le dossier `GenEX/` :
```
OPENAI_API_KEY=sk-votre-cle-ici
```

### Option C : Directement dans settings.py

Modifiez `GenEX/settings.py` :
```python
OPENAI_API_KEY = 'sk-votre-cle-ici'
```

## 🧪 **Étape 3 : Tester la configuration**

### 3.1 Test automatique
```bash
python openai_config.py
```

### 3.2 Test manuel
```python
import os
from GenEX.settings import OPENAI_API_KEY

print(f"Clé configurée: {OPENAI_API_KEY[:10]}...")
```

## 🚀 **Étape 4 : Utiliser la génération IA**

Une fois la clé configurée :

1. **Redémarrez le serveur Django** :
   ```bash
   python manage.py runserver
   ```

2. **Allez sur** : `http://127.0.0.1:8000/exercises/`

3. **Cliquez sur** "Générer avec IA"

4. **Remplissez le formulaire** et cliquez sur "Générer"

5. **Vérifiez** que les vrais exercices IA sont générés !

## 💰 **Coûts OpenAI**

- **GPT-3.5-turbo** : ~$0.002 par 1000 tokens
- **Génération d'exercices** : ~$0.01-0.05 par exercice
- **Essai gratuit** : $5 de crédit offert

## 🔒 **Sécurité**

- ✅ Ne jamais commiter la clé dans Git
- ✅ Utiliser des variables d'environnement
- ✅ Ajouter `.env` au `.gitignore`
- ✅ Utiliser des clés différentes pour dev/prod

## 🆘 **Dépannage**

### Erreur "API key not found"
- Vérifiez que la clé est bien configurée
- Redémarrez le serveur Django

### Erreur "Insufficient credits"
- Vérifiez votre solde sur OpenAI
- Ajoutez des fonds si nécessaire

### Erreur "Rate limit exceeded"
- Attendez quelques minutes
- Réduisez la fréquence des requêtes

## 📞 **Support**

Si vous avez des problèmes :
1. Vérifiez la console Django pour les erreurs
2. Vérifiez la console du navigateur (F12)
3. Testez avec `python openai_config.py`
