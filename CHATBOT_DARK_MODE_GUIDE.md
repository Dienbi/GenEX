# 🌙 Guide du Mode Sombre/Clair - Chatbot GenEX

## ✨ Fonctionnalités Ajoutées

### 🎨 **Mode Sombre/Clair Intelligent**
- **3 modes disponibles** : Clair, Sombre, Auto
- **Détection automatique** des préférences système
- **Mémorisation** des préférences utilisateur
- **Basculement en temps réel** sans rechargement

### 🔧 **Comment Utiliser**

#### **1. Basculement Manuel**
- Cliquez sur l'icône **🌙/☀️/⚙️** dans l'en-tête du chatbot
- Cycle automatique : Clair → Sombre → Auto → Clair...

#### **2. Modes Disponibles**
- **☀️ Clair** : Interface claire traditionnelle
- **🌙 Sombre** : Interface sombre pour les yeux
- **⚙️ Auto** : Suit automatiquement les préférences système

#### **3. Persistance**
- Les préférences sont **sauvegardées** automatiquement
- **Synchronisation** entre sessions
- **Mémorisation** locale et serveur

## 🎯 **Fonctionnalités Techniques**

### **Backend (Django)**
```python
# Nouveau champ dans le modèle User
theme_preference = models.CharField(
    max_length=10, 
    choices=THEME_CHOICES, 
    default='auto'
)
```

### **Frontend (JavaScript)**
```javascript
// API pour changer le thème
window.setChatbotTheme('dark');
window.getChatbotTheme(); // Retourne le thème actuel
```

### **CSS Responsive**
```css
/* Support des préférences système */
@media (prefers-color-scheme: dark) {
    [data-theme="auto"] { /* Styles sombres */ }
}
```

## 🚀 **Avantages**

### **👁️ Confort Visuel**
- **Réduction de la fatigue oculaire** en mode sombre
- **Adaptation automatique** aux conditions d'éclairage
- **Cohérence** avec les préférences système

### **🔧 Expérience Utilisateur**
- **Basculement instantané** sans rechargement
- **Mémorisation intelligente** des préférences
- **Interface intuitive** avec icônes claires

### **⚡ Performance**
- **CSS optimisé** avec sélecteurs efficaces
- **JavaScript léger** sans dépendances
- **Chargement asynchrone** des styles

## 🎨 **Personnalisation**

### **Couleurs du Mode Sombre**
- **Arrière-plan principal** : `#1a1a1a`
- **Arrière-plan secondaire** : `#2d3748`
- **Texte principal** : `#e0e0e0`
- **Accents** : `#3182ce` (bleu)

### **Éléments Stylisés**
- ✅ Messages de chat
- ✅ Zone de saisie
- ✅ Boutons d'action
- ✅ Zone de téléchargement
- ✅ Sessions de chat
- ✅ Fichiers uploadés

## 🔮 **Fonctionnalités Futures**

### **Prochaines Améliorations**
- **Thèmes personnalisés** par utilisateur
- **Gradients animés** pour les transitions
- **Mode sombre adaptatif** selon l'heure
- **Thèmes saisonniers** (Noël, Halloween, etc.)

### **Intégrations Possibles**
- **API système** pour détection automatique
- **Synchronisation** avec d'autres applications
- **Export/Import** des préférences

## 🐛 **Dépannage**

### **Problèmes Courants**
1. **Thème ne change pas** → Vérifier la console JavaScript
2. **Styles non appliqués** → Vider le cache navigateur
3. **Bouton manquant** → Vérifier le chargement des scripts

### **Support Technique**
- **Console développeur** pour les erreurs JavaScript
- **Logs Django** pour les erreurs serveur
- **Inspection CSS** pour les styles

## 📱 **Compatibilité**

### **Navigateurs Supportés**
- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+

### **Fonctionnalités Requises**
- **CSS Custom Properties** (variables CSS)
- **Media Queries** (préférences système)
- **LocalStorage** (sauvegarde locale)
- **Fetch API** (communication serveur)

---

## 🎉 **Résultat Final**

Votre chatbot GenEX dispose maintenant d'un **système de thèmes complet** qui :
- 🎨 **Améliore l'expérience utilisateur**
- 👁️ **Réduit la fatigue oculaire**
- ⚡ **Fonctionne en temps réel**
- 💾 **Mémorise les préférences**
- 🔄 **S'adapte automatiquement**

**Profitez de votre nouveau chatbot avec mode sombre/clair ! 🌙✨**
