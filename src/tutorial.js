class TutorialManager {
    constructor() {
        this.tutorials = {
            'hand_tracking': 'https://www.youtube.com/watch?v=NZde8Xt78Iw',
            'face_detection': 'https://www.youtube.com/watch?v=01sAkU_NvOY',
            'gesture_recognition': 'https://www.youtube.com/watch?v=vQZ4IvB07ec',
            'object_detection': 'https://www.youtube.com/watch?v=yqkISICHH-U',
            'pose_estimation': 'https://www.youtube.com/watch?v=06TE_U21FK4',
            'eye_tracking': 'https://www.youtube.com/watch?v=kbdbZFT9NQI',
            'emotion_detection': 'https://www.youtube.com/watch?v=37Kp4b_87Vs',
            'background_removal': 'https://www.youtube.com/watch?v=PyCJRhaNxPs'
        };
    }

    openTutorial(appName) {
        const tutorialUrl = this.tutorials[appName];
        
        if (tutorialUrl) {
            // Utiliser l'API Electron pour ouvrir le lien externe
            window.electronAPI.openExternal(tutorialUrl);
        } else {
            // URL par défaut vers la chaîne YouTube de SELI IA MASTER AGENCY
            const defaultUrl = 'https://www.youtube.com/@SELIIAMASTERAGENCY';
            window.electronAPI.openExternal(defaultUrl);
        }
    }

    // Méthode pour ajouter ou modifier un tutoriel
    setTutorial(appName, url) {
        this.tutorials[appName] = url;
    }

    // Méthode pour obtenir l'URL du tutoriel
    getTutorialUrl(appName) {
        return this.tutorials[appName] || 'https://www.youtube.com/@SELIIAMASTERAGENCY';
    }
}

// Créer une instance globale du gestionnaire de tutoriels
window.tutorialManager = new TutorialManager();
