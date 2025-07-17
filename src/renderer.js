class ComputerVisionApp {
    constructor() {
        this.apps = [];
        this.filteredApps = [];
        this.selectedCategory = 'all';
        this.runningApps = [];
        this.appDetails = {};
        this.categories = {};
        
        this.initializeElements();
        this.setupEventListeners();
        this.loadConfigurations().then(() => this.loadApplications());
        
        // Mettre à jour les applications en cours toutes les 3 secondes
        setInterval(() => this.updateRunningApps(), 3000);
    }

    initializeElements() {
        this.categoriesList = document.getElementById('categories-list');
        this.appsGrid = document.getElementById('apps-grid');
        this.searchInput = document.getElementById('search-input');
        this.refreshBtn = document.getElementById('refresh-btn');
        this.runningAppsList = document.getElementById('running-apps-list');
        this.modal = document.getElementById('app-modal');
        this.modalTitle = document.getElementById('modal-title');
        this.modalBody = document.getElementById('modal-body');
        this.closeModal = document.querySelector('.close');
    }

    setupEventListeners() {
        this.searchInput.addEventListener('input', (e) => {
            this.filterApps(e.target.value);
        });

        this.refreshBtn.addEventListener('click', () => {
            this.loadApplications();
        });

        this.closeModal.addEventListener('click', () => {
            this.modal.style.display = 'none';
        });

        window.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.modal.style.display = 'none';
            }
        });
    }

    async loadApplications() {
        this.showLoading();
        
        try {
            const { apps, categories } = await window.electronAPI.getPythonApps();
            this.apps = apps;
            this.categories = categories;
            this.filteredApps = [...this.apps];
            this.renderCategories();
            this.renderApps();
            this.updateRunningApps();
        } catch (error) {
            console.error('Erreur lors du chargement des applications:', error);
            this.showError('Erreur lors du chargement des applications');
        }
    }

    renderCategories() {
        // Use this.categories from config to show all categories, even empty ones
        const categories = Object.keys(this.categories).sort();
        
        let html = `
            <div class="category-item ${this.selectedCategory === 'all' ? 'active' : ''}" 
                 onclick="app.selectCategory('all')">
                <div class="category-name">Toutes les applications</div>
                <div class="category-count">${this.apps.length} applications</div>
            </div>
        `;

        categories.forEach(category => {
            const count = this.apps.filter(app => app.category === category).length;
            html += `
                <div class="category-item ${this.selectedCategory === category ? 'active' : ''}" 
                     onclick="app.selectCategory('${category}')">
                    <div class="category-name">${this.formatCategoryName(category)}</div>
                    <div class="category-count">${count} applications</div>
                </div>
            `;
        });

        this.categoriesList.innerHTML = html;
    }

    getCategories() {
        return [...new Set(this.apps.map(app => app.category))].sort();
    }

    async loadConfigurations() {
        try {
            // Charger les détails des applications
            const detailsResponse = await fetch('./config/app_details.json');
            if (detailsResponse.ok) {
                this.appDetails = await detailsResponse.json();
            }
            
            // Charger les catégories
            const categoriesResponse = await fetch('./config/categories.json');
            if (categoriesResponse.ok) {
                const categoriesData = await categoriesResponse.json();
                this.categories = categoriesData.categories;
            }
        } catch (error) {
            console.error('Erreur lors du chargement des configurations:', error);
        }
    }

    formatCategoryName(category) {
        if (this.categories[category]) {
            return this.categories[category].name;
        }
        return category;
    }

    selectCategory(category) {
        this.selectedCategory = category;
        this.filterApps(this.searchInput.value);
        this.renderCategories();
    }

    filterApps(searchTerm) {
        this.filteredApps = this.apps.filter(app => {
            const matchesSearch = !searchTerm || 
                app.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                (app.description && app.description.toLowerCase().includes(searchTerm.toLowerCase()));
            
            const matchesCategory = this.selectedCategory === 'all' || 
                app.category === this.selectedCategory;
            
            return matchesSearch && matchesCategory;
        });
        
        this.renderApps();
    }

    renderApps() {
        if (this.filteredApps.length === 0) {
            this.appsGrid.innerHTML = `
                <div class="no-apps">
                    <h3>Aucune application trouvée</h3>
                    <p>Essayez de modifier votre recherche ou créez de nouvelles applications.</p>
                </div>
            `;
            return;
        }

        const html = this.filteredApps.map(app => this.createAppCard(app)).join('');
        this.appsGrid.innerHTML = html;
    }

    createAppCard(app) {
        const isRunning = this.runningApps.includes(app.name);
        const statusClass = isRunning ? 'status-running' : 'status-ready';
        const statusText = isRunning ? '🟡 En cours d\'exécution' : '🟢 Prêt';
        
        return `
            <div class="app-card">
                <div class="app-header">
                    <h3 class="app-name">${app.name}</h3>
                    <span class="app-category">${this.formatCategoryName(app.category)}</span>
                </div>
                
                <div class="app-description">
                    ${this.getAppDescription(app)}
                </div>
                
                <div class="app-status ${statusClass}">
                    ${statusText}
                </div>
                
                <div class="app-actions">
                    <button class="btn btn-primary" onclick="app.launchApp('${app.name}')" 
                            ${isRunning ? 'disabled' : ''}>
                        ${isRunning ? 'En cours...' : 'Lancer'}
                    </button>
                    
                    ${isRunning ? `
                        <button class="btn btn-danger" onclick="app.stopApp('${app.name}')">
                            ⏹️ Arrêter
                        </button>
                    ` : ''}
                    
                    <button class="btn btn-info" onclick="app.openTutorial('${app.name}')">
                        📖 Tuto
                    </button>
                </div>
                
                ${this.createDetailsSection(app)}
            </div>
        `;
    }

    getAppDescription(app) {
        const descriptions = {
            'hand_tracking': 'Détection et suivi des mains en temps réel avec MediaPipe',
            'face_detection': 'Détection et analyse des visages avec OpenCV',
            'gesture_recognition': 'Reconnaissance des gestes de la main',
            'object_detection': 'Détection d\'objets en temps réel',
            'pose_estimation': 'Estimation de la pose corporelle',
            'eye_tracking': 'Suivi des mouvements oculaires',
            'emotion_detection': 'Détection des émotions faciales',
            'background_removal': 'Suppression d\'arrière-plan en temps réel'
        };
        
        return descriptions[app.name] || 'Application de computer vision';
    }

    async launchApp(appName) {
        const app = this.apps.find(a => a.name === appName);
        if (!app) return;

        try {
            const result = await window.electronAPI.launchPythonApp(app);
            
            if (result.success) {
                this.showNotification(`${appName} lancé avec succès`, 'success');
                this.updateRunningApps();
                this.renderApps();
            } else {
                this.showNotification(`Erreur: ${result.message}`, 'error');
            }
        } catch (error) {
            console.error('Erreur lors du lancement:', error);
            this.showNotification('Erreur lors du lancement de l\'application', 'error');
        }
    }

    async stopApp(appName) {
        try {
            const result = await window.electronAPI.stopPythonApp(appName);
            
            if (result.success) {
                this.showNotification(`${appName} arrêté`, 'success');
                this.updateRunningApps();
                this.renderApps();
            } else {
                this.showNotification(`Erreur: ${result.message}`, 'error');
            }
        } catch (error) {
            console.error('Erreur lors de l\'arrêt:', error);
            this.showNotification('Erreur lors de l\'arrêt de l\'application', 'error');
        }
    }

    async updateRunningApps() {
        try {
            this.runningApps = await window.electronAPI.getRunningApps();
            this.renderRunningApps();
        } catch (error) {
            console.error('Erreur lors de la mise à jour des applications en cours:', error);
        }
    }

    renderRunningApps() {
        if (this.runningApps.length === 0) {
            this.runningAppsList.innerHTML = '<p class="no-apps">Aucune application en cours</p>';
            return;
        }

        const html = this.runningApps.map(appName => `
            <div class="running-app">
                <span class="app-name">${appName}</span>
                <button class="stop-btn" onclick="app.stopApp('${appName}')">
                    ⏹️ Arrêter
                </button>
            </div>
        `).join('');

        this.runningAppsList.innerHTML = html;
    }

    showAppDetails(appName) {
        const app = this.apps.find(a => a.name === appName);
        if (!app) return;

        this.modalTitle.textContent = app.name;
        this.modalBody.innerHTML = `
            <div class="app-details">
                <p><strong>Catégorie:</strong> ${this.formatCategoryName(app.category)}</p>
                <p><strong>Description:</strong> ${this.getAppDescription(app)}</p>
                <p><strong>Chemin:</strong> ${app.path}</p>
                <p><strong>Fichier principal:</strong> ${app.mainPy}</p>
                <p><strong>Lanceur disponible:</strong> ${app.hasLauncher ? 'Oui' : 'Non'}</p>
                
                <div class="app-actions" style="margin-top: 20px;">
                    <button class="btn btn-primary" onclick="app.launchApp('${app.name}')">
                        ▶️ Lancer l'application
                    </button>
                    <button class="btn btn-secondary" onclick="app.openAppFolder('${app.path}')">
                        📁 Ouvrir le dossier
                    </button>
                </div>
            </div>
        `;
        
        this.modal.style.display = 'block';
    }

    async openAppFolder(appPath) {
        try {
            await window.electronAPI.openExternal(`file://${appPath}`);
        } catch (error) {
            console.error('Erreur lors de l\'ouverture du dossier:', error);
        }
    }

    openTutorial(appName) {
        if (window.tutorialManager) {
            window.tutorialManager.openTutorial(appName);
        } else {
            console.error('TutorialManager non disponible');
        }
    }

    showLoading() {
        this.appsGrid.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
            </div>
        `;
    }

    showError(message) {
        this.appsGrid.innerHTML = `
            <div class="error">
                <h3>Erreur</h3>
                <p>${message}</p>
                <button class="btn btn-primary" onclick="app.loadApplications()">
                    🔄 Réessayer
                </button>
            </div>
        `;
    }

    createDetailsSection(app) {
        const details = this.appDetails[app.name] || {};
        const appName = details.name || app.name;
        const description = details.description || this.getAppDescription(app);
        const features = details.features || [];
        const requirements = details.requirements || [];
        const usage = details.usage || 'Aucune information d\'utilisation disponible';
        
        return `
            <div class="app-details-toggle" onclick="app.toggleDetails('${app.name}')">
                <span class="toggle-text">📋 Détails</span>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="app-details-content" id="details-${app.name}">
                <div class="app-details-section">
                    <h4>📝 Description complète</h4>
                    <p>${description}</p>
                </div>
                
                ${features.length > 0 ? `
                    <div class="app-details-section">
                        <h4>✨ Fonctionnalités</h4>
                        <ul class="app-features-list">
                            ${features.map(feature => `<li>${feature}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${requirements.length > 0 ? `
                    <div class="app-details-section">
                        <h4>🔧 Prérequis</h4>
                        <ul class="app-requirements-list">
                            ${requirements.map(req => `<li>${req}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                <div class="app-details-section">
                    <h4>💡 Utilisation</h4>
                    <div class="app-usage-text">${usage}</div>
                </div>
            </div>
        `;
    }
    
    toggleDetails(appName) {
        const toggle = document.querySelector(`[onclick="app.toggleDetails('${appName}')"]`);
        const content = document.getElementById(`details-${appName}`);
        const icon = toggle.querySelector('.toggle-icon');
        
        if (content.classList.contains('active')) {
            content.classList.remove('active');
            toggle.classList.remove('active');
        } else {
            content.classList.add('active');
            toggle.classList.add('active');
        }
    }

    showNotification(message, type = 'info') {
        // Créer une notification simple
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        
        if (type === 'success') {
            notification.style.backgroundColor = '#28a745';
        } else if (type === 'error') {
            notification.style.backgroundColor = '#dc3545';
        } else {
            notification.style.backgroundColor = '#17a2b8';
        }
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialiser l'application
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new ComputerVisionApp();
});

// Styles pour les notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .notification {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        font-weight: 500;
    }
`;
document.head.appendChild(style);
