// Gestion du mode sombre/clair pour le chatbot
class ThemeManager {
    constructor() {
        this.currentTheme = this.getStoredTheme() || 'auto';
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.createThemeToggle();
        this.bindEvents();
    }

    getStoredTheme() {
        // Récupérer depuis localStorage
        const stored = localStorage.getItem('chatbot-theme');
        if (stored) return stored;
        
        // Récupérer depuis les préférences utilisateur (si connecté)
        const userTheme = document.body.getAttribute('data-user-theme');
        if (userTheme) return userTheme;
        
        return 'auto';
    }

    applyTheme(theme) {
        const body = document.body;
        const chatContainer = document.querySelector('.chat-container');
        
        if (chatContainer) {
            chatContainer.setAttribute('data-theme', theme);
        }
        
        // Mettre à jour l'icône du bouton
        this.updateThemeIcon(theme);
        
        // Sauvegarder la préférence
        localStorage.setItem('chatbot-theme', theme);
    }

    updateThemeIcon(theme) {
        const icon = document.querySelector('.theme-toggle i');
        if (!icon) return;

        // Supprimer toutes les classes d'icônes
        icon.className = '';
        
        switch(theme) {
            case 'light':
                icon.className = 'fas fa-sun';
                break;
            case 'dark':
                icon.className = 'fas fa-moon';
                break;
            case 'auto':
                icon.className = 'fas fa-adjust';
                break;
        }
    }

    createThemeToggle() {
        // Vérifier si le bouton existe déjà
        if (document.querySelector('.theme-toggle')) return;

        const chatHeader = document.querySelector('.chat-header');
        if (!chatHeader) return;

        // Créer le bouton de basculement
        const themeToggle = document.createElement('button');
        themeToggle.className = 'theme-toggle btn btn-sm';
        themeToggle.innerHTML = '<i class="fas fa-adjust"></i>';
        themeToggle.title = 'Changer le thème';
        
        // Ajouter au header
        chatHeader.appendChild(themeToggle);
    }

    bindEvents() {
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.cycleTheme();
            });
        }
    }

    cycleTheme() {
        const themes = ['light', 'dark', 'auto'];
        const currentIndex = themes.indexOf(this.currentTheme);
        const nextIndex = (currentIndex + 1) % themes.length;
        const nextTheme = themes[nextIndex];
        
        this.setTheme(nextTheme);
    }

    async setTheme(theme) {
        this.currentTheme = theme;
        this.applyTheme(theme);
        
        // Envoyer la préférence au serveur si l'utilisateur est connecté
        try {
            const response = await fetch('/chatbot/api/theme-toggle/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ theme: theme })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('Thème mis à jour:', data.message);
            }
        } catch (error) {
            console.error('Erreur lors de la mise à jour du thème:', error);
        }
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    // Méthode pour détecter les préférences système
    detectSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }
}

// Initialiser le gestionnaire de thème quand le DOM est prêt
document.addEventListener('DOMContentLoaded', function() {
    window.themeManager = new ThemeManager();
    
    // Écouter les changements de préférences système
    if (window.matchMedia) {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addListener(function(e) {
            if (window.themeManager.currentTheme === 'auto') {
                window.themeManager.applyTheme('auto');
            }
        });
    }
});

// Fonction utilitaire pour changer le thème depuis d'autres scripts
window.setChatbotTheme = function(theme) {
    if (window.themeManager) {
        window.themeManager.setTheme(theme);
    }
};

// Fonction pour obtenir le thème actuel
window.getChatbotTheme = function() {
    return window.themeManager ? window.themeManager.currentTheme : 'auto';
};
