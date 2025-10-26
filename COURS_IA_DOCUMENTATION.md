# 📚 Documentation - Fonctionnalité Cours IA

## Vue d'ensemble

La fonctionnalité **Cours IA** permet aux utilisateurs de générer automatiquement des cours détaillés en utilisant l'intelligence artificielle (OpenAI ChatGPT). Les utilisateurs peuvent créer, consulter et gérer leurs cours personnalisés.

---

## 🎯 Fonctionnalités

### 1. **Créer un cours**
- L'utilisateur entre simplement un titre de cours
- L'IA (ChatGPT) génère automatiquement un cours complet et structuré
- Le cours est sauvegardé dans la base de données

### 2. **Consulter les cours**
- Liste de tous les cours générés par l'utilisateur
- Affichage détaillé de chaque cours
- Interface moderne et responsive

### 3. **Gérer les cours**
- Supprimer des cours
- Confirmation avant suppression
- Historique des cours créés

---

## 🚀 Utilisation

### Accéder à la fonctionnalité

1. Connectez-vous à votre compte
2. Cliquez sur **"Cours IA"** dans la barre de navigation
3. Vous verrez la liste de tous vos cours

### Créer un nouveau cours

1. Cliquez sur le bouton **"Créer un nouveau cours"**
2. Entrez un titre descriptif pour votre cours (exemples : "Introduction à Python", "Les bases de la comptabilité", "Histoire de l'art moderne")
3. Cliquez sur **"Générer le cours avec l'IA"**
4. Patientez quelques secondes pendant que l'IA génère votre cours
5. Le cours généré s'affichera automatiquement

### Consulter un cours

1. Dans la liste des cours, cliquez sur **"Voir le cours"**
2. Le contenu complet du cours s'affiche
3. Vous pouvez imprimer le cours en cliquant sur **"Imprimer"**

### Supprimer un cours

1. Dans la liste des cours, cliquez sur l'icône **"Corbeille"**
2. Confirmez la suppression
3. Le cours sera définitivement supprimé

---

## 🔧 Architecture Technique

### Modèles (courses/models.py)

```python
class Course(models.Model):
    user = ForeignKey(User)          # Propriétaire du cours
    title = CharField                 # Titre du cours
    content = TextField               # Contenu généré par l'IA
    created_at = DateTimeField        # Date de création
    updated_at = DateTimeField        # Date de mise à jour
```

### Vues (courses/views.py)

- **course_list** : Liste tous les cours de l'utilisateur
- **course_create** : Formulaire de création + appel à l'API OpenAI
- **course_detail** : Affiche un cours spécifique
- **course_delete** : Supprime un cours avec confirmation

### URLs

- `/courses/` - Liste des cours
- `/courses/create/` - Créer un nouveau cours
- `/courses/<id>/` - Détails d'un cours
- `/courses/<id>/delete/` - Supprimer un cours

---

## 🤖 Configuration OpenAI

### Clé API

La clé API OpenAI est configurée dans `settings.py` :

```python
OPENAI_API_KEY = 'sk-proj-...'
```

### Paramètres de génération

- **Modèle** : `gpt-3.5-turbo`
- **Max tokens** : 2000 (environ 1500 mots)
- **Temperature** : 0.7 (équilibre créativité/précision)

### Prompt système

Le système utilise un prompt qui demande à l'IA de générer des cours :
- Bien structurés
- Avec introduction, développement et conclusion
- Avec des exemples pratiques
- Avec des explications claires

---

## 🎨 Interface Utilisateur

### Design

- **Couleurs principales** : Rouge (#dc3545) et noir
- **Style** : Moderne, épuré, professionnel
- **Responsive** : S'adapte à tous les écrans

### Pages

1. **Liste des cours** (`course_list.html`)
   - Grille de cartes pour chaque cours
   - Métadonnées (date, heure)
   - Actions rapides (voir, supprimer)

2. **Création de cours** (`course_create.html`)
   - Formulaire simple avec un champ de titre
   - Instructions claires
   - Animation de chargement pendant la génération

3. **Détail du cours** (`course_detail.html`)
   - Affichage complet du contenu
   - Formatage du texte (paragraphes, listes)
   - Options d'impression et de suppression

4. **Confirmation de suppression** (`course_confirm_delete.html`)
   - Message d'avertissement clair
   - Boutons Annuler/Confirmer

---

## 📊 Base de Données

### Table : courses_course

| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Clé primaire auto-incrémentée |
| user_id | Integer | Référence vers l'utilisateur |
| title | String(255) | Titre du cours |
| content | Text | Contenu HTML du cours |
| created_at | DateTime | Date de création |
| updated_at | DateTime | Date de dernière modification |

---

## 🔐 Sécurité

- **Authentification requise** : Toutes les vues nécessitent une connexion (`@login_required`)
- **Isolation des données** : Chaque utilisateur ne voit que ses propres cours
- **Protection CSRF** : Tous les formulaires sont protégés
- **Validation** : Les entrées utilisateur sont validées côté serveur

---

## 🚦 Tests

### Scénarios de test

1. **Création de cours**
   - Tester avec différents titres
   - Vérifier que le contenu est généré
   - Vérifier la sauvegarde en base de données

2. **Consultation de cours**
   - Vérifier l'affichage de la liste
   - Vérifier l'affichage des détails
   - Tester l'impression

3. **Suppression de cours**
   - Tester la confirmation
   - Vérifier la suppression effective

4. **Gestion des erreurs**
   - Tester avec un titre vide
   - Tester avec une clé API invalide
   - Tester avec un ID de cours inexistant

---

## 🛠️ Maintenance

### Logs

Les erreurs sont capturées et affichées via le système de messages Django :
- Messages de succès (vert)
- Messages d'erreur (rouge)

### Surveillance

Points à surveiller :
- Utilisation de l'API OpenAI (quotas, coûts)
- Temps de réponse de l'API
- Qualité des cours générés

---

## 🔄 Améliorations Futures

### Suggestions d'amélioration

1. **Édition de cours** : Permettre la modification du contenu généré
2. **Catégories** : Ajouter des catégories pour organiser les cours
3. **Partage** : Permettre le partage de cours entre utilisateurs
4. **Export** : Export en PDF, Word, etc.
5. **Niveaux** : Générer des cours adaptés au niveau (débutant, intermédiaire, avancé)
6. **Langues** : Support multilingue pour la génération
7. **Favoris** : Marquer des cours comme favoris
8. **Recherche** : Ajouter une recherche dans les cours

---

## 📞 Support

Pour toute question ou problème :
- Email : contact@genex.tn
- Téléphone : (+216) 70 250 000

---

## 📝 Changelog

### Version 1.0.0 (23 Octobre 2025)
- ✅ Création de cours avec IA
- ✅ Liste et consultation des cours
- ✅ Suppression de cours
- ✅ Interface utilisateur moderne
- ✅ Intégration OpenAI ChatGPT
- ✅ Sauvegarde en base de données
- ✅ Navigation intégrée

---

**Développé avec ❤️ pour GenEX Educational Platform**




